# -*- coding: utf-8 -*-
"""
نظام الإشعارات الشفافة
Transparent Notification System
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide6.QtGui import QPainter, QColor, QFont, QPixmap, QPainterPath
import os

class NotificationWidget(QWidget):
    """ويدجت الإشعار الشفاف"""
    
    # إشارة انتهاء الإشعار
    finished = Signal()
    
    def __init__(self, message, notification_type="info", parent=None):
        super().__init__(parent)
        
        self.message = message
        self.notification_type = notification_type
        self.parent_widget = parent
        
        # إعداد النافذة
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(60)
        
        # إعداد الواجهة
        self.setup_ui()
        
        # إعداد الرسوم المتحركة
        self.setup_animations()
        
        # مؤقت الإخفاء التلقائي
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide_notification)
        
    def setup_ui(self):
        """إعداد واجهة الإشعار"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # أيقونة نوع الإشعار
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignCenter)
        
        # تحديد الأيقونة حسب النوع
        icon_text = self.get_icon_for_type()
        self.icon_label.setText(icon_text)
        self.icon_label.setStyleSheet(f"""
            font-size: 16px;
            color: {self.get_color_for_type()};
            background: transparent;
            border: none;
        """)
        
        # نص الرسالة
        self.message_label = QLabel(self.message)
        self.message_label.setStyleSheet(f"""
            color: white;
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        self.message_label.setWordWrap(True)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label, 1)
        
    def get_icon_for_type(self):
        """الحصول على أيقونة حسب نوع الإشعار"""
        icons = {
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "info": "ℹ"
        }
        return icons.get(self.notification_type, "ℹ")
    
    def get_color_for_type(self):
        """الحصول على لون حسب نوع الإشعار"""
        colors = {
            "success": "#4ade80",  # أخضر
            "warning": "#fbbf24",  # أصفر
            "error": "#f87171",    # أحمر
            "info": "#60a5fa"      # أزرق
        }
        return colors.get(self.notification_type, "#60a5fa")
    
    def get_background_color_for_type(self):
        """الحصول على لون الخلفية حسب نوع الإشعار"""
        colors = {
            "success": "rgba(34, 197, 94, 0.9)",   # أخضر شفاف
            "warning": "rgba(245, 158, 11, 0.9)",  # أصفر شفاف
            "error": "rgba(239, 68, 68, 0.9)",     # أحمر شفاف
            "info": "rgba(59, 130, 246, 0.9)"      # أزرق شفاف
        }
        return colors.get(self.notification_type, "rgba(59, 130, 246, 0.9)")
    
    def setup_animations(self):
        """إعداد الرسوم المتحركة"""
        # رسم متحرك للظهور
        self.show_animation = QPropertyAnimation(self, b"geometry")
        self.show_animation.setDuration(300)
        self.show_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # رسم متحرك للإخفاء
        self.hide_animation = QPropertyAnimation(self, b"geometry")
        self.hide_animation.setDuration(250)
        self.hide_animation.setEasingCurve(QEasingCurve.InCubic)
        self.hide_animation.finished.connect(self.on_hide_finished)
        
        # رسم متحرك للشفافية
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
    
    def paintEvent(self, event):
        """رسم الخلفية الشفافة"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # رسم الخلفية المدورة الشفافة
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        
        # لون الخلفية حسب نوع الإشعار
        bg_color = QColor(self.get_background_color_for_type())
        painter.fillPath(path, bg_color)
        
        # إطار رفيع
        painter.setPen(QColor(self.get_color_for_type()))
        painter.drawPath(path)
    
    def show_notification(self, duration=4000):
        """عرض الإشعار"""
        if not self.parent_widget:
            return
            
        # حساب الموضع (أسفل شريط العنوان)
        parent_rect = self.parent_widget.geometry()
        notification_width = min(400, parent_rect.width() - 40)
        self.setFixedWidth(notification_width)
        
        # الموضع الابتدائي (مخفي فوق النافذة)
        start_x = parent_rect.x() + (parent_rect.width() - notification_width) // 2
        start_y = parent_rect.y() - self.height()
        
        # الموضع النهائي (أسفل شريط العنوان)
        end_y = parent_rect.y() + 35  # أسفل شريط العنوان
        
        # تعيين الموضع الابتدائي
        self.setGeometry(start_x, start_y, notification_width, self.height())
        
        # إعداد الرسم المتحرك للظهور
        self.show_animation.setStartValue(QRect(start_x, start_y, notification_width, self.height()))
        self.show_animation.setEndValue(QRect(start_x, end_y, notification_width, self.height()))
        
        # عرض النافذة وبدء الرسم المتحرك
        self.show()
        self.show_animation.start()
        
        # بدء مؤقت الإخفاء
        self.hide_timer.start(duration)
    
    def hide_notification(self):
        """إخفاء الإشعار"""
        if not self.isVisible():
            return
            
        # إيقاف مؤقت الإخفاء
        self.hide_timer.stop()
        
        # حساب الموضع للإخفاء (فوق النافذة)
        current_rect = self.geometry()
        hide_y = current_rect.y() - self.height() - 10
        
        # إعداد الرسم المتحرك للإخفاء
        self.hide_animation.setStartValue(current_rect)
        self.hide_animation.setEndValue(QRect(current_rect.x(), hide_y, current_rect.width(), current_rect.height()))
        
        # بدء الرسم المتحرك
        self.hide_animation.start()
    
    def on_hide_finished(self):
        """عند انتهاء رسم الإخفاء"""
        self.hide()
        self.finished.emit()
        self.deleteLater()
    
    def mousePressEvent(self, event):
        """إخفاء الإشعار عند النقر عليه"""
        if event.button() == Qt.LeftButton:
            self.hide_notification()


class NotificationManager:
    """مدير الإشعارات"""
    
    def __init__(self):
        self.active_notifications = []
        self.max_notifications = 3  # حد أقصى للإشعارات المتزامنة
    
    def show_notification(self, parent, message, notification_type="info", duration=4000):
        """عرض إشعار جديد"""
        # إزالة الإشعارات الزائدة
        while len(self.active_notifications) >= self.max_notifications:
            old_notification = self.active_notifications.pop(0)
            try:
                if old_notification and not old_notification.isHidden():
                    old_notification.hide_notification()
            except RuntimeError:
                # Widget was already deleted, just ignore since it has been popped.
                pass
        
        # إنشاء إشعار جديد
        notification = NotificationWidget(message, notification_type, parent)
        notification.finished.connect(lambda: self.remove_notification(notification))
        notification.destroyed.connect(lambda: self.remove_notification(notification))
        
        # إضافة للقائمة النشطة
        self.active_notifications.append(notification)
        
        # عرض الإشعار
        notification.show_notification(duration)
        
        return notification
    
    def remove_notification(self, notification):
        """إزالة إشعار من القائمة النشطة"""
        if notification in self.active_notifications:
            self.active_notifications.remove(notification)
    
    def clear_all(self):
        """إزالة جميع الإشعارات"""
        for notification in self.active_notifications[:]:
            try:
                if notification and not notification.isHidden():
                    notification.hide_notification()
            except RuntimeError:
                # Widget was already deleted, just ignore.
                pass
        self.active_notifications.clear()


# مدير الإشعارات العام
global_notification_manager = NotificationManager()


def show_notification(parent, message, notification_type="info", duration=4000):
    """دالة مساعدة لعرض الإشعارات"""
    try:
        # Check if the underlying C++ object of the parent is still valid.
        # Accessing any attribute will raise RuntimeError if it's deleted.
        if parent is not None:
            _ = parent.isWidgetType()
    except RuntimeError:
        # The parent widget has been deleted, so we can't show a notification attached to it.
        print(f"INFO: Notification parent widget has been deleted. Aborting notification: '{message}'")
        return None
        
    return global_notification_manager.show_notification(parent, message, notification_type, duration)


def show_success(parent, message, duration=3000):
    """عرض إشعار نجاح"""
    return show_notification(parent, message, "success", duration)


def show_warning(parent, message, duration=4000):
    """عرض إشعار تحذير"""
    return show_notification(parent, message, "warning", duration)


def show_error(parent, message, duration=5000):
    """عرض إشعار خطأ"""
    return show_notification(parent, message, "error", duration)


def show_info(parent, message, duration=3000):
    """عرض إشعار معلومات"""
    return show_notification(parent, message, "info", duration)
