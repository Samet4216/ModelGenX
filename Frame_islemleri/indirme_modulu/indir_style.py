# Frame_islemleri/indirme_modulu/indir_style.py

APP_BG_STYLE = "background-color: transparent;"

TITLE_LBL_STYLE = "color: #E2E8F0; font-size: 24px; font-weight: bold; letter-spacing: 1px;"
DESC_LBL_STYLE = "color: #94A3B8; font-size: 13px;"
URL_LBL_STYLE = "color: #CBD5E1; font-weight: bold; font-size: 14px;"
SAVE_PATH_LBL_STYLE = "color: #64748B; font-size: 12px;"

URL_INPUT_STYLE = """
    QLineEdit {
        background-color: #030610;
        border: 2px solid #1E293B;
        border-radius: 10px;
        padding: 12px;
        color: #FFFFFF;
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 2px solid #70C4FF;
        background-color: #060C17;
    }
"""

HISTORY_BTN_STYLE = """
    QPushButton {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
        color: #CBD5E1;
        padding: 6px 12px;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #1E293B;
        border: 1px solid #475569;
        color: #FFFFFF;
    }
"""

CHANGE_DIR_BTN_STYLE = """
    QPushButton {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
        color: #CBD5E1;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1E293B;
        border: 1px solid #475569;
        color: #FFFFFF;
    }
"""

DOWNLOAD_BTN_STYLE = """
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
        background-color: #1E3A5F;
        border: 1px solid #70C4FF;
        color: #70C4FF;
    }
"""

# DownloadSlotWidget Styles
SLOT_TITLE_STYLE = "color: #E2E8F0; font-size: 14px; font-weight: bold;"
SLOT_PERCENT_DEFAULT_STYLE = "color: #70C4FF; font-size: 13px; font-weight: bold;"
SLOT_PERCENT_SUCCESS_STYLE = "color: #4ADE80; font-size: 13px; font-weight: bold;"
SLOT_PERCENT_ERROR_STYLE = "color: #EF4444; font-size: 13px; font-weight: bold;"

SLOT_PROGRESS_ERROR_STYLE = """
    QProgressBar {
        background-color: #1E293B;
        border: none;
        border-radius: 4px;
    }
    QProgressBar::chunk {
        background-color: #EF4444;
        border-radius: 4px;
    }
"""

def get_progress_style(value):
    if value == 100:
        color = "#4ADE80"
    else:
        color = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1E90FF, stop:1 #70C4FF)"
        
    return f"""
        QProgressBar {{
            background-color: #1E293B;
            border: none;
            border-radius: 4px;
        }}
        QProgressBar::chunk {{
            background: {color};
            border-radius: 4px;
        }}
    """

# Dialog Styles
DIALOG_MAIN_STYLE = """
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
"""

DIALOG_TITLE_STYLE = "color: #E2E8F0; font-size: 20px; font-weight: bold;"

DIALOG_CLOSE_BTN_STYLE = """
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
"""

# Context Menu (Aksiyon Menüsü) Style
ACTION_MENU_STYLE = """
    QMenu {
        background-color: #010603;
        color: #70C4FF;
        border: 1px solid #021206;
        font-size: 13px;
        border-radius: 4px;
    }
    QMenu::item {
        padding: 6px 20px;
    }
    QMenu::item:selected {
        background-color: #021206;
    }
    QMenu::item:disabled {
        color: #334155;
    }
"""

# Slot Icon Button Styles
SLOT_ICON_DEFAULT_STYLE = "background: transparent; border: none; font-size: 16px; color: #E2E8F0;"
SLOT_ICON_PAUSED_STYLE = "background: transparent; border: none; font-size: 16px; color: #70C4FF; font-weight: bold;"
SLOT_ICON_ERROR_STYLE = "background: transparent; border: none; font-size: 16px; color: #EF4444;"
