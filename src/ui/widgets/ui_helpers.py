# -*- coding: utf-8 -*-
"""
مساعدات لواجهة المستخدم - دوال لإنشاء عناصر واجهة مستخدم مشتركة
"""
import os
import sys
from PySide6.QtWidgets import QPushButton, QLabel, QDialog, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QComboBox, QWidget
from PySide6.QtGui import QPainter, QColor, QLinearGradient
from PySide6.QtCore import Signal
from src.managers.theme_manager import make_theme_aware
from src.utils.translator import tr

def create_button(text, on_click=None, is_default=False):
    """
    إنشاء زر بتصميم موحد.
    """
    button = QPushButton(text)
    if on_click:
        button.clicked.connect(on_click)
    
    # تطبيق نمط الثيمة على الزر
    make_theme_aware(button, "button")
    
    if is_default:
        button.setDefault(True)
        # يمكنك إضافة نمط خاص للزر الافتراضي هنا إذا أردت
        
    return button

def create_title(text):
    """
    إنشاء عنوان بتصميم موحد.
    """
    title = QLabel(text)
    # تطبيق نمط الثيمة على العنوان
    make_theme_aware(title, "title_text")
    return title

def create_info_label(text):
    """
    إنشاء تسمية معلومات بتصميم موحد.
    """
    label = QLabel(text)
    # تطبيق نمط الثيمة على تسمية المعلومات
    make_theme_aware(label, "secondary_text")
    return label

def get_icon_path(icon_name):
    """الحصول على مسار الأيقونة الصحيح سواء كان التطبيق مجمداً أم لا"""
    from src.utils.resource_path import get_icon_resource_path
    icon_path = get_icon_resource_path(icon_name)
    return icon_path if icon_path else f"assets/icons/default/{icon_name}.svg"

class CustomMessageBox(QDialog):
    """
    مربع حوار مخصص متوافق مع السمات.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("warning"))
        self.setModal(True)
        make_theme_aware(self, "dialog")

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.message_label = QLabel()
        self.message_label.setWordWrap(False) # تعديل: منع التفاف النص
        make_theme_aware(self.message_label, "label")
        self.layout.addWidget(self.message_label)

        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        self.result = QDialog.Rejected

    def setText(self, text):
        self.message_label.setText(text)

    def addButton(self, text, role):
        button = create_button(text)
        from PySide6.QtWidgets import QDialogButtonBox
        
        # تبسيط: استخدام القيم القياسية. تجاهل = مقبول، إلغاء = مرفوض
        dialog_result = QDialog.Rejected # القيمة الافتراضية
        if role == QDialogButtonBox.DestructiveRole:
            dialog_result = QDialog.Accepted # زر التجاهل سيعيد "مقبول"
        elif role == QDialogButtonBox.RejectRole:
            dialog_result = QDialog.Rejected # زر الإلغاء سيعيد "مرفوض"

        button.clicked.connect(lambda r=dialog_result: self.done(r))
        self.buttons_layout.addWidget(button)
        return button

    def exec(self):
        return super().exec()

class FocusAwareComboBox(QComboBox):
    """
    QComboBox مخصص يرسل إشارة عند الحصول على التركيز أو فقدانه.
    """
    focus_in = Signal()
    focus_out = Signal()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focus_in.emit()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.focus_out.emit()

def create_notification_button(icon_name, on_click=None):
    """
    إنشاء زر مخصص للإشعارات مع أيقونة.
    """
    from PySide6.QtGui import QIcon

    button = QPushButton()
    icon_path = get_icon_path(icon_name)
    button.setIcon(QIcon(icon_path))
    button.setStyleSheet("background-color: transparent;")  # إزالة الخلفية السوداء الافتراضية

    if on_click:
        button.clicked.connect(on_click)

    # تطبيق الثيم على الزر
    make_theme_aware(button, "icon_button")

    return button

def create_close_button(on_click=None):
    """
    إنشاء زر إغلاق مخصص.
    """
    return create_notification_button("close", on_click)
