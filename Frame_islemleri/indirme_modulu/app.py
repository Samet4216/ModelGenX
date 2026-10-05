import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QProgressBar, QFileDialog, QMessageBox,
                             QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint

from Frame_islemleri.indirme_modulu.downloader import InfoExtractorThread, DownloadWorker
from Frame_islemleri.indirme_modulu.indir_style import *

class DownloadSlotWidget(QWidget):
    slot_freed = pyqtSignal() # İndirme bitince veya hata verince ana kuyruğa haber vermek için
    
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.worker = None
        self.is_free = True # Slotun boş/dolu durumunu tutar (isVisible yerine bunu kullanmalıyız)
        self.setMinimumHeight(65) # Barlar ve yazılar büyüdüğü için yüksekliği ayarladık
        self.setup_ui()
        self.hide() # Başlangıçta gizli

    def setup_ui(self):
        # Ana layout dikey (alt alta) olacak
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 5, 0, 5)
        main_layout.setSpacing(8) # Yazı ile barı arasına biraz daha nefes alma boşluğu eklendi
        
        # Üst kısım: İkon (Tıklanabilir) ve Yazı
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_btn = QPushButton("⏳")
        self.icon_btn.setFixedWidth(25)
        self.icon_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_btn.setStyleSheet(SLOT_ICON_DEFAULT_STYLE)
        self.icon_btn.clicked.connect(self.show_action_menu)
        
        # Video Adı
        self.title_lbl = QLabel("")
        self.title_lbl.setStyleSheet(SLOT_TITLE_STYLE)
        
        self.percent_lbl = QLabel("0%")
        self.percent_lbl.setStyleSheet(SLOT_PERCENT_DEFAULT_STYLE)
        
        top_layout.addWidget(self.icon_btn)
        top_layout.addWidget(self.title_lbl)
        top_layout.addStretch() # Sola yaslanması için
        top_layout.addWidget(self.percent_lbl)
        
        # Alt kısım: İlerleme Çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8) # İnceltildi
        self.progress_bar.setTextVisible(False)
        self.update_progress_style(0)
        
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.progress_bar)
        
        # Hayati Dokunuş: Elemanları yukarı iter ve aralarının açılmasını (dağılmasını) kesin olarak engeller
        main_layout.addStretch()

    def set_error_style(self):
        self.progress_bar.setStyleSheet(SLOT_PROGRESS_ERROR_STYLE)
        self.percent_lbl.setStyleSheet(SLOT_PERCENT_ERROR_STYLE)

    def update_progress_style(self, value):
        self.progress_bar.setStyleSheet(get_progress_style(value))

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.percent_lbl.setText(f"%{value}")
        self.update_progress_style(value)

    def show_action_menu(self):
        if not self.worker or not self.worker.isRunning(): return

        menu = QMenu(self)
        menu.setStyleSheet(ACTION_MENU_STYLE)

        pause_action = menu.addAction("⏸ Duraklat")
        resume_action = menu.addAction("▶️ Sürdür")
        cancel_action = menu.addAction("❌ İptal Et")

        if self.worker.is_paused: pause_action.setEnabled(False)
        else: resume_action.setEnabled(False)

        action = menu.exec(self.icon_btn.mapToGlobal(QPoint(0, self.icon_btn.height())))

        if action == pause_action:
            self.worker.pause()
            self.icon_btn.setText("⏸")
            self.icon_btn.setStyleSheet(SLOT_ICON_PAUSED_STYLE)
            if not self.title_lbl.text().startswith("Duraklatıldı:"):
                self.title_lbl.setText("Duraklatıldı: " + self.title_lbl.text())
        elif action == resume_action:
            self.worker.resume()
            self.icon_btn.setText("⬇️")
            self.icon_btn.setStyleSheet(SLOT_ICON_DEFAULT_STYLE)
            self.title_lbl.setText(self.title_lbl.text().replace("Duraklatıldı: ", ""))
        elif action == cancel_action:
            self.worker.cancel()

    def start(self, video_dict, save_dir):
        self.is_free = False
        self.show()
        self.icon_btn.setText("⬇️")
        self.icon_btn.setStyleSheet(SLOT_ICON_DEFAULT_STYLE)
        
        # İsmi eskisi gibi kısa kesiyoruz (35 harf + ...)
        short_title = video_dict['title'][:35] + "..." if len(video_dict['title']) > 35 else video_dict['title']
        self.title_lbl.setText(short_title)
        self.percent_lbl.setStyleSheet(SLOT_PERCENT_DEFAULT_STYLE)
        self.update_progress(0)
        
        # Worker'ı Başlat
        self.worker = DownloadWorker(video_dict, save_dir)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_msg.connect(self.parent_app.relay_log)
        self.worker.finished_success.connect(self.on_success)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def on_success(self, video_id, title, size, duration, date):
        self.update_progress(100)
        self.percent_lbl.setStyleSheet(SLOT_PERCENT_SUCCESS_STYLE)
        self.icon_btn.setText("✅")
        self.title_lbl.setText(f"Tamamlandı: {title[:25]}...")
        
        # Ana sınıftaki history fonksiyonunu çağırarak thread safe bir şekilde dosyaya yazıyoruz
        self.parent_app.save_to_history(video_id, title, size, duration, date)
        # Log paneline başarılı indirme mesajı gönderiyoruz
        self.parent_app.relay_log("BAŞ", f"İndirme Tamamlandı: {title}")
        # 1.5 saniye ekranda ✅ kaldıktan sonra bar kaybolur ve yerini yeni videoya bırakır
        QTimer.singleShot(1500, self.free_slot)

    def on_error(self, err_msg):
        if err_msg == "İptal Edildi":
            self.icon_btn.setText("❌")
            self.icon_btn.setStyleSheet(SLOT_ICON_ERROR_STYLE)
            self.title_lbl.setText("İptal Edildi!")
            self.set_error_style()
        else:
            self.icon_btn.setText("❌")
            self.icon_btn.setStyleSheet(SLOT_ICON_ERROR_STYLE)
            self.title_lbl.setText("İndirme Hatası!")
            self.set_error_style()
            self.parent_app.relay_log("HTA", f"Hata: {err_msg}")
        
        # 3 saniye sonra kaybolur
        QTimer.singleShot(3000, self.free_slot)

    def free_slot(self):
        self.is_free = True
        self.hide()
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
        self.slot_freed.emit()

class IndirmeModuluApp(QWidget):
    send_log_signal = pyqtSignal(str, str) 

    def __init__(self):
        super().__init__()
        self.module_dir = os.path.dirname(os.path.abspath(__file__))
        self.history_file = os.path.join(self.module_dir, "indirme_gecmisi.txt")
        self.save_dir = os.path.join(os.path.expanduser("~"), "Downloads", "ModelGenX_Videolar")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        # Playlist kuyruğu ve aktif thread'leri takip etmek için
        self.queue = []
        self.slots = []
        self.batch_success_count = 0

        self.setup_ui()

    def setup_ui(self): # Arka planın (Card) rengini alması için bu widget'ı saydam yapıyoruz
        self.setStyleSheet(APP_BG_STYLE)
        layout = QVBoxLayout(self)
        # Ekran daraldığında taşmayı önlemek için genel boşlukları kıstım
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_lbl = QLabel("🎥 YouTube Video İndirici")
        title_lbl.setStyleSheet(TITLE_LBL_STYLE)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        self.history_btn = QPushButton("📜 Geçmişi Gör")
        self.history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_btn.setStyleSheet(HISTORY_BTN_STYLE)
        self.history_btn.clicked.connect(self.show_history_dialog)
        header_layout.addWidget(self.history_btn)
        
        desc_lbl = QLabel("Aynı anda 4 adede kadar video indirebilirsiniz. Playlist linki girildiğinde sıraya alınır.")
        desc_lbl.setStyleSheet(DESC_LBL_STYLE)

        # --- Link Girişi ---
        input_layout = QVBoxLayout()
        input_layout.setSpacing(8)
        url_label = QLabel("Video veya Playlist Linki:")
        url_label.setStyleSheet(URL_LBL_STYLE)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Örn: https://www.youtube.com/watch?v=...")
        self.url_input.setStyleSheet(URL_INPUT_STYLE)
        input_layout.addWidget(url_label)
        input_layout.addWidget(self.url_input)

        # --- Klasör Seçimi ---
        save_layout = QHBoxLayout()
        self.save_path_lbl = QLabel(f"Kayıt Yeri: {self.save_dir}")
        self.save_path_lbl.setStyleSheet(SAVE_PATH_LBL_STYLE)
        change_dir_btn = QPushButton("📂 Klasör Değiştir")
        change_dir_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_dir_btn.setStyleSheet(CHANGE_DIR_BTN_STYLE)
        change_dir_btn.clicked.connect(self.choose_directory)
        save_layout.addWidget(self.save_path_lbl)
        save_layout.addStretch()
        save_layout.addWidget(change_dir_btn)

        # --- 4'lü Paralel İndirme Slotları (Alt Alta) ---
        self.slots_container = QVBoxLayout()
        self.slots_container.setSpacing(15) # Slotlar arası mesafeyi belirginleştirdik
        for _ in range(4):
            slot = DownloadSlotWidget(self)
            slot.slot_freed.connect(self.process_queue)
            self.slots_container.addWidget(slot)
            self.slots.append(slot)

        # --- İndirme Butonu ---
        self.download_btn = QPushButton("İndirmeyi Başlat")
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.setFixedHeight(50)
        self.download_btn.setStyleSheet(DOWNLOAD_BTN_STYLE)
        self.download_btn.clicked.connect(self.start_download)

        layout.addLayout(header_layout)
        layout.addWidget(desc_lbl)
        layout.addSpacing(5)
        layout.addLayout(input_layout)
        layout.addLayout(save_layout)
        layout.addSpacing(10) # Klasör ve barlar arası boşluk
        layout.addLayout(self.slots_container)
        layout.addSpacing(15) # Buton ve barlar arası boşluk
        layout.addWidget(self.download_btn)
        
        # QWidget yerine standart layout esnemesi kullanıyoruz ki elemanlar ezilmesin
        layout.addStretch()

    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Kayıt Klasörünü Seç", self.save_dir)
        if directory:
            self.save_dir = directory
            self.save_path_lbl.setText(f"Kayıt Yeri: {self.save_dir}")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.send_log_signal.emit("UYR", "Lütfen bir YouTube linki giriniz.")
            return

        self.download_btn.setEnabled(False)
        self.download_btn.setText("⏳ Link Analiz Ediliyor...")

        # Link analizi için arka plan işini başlat
        self.info_thread = InfoExtractorThread(url)
        self.info_thread.finished_info.connect(self.on_info_extracted)
        self.info_thread.log_msg.connect(self.relay_log)
        self.info_thread.error_occurred.connect(self.on_info_error)
        self.info_thread.start()

    def on_info_extracted(self, entries):
        to_download = []
        for e in entries:
            if self.check_history(e['id']):
                self.relay_log("UYR", f"Geçildi (Zaten İndirilmiş): {e['title']}")
            else: to_download.append(e)

        if not to_download:
            self.relay_log("BİL", "Bu linkten indirilecek yeni video bulunamadı.")
            self.reset_ui()
            return

        self.queue.extend(to_download)
        self.url_input.clear()
        
        # Eğer çok dosya varsa bilgi verelim
        if len(self.queue) > 1:
            self.relay_log("BİL", f"Kuyruğa eklendi: {len(self.queue)} video. 4'erli indirilecek.")
        self.download_btn.setText("⏳ İndirmeler Devam Ediyor...")
        self.process_queue()

    def on_info_error(self, err_msg):
        self.reset_ui()
        QMessageBox.warning(self, "Analiz Hatası", f"Link okunurken hata:\n{err_msg}")

    def process_queue(self):
        # Kuyruk tamamen bittiyse ve aktif inen yoksa butonu aç
        if not self.queue:
            if all(s.is_free for s in self.slots):
                self.reset_ui()
                self.relay_log("BİL", "=" * 40)
                self.relay_log("BİL", f"Tüm indirme kuyruğu tamamlandı.")
                self.relay_log("BİL", f"Toplam {self.batch_success_count} video başarıyla indirildi.")
                self.relay_log("BİL", "=" * 40)
                # Sıfırla
                self.batch_success_count = 0
                
                if hasattr(self.window(), 'show_toast'): self.window().show_toast("Tüm videolar başarıyla indirildi!")
            return

        # 4 tane slottan boş olanları bul ve kuyruktaki işleri ver
        for slot in self.slots:
            if slot.is_free and self.queue:
                video = self.queue.pop(0)
                slot.start(video, self.save_dir)

    def relay_log(self, level, msg):
        self.send_log_signal.emit(level, msg)

    def reset_ui(self):
        self.download_btn.setEnabled(True)
        self.download_btn.setText("İndirmeyi Başlat")

    def check_history(self, video_id):
        if not video_id or not os.path.exists(self.history_file):
            return False
        with open(self.history_file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if video_id in line:  return True
        return False

    def save_to_history(self, video_id, title, size, duration, date): # Multi-thread indirme olduğu için dosyaya tek bir noktadan yazmak veriyi güvende tutar
        if not video_id: return
        self.batch_success_count += 1
        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(f"{video_id} | {title} | {size} | {duration} | {date}\n")

    def show_history_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("İndirme Geçmişi")
        dialog.resize(700, 450)
        
        dialog.setStyleSheet(DIALOG_MAIN_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_lbl = QLabel("📂 Geçmiş İndirilen Videolar")
        title_lbl.setStyleSheet(DIALOG_TITLE_STYLE)
        layout.addWidget(title_lbl)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Video Adı", "Boyut", "Süre", "İndirilme Tarihi"])
        
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(False)
        table.setShowGrid(True)
        
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                table.setRowCount(len(lines))
                
                for row_idx, line in enumerate(reversed(lines)):
                    parts = [p.strip() for p in line.split('|')]
                    title = parts[1] if len(parts) > 1 else "Bilinmiyor"
                    
                    if len(parts) >= 5:
                        size = parts[2]
                        duration = parts[3]
                        date = parts[4]
                    elif len(parts) == 4:
                        size = "-"
                        duration = parts[2]
                        date = parts[3]
                    else:
                        size = "-"
                        duration = "-"
                        date = "-"
                    
                    title_item = QTableWidgetItem(title)
                    table.setItem(row_idx, 0, title_item)
                    
                    size_item = QTableWidgetItem(size)
                    size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(row_idx, 1, size_item)
                    
                    dur_item = QTableWidgetItem(duration)
                    dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(row_idx, 2, dur_item)
                    
                    date_item = QTableWidgetItem(date)
                    date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(row_idx, 3, date_item)
        else:
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem("Henüz hiç video indirilmedi."))
            table.setItem(0, 1, QTableWidgetItem("-"))
            table.setItem(0, 2, QTableWidgetItem("-"))
            table.setItem(0, 3, QTableWidgetItem("-"))

        layout.addWidget(table)
        
        close_btn = QPushButton("Kapat")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(DIALOG_CLOSE_BTN_STYLE)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.exec()
