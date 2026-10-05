#tüm videolar indikten sonra toast bildirimini göstermek için
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QVariantAnimation, QEasingCurve, QTimer, QPoint
from PyQt6.QtGui import QColor

class ToastNotification(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Sadece parent içinde sınırlandırılmış bir widget olacak
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # Tıklamaları engellememesi için
        self.setFixedSize(300, 60)
        
        self.init_ui()
        self.hide()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        self.icon_lbl = QLabel("✅")
        self.icon_lbl.setStyleSheet("font-size: 20px; background: transparent;")
        
        self.text_lbl = QLabel("Tüm videolar başarıyla indirildi!")
        self.text_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background: transparent;")
        self.text_lbl.setWordWrap(True)
        
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_lbl, stretch=1)
        
        # Gölge
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        # Mavi (başlangıç) -> Yeşil (bitiş) renk animasyonu için değişkenler
        self.start_color = QColor("#1E90FF")
        self.end_color = QColor("#10B981")
        
        # Animasyon nesneleri
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.color_anim = QVariantAnimation(self)
        self.color_anim.valueChanged.connect(self.update_color)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_toast)

    def update_color(self, color):
        hex_color = color.name()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {hex_color};
                border-radius: 10px;
                border: none;
            }}
        """)

    def show_toast(self, message):
        self.text_lbl.setText(message)
        
        # Parent (MainWindow) boyutlarına göre başlangıç ve bitiş noktalarını hesapla
        if not self.parent(): return
            
        parent_rect = self.parent().rect()
        target_x = parent_rect.width() - self.width() - 30
        target_y = parent_rect.height() - self.height() - 70
        
        # Animasyon başlangıç noktası: Tamamen ekranın sağında (görünmez)
        start_x = parent_rect.width()
        self.move(start_x, target_y)
        self.update_color(self.start_color) # Başlangıç rengini set et
        self.raise_() # En üste al
        self.show()
        
        # Konum Animasyonu (Sağdan Sola)
        self.pos_anim.setDuration(600)
        self.pos_anim.setStartValue(QPoint(start_x, target_y))
        self.pos_anim.setEndValue(QPoint(target_x, target_y))
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_anim.start()
        
        # Renk Animasyonu (Maviden Yeşile)
        self.color_anim.setDuration(2500) # Konum oturduktan sonra yeşile dönmeye devam etsin
        self.color_anim.setStartValue(self.start_color)
        self.color_anim.setEndValue(self.end_color)
        self.color_anim.start()
        
        # 5 Saniye sonra otomatik kapat
        self.timer.start(5000)

    def hide_toast(self):
        self.timer.stop()
        
        # Kaybolurken de sağa doğru çıksın
        target_x = self.parent().rect().width()
        target_y = self.y()
        self.pos_anim.setDuration(500)
        self.pos_anim.setStartValue(self.pos())
        self.pos_anim.setEndValue(QPoint(target_x, target_y))
        self.pos_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.pos_anim.start()
        
        # Animasyon bitince widget'ı gizle
        self.pos_anim.finished.connect(self._on_hide_finished)
        
    def _on_hide_finished(self):
        try: self.pos_anim.finished.disconnect(self._on_hide_finished)
        except TypeError: pass
        self.hide()
