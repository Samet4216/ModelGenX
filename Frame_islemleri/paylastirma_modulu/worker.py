import os
import cv2
import shutil
from PyQt6.QtCore import QThread, pyqtSignal

class FrameExtractionThread(QThread):
    log_msg = pyqtSignal(str, str)
    progress_update = pyqtSignal(int)
    finished_extraction = pyqtSignal(dict)
    
    def __init__(self, videos, annotators, output_dir, output_format, output_name):
        super().__init__()
        self.videos = videos
        self.annotators = annotators
        self.output_dir = output_dir
        self.output_format = output_format
        self.output_name = output_name
        self._is_cancelled = False
        
    def cancel(self):
        self._is_cancelled = True
        
    def run(self):
        try:
            self.log_msg.emit("BİLGİ", "Frame paylaştırma işlemi başladı...")
            
            # Gerekli ana dizini oluştur
            base_target = os.path.join(self.output_dir, self.output_name)
            os.makedirs(base_target, exist_ok=True)
            
            
            # İstatistikleri tutmak için
            stats = {a['name']: 0 for a in self.annotators}
            
            # --- ORTAK KOTA VE DAĞITIM HESAPLAMASI ---
            from Frame_islemleri.paylastirma_modulu.distribution_engine import calculate_distribution
            dist_data = calculate_distribution(self.videos, self.annotators)
            total_extracted_all_videos = dist_data['total_frames']
            
            for video in self.videos:
                vid_path = video['path']
                vid_name = os.path.splitext(video['name'])[0]
                vid_split = video['split']
                vid_interval = video['interval']
                
                vid_assignments = dist_data['video_assignments'].get(vid_path, [])
                
                if not vid_assignments:
                    self.log_msg.emit('UYARI', f'{vid_name} ({vid_split}) için uygun kişi bulunamadı. Atlanıyor.')
                    continue
                
                self.log_msg.emit('BİLGİ', f'{vid_name} işleniyor... (Tahmini Çıkacak Kare: {len(vid_assignments)})')
                
                cap = cv2.VideoCapture(vid_path)
                frame_idx = 0
                extracted_idx = 0
                
                while True:
                    if self._is_cancelled:
                        break
                        
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    if frame_idx % vid_interval == 0:
                        if extracted_idx < len(vid_assignments):
                            annotator = vid_assignments[extracted_idx]
                            
                            # Kişi_Rol -> Video (örn: Meryem_train)
                            save_path = os.path.join(base_target, f"{annotator}_{vid_split}")
                            
                            os.makedirs(save_path, exist_ok=True)
                            
                            # Frame adında numara formatı korunur (Önizleme ağacıyla birebir aynı)
                            file_name = f"{vid_name}_{extracted_idx + 1:05d}.png"
                            cv2.imwrite(os.path.join(save_path, file_name), frame)
                            
                            stats[annotator] += 1
                            extracted_idx += 1
                            processed_frames += 1
                            
                            if processed_frames % 50 == 0:
                                prog = int((processed_frames / total_extracted_all_videos) * 100) if total_extracted_all_videos > 0 else 0
                                self.progress_update.emit(prog)
                                
                    frame_idx += 1
                        
                cap.release()
                
                if self._is_cancelled:
                    break
                
            if self._is_cancelled:
                self.log_msg.emit("UYARI", "İşlem iptal edildi, dosyalar siliniyor...")
                if os.path.exists(base_target):
                    shutil.rmtree(base_target, ignore_errors=True)
                self.log_msg.emit("BİLGİ", "İptal tamamlandı, depolama temizlendi.")
                self.finished_extraction.emit({})
                return
                
            self.progress_update.emit(100)
            
            # Zip format seçildiyse, zipleyip klasörü sil
            if self.output_format.lower() == "zip":
                self.log_msg.emit("BİLGİ", "Zip arşivi oluşturuluyor, lütfen bekleyin...")
                shutil.make_archive(base_target, 'zip', base_target)
                shutil.rmtree(base_target)
                self.log_msg.emit("BAŞARILI", f"İşlem tamamlandı! ({self.output_name}.zip)")
            else:
                self.log_msg.emit("BAŞARILI", f"İşlem tamamlandı! Klasör: {self.output_name}")
                
            self.finished_extraction.emit(stats)
            
        except Exception as e:
            self.log_msg.emit("HATA", str(e))
            self.finished_extraction.emit({})
