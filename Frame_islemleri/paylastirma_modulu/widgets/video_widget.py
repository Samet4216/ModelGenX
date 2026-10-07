import os
import cv2
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QComboBox, QFileDialog, QAbstractItemView, QLabel, QSpinBox, QCheckBox, QWidget
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

from Frame_islemleri.paylastirma_modulu.paylastirma_style import (
    BTN_STYLE, BTN_DANGER_STYLE, TABLE_STYLE, GROUP_BOX_STYLE, INPUT_STYLE
)

class VideoAnalyzerThread(QThread):
    # filepath, fps, total_frames
    result_signal = pyqtSignal(str, float, int)
    
    def __init__(self, files):
        super().__init__()
        self.files = files
        
    def run(self):
        for file in self.files:
            try:
                cap = cv2.VideoCapture(file)
                if cap.isOpened():
                    fps = float(cap.get(cv2.CAP_PROP_FPS))
                    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    cap.release()
                else:
                    fps = 0.0
                    frames = 0
            except Exception:
                fps = 0.0
                frames = 0
            
            self.result_signal.emit(file, fps, frames)


class VideoSelectionWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Video Düzenleme ve Rol Belirleme", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.videos = []
        self.init_ui()
        
    def init_ui(self):
        vid_layout = QVBoxLayout()
        
        # Üst Araç Çubuğu (Ekleme ve Toplu İşlem)
        top_layout = QHBoxLayout()
        self.add_vid_btn = QPushButton("Video Ekle")
        self.add_vid_btn.setStyleSheet(BTN_STYLE)
        self.add_vid_btn.clicked.connect(self.add_videos)
        top_layout.addWidget(self.add_vid_btn)
        
        top_layout.addStretch()
        
        # Toplu İşlem Alanı
        top_layout.addWidget(QLabel("Seçililer İçin Kaç_Frame (Atlama):"))
        self.bulk_spin = QSpinBox()
        self.bulk_spin.setMinimum(1)
        self.bulk_spin.setMaximum(99999)
        self.bulk_spin.setValue(1)
        self.bulk_spin.setStyleSheet(INPUT_STYLE)
        top_layout.addWidget(self.bulk_spin)
        
        self.bulk_btn = QPushButton("Toplu Uygula")
        self.bulk_btn.setStyleSheet(BTN_STYLE)
        self.bulk_btn.clicked.connect(self.apply_bulk_interval)
        top_layout.addWidget(self.bulk_btn)
        
        vid_layout.addLayout(top_layout)
        
        # Tablo
        self.vid_table = QTableWidget()
        self.vid_table.setStyleSheet(TABLE_STYLE)
        self.vid_table.setColumnCount(7)
        self.vid_table.setHorizontalHeaderLabels(["Seç", "Video Adı", "Rol", "FPS", "Kaç_Frame", "Çıkan_Kare", "İşlem"])
        self.vid_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.vid_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.vid_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.vid_table.setColumnWidth(2, 110)
        self.vid_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.vid_table.setColumnWidth(3, 85)
        self.vid_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.vid_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.vid_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.vid_table.verticalHeader().setDefaultSectionSize(46)
        self.vid_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.vid_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        vid_layout.addWidget(self.vid_table)
        
        # Tümünü Seç
        bot_layout = QHBoxLayout()
        self.chk_select_all = QCheckBox("Tümünü Seç / Kaldır")
        self.chk_select_all.setStyleSheet("color: white;")
        self.chk_select_all.stateChanged.connect(self.toggle_select_all)
        bot_layout.addWidget(self.chk_select_all)
        bot_layout.addStretch()
        vid_layout.addLayout(bot_layout)
        
        self.setLayout(vid_layout)

    def add_videos(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Video Seç", "", "Videolar (*.mp4 *.avi *.mkv *.mov)")
        if not files:
            return
            
        self.add_vid_btn.setEnabled(False)
        self.add_vid_btn.setText("Videolar Analiz Ediliyor...")

        for file in files:
            name = os.path.basename(file).split('.')[0]
            video_data = {
                'path': file,
                'name': name,
                'split': 'train',
                'fps': "...",
                'total_frames': "Hesaplanıyor...",
                'interval': 1,
                'selected': False
            }
            self.videos.append(video_data)
            
        self.update_vid_table()
        
        self.analyzer_thread = VideoAnalyzerThread(files)
        self.analyzer_thread.result_signal.connect(self.on_video_analyzed)
        self.analyzer_thread.finished.connect(self.on_analysis_finished)
        self.analyzer_thread.start()

    def on_video_analyzed(self, filepath, fps, total_frames):
        for i, vid in enumerate(self.videos):
            if vid['path'] == filepath:
                vid['fps'] = fps
                vid['total_frames'] = total_frames
                
                # FPS Güncelle
                item_fps = self.vid_table.item(i, 3)
                if item_fps:
                    item_fps.setText(f"{fps:.2f}")
                
                # Çıkan Kare Güncelle
                item_kare = self.vid_table.item(i, 5)
                if item_kare:
                    extracted = total_frames // vid['interval']
                    item_kare.setText(str(extracted))
                break

    def on_analysis_finished(self):
        self.add_vid_btn.setEnabled(True)
        self.add_vid_btn.setText("Video Ekle")
        
    def toggle_select_all(self, state):
        checked = (state == Qt.CheckState.Checked.value)
        for i, vid in enumerate(self.videos):
            vid['selected'] = checked
            # Checkbox widgeti manuel tetiklemeden güncelle
            chk_widget = self.vid_table.cellWidget(i, 0)
            if chk_widget:
                cb = chk_widget.layout().itemAt(0).widget()
                cb.blockSignals(True)
                cb.setChecked(checked)
                cb.blockSignals(False)

    def apply_bulk_interval(self):
        val = self.bulk_spin.value()
        for i, vid in enumerate(self.videos):
            if vid['selected']:
                vid['interval'] = val
                # Spinbox güncelle
                spin_widget = self.vid_table.cellWidget(i, 4)
                if spin_widget:
                    spin_widget.blockSignals(True)
                    spin_widget.setValue(val)
                    spin_widget.blockSignals(False)
                
                # Çıkan Kare güncelle
                self.update_extracted_frames_label(i)

    def update_vid_table(self):
        self.vid_table.setRowCount(0)
        for i, vid in enumerate(self.videos):
            self.vid_table.insertRow(i)
            
            # 0: Seç (Checkbox)
            chk_container = QWidget()
            chk_layout = QHBoxLayout(chk_container)
            chk_layout.setContentsMargins(5, 0, 5, 0)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cb = QCheckBox()
            cb.setChecked(vid['selected'])
            cb.stateChanged.connect(lambda state, idx=i: self.on_vid_selected(idx, state))
            chk_layout.addWidget(cb)
            self.vid_table.setCellWidget(i, 0, chk_container)
            
            # 1: Video Adı
            self.vid_table.setItem(i, 1, QTableWidgetItem(vid['name']))
            
            # 2: Rol
            combo = QComboBox()
            combo.addItems(["train", "val", "test"])
            combo.setCurrentText(vid['split'])
            self.apply_combo_color(combo, vid['split'])
            combo.currentTextChanged.connect(lambda text, idx=i: self.update_vid_split(idx, text))
            self.vid_table.setCellWidget(i, 2, combo)
            
            # 3: FPS
            fps_str = str(vid['fps']) if isinstance(vid['fps'], str) else f"{vid['fps']:.2f}"
            item_fps = QTableWidgetItem(fps_str)
            item_fps.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.vid_table.setItem(i, 3, item_fps)
            
            # 4: Kaç_Frame (Atlama)
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(99999)
            spin.setValue(vid['interval'])
            spin.setStyleSheet(INPUT_STYLE)
            spin.valueChanged.connect(lambda val, idx=i: self.on_interval_changed(idx, val))
            self.vid_table.setCellWidget(i, 4, spin)
            
            # 5: Çıkan_Kare
            if isinstance(vid['total_frames'], str):
                extracted_str = vid['total_frames']
            else:
                extracted = vid['total_frames'] // vid['interval']
                extracted_str = str(extracted)
                
            item_frames = QTableWidgetItem(extracted_str)
            item_frames.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.vid_table.setItem(i, 5, item_frames)
            
            # 6: İşlem (Sil)
            del_btn = QPushButton("Sil")
            del_btn.setStyleSheet(BTN_DANGER_STYLE)
            del_btn.clicked.connect(lambda _, idx=i: self.delete_vid(idx))
            self.vid_table.setCellWidget(i, 6, del_btn)
            
    def on_vid_selected(self, idx, state):
        self.videos[idx]['selected'] = (state == Qt.CheckState.Checked.value)

    def on_interval_changed(self, idx, val):
        self.videos[idx]['interval'] = val
        self.update_extracted_frames_label(idx)
        
    def update_extracted_frames_label(self, idx):
        vid = self.videos[idx]
        if not isinstance(vid['total_frames'], str):
            extracted = vid['total_frames'] // vid['interval']
            item = self.vid_table.item(idx, 5)
            if item:
                item.setText(str(extracted))

    def update_vid_split(self, idx, split):
        self.videos[idx]['split'] = split
        combo = self.vid_table.cellWidget(idx, 2)
        if combo:
            self.apply_combo_color(combo, split)
            
    def apply_combo_color(self, combo, text):
        if text == "train":
            color_style = "background-color: #2E7D32; color: #FFFFFF; font-weight: bold; border-color: #2E7D32;"
        elif text == "val":
            color_style = "background-color: #1565C0; color: #FFFFFF; font-weight: bold; border-color: #1565C0;"
        elif text == "test":
            color_style = "background-color: #FBC02D; color: #000000; font-weight: bold; border-color: #FBC02D;"
        else:
            color_style = ""
            
        custom = INPUT_STYLE + f"\nQComboBox {{ {color_style} }}"
        combo.setStyleSheet(custom)
        
    def delete_vid(self, idx):
        self.videos.pop(idx)
        self.update_vid_table()
        
    def get_videos(self):
        return self.videos
