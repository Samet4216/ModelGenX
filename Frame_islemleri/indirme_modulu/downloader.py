import os
import yt_dlp
import datetime
from PyQt6.QtCore import QThread, pyqtSignal

class InfoExtractorThread(QThread):
    finished_info = pyqtSignal(list)
    log_msg = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        ydl_opts = {
            'extract_flat': True,
            'noplaylist': False,
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': ['player_client=ios,web']}
        }
        try:
            self.log_msg.emit("BİL", "Link analiz ediliyor...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if info is None: # YouTube geçici olarak bağlantıyı reddetmiş (IP engeli) veya link gizli/yanlış olabilir.
                    raise Exception("Bağlantıdan veri alınamadı. Link gizli/hatalı olabilir veya YouTube geçici olarak (çok fazla istekten) erişimi engellemiş olabilir. Lütfen 1-2 dakika bekleyip tekrar deneyin.")

                entries = []     
                if 'entries' in info: # Playlist
                    self.log_msg.emit("BİL", f"Playlist algılandı. Toplam video: {len(info['entries'])}")
                    for e in info['entries']:
                        if e and e.get('id'):
                            # YouTube shortlink garantisi
                            url = e.get('url')
                            if not url: url = f"https://www.youtube.com/watch?v={e.get('id')}" 
                            entries.append({
                                'url': url,
                                'id': e.get('id'),
                                'title': e.get('title', 'Bilinmeyen Video')
                            })
                else: # Tekil Video
                    entries.append({
                        'url': info.get('webpage_url', self.url),
                        'id': info.get('id'),
                        'title': info.get('title', 'Bilinmeyen Video')
                    })
            self.finished_info.emit(entries)
        except Exception as e: self.error_occurred.emit(f"Analiz Hatası: {str(e)}")

class DownloadWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_msg = pyqtSignal(str, str)
    finished_success = pyqtSignal(str, str, str, str, str) # id, title, size, duration, date
    error_occurred = pyqtSignal(str)

    def __init__(self, video_dict, save_dir):
        super().__init__()
        self.video_dict = video_dict
        self.save_dir = save_dir
        self.total_downloaded_bytes = 0
        self.max_p = 0
        self.duration_str = "-"
        self.title = self.video_dict['title']
        self.is_paused = False
        self.is_canceled = False
        self.file_index = 0

    def pause(self): self.is_paused = True
    def resume(self): self.is_paused = False
    def cancel(self): self.is_canceled = True

    def run(self):
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")   
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.save_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'no_warnings': True,
            'color': 'no_color',
            'merge_output_format': 'mp4',
            # 403 Forbidden (Erişim Reddedildi) ve Hız Kısıtlamasını Atlatmak İçin iOS API Bypass
            'extractor_args': {'youtube': ['player_client=ios,web']},
            # Yedek Native Ayarlar (Eğer Aria2c çalışmazsa)
            'concurrent_fragment_downloads': 6,
            'socket_timeout': 15,
            'retries': 25,
            'fragment_retries': 25,
        }
        
        if ffmpeg_path: ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_path)
        try:
            if self.is_canceled: raise Exception("İndirme iptal edildi.")
                
            def do_download(opts, is_fallback=False):
                with yt_dlp.YoutubeDL(opts) as ydl:
                    if is_fallback:
                        ydl.cache.remove()
                    info = ydl.extract_info(self.video_dict['url'], download=False)
                    
                    self.title = info.get('title', self.title)
                    duration_sec = info.get('duration', 0)
                    mins, secs = divmod(duration_sec, 60)
                    hours, mins = divmod(mins, 60)
                    if hours > 0: self.duration_str = f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}"
                    else: self.duration_str = f"{int(mins):02d}:{int(secs):02d}"
                    if not is_fallback: self.log_msg.emit("DTY", f"İndiriliyor: {self.title}")
                    
                    ydl.download([self.video_dict['url']])
                    date_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                    
                    if self.total_downloaded_bytes > 0: size_mb = f"{self.total_downloaded_bytes / (1024 * 1024):.1f} MB"
                    else:
                        approx = info.get('filesize_approx', info.get('filesize', 0))
                        size_mb = f"{approx / (1024 * 1024):.1f} MB" if approx else "Bilinmiyor"
                    self.finished_success.emit(self.video_dict['id'], self.title, size_mb, self.duration_str, date_str)

            try: do_download(ydl_opts)
            except Exception as e:
                err_str = str(e).lower()
                if "403" in err_str or "forbidden" in err_str or "http error 403" in err_str:
                    self.log_msg.emit("UYR", f"403 Hatası. Alternatif istemci (Android) ile deneniyor: {self.title}")
                    ydl_opts['extractor_args'] = {'youtube': ['player_client=android,web']}
                    do_download(ydl_opts, is_fallback=True)
                else: raise e
                
        except Exception as e:
            if "iptal edildi" in str(e).lower():
                self.error_occurred.emit("İptal Edildi")
                self.log_msg.emit("UYR", f"İndirme İptal Edildi: {self.title}")
            else:
                self.error_occurred.emit(str(e))
                self.log_msg.emit("HTA", f"Hata: {str(e)}")

    def my_hook(self, d): # İptal ve Duraklatma Kontrolü
        import time
        while getattr(self, 'is_paused', False):
            if getattr(self, 'is_canceled', False): raise Exception("İndirme iptal edildi.")
            time.sleep(0.5)
            
        if getattr(self, 'is_canceled', False):
            raise Exception("İndirme iptal edildi.")

        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0.0%').replace('%', '').strip()
            import re
            p = re.sub(r'\x1b\[[0-9;]*m', '', p)
            try:
                raw_percent = float(p) 
                # Video dosyası %0-80, Ses dosyası %80-98 arası haritalandırılıyor
                # Böylece bar asla geriye gitmez.
                if self.file_index == 0:
                    mapped_percent = int(raw_percent * 0.80)
                elif self.file_index == 1: mapped_percent = 80 + int(raw_percent * 0.18)
                else: mapped_percent = 98
                if mapped_percent > self.max_p:
                    self.max_p = mapped_percent
                    self.progress_updated.emit(self.max_p)
            except ValueError: pass
                
        elif d['status'] == 'finished':
            self.file_index += 1
            if self.file_index == 1:
                self.max_p = 80
                self.progress_updated.emit(80) # Video bitti
            elif self.file_index >= 2:
                self.max_p = 98
                self.progress_updated.emit(98) # Ses bitti, birleştirme başlıyor
            
            self.total_downloaded_bytes += d.get('total_bytes', d.get('downloaded_bytes', 0))
