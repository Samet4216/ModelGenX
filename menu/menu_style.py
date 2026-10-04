"""
ModelGenX Arayüz Renk ve Stil Tanımlamaları
Bu dosya projenin tüm tema renklerini ve CSS/QSS stillerini tek bir merkezde toplar.
"""

# ----------------- TEMA RENKLERİ ----------------- #
COLORS = {
    "BG_MAIN": "#030610",         # Çok koyu siyahımsı lacivert ana zemin
    "BG_PANEL": "#080F1C",        # Kartlar, üst bar ve kenar çubuğu zemini
    "BORDER": "#15243B",          # Çerçeve ve kenarlık rengi
    "BORDER_HOVER": "#1E3557",    # Üzerine gelince kenarlık / buton rengi
    "ACCENT_BLUE": "#70C4FF",     # Modül isimleri, başlıklar ve aktif vurgu açık mavi
    "TEXT_PRIMARY": "#E4F9ED",    # Okunabilir açık yeşilimsi beyaz metin
    "TEXT_MUTED": "#9BAEBC",      # İkincil soluk açıklama metinleri
    "TEXT_HEADER": "#4A85A3",     # Kategori üst başlıkları
}

# ----------------- GENEL ARAYÜZ STİLİ (BRAND_STYLE) ----------------- #
BRAND_STYLE = f"""
QMainWindow {{
    background-color: {COLORS['BG_MAIN']};
}}

QWidget {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
    color: {COLORS['TEXT_PRIMARY']};
}}

/* Scroll Area */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    border: none;
    background: {COLORS['BG_MAIN']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['BORDER']};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['BORDER_HOVER']};
}}

/* Category Card */
QFrame#CategoryCard {{
    background-color: {COLORS['BG_PANEL']};
    border: 1px solid {COLORS['BORDER']};
    border-radius: 14px;
    padding: 16px;
}}
QFrame#CategoryCard:hover {{
    border: 1px solid {COLORS['BORDER_HOVER']};
}}

/* Dashboard Module Button */
QPushButton#ModuleBtn {{
    background-color: {COLORS['BG_MAIN']};
    border: 1px solid {COLORS['BORDER']};
    border-radius: 10px;
    color: {COLORS['ACCENT_BLUE']};
    padding: 6px 16px;
    min-height: 44px;
    text-align: left;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#ModuleBtn:hover {{
    background-color: {COLORS['BORDER']};
    border: 1px solid {COLORS['BORDER_HOVER']};
    color: #FFFFFF;
}}
QPushButton#ModuleBtn:pressed {{
    background-color: {COLORS['BORDER_HOVER']};
}}

/* Sidebar Styling */
QFrame#Sidebar {{
    background-color: {COLORS['BG_PANEL']};
    border-right: 1px solid {COLORS['BORDER']};
}}

QPushButton#SidebarCategoryHeader {{
    text-align: left;
    background: transparent;
    border: none;
    color: {COLORS['TEXT_HEADER']};
    font-size: 12px;
    font-weight: 700;
    padding: 8px 12px 4px 12px;
}}

QPushButton#SidebarModuleBtn {{
    text-align: left;
    background-color: transparent;
    border: none;
    border-radius: 8px;
    color: {COLORS['ACCENT_BLUE']};
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#SidebarModuleBtn:hover {{
    background-color: {COLORS['BORDER']};
    color: #FFFFFF;
}}
QPushButton#SidebarModuleBtn[active="true"] {{
    background-color: {COLORS['BORDER_HOVER']};
    color: #FFFFFF;
    font-weight: bold;
}}

/* Top Bar */
QFrame#TopBar {{
    background-color: {COLORS['BG_PANEL']};
    border-bottom: 1px solid {COLORS['BORDER']};
    padding: 10px 20px;
}}

QPushButton#NavBtn {{
    background-color: {COLORS['BORDER']};
    border: 1px solid {COLORS['BORDER']};
    border-radius: 8px;
    color: {COLORS['ACCENT_BLUE']};
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#NavBtn:hover {{
    background-color: {COLORS['BORDER_HOVER']};
    color: #FFFFFF;
}}
"""

# ----------------- HAMBURGER MENÜ BUTON STİLLERİ ----------------- #
HAMBURGER_EXPANDED = f"""
QPushButton {{
    background-color: {COLORS['BORDER']};
    border: 1px solid {COLORS['BORDER_HOVER']};
    border-radius: 8px;
    color: {COLORS['ACCENT_BLUE']};
    font-size: 12px;
    font-weight: bold;
    padding: 10px 12px;
    text-align: left;
}}
QPushButton:hover {{
    background-color: {COLORS['BORDER_HOVER']};
    color: #FFFFFF;
}}
"""

HAMBURGER_COLLAPSED = f"""
QPushButton {{
    background-color: {COLORS['BORDER']};
    border: 1px solid {COLORS['BORDER_HOVER']};
    border-radius: 8px;
    color: {COLORS['ACCENT_BLUE']};
    font-size: 18px;
    font-weight: bold;
    padding: 8px 0px;
    text-align: center;
}}
QPushButton:hover {{
    background-color: {COLORS['BORDER_HOVER']};
    color: #FFFFFF;
}}
"""

# ----------------- KATEGORİ RENK TEMALARI ----------------- #
# K1: Kapalı Kırmızı, K2: Kapalı Mor, K3: Kapalı Gri, K4: Kapalı Yeşil
CATEGORY_THEMES = [
    {  # K1: Kapalı Kırmızı
        "inactive_stripe": "#8B1E28",
        "active_stripe": "#B82835",
        "active_border": "#4D1017",
        "active_bg": "#14070A",
        "active_text": "#FFA8AF",
        "tab_active_bg": "#2A0B12",
        "tab_active_border": "#7A1A24",
        "tab_active_stripe": "#FF3B4E",
        "tab_active_text": "#FFFFFF",
    },
    {  # K2: Kapalı Mor
        "inactive_stripe": "#5E2779",
        "active_stripe": "#8A37B3",
        "active_border": "#351247",
        "active_bg": "#110618",
        "active_text": "#DBA3F5",
        "tab_active_bg": "#1F0A2C",
        "tab_active_border": "#5E1E82",
        "tab_active_stripe": "#BD42FA",
        "tab_active_text": "#FFFFFF",
    },
    {  # K3: Kapalı Gri / Beyazlı
        "inactive_stripe": "#5A677B",
        "active_stripe": "#E2E8F0",
        "active_border": "#64748B",
        "active_bg": "#2E3A4B",
        "active_text": "#FFFFFF",
        "tab_active_bg": "#283445",
        "tab_active_border": "#64748B",
        "tab_active_stripe": "#F1F5F9",
        "tab_active_text": "#FFFFFF",
    },
    {  # K4: Kapalı Yeşil
        "inactive_stripe": "#1B5E38",
        "active_stripe": "#288852",
        "active_border": "#0F331F",
        "active_bg": "#05140C",
        "active_text": "#7EE5A7",
        "tab_active_bg": "#0A2616",
        "tab_active_border": "#1B663A",
        "tab_active_stripe": "#2FE07A",
        "tab_active_text": "#FFFFFF",
    },
]

# ----------------- SOL DİKEY KATEGORİ ÇUBUĞU STİLLERİ ----------------- #
VERTICAL_BAR_STYLE = """
QFrame {
    background-color: #060C17;
    border-right: 1px solid #101E33;
}
"""

VERTICAL_LOGO_BTN_STYLE = """
QPushButton {
    background-color: #091322;
    border: 1px solid #15243B;
    border-radius: 8px;
}
QPushButton:hover {
    border: 1px solid #70C4FF;
    background-color: #0E1B33;
}
"""

VERTICAL_SEP_STYLE = """
background-color: #101E33;
border: none;
"""

def get_category_button_style(cat_idx: int, active: bool = False) -> str:
    """K1-K4 butonlarının aktif/pasif stillerini ve sağ kenar şerit renklerini döner."""
    theme = CATEGORY_THEMES[cat_idx % len(CATEGORY_THEMES)]
    if active:
        return f"""
            QPushButton {{
                background-color: {theme['active_bg']};
                border: 1px solid {theme['active_border']};
                border-right: 4px solid {theme['active_stripe']};
                border-radius: 6px;
                color: {theme['active_text']};
                font-size: 13px;
                font-weight: bold;
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: #050B14;
                border: 1px solid #0F1D33;
                border-right: 4px solid {theme['inactive_stripe']};
                border-radius: 6px;
                color: #7A8B9E;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0E1B33;
                border: 1px solid #1E3557;
                border-right: 4px solid {theme['active_stripe']};
                color: #FFFFFF;
            }}
        """

# ----------------- ÜST YATAY MODÜL ÇUBUĞU STİLLERİ ----------------- #
TOP_BAR_STYLE = """
QFrame {
    background-color: #060C17;
    border-bottom: 1px solid #101E33;
}
"""

def get_top_module_button_style(cat_idx: int = 0, active: bool = False) -> str:
    """Üst bar sekmelerinin (1.1 MODÜL vb.) aktif kategori rengine göre belirgin kutu stilini döner."""
    theme = CATEGORY_THEMES[cat_idx % len(CATEGORY_THEMES)]
    if active:
        return f"""
            QPushButton {{
                background-color: {theme['tab_active_bg']};
                border: 1px solid {theme['tab_active_border']};
                border-bottom: 3px solid {theme['tab_active_stripe']};
                border-radius: 6px;
                color: {theme['tab_active_text']};
                font-size: 13px;
                font-weight: bold;
                padding: 0 18px;
            }}
        """
    else:
        return """
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-bottom: 3px solid transparent;
                border-radius: 6px;
                color: #5A7699;
                font-size: 13px;
                font-weight: 500;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #0E1B33;
                border: 1px solid #1E3557;
                color: #B0C4DE;
            }
        """

# ----------------- ALT SİSTEM DURUM ÇUBUĞU STİLİ ----------------- #
STATUS_BAR_STYLE = """
QFrame#SystemStatusBar {
    background-color: #040812;
    border-top: 1px solid #101E33;
}
"""
