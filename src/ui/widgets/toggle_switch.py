# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QCheckBox, QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, Property, QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QShowEvent
from managers.theme_manager import global_theme_manager

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self._bg_color = global_theme_manager.get_color("toggle_bg_color")
        self._circle_color = global_theme_manager.get_color("toggle_circle_color")
        self._active_color = global_theme_manager.get_color("toggle_active_color")
        
        self._circle_position = 2
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        self.animation.setDuration(300)
        
        self.stateChanged.connect(self.start_animation)
        global_theme_manager.theme_changed.connect(self.update_colors)
        
        # تأخير إعداد الموضع الأولي قليلاً لضمان التهيئة الكاملة
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1, self._setup_initial_position)

    def sizeHint(self):
        return QSize(40, 20)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    @Property(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()

    def start_animation(self, value):
        self.animation.stop()
        circle_size = min(self.height() - 4, 16)  # حجم الدائرة متناسب مع الارتفاع
        if value:
            self.animation.setEndValue(self.width() - circle_size - 2)
        else:
            self.animation.setEndValue(2)
        self.animation.start()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        
        rect = QRect(0, 0, self.width(), self.height())
        
        # Determine background color based on state
        if self.isChecked():
            bg_color = self._active_color
        else:
            bg_color = self._bg_color
            
        # Draw the background
        p.setBrush(QColor(bg_color))
        p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)
        
        # Draw the circle - تأكد من وجود حجم صحيح
        if self.width() > 0 and self.height() > 0:
            circle_size = min(self.height() - 4, 16)
            circle_y = (self.height() - circle_size) // 2
            
            # تأكد من أن موضع الدائرة صحيح
            if self._circle_position < 2:
                self._circle_position = 2
            elif self._circle_position > self.width() - circle_size - 2:
                self._circle_position = self.width() - circle_size - 2
                
            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(int(self._circle_position), circle_y, circle_size, circle_size)

    def showEvent(self, event):
        super().showEvent(event)
        # Force initial position setup
        self._setup_initial_position()
        
    def _setup_initial_position(self):
        """إعداد الموضع الأولي للدائرة"""
        if self.width() <= 0 or self.height() <= 0:
            # إذا لم يتم تحديد الحجم بعد، أعد المحاولة لاحقاً
            from PySide6.QtCore import QTimer
            QTimer.singleShot(10, self._setup_initial_position)
            return
            
        circle_size = min(self.height() - 4, 16)
        if self.isChecked():
            self._circle_position = self.width() - circle_size - 2
        else:
            self._circle_position = 2
        self.update()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # إعادة تحديد موضع الدائرة عند تغيير الحجم
        self._setup_initial_position()

    def update_colors(self):
        self._bg_color = global_theme_manager.get_color("toggle_bg_color")
        self._circle_color = global_theme_manager.get_color("toggle_circle_color")
        self._active_color = global_theme_manager.get_color("toggle_active_color")
        self.update()

if __name__ == '__main__':
    app = QApplication([])
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Example usage
    toggle = ToggleSwitch()
    layout.addWidget(toggle)
    
    widget.show()
    app.exec()
