# -*- coding: utf-8 -*-
"""
الفئة الأساسية لصفحات الوظائف في ApexFlow
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from .theme_aware_widget import make_theme_aware
from .file_list_frame import FileListFrame
from .ui_helpers import create_button, create_title

class BasePageWidget(QWidget):
    """
    فئة أساسية لصفحات الوظائف لتقليل تكرار الكود.
    تحتوي على العناصر المشتركة مثل العنوان، إطار قائمة الملفات، وتخطيط الأزرار.
    """
    def __init__(self, page_title, theme_key, notification_manager, parent=None):
        """
        :param page_title: عنوان الصفحة الذي سيظهر في الأعلى.
        :param theme_key: مفتاح السمة الخاص بالصفحة (e.g., "merge_page").
        :param notification_manager: مدير الإشعارات المركزي.
        :param parent: الويدجت الأب.
        """
        super().__init__(parent)
        
        self.notification_manager = notification_manager
        
        # جعل الويدجت متجاوبًا مع السمات
        self.theme_handler = make_theme_aware(self, theme_key)

        # Use a QScrollArea to ensure the entire page is scrollable
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Apply theme to the scroll area to style the scrollbar
        make_theme_aware(scroll_area, "graphics_view")

        # Main container widget inside the scroll area
        self.content_widget = QWidget()
        scroll_area.setWidget(self.content_widget)

        # The main layout for the page's content
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Layout for the BasePageWidget itself, containing only the scroll area
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll_area)

        # إنشاء وإضافة العنوان
        self.title_label = create_title(page_title)
        self.main_layout.addWidget(self.title_label)

        # تخطيط الأزرار العلوية
        self.top_buttons_layout = QHBoxLayout()
        self.top_buttons_layout.setSpacing(15)
        self.main_layout.addLayout(self.top_buttons_layout)

        # إضافة مساحة فارغة مرنة فوق قائمة الملفات
        self.main_layout.addStretch(1)

        # إطار قائمة الملفات - مع عامل تمدد ليأخذ المساحة المتاحة
        self.file_list_frame = FileListFrame()
        self.main_layout.addWidget(self.file_list_frame, 2) # عامل تمدد أكبر

        # تخطيط الأزرار السفلية (للعمليات)
        self.action_buttons_layout = QHBoxLayout()
        self.action_buttons_layout.setSpacing(15)
        self.main_layout.addLayout(self.action_buttons_layout)

        # إعداد الاتصالات الأساسية
        self.file_list_frame.files_changed.connect(self.on_files_changed)

        # تفعيل السحب والإفلات للصفحة بأكملها
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """معالجة دخول السحب إلى الصفحة"""
        if event.mimeData().hasUrls():
            # إظهار الطبقة الذكية بدلاً من معالجة الحدث هنا
            main_window = self._get_main_window()
            if main_window and hasattr(main_window, 'smart_drop_overlay'):
                main_window.dragEnterEvent(event)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """معالجة إفلات الملفات على الصفحة"""
        # تمرير الحدث إلى النافذة الرئيسية لمعالجته عبر الطبقة الذكية
        main_window = self._get_main_window()
        if main_window:
            main_window.dropEvent(event)
            event.accept()
        else:
            event.ignore()

    def _get_main_window(self):
        """الحصول على النافذة الرئيسية للتطبيق"""
        parent = self.parent()
        while parent:
            if parent.__class__.__name__ == 'ApexFlow':
                return parent
            parent = parent.parent()
        
        # كحل بديل إذا لم يتم العثور على النافذة الرئيسية
        from PySide6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ApexFlow':
                return widget
        return None

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
