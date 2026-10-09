from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from Frame_islemleri.paylastirma_modulu.paylastirma_style import GROUP_BOX_STYLE

class PreviewWidget(QGroupBox):
    send_log_signal = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__("Dağıtım Önizlemesi", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.init_ui()
        
    def create_kpi_card(self, title, initial_val):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #0A1224;
                border: 1px solid #1A2C4E;
                border-radius: 8px;
            }
        """)
        card.setMinimumHeight(80)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #8CA6BE; font-size: 10pt; font-weight: bold; border: none;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        val_lbl = QLabel(initial_val)
        val_lbl.setStyleSheet("color: #4CAF50; font-size: 18pt; font-weight: bold; border: none;")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_lbl)
        layout.addWidget(val_lbl)
        
        card.value_label = val_lbl
        return card
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # --- KPI CARDS (Suggestion 3) ---
        cards_layout = QHBoxLayout()
        self.card_vids = self.create_kpi_card("🎬 Seçili Video", "0")
        self.card_pers = self.create_kpi_card("👥 Aktif Personel", "0")
        self.card_frames = self.create_kpi_card("🖼️ Toplam Çıktı", "0")
        
        cards_layout.addWidget(self.card_vids)
        cards_layout.addWidget(self.card_pers)
        cards_layout.addWidget(self.card_frames)
        
        main_layout.addLayout(cards_layout)
        
        # --- DETAILS AREA ---
        self.detail_lbl = QLabel("Seçimlerinizi yapıp bu sekmeye geçtiğinizde otomatik hesaplanacaktır.")
        self.detail_lbl.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
                color: #FFFFFF;
                line-height: 1.5;
                padding: 15px;
                background-color: #050A15;
                border-radius: 8px;
            }
        """)
        self.detail_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.detail_lbl.setWordWrap(True)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.detail_lbl)
        scroll_area.setStyleSheet("""
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
        """)
        
        main_layout.addWidget(scroll_area)

    def reset_cards(self):
        self.card_vids.value_label.setText("0")
        self.card_pers.value_label.setText("0")
        self.card_frames.value_label.setText("0")

    def calculate_preview(self, videos, annotators):
        if not videos:
            self.reset_cards()
            self.detail_lbl.setText("<span style='color: #FF5252;'>⚠️ Video seçilmedi. En az bir videoyu aktif hale getirin.</span>")
            return
        if not annotators:
            self.reset_cards()
            self.detail_lbl.setText("<span style='color: #FF5252;'>⚠️ Kişi eklenmedi veya hiçbiri aktif değil.</span>")
            return
            
        for v in videos:
            if isinstance(v.get('total_frames', 100), str):
                self.reset_cards()
                self.detail_lbl.setText("<span style='color: #FBC02D;'>⏳ Lütfen videoların analizinin bitmesini bekleyin...</span>")
                return
                
        from Frame_islemleri.paylastirma_modulu.distribution_engine import calculate_distribution
        dist_data = calculate_distribution(videos, annotators)
        
        total_extracted_all_videos = dist_data['total_frames']
        valid_annotators = dist_data['valid_annotators']
        quotas = dist_data['quotas']
        assignments = dist_data['ui_assignments']
        
        if not valid_annotators:
            self.reset_cards()
            self.detail_lbl.setText("<span style='color: #FF5252;'>⚠️ Tüm kişiler pasif durumda!</span>")
            return
            
        # Update KPI Cards
        self.card_vids.value_label.setText(str(len(videos)))
        self.card_pers.value_label.setText(str(len(valid_annotators)))
        self.card_frames.value_label.setText(f'{total_extracted_all_videos:,}'.replace(',', '.'))
        
        # Group detailed assignments
        # person -> role -> total_frames
        detailed_stats = {}
        for a in assignments:
            p, r, f = a['person'], a['role'], a['frames']
            if p not in detailed_stats:
                detailed_stats[p] = {}
            if r not in detailed_stats[p]:
                detailed_stats[p][r] = 0
            detailed_stats[p][r] += f

        # HTML Rendering
        c_folder = "<span style='color: #FBC02D;'>📁</span>"
        c_img = "<span style='color: #4CAF50;'>🖼️</span>"
        c_branch = "<span style='color: #15243B;'>├──</span>"
        c_end = "<span style='color: #15243B;'>└──</span>"
        
        html = "<b><span style='color: #9BAEBC;'>👥 KİŞİ BAŞI DÜŞEN TOPLAM KOTA:</span></b><br>"
        
        for a in annotators:
            if not a.get("active", True):
                html += f"<span style='color: #555555;'>• {a['name']}: [PASİF]</span><br>"
            else:
                person_q = next((q for q in quotas if q['person'] == a['name']), None)
                assigned_total = person_q['current'] if person_q else 0
                html += f"<span style='color: #FFFFFF;'>• {a['name']}:</span> <span style='color: #FBC02D;'><b>{assigned_total}</b> Kare</span><br>"
                
        html += "<br><b><span style='color: #9BAEBC;'>🌳 ROL BAZLI DETAYLI DAĞILIM:</span></b><br>"
        
        if not detailed_stats:
            html += "<span style='color: #FF5252;'>Hiçbir kare paylaştırılamadı. Rol uyuşmazlığı olabilir.</span>"
        else:
            for i, (p, roles) in enumerate(detailed_stats.items()):
                html += f"<br>{c_folder} <b><span style='color: #FFFFFF;'>{p}</span></b><br>"
                
                role_items = list(roles.items())
                for j, (r, f_cnt) in enumerate(role_items):
                    is_last_r = (j == len(role_items) - 1)
                    r_pref = c_end if is_last_r else c_branch
                    html += f"&nbsp;&nbsp;&nbsp;&nbsp;{r_pref} {c_img} <span style='color: #8CA6BE;'>{r}: <b><span style='color: #4CAF50;'>{f_cnt} Kare</span></b></span><br>"

        self.detail_lbl.setText(html)
        self.send_log_signal.emit("BİLGİ", "Önizleme başarıyla hesaplandı.")
