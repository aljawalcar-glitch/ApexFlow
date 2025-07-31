import weakref
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal
from modules.settings import load_settings, set_setting  # استيراد مباشر لتجنب تحميل وحدات PDF
from modules.logger import debug, info, warning, error
from .global_styles import get_widget_style, darken_color

class GlobalThemeManager(QObject):
    """
    مدير السمات المركزي والمبسط.
    - يدير السمة الحالية واللون المميز.
    - يخبر العناصر المسجلة عند حدوث تغيير.
    """
    theme_changed = Signal(str, str, dict)  # theme_name, accent_color, options

    def __init__(self):
        super().__init__()

        # تهيئة القيم الافتراضية أولاً
        self.current_theme = "dark"
        self.current_accent = "#ff6f00"
        self.current_options = {}  # خيارات إضافية للسمة

        # قاموس مركزي وموحد لجميع السمات
        self.themes = {
            "dark": {
                "bg": "#1a202c", "surface": "#2d3748", "border": "#4a5568",
                "text_title": "#ffffff", "text_body": "#ffffff", "text_secondary": "#a0aec0",
                "text_muted": "#718096", "text_accent": "#ff6f00", "text": "#ffffff"
            },
            "light": {
                "bg": "#ffffff", "surface": "#f7fafc", "border": "#e2e8f0",
                "text_title": "#000000", "text_body": "#000000", "text_secondary": "#4a5568",
                "text_muted": "#718096", "text_accent": "#ff6f00", "text": "#000000"
            },
            "blue": {
                "bg": "#1a2332", "surface": "#2a4365", "border": "#4a5568",
                "text_title": "#ffffff", "text_body": "#ffffff", "text_secondary": "#a0aec0",
                "text_muted": "#718096", "text_accent": "#3182ce", "text": "#ffffff"
            },
            "green": {
                "bg": "#1a3221", "surface": "#275432", "border": "#3f684a",
                "text_title": "#ffffff", "text_body": "#ffffff", "text_secondary": "#a0aec0",
                "text_muted": "#718096", "text_accent": "#38a169", "text": "#ffffff"
            },
            "purple": {
                "bg": "#2c1a32", "surface": "#4d2a54", "border": "#6b3f72",
                "text_title": "#ffffff", "text_body": "#ffffff", "text_secondary": "#a0aec0",
                "text_muted": "#718096", "text_accent": "#805ad5", "text": "#ffffff"
            }
        }

        self.registered_widgets = []  # قائمة المراجع الضعيفة للعناصر المسجلة
        self.load_theme_from_settings()

    def load_theme_from_settings(self):
        """تحميل السمة من الإعدادات عند بدء التشغيل."""
        try:
            settings_data = load_settings()
            self.current_theme = settings_data.get("theme", "dark")
            self.current_accent = settings_data.get("accent_color", "#ff6f00")
            # تحديث اللون المميز في قواميس السمات
            for theme_data in self.themes.values():
                theme_data["text_accent"] = self.current_accent
        except Exception as e:
            print(f"خطأ في تحميل السمة: {e}")
            self.current_theme = "dark"
            self.current_accent = "#ff6f00"

    def apply_theme(self, widget, widget_type="default"):
        """تطبيق السمة الموحدة على أي عنصر"""
        apply_theme_style(widget, widget_type, auto_register=False)

    def get_current_colors(self):
        """الحصول على قاموس الألوان للسمة الحالية."""
        return self.themes.get(self.current_theme, self.themes["dark"])

    def change_theme(self, theme_name, accent_color=None, options=None):
        """تغيير السمة الحالية وإعلام جميع العناصر المسجلة."""
        if theme_name in self.themes:
            self.current_theme = theme_name

        if accent_color:
            self.current_accent = accent_color
            # تحديث اللون المميز في كل السمات
            for theme_data in self.themes.values():
                theme_data["text_accent"] = self.current_accent

        # حفظ الخيارات الإضافية إذا تم تمريرها
        if options:
            self.current_options = options

        print(f"تغيير السمة إلى: {self.current_theme}, اللون المميز: {self.current_accent}")
        if options:
            print(f"خيارات إضافية: {options}")

        # Clean up dead references before emitting the signal
        self.registered_widgets = [ref for ref in self.registered_widgets if ref["widget"]()]

        self.theme_changed.emit(self.current_theme, self.current_accent, self.current_options)
        self.save_theme_to_settings()

    def register_widget(self, widget: QWidget, widget_type: str):
        """تسجيل عنصر لتحديثات السمة المستقبلية باستخدام المراجع الضعيفة."""
        # تجنب التكرار
        if not any(w['widget']() == widget for w in self.registered_widgets):
            widget_ref = weakref.ref(widget)
            self.registered_widgets.append({
                "widget": widget_ref,
                "type": widget_type
            })

            def on_theme_change(theme_name, accent_color, options):
                w = widget_ref()
                if w:
                    apply_theme_style(w, widget_type, auto_register=False)

            self.theme_changed.connect(on_theme_change)
            debug(f"تم تسجيل عنصر: {widget_type} للاستجابة لتغييرات السمة.")

    def save_theme_to_settings(self, theme_name: str = None, accent_color: str = None):
        """حفظ السمة الحالية في ملف الإعدادات."""
        try:
            # استخدام المعاملات المرسلة أو القيم الحالية
            theme_to_save = theme_name or self.current_theme
            accent_to_save = accent_color or self.current_accent

            set_setting("theme", theme_to_save)
            set_setting("accent_color", accent_to_save)
            debug(f"تم حفظ السمة في الإعدادات: {theme_to_save}, {accent_to_save}")
        except Exception as e:
            error(f"خطأ في حفظ السمة: {e}")

# --- المثيل المركزي ---
global_theme_manager = GlobalThemeManager()

# --- الدوال العامة للاستخدام في التطبيق ---
def apply_theme_style(widget: QWidget, widget_type: str = "default", auto_register: bool = True):
    """
    الدالة الموحدة والمبسطة لتطبيق النمط على أي عنصر.
    تعتمد على global_styles.py كمصدر وحيد للأنماط.
    """
    try:
        colors = global_theme_manager.get_current_colors()
        accent = global_theme_manager.current_accent
        
        style = get_widget_style(widget_type, colors, accent)
        widget.setStyleSheet(style)
        
        if auto_register:
            global_theme_manager.register_widget(widget, widget_type)
    
    except RuntimeError:
        # The widget was likely deleted. Ignore.
        pass
    except Exception as e:
        print(f"خطأ فادح في تطبيق السمة على {widget_type}: {e}")
        # نمط احتياطي في حالة الفشل
        try:
            widget.setStyleSheet("background-color: #1a202c; color: white;")
        except RuntimeError:
            pass # Widget deleted.
        
def make_theme_aware(widget: QWidget, widget_type: str):
    """
    تجعل العنصر يستجيب تلقائياً لتغييرات السمة.
    هي الطريقة الموصى بها لتسجيل العناصر.
    """
    # تطبيق النمط الأولي وتسجيل العنصر
    apply_theme_style(widget, widget_type, auto_register=True)

def refresh_all_fonts():
    """إعادة تطبيق الأنماط على جميع العناصر المسجلة عند تغيير الخطوط"""
    # This function now correctly triggers the change_theme method,
    # which handles the weak references properly.
    try:
        current_theme = global_theme_manager.current_theme
        current_accent = global_theme_manager.current_accent
        global_theme_manager.change_theme(current_theme, current_accent)
    except Exception as e:
        print(f"خطأ في إعادة تطبيق الخطوط: {e}")
    
# --- دوال وهياكل للتوافق مع الكود القديم ---
theme_manager = global_theme_manager
def apply_theme(widget, widget_type="default"):
    """دالة توافق لتطبيق السمة على أي عنصر."""
    apply_theme_style(widget, widget_type, auto_register=False)
class WindowManager:
    """مدير النوافذ الموحد - مسؤول عن جميع النوافذ والحوارات"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.app_title = "ApexFlow - أداة معالجة ملفات PDF"
        self.app_icon = "assets/icon.png"

    def set_window_properties(self, window, title_suffix=""):
        """تطبيق خصائص موحدة على النافذة"""
        full_title = f"ApexFlow - {title_suffix}" if title_suffix else "ApexFlow"
        window.setWindowTitle(full_title)

        # تطبيق الأيقونة
        try:
            from PySide6.QtGui import QIcon
            window.setWindowIcon(QIcon(self.app_icon))
        except:
            pass

        # تطبيق السمة الموحدة
        apply_theme(window, "dialog")

    def create_file_dialog(self, dialog_type, title, file_filter="", directory=""):
        """إنشاء حوار ملفات موحد"""
        from PySide6.QtWidgets import QFileDialog

        full_title = f"ApexFlow - {title}"

        if dialog_type == "open_file":
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                full_title,
                directory,
                file_filter
            )
            return file_path

        elif dialog_type == "open_files":
            file_paths, _ = QFileDialog.getOpenFileNames(
                self.main_window,
                full_title,
                directory,
                file_filter
            )
            return file_paths

        elif dialog_type == "save_file":
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                full_title,
                directory,
                file_filter
            )
            return file_path

        return None

    def show_message(self, message_type, title, text, details=""):
        """عرض رسالة موحدة"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QIcon

        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(f"ApexFlow - {title}")
        msg_box.setText(text)

        if details:
            msg_box.setDetailedText(details)

        # تطبيق الأيقونة
        try:
            msg_box.setWindowIcon(QIcon(self.app_icon))
        except:
            pass

        # تحديد نوع الرسالة
        if message_type == "info":
            msg_box.setIcon(QMessageBox.Information)
        elif message_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif message_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        elif message_type == "question":
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # تطبيق السمة
        apply_theme(msg_box, "dialog")

        return msg_box.exec()
