from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QTabWidget
from PyQt6.QtCore import pyqtSignal

from Frame_islemleri.paylastirma_modulu.paylastirma_style import BTN_STYLE
from Frame_islemleri.paylastirma_modulu.worker import FrameExtractionThread
from Frame_islemleri.paylastirma_modulu.widgets.video_widget import VideoSelectionWidget
from Frame_islemleri.paylastirma_modulu.widgets.annotator_widget import AnnotatorSelectionWidget
from Frame_islemleri.paylastirma_modulu.widgets.output_widget import OutputConfigWidget
from Frame_islemleri.paylastirma_modulu.widgets.preview_widget import PreviewWidget

class PaylastirmaModuluApp(QWidget):
    send_log_signal = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)
        
        self.tabs = QTabWidget()
        from Frame_islemleri.paylastirma_modulu.paylastirma_style import TAB_STYLE
        self.tabs.setStyleSheet(TAB_STYLE)
        
        # --- TAB 1: VİDEOLAR ---
        self.tab_videos = QWidget()
        tab_vid_layout = QVBoxLayout(self.tab_videos)
        self.video_widget = VideoSelectionWidget()
        tab_vid_layout.addWidget(self.video_widget)
        self.tabs.addTab(self.tab_videos, "1. Video Düzenleme ve Rol Belirleme")
        
        # --- TAB 2: KİŞİLER ---
        self.tab_annotators = QWidget()
        tab_ann_layout = QVBoxLayout(self.tab_annotators)
        self.annotator_widget = AnnotatorSelectionWidget()
        self.annotator_widget.send_log_signal.connect(self.relay_log)
        tab_ann_layout.addWidget(self.annotator_widget)
        self.tabs.addTab(self.tab_annotators, "2. Kişiler ve Ağırlıklar")
        
        # --- TAB 3: ÇIKTI AYARLARI ---
        self.tab_output = QWidget()
        tab_out_layout = QVBoxLayout(self.tab_output)
        self.output_widget = OutputConfigWidget()
        self.output_widget.data_source_videos = self.video_widget.get_videos
        self.output_widget.data_source_annotators = self.annotator_widget.get_annotators
        tab_out_layout.addWidget(self.output_widget)
        self.tabs.addTab(self.tab_output, "3. Çıktı Ayarları")
        
        # --- TAB 4: DAĞITIM ÖNİZLEMESİ ---
        self.tab_preview = QWidget()
        tab_prev_layout = QVBoxLayout(self.tab_preview)
        self.preview_widget = PreviewWidget()
        self.preview_widget.send_log_signal.connect(self.relay_log)
        tab_prev_layout.addWidget(self.preview_widget)
        self.tabs.addTab(self.tab_preview, "4. Dağıtım Önizlemesi")
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tabs)
        
        # --- İLERLEME VE BAŞLAT ---
        bottom_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #15243B; border-radius: 5px; text-align: center; color: white; } QProgressBar::chunk { background-color: #70C4FF; }")
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        bottom_layout.addWidget(self.progress_bar)
        
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("İşlemi Başlat")
        self.start_btn.setStyleSheet(BTN_STYLE)
        self.start_btn.setMinimumHeight(50)
        self.start_btn.clicked.connect(self.start_extraction)
        
        from Frame_islemleri.paylastirma_modulu.paylastirma_style import BTN_DANGER_STYLE
        self.cancel_btn = QPushButton("İptal Et")
        self.cancel_btn.setStyleSheet(BTN_DANGER_STYLE)
        self.cancel_btn.setMinimumHeight(50)
        self.cancel_btn.hide()
        self.cancel_btn.clicked.connect(self.cancel_extraction)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        bottom_layout.addLayout(btn_layout)
        
        main_layout.addLayout(bottom_layout)

    def on_tab_changed(self, index):
        if index == 2:
            self.output_widget.update_preview()
        elif index == 3:
            self.handle_preview_calculation()

    def handle_preview_calculation(self):
        videos = [v for v in self.video_widget.get_videos() if v.get('selected', False)]
        annotators = self.annotator_widget.get_annotators()
        self.preview_widget.calculate_preview(videos, annotators)

    def start_extraction(self):
        videos = [v for v in self.video_widget.get_videos() if v.get('selected', False)]
        annotators = self.annotator_widget.get_annotators()
        config = self.output_widget.get_config()
        
        if not videos:
            self.relay_log("UYR", "Lütfen en az bir video ekleyin.")
            return
        
        for v in videos:
            if isinstance(v['total_frames'], str):
                self.relay_log("UYR", "Lütfen videoların analizinin bitmesini bekleyin.")
                return

        if not annotators:
            self.relay_log("UYR", "Lütfen en az bir kişi ekleyin.")
            return
        if not config['dir']:
            self.relay_log("UYR", "Lütfen çıktı konumunu seçin.")
            return
        if not config['name']:
            self.relay_log("UYR", "Lütfen hedef (klasör/zip) adını girin.")
            return
            
        self.start_btn.setEnabled(False)
        self.start_btn.setText("İşlem Sürüyor...")
        self.cancel_btn.show()
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("İptal Et")
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        self.thread = FrameExtractionThread(
            videos=videos,
            annotators=annotators,
            output_dir=config['dir'],
            output_format=config['format'],
            output_name=config['name']
        )
        self.thread.log_msg.connect(self.relay_log)
        self.thread.progress_update.connect(self.progress_bar.setValue)
        self.thread.finished_extraction.connect(self.on_finished)
        self.thread.start()

    def cancel_extraction(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.cancel()
            self.cancel_btn.setEnabled(False)
            self.cancel_btn.setText("İptal Ediliyor...")
        
    def relay_log(self, level, msg):
        self.send_log_signal.emit(level, msg)
        
    def on_finished(self, stats):
        self.start_btn.setEnabled(True)
        self.start_btn.setText("İşlemi Başlat")
        self.cancel_btn.hide()
        self.progress_bar.hide()
        
        if not stats:
            return
            
        # Sonuç logları (ör. samet 28 epli 34)
        log_str = " ".join([f"{name} {count}" for name, count in stats.items()])
        self.relay_log("BİLGİ", log_str)
        self.relay_log("BİLGİ", "işlem tamamlandı.")
        
        if hasattr(self.window(), 'show_toast'):
            self.window().show_toast("Frame paylaştırma ve çıkarma tamamlandı!")
