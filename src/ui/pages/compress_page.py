# -*- coding: utf-8 -*-
"""
صفحة ضغط ملفات PDF
"""

from src.ui.widgets.base_page import BasePageWidget
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QSlider, QLabel, QCheckBox, QWidget,
    QGroupBox, QFormLayout, QPushButton, QComboBox, QProgressBar, QApplication
)
from PySide6.QtCore import Qt
from src.managers.theme_manager import make_theme_aware
from src.ui.widgets.svg_icon_button import create_action_button
from src.ui.widgets.icon_utils import create_colored_icon_button
from src.utils.translator import tr
import os

class CompressPage(BasePageWidget):
    """
    واجهة المستخدم الخاصة بوظيفة ضغط ملفات PDF.
    """
    def __init__(self, file_manager, operations_manager, notification_manager, parent=None):
        super().__init__(
            page_title=tr("compress_page_title"),
            theme_key="compress_page",
            notification_manager=notification_manager,
            parent=parent
        )

        # تفعيل السحب والإفلات
        self.setAcceptDrops(True)

        self.file_manager = file_manager
        self.operations_manager = operations_manager
        self.selected_files = []
        self.has_unsaved_changes = False

        self.add_file_button = self.add_top_button(
            text=tr("add_file"),
            on_click=self.add_file
        )
        self.add_folder_button = self.add_top_button(
            text=tr("add_folder"),
            on_click=self.add_folder
        )

        # Create a container for all options
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout(self.options_container)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.insertWidget(2, self.options_container)

        self.create_batch_options()

        self.hide_all_frames()
        self.update_page_drop_settings()

    def update_page_drop_settings(self):
        """Sets the drag-and-drop settings for this page."""
        main_window = self._get_main_window()
        if main_window and hasattr(main_window, 'smart_drop_overlay'):
            from src.utils.page_settings import page_settings
            compress_settings = page_settings.get('compress', {})
            compress_settings['allow_folders'] = True
            compress_settings['allow_multiple_files'] = True
            main_window.smart_drop_overlay.update_page_settings(compress_settings)

    def create_batch_options(self):
        self.batch_options_widget = QWidget()
        self.batch_horizontal_layout = QHBoxLayout(self.batch_options_widget)

        self.batch_save_frame = QGroupBox(tr("save_folder"))
        make_theme_aware(self.batch_save_frame, "group_box")
        batch_save_layout = QVBoxLayout(self.batch_save_frame)
        
        batch_path_layout = QHBoxLayout()
        self.batch_save_label = QLabel(tr("new_folder_will_be_created"))
        make_theme_aware(self.batch_save_label, "label")
        self.batch_save_label.setWordWrap(True)
        
        self.batch_browse_btn = create_colored_icon_button("folder-open", 18, "", tr("change_folder_tooltip"))
        self.batch_browse_btn.clicked.connect(self.select_batch_save_location)
        
        batch_path_layout.addWidget(self.batch_save_label, 1)
        batch_path_layout.addWidget(self.batch_browse_btn)
        batch_save_layout.addLayout(batch_path_layout)

        self.batch_options_frame = QGroupBox(tr("compression_options"))
        make_theme_aware(self.batch_options_frame, "group_box")
        batch_layout = QFormLayout(self.batch_options_frame)
        self.batch_compression_combo = QComboBox()
        self.batch_compression_combo.addItems([tr("light_compression"), tr("medium_compression"), tr("high_compression"), tr("max_compression")])
        self.batch_compression_combo.setCurrentIndex(1)
        make_theme_aware(self.batch_compression_combo, "combo")
        compression_label = QLabel(tr("compression_level"))
        compression_label.setStyleSheet("background: transparent;")
        batch_layout.addRow(compression_label, self.batch_compression_combo)

        self.batch_button_frame = QGroupBox(tr("execute"))
        make_theme_aware(self.batch_button_frame, "group_box")
        button_layout = QVBoxLayout(self.batch_button_frame)
        self.batch_compress_button = create_colored_icon_button("play", 18, "", tr("execute_compression_tooltip"))
        self.batch_compress_button.clicked.connect(self.execute_compress)
        button_layout.addWidget(self.batch_compress_button)
        button_layout.addStretch()

        self.batch_horizontal_layout.addWidget(self.batch_save_frame, 2)
        self.batch_horizontal_layout.addWidget(self.batch_options_frame, 1)
        self.batch_horizontal_layout.addWidget(self.batch_button_frame, 1)
        self.options_layout.addWidget(self.batch_options_widget)

    def hide_all_frames(self):
        self.options_container.hide()

    def show_ui_for_files(self):
        """Show the appropriate UI elements when files are present."""
        self.options_container.show()
        self.batch_options_widget.show()
        self.file_list_frame.show()

    def add_file(self):
        """Add a single file for compression."""
        files = self.file_manager.select_pdf_files(title=tr("select_pdf_to_compress"), multiple=True)
        if files:
            self.add_files(files)

    def add_folder(self):
        """Add all PDF files from a folder for compression."""
        folder_path = self.file_manager.select_directory(title=tr("select_folder_to_compress"))
        if folder_path:
            pdf_files = self.file_manager.get_pdf_files_from_folder(folder_path)
            if pdf_files:
                self.add_files(pdf_files)
            else:
                self.notification_manager.show_notification(tr("no_pdf_files_in_folder"), "warning")

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

    def on_files_changed(self, files):
        self.has_unsaved_changes = bool(files)
        
        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(main_window.get_page_index(self), self.has_unsaved_changes)
        
        if not files:
            self.hide_all_frames()
            self.selected_files = []
        else:
            self.selected_files = files
            self.show_ui_for_files()

    def select_batch_save_location(self):
        """Opens a dialog to select a save directory for batch processing."""
        directory = self.file_manager.select_directory(tr("select_batch_save_folder"))
        if directory:
            self.batch_save_label.setText(f"{tr('path_prefix')} {directory}")

    def get_save_path(self):
        """Extracts the save path from the batch_save_label."""
        full_text = self.batch_save_label.text()
        prefix = tr('path_prefix') + " "
        if full_text.startswith(prefix):
            return full_text[len(prefix):]
        
        if self.selected_files:
            base_dir = os.path.dirname(self.selected_files[0])
            return self.create_unique_folder(base_dir, tr("compressed_files"))
        return None

    def create_unique_folder(self, base_dir, folder_name):
        """Creates a unique folder name to avoid overwriting."""
        path = os.path.join(base_dir, folder_name)
        count = 1
        while os.path.exists(path):
            path = os.path.join(base_dir, f"{folder_name}_{count}")
            count += 1
        return path

    def get_batch_compression_level(self):
        """Maps combo box text to a compression level 1-5."""
        mapping = {
            tr("light_compression"): 2,
            tr("medium_compression"): 3,
            tr("high_compression"): 4,
            tr("max_compression"): 5
        }
        return mapping.get(self.batch_compression_combo.currentText(), 3)


    def execute_compress(self):
        """Initiates the compression process via the OperationsManager."""
        try:
            # The manager will handle everything: getting files, paths, levels, and showing messages.
            self.operations_manager.compress_files(self)
            # Assuming success, reset the UI. A better implementation would be for compress_files to return a status.
            self.reset_ui()
        except Exception as e:
            self.notification_manager.show_notification(f"{tr('compression_error')}: {str(e)}", "error")

    def reset_ui(self):
        """إعادة تعيين واجهة المستخدم إلى حالتها الأولية."""
        # مسح قائمة الملفات وإعادة تعيين الحالة
        self.file_list_frame.clear_all_files()
        self.has_unsaved_changes = False
        self.selected_files = []

        # إخفاء جميع الإطارات والخيارات
        self.hide_all_frames()

        # إعادة تعيين تسميات مسار الحفظ
        self.batch_save_label.setText(tr("new_folder_will_be_created"))

        # تحديث حالة العمل في النافذة الرئيسية
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
                    # تمرير الملفات إلى الطبقة الذكية في النافذة الرئيسية
                    main_window.smart_drop_overlay.dropEvent(event)
                    event.acceptProposedAction()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    def add_files(self, files):
        """إضافة ملفات مباشرة إلى القائمة (للسحب والإفلات)"""
        if not files: return

        # Add new files to the existing list, avoiding duplicates
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
        
        self.has_unsaved_changes = True

        self.file_list_frame.clear_all_files()
        self.file_list_frame.add_files(self.selected_files)
        
        if self.selected_files:
            base_dir = os.path.dirname(self.selected_files[0])
            new_folder = self.create_unique_folder(base_dir, tr("compressed_files"))
            self.batch_save_label.setText(f"{tr('path_prefix')} {new_folder}")
        
        self.notification_manager.show_notification(f"{tr('files_selected_for_batch_compression')} ({len(self.selected_files)} ملف)", "info", duration=3000)

        self.on_files_changed(self.selected_files)

    def handle_smart_drop_action(self, action_type, files):
        """معالجة الإجراء المحدد من الطبقة الذكية"""
        if action_type == "add_to_list":
            self.add_files(files)
