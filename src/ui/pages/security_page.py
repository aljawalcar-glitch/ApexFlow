# -*- coding: utf-8 -*-

"""
صفحة حماية وخصائص ملفات PDF
"""

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QFormLayout, QCheckBox, QFileDialog, QScrollArea, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from src.ui.widgets.base_page import BasePageWidget as BasePage
from src.ui.widgets.ui_helpers import create_info_label, create_button
from src.ui.widgets.global_styles import get_scroll_style
from src.utils.logger import info, error
from src.managers.operations_manager import get_icon_path
from src.managers.theme_manager import make_theme_aware
from src.utils.translator import tr
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
        self.has_unsaved_changes = False

        # تفعيل السحب والإفلات
        self.setAcceptDrops(True)

        self.init_ui()

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
            # صفحة الأمان تقبل ملف واحد فقط
            file_path = files[0]
            if os.path.exists(file_path):
                self.source_file = file_path
                file_name = os.path.basename(file_path)
                self.file_label.setText(f"الملف المحدد: {file_name}")
                self.load_pdf_properties(self.source_file)
                self.update_ui_state()
                self.notification_manager.show_notification(f"{tr('file_selected_successfully')}: {file_name}", "info", duration=3000)

    def handle_smart_drop_action(self, action_type, files):
        """معالجة الإجراء المحدد من الطبقة الذكية"""
        if action_type == "add_to_list":
            self.add_files(files)

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

    def init_ui(self):
        """إنشاء واجهة المستخدم للصفحة"""
        # إزالة الاعتماد على file_list_frame من BasePage
        if self.file_list_frame:
            self.main_layout.removeWidget(self.file_list_frame)
            self.file_list_frame.deleteLater()
            self.file_list_frame = None

        # إنشاء منطقة التمرير مباشرة بعد عنوان الصفحة
        scroll_area = QScrollArea()
        from src.managers.theme_manager import global_theme_manager
        colors = global_theme_manager.get_current_colors()
        accent_color = global_theme_manager.current_accent
        scroll_area.setStyleSheet(get_scroll_style(colors, accent_color) + "background-color: transparent;")
        scroll_area.viewport().setStyleSheet("background-color: transparent;")
        
        # تسجيل منطقة التمرير في مدير الثيمات العالمي
        make_theme_aware(scroll_area, "graphics_view")

        # 1. قسم اختيار الملف داخل المحتوى
        file_selection_layout = QHBoxLayout()
        self.select_file_button = create_button(tr("select_pdf_file"), on_click=self.select_file)
        self.file_label = QLabel(tr("no_file_selected"))
        from src.managers.language_manager import language_manager
        self.file_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter if language_manager.is_rtl() else Qt.AlignLeft | Qt.AlignVCenter)
        # تطبيق نمط الثيمة على تسمية الملف
        make_theme_aware(self.file_label, "label")
        file_selection_layout.addWidget(self.select_file_button)
        file_selection_layout.addWidget(self.file_label, 1)
        scroll_area.setWidgetResizable(True)  # السماح بتغيير حجم المحتوى
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # إنشاء حاوية للمحتوى
        scroll_content = QWidget()
        # تطبيق نمط الثيمة على محتوى التمرير
        make_theme_aware(scroll_content, "dialog")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)

        # إضافة قسم اختيار الملف إلى المحتوى
        content_layout.addLayout(file_selection_layout)

        # 2. قسم إدارة كلمة المرور
        password_container = QWidget()
        # تطبيق نمط الثيمة على الحاوية
        make_theme_aware(password_container, "transparent_container")
        password_layout = QGridLayout(password_container)
        password_layout.setSpacing(15)
        
        password_section_label = QLabel(tr("password_management"))
        make_theme_aware(password_section_label, "section_label")
        password_layout.addWidget(password_section_label, 0, 0, 1, 2)

        # حقل كلمة مرور المستخدم
        user_password_label = QLabel(tr("user_password"))
        # تطبيق نمط الثيمة على التسمية
        make_theme_aware(user_password_label, "label")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(tr("password_placeholder"))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        # استخدام النمط الافتراضي للتطبيق
        # تطبيق نمط الثيمة على حقل الإدخال
        make_theme_aware(self.password_input, "text_edit_with_frame")

        password_layout.addWidget(user_password_label, 1, 0)
        password_layout.addWidget(self.password_input, 2, 0)

        # حقل كلمة مرور المالك
        owner_password_label = QLabel(tr("owner_password"))
        # تطبيق نمط الثيمة على التسمية
        make_theme_aware(owner_password_label, "label")

        self.owner_password_input = QLineEdit()
        self.owner_password_input.setPlaceholderText(tr("owner_password_placeholder"))
        self.owner_password_input.setEchoMode(QLineEdit.Password)
        self.owner_password_input.setMinimumHeight(35)
        # استخدام النمط الافتراضي للتطبيق
        # تطبيق نمط الثيمة على حقل الإدخال
        make_theme_aware(self.owner_password_input, "text_edit_with_frame")

        password_layout.addWidget(owner_password_label, 1, 1)
        password_layout.addWidget(self.owner_password_input, 2, 1)
        
        permissions_label = QLabel(tr("permissions_label"))
        # تطبيق نمط الثيمة على التسمية
        make_theme_aware(permissions_label, "label")

        from src.ui.widgets.toggle_switch import ToggleSwitch
        
        printing_layout = QHBoxLayout()
        printing_label = QLabel(tr("allow_printing"))
        make_theme_aware(printing_label, "label")
        self.allow_printing_cb = ToggleSwitch()
        self.allow_printing_cb.setChecked(True)
        printing_layout.addWidget(printing_label)
        printing_layout.addStretch()
        printing_layout.addWidget(self.allow_printing_cb)
        
        copying_layout = QHBoxLayout()
        copying_label = QLabel(tr("allow_copying"))
        make_theme_aware(copying_label, "label")
        self.allow_copying_cb = ToggleSwitch()
        self.allow_copying_cb.setChecked(True)
        copying_layout.addWidget(copying_label)
        copying_layout.addStretch()
        copying_layout.addWidget(self.allow_copying_cb)

        password_layout.addWidget(permissions_label, 3, 0)
        password_layout.addLayout(printing_layout, 3, 1)
        password_layout.addLayout(copying_layout, 4, 1)
        
        content_layout.addWidget(password_container)

        # 3. قسم خصائص الملف (Metadata)
        properties_container = QWidget()
        # تطبيق نمط الثيمة على الحاوية
        make_theme_aware(properties_container, "transparent_container")
        properties_layout = QGridLayout(properties_container)
        properties_layout.setSpacing(15)
        
        metadata_section_label = QLabel(tr("metadata_section"))
        make_theme_aware(metadata_section_label, "section_label")
        properties_layout.addWidget(metadata_section_label, 0, 0, 1, 2)

        # Title and Author
        title_label = QLabel(tr("title_label"))
        make_theme_aware(title_label, "label")
        self.title_input = QLineEdit()
        self.title_input.setMinimumHeight(35)
        # استخدام النمط الافتراضي للتطبيق
        make_theme_aware(self.title_input, "text_edit_with_frame")
        properties_layout.addWidget(title_label, 1, 0)
        properties_layout.addWidget(self.title_input, 2, 0)

        author_label = QLabel(tr("author_field_label"))
        make_theme_aware(author_label, "label")
        self.author_input = QLineEdit()
        self.author_input.setMinimumHeight(35)
        # استخدام النمط الافتراضي للتطبيق
        make_theme_aware(self.author_input, "text_edit_with_frame")
        properties_layout.addWidget(author_label, 1, 1)
        properties_layout.addWidget(self.author_input, 2, 1)

        # Subject and Keywords
        subject_label = QLabel(tr("subject_label"))
        make_theme_aware(subject_label, "label")
        self.subject_input = QLineEdit()
        self.subject_input.setMinimumHeight(35)
        # استخدام النمط الافتراضي للتطبيق
        make_theme_aware(self.subject_input, "text_edit_with_frame")
        properties_layout.addWidget(subject_label, 3, 0)
        properties_layout.addWidget(self.subject_input, 4, 0)

        keywords_label = QLabel(tr("keywords_label"))
        make_theme_aware(keywords_label, "label")
        self.keywords_input = QLineEdit()
        self.keywords_input.setMinimumHeight(35)
        # استخدام النمط الافتراضي للتطبيق
        make_theme_aware(self.keywords_input, "text_edit_with_frame")
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
        make_theme_aware(self.action_combo, "combo")

        # زر حفظ واحد
        self.save_button = create_button(tr("save_file"), on_click=self.save_file_with_selected_action)

        action_label = QLabel(tr("select_action"))
        make_theme_aware(action_label, "label")
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

        # ربط الإشارات لتتبع التغييرات
        self.password_input.textChanged.connect(self.mark_as_changed)
        self.owner_password_input.textChanged.connect(self.mark_as_changed)
        self.allow_printing_cb.stateChanged.connect(self.mark_as_changed)
        self.allow_copying_cb.stateChanged.connect(self.mark_as_changed)
        self.title_input.textChanged.connect(self.mark_as_changed)
        self.author_input.textChanged.connect(self.mark_as_changed)
        self.subject_input.textChanged.connect(self.mark_as_changed)
        self.keywords_input.textChanged.connect(self.mark_as_changed)

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
            from src.utils.settings import should_show_tooltips
            if should_show_tooltips():
                self.toggle_password_btn.setToolTip(tr("hide_password"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            eye_path = os.path.join(base_path, "assets", "icons", "default", "eye.svg")
            self.toggle_password_btn.setIcon(QIcon(eye_path))
            # استخدام إعدادات التلميحات
            from src.utils.settings import should_show_tooltips
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
            from src.utils.settings import should_show_tooltips
            if should_show_tooltips():
                self.toggle_owner_password_btn.setToolTip(tr("hide_owner_password"))
        else:
            self.owner_password_input.setEchoMode(QLineEdit.Password)
            eye_path = os.path.join(base_path, "assets", "icons", "default", "eye.svg")
            self.toggle_owner_password_btn.setIcon(QIcon(eye_path))
            # استخدام إعدادات التلميحات
            from src.utils.settings import should_show_tooltips
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

    def reset_ui(self):
        """إعادة تعيين الواجهة إلى حالتها الأولية."""
        self.source_file = None
        self.has_unsaved_changes = False
        self.clear_properties_fields()
        self.password_input.clear()
        self.owner_password_input.clear()
        self.allow_printing_cb.setChecked(True)
        self.allow_copying_cb.setChecked(True)
        self.update_ui_state()
        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(main_window.get_page_index(self), False)

    def mark_as_changed(self):
        """يسجل أن هناك تغييرات غير محفوظة."""
        if self.source_file:
            self.has_unsaved_changes = True
            main_window = self._get_main_window()
            if main_window:
                main_window.set_page_has_work(main_window.get_page_index(self), True)
