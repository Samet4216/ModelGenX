"""
Bilgisayarın donanım kaynaklarını (GPU, VRAM, RAM, CPU) ve anlık saati alt çubukta canlı gösterir.
"""
import ctypes
from ctypes import byref, c_uint, c_ulonglong, Structure
import psutil
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QFont
from menu.menu_style import STATUS_BAR_STYLE

class nvmlMemory_t(Structure):
    _fields_ = [('total', c_ulonglong), ('free', c_ulonglong), ('used', c_ulonglong)]

class nvmlUtilization_t(Structure):
    _fields_ = [('gpu', c_uint), ('memory', c_uint)]

class SystemMetricsReader: #"NVIDIA GPU ve Sistem (CPU/RAM) donanım verilerini hafif ve yerel yoldan okur
    def __init__(self):
        self.has_nvml = False
        self.device = None
        self.nvml = None
        self._init_nvml()

    def _init_nvml(self):
        try:
            self.nvml = ctypes.CDLL('nvml.dll')
            if self.nvml.nvmlInit() == 0:
                self.device = ctypes.c_void_p()
                if self.nvml.nvmlDeviceGetHandleByIndex(0, byref(self.device)) == 0:
                    self.has_nvml = True
        except Exception: self.has_nvml = False

    def get_metrics(self): #gerçek donanım verilerini çeker
        metrics = {
            "gpu_util": None,
            "vram_used": None,
            "vram_total": None,
            "ram_used": 0.0,
            "ram_total": 0.0,
            "cpu_percent": 0.0,
        }
        # CPU ve RAM (psutil)
        try:
            metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            metrics["ram_used"] = ram.used / (1024 ** 3)
            metrics["ram_total"] = ram.total / (1024 ** 3)
        except Exception: pass

        # NVIDIA GPU ve VRAM (Yerel NVML)
        if self.has_nvml and self.device:
            try:
                mem = nvmlMemory_t()
                if self.nvml.nvmlDeviceGetMemoryInfo(self.device, byref(mem)) == 0:
                    metrics["vram_used"] = mem.used / (1024 ** 3)
                    metrics["vram_total"] = mem.total / (1024 ** 3)
                util = nvmlUtilization_t()
                if self.nvml.nvmlDeviceGetUtilizationRates(self.device, byref(util)) == 0:
                    metrics["gpu_util"] = util.gpu
            except Exception: pass

        return metrics

class SystemStatusBar(QFrame):
    """
    Alt Cyberpunk Durum Çubuğu:
    - ● SİSTEM ÇEVRİMİÇİ rozeti
    - GPU %0 | VRAM 0.2/6.0 GB | RAM 12.6/15.2 GB | CPU %14
    - Sağda anlık canlı saat (hh:mm:ssZ)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SystemStatusBar")
        self.metrics_reader = SystemMetricsReader()
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(20)
        self.setStyleSheet(STATUS_BAR_STYLE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(18)

        # 1. Canlı Durum Rozeti
        self.status_badge = QLabel("● SİSTEM ÇEVRİMİÇİ")
        self.status_badge.setStyleSheet("color: #38E07A; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.status_badge)

        # 2. Donanım Metrikleri Etiketi
        self.metrics_label = QLabel()
        self.metrics_label.setFont(QFont("Consolas", 7))
        self.metrics_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.metrics_label)
        layout.addStretch()

        # 3. Sağ Canlı Zaman Etiketi
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Consolas", 10))
        self.time_label.setStyleSheet("color: #70C4FF; font-weight: bold;")
        layout.addWidget(self.time_label)

        # Zamanlayıcı (Her 1.5 saniyede bir hafifçe günceller)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1500)
        self.update_status()

    def update_status(self):
        m = self.metrics_reader.get_metrics()
        parts = []
        # GPU
        if m["gpu_util"] is not None: parts.append(f'<span style="color:#5A7699;">GPU</span> <b style="color:#70C4FF;">%{m["gpu_util"]}</b>')
        else: parts.append('<span style="color:#5A7699;">GPU</span> <b style="color:#8CA6BE;">--</b>')
        # VRAM
        if m["vram_used"] is not None and m["vram_total"] is not None: parts.append(f'<span style="color:#5A7699;">VRAM</span> <b style="color:#E4F9ED;">{m["vram_used"]:.1f}/{m["vram_total"]:.1f} GB</b>')
        # RAM
        parts.append(f'<span style="color:#5A7699;">RAM</span> <b style="color:#E4F9ED;">{m["ram_used"]:.1f}/{m["ram_total"]:.1f} GB</b>')
        # CPU
        parts.append(f'<span style="color:#5A7699;">CPU</span> <b style="color:#70C4FF;">%{int(m["cpu_percent"])}</b>')
        self.metrics_label.setText(" &nbsp;│&nbsp; ".join(parts))
        # Canlı Zaman
        now_str = QTime.currentTime().toString("hh:mm:ss")
        self.time_label.setText(f"{now_str}")
