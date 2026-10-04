from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont

class SidebarWidget(QFrame):
    # Modül tıklandığında ana ekrana bildiren sinyal
    module_clicked = pyqtSignal(str, str) # kategori_ismi, modül_ismi

    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.sidebar_buttons = {}
        
        # Animasyon genişlikleri
        self.expanded_width = 260
        self.collapsed_width = 50
        self.is_expanded = True
        
        self.init_ui()

    def init_ui(self):
        self.setObjectName("Sidebar")
        self.setFixedWidth(self.expanded_width)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 14, 8, 14)
        self.main_layout.setSpacing(6)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Yeşil kutu ile gösterilen yer: Hamburger Menü Butonu & Başlık
        self.header_btn = QPushButton("☰   TÜM MODÜLLER")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.setStyleSheet("""
            QPushButton {
                background-color: #15243B;
                border: 1px solid #1E3557;
                border-radius: 8px;
                color: #70C4FF;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E3557;
                color: #FFFFFF;
            }
        """)
        self.header_btn.clicked.connect(self.toggle_sidebar)
        self.main_layout.addWidget(self.header_btn)
        
        # Modüllerin Listesi (Scroll Area) - Yukarı doğru katlanacak kısım
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 6, 0, 0)
        self.scroll_layout.setSpacing(6)
        
        for cat in self.categories:
            cat_header = QLabel(cat["name"].upper())
            cat_header.setStyleSheet("color: #4A85A3; font-size: 11px; font-weight: bold; margin-top: 8px; margin-left: 6px;")
            self.scroll_layout.addWidget(cat_header)

            for mod_name in cat["modules"]:
                btn = QPushButton(f"•  {mod_name}")
                btn.setObjectName("SidebarModuleBtn")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda checked, c=cat["name"], m=mod_name: self.module_clicked.emit(c, m))
                self.scroll_layout.addWidget(btn)
                
                self.sidebar_buttons[(cat["name"], mod_name)] = btn
                
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)
        
        # Katlanma / Açılma Animasyonu
        self.animation = QVariantAnimation()
        self.animation.setDuration(260)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.valueChanged.connect(self.setFixedWidth)

    def toggle_sidebar(self):
        """Hamburger menüye basıldığında modülleri yukarı/içeri katlar ve paneli küçültür."""
        self.animation.stop()
        if self.is_expanded:
            # Kapat: Modülleri yukarı katla ve paneli daralt
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.collapsed_width)
            self.header_btn.setText("☰")
            self.header_btn.setStyleSheet("""
                QPushButton {
                    background-color: #15243B;
                    border: 1px solid #1E3557;
                    border-radius: 8px;
                    color: #70C4FF;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 8px 0px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #1E3557;
                    color: #FFFFFF;
                }
            """)
            self.scroll_area.hide()
            self.is_expanded = False
        else:
            # Aç: Paneli genişlet ve modülleri geri aç
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.expanded_width)
            self.header_btn.setText("☰   TÜM MODÜLLER")
            self.header_btn.setStyleSheet("""
                QPushButton {
                    background-color: #15243B;
                    border: 1px solid #1E3557;
                    border-radius: 8px;
                    color: #70C4FF;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 10px 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #1E3557;
                    color: #FFFFFF;
                }
            """)
            self.scroll_area.show()
            self.is_expanded = True
            
        self.animation.start()

    def set_active_module(self, cat_name, mod_name):
        """Seçilen modülü renklendirir."""
        for key, btn in self.sidebar_buttons.items():
            if key == (cat_name, mod_name):
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)