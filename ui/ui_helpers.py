# -*- coding: utf-8 -*-
"""
مساعدات لواجهة المستخدم - دوال لإنشاء عناصر واجهة مستخدم مشتركة
"""

from PySide6.QtWidgets import QPushButton, QLabel, QDialog, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QComboBox
from PySide6.QtCore import Signal
from .theme_manager import apply_theme_style
from modules.translator import tr

def create_button(text, on_click=None, is_default=False):
    """
    إنشاء زر بتصميم موحد.
    """
    button = QPushButton(text)
    if on_click:
        button.clicked.connect(on_click)
    
    # تطبيق نمط الثيمة على الزر
    apply_theme_style(button, "button", auto_register=True)
    
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
    apply_theme_style(title, "title_text", auto_register=True)
    return title

def create_section_label(text):
    """
    إنشاء تسمية قسم بتصميم موحد.
    """
    label = QLabel(text)
    # تطبيق نمط الثيمة على تسمية القسم
    apply_theme_style(label, "label", auto_register=True)
    label.setStyleSheet(label.styleSheet() + "font-weight: bold;")
    return label

def create_info_label(text):
    """
    إنشاء تسمية معلومات بتصميم موحد.
    """
    label = QLabel(text)
    # تطبيق نمط الثيمة على تسمية المعلومات
    apply_theme_style(label, "secondary_text", auto_register=True)
    return label

class CustomMessageBox(QDialog):
    """
    مربع حوار مخصص متوافق مع السمات.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("warning"))
        self.setModal(True)
        apply_theme_style(self, "dialog")

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.message_label = QLabel()
        self.message_label.setWordWrap(False) # تعديل: منع التفاف النص
        apply_theme_style(self.message_label, "label")
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
