# -*- coding: utf-8 -*-
"""
صفحة تقسيم ملفات PDF
"""

from src.ui.widgets.base_page import BasePageWidget
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton, QWidget, QApplication
)
from PySide6.QtCore import Qt
from src.managers.theme_manager import make_theme_aware
from src.ui.widgets.svg_icon_button import create_action_button
from src.ui.widgets.icon_utils import create_colored_icon_button
from src.utils.translator import tr
import os

class SplitPage(BasePageWidget):
    """
    واجهة المستخدم الخاصة بوظيفة تقسيم ملفات PDF.
    """
    def __init__(self, file_manager, operations_manager, notification_manager, parent=None):
        """
        :param file_manager: مدير الملفات لاختيار الملف.
        :param operations_manager: مدير العمليات لتنفيذ التقسيم.
        :param notification_manager: مدير الإشعارات المركزي.
        """
        super().__init__(
            page_title=tr("split_page_title"),
            theme_key="split_page",
            notification_manager=notification_manager,
            parent=parent
        )
        
        # تفعيل السحب والإفلات
        self.setAcceptDrops(True)

        self.file_manager = file_manager
        self.operations_manager = operations_manager
        self.has_unsaved_changes = False

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
        make_theme_aware(self.save_and_split_widget, "frame")
        self.save_and_split_layout = QHBoxLayout(self.save_and_split_widget)

        # فريم مجلد الحفظ
        self.save_location_frame = QGroupBox(tr("save_folder"))
        make_theme_aware(self.save_location_frame, "group_box")
        save_layout = QVBoxLayout(self.save_location_frame)

        # تخطيط أفقي للمسار وزر التغيير
        path_layout = QHBoxLayout()

        # عرض المسار التلقائي
        self.save_location_label = QLabel(tr("auto_folder_creation"))
        make_theme_aware(self.save_location_label, "label")
        self.save_location_label.setWordWrap(True)

        # زر تغيير المجلد
        self.browse_save_btn = create_colored_icon_button("folder-open", 18, "", tr("change_folder_tooltip"))
        self.browse_save_btn.clicked.connect(self.select_save_location)

        path_layout.addWidget(self.save_location_label, 1)
        path_layout.addWidget(self.browse_save_btn)

        save_layout.addLayout(path_layout)

        # فريم زر التقسيم
        self.split_button_frame = QGroupBox(tr("execute"))
        make_theme_aware(self.split_button_frame, "group_box")
        split_layout = QVBoxLayout(self.split_button_frame)

        # زر التقسيم بأيقونة ملونة
        self.split_button = create_colored_icon_button("scissors", 24, "", tr("split_file_tooltip"))
        self.split_button.clicked.connect(self.execute_split)

        split_layout.addWidget(self.split_button)
        split_layout.addStretch()

        # إضافة الفريمين للتخطيط الأفقي
        self.save_and_split_layout.addWidget(self.save_location_frame, 2)  # يأخذ مساحة أكبر
        self.save_and_split_layout.addWidget(self.split_button_frame, 0)  # مساحة صغيرة

        # إضافة الـ widget للتخطيط الرئيسي
        self.main_layout.insertWidget(2, self.save_and_split_widget)

    def select_file_for_splitting(self):
        """
        فتح حوار لاختيار ملف PDF واحد وتحديث القائمة.
        """
        try:
            # مسح الملفات القديمة قبل إضافة الجديد
            self.reset_ui()

            file = self.file_manager.select_pdf_files(title=tr("select_pdf_to_split_title"), multiple=False)
            if file and os.path.exists(file):
                self.current_file_path = file
                self.file_list_frame.add_files([file])
                self.has_unsaved_changes = True

                # إنشاء مسار الحفظ التلقائي
                self.create_auto_save_path(file)

                # إظهار التخطيط الكامل (فريم الحفظ + زر التقسيم)
                self.save_and_split_widget.setVisible(True)

                # إشعار بنجاح تحديد الملف
                file_name = os.path.basename(file)
                self.notification_manager.show_notification(f"{tr('file_selected_for_splitting')}: {file_name}", "info", duration=3000)

            elif file:
                self.notification_manager.show_notification(f"{tr('file_not_found')}: {file}", "error")

        except Exception as e:
            self.notification_manager.show_notification(f"{tr('error_selecting_file')}: {str(e)}", "error")

    def create_auto_save_path(self, file_path):
        """إنشاء مسار الحفظ التلقائي في سطح المكتب"""
        # الحصول على اسم الملف بدون امتداد
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # الحصول على مسار سطح المكتب
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        # إنشاء اسم مجلد ذكي
        folder_name = f"{file_name}{tr('split_pages_suffix')}"

        # إنشاء مسار فريد لتجنب التضارب
        self.auto_save_path = self.get_unique_folder_path(desktop_path, folder_name)

        # تحديث النص المعروض
        self.save_location_label.setText(f"{tr('path_prefix')} {self.auto_save_path}")

    def get_unique_folder_path(self, base_path, folder_name):
        """إنشاء مسار مجلد فريد لتجنب التضارب دون إنشائه."""
        counter = 1
        original_name = folder_name

        while True:
            if counter == 1:
                new_folder_path = os.path.join(base_path, original_name)
            else:
                new_folder_path = os.path.join(base_path, f"{original_name}_{counter}")

            if not os.path.exists(new_folder_path):
                return new_folder_path

            counter += 1
            # تجنب الحلقة اللانهائية
            if counter > 100:
                return os.path.join(base_path, original_name)

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
                self.auto_save_path = self.get_unique_folder_path(directory, folder_name)
                self.save_location_label.setText(f"{tr('path_prefix')} {self.auto_save_path}")

    def _get_main_window(self):
        """الحصول على النافذة الرئيسية للتطبيق"""
        parent = self.parent()
        while parent:
            if parent.__class__.__name__ == 'ApexFlow':
                return parent
            parent = parent.parent()
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ApexFlow':
                return widget
        return None

    def execute_split(self):
        """
        تنفيذ عملية التقسيم باستخدام مدير العمليات.
        """
        try:
            # التحقق من وجود ملف للتقسيم
            if not hasattr(self, 'current_file_path') or not self.current_file_path:
                self.notification_manager.show_notification(tr("no_file_selected_for_splitting"), "warning")
                return

            if not os.path.exists(self.current_file_path):
                self.notification_manager.show_notification(tr("selected_file_not_found"), "error")
                return

            # التحقق من مسار الحفظ
            if not hasattr(self, 'auto_save_path') or not self.auto_save_path:
                self.notification_manager.show_notification(tr("no_save_path_specified"), "warning")
                return

            # إنشاء المجلد قبل بدء العملية مباشرة
            try:
                os.makedirs(self.auto_save_path, exist_ok=True)
            except Exception as e:
                self.notification_manager.show_notification(f"{tr('error_creating_folder')}: {e}", "error")
                return

            # إشعار بدء عملية التقسيم
            file_name = os.path.basename(self.current_file_path)
            self.notification_manager.show_notification(f"{tr('splitting_started')}: {file_name}", "info", duration=3000)

            # تنفيذ عملية التقسيم
            success = self.operations_manager.split_file(self)

            if success:
                self.notification_manager.show_notification(f"{tr('splitting_completed_successfully')}: {file_name}", "success", duration=4000)
                self.reset_ui()
            else:
                self.notification_manager.show_notification(tr("splitting_failed"), "error")

        except Exception as e:
            self.notification_manager.show_notification(f"{tr('splitting_error')}: {str(e)}", "error")

    def on_files_changed(self, files):
        """
        إظهار أو إخفاء العناصر بناءً على عدد الملفات.
        """
        has_file = len(files) == 1
        self.has_unsaved_changes = has_file

        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(main_window.get_page_index(self), has_file)
        
        if hasattr(self, 'save_and_split_widget'):
            self.save_and_split_widget.setVisible(has_file)
        
        if not has_file:
            # مسح المسار المحفوظ
            self.current_file_path = ""
            self.auto_save_path = ""

    def get_save_path(self):
        """الحصول على مسار الحفظ المحدد"""
        return self.auto_save_path if self.auto_save_path else ""

    def reset_ui(self):
        """إعادة تعيين الواجهة إلى حالتها الأولية."""
        self.file_list_frame.clear_all_files()
        self.current_file_path = ""
        self.auto_save_path = ""
        self.has_unsaved_changes = False
        if hasattr(self, 'save_and_split_widget'):
            self.save_and_split_widget.setVisible(False)
        self.save_location_label.setText(tr("auto_folder_creation"))
        
        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(main_window.get_page_index(self), False)

    def dragEnterEvent(self, event):
        """عند دخول ملفات مسحوبة إلى منطقة الصفحة"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """عند إفلات الملفات في منطقة الصفحة"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            files = [url.toLocalFile() for url in urls if url.isLocalFile()]
            
            if files:
                main_window = self._get_main_window()
                if main_window and hasattr(main_window, 'smart_drop_overlay'):
                    # تحديث وضع الطبقة الذكية بناءً على الصفحة الحالية
                    main_window._update_smart_drop_mode_for_page(main_window.stack.currentIndex())
                    
                    # تعيين الملفات والتحقق من صحتها
                    main_window.smart_drop_overlay.files = files
                    main_window.smart_drop_overlay.is_valid_drop = main_window.smart_drop_overlay._validate_files_for_context(files)
                    
                    # تعطيل النافذة الرئيسية بالكامل عند تفعيل واجهة الافلات
                    main_window.setEnabled(False)
                    
                    # التقاط وتطبيق تأثير البلور على الخلفية
                    main_window.smart_drop_overlay.capture_background_blur()
                    main_window.smart_drop_overlay.update_styles()
                    main_window.smart_drop_overlay.update_ui_for_context()
                    
                    # إظهار الطبقة مع تأثير انتقالي سلس
                    main_window.smart_drop_overlay.animate_show()
                    
                    # معالجة الإفلات
                    main_window.smart_drop_overlay.handle_drop(event)
                    event.acceptProposedAction()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()
            
    def add_files(self, files):
        """إضافة ملفات مباشرة إلى القائمة (للسحب والإفلات)"""
        if files:
            # صفحة التقسيم تقبل ملف واحد فقط
            file = files[0]
            if os.path.exists(file):
                self.current_file_path = file
                self.file_list_frame.add_files([file])
                self.has_unsaved_changes = True
                self.create_auto_save_path(file)
                self.save_and_split_widget.setVisible(True)
                file_name = os.path.basename(file)
                self.notification_manager.show_notification(f"{tr('file_selected_for_splitting')}: {file_name}", "info", duration=3000)
            else:
                self.notification_manager.show_notification(f"{tr('file_not_found')}: {file}", "error")

    def handle_smart_drop_action(self, action_type, files):
        """معالجة الإجراء المحدد من الطبقة الذكية"""
        if action_type == "add_to_list":
            self.add_files(files)
