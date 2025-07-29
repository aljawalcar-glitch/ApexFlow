# -*- coding: utf-8 -*-
"""
الفئة الأساسية لصفحات الوظائف في ApexFlow
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from .theme_aware_widget import make_theme_aware
from .file_list_frame import FileListFrame
from .ui_helpers import create_button, create_title

class BasePageWidget(QWidget):
    """
    فئة أساسية لصفحات الوظائف لتقليل تكرار الكود.
    تحتوي على العناصر المشتركة مثل العنوان، إطار قائمة الملفات، وتخطيط الأزرار.
    """
    def __init__(self, page_title, theme_key, parent=None):
        """
        :param page_title: عنوان الصفحة الذي سيظهر في الأعلى.
        :param theme_key: مفتاح السمة الخاص بالصفحة (e.g., "merge_page").
        :param parent: الويدجت الأب.
        """
        super().__init__(parent)
        
        # جعل الويدجت متجاوبًا مع السمات
        self.theme_handler = make_theme_aware(self, theme_key)

        # التخطيط الرئيسي
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # إنشاء وإضافة العنوان
        self.title_label = create_title(page_title)
        self.main_layout.addWidget(self.title_label)

        # تخطيط الأزرار العلوية
        self.top_buttons_layout = QHBoxLayout()
        self.top_buttons_layout.setSpacing(15)
        self.main_layout.addLayout(self.top_buttons_layout)

        # إضافة مساحة فارغة
        self.main_layout.addStretch(1)

        # إطار قائمة الملفات
        self.file_list_frame = FileListFrame()
        self.main_layout.addWidget(self.file_list_frame)

        # تخطيط الأزرار السفلية (للعمليات)
        self.action_buttons_layout = QHBoxLayout()
        self.action_buttons_layout.setSpacing(15)
        self.main_layout.addLayout(self.action_buttons_layout)

        # إعداد الاتصالات الأساسية
        self.file_list_frame.files_changed.connect(self.on_files_changed)

    def add_top_button(self, text, on_click):
        """
        إضافة زر إلى شريط الأزرار العلوي (مثل زر اختيار الملفات).
        """
        button = create_button(text)
        button.clicked.connect(on_click)
        self.top_buttons_layout.addWidget(button)
        return button

    def add_action_button(self, text, on_click, is_default=False):
        """
        إضافة زر إلى شريط أزرار العمليات السفلي.
        """
        button = create_button(text, is_default=is_default)
        button.clicked.connect(on_click)
        self.action_buttons_layout.addWidget(button)
        # إخفاء زر الإجراء افتراضيًا حتى يتم تحديد الملفات
        button.hide()
        return button

    def on_files_changed(self, files):
        """
        دالة افتراضية يتم استدعاؤها عند تغيير قائمة الملفات.
        يجب على الفئات الفرعية تنفيذ هذه الدالة لإظهار/إخفاء أزرار الإجراءات.
        """
        # يمكن للفئات الفرعية إعادة تعريف هذه الدالة
        pass

    def get_valid_files(self):
        """
        الحصول على قائمة الملفات الصالحة من إطار قائمة الملفات.
        """
        return self.file_list_frame.get_valid_files()

    def clear_files(self):
        """
        مسح جميع الملفات من القائمة.
        """
        self.file_list_frame.clear_all_files()
