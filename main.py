import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QFrame, QStackedWidget,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTime
from PyQt6.QtGui import QFont, QIcon, QColor
from log.log_paneli import LogPanelWidget
from menü.modül import SidebarWidget
from menü.menü_style import BRAND_STYLE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModelGenX - Masaüstü Arayüz Tasarımı")
        self.resize(1200, 750)
        self.setMinimumSize(950, 600)
        self.setStyleSheet(BRAND_STYLE)

        # Veri Yapısı
        self.categories = [
            {
                "id": 1,
                "name": "Kategori 1",
                "desc": "Temel İşlemler & Ayarlar",
                "modules": ["Modül 1.1", "Modül 1.2", "Modül 1.3"]
            },
            {
                "id": 2,
                "name": "Kategori 2",
                "desc": "Veri Analizi & Filtreleme",
                "modules": ["Modül 2.1", "Modül 2.2", "Modül 2.3"]
            },
            {
                "id": 3,
                "name": "Kategori 3",
                "desc": "Model Eğitimi & Üretim",
                "modules": ["Modül 3.1", "Modül 3.2", "Modül 3.3"]
            },
            {
                "id": 4,
                "name": "Kategori 4",
                "desc": "Dışa Aktarma & Raporlama",
                "modules": ["Modül 4.1", "Modül 4.2", "Modül 4.3"]
            }
        ]

        self.current_cat_name = ""
        self.current_mod_name = ""
        self.sidebar_buttons = {}

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.dashboard_page = self.create_dashboard_page()
        self.stacked_widget.addWidget(self.dashboard_page)

        self.module_page = self.create_module_page()
        self.stacked_widget.addWidget(self.module_page)

        self.stacked_widget.setCurrentIndex(0)

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(24)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)
        
        title = QLabel("ModelGenX")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #70C4FF;") # Açık Mavi
        
        subtitle = QLabel("Lütfen çalışmak istediğiniz kategoriyi ve alt modülü seçin.")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #9BAEBC;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)

        grid_container = QWidget()
        grid = QGridLayout(grid_container)
        grid.setSpacing(24)
        grid.setContentsMargins(0, 10, 0, 0)

        for idx, cat in enumerate(self.categories):
            row = idx // 2
            col = idx % 2
            card = self.create_category_card(cat)
            grid.addWidget(card, row, col)

        layout.addWidget(grid_container)
        layout.addStretch()
        return page

    def create_category_card(self, cat):
        card = QFrame()
        card.setObjectName("CategoryCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)

        cat_title = QLabel(cat["name"])
        cat_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        cat_title.setStyleSheet("color: #70C4FF;") # Açık Mavi
        cat_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(cat_title)

        cat_desc = QLabel(cat["desc"])
        cat_desc.setStyleSheet("color: #9BAEBC; font-size: 13px; margin-bottom: 12px;")
        cat_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(cat_desc)

        for mod_name in cat["modules"]:
            btn = QPushButton(f"▶  {mod_name}")
            btn.setObjectName("ModuleBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=cat["name"], m=mod_name: self.open_module_view(c, m))
            card_layout.addWidget(btn)

        return card

    def create_module_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(16, 12, 16, 12)

        back_btn = QPushButton("⬅ Ana Menüye Dön")
        back_btn.setObjectName("NavBtn")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.back_to_dashboard)
        top_bar_layout.addWidget(back_btn)

        self.breadcrumb_label = QLabel("Kategori 1 > Modül 1.1")
        self.breadcrumb_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self.breadcrumb_label.setStyleSheet("color: #70C4FF; margin-left: 16px;") # Açık Mavi
        top_bar_layout.addWidget(self.breadcrumb_label)

        top_bar_layout.addStretch()
        page_layout.addWidget(top_bar)

        content_row = QWidget()
        content_row_layout = QHBoxLayout(content_row)
        content_row_layout.setContentsMargins(0, 0, 0, 0)
        content_row_layout.setSpacing(0)

        # 1. SOL KENAR ÇUBUĞU (menü/modül.py dosyasından gelen katlanabilir hamburger menü)
        self.sidebar_widget = SidebarWidget(self.categories)
        self.sidebar_widget.module_clicked.connect(self.open_module_view)
        content_row_layout.addWidget(self.sidebar_widget)

        # 2. ORTA ÇALIŞMA ALANI (Modül Ekranı)
        self.center_area = self.create_center_workspace()
        content_row_layout.addWidget(self.center_area, stretch=1)

        # 3. SAĞ LOG ÇEKMECESİ (Harici dosyadan LogPanelWidget)
        self.log_panel_widget = LogPanelWidget()
        content_row_layout.addWidget(self.log_panel_widget)

        page_layout.addWidget(content_row, stretch=1)
        return page

    def create_center_workspace(self):
        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #030610;")
        layout = QVBoxLayout(center_widget)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(20)

        self.mod_title_label = QLabel("Modül İçeriği")
        self.mod_title_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.mod_title_label.setStyleSheet("color: #70C4FF;") # Açık Mavi
        layout.addWidget(self.mod_title_label)

        self.mod_desc_label = QLabel("Bu modülün içerikleri ve araçları buraya gelecek.")
        self.mod_desc_label.setFont(QFont("Segoe UI", 13))
        self.mod_desc_label.setStyleSheet("color: #9BAEBC;")
        layout.addWidget(self.mod_desc_label)

        self.module_content_area = QFrame()
        self.module_content_area.setStyleSheet("""
            background-color: #080F1C;
            border: 1px dashed #15243B;
            border-radius: 12px;
        """)
        
        layout.addWidget(self.module_content_area, stretch=1)
        return center_widget

    def open_module_view(self, cat_name, mod_name):
        self.current_cat_name = cat_name
        self.current_mod_name = mod_name

        self.breadcrumb_label.setText(f"{cat_name}  ❯  {mod_name}")
        self.mod_title_label.setText(f"{mod_name} Yönetim Alanı")
        self.mod_desc_label.setText(f"{cat_name} altındaki {mod_name} modülünün aktif çalışma ekranı.")

        self.sidebar_widget.set_active_module(cat_name, mod_name)

        self.stacked_widget.setCurrentIndex(1)
        self.log_panel_widget.append_log(f"'{cat_name} > {mod_name}' modülüne geçiş yapıldı.", "INFO")

    def back_to_dashboard(self):
        self.stacked_widget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
