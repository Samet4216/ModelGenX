import os
import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont


class KPICard(QFrame):
    """Tek bir KPI bilgi kartı."""
    def __init__(self, icon, title, value="0", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0A1224;
                border: 1px solid #15243B;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(80)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_lbl = QLabel(f"{icon} {title}")
        title_lbl.setStyleSheet("color: #8CA6BE; font-size: 9pt; font-weight: bold; border: none;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.value_lbl = QLabel(str(value))
        self.value_lbl.setStyleSheet("color: #4CAF50; font-size: 18pt; font-weight: bold; border: none;")
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_lbl)
        layout.addWidget(self.value_lbl)

    def set_value(self, val):
        self.value_lbl.setText(str(val))


class BarChartWidget(QWidget):
    """Yatay çubuk grafik widget'ı - Sınıf dağılımı için."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}  # {"class_name": count}
        self.title = "Sınıf Dağılımı"
        self.setMinimumHeight(200)

    def set_data(self, data, title="Sınıf Dağılımı"):
        self.data = data
        self.title = title
        self.setMinimumHeight(max(200, len(data) * 30 + 60))
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Arka plan
        painter.fillRect(0, 0, w, h, QColor("#050A15"))

        # Başlık
        painter.setPen(QColor("#4CAF50"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(10, 25, self.title)

        if not self.data:
            return

        sorted_data = sorted(self.data.items(), key=lambda x: x[1], reverse=True)
        max_val = max(self.data.values()) if self.data else 1

        left_margin = 120
        right_margin = 80
        top_start = 45
        bar_height = 20
        bar_gap = 8
        available_width = w - left_margin - right_margin

        for i, (name, count) in enumerate(sorted_data):
            y = top_start + i * (bar_height + bar_gap)
            if y + bar_height > h:
                break

            # Sınıf adı
            painter.setPen(QColor("#9BAEBC"))
            painter.setFont(QFont("Consolas", 9))
            painter.drawText(5, y + bar_height - 4, name[:14])

            # Çubuk
            bar_w = int((count / max_val) * available_width) if max_val > 0 else 0
            bar_w = max(bar_w, 3)

            # Gradient efekti
            color = QColor("#2E7D32")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(left_margin, y, bar_w, bar_height, 4, 4)

            # Parlak üst katman
            highlight = QColor("#4CAF50")
            highlight.setAlpha(80)
            painter.setBrush(highlight)
            painter.drawRoundedRect(left_margin, y, bar_w, bar_height // 2, 4, 4)

            # Değer
            painter.setPen(QColor("#81C784"))
            painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            painter.drawText(left_margin + bar_w + 8, y + bar_height - 4, f"{count:,}".replace(',', '.'))

        painter.end()


class DonutChartWidget(QWidget):
    """Donut (Halka) grafik - Split dağılımı için."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        self.title = "Split Dağılımı"
        self.setMinimumSize(250, 250)

    def set_data(self, data, title="Split Dağılımı"):
        self.data = data
        self.title = title
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor("#050A15"))

        # Başlık
        painter.setPen(QColor("#4CAF50"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(10, 25, self.title)

        if not self.data:
            return

        total = sum(self.data.values())
        if total == 0:
            return

        colors = [
            QColor("#2E7D32"), QColor("#1565C0"), QColor("#FBC02D"),
            QColor("#E53935"), QColor("#8E24AA"), QColor("#00ACC1"),
        ]

        # Donut çizimi
        center_x = w // 2
        center_y = (h + 30) // 2
        radius = min(w, h - 40) // 2 - 30
        inner_radius = radius * 0.55

        start_angle = 90 * 16  # 12 o'clock

        for i, (name, count) in enumerate(self.data.items()):
            span = int((count / total) * 360 * 16)
            color = colors[i % len(colors)]

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            rect = (center_x - radius, center_y - radius, radius * 2, radius * 2)
            painter.drawPie(*rect, start_angle, -span)

            start_angle -= span

        # İç daire (donut deliği)
        painter.setBrush(QColor("#050A15"))
        painter.drawEllipse(
            int(center_x - inner_radius), int(center_y - inner_radius),
            int(inner_radius * 2), int(inner_radius * 2)
        )

        # Ortadaki toplam
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        total_str = f"{total:,}".replace(',', '.')
        text_rect = painter.fontMetrics().boundingRect(total_str)
        painter.drawText(
            center_x - text_rect.width() // 2,
            center_y + text_rect.height() // 4,
            total_str
        )

        # Lejant
        legend_y = h - 20
        legend_x = 10
        painter.setFont(QFont("Consolas", 9))
        for i, (name, count) in enumerate(self.data.items()):
            color = colors[i % len(colors)]
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(legend_x, legend_y - 10, 12, 12, 3, 3)

            painter.setPen(QColor("#9BAEBC"))
            pct = (count / total * 100) if total > 0 else 0
            painter.drawText(legend_x + 18, legend_y, f"{name}: {count} (%{pct:.1f})")
            legend_x += 160

        painter.end()


class BBoxSizeChart(QWidget):
    """BBox boyut dağılımı: Küçük / Orta / Büyük."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {"Küçük (<32²)": 0, "Orta (32²-96²)": 0, "Büyük (>96²)": 0}
        self.title = "BBox Boyut Dağılımı"
        self.setMinimumHeight(180)

    def set_data(self, bbox_sizes, estimated=False):
        """
        bbox_sizes: [(w_px, h_px), ...] kutu boyutları PİKSEL cinsinden.
        COCO tanımı: alan < 32² küçük, 32²-96² orta, > 96² büyük.
        estimated: Bazı görsellerin boyutu okunamayıp 640px varsayıldıysa True.
        """
        small, medium, large = 0, 0, 0
        for w, h in bbox_sizes:
            area = w * h
            if area < 32 * 32:
                small += 1
            elif area < 96 * 96:
                medium += 1
            else:
                large += 1
        self.data = {"Küçük (<32²)": small, "Orta (32²-96²)": medium, "Büyük (>96²)": large}
        self.title = "BBox Boyut Dağılımı (tahmini)" if estimated else "BBox Boyut Dağılımı"
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor("#050A15"))

        painter.setPen(QColor("#4CAF50"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(10, 25, self.title)

        total = sum(self.data.values())
        if total == 0:
            painter.setPen(QColor("#555555"))
            painter.drawText(w // 2 - 50, h // 2, "Veri yok")
            painter.end()
            return

        colors = [QColor("#FBC02D"), QColor("#4CAF50"), QColor("#1565C0")]
        bar_width = (w - 80) // 3
        max_bar_h = h - 70

        for i, (label, count) in enumerate(self.data.items()):
            x = 30 + i * (bar_width + 10)
            ratio = count / total if total > 0 else 0
            bar_h = int(ratio * max_bar_h)
            bar_h = max(bar_h, 3)

            y = h - 30 - bar_h

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(colors[i])
            painter.drawRoundedRect(x, y, bar_width - 10, bar_h, 6, 6)

            # Label
            painter.setPen(QColor("#9BAEBC"))
            painter.setFont(QFont("Consolas", 8))
            painter.drawText(x, h - 12, label)

            # Değer
            painter.setPen(QColor("#FFFFFF"))
            painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            pct_str = f"%{ratio*100:.0f}"
            painter.drawText(x + 5, y - 5, f"{count} ({pct_str})")

        painter.end()