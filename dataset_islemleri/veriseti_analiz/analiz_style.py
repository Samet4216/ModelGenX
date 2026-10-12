# Veri Seti Analiz Modülü - Yeşil Tema Stil Dosyası

INPUT_STYLE = """
QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
    background-color: #050A15;
    border: 1px solid #15243B;
    border-radius: 8px;
    padding: 6px 10px;
    color: #FFFFFF;
    font-size: 10pt;
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #4CAF50;
}
QComboBox::drop-down {
    border: none;
}
"""

BTN_STYLE = """
QPushButton {
    background-color: #2E7D32;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 10pt;
}
QPushButton:hover {
    background-color: #43A047;
}
QPushButton:pressed {
    background-color: #1B5E20;
}
QPushButton:disabled {
    background-color: #15243B;
    color: #4A5B70;
}
"""

BTN_SECONDARY_STYLE = """
QPushButton {
    background-color: #0A1224;
    color: #81C784;
    border: 1px solid #2E7D32;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 9pt;
}
QPushButton:hover {
    background-color: #1B5E20;
    color: white;
}
"""

BTN_DANGER_STYLE = """
QPushButton {
    background-color: #5E1015;
    color: #FF8A8A;
    border: 1px solid #B31D28;
    border-radius: 4px;
    padding: 5px 10px;
    font-weight: bold;
    font-size: 9pt;
}
QPushButton:hover {
    background-color: #B31D28;
    color: white;
}
"""

TABLE_STYLE = """
QTableWidget {
    background-color: #050A15;
    alternate-background-color: #0B1325;
    color: #FFFFFF;
    border: 1px solid #15243B;
    border-radius: 8px;
    gridline-color: #15243B;
    font-size: 10pt;
}
QHeaderView::section {
    background-color: #0A1224;
    color: #4CAF50;
    padding: 5px;
    border: none;
    border-right: 1px solid #15243B;
    border-bottom: 1px solid #15243B;
    font-weight: bold;
}
QScrollBar:vertical {
    border: none;
    background: #050A15;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #15243B;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #2E7D32;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

STAT_CARD_STYLE = """
QFrame {
    background-color: #0A1224;
    border: 1px solid #15243B;
    border-radius: 8px;
}
"""

GROUP_BOX_STYLE = """
QGroupBox {
    border: 1px solid #15243B;
    border-radius: 8px;
    margin-top: 20px;
    padding-top: 15px;
    color: #4CAF50;
    font-weight: bold;
    font-size: 10pt;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    left: 10px;
}
"""

TAB_STYLE = """
QTabWidget::pane {
    border: 1px solid #15243B;
    border-radius: 8px;
    background-color: transparent;
    margin-top: -1px;
}
QTabBar::tab {
    background-color: #0A1224;
    color: #FFFFFF;
    border: 1px solid #15243B;
    padding: 10px 20px;
    margin-right: 5px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: bold;
    font-size: 10pt;
}
QTabBar::tab:selected {
    background-color: #2E7D32;
    color: #FFFFFF;
    border-bottom: 1px solid #2E7D32;
}
QTabBar::tab:hover:!selected {
    background-color: #15243B;
}
"""

SCROLL_AREA_STYLE = """
QScrollArea {
    border: 1px solid #1A2C4E;
    background-color: transparent;
    border-radius: 8px;
}
QScrollBar:vertical {
    border: none;
    background: #15243B;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #2D3A54;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #4A5A7B;
}
"""
