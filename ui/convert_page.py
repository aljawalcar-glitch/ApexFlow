# -*- coding: utf-8 -*-
"""
صفحة تحويل الملفات - تصميم جديد يعتمد على سير عمل مبسط ومظهر التبويبات
"""

import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QWidget
from .base_page import BasePageWidget
from .svg_icon_button import create_action_button
from .theme_manager import make_theme_aware
from .ui_helpers import create_button, create_title
from modules.translator import tr

class ConvertPage(BasePageWidget):
    """
    واجهة المستخدم الخاصة بوظائف التحويل المختلفة.
    """
    def __init__(self, file_manager, operations_manager, parent=None):
        # استدعاء المُنشئ الأصلي بدون عنوان مبدئيًا
        super().__init__(page_title="", theme_key="convert_page", parent=parent)
        
        self.file_manager = file_manager
        self.operations_manager = operations_manager
        self.active_operation = None

        # إزالة التخطيطات الافتراضية من BasePageWidget
        if hasattr(self, 'title_layout'):
            self.main_layout.removeItem(self.title_layout)
            self.title_layout.setParent(None)
        if hasattr(self, 'top_buttons_layout') and self.top_buttons_layout:
            self.main_layout.removeItem(self.top_buttons_layout)
            self.top_buttons_layout.setParent(None)

        self.top_buttons = {}
        self.create_header_layout()
        self.create_workspace_area()
        
        self.apply_styles()
        self.reset_ui()

    def create_header_layout(self):
        """إنشاء التخطيط العلوي الذي يحتوي على العنوان وتبويبات العمليات."""
        # حاوية رأسية لتنظيم العنوان والأزرار
        header_area_layout = QVBoxLayout()
        header_area_layout.setContentsMargins(0, 0, 0, 0)
        header_area_layout.setSpacing(5) # مسافة صغيرة بين العنوان والأزرار

        # العنوان
        self.title_label = create_title(tr("convert_files_title"))
        # تأكد من أن العنوان يمتد بعرض النافذة
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        header_area_layout.addLayout(title_layout)

        # تخطيط أفقي للأزرار لوضعها على اليمين
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(0)  # المسافة بين الأزرار 0
        buttons_layout.addStretch()   # لدفع الأزرار إلى أقصى اليمين

        # أزرار التحويل (التبويبات)
        self.convert_options = {
            "pdf_to_images": tr("pdf_to_images"),
            "images_to_pdf": tr("images_to_pdf"),
            "pdf_to_text": tr("pdf_to_text"),
            "text_to_pdf": tr("text_to_pdf"),
        }

        for key, text in self.convert_options.items():
            button = QPushButton(text)
            button.setObjectName(key)
            button.setCheckable(True)
            button.clicked.connect(self.on_tab_selected)
            button.setProperty("class", "tab-button")
            # تطبيق النمط الخاص هنا
            button.setStyleSheet(self.get_special_button_style())
            self.top_buttons[key] = button
            buttons_layout.addWidget(button)
        
        header_area_layout.addLayout(buttons_layout)

        # أزرار التحكم بالعملية
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setAlignment(Qt.AlignRight)
        self.add_files_btn = create_button(tr("add_files_convert"), on_click=self.select_files)
        self.cancel_btn = create_button(tr("cancel_operation"), on_click=self.reset_ui)
        self.cancel_btn.setProperty("class", "cancel-button")

        self.controls_layout.addWidget(self.add_files_btn)
        self.controls_layout.addWidget(self.cancel_btn)
        header_area_layout.addLayout(self.controls_layout)

        self.main_layout.insertLayout(0, header_area_layout)

    def create_workspace_area(self):
        """إنشاء منطقة العمل التي تظهر تحت التبويبات."""
        self.workspace_widget = QWidget()
        workspace_layout = QVBoxLayout(self.workspace_widget)
        workspace_layout.setContentsMargins(0, 15, 0, 0)
        workspace_layout.setSpacing(10)

        # منطقة عرض الملفات والحفظ
        workspace_layout.addWidget(self.file_list_frame)
        self.file_list_frame.clear_button_clicked.connect(self.reset_ui)
        self.file_list_frame.files_changed.connect(self.update_controls_visibility)
        self.create_save_location_frame(workspace_layout)

        self.main_layout.addWidget(self.workspace_widget)

    def create_save_location_frame(self, parent_layout):
        self.save_and_process_layout = QHBoxLayout()
        self.save_location_frame = QGroupBox(tr("save_folder"))
        make_theme_aware(self.save_location_frame, "group_box")
        save_layout = QVBoxLayout(self.save_location_frame)
        path_layout = QHBoxLayout()
        self.save_location_label = QLabel(tr("path_not_selected"))
        make_theme_aware(self.save_location_label, "label")
        self.save_location_label.setWordWrap(True)
        self.browse_save_btn = create_action_button("folder-open", 24, tr("change_folder"))
        self.browse_save_btn.clicked.connect(self.select_save_location)
        path_layout.addWidget(self.save_location_label, 1)
        path_layout.addWidget(self.browse_save_btn)
        save_layout.addLayout(path_layout)
        self.process_frame = QGroupBox(tr("execute"))
        make_theme_aware(self.process_frame, "group_box")
        process_layout = QVBoxLayout(self.process_frame)
        self.process_button = create_action_button("play", 24, tr("start_processing"))
        self.process_button.clicked.connect(self.execute_conversion)
        process_layout.addWidget(self.process_button)
        process_layout.addStretch()
        self.save_and_process_layout.addWidget(self.save_location_frame, 2)
        self.save_and_process_layout.addWidget(self.process_frame, 0)
        parent_layout.addLayout(self.save_and_process_layout)

    def get_special_button_style(self, color_rgb="13, 110, 253", checked_color_rgb="255, 111, 0"):
        """Generate a special button style with a given color."""
        from .theme_manager import global_theme_manager
        colors = global_theme_manager.get_current_colors()
        text_color = colors.get('text_body', '#ffffff')

        return f"""
            QPushButton {{
                background: rgba({color_rgb}, 0.2);
                border: 1px solid rgba({color_rgb}, 0.4);
                border-radius: 8px;
                color: {text_color};
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background: rgba({color_rgb}, 0.3);
                border: 1px solid rgba({color_rgb}, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba({color_rgb}, 0.1);
            }}
            QPushButton:checked {{
                background: rgba({checked_color_rgb}, 0.8);
                border: 1px solid rgba({checked_color_rgb}, 1);
            }}
        """

    def apply_styles(self):
        """تطبيق الأنماط المخصصة للأزرار التي تعمل كتبويبات."""
        # تطبيق النمط الخاص على الأزرار
        special_style = self.get_special_button_style()
        self.add_files_btn.setStyleSheet(special_style)
        self.cancel_btn.setStyleSheet(self.get_special_button_style("220, 53, 69")) # لون أحمر للإلغاء

        # لا حاجة لـ setStyleSheet هنا بعد الآن
        # تم تطبيق الأنماط مباشرة على الأزرار

    def on_tab_selected(self):
        sender = self.sender()
        if not sender.isChecked():
            sender.setChecked(True)
            return

        self.active_operation = sender.objectName()
        
        for button in self.top_buttons.values():
            if button != sender:
                button.setChecked(False)
        
        self.workspace_widget.show()
        self.add_files_btn.show()
        self.cancel_btn.show()
        self.update_controls_visibility([])

    def select_files(self):
        if not self.active_operation: return
        file_filters = {
            "pdf_to_images": tr("pdf_files_filter"),
            "images_to_pdf": tr("image_files_filter"),
            "pdf_to_text": tr("pdf_files_filter"),
            "text_to_pdf": tr("text_files_filter"),
        }
        multiple = self.active_operation == "images_to_pdf"
        title = self.convert_options.get(self.active_operation, "")
        files = self.file_manager.select_file(title, file_filters.get(self.active_operation, tr("all_files_filter")), multiple=multiple)
        if not files: return
        if not isinstance(files, list): files = [files]
        self.on_files_added(files)

    def on_files_added(self, files):
        self.file_list_frame.add_files(files)
        current_files = self.file_list_frame.get_files()
        if current_files:
            self.update_save_path(current_files[0])

    def select_save_location(self):
        files = self.file_list_frame.get_valid_files()
        if not files: return
        directory = self.file_manager.select_directory(tr("select_save_folder"))
        if directory:
            self.update_save_path(files[0], directory)

    def update_save_path(self, file_path, base_dir=None):
        if not base_dir: base_dir = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, _ = os.path.splitext(filename)
        output_ext_map = {
            "pdf_to_images": "", "images_to_pdf": ".pdf",
            "pdf_to_text": ".txt", "text_to_pdf": ".pdf",
        }
        ext = output_ext_map.get(self.active_operation, "")
        if self.active_operation == "pdf_to_images":
            new_path = self.create_unique_folder(base_dir, f"{name}{tr('images_folder_suffix')}")
        else:
            new_filename = f"{name}{tr('converted_suffix')}{ext}"
            new_path = os.path.join(base_dir, new_filename)
        self.save_location_label.setText(f"{tr('path_prefix')} {new_path}")

    def create_unique_folder(self, base_dir, folder_name):
        path = os.path.join(base_dir, folder_name)
        count = 1
        while os.path.exists(path):
            path = os.path.join(base_dir, f"{folder_name}_{count}")
            count += 1
        return path

    def execute_conversion(self):
        files = self.file_list_frame.get_valid_files()
        if not self.active_operation or not files: return
        save_path = self.save_location_label.text().replace(f"{tr('path_prefix')} ", "")
        operation_func_map = {
            "pdf_to_images": self.operations_manager.pdf_to_images,
            "images_to_pdf": self.operations_manager.images_to_pdf,
            "pdf_to_text": self.operations_manager.pdf_to_text,
            "text_to_pdf": self.operations_manager.text_to_pdf,
        }
        func = operation_func_map.get(self.active_operation)
        if func:
            success = func(files, save_path)
            if success: self.reset_ui()

    def reset_ui(self):
        self.workspace_widget.hide()
        self.add_files_btn.hide()
        self.cancel_btn.hide()

        if self.file_list_frame.get_files():
            self.file_list_frame.clear_all_files()
        
        self.active_operation = None
        for button in self.top_buttons.values():
            button.setChecked(False)
        
        self.update_controls_visibility([])
            
    def clear_files(self):
        self.reset_ui()
        super().clear_files()

    def update_controls_visibility(self, files):
        """Show/hide controls based on whether there are files."""
        has_files = bool(files)
        self.save_location_frame.setVisible(has_files)
        self.process_frame.setVisible(has_files)
