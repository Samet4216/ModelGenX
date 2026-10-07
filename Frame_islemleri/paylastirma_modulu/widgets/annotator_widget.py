import os
import json
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QCheckBox, QComboBox, QWidget, QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QColor, QBrush
from Frame_islemleri.paylastirma_modulu.paylastirma_style import (
    BTN_STYLE, BTN_DANGER_STYLE, TABLE_STYLE, GROUP_BOX_STYLE, INPUT_STYLE, STAT_CARD_STYLE
)

class AnnotatorSelectionWidget(QGroupBox):
    send_log_signal = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__("Kişiler ve Ağırlıklar", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.annotators = []
        self.json_path = os.path.join(os.path.dirname(__file__), "..", "kisiler.json")
        self.init_ui()
        self.load_annotators()
        
    def load_annotators(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.annotators = json.load(f)
                self.update_ann_table()
            except Exception as e:
                self.send_log_signal.emit("HATA", f"Kişiler yüklenemedi: {e}")

    def save_annotators(self):
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.annotators, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.send_log_signal.emit("HATA", f"Kişiler kaydedilemedi: {e}")
            
    def init_ui(self):
        ann_layout = QVBoxLayout()
        
        # --- STATS VE AKSİYON PANELİ ---
        stats_action_layout = QHBoxLayout()
        
        frame_total, self.lbl_total_team = self.create_stat_card("Toplam Ekip", "0")
        frame_active, self.lbl_active_team = self.create_stat_card("Aktif Çalışan", "0")
        
        stats_action_layout.addWidget(frame_total)
        stats_action_layout.addWidget(frame_active)
        
        stats_action_layout.addStretch()
        
        btn_active_all = QPushButton("Tümünü Aktif Yap")
        btn_active_all.setStyleSheet(BTN_STYLE + "background-color: #2E7D32; font-weight: bold; padding: 5px 10px;")
        btn_active_all.clicked.connect(self.set_all_active)
        
        btn_inactive_all = QPushButton("Tümünü Pasif Yap")
        btn_inactive_all.setStyleSheet(BTN_STYLE + "background-color: #C62828; font-weight: bold; padding: 5px 10px;")
        btn_inactive_all.clicked.connect(self.set_all_inactive)
        
        balance_btn = QPushButton("Tümünü Eşitle (1.0x)")
        balance_btn.setStyleSheet(BTN_STYLE + "background-color: #1565C0; font-weight: bold; padding: 5px 10px;")
        balance_btn.clicked.connect(self.balance_weights)
        
        stats_action_layout.addWidget(btn_active_all)
        stats_action_layout.addWidget(btn_inactive_all)
        stats_action_layout.addWidget(balance_btn)
        
        ann_layout.addLayout(stats_action_layout)
        
        # --- EKLEME PANELİ ---
        ann_input_layout = QHBoxLayout()
        self.ann_name_input = QLineEdit()
        self.ann_name_input.setPlaceholderText("Kişi Adı")
        self.ann_name_input.setStyleSheet(INPUT_STYLE)
        self.ann_name_input.returnPressed.connect(self.add_annotator)
        
        self.ann_weight_input = QDoubleSpinBox()
        self.ann_weight_input.setDecimals(1)
        self.ann_weight_input.setSingleStep(0.1)
        self.ann_weight_input.setValue(1.0)
        self.ann_weight_input.setStyleSheet(INPUT_STYLE)
        self.ann_weight_input.lineEdit().returnPressed.connect(self.add_annotator)
        
        add_ann_btn = QPushButton("Ekle")
        add_ann_btn.setStyleSheet(BTN_STYLE)
        add_ann_btn.clicked.connect(self.add_annotator)
        
        ann_input_layout.addWidget(self.ann_name_input)
        ann_input_layout.addWidget(QLabel("Ağırlık (x):"))
        ann_input_layout.addWidget(self.ann_weight_input)
        ann_input_layout.addWidget(add_ann_btn)
        ann_layout.addLayout(ann_input_layout)
        
        # --- TABLO ---
        self.ann_table = QTableWidget()
        self.ann_table.setStyleSheet(TABLE_STYLE)
        self.ann_table.setColumnCount(5)
        # BAŞLIKLAR
        self.ann_table.setHorizontalHeaderLabels(["Aktif", "İsim", "Rol", "Ağırlık", "İşlem"])
        
        self.ann_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.ann_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.ann_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.ann_table.setColumnWidth(2, 110)
        self.ann_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.ann_table.setColumnWidth(3, 200) # Genişliği artırdık ki hem sayılar hem % sığsın
        self.ann_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.ann_table.verticalHeader().setDefaultSectionSize(46)
        self.ann_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.ann_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ann_table.setAlternatingRowColors(True)
        # TIKLANABİLİR SIRALAMA (Sorting)
        self.ann_table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.ann_table.setSortingEnabled(True)
        ann_layout.addWidget(self.ann_table)
        
        # --- BOŞ DURUM YAZISI ---
        self.empty_lbl = QLabel("Henüz kimse eklenmedi. Yukarıdan ekip arkadaşlarınızı ekleyin.")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet("color: #8CA6BE; font-size: 11pt; font-style: italic; padding: 40px;")
        ann_layout.addWidget(self.empty_lbl)
        
        self.setLayout(ann_layout)

    def create_stat_card(self, title, initial_value):
        frame = QFrame(self)
        frame.setStyleSheet(STAT_CARD_STYLE)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("StatTitle")
        
        lbl_val = QLabel(initial_value)
        lbl_val.setObjectName("StatValue")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_val)
        return frame, lbl_val

    def add_annotator(self):
        name = self.ann_name_input.text().strip()
        weight = self.ann_weight_input.value()
        
        if not name:
            self.send_log_signal.emit("UYR", "Lütfen kişi adı giriniz.")
            return
            
        if any(a["name"] == name for a in self.annotators):
            self.send_log_signal.emit("UYR", "Bu kişi zaten listede mevcut.")
            return
            
        self.annotators.append({"name": name, "weight": weight, "active": True, "role": "Tümü"})
        self.ann_name_input.clear()
        self.ann_weight_input.setValue(1.0)
        self.update_ann_table()
        self.save_annotators()
        
    def set_all_active(self):
        for ann in self.annotators:
            ann["active"] = True
        self.save_annotators()
        self.update_ann_table()
        self.send_log_signal.emit("BİLGİ", "Tüm kişiler aktif edildi.")
        
    def set_all_inactive(self):
        for ann in self.annotators:
            ann["active"] = False
        self.save_annotators()
        self.update_ann_table()
        self.send_log_signal.emit("BİLGİ", "Tüm kişiler pasif edildi.")
        
    def balance_weights(self):
        for ann in self.annotators:
            if ann.get("active", True):
                ann["weight"] = 1.0
        self.update_ann_table()
        self.save_annotators()
        self.send_log_signal.emit("BİLGİ", "Aktif kişilerin ağırlıkları eşitlendi (1.0x).")
        
    def update_stats_panel(self):
        total = len(self.annotators)
        active = sum(1 for a in self.annotators if a.get("active", True))
            
        self.lbl_total_team.setText(str(total))
        self.lbl_active_team.setText(str(active))
        
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
        
    def update_ann_table(self):
        self.update_stats_panel()
        
        # Boş durum kontrolü
        if len(self.annotators) == 0:
            self.ann_table.setVisible(False)
            self.empty_lbl.setVisible(True)
            return
        else:
            self.ann_table.setVisible(True)
            self.empty_lbl.setVisible(False)
        
        # Scroll pozisyonunu kaydet
        v_scroll = self.ann_table.verticalScrollBar().value()
        
        # Sıralamayı geçici olarak kapatıyoruz (veri eklerken çakışmaması için)
        self.ann_table.setSortingEnabled(False)
        self.ann_table.setRowCount(0)
        
        active_weight = sum(a["weight"] for a in self.annotators if a.get("active", True))
        
        for i, ann in enumerate(self.annotators):
            if "active" not in ann: ann["active"] = True
            if "role" not in ann: ann["role"] = "Tümü"
            
            self.ann_table.insertRow(i)
            
            # 0: Aktif Checkbox
            chk_container = QWidget()
            chk_layout = QHBoxLayout(chk_container)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            chk_layout.setSpacing(0)
            
            toggle_btn = QPushButton()
            toggle_btn.setCheckable(True)
            toggle_btn.setChecked(ann["active"])
            toggle_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            def update_btn_style(btn, is_checked):
                if is_checked:
                    btn.setText("✔")
                    btn.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; border-radius: 0px; font-size: 14pt; border: none;")
                else:
                    btn.setText("✖")
                    btn.setStyleSheet("background-color: #C62828; color: white; font-weight: bold; border-radius: 0px; font-size: 14pt; border: none;")
                    
            update_btn_style(toggle_btn, ann["active"])
            
            def on_toggle(checked, name=ann["name"], btn=toggle_btn):
                update_btn_style(btn, checked)
                self.update_ann_active(name, checked)
                
            toggle_btn.toggled.connect(on_toggle)
            chk_layout.addWidget(toggle_btn)
            
            chk_item = QTableWidgetItem()
            chk_item.setData(Qt.ItemDataRole.EditRole, 1 if ann["active"] else 0)
            chk_item.setForeground(QBrush(Qt.GlobalColor.transparent))
            self.ann_table.setItem(i, 0, chk_item)
            self.ann_table.setCellWidget(i, 0, chk_container)
            
            # 1: İsim (Büyük, kalın, ORTALI ve eğer pasifse Kırmızı yazıyor)
            item = QTableWidgetItem(ann["name"])
            font = item.font()
            font.setPointSize(11)
            font.setBold(True)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if not ann["active"]:
                item.setForeground(QBrush(QColor("#FF5252")))
            else:
                item.setForeground(QBrush(QColor("#FFFFFF")))
                
            self.ann_table.setItem(i, 1, item)
            
            # 2: Rol
            role_combo = QComboBox()
            role_combo.addItems(["Tümü", "train", "val", "test"])
            role_combo.setCurrentText(ann["role"])
            self.apply_combo_color(role_combo, ann["role"])
            role_combo.currentTextChanged.connect(lambda text, name=ann["name"]: self.update_ann_role(name, text))
            
            role_item = QTableWidgetItem(ann["role"])
            role_item.setForeground(QBrush(Qt.GlobalColor.transparent))
            self.ann_table.setItem(i, 2, role_item)
            self.ann_table.setCellWidget(i, 2, role_combo)
            
            # 3: Ağırlık Hızlı Düzenleme & Yüzde
            w_container = QWidget()
            w_layout = QHBoxLayout(w_container)
            w_layout.setContentsMargins(5, 0, 5, 0)
            
            weight_spin = QDoubleSpinBox()
            weight_spin.setDecimals(1)
            weight_spin.setSingleStep(0.1)
            weight_spin.setValue(ann["weight"])
            weight_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            is_overloaded = False
            perc = 0
            if ann["active"] and active_weight > 0:
                percentage = ann["weight"] / active_weight
                perc = percentage * 100
                active_count = sum(1 for a in self.annotators if a.get("active", True))
                if active_count > 1 and percentage > 0.60:
                    is_overloaded = True
            
            lbl_perc = QLabel(f"( %{perc:.0f} )")
            lbl_perc.setFixedWidth(55)
            lbl_perc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if is_overloaded:
                weight_spin.setStyleSheet(INPUT_STYLE + "background-color: #FBC02D; color: #000000; border: 2px solid #F57F17; font-weight: bold;")
                weight_spin.setToolTip("DİKKAT: Bu kişiye %60'tan fazla iş yükü bindirdiniz!")
                lbl_perc.setStyleSheet("color: #FBC02D; font-size: 9pt; font-weight: bold;")
            else:
                weight_spin.setStyleSheet(INPUT_STYLE)
                weight_spin.setToolTip("")
                lbl_perc.setStyleSheet("color: #8CA6BE; font-size: 9pt; font-weight: bold;")
                
            weight_spin.valueChanged.connect(lambda val, name=ann["name"]: self.update_ann_weight_deferred(name, val))
            
            w_layout.addWidget(weight_spin)
            w_layout.addWidget(lbl_perc)
            
            weight_item = QTableWidgetItem()
            weight_item.setData(Qt.ItemDataRole.EditRole, float(ann["weight"]))
            weight_item.setForeground(QBrush(Qt.GlobalColor.transparent))
            self.ann_table.setItem(i, 3, weight_item)
            self.ann_table.setCellWidget(i, 3, w_container)
            
            # 4: İşlem
            del_btn = QPushButton("Sil")
            del_btn.setStyleSheet(BTN_DANGER_STYLE)
            del_btn.clicked.connect(lambda checked, name=ann["name"]: self.delete_ann(name))
            self.ann_table.setCellWidget(i, 4, del_btn)

        # Tabloyu doldurduktan sonra sıralamayı tekrar aktif et
        self.ann_table.setSortingEnabled(True)
        self.ann_table.verticalScrollBar().setValue(v_scroll)

    def update_ann_active(self, name, checked):
        for a in self.annotators:
            if a["name"] == name:
                a["active"] = checked
                break
        self.save_annotators()
        self.update_ann_table()
        
    def update_ann_role(self, name, text):
        for a in self.annotators:
            if a["name"] == name:
                a["role"] = text
                break
        self.save_annotators()
        self.update_ann_table()
        
    def update_ann_weight(self, name, val):
        for a in self.annotators:
            if a["name"] == name:
                a["weight"] = val
                break
        self.save_annotators()
        self.update_ann_table()
        
    def update_ann_weight_deferred(self, name, val):
        QTimer.singleShot(10, lambda: self.update_ann_weight(name, val))
            
    def delete_ann(self, name):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Silme Onayı")
        msg_box.setText(f"'{name}' adlı çalışanı listeden kaldırmak istediğinize emin misiniz?")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #050A15;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #C62828;
                color: white;
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
        """)
        
        btn_yes = msg_box.addButton("Evet, Sil", QMessageBox.ButtonRole.YesRole)
        btn_no = msg_box.addButton("İptal", QMessageBox.ButtonRole.NoRole)
        btn_no.setStyleSheet("background-color: #15243B; color: white;")
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_yes:
            self.annotators = [a for a in self.annotators if a["name"] != name]
            self.save_annotators()
            self.update_ann_table()
            self.send_log_signal.emit("BİLGİ", f"'{name}' listeden silindi.")
        
    def get_annotators(self):
        return self.annotators
