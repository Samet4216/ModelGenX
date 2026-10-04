import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QFrame, QStackedWidget,
    QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTime, QTimer, QDateTime
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap
from log.log_paneli import LogPanelWidget
from menu.modul import SidebarWidget
from menu.menu_style import BRAND_STYLE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModelGenX - Masaüstü Arayüz Tasarımı")
        self.setWindowIcon(QIcon("resimler/logo.png"))
        self.resize(1200, 750)
        self.setMinimumSize(950, 600)
        self.setStyleSheet(BRAND_STYLE)

        # Veri Yapısı (config.json dosyasından dinamik olarak yüklenir)
        self.categories = self.load_categories()

        self.current_cat_name = ""
        self.current_mod_name = ""

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
        layout.setContentsMargins(36, 18, 36, 18)
        layout.setSpacing(12)

        # ÜST BAŞLIK ALANI (Sol: 110x110 Logo + MODELGENX Başlığı, Sağ: Sade Tarih-Saat)
        top_header_row = QHBoxLayout()
        top_header_row.setContentsMargins(0, 0, 0, 0)
        top_header_row.setSpacing(20)

        # SOL: Logo ve Başlık Bloğu
        brand_container = QWidget()
        brand_layout = QHBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(18)
        brand_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # 1. Büyütülmüş Logo (Neon Glow / Işıma Efektli)
        logo_label = QLabel()
        logo_pixmap = QPixmap("resimler/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(105, 105, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # Neon Işıma (Glow) Efekti
        glow_effect = QGraphicsDropShadowEffect(logo_label)
        glow_effect.setBlurRadius(28)
        glow_effect.setColor(QColor(112, 196, 255, 150))
        glow_effect.setOffset(0, 0)
        logo_label.setGraphicsEffect(glow_effect)
        brand_layout.addWidget(logo_label)

        # 2. Logonun Hemen Sağındaki Başlık ve Slogan (Mavi Alan)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # İki Renkli Başlık (MODEL beyaz, GEN-X açık mavi)
        title = QLabel('<span style="color:#FFFFFF;">MODEL</span><span style="color:#70C4FF;">GEN-X</span>')
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setTextFormat(Qt.TextFormat.RichText)
        text_layout.addWidget(title)

        # Alt Slogan (DATASET GENERATOR)
        tagline = QLabel("DATASET GENERATOR")
        tagline.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        tagline.setStyleSheet("color: #70C4FF; letter-spacing: 3px;")
        text_layout.addWidget(tagline)

        brand_layout.addLayout(text_layout)
        top_header_row.addWidget(brand_container)

        top_header_row.addStretch()

        # SAĞ: Kutusuz ve Emojisiz Sade Tarih & Saat
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.datetime_label.setStyleSheet("""
            background: transparent;
            border: none;
            color: #8CA6BE;
            padding: 8px 0px;
        """)
        top_header_row.addWidget(self.datetime_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        layout.addLayout(top_header_row)

        # Altına İnce Gradyanlı Ayırıcı Çizgi (Divider)
        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(21, 36, 59, 0),
                stop:0.1 rgba(112, 196, 255, 60),
                stop:0.5 rgba(112, 196, 255, 200),
                stop:0.9 rgba(112, 196, 255, 60),
                stop:1 rgba(21, 36, 59, 0)
            );
            border: none;
            margin-top: 4px;
            margin-bottom: 2px;
        """)
        layout.addWidget(divider)

        # Tarih-Saat Zamanlayıcısı
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_datetime)
        self.clock_timer.start(1000)
        self.update_datetime()

        grid_container = QWidget()
        grid = QGridLayout(grid_container)
        grid.setSpacing(16)
        grid.setContentsMargins(0, 4, 0, 0)

        for idx, cat in enumerate(self.categories):
            row = idx // 2
            col = idx % 2
            card = self.create_category_card(cat)
            grid.addWidget(card, row, col)

        layout.addWidget(grid_container, 1)
        return page

    def create_category_card(self, cat):
        card = QFrame()
        card.setObjectName("CategoryCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(8)

        cat_title = QLabel(cat["name"])
        cat_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        cat_title.setStyleSheet("color: #70C4FF;") # Açık Mavi
        cat_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(cat_title)

        cat_desc = QLabel(cat["desc"])
        cat_desc.setStyleSheet("color: #9BAEBC; font-size: 13px; margin-bottom: 4px;")
        cat_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(cat_desc)

        for mod_name in cat["modules"]:
            btn = QPushButton(f"▶  {mod_name}")
            btn.setObjectName("ModuleBtn")
            btn.setMinimumHeight(44)
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

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        date_str = now.toString("dd.MM.yyyy")
        time_str = now.toString("hh:mm:ss")
        self.datetime_label.setText(f"{date_str}   {time_str}")

    def load_categories(self):
        config_path = os.path.join(os.path.dirname(__file__), "config_menu.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("categories", [])
            except Exception as e:
                print(f"Config hatası: {e}")
        return []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
