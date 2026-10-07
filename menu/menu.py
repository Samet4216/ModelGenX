"""
ModelGenX Menü ve Navigasyon Modülü (menu.py)
Bu dosya uygulamanın sol dikey kategori çubuğunu ve üst yatay modül sekmelerini yönetir.
Tüm CSS/QSS stilleri menu_style.py dosyasından beslenir.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon

from menu.menu_style import (
    VERTICAL_BAR_STYLE,
    VERTICAL_LOGO_BTN_STYLE,
    VERTICAL_SEP_STYLE,
    TOP_BAR_STYLE,
    get_category_button_style,
    get_top_module_button_style,
)

class VerticalCategoryBar(QFrame):
    """
    Sol Dikey Kenar Çubuğu:
    - En üstte logo (Ana ekrana dönüş)
    - Koyu renkli, emojisiz, büyük harfli K1, K2, K3, K4 butonları
    - Her butonun sağında kendi kalın tema rengi (Kapalı Kırmızı, Kapalı Mor, Kapalı Gri, Kapalı Yeşil)
    """
    category_clicked = pyqtSignal(dict) # Kategori tıklandığında sözlüğü iletir
    home_clicked = pyqtSignal()         # Logoya tıklandığında ana ekrana döner

    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.category_buttons = {}
        self.category_indices = {}
        self.active_category_id = None
        
        self.is_expanded = False
        self.collapsed_width = 64
        self.expanded_width = 200
        self.init_ui()

    def init_ui(self):
        self.setFixedWidth(self.collapsed_width)
        self.setStyleSheet(VERTICAL_BAR_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 12, 6, 12)
        layout.setSpacing(18) # K'lar arası yukarı-aşağı boşluk
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 0. Toggle Butonu (Hamburger)
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedHeight(32)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #70C4FF;
                font-size: 20px;
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_menu)
        layout.addWidget(self.toggle_btn)

        # 1. En Üst Logo Butonu (Dashboard'a dönüş)
        self.logo_btn = QPushButton()
        self.logo_btn.setFixedHeight(46)
        self.logo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logo_btn.setToolTip("Ana Menüye Dön")
        self.logo_btn.setStyleSheet(VERTICAL_LOGO_BTN_STYLE)
        logo_pixmap = QPixmap("resimler/logo.png")
        if not logo_pixmap.isNull():
            self.logo_btn.setIcon(QIcon(logo_pixmap))
            self.logo_btn.setIconSize(QSize(32, 32))
        self.logo_btn.clicked.connect(self.home_clicked.emit)
        layout.addWidget(self.logo_btn)

        # İnce ayırıcı çizgi
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(VERTICAL_SEP_STYLE)
        layout.addWidget(sep)

        # 2. Koyu Renkli K1, K2, K3, K4 Butonları (Sağlarında Kalın Renkli Şeritler)
        for idx, cat in enumerate(self.categories):
            cat_id = cat.get("id", idx + 1)
            
            btn = QPushButton(f"K{cat_id}")
            btn.setFixedHeight(44)
            from PyQt6.QtWidgets import QSizePolicy
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(f"{cat.get('name', '')} ({cat.get('desc', '')})")
            btn.setStyleSheet(get_category_button_style(idx, False))
            btn.clicked.connect(lambda checked, c=cat: self.on_category_pressed(c))

            layout.addWidget(btn)
            self.category_buttons[cat_id] = btn
            self.category_indices[cat_id] = idx
            
        layout.addStretch()
        
        self.sidebar_exit_btn = QPushButton("✕")
        self.sidebar_exit_btn.setFixedHeight(44)
        self.sidebar_exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar_exit_btn.setToolTip("Uygulamadan Çık")
        self.sidebar_exit_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #FF5252;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid transparent;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5E1015;
                border: 1px solid #B31D28;
            }
        """)
        from PyQt6.QtWidgets import QApplication
        self.sidebar_exit_btn.clicked.connect(lambda: QApplication.instance().quit())
        layout.addWidget(self.sidebar_exit_btn)

        from PyQt6.QtCore import QVariantAnimation, QEasingCurve
        self.animation = QVariantAnimation()
        self.animation.setDuration(280)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.valueChanged.connect(self.setFixedWidth)

    def toggle_menu(self):
        self.is_expanded = not self.is_expanded
        
        # Yazıları güncelle
        for cid, btn in self.category_buttons.items():
            idx = self.category_indices.get(cid, 0)
            cat = self.categories[idx]
            
            if self.is_expanded:
                btn.setText(cat.get("name", f"Kategori {cid}"))
            else:
                btn.setText(f"K{cid}")
                
        if self.is_expanded:
            self.sidebar_exit_btn.setText("Çıkış")
        else:
            self.sidebar_exit_btn.setText("✕")
                
        # Animasyonu başlat
        self.animation.stop()
        if self.is_expanded:
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.expanded_width)
        else:
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.collapsed_width)
        self.animation.start()

    def on_category_pressed(self, cat): # K1-K4 butonlarından birine tıklandığında aktif kategori olarak işaretler ve sinyal gönderir
        self.set_active_category(cat.get("id"))
        self.category_clicked.emit(cat)

    def set_active_category(self, cat_id): # K1-K4 butonlarından birini aktif/pasif yapar ve sağ kenar şerit rengini değiştirir
        self.active_category_id = cat_id
        for cid, btn in self.category_buttons.items():
            idx = self.category_indices.get(cid, 0)
            btn.setStyleSheet(get_category_button_style(idx, cid == cat_id))

class TopModuleBar(QFrame):
    """
    Üst Yatay Modül Çubuğu:
    - Seçili kategorinin alt modüllerini sağa doğru yatay sekmeler (tab) halinde açar
    - Örn: 1.1 MODÜL   1.2 MODÜL   1.3 MODÜL
    """
    module_clicked = pyqtSignal(str, str) # cat_name, mod_name
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_category = None
        self.active_mod_name = None
        self.module_buttons = {}
        self.init_ui()

    def init_ui(self): # Üst yatay modül çubuğu ve sekmelerin (tab) oluşturulması
        self.setFixedHeight(56)
        self.setStyleSheet(TOP_BAR_STYLE)

        self.bar_layout = QHBoxLayout(self)
        self.bar_layout.setContentsMargins(18, 7, 18, 7)
        self.bar_layout.setSpacing(8)

        # Modüllerin dinamik olarak dizileceği yatay konteyner
        self.tabs_layout = QHBoxLayout()
        self.tabs_layout.setSpacing(6)
        self.bar_layout.addLayout(self.tabs_layout)
        self.bar_layout.addStretch()

    def load_category_modules(self, cat, active_mod_name=None): #seçilen kategoriye ait modülleri yükler
        self.current_category = cat
        self.module_buttons.clear() 

        # Eski sekmeleri temizle
        while self.tabs_layout.count():
            item = self.tabs_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()

        modules = cat.get("modules", [])
        cat_name = cat.get("name", "")

        for mod_name in modules: # "Modül 1.1" -> "1.1 MODÜL" formatına dönüştürme
            if " " in mod_name and ("modül" in mod_name.lower() or "modul" in mod_name.lower()):
                parts = mod_name.split()
                tab_text = f"{parts[1]} {parts[0].upper()}"
            else: tab_text = mod_name.upper()

            btn = QPushButton(tab_text)
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=cat_name, m=mod_name: self.on_module_pressed(c, m))
            
            self.tabs_layout.addWidget(btn)
            self.module_buttons[mod_name] = btn

        # İstenen veya ilk modülü aktif yap
        target_mod = active_mod_name if active_mod_name in modules else (modules[0] if modules else None)
        if target_mod: self.set_active_module(target_mod)

    def on_module_pressed(self, cat_name, mod_name):
        self.set_active_module(mod_name)
        self.module_clicked.emit(cat_name, mod_name)

    def set_active_module(self, mod_name):
        self.active_mod_name = mod_name
        cat_idx = (self.current_category.get("id", 1) - 1) if self.current_category else 0
        for mname, btn in self.module_buttons.items():
            btn.setStyleSheet(get_top_module_button_style(cat_idx, mname == mod_name))
