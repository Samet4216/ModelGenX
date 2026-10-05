import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QProgressBar, QFileDialog, QMessageBox,
                             QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from Frame_islemleri.indirme_modulu.downloader import InfoExtractorThread, DownloadWorker

class DownloadSlotWidget(QWidget):
    slot_freed = pyqtSignal() # İndirme bitince veya hata verince ana kuyruğa haber vermek için
    
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.worker = None
        self.setMinimumHeight(45) # Slotları biraz daha büyüttüm
        self.setup_ui()
        self.hide() # Başlangıçta gizli

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # Durum İkonu (Kum saati, tik veya çarpı)
        self.icon_lbl = QLabel("⏳")
        self.icon_lbl.setFixedWidth(25)
        
        # Video Adı
        self.title_lbl = QLabel("")
        self.title_lbl.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: bold;")
        
        # İlerleme Çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(24) # Bar çubuğu daha kalın ve belirgin
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_progress_style(0)
        
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.title_lbl, stretch=1)
        layout.addWidget(self.progress_bar, stretch=2)

    def update_progress_style(self, value):
        # Kırmızıdan (#B80000) Yeşile (#10B981) dinamik renk geçişi
        r = int(184 + (16 - 184) * (value / 100.0))
        g = int(0 + (185 - 0) * (value / 100.0))
        b = int(0 + (129 - 0) * (value / 100.0))
        color_hex = f"#{r:02X}{g:02X}{b:02X}"

        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #060C17;
                border: 1px solid #1E293B;
                border-radius: 12px;
                color: white;
                font-weight: bold;
                font-size: 13px; /* Yüzdelik yazısı daha büyük */
            }}
            QProgressBar::chunk {{
                background-color: {color_hex};
                border-radius: 11px;
            }}
        """)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.update_progress_style(value)

    def start(self, video_dict, save_dir):
        self.show()
        self.icon_lbl.setText("⬇️")
        
        # İsmi kısaltarak gösterelim ki bar taşmasın
        short_title = video_dict['title'][:35] + "..." if len(video_dict['title']) > 35 else video_dict['title']
        self.title_lbl.setText(short_title)
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
        self.icon_lbl.setText("✅")
        self.title_lbl.setText(f"Tamamlandı: {title[:25]}...")
        
        # Ana sınıftaki history fonksiyonunu çağırarak thread safe bir şekilde dosyaya yazıyoruz
        self.parent_app.save_to_history(video_id, title, size, duration, date)
        
        # Log paneline başarılı indirme mesajı gönderiyoruz
        self.parent_app.relay_log("BİL", f"İndirme Tamamlandı: {title}")
        
        # 1.5 saniye ekranda ✅ kaldıktan sonra bar kaybolur ve yerini yeni videoya bırakır
        QTimer.singleShot(1500, self.free_slot)

    def on_error(self, err_msg):
        self.icon_lbl.setText("❌")
        self.title_lbl.setText("İndirme Hatası!")
        
        # 3 saniye sonra kaybolur
        QTimer.singleShot(3000, self.free_slot)

    def free_slot(self):
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

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title_lbl = QLabel("🎥 YouTube Video İndirici")
        title_lbl.setStyleSheet("color: #E2E8F0; font-size: 26px; font-weight: bold; letter-spacing: 1px;")
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        self.history_btn = QPushButton("📜 Geçmişi Gör")
        self.history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #CBD5E1;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1E293B;
                border: 1px solid #475569;
                color: #FFFFFF;
            }
        """)
        self.history_btn.clicked.connect(self.show_history_dialog)
        header_layout.addWidget(self.history_btn)
        
        desc_lbl = QLabel("Aynı anda 4 adede kadar video indirebilirsiniz. Playlist linki girildiğinde sıraya alınır.")
        desc_lbl.setStyleSheet("color: #94A3B8; font-size: 14px;")

        # --- Link Girişi ---
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        url_label = QLabel("Video veya Playlist Linki:")
        url_label.setStyleSheet("color: #CBD5E1; font-weight: bold; font-size: 14px;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Örn: https://www.youtube.com/watch?v=...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #030610;
                border: 2px solid #1E293B;
                border-radius: 10px;
                padding: 15px;
                color: #FFFFFF;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #B80000;
                background-color: #060C17;
            }
        """)
        input_layout.addWidget(url_label)
        input_layout.addWidget(self.url_input)

        # --- Klasör Seçimi ---
        save_layout = QHBoxLayout()
        self.save_path_lbl = QLabel(f"Kayıt Yeri: {self.save_dir}")
        self.save_path_lbl.setStyleSheet("color: #64748B; font-size: 13px;")
        change_dir_btn = QPushButton("📂 Klasör Değiştir")
        change_dir_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #CBD5E1;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E293B;
                border: 1px solid #475569;
                color: #FFFFFF;
            }
        """)
        change_dir_btn.clicked.connect(self.choose_directory)
        save_layout.addWidget(self.save_path_lbl)
        save_layout.addStretch()
        save_layout.addWidget(change_dir_btn)

        # --- 4'lü Paralel İndirme Slotları (Alt Alta) ---
        self.slots_container = QVBoxLayout()
        self.slots_container.setSpacing(5)
        for _ in range(4):
            slot = DownloadSlotWidget(self)
            slot.slot_freed.connect(self.process_queue)
            self.slots_container.addWidget(slot)
            self.slots.append(slot)

        # --- İndirme Butonu ---
        self.download_btn = QPushButton("İndirmeyi Başlat")
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.setFixedHeight(55)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #B80000;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #D30000;
            }
            QPushButton:disabled {
                background-color: #334155;
                color: #94A3B8;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)

        layout.addLayout(header_layout)
        layout.addWidget(desc_lbl)
        layout.addSpacing(15)
        layout.addLayout(input_layout)
        layout.addLayout(save_layout)
        layout.addSpacing(20) # Daha fazla boşluk
        layout.addLayout(self.slots_container)
        layout.addSpacing(20) # Daha fazla boşluk
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
            else:
                to_download.append(e)

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
            if all(not s.isVisible() for s in self.slots):
                self.reset_ui()
                self.relay_log("BİL", "Tüm indirme kuyruğu tamamlandı.")
            return

        # 4 tane slottan boş olanları bul ve kuyruktaki işleri ver
        for slot in self.slots:
            if not slot.isVisible() and self.queue:
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
                if video_id in line:
                    return True
        return False

    def save_to_history(self, video_id, title, size, duration, date):
        # Multi-thread indirme olduğu için dosyaya tek bir noktadan yazmak veriyi güvende tutar
        if not video_id: return
        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(f"{video_id} | {title} | {size} | {duration} | {date}\n")

    def show_history_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("İndirme Geçmişi")
        dialog.resize(700, 450)
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #060C17;
                border: 2px solid #1E293B;
                border-radius: 10px;
            }
            QTableWidget {
                background-color: #030610;
                color: #E2E8F0;
                gridline-color: #1E293B;
                border: 1px solid #1E293B;
                border-radius: 6px;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #70C4FF;
                padding: 8px;
                border: 1px solid #1E293B;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #15243B;
                color: #FFFFFF;
            }
            QScrollBar:vertical {
                background: #030610;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: #1E293B;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_lbl = QLabel("📂 Geçmiş İndirilen Videolar")
        title_lbl.setStyleSheet("color: #E2E8F0; font-size: 20px; font-weight: bold;")
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
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: white;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.exec()
