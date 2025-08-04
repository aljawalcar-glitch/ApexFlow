# -*- coding: utf-8 -*-
"""
صفحة دمج وطباعة ملفات PDF
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QComboBox, QLabel
from .base_page import BasePageWidget
from .ui_helpers import create_button
from .theme_manager import apply_theme_style
from modules.translator import tr

class MergePage(BasePageWidget):
    """
    واجهة المستخدم الخاصة بوظيفة دمج وطباعة ملفات PDF.
    """
    def __init__(self, file_manager, operations_manager, notification_manager, parent=None):
        """
        :param file_manager: مدير الملفات لاختيار الملفات.
        :param operations_manager: مدير العمليات لتنفيذ الدمج والطباعة.
        :param notification_manager: مدير الإشعارات المركزي.
        """
        super().__init__(
            page_title=tr("merge_page_title"),
            theme_key="merge_page",
            notification_manager=notification_manager,
            parent=parent
        )

        self.file_manager = file_manager
        self.operations_manager = operations_manager
        self.has_unsaved_changes = False

        # --- إزالة الأزرار العلوية الافتراضية ---
        for i in reversed(range(self.top_buttons_layout.count())): 
            widget = self.top_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # --- حاوية عناصر التحكم العلوية ---
        self.controls_widget = QWidget()
        # تطبيق نمط الثيمة على الحاوية
        apply_theme_style(self.controls_widget, "frame", auto_register=True)
        self.controls_layout = QVBoxLayout(self.controls_widget)
        self.controls_layout.setSpacing(10)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)

        # --- أزرار إضافة الملفات ---
        add_files_layout = QHBoxLayout()
        self.add_folder_button = create_button(tr("add_folder"))
        self.add_folder_button.clicked.connect(self.add_folder)
        self.add_file_button = create_button(tr("add_file"))
        self.add_file_button.clicked.connect(self.select_files)
        add_files_layout.addWidget(self.add_folder_button)
        add_files_layout.addWidget(self.add_file_button)
        self.controls_layout.addLayout(add_files_layout)

        # --- أزرار وخيارات الإجراءات ---
        self.action_widget = QWidget()
        # تطبيق نمط الثيمة على حاوية الإجراءات
        apply_theme_style(self.action_widget, "frame", auto_register=True)
        action_layout = QHBoxLayout(self.action_widget)

        self.printer_label = QLabel(tr("select_printer"))
        self.printer_combo = QComboBox()
        self.merge_button = create_button(tr("merge_files"), is_default=True)
        self.print_button = create_button(tr("print_files"))

        # تطبيق أنماط الثيمة على العناصر
        apply_theme_style(self.printer_label, "label", auto_register=True)
        apply_theme_style(self.printer_combo, "combo", auto_register=True)

        action_layout.addWidget(self.merge_button)
        action_layout.addStretch()
        action_layout.addWidget(self.printer_label)
        action_layout.addWidget(self.printer_combo)
        action_layout.addWidget(self.print_button)

        self.merge_button.clicked.connect(self.execute_merge)
        self.print_button.clicked.connect(self.execute_print)
        
        self.controls_layout.addWidget(self.action_widget)
        self.action_widget.setVisible(False)

        # --- إضافة الحاوية إلى التخطيط الرئيسي ---
        self.main_layout.insertWidget(1, self.controls_widget)

        # --- إخفاء إطار الملفات افتراضيًا ---
        self.file_list_frame.setVisible(False)

        # تأجيل تحميل الطابعات حتى الحاجة إليها
        self._printers_loaded = False

    def load_printers(self):
        """تحميل قائمة الطابعات المتاحة في القائمة المنسدلة (عند الحاجة فقط)"""
        if self._printers_loaded:
            return  # تم التحميل مسبقاً

        try:
            if self.operations_manager:
                # تحميل الطابعات بدون إظهار رسائل خطأ
                printers = self.operations_manager.get_available_printers()
                self.printer_combo.addItems(printers)
            else:
                # في حالة عدم توفر operations_manager
                self.printer_combo.addItems(["Microsoft Print to PDF"])
            self._printers_loaded = True
        except Exception as e:
            # إضافة طابعة افتراضية في حالة أي خطأ (بدون إظهار رسالة)
            print(f"تحذير: لا يمكن تحميل الطابعات - {e}")
            self.printer_combo.addItems(["Microsoft Print to PDF"])
            self._printers_loaded = True

    def select_files(self):
        """فتح حوار لاختيار ملفات PDF وتحديث القائمة."""
        files = self.file_manager.select_pdf_files(title=tr("select_pdf_files_title"), multiple=True)
        if files:
            self.file_list_frame.add_files(files)
            self.on_files_changed(self.file_list_frame.get_valid_files())
            self.has_unsaved_changes = True

    def add_folder(self):
        """فتح حوار لاختيار مجلد وإضافة كل ملفات PDF فيه."""
        from modules.app_utils import browse_folder_simple

        # استخدام نافذة اختيار المجلد البسيطة
        folder = browse_folder_simple(title=tr("select_folder_title"))

        # إذا تم اختيار مجلد، معالجته
        if folder:
            files = self.file_manager.get_pdf_files_from_folder(folder)
            if files:
                self.file_list_frame.add_files(files)
                self.on_files_changed(self.file_list_frame.get_valid_files())
                self.has_unsaved_changes = True

    def execute_merge(self):
        """تنفيذ عملية الدمج مع إشعارات للمستخدم."""
        try:
            files_to_merge = self.file_list_frame.get_valid_files()

            if len(files_to_merge) < 2:
                self.notification_manager.show_notification(tr("select_at_least_two_files_for_merge"), "warning")
                return

            # إشعار بدء عملية الدمج
            self.notification_manager.show_notification(f"{tr('merging_started')} ({len(files_to_merge)} ملف)", "info", duration=3000)

            # تنفيذ عملية الدمج
            success = self.operations_manager.merge_files(self)

            if success:
                self.notification_manager.show_notification(f"{tr('merging_completed_successfully')} ({len(files_to_merge)} ملف)", "success", duration=4000)
                self.reset_ui()
            else:
                # عرض رسالة خطأ أكثر تحديدًا
                QMessageBox.critical(self, tr("error_title"), tr("merge_failed_check_files"))

        except Exception as e:
            self.notification_manager.show_notification(f"{tr('merging_error')}: {str(e)}", "error")

    def execute_print(self):
        """تنفيذ عملية الطباعة بعد تأكيد المستخدم."""
        try:
            # تحميل الطابعات عند الحاجة فقط
            self.load_printers()

            selected_files = self.file_list_frame.get_valid_files()
            if not selected_files:
                self.notification_manager.show_notification(tr("select_one_file_message"), "warning")
                return

            printer_name = self.printer_combo.currentText()
            if not printer_name:
                self.notification_manager.show_notification(tr("select_printer_message"), "warning")
                return

            # إشعار بدء عملية الطباعة
            self.notification_manager.show_notification(f"{tr('printing_started')} ({len(selected_files)} ملف) - {printer_name}", "info", duration=3000)

            # تنفيذ عملية الطباعة
            success = self.operations_manager.print_files(selected_files, printer_name, self)

            if success:
                self.notification_manager.show_notification(f"{tr('printing_completed_successfully')} ({len(selected_files)} ملف)", "success", duration=4000)
                self.reset_ui()
            else:
                self.notification_manager.show_notification(tr("printing_failed"), "error")

        except Exception as e:
            self.notification_manager.show_notification(f"{tr('printing_error')}: {str(e)}", "error")

    def on_files_changed(self, files):
        """إظهار أو إخفاء العناصر بناءً على وجود الملفات."""
        has_files = len(files) > 0
        self.file_list_frame.setVisible(has_files)
        self.action_widget.setVisible(has_files)
        self.has_unsaved_changes = has_files

        # تحميل الطابعات عند إظهار عناصر التحكم لأول مرة
        if has_files and not self._printers_loaded:
            self.load_printers()

        self.merge_button.setEnabled(True)
        self.print_button.setEnabled(has_files)

    def reset_ui(self):
        """إعادة تعيين الواجهة إلى حالتها الأولية."""
        self.file_list_frame.clear_all_files()
        self.has_unsaved_changes = False
        self.on_files_changed([])
