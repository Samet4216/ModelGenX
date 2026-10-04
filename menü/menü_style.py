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
    padding: 14px 16px;
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
