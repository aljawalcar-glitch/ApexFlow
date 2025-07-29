"""
وحدة الأدوات المساعدة للتطبيق
تحتوي على الدوال المساعدة للنظام والملفات والموارد
"""

import os
import psutil
from PySide6.QtWidgets import QMessageBox, QProgressDialog
from PySide6.QtCore import Qt

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

    def select_pdf_files(self, title="اختيار ملفات PDF", multiple=True):
        """اختيار ملفات PDF"""
        from PySide6.QtWidgets import QFileDialog
        import os

        full_title = f"ApexFlow - {title}"
        pdf_filter = "PDF Files (*.pdf)"
        # مجلد Documents كافتراضي
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")

        if multiple:
            files, _ = QFileDialog.getOpenFileNames(
                self.main_window,
                full_title,
                default_dir,
                pdf_filter
            )
            return files
        else:
            file, _ = QFileDialog.getOpenFileName(
                self.main_window,
                full_title,
                default_dir,
                pdf_filter
            )
            return file

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
                self.message_manager.show_error("يجب اختيار ملفين على الأقل للدمج")
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
                    self.message_manager.show_success(f"تم تقسيم الملف بنجاح!\nحُفظت الصفحات في: {output_dir}")
                    page.file_list_frame.clear_all_files()
                    # إخفاء التخطيط الكامل بعد النجاح
                    if hasattr(page, 'save_and_split_widget'):
                        page.save_and_split_widget.setVisible(False)
                    return True
                else:
                    self.message_manager.show_error("فشل في تقسيم الملف.")
                    return False

        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def compress_files(self, page):
        """تنفيذ عملية ضغط الملفات"""
        try:
            files = page.file_list_frame.get_valid_files()
            if not files:
                self.message_manager.show_error("يجب اختيار ملف واحد على الأقل للضغط")
                return False

            from modules import settings
            settings_data = settings.load_settings()
            
            # الحصول على مستوى الضغط من الواجهة
            compression_level = page.get_batch_compression_level(page.batch_compression_combo.currentText())

            for file in files:
                output = self.file_manager.get_output_path_with_settings(
                    settings_data,
                    f"compressed_{os.path.basename(file)}"
                )

                if output:
                    success = self.compress_module.compress_pdf(file, output, compression_level)
                    if success:
                        self.message_manager.show_success(f"تم ضغط الملف {os.path.basename(file)} بنجاح!")
                    else:
                        self.message_manager.show_error(f"فشل في ضغط الملف {os.path.basename(file)}.")
                        return False

            page.clear_files()
            return True

        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
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

    def pdf_to_images(self):
        """تحويل PDF إلى صور"""
        try:
            file = self.file_manager.select_pdf_files("اختيار ملف PDF للتحويل", multiple=False)
            if file:
                output_dir = self.file_manager.select_directory("اختيار مجلد حفظ الصور")
                if output_dir:
                    success = self.convert_module.pdf_to_images(file, output_dir)
                    if success:
                        self.message_manager.show_success("تم تحويل PDF إلى صور بنجاح!")
                        return True
                    else:
                        self.message_manager.show_error("فشل في تحويل PDF إلى صور.")
                        return False

        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def images_to_pdf(self):
        """تحويل صور إلى PDF"""
        try:
            files = self.file_manager.select_image_files("اختيار الصور للتحويل")
            if files:
                from modules import settings
                settings_data = settings.load_settings()
                output = self.file_manager.get_output_path_with_settings(settings_data, "images_to_pdf.pdf")

                if output:
                    success = self.convert_module.images_to_pdf(files, output)
                    if success:
                        self.message_manager.show_success("تم تحويل الصور إلى PDF بنجاح!")
                        return True
                    else:
                        self.message_manager.show_error("فشل في تحويل الصور إلى PDF.")
                        return False

        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def pdf_to_text(self):
        """استخراج النص من PDF"""
        try:
            file = self.file_manager.select_pdf_files("اختيار ملف PDF لاستخراج النص", multiple=False)
            if file:
                from modules.settings import load_settings
                settings_data = load_settings()
                output = self.file_manager.get_output_path_with_settings(settings_data, "extracted_text.txt")

                if output:
                    success = self.convert_module.pdf_to_text(file, output)
                    if success:
                        self.message_manager.show_success("تم استخراج النص من PDF بنجاح!")
                        return True
                    else:
                        self.message_manager.show_error("فشل في استخراج النص من PDF.")
                        return False

        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def text_to_pdf(self):
        """تحويل نص إلى PDF"""
        try:
            file = self.file_manager.select_text_file("اختيار ملف نصي للتحويل")
            if file:
                from modules import settings
                settings_data = settings.load_settings()
                output = self.file_manager.get_output_path_with_settings(settings_data, "text_to_pdf.pdf")

                if output:
                    success = self.convert_module.text_to_pdf(file, output, 12)
                    if success:
                        self.message_manager.show_success("تم تحويل النص إلى PDF بنجاح!")
                        return True
                    else:
                        self.message_manager.show_error("فشل في تحويل النص إلى PDF.")
                        return False

        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع: {str(e)}")
            return False

    def get_available_printers(self):
        """الحصول على قائمة بأسماء الطابعات المتاحة"""
        try:
            import win32print
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            return [printer[2] for printer in printers]
        except ImportError:
            self.message_manager.show_error("مكتبة pywin32 غير مثبتة. لا يمكن جلب قائمة الطابعات.")
            return []
        except Exception as e:
            self.message_manager.show_error(f"فشل في جلب قائمة الطابعات: {str(e)}")
            return []

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
            self.message_manager.show_error("مكتبة pywin32 غير مثبتة. لا يمكن تنفيذ الطباعة.")
            return False
        except Exception as e:
            self.message_manager.show_error(f"حدث خطأ غير متوقع أثناء الطباعة: {str(e)}")
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
    فتح نافذة اختيار مجلد بسيطة باستخدام tkinter

    Args:
        title: عنوان النافذة

    Returns:
        str: مسار المجلد المختار أو None إذا تم الإلغاء
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        # إنشاء نافذة مخفية
        root = tk.Tk()
        root.withdraw()

        # فتح نافذة اختيار المجلد
        folder = filedialog.askdirectory(
            title=title,
            initialdir=os.path.join(os.path.expanduser("~"), "Documents")
        )

        # تنظيف النافذة
        root.destroy()

        return folder if folder else None

    except Exception:
        # في حالة فشل tkinter، إرجاع None
        return None
