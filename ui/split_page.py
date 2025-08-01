# -*- coding: utf-8 -*-
"""
صفحة تقسيم ملفات PDF
"""

from .base_page import BasePageWidget
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton, QWidget
)
from PySide6.QtCore import Qt
from .theme_manager import apply_theme_style
from .svg_icon_button import create_action_button
from .notification_system import show_success, show_warning, show_error, show_info
from modules.translator import tr
import os

class SplitPage(BasePageWidget):
    """
    واجهة المستخدم الخاصة بوظيفة تقسيم ملفات PDF.
    """
    def __init__(self, file_manager, operations_manager, parent=None):
        """
        :param file_manager: مدير الملفات لاختيار الملف.
        :param operations_manager: مدير العمليات لتنفيذ التقسيم.
        """
        super().__init__(page_title=tr("split_page_title"), theme_key="split_page", parent=parent)

        self.file_manager = file_manager
        self.operations_manager = operations_manager

        # متغيرات لحفظ معلومات المسار
        self.current_file_path = ""
        self.auto_save_path = ""

        # إضافة زر اختيار الملف
        self.add_top_button(
            text=tr("select_pdf_to_split"),
            on_click=self.select_file_for_splitting
        )

        # إنشاء فريم مسار الحفظ مع زر التقسيم
        self.create_save_location_frame()

        # إخفاء widget الحفظ في البداية
        self.save_and_split_widget.setVisible(False)

    def create_save_location_frame(self):
        """إنشاء فريم مسار الحفظ مع زر التقسيم محاذي"""
        # إنشاء widget container للتخطيط الأفقي
        self.save_and_split_widget = QWidget()
        # تطبيق نمط الثيمة على الحاوية
        apply_theme_style(self.save_and_split_widget, "frame", auto_register=True)
        self.save_and_split_layout = QHBoxLayout(self.save_and_split_widget)

        # فريم مجلد الحفظ
        self.save_location_frame = QGroupBox(tr("save_folder"))
        apply_theme_style(self.save_location_frame, "group_box", auto_register=True)
        save_layout = QVBoxLayout(self.save_location_frame)

        # تخطيط أفقي للمسار وزر التغيير
        path_layout = QHBoxLayout()

        # عرض المسار التلقائي
        self.save_location_label = QLabel(tr("auto_folder_creation"))
        apply_theme_style(self.save_location_label, "label", auto_register=True)
        self.save_location_label.setWordWrap(True)

        # تحديد لون الأيقونات حسب السمة
        from .theme_manager import global_theme_manager
        if global_theme_manager.current_theme == "light":
            icon_color = "#333333"  # لون داكن للوضع الفاتح
        else:
            icon_color = "#ffffff"  # لون أبيض للوضع المظلم

        # زر تغيير المجلد
        self.browse_save_btn = create_action_button("folder-open", 24, tr("change_folder"))
        self.browse_save_btn.set_icon_color(icon_color)
        self.browse_save_btn.clicked.connect(self.select_save_location)

        path_layout.addWidget(self.save_location_label, 1)
        path_layout.addWidget(self.browse_save_btn)

        save_layout.addLayout(path_layout)

        # فريم زر التقسيم
        self.split_button_frame = QGroupBox(tr("execute"))
        apply_theme_style(self.split_button_frame, "group_box", auto_register=True)
        split_layout = QVBoxLayout(self.split_button_frame)

        # زر التقسيم بأيقونة
        self.split_button = create_action_button("scissors", 32, tr("split_file"))
        self.split_button.set_icon_color(icon_color)
        self.split_button.clicked.connect(self.execute_split)

        split_layout.addWidget(self.split_button)
        split_layout.addStretch()

        # إضافة الفريمين للتخطيط الأفقي
        self.save_and_split_layout.addWidget(self.save_location_frame, 2)  # يأخذ مساحة أكبر
        self.save_and_split_layout.addWidget(self.split_button_frame, 0)  # مساحة صغيرة

        # إضافة الـ widget للتخطيط الرئيسي
        self.main_layout.addWidget(self.save_and_split_widget)

    def select_file_for_splitting(self):
        """
        فتح حوار لاختيار ملف PDF واحد وتحديث القائمة.
        """
        try:
            # مسح الملفات القديمة قبل إضافة الجديد
            self.clear_files()
            self.save_and_split_widget.setVisible(False)

            file = self.file_manager.select_pdf_files(title=tr("select_pdf_to_split_title"), multiple=False)
            if file and os.path.exists(file):
                self.current_file_path = file
                self.file_list_frame.add_files([file])

                # إنشاء مسار الحفظ التلقائي
                self.create_auto_save_path(file)

                # إظهار التخطيط الكامل (فريم الحفظ + زر التقسيم)
                self.save_and_split_widget.setVisible(True)

                # إشعار بنجاح تحديد الملف
                file_name = os.path.basename(file)
                show_info(self, f"{tr('file_selected_for_splitting')}: {file_name}", duration=3000)

            elif file:
                show_error(self, f"{tr('file_not_found')}: {file}")

        except Exception as e:
            show_error(self, f"{tr('error_selecting_file')}: {str(e)}")

    def create_auto_save_path(self, file_path):
        """إنشاء مسار الحفظ التلقائي في سطح المكتب"""
        # الحصول على اسم الملف بدون امتداد
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # الحصول على مسار سطح المكتب
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        # إنشاء اسم مجلد ذكي
        folder_name = f"{file_name}{tr('split_pages_suffix')}"

        # إنشاء مسار فريد لتجنب التضارب
        self.auto_save_path = self.create_unique_folder(desktop_path, folder_name)

        # تحديث النص المعروض
        self.save_location_label.setText(f"{tr('path_prefix')} {self.auto_save_path}")

    def create_unique_folder(self, base_path, folder_name):
        """إنشاء مجلد بأسم فريد لتجنب التضارب"""
        counter = 1
        original_name = folder_name

        while True:
            if counter == 1:
                new_folder_path = os.path.join(base_path, original_name)
            else:
                new_folder_path = os.path.join(base_path, f"{original_name}_{counter}")

            if not os.path.exists(new_folder_path):
                try:
                    os.makedirs(new_folder_path, exist_ok=True)
                    return new_folder_path
                except Exception as e:
                    print(f"Error creating folder: {e}")
                    return base_path

            counter += 1
            # تجنب الحلقة اللانهائية
            if counter > 100:
                return base_path

    def select_save_location(self):
        """اختيار مجلد الحفظ يدوياً"""
        from PySide6.QtWidgets import QFileDialog

        # فتح حوار اختيار المجلد
        directory = QFileDialog.getExistingDirectory(
            self,
            tr("select_save_folder_title"),
            os.path.join(os.path.expanduser("~"), "Desktop")
        )

        if directory:
            # إنشاء مجلد فرعي ذكي
            if self.current_file_path:
                file_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
                folder_name = f"{file_name}{tr('split_pages_suffix')}"
                self.auto_save_path = self.create_unique_folder(directory, folder_name)
                self.save_location_label.setText(f"{tr('path_prefix')} {self.auto_save_path}")

    def execute_split(self):
        """
        تنفيذ عملية التقسيم باستخدام مدير العمليات.
        """
        try:
            # التحقق من وجود ملف للتقسيم
            if not hasattr(self, 'current_file_path') or not self.current_file_path:
                show_warning(self, tr("no_file_selected_for_splitting"))
                return

            if not os.path.exists(self.current_file_path):
                show_error(self, tr("selected_file_not_found"))
                return

            # التحقق من مسار الحفظ
            if not hasattr(self, 'auto_save_path') or not self.auto_save_path:
                show_warning(self, tr("no_save_path_specified"))
                return

            # إشعار بدء عملية التقسيم
            file_name = os.path.basename(self.current_file_path)
            show_info(self, f"{tr('splitting_started')}: {file_name}", duration=3000)

            # تنفيذ عملية التقسيم
            success = self.operations_manager.split_file(self)

            if success:
                show_success(self, f"{tr('splitting_completed_successfully')}: {file_name}", duration=4000)
            else:
                show_error(self, tr("splitting_failed"))

        except Exception as e:
            show_error(self, f"{tr('splitting_error')}: {str(e)}")

    def on_files_changed(self, files):
        """
        إظهار أو إخفاء العناصر بناءً على عدد الملفات.
        """
        if len(files) == 1:
            # إظهار التخطيط الكامل (فريم الحفظ + زر التقسيم)
            if hasattr(self, 'save_and_split_widget'):
                self.save_and_split_widget.setVisible(True)
        else:
            # إخفاء التخطيط الكامل
            if hasattr(self, 'save_and_split_widget'):
                self.save_and_split_widget.setVisible(False)
            # مسح المسار المحفوظ
            self.current_file_path = ""
            self.auto_save_path = ""

    def get_save_path(self):
        """الحصول على مسار الحفظ المحدد"""
        return self.auto_save_path if self.auto_save_path else ""
