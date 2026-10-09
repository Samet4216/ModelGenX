import os
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QComboBox, QFileDialog, QFrame, QWidget, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from Frame_islemleri.paylastirma_modulu.paylastirma_style import (
    BTN_STYLE, GROUP_BOX_STYLE, INPUT_STYLE, STAT_CARD_STYLE
)

class DropZoneFrame(QFrame):
    folder_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.icon_lbl = QLabel("📁")
        self.icon_lbl.setStyleSheet("font-size: 32px; background: transparent; border: none; color: #8CA6BE;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_lbl = QLabel("Kayıt Klasörünü Buraya Sürükleyin\nveya Tıklayıp Seçin")
        self.text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_lbl.setStyleSheet("color: #9BAEBC; font-size: 10pt; background: transparent; border: none; font-weight: bold;")
        
        self.path_lbl = QLabel("Seçilen Konum: Yok")
        self.path_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.path_lbl.setStyleSheet("color: #FF5252; font-size: 9pt; background: transparent; border: none; margin-top: 5px;")
        
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_lbl)
        layout.addWidget(self.path_lbl)
        
        self.set_default_style()
        self.setMinimumHeight(120)
        
    def set_default_style(self):
        self.setStyleSheet("""
            DropZoneFrame {
                border: 2px dashed #15243B;
                border-radius: 12px;
                background-color: #050A15;
            }
        """)
        
    def set_hover_style(self):
        self.setStyleSheet("""
            DropZoneFrame {
                border: 2px dashed #FF5252;
                border-radius: 12px;
                background-color: #0A1224;
            }
        """)

    def enterEvent(self, event):
        self.set_hover_style()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.set_default_style()
        super().leaveEvent(event)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.set_hover_style()
            
    def dragLeaveEvent(self, event):
        self.set_default_style()
        
    def dropEvent(self, event):
        self.set_default_style()
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                if os.path.isdir(path):
                    self.folder_selected.emit(path)
                    self.path_lbl.setText(f"Seçilen: {path}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            directory = QFileDialog.getExistingDirectory(self, "Kayıt Konumunu Seç")
            if directory:
                self.folder_selected.emit(directory)
                self.path_lbl.setText(f"Seçilen: {directory}")

class OutputConfigWidget(QGroupBox):
    
    def __init__(self, parent=None):
        super().__init__("Çıktı Konfigürasyonu", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.save_dir = ""
        
        # Injectable data sources
        self.data_source_videos = lambda: []
        self.data_source_annotators = lambda: []
        
        self.init_ui()
        self.update_preview()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 20, 15, 15)
        main_layout.setSpacing(20)
        
        left_panel = QVBoxLayout()
        
        name_layout = QVBoxLayout()
        name_label = QLabel("🎯 Hedef Klasör Adı:")
        name_label.setStyleSheet("color: #FF5252; font-weight: bold;")
        
        self.out_name_input = QLineEdit()
        self.out_name_input.setPlaceholderText("örn: veriseti_v1")
        self.out_name_input.setStyleSheet(INPUT_STYLE)
        self.out_name_input.textChanged.connect(self.update_preview)
        
        self.zip_checkbox = QCheckBox("📦 İşlem Bitince Otomatik ZIP'le")
        self.zip_checkbox.setStyleSheet("""
            QCheckBox {
                color: #8CA6BE;
                font-size: 10pt;
                font-weight: bold;
                padding-top: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                background-color: #050A15;
                border: 2px solid #1A2C4E;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #FF5252;
            }
            QCheckBox::indicator:checked {
                background-color: #FF5252;
                border: 2px solid #FF5252;
            }
        """)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.out_name_input)
        name_layout.addWidget(self.zip_checkbox)
        left_panel.addLayout(name_layout)
        
        left_panel.addSpacing(20)
        
        self.drop_zone = DropZoneFrame()
        self.drop_zone.folder_selected.connect(self.on_folder_selected)
        left_panel.addWidget(self.drop_zone)
        
        left_panel.addStretch()
        
        right_panel = QVBoxLayout()
        preview_group = QFrame()
        preview_group.setStyleSheet("""
            QFrame {
                background-color: #050A15;
                border: 1px solid #1A2C4E;
                border-radius: 8px;
            }
        """)
        preview_layout = QVBoxLayout(preview_group)
        
        title_layout = QHBoxLayout()
        preview_title = QLabel("🎯 Canlı Klasör Ağacı Önizlemesi")
        preview_title.setStyleSheet("color: #FF5252; font-weight: bold; border: none;")
        
        self.refresh_btn = QPushButton("🔄 Yenile")
        self.refresh_btn.setStyleSheet(BTN_STYLE)
        self.refresh_btn.clicked.connect(self.update_preview)
        
        title_layout.addWidget(preview_title)
        title_layout.addStretch()
        title_layout.addWidget(self.refresh_btn)
        
        self.preview_lbl = QLabel()
        self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.preview_lbl.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
                color: #FFFFFF;
                line-height: 1.5;
                padding: 10px;
                background-color: transparent;
                border: none;
            }
        """)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.preview_lbl)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
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
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        preview_layout.addLayout(title_layout)
        preview_layout.addWidget(scroll_area)
        
        right_panel.addWidget(preview_group)
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(280)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
    def on_folder_selected(self, path):
        self.save_dir = path
        self.update_preview()
        
    def update_preview(self):
        target = self.out_name_input.text().strip()
            
        c_folder = "<span style='color: #FBC02D;'>📁</span>"
        c_img = "<span style='color: #4CAF50;'>🖼️</span>"
        c_line = "<span style='color: #15243B;'>│</span>"
        c_branch = "<span style='color: #15243B;'>├──</span>"
        c_end = "<span style='color: #15243B;'>└──</span>"
        
        # Akıllı "Hedef" görselleştirmesi (Idea 3)
        if not self.save_dir and not target:
            root_text = "<span style='color: #FF5252; background-color: #2A0A0A; padding: 2px;'>[⚠️ KAYIT KONUMU VE ADI SEÇİLMEDİ]</span>"
        elif not self.save_dir:
            root_text = f"<span style='color: #FBC02D;'>[⚠️ Kayıt Konumu Seçin]</span> / <b><span style='color: #FFFFFF;'>{target}</span></b>"
        elif not target:
            root_text = f"<span style='color: #8CA6BE;'>{self.save_dir}</span> / <span style='color: #FF5252; background-color: #2A0A0A;'>[⚠️ KLASÖR ADI YAZIN]</span>"
        else:
            root_text = f"<span style='color: #8CA6BE;'>{self.save_dir}</span> / <b><span style='color: #FFFFFF;'>{target}</span></b>"
            
        html = f"{c_folder} {root_text}<br>"
        
        videos = [v for v in self.data_source_videos() if v.get('selected', False)]
        annotators = self.data_source_annotators()
        
        if not videos:
            html += "&nbsp;&nbsp;&nbsp;&nbsp;<span style='color: #FF5252;'>⚠️ 1. Sekmeden en az bir videonun solundaki 'Seç' kutucuğunu işaretlemelisiniz!</span><br>"
            self.preview_lbl.setText(html)
            return
            
        if not any(a.get("active", True) for a in annotators):
            html += "&nbsp;&nbsp;&nbsp;&nbsp;<span style='color: #FF5252;'>⚠️ 2. Sekmeden en az bir kişiyi 'Aktif' duruma getirmelisiniz!</span><br>"
            self.preview_lbl.setText(html)
            return

        
        from Frame_islemleri.paylastirma_modulu.distribution_engine import calculate_distribution
        dist_data = calculate_distribution(videos, annotators)
        assignments = dist_data['ui_assignments']
        
        if not assignments:
            html += "&nbsp;&nbsp;&nbsp;&nbsp;<span style='color: #FF5252;'>⚠️ Hiçbir geçerli eşleşme bulunamadı! Rolleri kontrol edin.</span><br>"
            self.preview_lbl.setText(html)
            return
            
        def render_vid_frames(vid_str, frames_cnt, start_idx, is_last, indent):
            res_html = ""
            display_count = min(3, frames_cnt)
            for i in range(display_count):
                frame_num = start_idx + i
                is_last_frame = (i == display_count - 1)
                pref = c_end if (is_last and is_last_frame) else c_branch
                
                extra_text = ""
                if is_last_frame and frames_cnt > display_count:
                    extra_text = f" <span style='color: #FBC02D; font-size: 9pt;'>(... +{frames_cnt - display_count} Kare daha)</span>"
                    
                res_html += f"{indent}{pref} {c_img} <span style='color: #9BAEBC;'>{vid_str}_{frame_num:05d}.png</span>{extra_text}<br>"
            return res_html
            
        grouped = {}
        for a in assignments:
            p, r, v, f, s = a["person"], a["role"], a["video"], a["frames"], a["start"]
            pr_key = f"{p}_{r}"
            if pr_key not in grouped: grouped[pr_key] = []
            grouped[pr_key].append((v, f, s))
            
        for i, (pr_key, vids) in enumerate(grouped.items()):
            is_last_pr = (i == len(grouped) - 1)
            pr_pref = c_end if is_last_pr else c_branch
            pr_ind = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" if is_last_pr else f"{c_line}&nbsp;&nbsp;&nbsp;&nbsp;"
            html += f"{pr_pref} {c_folder} <b><span style='color: #FFFFFF;'>{pr_key}</span></b> <span style='color: #4CAF50;'>(Kişi_Rol)</span><br>"
            
            display_vids = vids[:3]
            for k, (v, f_cnt, s_idx) in enumerate(display_vids):
                is_last_v = (k == len(display_vids) - 1) and (len(vids) <= 3)
                html += render_vid_frames(v, f_cnt, s_idx, is_last_v, pr_ind)
            if len(vids) > 3:
                html += f"{pr_ind}{c_end} <span style='color: #8CA6BE;'>... (ve diğer {len(vids) - 3} video daha)</span><br>"

        self.preview_lbl.setText(html)
        
    def get_config(self):
        return {
            "format": "ZIP" if self.zip_checkbox.isChecked() else "PNG",
            "name": self.out_name_input.text().strip(),
            "dir": self.save_dir
        }
