# -*- coding: utf-8 -*-
"""
صفحة دمج وطباعة ملفات PDF
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QComboBox, QLabel, QApplication, QGroupBox, QCheckBox
from PySide6.QtCore import Qt
from .base_page import BasePageWidget
from .ui_helpers import create_button
from .theme_manager import apply_theme_style
from modules.translator import tr
from .smart_drop_overlay import SmartDropOverlay

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
        
        # تفعيل السحب والإفلات
        self.setAcceptDrops(True)

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

        # فريم خيارات الطباعة
        self.print_options_frame = QGroupBox(tr("print_options"))
        apply_theme_style(self.print_options_frame, "group_box", auto_register=True)
        print_options_layout = QVBoxLayout(self.print_options_frame)

        # تخطيط أفقي للطابعة ومربع الاختيار
        printer_layout = QHBoxLayout()
        
        self.printer_label = QLabel(tr("select_printer"))
        self.printer_combo = QComboBox()
        # تطبيق أنماط الثيمة على العناصر
        apply_theme_style(self.printer_label, "label", auto_register=True)
        apply_theme_style(self.printer_combo, "combo", auto_register=True)
        
        printer_layout.addWidget(self.printer_label)
        printer_layout.addWidget(self.printer_combo)
        print_options_layout.addLayout(printer_layout)
        
        # إضافة خانة اختيار للطباعة بعد الدمج
        self.print_after_merge = QCheckBox(tr("print_after_merge"))
        self.print_after_merge.setLayoutDirection(Qt.RightToLeft)
        apply_theme_style(self.print_after_merge, "checkbox", auto_register=True)
        print_options_layout.addWidget(self.print_after_merge)
        
        # فريم زر الدمج
        self.merge_button_frame = QGroupBox(tr("execute"))
        apply_theme_style(self.merge_button_frame, "group_box", auto_register=True)
        merge_layout = QVBoxLayout(self.merge_button_frame)
        
        # زر الدمج بأيقونة
        from .svg_icon_button import create_action_button
        from .theme_manager import global_theme_manager
        if global_theme_manager.current_theme == "light":
            icon_color = "#333333"  # لون داكن للوضع الفاتح
        else:
            icon_color = "#ffffff"  # لون أبيض للوضع المظلم
            
        self.merge_button = create_action_button("merge", 32, tr("merge_files"))
        self.merge_button.set_icon_color(icon_color)
        
        # تحديث نص الزر بناءً على الحالة الأولية
        self.update_merge_button_text()

        # إضافة زر الدمج للتخطيط
        merge_layout.addWidget(self.merge_button)
        merge_layout.addStretch()
        
        # إضافة الفريمين للتخطيط الأفقي
        action_layout.addWidget(self.print_options_frame, 2)  # يأخذ مساحة أكبر
        action_layout.addWidget(self.merge_button_frame, 0)  # مساحة صغيرة
        
        # ربط حدث تغيير خانة الاختيار
        self.print_after_merge.stateChanged.connect(self.toggle_print_button)
        
        # ربط حدث النقر على زر الدمج
        self.merge_button.clicked.connect(self.execute_merge)
        
        self.controls_layout.addWidget(self.action_widget)
        self.action_widget.setVisible(False)

        # --- إضافة الحاوية إلى التخطيط الرئيسي ---
        self.main_layout.insertWidget(1, self.controls_widget)

        # --- إخفاء إطار الملفات افتراضيًا ---
        # self.file_list_frame.setVisible(False) # تم التعطيل للسماح للإطار بإدارة حالته

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
            
    def add_files(self, files):
        """إضافة ملفات مباشرة إلى القائمة (للسحب والإفلات)"""
        if files:
            # التأكد من أن إطار الملفات مرئي قبل إضافة الملفات
            if not self.file_list_frame.isVisible():
                self.file_list_frame.setVisible(True)
            
            self.file_list_frame.add_files(files)
            self.on_files_changed(self.file_list_frame.get_valid_files())
            self.has_unsaved_changes = True
            
            # فرض تحديث فوري للواجهة
            QApplication.processEvents()

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
            print_after_merge = self.print_after_merge.isChecked()
            
            # حالة الطباعة فقط (ملف واحد ومربع الطباعة محدد)
            if print_after_merge and len(files_to_merge) == 1:
                # تحميل الطابعات عند الحاجة فقط
                self.load_printers()
                
                printer_name = self.printer_combo.currentText()
                if not printer_name:
                    self.notification_manager.show_notification(tr("no_printer_selected"), "warning")
                    return
                
                # إشعار بدء عملية الطباعة
                self.notification_manager.show_notification(f"{tr('printing_started')} ({len(files_to_merge)} ملف) - {printer_name}", "info", duration=3000)
                
                # تنفيذ عملية الطباعة فقط
                print_success = self.operations_manager.print_files(files_to_merge, printer_name, self)
                
                if print_success:
                    self.notification_manager.show_notification(f"{tr('printing_completed_successfully')} ({len(files_to_merge)} ملف)", "success", duration=4000)
                    self.reset_ui()
                else:
                    self.notification_manager.show_notification(tr("printing_failed"), "error")
                return
            
            # حالة الدمج والطباعة (أكثر من ملف ومربع الطباعة محدد)
            if print_after_merge:
                if len(files_to_merge) < 2:
                    self.notification_manager.show_notification(tr("select_at_least_two_files_for_merge"), "warning")
                    return
                
                # إشعار بدء عملية الدمج
                self.notification_manager.show_notification(f"{tr('merging_started')} ({len(files_to_merge)} ملف)", "info", duration=3000)
                
                # تنفيذ عملية الدمج
                merge_success = self.operations_manager.merge_files(self)
                
                if merge_success:
                    self.notification_manager.show_notification(f"{tr('merging_completed_successfully')} ({len(files_to_merge)} ملف)", "success", duration=4000)
                    
                    # تحميل الطابعات عند الحاجة فقط
                    self.load_printers()
                    
                    printer_name = self.printer_combo.currentText()
                    if printer_name:
                        self.notification_manager.show_notification(f"{tr('printing_started')} ({len(files_to_merge)} ملف) - {printer_name}", "info", duration=3000)
                        print_success = self.operations_manager.print_files(files_to_merge, printer_name, self)
                        
                        if print_success:
                            self.notification_manager.show_notification(f"{tr('printing_completed_successfully')} ({len(files_to_merge)} ملف)", "success", duration=4000)
                        else:
                            self.notification_manager.show_notification(tr("printing_failed"), "error")
                    else:
                        self.notification_manager.show_notification(tr("no_printer_selected"), "warning")
                    
                    self.reset_ui()
                else:
                    # عرض رسالة خطأ أكثر تحديدًا باستخدام نظام الإشعارات
                    self.notification_manager.show_notification(tr("merge_failed_check_files"), "error")
                return
            
            # حالة الدمج فقط (مربع الطباعة غير محدد)
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
                # عرض رسالة خطأ أكثر تحديدًا باستخدام نظام الإشعارات
                self.notification_manager.show_notification(tr("merge_failed_check_files"), "error")

        except Exception as e:
            self.notification_manager.show_notification(f"{tr('merging_error')}: {str(e)}", "error")

    def toggle_print_button(self, state):
        """تبديل حالة خيارات الطباعة بناءً على خانة الاختيار."""
        # تمكين أو تعطيل خيارات الطباعة بناءً على حالة خانة الاختيار
        is_checked = (state == Qt.CheckState.Checked.value)
        self.printer_label.setEnabled(is_checked)
        self.printer_combo.setEnabled(is_checked)
        
        # تحديث نص الزر عند تغيير حالة خانة الاختيار
        self.update_merge_button_text()
        
    def update_merge_button_text(self):
        """تحديث عنوان إطار الزر بناءً على حالة خانة الاختيار وعدد الملفات."""
        files_count = len(self.file_list_frame.get_valid_files())
        print_after_merge = self.print_after_merge.isChecked()
        
        # تحديد لون الأيقونة بناءً على السمة
        from .theme_manager import global_theme_manager
        if global_theme_manager.current_theme == "light":
            icon_color = "#333333"  # لون داكن للوضع الفاتح
        else:
            icon_color = "#ffffff"  # لون أبيض للوضع المظلم
            
        if print_after_merge and files_count == 1:
            # حالة الطباعة فقط
            self.merge_button_frame.setTitle(tr("print_files"))
            # تغيير الأيقونة إلى أيقونة الطباعة
            self.merge_button.icon_name = "printer"
            self.merge_button.load_icon(icon_color)
        elif print_after_merge:
            # حالة الدمج والطباعة
            self.merge_button_frame.setTitle(tr("merge_and_print_files"))
            # تغيير الأيقونة إلى أيقونة الدمج
            self.merge_button.icon_name = "merge"
            self.merge_button.load_icon(icon_color)
        else:
            # حالة الدمج فقط
            self.merge_button_frame.setTitle(tr("merge_files"))
            # تغيير الأيقونة إلى أيقونة الدمج
            self.merge_button.icon_name = "merge"
            self.merge_button.load_icon(icon_color)

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
        """إظهار أو إخفاء العناصر بناءً على وجود الملفات."""
        has_files = len(files) > 0
        # self.file_list_frame.setVisible(has_files) # تم التعطيل للسماح للإطار بإدارة حالته
        self.action_widget.setVisible(has_files)
        self.has_unsaved_changes = has_files

        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(main_window.get_page_index(self), has_files)

        # تحميل الطابعات عند إظهار عناصر التحكم لأول مرة
        if has_files and not self._printers_loaded:
            self.load_printers()

        self.merge_button.setEnabled(True)
        # تمكين أو تعطيل خيارات الطباعة بناءً على حالة خانة الاختيار
        is_print_enabled = has_files and self.print_after_merge.isChecked()
        self.printer_label.setEnabled(is_print_enabled)
        self.printer_combo.setEnabled(is_print_enabled)
        
        # تحديث نص الزر عند تغيير عدد الملفات
        self.update_merge_button_text()

    def reset_ui(self):
        """إعادة تعيين الواجهة إلى حالتها الأولية."""
        self.file_list_frame.clear_all_files()
        self.has_unsaved_changes = False
        self.on_files_changed([])
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

    def handle_smart_drop_action(self, action_type, files):
        """معالجة الإجراء المحدد من الطبقة الذكية"""
        if action_type == "add_to_list":
            self.add_files(files)
        elif action_type == "merge_now":
            self.add_files(files)
            # التأكد من أن الواجهة محدثة قبل بدء الدمج
            QApplication.processEvents()
            self.execute_merge()
