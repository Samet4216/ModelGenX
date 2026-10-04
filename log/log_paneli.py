import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QFileDialog, QMenu
)
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QTime
from PyQt6.QtGui import QFont, QAction

class LogPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._log_history = []  # Logları hafızada tutacağımız liste
        self.MAX_LINES = 1000   # Maksimum satır sınırı
        self.init_ui()

    def init_ui(self):
        container_layout = QHBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 1. Kenardaki Aç/Kapat Tutamacı (Dikdörtgen Buton)
        self.log_handle_btn = QPushButton("▶")
        self.log_handle_btn.setFixedSize(24, 60)
        self.log_handle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.log_handle_btn.setStyleSheet("""
            QPushButton {
                background-color: #010603; /* Koyu yeşil panel rengi */
                border: 1px solid #021206;
                border-right: none;
                border-top-left-radius: 6px;
                border-bottom-left-radius: 6px;
                color: #70C4FF; /* Açık Mavi ok */
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #021206;
            }
        """)
        self.log_handle_btn.clicked.connect(self.toggle_drawer)
        
        handle_layout = QVBoxLayout()
        handle_layout.addStretch()
        handle_layout.addWidget(self.log_handle_btn)
        handle_layout.addStretch()
        container_layout.addLayout(handle_layout)

        # 2. Asıl Log İçeriği
        self.log_content_frame = QFrame()
        self.log_content_frame.setObjectName("LogPanel")
        self.log_content_frame.setStyleSheet("""
            QFrame#LogPanel {
                background-color: #010603; /* En koyu yeşil */
                border-left: 1px solid #021206;
            }
        """)
        
        self.content_expanded_width = 340
        self.is_drawer_open = True
        self.log_content_frame.setFixedWidth(self.content_expanded_width)

        drawer_layout = QVBoxLayout(self.log_content_frame)
        drawer_layout.setContentsMargins(16, 16, 16, 16)
        drawer_layout.setSpacing(12)

        # Log Başlık Alanı
        log_header = QHBoxLayout()
        log_title = QLabel("📟 Sistem Logları")
        log_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        log_title.setStyleSheet("color: #70C4FF;") # Açık Mavi

        # Dışa Aktar Butonu
        export_btn = QPushButton("💾 İndir")
        export_btn.setObjectName("SmallBtn")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton#SmallBtn {
                background-color: #021206;
                border: 1px solid #021206;
                border-radius: 6px;
                color: #70C4FF;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#SmallBtn:hover {
                background-color: #092B13;
                color: #FFFFFF;
            }
        """)
        export_btn.clicked.connect(self.export_logs)
        export_btn.setToolTip("Logları bilgisayara kaydet")

        # Temizle Butonu
        clear_btn = QPushButton("🗑 Temizle")
        clear_btn.setObjectName("SmallBtn")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(export_btn.styleSheet()) # Aynı stili uygula
        clear_btn.clicked.connect(self.clear_logs)

        log_header.addWidget(log_title)
        log_header.addStretch()
        log_header.addWidget(export_btn)
        log_header.addWidget(clear_btn)
        drawer_layout.addLayout(log_header)

        # Arama ve Filtreleme Kutusu
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Loglarda ara (hata, bilgi, id vs.)...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #000301;
                border: 1px solid #021206;
                border-radius: 6px;
                color: #E4F9ED;
                padding: 6px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #092B13;
            }
        """)
        self.search_bar.textChanged.connect(self.on_search_changed)
        drawer_layout.addWidget(self.search_bar)

        # Log Metin Alanı
        self.log_output = QTextEdit()
        self.log_output.setObjectName("LogTextEdit")
        self.log_output.setStyleSheet("""
            QTextEdit#LogTextEdit {
                background-color: #000301;
                border: 1px solid #021206;
                border-radius: 8px;
                color: #E4F9ED;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        self.log_output.setReadOnly(True)
        # Performans için maksimum blok (satır) sayısı (HTML tabanlı render olduğu için faydalı, ama asıl limiti _log_history'de yöneteceğiz)
        self.log_output.document().setMaximumBlockCount(self.MAX_LINES)
        
        # Sağ Tık Menüsü Ayarı
        self.log_output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.log_output.customContextMenuRequested.connect(self.show_context_menu)
        
        drawer_layout.addWidget(self.log_output)

        # Log Alt Bilgisi
        log_footer = QLabel(f"Sadece son {self.MAX_LINES} işlem tutulur. Seçmek için sürükle, menü için sağ tıkla.")
        log_footer.setStyleSheet("color: #4A85A3; font-size: 11px;")
        log_footer.setWordWrap(True)
        drawer_layout.addWidget(log_footer)

        container_layout.addWidget(self.log_content_frame)

        # Animasyon Tanımlaması
        self.drawer_animation = QVariantAnimation()
        self.drawer_animation.setDuration(280)
        self.drawer_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.drawer_animation.valueChanged.connect(self.log_content_frame.setFixedWidth)

    def toggle_drawer(self):
        """Sağdan sola açılan ve sola doğru kapanan animasyon kontrolü"""
        current_width = self.log_content_frame.width()
        
        if self.is_drawer_open:
            self.drawer_animation.stop()
            self.drawer_animation.setStartValue(current_width)
            self.drawer_animation.setEndValue(0)
            self.drawer_animation.start()
            self.is_drawer_open = False
            self.log_handle_btn.setText("◀")
        else:
            self.drawer_animation.stop()
            self.drawer_animation.setStartValue(current_width)
            self.drawer_animation.setEndValue(self.content_expanded_width)
            self.drawer_animation.start()
            self.is_drawer_open = True
            self.log_handle_btn.setText("▶")

    def append_log(self, text, level="INFO"):
        """Log ekleme metodu. Renkli seviyeler (INFO, WARNING, ERROR, DEBUG, SYSTEM) destekler."""
        time_str = QTime.currentTime().toString("hh:mm:ss")
        
        # Seviyelere göre renkler
        colors = {
            "INFO": "#E4F9ED",     # Yeşilimsi beyaz
            "WARNING": "#F59E0B",  # Turuncu/Sarı
            "ERROR": "#EF4444",    # Kırmızı
            "DEBUG": "#8CA6BE",    # Soluk mavi/gri
            "SYSTEM": "#70C4FF"    # Açık mavi
        }
        color = colors.get(level.upper(), "#E4F9ED")
        
        # Gösterilecek HTML string'i
        html_str = f'<span style="color:#8CA6BE">[{time_str}]</span> <b style="color:{color}">[{level.upper()}]</b> <span style="color:#E4F9ED">{text}</span>'
        
        # Saf metin formatı (Export ve Arama için)
        raw_str = f"[{time_str}] [{level.upper()}] {text}"
        
        self._log_history.append({
            "raw": raw_str,
            "html": html_str
        })
        
        # Sınırı aşıyorsa eskiyi sil (Performans)
        if len(self._log_history) > self.MAX_LINES:
            self._log_history.pop(0)

        # Eğer arama çubuğu boşsa veya bu metin aramayla eşleşiyorsa ekranda göster
        search_query = self.search_bar.text().lower()
        if not search_query or search_query in raw_str.lower():
            self.log_output.append(html_str)
            # Otomatik aşağı kaydır
            scrollbar = self.log_output.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def on_search_changed(self, text):
        """Arama kutusuna bir şey yazıldığında logları filtreler."""
        self.log_output.clear()
        search_query = text.lower()
        
        for log in self._log_history:
            if not search_query or search_query in log["raw"].lower():
                self.log_output.append(log["html"])
                
        # Aşağı kaydır
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        """Tüm logları siler."""
        self.log_output.clear()
        self._log_history.clear()
        self.search_bar.clear()
        self.append_log("Log geçmişi temizlendi.", "SYSTEM")

    def export_logs(self):
        """Logları .txt veya .log olarak bilgisayara kaydeder."""
        if not self._log_history:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Logları Kaydet", "", "Metin Dosyaları (*.txt);;Log Dosyaları (*.log);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    for log in self._log_history:
                        f.write(log["raw"] + "\n")
                self.append_log(f"Loglar başarıyla kaydedildi: {os.path.basename(file_path)}", "SYSTEM")
            except Exception as e:
                self.append_log(f"Log kaydetme hatası: {str(e)}", "ERROR")

    def show_context_menu(self, pos):
        """Sağ tık menüsünü gösterir."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #010603;
                color: #70C4FF;
                border: 1px solid #021206;
            }
            QMenu::item:selected {
                background-color: #021206;
            }
        """)
        
        copy_action = menu.addAction("Kopyala")
        select_all_action = menu.addAction("Tümünü Seç")
        menu.addSeparator()
        clear_action = menu.addAction("Temizle")

        action = menu.exec(self.log_output.mapToGlobal(pos))
        
        if action == copy_action:
            self.log_output.copy()
        elif action == select_all_action:
            self.log_output.selectAll()
        elif action == clear_action:
            self.clear_logs()
