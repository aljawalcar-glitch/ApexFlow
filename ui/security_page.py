# -*- coding: utf-8 -*-

"""
صفحة حماية وخصائص ملفات PDF
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QFormLayout, QCheckBox, QFileDialog, QScrollArea, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from .base_page import BasePageWidget as BasePage
from .ui_helpers import create_section_label, create_info_label, create_button
from .global_styles import get_scroll_style
from modules.logger import info, error
from modules.app_utils import get_icon_path
from modules.translator import tr
import os

class SecurityPage(BasePage):
    def __init__(self, file_manager, operations_manager, notification_manager):
        super().__init__(
            page_title=tr("security_page_title"),
            theme_key="security_page",
            notification_manager=notification_manager
        )
        self.file_manager = file_manager
        self.operations_manager = operations_manager
        self.source_file = None
        self.init_ui()

    def init_ui(self):
        """إنشاء واجهة المستخدم للصفحة"""
        # إزالة الاعتماد على file_list_frame من BasePage
        if self.file_list_frame:
            self.main_layout.removeWidget(self.file_list_frame)
            self.file_list_frame.deleteLater()
            self.file_list_frame = None

        # إنشاء منطقة التمرير مباشرة بعد عنوان الصفحة
        scroll_area = QScrollArea()
        from .theme_manager import global_theme_manager
        colors = global_theme_manager.get_current_colors()
        accent_color = global_theme_manager.current_accent
        scroll_area.setStyleSheet(get_scroll_style(colors, accent_color))
        # تسجيل منطقة التمرير في مدير الثيمات العالمي
        global_theme_manager.register_widget(scroll_area, "graphics_view")

        # 1. قسم اختيار الملف داخل المحتوى
        file_selection_layout = QHBoxLayout()
        self.select_file_button = create_button(tr("select_pdf_file"), on_click=self.select_file)
        self.file_label = QLabel(tr("no_file_selected"))
        self.file_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # تطبيق نمط الثيمة على تسمية الملف
        from .theme_manager import apply_theme_style
        apply_theme_style(self.file_label, "label")
        file_selection_layout.addWidget(self.select_file_button)
        file_selection_layout.addWidget(self.file_label, 1)
        scroll_area.setWidgetResizable(True)  # السماح بتغيير حجم المحتوى
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # إنشاء حاوية للمحتوى
        scroll_content = QWidget()
        # تطبيق نمط الثيمة على محتوى التمرير
        apply_theme_style(scroll_content, "dialog", auto_register=True)
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)

        # إضافة قسم اختيار الملف إلى المحتوى
        content_layout.addLayout(file_selection_layout)

        # 2. قسم إدارة كلمة المرور
        password_container = QWidget()
        # تطبيق نمط الثيمة على الحاوية
        apply_theme_style(password_container, "frame")
        password_layout = QGridLayout(password_container)
        password_layout.setSpacing(15)
        password_layout.addWidget(create_section_label(tr("password_management")), 0, 0, 1, 2)

        # حقل كلمة مرور المستخدم
        user_password_label = QLabel(tr("user_password"))
        # تطبيق نمط الثيمة على التسمية
        from .theme_manager import apply_theme_style
        apply_theme_style(user_password_label, "label")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(tr("password_placeholder"))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        # تطبيق نمط الثيمة على حقل الإدخال
        apply_theme_style(self.password_input, "text_edit")

        password_layout.addWidget(user_password_label, 1, 0)
        password_layout.addWidget(self.password_input, 2, 0)

        # حقل كلمة مرور المالك
        owner_password_label = QLabel(tr("owner_password"))
        # تطبيق نمط الثيمة على التسمية
        apply_theme_style(owner_password_label, "label")

        self.owner_password_input = QLineEdit()
        self.owner_password_input.setPlaceholderText(tr("owner_password_placeholder"))
        self.owner_password_input.setEchoMode(QLineEdit.Password)
        self.owner_password_input.setMinimumHeight(35)
        # تطبيق نمط الثيمة على حقل الإدخال
        apply_theme_style(self.owner_password_input, "text_edit")

        password_layout.addWidget(owner_password_label, 1, 1)
        password_layout.addWidget(self.owner_password_input, 2, 1)
        
        permissions_label = QLabel(tr("permissions_label"))
        # تطبيق نمط الثيمة على التسمية
        apply_theme_style(permissions_label, "label")

        self.allow_printing_cb = QCheckBox(tr("allow_printing"))
        self.allow_printing_cb.setChecked(True)
        # تطبيق نمط الثيمة على مربع الاختيار
        apply_theme_style(self.allow_printing_cb, "checkbox")

        self.allow_copying_cb = QCheckBox(tr("allow_copying"))
        self.allow_copying_cb.setChecked(True)
        # تطبيق نمط الثيمة على مربع الاختيار
        apply_theme_style(self.allow_copying_cb, "checkbox")

        password_layout.addWidget(permissions_label, 3, 0)
        password_layout.addWidget(self.allow_printing_cb, 3, 1)
        password_layout.addWidget(self.allow_copying_cb, 4, 1)
        
        content_layout.addWidget(password_container)

        # 3. قسم خصائص الملف (Metadata)
        properties_container = QWidget()
        # تطبيق نمط الثيمة على الحاوية
        apply_theme_style(properties_container, "frame")
        properties_layout = QGridLayout(properties_container)
        properties_layout.setSpacing(15)
        properties_layout.addWidget(create_section_label(tr("metadata_section")), 0, 0, 1, 2)

        # Title and Author
        title_label = QLabel(tr("title_label"))
        apply_theme_style(title_label, "label")
        self.title_input = QLineEdit()
        self.title_input.setMinimumHeight(35)
        apply_theme_style(self.title_input, "text_edit")
        properties_layout.addWidget(title_label, 1, 0)
        properties_layout.addWidget(self.title_input, 2, 0)

        author_label = QLabel(tr("author_field_label"))
        apply_theme_style(author_label, "label")
        self.author_input = QLineEdit()
        self.author_input.setMinimumHeight(35)
        apply_theme_style(self.author_input, "text_edit")
        properties_layout.addWidget(author_label, 1, 1)
        properties_layout.addWidget(self.author_input, 2, 1)

        # Subject and Keywords
        subject_label = QLabel(tr("subject_label"))
        apply_theme_style(subject_label, "label")
        self.subject_input = QLineEdit()
        self.subject_input.setMinimumHeight(35)
        apply_theme_style(self.subject_input, "text_edit")
        properties_layout.addWidget(subject_label, 3, 0)
        properties_layout.addWidget(self.subject_input, 4, 0)

        keywords_label = QLabel(tr("keywords_label"))
        apply_theme_style(keywords_label, "label")
        self.keywords_input = QLineEdit()
        self.keywords_input.setMinimumHeight(35)
        apply_theme_style(self.keywords_input, "text_edit")
        properties_layout.addWidget(keywords_label, 3, 1)
        properties_layout.addWidget(self.keywords_input, 4, 1)
        
        content_layout.addWidget(properties_container)

        # 4. أزرار الإجراءات
        action_buttons_layout = QHBoxLayout()
        # إضافة قائمة منسدلة للاختيار بين الإجراءات
        from PySide6.QtWidgets import QComboBox
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            tr("encrypt_file"),
            tr("decrypt_file"),
            tr("update_properties_only")
        ])
        self.action_combo.setMinimumWidth(200)
        # تطبيق نمط الثيمة على القائمة المنسدلة
        apply_theme_style(self.action_combo, "combo")

        # زر حفظ واحد
        self.save_button = create_button(tr("save_file"), on_click=self.save_file_with_selected_action)

        action_label = QLabel(tr("select_action"))
        apply_theme_style(action_label, "label")
        action_buttons_layout.addWidget(action_label)
        action_buttons_layout.addWidget(self.action_combo)
        action_buttons_layout.addStretch(1)
        action_buttons_layout.addWidget(self.save_button)
        content_layout.addLayout(action_buttons_layout)

        # إضافة مساحة تمدد في نهاية المحتوى
        content_layout.addStretch()

        # ضبط حاوية المحتوى في منطقة التمرير
        scroll_area.setWidget(scroll_content)

        # إضافة منطقة التمرير إلى التخطيط الرئيسي مباشرة بعد العنوان وقبل الأزرار
        # إزالة الـ stretch الموجود في BasePage واستبداله بمنطقة التمرير
        self.main_layout.removeItem(self.main_layout.itemAt(2))  # إزالة الـ stretch
        self.main_layout.insertWidget(2, scroll_area)  # إضافة منطقة التمرير

        # تحديث حالة الواجهة
        self.update_ui_state()

    def select_file(self):
        """فتح مربع حوار لاختيار ملف PDF"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, tr("select_pdf_file_title"), "", tr("pdf_files_filter_rotate"))
            if file_path:
                self.source_file = file_path
                # إصلاح استخدام tr() - استخدام f-string بدلاً من معاملات
                file_name = os.path.basename(file_path)
                self.file_label.setText(f"الملف المحدد: {file_name}")
                self.load_pdf_properties(self.source_file)
                self.update_ui_state()

                # إشعار بنجاح تحديد الملف
                self.notification_manager.show_notification(f"{tr('file_selected_successfully')}: {file_name}", "info", duration=3000)

        except Exception as e:
            self.notification_manager.show_notification(f"{tr('error_selecting_file')}: {str(e)}", "error")

    def save_file_with_selected_action(self):
        """تنفيذ الإجراء المختار وحفظ الملف"""
        if not self.source_file:
            # self.message_manager.show_warning("لم يتم تحديد ملف", "الرجاء تحديد ملف PDF أولاً.")
            return

        # الحصول على الإجراء المحدد
        selected_action = self.action_combo.currentText()

        if selected_action == tr("encrypt_file"):
            # تنفيذ عملية التشفير
            password = self.password_input.text()
            if not password:
                # self.message_manager.show_warning("كلمة مرور فارغة", "الرجاء إدخال كلمة مرور للمستخدم.")
                return

            output_path = self.get_save_path(tr("encrypted_suffix"))
            if not output_path:
                return

            owner_password = self.owner_password_input.text()
            permissions = {
                'print': self.allow_printing_cb.isChecked(),
                'copy': self.allow_copying_cb.isChecked(),
            }

            info(f"بدء عملية التشفير للملف: {self.source_file}")
            self.operations_manager.encrypt_pdf(self.source_file, output_path, password, owner_password, permissions)

        elif selected_action == tr("decrypt_file"):
            # تنفيذ عملية فك التشفير
            password = self.password_input.text()
            if not password:
                # self.message_manager.show_warning("كلمة مرور فارغة", "الرجاء إدخال كلمة المرور الحالية لفك التشفير.")
                return

            output_path = self.get_save_path(tr("decrypted_suffix"))
            if not output_path:
                return

            info(f"بدء عملية فك التشفير للملف: {self.source_file}")
            self.operations_manager.decrypt_pdf(self.source_file, output_path, password)

        elif selected_action == tr("update_properties_only"):
            # تنفيذ عملية تحديث الخصائص
            output_path = self.get_save_path(tr("properties_updated_suffix"))
            if not output_path:
                return

            properties = {
                '/Title': self.title_input.text(),
                '/Author': self.author_input.text(),
                '/Subject': self.subject_input.text(),
                '/Keywords': self.keywords_input.text(),
            }

            info(f"بدء عملية تحديث الخصائص للملف: {self.source_file}")
            self.operations_manager.update_pdf_properties(self.source_file, output_path, properties)

    def update_ui_state(self):
        """تحديث حالة الأزرار بناءً على اختيار الملف"""
        has_selection = bool(self.source_file)
        # تعطيل زر الحفظ وقائمة الاختيارات إذا لم يتم اختيار ملف
        self.save_button.setEnabled(has_selection)
        self.action_combo.setEnabled(has_selection)
        
        if not has_selection:
            self.file_label.setText(tr("no_file_selected"))
            self.clear_properties_fields()

    def load_pdf_properties(self, file_path):
        """تحميل وعرض خصائص ملف PDF المحدد"""
        try:
            info(f"جاري تحميل خصائص الملف: {file_path}")
            # محاولة تحميل الخصائص بدون كلمة مرور أولاً
            properties = self.operations_manager.get_pdf_properties(file_path)

            # فحص ما إذا كان الملف مشفراً
            if properties and 'encrypted' in properties and properties['encrypted']:
                # إذا كان هناك كلمة مرور مدخلة بالفعل، استخدمها
                password = self.password_input.text()
                if password:
                    # محاولة أخرى مع كلمة المرور
                    properties = self.operations_manager.get_pdf_properties(file_path, password)
                else:
                    # تنبيه المستخدم أن الملف مشفر ويحتاج كلمة مرور
                    info("الملف مشفر. الرجاء إدخال كلمة المرور وإعادة اختيار الملف.")
                    return

            if properties:
                self.title_input.setText(properties.get('/Title', ''))
                self.author_input.setText(properties.get('/Author', ''))
                self.subject_input.setText(properties.get('/Subject', ''))
                self.keywords_input.setText(properties.get('/Keywords', ''))
                info("تم تحميل الخصائص بنجاح.")
                self.notification_manager.show_notification(tr("pdf_properties_loaded_successfully"), "info", duration=2000)
            else:
                self.clear_properties_fields()
                self.notification_manager.show_notification(tr("no_properties_found_in_pdf"), "warning")
        except Exception as e:
            error(f"فشل في تحميل خصائص PDF: {e}")
            self.notification_manager.show_notification(f"{tr('pdf_properties_update_error')}: {str(e)}", "error")
            self.clear_properties_fields()

    def clear_properties_fields(self):
        """مسح حقول الخصائص"""
        self.title_input.clear()
        self.author_input.clear()
        self.subject_input.clear()
        self.keywords_input.clear()

    def get_save_path(self, suffix):
        """فتح مربع حوار لحفظ الملف"""
        if not self.source_file:
            return None
        
        # اقتراح اسم ملف جديد
        default_path = self.operations_manager.get_output_path(self.source_file, suffix)
        save_path, _ = QFileDialog.getSaveFileName(self, tr("save_file_title"), default_path, tr("pdf_files_filter_rotate"))
        return save_path

    def encrypt_pdf(self):
        """تشفير ملف PDF بكلمة مرور"""
        if not self.source_file:
            # self.message_manager.show_warning("لم يتم تحديد ملف", "الرجاء تحديد ملف PDF لتشفيره.")
            return

        password = self.password_input.text()
        if not password:
            # self.message_manager.show_warning("كلمة مرور فارغة", "الرجاء إدخال كلمة مرور للمستخدم.")
            return

        output_path = self.get_save_path(tr("encrypted_suffix"))
        if not output_path:
            return

        owner_password = self.owner_password_input.text()
        permissions = {
            'print': self.allow_printing_cb.isChecked(),
            'copy': self.allow_copying_cb.isChecked(),
        }
        
        info(f"بدء عملية التشفير للملف: {self.source_file}")
        self.operations_manager.encrypt_pdf(self.source_file, output_path, password, owner_password, permissions)

    def decrypt_pdf(self):
        """فك تشفير ملف PDF"""
        if not self.source_file:
            # self.message_manager.show_warning("لم يتم تحديد ملف", "الرجاء تحديد ملف PDF لفك تشفيره.")
            return

        password = self.password_input.text()
        if not password:
            # self.message_manager.show_warning("كلمة مرور فارغة", "الرجاء إدخال كلمة المرور الحالية لفك التشفير.")
            return

        output_path = self.get_save_path(tr("decrypted_suffix"))
        if not output_path:
            return

        info(f"بدء عملية فك التشفير للملف: {self.source_file}")
        self.operations_manager.decrypt_pdf(self.source_file, output_path, password)

    def toggle_password_visibility(self):
        """تبديل إظهار/إخفاء كلمة المرور الرئيسية"""
        # الحصول على مسار الأيقونة
        base_path = os.path.abspath(".")

        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            eye_off_path = os.path.join(base_path, "assets", "icons", "default", "eye-off.svg")
            self.toggle_password_btn.setIcon(QIcon(eye_off_path))
            # استخدام إعدادات التلميحات
            from modules.settings import should_show_tooltips
            if should_show_tooltips():
                self.toggle_password_btn.setToolTip(tr("hide_password"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            eye_path = os.path.join(base_path, "assets", "icons", "default", "eye.svg")
            self.toggle_password_btn.setIcon(QIcon(eye_path))
            # استخدام إعدادات التلميحات
            from modules.settings import should_show_tooltips
            if should_show_tooltips():
                self.toggle_password_btn.setToolTip(tr("show_password"))

    def toggle_owner_password_visibility(self):
        """تبديل إظهار/إخفاء كلمة مرور المالك"""
        # الحصول على مسار الأيقونة
        base_path = os.path.abspath(".")

        if self.owner_password_input.echoMode() == QLineEdit.Password:
            self.owner_password_input.setEchoMode(QLineEdit.Normal)
            eye_off_path = os.path.join(base_path, "assets", "icons", "default", "eye-off.svg")
            self.toggle_owner_password_btn.setIcon(QIcon(eye_off_path))
            # استخدام إعدادات التلميحات
            from modules.settings import should_show_tooltips
            if should_show_tooltips():
                self.toggle_owner_password_btn.setToolTip(tr("hide_owner_password"))
        else:
            self.owner_password_input.setEchoMode(QLineEdit.Password)
            eye_path = os.path.join(base_path, "assets", "icons", "default", "eye.svg")
            self.toggle_owner_password_btn.setIcon(QIcon(eye_path))
            # استخدام إعدادات التلميحات
            from modules.settings import should_show_tooltips
            if should_show_tooltips():
                self.toggle_owner_password_btn.setToolTip(tr("show_owner_password"))

    def update_properties(self):
        """تحديث خصائص ملف PDF"""
        try:
            if not self.source_file:
                self.notification_manager.show_notification(tr("no_file_selected_for_properties_update"), "warning")
                return

            output_path = self.get_save_path(tr("properties_updated_suffix"))
            if not output_path:
                return

            properties = {
                '/Title': self.title_input.text(),
                '/Author': self.author_input.text(),
                '/Subject': self.subject_input.text(),
                '/Keywords': self.keywords_input.text(),
            }

            # إشعار بدء العملية
            self.notification_manager.show_notification(tr("updating_pdf_properties"), "info", duration=2000)

            info(f"بدء عملية تحديث الخصائص للملف: {self.source_file}")
            success = self.operations_manager.update_pdf_properties(self.source_file, output_path, properties)

            if success:
                self.notification_manager.show_notification(tr("pdf_properties_updated_successfully"), "success", duration=4000)
            else:
                self.notification_manager.show_notification(tr("pdf_properties_update_failed"), "error")

        except Exception as e:
            self.notification_manager.show_notification(f"{tr('pdf_properties_update_error')}: {str(e)}", "error")
