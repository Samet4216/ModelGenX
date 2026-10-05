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
            'extract_flat': True, # Tüm playlisti flat olarak çıkart
            'noplaylist': False,  # Linkte video ve list beraber varsa kesinlikle listeyi al
            'ignoreerrors': True, # Ulaşılamayan/gizli videolarda patlamasın
            'quiet': True,
            'no_warnings': True
        }
        try:
            self.log_msg.emit("BİL", "Link analiz ediliyor...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                entries = []
                
                if 'entries' in info: # Playlist
                    self.log_msg.emit("BİL", f"Playlist algılandı. Toplam video: {len(info['entries'])}")
                    for e in info['entries']:
                        if e and e.get('id'):
                            # YouTube shortlink garantisi
                            url = e.get('url')
                            if not url:
                                url = f"https://www.youtube.com/watch?v={e.get('id')}"
                            
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
        except Exception as e:
            self.error_occurred.emit(f"Analiz Hatası: {str(e)}")


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

    def run(self):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.save_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
            'concurrent_fragment_downloads': 5,
            'http_chunk_size': 10485760,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Sadece bu videonun süresini ve boyutunu almak için
                info = ydl.extract_info(self.video_dict['url'], download=False)
                
                self.title = info.get('title', self.title)
                duration_sec = info.get('duration', 0)
                mins, secs = divmod(duration_sec, 60)
                hours, mins = divmod(mins, 60)
                if hours > 0:
                    self.duration_str = f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}"
                else:
                    self.duration_str = f"{int(mins):02d}:{int(secs):02d}"
                
                self.log_msg.emit("DTY", f"İndiriliyor: {self.title}")
                
                # İndirmeyi başlat
                ydl.download([self.video_dict['url']])
                
                # Tarih ve boyut formatlaması
                date_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                
                if self.total_downloaded_bytes > 0:
                    size_mb = f"{self.total_downloaded_bytes / (1024 * 1024):.1f} MB"
                else:
                    approx = info.get('filesize_approx', info.get('filesize', 0))
                    size_mb = f"{approx / (1024 * 1024):.1f} MB" if approx else "Bilinmiyor"
                
                # Başarı sinyalini ana arayüze yolla
                self.finished_success.emit(self.video_dict['id'], self.title, size_mb, self.duration_str, date_str)
                
        except Exception as e:
            self.error_occurred.emit(str(e))

    def my_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0.0%').replace('%', '').strip()
            import re
            p = re.sub(r'\x1b\[[0-9;]*m', '', p)
            try:
                percent = int(float(p))
                
                if percent < 5 and self.max_p > 80:
                    self.max_p = 0
                
                if percent >= self.max_p:
                    self.max_p = percent
                    self.progress_updated.emit(percent)
            except ValueError:
                pass
        elif d['status'] == 'finished':
            self.progress_updated.emit(100)
            self.max_p = 0
            self.total_downloaded_bytes += d.get('total_bytes', d.get('downloaded_bytes', 0))
