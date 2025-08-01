# -*- coding: utf-8 -*-
"""
صفحة تحويل الملفات - تصميم جديد يعتمد على سير عمل مبسط ومظهر التبويبات
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QGroupBox
from .base_page import BasePageWidget
from .ui_helpers import create_button, create_title
from modules.translator import tr, register_language_change_callback, get_current_language

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
        # إخفاء الفريمات بعد إنشائها
        self.reset_ui()

        # تسجيل callback لتغيير اللغة
        register_language_change_callback(self.update_button_order_for_language)

    def create_header_layout(self):
        """إنشاء التخطيط العلوي الذي يحتوي على العنوان وتبويبات العمليات."""
        # حاوية رأسية لتنظيم العنوان والأزرار
        header_area_layout = QVBoxLayout()
        header_area_layout.setContentsMargins(0, 0, 0, 0)
        header_area_layout.setSpacing(5) # مسافة صغيرة بين العنوان والأزرار

        # تخطيط موحد للعنوان والأزرار مع مراعاة اتجاه اللغة
        header_content_layout = QHBoxLayout()
        header_content_layout.setSpacing(20)

        # العنوان
        self.title_label = create_title(tr("convert_files_title"))

        # تخطيط الأزرار
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(0)  # المسافة بين الأزرار 0

        # أزرار التحويل (التبويبات)
        self.convert_options = {
            "pdf_to_images": tr("pdf_to_images"),
            "images_to_pdf": tr("images_to_pdf"),
            "pdf_to_text": tr("pdf_to_text"),
            "text_to_pdf": tr("text_to_pdf"),
        }

        # حاوية للأزرار والمؤشر
        buttons_container = QWidget()
        buttons_container_layout = QVBoxLayout(buttons_container)
        buttons_container_layout.setContentsMargins(0, 0, 0, 0)
        buttons_container_layout.setSpacing(0)

        # تخطيط الأزرار
        buttons_widget = QWidget()
        buttons_widget_layout = QHBoxLayout(buttons_widget)
        buttons_widget_layout.setContentsMargins(0, 0, 0, 0)
        buttons_widget_layout.setSpacing(0)

        for key, text in self.convert_options.items():
            button = QPushButton(text)
            button.setObjectName(key)
            button.setCheckable(True)
            button.clicked.connect(self.on_tab_selected)
            button.setProperty("class", "tab-button")

            # استخدام نظام السمات الموحد
            from .theme_manager import apply_theme
            apply_theme(button, "tab_button")

            self.top_buttons[key] = button
            buttons_widget_layout.addWidget(button)

        # مؤشر الانزلاق المحسن
        from PySide6.QtWidgets import QFrame
        self.slider_indicator = QFrame()
        from .theme_manager import apply_theme
        apply_theme(self.slider_indicator, "slider_indicator")
        self.slider_indicator.setFixedHeight(3)

        buttons_container_layout.addWidget(buttons_widget)
        buttons_container_layout.addWidget(self.slider_indicator)

        buttons_layout.addWidget(buttons_container)
        
        # ترتيب العنوان والأزرار حسب اتجاه اللغة
        from modules.translator import get_current_language
        current_lang = get_current_language()

        if current_lang == "ar":  # العربية: العنوان يمين، الأزرار يسار
            header_content_layout.addLayout(buttons_layout)
            header_content_layout.addStretch()
            header_content_layout.addWidget(self.title_label)
        else:  # الإنجليزية: العنوان يسار، الأزرار يمين
            header_content_layout.addWidget(self.title_label)
            header_content_layout.addStretch()
            header_content_layout.addLayout(buttons_layout)

        header_area_layout.addLayout(header_content_layout)

        # أزرار التحكم بالعملية
        self.controls_layout = QHBoxLayout()

        self.add_files_btn = create_button(tr("add_files_convert"), on_click=self.select_files)
        self.cancel_btn = create_button(tr("cancel_operation"), on_click=self.reset_ui)
        self.cancel_btn.setProperty("class", "cancel-button")

        # إخفاء الأزرار افتراضياً
        self.add_files_btn.hide()
        self.cancel_btn.hide()

        # ترتيب الأزرار حسب اتجاه اللغة
        current_lang = get_current_language()

        # تنظيف التخطيط أولاً لتجنب التكرار
        while self.controls_layout.count():
            child = self.controls_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # ترتيب الأزرار حسب اللغة
        if current_lang == "ar":  # العربية RTL: إلغاء ← إضافة ملفات
            self.controls_layout.addWidget(self.cancel_btn)
            self.controls_layout.addWidget(self.add_files_btn)
            self.controls_layout.setAlignment(Qt.AlignRight)
        else:  # الإنجليزية LTR: إضافة ملفات ← إلغاء
            self.controls_layout.addWidget(self.add_files_btn)
            self.controls_layout.addWidget(self.cancel_btn)
            self.controls_layout.setAlignment(Qt.AlignLeft)
        header_area_layout.addLayout(self.controls_layout)

        self.main_layout.insertLayout(0, header_area_layout)

    def update_button_order_for_language(self):
        """إعادة ترتيب الأزرار عند تغيير اللغة"""
        current_lang = get_current_language()

        # تنظيف التخطيط
        while self.controls_layout.count():
            child = self.controls_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # إعادة ترتيب الأزرار حسب اللغة
        if current_lang == "ar":  # العربية RTL: إلغاء ← إضافة ملفات
            self.controls_layout.addWidget(self.cancel_btn)
            self.controls_layout.addWidget(self.add_files_btn)
            self.controls_layout.setAlignment(Qt.AlignRight)
        else:  # الإنجليزية LTR: إضافة ملفات ← إلغاء
            self.controls_layout.addWidget(self.add_files_btn)
            self.controls_layout.addWidget(self.cancel_btn)
            self.controls_layout.setAlignment(Qt.AlignLeft)

    def create_workspace_area(self):
        """إنشاء منطقة العمل التي تظهر تحت التبويبات."""
        self.workspace_widget = QWidget()
        workspace_layout = QVBoxLayout(self.workspace_widget)
        workspace_layout.setContentsMargins(0, 15, 0, 0)
        workspace_layout.setSpacing(10)

        # منطقة عرض الملفات
        workspace_layout.addWidget(self.file_list_frame)
        self.file_list_frame.clear_button_clicked.connect(self.reset_ui)
        self.file_list_frame.files_changed.connect(self.update_controls_visibility)

        # إضافة المسار وزر التنفيذ
        self.create_path_and_execute_section(workspace_layout)

        self.main_layout.addWidget(self.workspace_widget)

        # إخفاء منطقة العمل افتراضياً
        self.workspace_widget.hide()

    def create_path_and_execute_section(self, parent_layout):
        """إنشاء قسم المسار وزر التنفيذ مع فريمات منفصلة"""
        from PySide6.QtWidgets import QLabel, QHBoxLayout, QGroupBox, QVBoxLayout
        from .svg_icon_button import create_action_button
        from .theme_manager import make_theme_aware

        # تخطيط أفقي للفريمين
        frames_layout = QHBoxLayout()

        # فريم المسار
        self.save_path_frame = QGroupBox(tr("save_path_frame_title"))
        make_theme_aware(self.save_path_frame, "group_box")
        path_layout = QVBoxLayout(self.save_path_frame)

        self.save_path_label = QLabel(tr("path_not_selected"))
        self.save_path_label.setWordWrap(True)
        self.save_path_label.setMinimumHeight(30)
        make_theme_aware(self.save_path_label, "label")
        path_layout.addWidget(self.save_path_label)

        # فريم التنفيذ
        self.execute_frame = QGroupBox(tr("execute_frame_title"))
        make_theme_aware(self.execute_frame, "group_box")
        execute_layout = QVBoxLayout(self.execute_frame)

        self.execute_btn = create_action_button("play", 24, tr("execute"))
        self.execute_btn.clicked.connect(self.execute_conversion)
        self.execute_btn.setMinimumHeight(40)
        execute_layout.addWidget(self.execute_btn)
        execute_layout.addStretch()

        # إضافة الفريمين للتخطيط
        frames_layout.addWidget(self.save_path_frame, 2)  # فريم المسار أكبر
        frames_layout.addWidget(self.execute_frame, 0)    # فريم التنفيذ أصغر

        parent_layout.addLayout(frames_layout)

        # إخفاء الفريمين افتراضياً
        self.save_path_frame.hide()
        self.execute_frame.hide()



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

        # تغيير نص زر الإضافة حسب نوع العملية
        button_texts = {
            "pdf_to_images": tr("add_pdf_files"),
            "images_to_pdf": tr("add_images"),
            "pdf_to_text": tr("add_pdf_files"),
            "text_to_pdf": tr("add_text_files")
        }
        new_text = button_texts.get(self.active_operation, "إضافة ملفات")
        self.add_files_btn.setText(new_text)

        self.workspace_widget.show()
        self.add_files_btn.show()
        self.cancel_btn.show()

        # عند تغيير العملية: مسح الملفات وإخفاء جميع الفريمات
        if hasattr(self, 'file_list_frame') and self.file_list_frame.get_files():
            self.file_list_frame.clear_all_files()

        # إخفاء الفريمات الثلاثة دائماً عند تغيير العملية
        self.file_list_frame.hide()
        if hasattr(self, 'save_path_frame'):
            self.save_path_frame.hide()
        if hasattr(self, 'execute_frame'):
            self.execute_frame.hide()

        self.update_slider_position()

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
        # تحديث المسار عند إضافة ملفات
        if files:
            self.update_save_path(files[0])

    def update_save_path(self, file_path):
        """تحديث مسار الحفظ بناءً على الملف المحدد"""
        import os
        base_dir = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, _ = os.path.splitext(filename)

        # تحديد امتداد الملف الناتج حسب العملية
        if self.active_operation == "pdf_to_images":
            save_path = os.path.join(base_dir, f"{name}_صور")
        elif self.active_operation == "images_to_pdf":
            save_path = os.path.join(base_dir, f"{name}_محول.pdf")
        elif self.active_operation == "pdf_to_text":
            save_path = os.path.join(base_dir, f"{name}_نص.txt")
        elif self.active_operation == "text_to_pdf":
            save_path = os.path.join(base_dir, f"{name}_محول.pdf")
        else:
            save_path = os.path.join(base_dir, f"{name}_محول")

        self.save_path_label.setText(f"{tr('save_path_prefix')} {save_path}")

    def execute_conversion(self):
        """تنفيذ عملية التحويل"""
        from .notification_system import show_info, show_success, show_error, show_warning

        try:
            files = self.file_list_frame.get_valid_files()
            if not files:
                show_warning(self, tr("no_files_for_conversion"))
                return

            if not self.active_operation:
                show_warning(self, tr("no_conversion_operation_selected"))
                return

            # الحصول على مسار الحفظ
            save_path = self.save_path_label.text().replace("مسار الحفظ: ", "")

            show_info(self, f"{tr('converting_files_notification')} ({len(files)} ملف)", duration=2000)

            # هنا يمكن إضافة منطق التحويل الفعلي لاحقاً
            # success = self.operations_manager.convert_files(files, save_path, self.active_operation)

            # للاختبار - نفترض النجاح
            show_success(self, f"{tr('conversion_completed_notification')} ({len(files)} ملف)", duration=3000)

        except Exception as e:
            show_error(self, f"{tr('conversion_error_occurred')}: {str(e)}")





    def reset_ui(self):
        # إخفاء جميع العناصر عند التنقل بين التبويبات
        self.workspace_widget.hide()
        self.add_files_btn.hide()
        self.cancel_btn.hide()

        # إخفاء فريمات المسار والتنفيذ
        if hasattr(self, 'save_path_frame'):
            self.save_path_frame.hide()
        if hasattr(self, 'execute_frame'):
            self.execute_frame.hide()

        # مسح العملية النشطة أولاً
        self.active_operation = None

        # مسح الملفات
        if self.file_list_frame.get_files():
            self.file_list_frame.clear_all_files()

        # إلغاء تحديد جميع الأزرار
        for button in self.top_buttons.values():
            button.setChecked(False)

        # إعادة تعيين نص زر الإضافة
        self.add_files_btn.setText(tr("add_files_convert"))

        # لا نستدعي update_controls_visibility هنا لأننا نريد إخفاء كل شيء



    def clear_files(self):
        self.reset_ui()
        super().clear_files()

    def update_controls_visibility(self, files):
        """إظهار/إخفاء العناصر بناءً على وجود الملفات"""
        has_files = bool(files) and len(files) > 0

        # إظهار/إخفاء الفريمات الثلاثة
        self.file_list_frame.setVisible(has_files)

        if hasattr(self, 'save_path_frame'):
            self.save_path_frame.setVisible(has_files)
        if hasattr(self, 'execute_frame'):
            self.execute_frame.setVisible(has_files)

    def update_slider_position(self):
        """تحديث موضع مؤشر الانزلاق المحسن"""
        from PySide6.QtCore import QTimer
        if hasattr(self, 'slider_indicator') and self.top_buttons and self.active_operation:
            if self.active_operation in self.top_buttons:
                btn = self.top_buttons[self.active_operation]
                # تأخير التحديث للتأكد من أن الأزرار تم رسمها
                QTimer.singleShot(50, lambda: self.slider_indicator.setGeometry(
                    btn.x(), btn.y() + btn.height() - 3,
                    btn.width(), 3
                ))
