import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QScrollArea, QFrame, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter, QPageSize, QPdfWriter
from PyQt6.QtCore import QMarginsF
from PyQt6.QtGui import QPageLayout

from dataset_islemleri.veriseti_analiz.analiz_style import (
    BTN_STYLE, BTN_SECONDARY_STYLE, TABLE_STYLE, GROUP_BOX_STYLE,
    TAB_STYLE, SCROLL_AREA_STYLE, INPUT_STYLE
)
from dataset_islemleri.veriseti_analiz.analiz_engine import analyze_dataset
from dataset_islemleri.veriseti_analiz.widgets.chart_widgets import (
    KPICard, BarChartWidget, DonutChartWidget, BBoxSizeChart
)


class AnalysisWorkerThread(QThread):
    """Arka planda veri seti analizi çalıştırır."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, dataset_path):
        super().__init__()
        self.dataset_path = dataset_path

    def run(self):
        try:
            result = analyze_dataset(self.dataset_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class VeriSetiAnalizApp(QWidget):
    send_log_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.analysis_result = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        # --- ÜST: Klasör Seçme ---
        top_bar = QHBoxLayout()

        self.path_lbl = QLabel("📂 Veri seti klasörünü seçin...")
        self.path_lbl.setStyleSheet("color: #9BAEBC; font-size: 11pt; padding: 8px;")

        self.select_btn = QPushButton("📁 Klasör Seç")
        self.select_btn.setStyleSheet(BTN_STYLE)
        self.select_btn.clicked.connect(self.select_dataset)

        self.analyze_btn = QPushButton("🔍 Analiz Et")
        self.analyze_btn.setStyleSheet(BTN_STYLE)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.start_analysis)

        top_bar.addWidget(self.path_lbl, stretch=1)
        top_bar.addWidget(self.select_btn)
        top_bar.addWidget(self.analyze_btn)

        main_layout.addLayout(top_bar)

        # --- TABS ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_STYLE)

        # Tab 1: Genel Özet
        self.tab_overview = QWidget()
        self.setup_overview_tab()
        self.tabs.addTab(self.tab_overview, "1. Genel Özet")

        # Tab 2: Sınıf Dağılımı
        self.tab_classes = QWidget()
        self.setup_classes_tab()
        self.tabs.addTab(self.tab_classes, "2. Sınıf Dağılımı")

        # Tab 3: Detaylı Tablo
        self.tab_details = QWidget()
        self.setup_details_tab()
        self.tabs.addTab(self.tab_details, "3. Detaylı Tablo")

        # Tab 4: Dışa Aktarma
        self.tab_export = QWidget()
        self.setup_export_tab()
        self.tabs.addTab(self.tab_export, "4. Dışa Aktarma")

        main_layout.addWidget(self.tabs)

    # =========================================================================
    # TAB 1: GENEL ÖZET
    # =========================================================================
    def setup_overview_tab(self):
        layout = QVBoxLayout(self.tab_overview)
        layout.setSpacing(15)

        # KPI Kartları
        cards_layout = QHBoxLayout()
        self.kpi_images = KPICard("🖼️", "Toplam Görsel")
        self.kpi_labels = KPICard("🏷️", "Toplam Etiket")
        self.kpi_annotations = KPICard("📌", "Toplam Anotasyon")
        self.kpi_classes = KPICard("📊", "Sınıf Sayısı")
        self.kpi_missing = KPICard("⚠️", "Eksik Etiket")

        cards_layout.addWidget(self.kpi_images)
        cards_layout.addWidget(self.kpi_labels)
        cards_layout.addWidget(self.kpi_annotations)
        cards_layout.addWidget(self.kpi_classes)
        cards_layout.addWidget(self.kpi_missing)

        layout.addLayout(cards_layout)

        # Grafikler: Split Dağılımı + BBox Boyutu
        charts_layout = QHBoxLayout()

        self.donut_chart = DonutChartWidget()
        self.bbox_chart = BBoxSizeChart()

        charts_layout.addWidget(self.donut_chart)
        charts_layout.addWidget(self.bbox_chart)

        layout.addLayout(charts_layout)

        # Boş mesaj
        self.overview_msg = QLabel("Lütfen bir veri seti klasörü seçip 'Analiz Et' butonuna basın.")
        self.overview_msg.setStyleSheet("color: #555555; font-size: 12pt;")
        self.overview_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.overview_msg)

    # =========================================================================
    # TAB 2: SINIF DAĞILIMI
    # =========================================================================
    def setup_classes_tab(self):
        layout = QVBoxLayout(self.tab_classes)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(SCROLL_AREA_STYLE)

        self.bar_chart = BarChartWidget()
        scroll.setWidget(self.bar_chart)

        layout.addWidget(scroll)

    # =========================================================================
    # TAB 3: DETAYLI TABLO
    # =========================================================================
    def setup_details_tab(self):
        layout = QVBoxLayout(self.tab_details)

        # Split bazlı tablo
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(6)
        self.detail_table.setHorizontalHeaderLabels([
            "Split", "Görsel", "Etiket", "Anotasyon",
            "Eksik Etiket", "Boş Etiket"
        ])
        self.detail_table.setStyleSheet(TABLE_STYLE)
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detail_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.detail_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        layout.addWidget(self.detail_table)

        # Sınıf bazlı tablo
        lbl = QLabel("📊 Sınıf Bazlı İstatistikler")
        lbl.setStyleSheet("color: #4CAF50; font-size: 11pt; font-weight: bold; padding-top: 10px;")
        layout.addWidget(lbl)

        self.class_table = QTableWidget()
        self.class_table.setColumnCount(4)
        self.class_table.setHorizontalHeaderLabels([
            "Sınıf Adı", "Anotasyon Sayısı", "Yüzde (%)", "Durum"
        ])
        self.class_table.setStyleSheet(TABLE_STYLE)
        self.class_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.class_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.class_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        layout.addWidget(self.class_table)

    # =========================================================================
    # TAB 4: DIŞA AKTARMA
    # =========================================================================
    def setup_export_tab(self):
        layout = QVBoxLayout(self.tab_export)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)

        info_lbl = QLabel("📤 Analiz sonuçlarını dışa aktarma seçenekleri")
        info_lbl.setStyleSheet("color: #4CAF50; font-size: 12pt; font-weight: bold; padding: 10px;")
        layout.addWidget(info_lbl)

        # PNG Butonu
        png_group = QGroupBox("🖼️ Grafikleri PNG Olarak Kaydet")
        png_group.setStyleSheet(GROUP_BOX_STYLE)
        png_layout = QVBoxLayout(png_group)

        png_desc = QLabel("Tüm grafikleri (Sınıf Dağılımı, Split Dağılımı, BBox Analizi) ayrı ayrı PNG formatında kaydeder.")
        png_desc.setStyleSheet("color: #9BAEBC; font-size: 10pt;")
        png_desc.setWordWrap(True)
        png_layout.addWidget(png_desc)

        self.export_png_btn = QPushButton("📸 PNG Olarak Dışa Aktar")
        self.export_png_btn.setStyleSheet(BTN_STYLE)
        self.export_png_btn.setEnabled(False)
        self.export_png_btn.clicked.connect(self.export_png)
        png_layout.addWidget(self.export_png_btn)

        layout.addWidget(png_group)

        # PDF Butonu
        pdf_group = QGroupBox("📄 PDF Raporu Oluştur")
        pdf_group.setStyleSheet(GROUP_BOX_STYLE)
        pdf_layout = QVBoxLayout(pdf_group)

        pdf_desc = QLabel("Tüm grafikleri ve istatistikleri tek bir PDF dosyası olarak derler.")
        pdf_desc.setStyleSheet("color: #9BAEBC; font-size: 10pt;")
        pdf_desc.setWordWrap(True)
        pdf_layout.addWidget(pdf_desc)

        self.export_pdf_btn = QPushButton("📄 PDF Raporu Oluştur")
        self.export_pdf_btn.setStyleSheet(BTN_STYLE)
        self.export_pdf_btn.setEnabled(False)
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        pdf_layout.addWidget(self.export_pdf_btn)

        layout.addWidget(pdf_group)

        layout.addStretch()

    # =========================================================================
    # İŞLEM FONKSİYONLARI
    # =========================================================================
    def select_dataset(self):
        path = QFileDialog.getExistingDirectory(self, "Veri Seti Klasörünü Seçin", "")
        if path:
            self.dataset_path = path
            self.path_lbl.setText(f"📂 {path}")
            self.path_lbl.setStyleSheet("color: #4CAF50; font-size: 11pt; font-weight: bold; padding: 8px;")
            self.analyze_btn.setEnabled(True)
            self.send_log_signal.emit("BİLGİ", f"Veri seti seçildi: {path}")

    def start_analysis(self):
        if not hasattr(self, 'dataset_path'):
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("⏳ Analiz Ediliyor...")
        self.send_log_signal.emit("BİLGİ", "Veri seti analizi başladı...")

        self.worker = AnalysisWorkerThread(self.dataset_path)
        self.worker.finished.connect(self.on_analysis_done)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_done(self, result):
        self.analysis_result = result
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🔍 Analiz Et")

        self.update_overview(result)
        self.update_classes(result)
        self.update_details(result)

        self.export_png_btn.setEnabled(True)
        self.export_pdf_btn.setEnabled(True)

        self.send_log_signal.emit("BİLGİ", f"Algılanan yapı: {result['layout']}")
        for err in result["errors"][:5]:
            self.send_log_signal.emit("HATA", err)
        if len(result["errors"]) > 5:
            self.send_log_signal.emit("HATA", f"... ve {len(result['errors']) - 5} hata daha.")

        if result["total_images"] == 0:
            self.send_log_signal.emit("HATA", "Hiç görsel bulunamadı, analiz sonucu boş.")
            return

        if result["estimated_bbox_count"] > 0:
            self.send_log_signal.emit(
                "BİLGİ",
                f"{result['estimated_bbox_count']} kutunun görsel boyutu okunamadı, "
                "bbox boyutları 640px varsayımıyla tahmin edildi."
            )

        total = result["total_annotations"]
        classes = len(result["class_counts"])
        self.send_log_signal.emit("BAŞARILI", f"Analiz tamamlandı! {total} anotasyon, {classes} sınıf bulundu.")

        if hasattr(self.window(), 'show_toast'):
            self.window().show_toast("Veri seti analizi başarıyla tamamlandı!")

    def on_analysis_error(self, err):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🔍 Analiz Et")
        self.send_log_signal.emit("HATA", f"Analiz hatası: {err}")

    # =========================================================================
    # GÜNCELLEMELERİ
    # =========================================================================
    def update_overview(self, r):
        self.overview_msg.hide()

        self.kpi_images.set_value(f"{r['total_images']:,}".replace(',', '.'))
        self.kpi_labels.set_value(f"{r['total_labels']:,}".replace(',', '.'))
        self.kpi_annotations.set_value(f"{r['total_annotations']:,}".replace(',', '.'))
        self.kpi_classes.set_value(str(len(r['class_counts'])))
        self.kpi_missing.set_value(str(len(r['missing_labels'])))

        missing_color = "#FF5252" if r["missing_labels"] else "#4CAF50"
        self.kpi_missing.value_lbl.setStyleSheet(
            f"color: {missing_color}; font-size: 18pt; font-weight: bold; border: none;"
        )

        # Split dağılımı donut
        split_data = {}
        for split_name, split_info in r["splits"].items():
            split_data[split_name] = split_info["image_count"]
        self.donut_chart.set_data(split_data, "Split Dağılımı (Görsel)")

        # BBox boyut dağılımı
        self.bbox_chart.set_data(r["bbox_sizes"], estimated=r["estimated_bbox_count"] > 0)

    def update_classes(self, r):
        self.bar_chart.set_data(r["class_counts"], "Sınıf Bazlı Anotasyon Dağılımı")

    def update_details(self, r):
        # Split tablosu
        splits = r["splits"]
        self.detail_table.setRowCount(len(splits))
        for i, (split_name, s) in enumerate(splits.items()):
            self.detail_table.setItem(i, 0, QTableWidgetItem(split_name))
            self.detail_table.setItem(i, 1, QTableWidgetItem(str(s["image_count"])))
            self.detail_table.setItem(i, 2, QTableWidgetItem(str(s["label_count"])))
            self.detail_table.setItem(i, 3, QTableWidgetItem(str(s["annotation_count"])))
            self.detail_table.setItem(i, 4, QTableWidgetItem(str(len(s["images_without_labels"]))))
            self.detail_table.setItem(i, 5, QTableWidgetItem(str(len(s["empty_labels"]))))

            for col in range(6):
                item = self.detail_table.item(i, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Sınıf tablosu
        total_ann = r["total_annotations"]
        sorted_classes = sorted(r["class_counts"].items(), key=lambda x: x[1], reverse=True)
        self.class_table.setRowCount(len(sorted_classes))

        for i, (cls_name, count) in enumerate(sorted_classes):
            self.class_table.setItem(i, 0, QTableWidgetItem(cls_name))

            count_item = QTableWidgetItem(f"{count:,}".replace(',', '.'))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.class_table.setItem(i, 1, count_item)

            pct = (count / total_ann * 100) if total_ann > 0 else 0
            pct_item = QTableWidgetItem(f"%{pct:.2f}")
            pct_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.class_table.setItem(i, 2, pct_item)

            # Dengesizlik kontrolü
            avg = total_ann / len(sorted_classes) if sorted_classes else 0
            if count < avg * 0.3:
                status = "⚠️ Az Temsil"
                color = "#FF5252"
            elif count > avg * 2.5:
                status = "📈 Baskın"
                color = "#FBC02D"
            else:
                status = "✅ Dengeli"
                color = "#4CAF50"

            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(QColor(color))
            self.class_table.setItem(i, 3, status_item)

    # =========================================================================
    # DIŞA AKTARMA
    # =========================================================================
    def export_png(self):
        if not self.analysis_result:
            return

        save_dir = QFileDialog.getExistingDirectory(self, "PNG Kayıt Klasörünü Seçin", "")
        if not save_dir:
            return

        name = self.analysis_result["name"]
        count = 0

        # Sınıf dağılımı çubuğu
        pixmap = self.bar_chart.grab()
        pixmap.save(os.path.join(save_dir, f"{name}_sinif_dagilimi.png"))
        count += 1

        # Split donut
        pixmap = self.donut_chart.grab()
        pixmap.save(os.path.join(save_dir, f"{name}_split_dagilimi.png"))
        count += 1

        # BBox boyut
        pixmap = self.bbox_chart.grab()
        pixmap.save(os.path.join(save_dir, f"{name}_bbox_boyut.png"))
        count += 1

        self.send_log_signal.emit("BAŞARILI", f"{count} grafik PNG olarak kaydedildi: {save_dir}")
        if hasattr(self.window(), 'show_toast'):
            self.window().show_toast(f"{count} grafik başarıyla kaydedildi!")

    def export_pdf(self):
        if not self.analysis_result:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "PDF Raporu Kaydet", f"{self.analysis_result['name']}_rapor.pdf",
            "PDF Dosyası (*.pdf)"
        )
        if not save_path:
            return

        try:
            writer = QPdfWriter(save_path)
            writer.setResolution(96)  # varsayılan 1200 dpi'da piksel koordinatları çok küçük kalır
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            writer.setPageMargins(QMarginsF(20, 20, 20, 20), QPageLayout.Unit.Millimeter)

            painter = QPainter(writer)
            r = self.analysis_result
            page_w = writer.width()

            # Başlık
            painter.setPen(QColor("#2E7D32"))
            painter.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
            painter.drawText(50, 100, "Veri Seti Analiz Raporu")

            painter.setPen(QColor("#555555"))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(50, 160, f"Veri Seti: {r['name']}")
            painter.drawText(50, 200, f"Yol: {r['path']}")

            y = 280
            painter.setPen(QColor("#000000"))
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.drawText(50, y, "Genel İstatistikler")
            y += 50

            painter.setFont(QFont("Consolas", 11))
            stats = [
                f"Toplam Görsel: {r['total_images']:,}".replace(',', '.'),
                f"Toplam Etiket: {r['total_labels']:,}".replace(',', '.'),
                f"Toplam Anotasyon: {r['total_annotations']:,}".replace(',', '.'),
                f"Sınıf Sayısı: {len(r['class_counts'])}",
                f"Eksik Etiket: {len(r['missing_labels'])}",
                f"Boş Etiket: {len(r['empty_labels'])}",
            ]
            for stat in stats:
                painter.drawText(80, y, stat)
                y += 40

            # Split bilgileri
            y += 30
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.drawText(50, y, "Split Bilgileri")
            y += 50
            painter.setFont(QFont("Consolas", 11))
            for split_name, split_data in r["splits"].items():
                painter.drawText(80, y, f"{split_name}: {split_data['image_count']} görsel, {split_data['annotation_count']} anotasyon")
                y += 40

            # Sınıf dağılımı
            y += 30
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.drawText(50, y, "Sınıf Dağılımı")
            y += 50
            painter.setFont(QFont("Consolas", 11))
            total_ann = r["total_annotations"]
            sorted_classes = sorted(r["class_counts"].items(), key=lambda x: x[1], reverse=True)
            for cls_name, count in sorted_classes:
                pct = (count / total_ann * 100) if total_ann > 0 else 0
                text = f"{cls_name}: {count:,} (%{pct:.1f})".replace(',', '.')
                painter.drawText(80, y, text)
                y += 35

                if y > writer.height() - 100:
                    writer.newPage()
                    y = 80

            painter.end()

            self.send_log_signal.emit("BAŞARILI", f"PDF raporu oluşturuldu: {save_path}")
            if hasattr(self.window(), 'show_toast'):
                self.window().show_toast("PDF raporu başarıyla oluşturuldu!")

        except Exception as e:
            self.send_log_signal.emit("HATA", f"PDF oluşturma hatası: {str(e)}")