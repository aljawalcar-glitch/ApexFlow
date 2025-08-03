"""
وحدة الأدوات المساعدة للتطبيق
تحتوي على الدوال المساعدة للنظام والملفات والموارد
"""

import os
import psutil
from PySide6.QtWidgets import QMessageBox, QProgressDialog
from PySide6.QtCore import Qt
from modules.translator import tr

def get_icon_path():
    """العثور على مسار الأيقونة الصحيح سواء كان التطبيق مجمداً أم لا"""
    import sys

    if getattr(sys, 'frozen', False):
        # المسار داخل الملف التنفيذي
        base_path = sys._MEIPASS
    else:
        # المسار في بيئة التطوير
        base_path = os.path.abspath(".")

    # مسارات محتملة للأيقونة
    possible_paths = [
        os.path.join(base_path, "assets", "icons", "ApexFlow.ico"),
        os.path.join(base_path, "ApexFlow.ico"),
        os.path.join(base_path, "assets", "logo.png")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def check_system_resources(file_path):
    """التحقق من موارد النظام قبل معالجة الملفات الكبيرة"""
    try:
        # حجم الملف بالميجابايت
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        
        # الذاكرة المتاحة بالميجابايت
        available_memory = psutil.virtual_memory().available / (1024 * 1024)
        
        # تحذير إذا كان الملف كبير والذاكرة قليلة
        if file_size > 100 and available_memory < file_size * 3:
            return {
                'proceed': False,
                'file_size': file_size,
                'available_memory': available_memory,
                'warning': f"الملف كبير ({file_size:.1f} MB) والذاكرة المتاحة قليلة ({available_memory:.1f} MB).\nقد تستغرق العملية وقتاً أطول. هل تريد المتابعة؟"
            }
        
        return {'proceed': True}
    except:
        # في حالة عدم توفر psutil، نتابع بدون تحقق
        return {'proceed': True}

def show_progress_dialog(parent, title, message, maximum=0):
    """إنشاء وإظهار حوار التقدم للعمليات الطويلة"""
    progress = QProgressDialog(message, "إلغاء", 0, maximum, parent)
    progress.setWindowTitle(title)
    progress.setWindowModality(Qt.WindowModal)
    progress.setMinimumDuration(1000)  # إظهار بعد ثانية واحدة
    progress.setValue(0)
    return progress

def validate_pdf_files(files):
    """التحقق من صحة ملفات PDF"""
    if not files:
        return False, "لم يتم اختيار أي ملفات"
    
    invalid_files = []
    for file in files:
        if not os.path.exists(file):
            invalid_files.append(f"{file} (غير موجود)")
        elif not file.lower().endswith('.pdf'):
            invalid_files.append(f"{file} (ليس ملف PDF)")
    
    if invalid_files:
        return False, f"ملفات غير صالحة:\n" + "\n".join(invalid_files)
    
    return True, "جميع الملفات صالحة"

def get_output_path(parent, settings_data, default_name="output.pdf"):
    """الحصول على مسار الحفظ بناءً على الإعدادات"""
    from PySide6.QtWidgets import QFileDialog
    
    if settings_data.get('save_mode') == 'fixed' and settings_data.get('save_path'):
        return os.path.join(settings_data['save_path'], default_name)
    else:
        return QFileDialog.getSaveFileName(parent, "حفظ باسم", default_name, "PDF Files (*.pdf)")[0]

def show_success_message(parent, message):
    """عرض رسالة نجاح"""
    QMessageBox.information(parent, "نجاح", message)

def show_error_message(parent, message):
    """عرض رسالة خطأ"""
    QMessageBox.critical(parent, "خطأ", message)


class FileManager:
    """مدير الملفات الموحد - مسؤول عن جميع عمليات الملفات"""

    def __init__(self, main_window):
        self.main_window = main_window

    def select_file(self, title="اختيار ملف", file_filter="All Files (*)", multiple=False):
        """اختيار ملف واحد أو عدة ملفات مع مرشح مخصص."""
        from PySide6.QtWidgets import QFileDialog
        import os

        full_title = f"ApexFlow - {title}"
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")

        # إنشاء نافذة حوار اختيار الملفات
        dialog = QFileDialog(self.main_window, full_title, default_dir, file_filter)

        # جعل النافذة تظهر فوق الكل وتعطل الوصول للنافذة الرئيسية
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)

        if multiple:
            dialog.setFileMode(QFileDialog.ExistingFiles)
        else:
            dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_() == QFileDialog.Accepted:
            if multiple:
                return dialog.selectedFiles()
            else:
                return dialog.selectedFiles()[0] if dialog.selectedFiles() else None
        return None

    def select_pdf_files(self, title="اختيار ملفات PDF", multiple=True):
        """اختيار ملفات PDF"""
        return self.select_file(title, "PDF Files (*.pdf)", multiple)

    def select_image_files(self, title="اختيار ملفات الصور"):
        """اختيار ملفات الصور"""
        from PySide6.QtWidgets import QFileDialog
        import os

        full_title = f"ApexFlow - {title}"
        image_filter = "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        # مجلد Documents كافتراضي
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")

        files, _ = QFileDialog.getOpenFileNames(
            self.main_window,
            full_title,
            default_dir,
            image_filter
        )
        return files

    def select_text_file(self, title="اختيار ملف نصي"):
        """اختيار ملف نصي"""
        from PySide6.QtWidgets import QFileDialog
        import os

        full_title = f"ApexFlow - {title}"
        text_filter = "Text Files (*.txt)"
        # مجلد Documents كافتراضي
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")

        file, _ = QFileDialog.getOpenFileName(
            self.main_window,
            full_title,
            default_dir,
            text_filter
        )
        return file

    def select_save_location(self, title="حفظ الملف", default_name="output.pdf", file_filter="PDF Files (*.pdf)"):
        """اختيار مكان الحفظ"""
        from PySide6.QtWidgets import QFileDialog
        import os

        full_title = f"ApexFlow - {title}"
        # مجلد Documents كافتراضي مع اسم الملف
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")
        default_path = os.path.join(default_dir, default_name)

        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            full_title,
            default_path,
            file_filter
        )
        return file_path

    def select_directory(self, title="اختيار مجلد"):
        """اختيار مجلد باستخدام نافذة النظام"""
        from PySide6.QtWidgets import QFileDialog
        import os

        # الحصول على مجلد Documents كافتراضي
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")

        directory = QFileDialog.getExistingDirectory(
            self.main_window,
            f"ApexFlow - {title}",
            default_dir
        )
        return directory if directory else None

    def get_pdf_files_from_folder(self, folder_path):
        """الحصول على جميع ملفات PDF من مجلد معين"""
        pdf_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return pdf_files

    def get_output_path_with_settings(self, settings_data, default_name="output.pdf"):
        """الحصول على مسار الحفظ بناءً على الإعدادات"""
        if settings_data.get('save_mode') == 'fixed' and settings_data.get('save_path'):
            return os.path.join(settings_data['save_path'], default_name)
        else:
            return self.select_save_location("حفظ الملف", default_name)


class MessageManager:
    """مدير الرسائل الموحد - مسؤول عن جميع الرسائل"""

    def __init__(self, main_window):
        self.main_window = main_window

    def show_success(self, message, title="نجح"):
        """عرض رسالة نجاح"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QIcon

        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(f"ApexFlow - {title}")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)

        # تطبيق السمة
        try:
            from ui.theme_manager import apply_theme
            apply_theme(msg_box, "dialog")
        except:
            pass

        return msg_box.exec()

    def show_error(self, message, title="خطأ", details=""):
        """عرض رسالة خطأ"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QIcon

        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(f"ApexFlow - {title}")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)

        if details:
            msg_box.setDetailedText(details)

        # تطبيق السمة
        try:
            from ui.theme_manager import apply_theme
            apply_theme(msg_box, "dialog")
        except:
            pass

        return msg_box.exec()

    def show_warning(self, message, title="تحذير"):
        """عرض رسالة تحذير"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QIcon

        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(f"ApexFlow - {title}")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)

        # تطبيق السمة
        try:
            from ui.theme_manager import apply_theme
            apply_theme(msg_box, "dialog")
        except:
            pass

        return msg_box.exec()

    def ask_for_save_confirmation(self, inner_widget):
        """Asks the user to confirm saving changes and handles the response."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QCheckBox
        from ui.theme_manager import apply_theme_style
        from modules import settings

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(tr("confirm_title"))
        dialog.setMinimumWidth(400)
        apply_theme_style(dialog, "dialog")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        message_label = QLabel(tr("unsaved_changes_prompt"))
        message_label.setWordWrap(True)
        apply_theme_style(message_label, "label")
        layout.addWidget(message_label)

        dont_ask_checkbox = QCheckBox(tr("dont_ask_again_and_discard"))
        apply_theme_style(dont_ask_checkbox, "checkbox")
        layout.addWidget(dont_ask_checkbox)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton(tr("save_and_close"))
        apply_theme_style(save_button, "button")
        buttons_layout.addWidget(save_button)

        discard_button = QPushButton(tr("discard_changes"))
        apply_theme_style(discard_button, "button")
        buttons_layout.addWidget(discard_button)

        cancel_button = QPushButton(tr("cancel_button"))
        apply_theme_style(cancel_button, "button")
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        # Connect signals to dialog slots
        save_button.clicked.connect(lambda: self._handle_save_confirmation(inner_widget, dialog, dont_ask_checkbox, "save"))
        discard_button.clicked.connect(lambda: self._handle_save_confirmation(inner_widget, dialog, dont_ask_checkbox, "discard"))
        cancel_button.clicked.connect(dialog.reject)

        return dialog.exec_()

    def _handle_save_confirmation(self, widget, dialog, checkbox, action):
        """Handles the logic for the save confirmation dialog buttons."""
        from modules import settings
        if checkbox.isChecked():
            settings.set_setting("dont_ask_again_and_discard", True)
            self.show_info(tr("dont_ask_again_info"))

        if action == "save":
            if hasattr(widget, 'save_all_settings'):
                widget.save_all_settings()
            dialog.accept()
        elif action == "discard":
            dialog.accept()

    def ask_question(self, message, title="سؤال"):
        """طرح سؤال مع نعم/لا"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QIcon

        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(f"ApexFlow - {title}")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # تطبيق السمة
        try:
            from ui.theme_manager import apply_theme
            apply_theme(msg_box, "dialog")
        except:
            pass

        return msg_box.exec() == QMessageBox.Yes

    def show_warning(self, message, title="تحذير"):
        """عرض رسالة تحذير"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QIcon

        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(f"ApexFlow - {title}")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)

        # تطبيق السمة
        try:
            from ui.theme_manager import apply_theme
            apply_theme(msg_box, "dialog")
        except:
            pass

        return msg_box.exec()


class OperationsManager:
    """
    مدير العمليات الموحد - مسؤول عن جميع عمليات PDF.
    يستخدم التحميل الكسول للوحدات لضمان بدء تشغيل سريع.
    """

    def __init__(self, main_window, file_manager, message_manager):
        self.main_window = main_window
        self.file_manager = file_manager
        self.message_manager = message_manager
        self._merge = None
        self._split = None
        self._compress = None
        self._rotate = None
        self._convert = None
        self._security = None

    @property
    def security_module(self):
        if self._security is None:
            from modules import security
            self._security = security
        return self._security

    @property
    def merge_module(self):
        if self._merge is None:
            from modules import merge
            self._merge = merge
        return self._merge

    @property
    def split_module(self):
        if self._split is None:
            from modules import split
            self._split = split
        return self._split

    @property
    def compress_module(self):
        if self._compress is None:
            from modules import compress
            self._compress = compress
        return self._compress

    @property
    def rotate_module(self):
        if self._rotate is None:
            from modules import rotate
            self._rotate = rotate
        return self._rotate

    @property
    def convert_module(self):
        if self._convert is None:
            from modules import convert
            self._convert = convert
        return self._convert

    def merge_files(self, page):
        """تنفيذ عملية دمج الملفات"""
        try:
            files = page.file_list_frame.get_valid_files()
            if len(files) < 2:
                page.notification_manager.show_notification("يجب اختيار ملفين على الأقل للدمج", "warning")
                return False

            # الحصول على مسار الحفظ
            from modules import settings
            settings_data = settings.load_settings()
            output = self.file_manager.get_output_path_with_settings(settings_data, "merged.pdf")

            if output:
                # تنفيذ عملية الدمج
                # استخدام إعدادات الدمج
                merge_settings = settings_data.get("merge_settings", {})
                if merge_settings.get("add_bookmarks", True):
                    success = self.merge_module.merge_pdfs_with_bookmarks(files, output)
                else:
                    success = self.merge_module.merge_pdfs(files, output)

                if success:
                    self.message_manager.show_success("تم دمج الملفات بنجاح!")
                    page.file_list_frame.clear_all_files()
                    return True
                else:
                    self.message_manager.show_error("فشل في دمج الملفات. تحقق من صحة الملفات.")
                    return False

        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def split_file(self, page):
        """تنفيذ عملية تقسيم الملف مع استخدام المسار التلقائي"""
        try:
            files = page.file_list_frame.get_valid_files()
            if len(files) != 1:
                self.message_manager.show_error("يجب اختيار ملف واحد فقط للتقسيم")
                return False

            file = files[0]

            # استخدام المسار التلقائي من الصفحة إذا كان متوفراً
            output_dir = None
            if hasattr(page, 'get_save_path'):
                output_dir = page.get_save_path()

            # إذا لم يكن هناك مسار تلقائي، اطلب من المستخدم اختيار مجلد
            if not output_dir:
                output_dir = self.file_manager.select_directory("اختيار مجلد الحفظ")

            if output_dir:
                # التأكد من وجود المجلد
                if not os.path.exists(output_dir):
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                    except Exception as e:
                        self.message_manager.show_error(f"فشل في إنشاء مجلد الحفظ: {str(e)}")
                        return False

                success = self.split_module.split_pdf_advanced(file, output_dir)

                if success:
                    page.notification_manager.show_notification(f"{tr('split_completed_successfully')}\n{tr('pages_saved_in')}: {output_dir}", "success", duration=4000)
                    page.file_list_frame.clear_all_files()
                    # إخفاء التخطيط الكامل بعد النجاح
                    if hasattr(page, 'save_and_split_widget'):
                        page.save_and_split_widget.setVisible(False)
                    return True
                else:
                    page.notification_manager.show_notification(tr("split_failed"), "error", duration=4000)
                    return False

        except Exception as e:
            page.notification_manager.show_notification(f"{tr('split_error')}: {str(e)}", "error")
            return False

    def compress_files(self, page):
        """تنفيذ عملية ضغط الملفات"""
        try:
            files = page.selected_files
            if not files:
                page.notification_manager.show_notification(tr("select_one_file_message"), "warning")
                return False

            from modules import settings
            settings_data = settings.load_settings()
            
            # الحصول على مستوى الضغط من الواجهة
            compression_level = page.get_batch_compression_level()

            for file in files:
                output = self.file_manager.get_output_path_with_settings(
                    settings_data,
                    f"compressed_{os.path.basename(file)}"
                )

                if output:
                    success = self.compress_module.compress_pdf(file, output, compression_level)
                    if success:
                        page.notification_manager.show_notification(f"{tr('file_compressed_successfully')}: {os.path.basename(file)}", "success", duration=4000)
                    else:
                        page.notification_manager.show_notification(f"{tr('compress_failed')}: {os.path.basename(file)}", "error", duration=4000)
                        return False

            page.clear_files()
            return True

        except Exception as e:
            page.notification_manager.show_notification(f"{tr('compress_error')}: {str(e)}", "error")
            return False

    def rotate_files(self, page, angle=90):
        """تنفيذ عملية تدوير الملفات"""
        try:
            files = page.file_list_frame.get_valid_files()
            if not files:
                self.message_manager.show_error("يجب اختيار ملف واحد على الأقل للتدوير")
                return False

            from modules import settings
            settings_data = settings.load_settings()

            for file in files:
                output = self.file_manager.get_output_path_with_settings(
                    settings_data,
                    f"rotated_{os.path.basename(file)}"
                )

                if output:
                    success = self.rotate_module.rotate_pdf(file, output, angle)
                    if success:
                        self.message_manager.show_success(f"تم تدوير الملف {os.path.basename(file)} بزاوية {angle} درجة بنجاح!")
                    else:
                        self.message_manager.show_error(f"فشل في تدوير الملف {os.path.basename(file)}.")
                        return False

            page.file_list_frame.clear_all_files()
            return True

        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def pdf_to_images(self, files, output_dir):
        """تحويل PDF إلى صور"""
        try:
            # يفترض أن files تحتوي على ملف واحد فقط لهذه العملية
            if not files or len(files) != 1:
                self.message_manager.show_error("يجب تحديد ملف PDF واحد فقط.")
                return False
            
            success = self.convert_module.pdf_to_images(files[0], output_dir)
            if success:
                return True
            else:
                self.message_manager.show_error("فشل في تحويل PDF إلى صور.")
                return False
        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def images_to_pdf(self, files, output_path):
        """تحويل صور إلى PDF"""
        try:
            if not files:
                self.message_manager.show_error("يجب تحديد صورة واحدة على الأقل.")
                return False

            success = self.convert_module.images_to_pdf(files, output_path)
            if success:
                return True
            else:
                self.message_manager.show_error("فشل في تحويل الصور إلى PDF.")
                return False
        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def pdf_to_text(self, files, output_path):
        """استخراج النص من PDF"""
        try:
            if not files or len(files) != 1:
                self.message_manager.show_error("يجب تحديد ملف PDF واحد فقط.")
                return False

            success = self.convert_module.pdf_to_text(files[0], output_path)
            if success:
                return True
            else:
                self.message_manager.show_error("فشل في استخراج النص من PDF.")
                return False
        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def text_to_pdf(self, files, output_path):
        """تحويل نص إلى PDF"""
        try:
            if not files or len(files) != 1:
                self.message_manager.show_error("يجب تحديد ملف نصي واحد فقط.")
                return False

            success = self.convert_module.text_to_pdf(files[0], output_path, 12)
            if success:
                return True
            else:
                self.message_manager.show_error("فشل في تحويل النص إلى PDF.")
                return False
        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def _check_pywin32_available(self):
        """فحص توفر pywin32 بهدوء"""
        try:
            import win32print
            return True
        except ImportError:
            return False

    def get_available_printers(self):
        """الحصول على قائمة بأسماء الطابعات المتاحة"""
        try:
            import win32print
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            printer_names = [printer[2] for printer in printers]

            return printer_names if printer_names else ["Microsoft Print to PDF"]

        except ImportError:
            # تسجيل الخطأ بهدوء بدون إظهار رسائل للمستخدم
            from modules.logger import debug
            debug("pywin32 غير متوفر - استخدام طابعة افتراضية")
            return ["Microsoft Print to PDF"]  # طابعة افتراضية

        except Exception as e:
            from modules.logger import warning
            warning(f"فشل في جلب قائمة الطابعات: {str(e)}")

            # عرض تحذير بسيط
            try:
                self.message_manager.show_warning(f"تحذير: لا يمكن الوصول لجميع الطابعات")
            except:
                print(f"تحذير: مشكلة في الطابعات - {str(e)}")

            return ["Microsoft Print to PDF"]  # طابعة افتراضية

    def print_files(self, files, printer_name=None, parent_widget=None):
        """طباعة ملفات PDF المحددة مع إظهار حوار التقدم"""
        if not files:
            self.message_manager.show_error("لم يتم تحديد ملفات للطباعة.")
            return False

        try:
            import win32api
            import time
            from PySide6.QtWidgets import QProgressDialog, QApplication
            from PySide6.QtCore import Qt

            progress = QProgressDialog(parent_widget)
            progress.setWindowTitle("جاري الطباعة")
            progress.setLabelText("التحضير للطباعة...")
            progress.setRange(0, len(files))
            progress.setModal(True)
            progress.setCancelButtonText("إلغاء")
            progress.show()

            for i, file_path in enumerate(files):
                if progress.wasCanceled():
                    break
                
                progress.setValue(i)
                progress.setLabelText(f"طباعة ملف: {os.path.basename(file_path)} ({i+1} من {len(files)})")
                QApplication.processEvents()

                try:
                    if printer_name:
                        win32api.ShellExecute(0, "printto", file_path, f'"{printer_name}"', ".", 0)
                    else:
                        win32api.ShellExecute(0, "print", file_path, None, ".", 0)
                    time.sleep(2)  # انتظر قليلاً لإرسال المهمة
                except Exception as e:
                    self.message_manager.show_error(f"فشل في طباعة الملف {os.path.basename(file_path)}: {e}")
                    progress.close()
                    return False
            
            progress.setValue(len(files))
            if not progress.wasCanceled():
                self.message_manager.show_success("تم إرسال جميع الملفات إلى طابور الطباعة بنجاح.")
            
            return True

        except ImportError:
            # إظهار رسالة خطأ فقط عند الطباعة الفعلية
            error_msg = """مكتبة pywin32 غير مثبتة أو لا تعمل بشكل صحيح.

لحل هذه المشكلة:
1. افتح موجه الأوامر كمدير
2. نفذ: pip install pywin32

إذا استمرت المشكلة:
pip uninstall pywin32
pip install pywin32==306"""

            self.message_manager.show_error(error_msg)
            return False
        except Exception as e:
            from modules.logger import error
            error(f"خطأ غير متوقع أثناء الطباعة: {str(e)}")
            self.message_manager.show_error(f"حدث خطأ غير متوقع أثناء الطباعة:\n{str(e)}")
            return False

    def get_output_path(self, file_path, suffix):
        """إنشاء مسار إخراج افتراضي مع لاحقة مخصصة"""
        dir_name, file_name = os.path.split(file_path)
        base_name, ext = os.path.splitext(file_name)
        return os.path.join(dir_name, f"{base_name}{suffix}{ext}")

    def get_pdf_properties(self, file_path):
        """الحصول على خصائص ملف PDF"""
        try:
            return self.security_module.get_pdf_metadata(file_path)
        except Exception as e:
            self.message_manager.show_error(f"فشل في قراءة خصائص الملف: {e}")
            return None

    def encrypt_pdf(self, file_path, output_path, password, owner_password, permissions):
        """تشفير ملف PDF"""
        try:
            success = self.security_module.encrypt_pdf(file_path, output_path, password, owner_password, permissions)
            if success:
                self.message_manager.show_success(f"تم تشفير الملف بنجاح!\nحُفظ في: {output_path}")
            else:
                self.message_manager.show_error("فشل تشفير الملف.")
        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ أثناء التشفير: {e}")

    def decrypt_pdf(self, file_path, output_path, password):
        """فك تشفير ملف PDF"""
        try:
            success = self.security_module.decrypt_pdf(file_path, output_path, password)
            if success:
                self.message_manager.show_success(f"تم فك تشفير الملف بنجاح!\nحُفظ في: {output_path}")
            else:
                self.message_manager.show_error("فشل فك تشفير الملف. تأكد من كلمة المرور.")
        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ أثناء فك التشفير: {e}")

    def update_pdf_properties(self, file_path, output_path, properties):
        """تحديث خصائص ملف PDF"""
        try:
            success = self.security_module.update_pdf_metadata(file_path, output_path, properties)
            if success:
                self.message_manager.show_success(f"تم تحديث خصائص الملف بنجاح!\nحُفظ في: {output_path}")
            else:
                self.message_manager.show_error("فشل تحديث خصائص الملف.")
        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ أثناء تحديث الخصائص: {e}")


def show_warning_message(parent, message):
    """عرض رسالة تحذير"""
    return QMessageBox.warning(parent, "تحذير", message, QMessageBox.Yes | QMessageBox.No)


def browse_folder_simple(title="اختر مجلدًا"):
    """
    فتح نافذة اختيار مجلد بسيطة باستخدام QFileDialog

    Args:
        title: عنوان النافذة

    Returns:
        str: مسار المجلد المختار أو None إذا تم الإلغاء
    """
    try:
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtCore import Qt
        import os

        full_title = f"ApexFlow - {title}"
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")

        # إنشاء نافذة حوار اختيار المجلد
        dialog = QFileDialog()
        dialog.setWindowTitle(full_title)
        dialog.setDirectory(default_dir)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        # جعل النافذة تظهر فوق الكل وتعطل الوصول للنافذة الرئيسية
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)

        if dialog.exec_() == QFileDialog.Accepted:
            return dialog.selectedFiles()[0] if dialog.selectedFiles() else None
        return None

    except Exception:
        # في حالة فشل QFileDialog، إرجاع None
        return None
