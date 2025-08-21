import weakref
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QPushButton
from PySide6.QtCore import QObject, Signal, QEvent
from src.utils.settings import load_settings, update_setting
from src.utils.logger import error

class ThemeAwareFilter(QObject):
    """فلتر لمراقبة ظهور أي ويدجت جديد وتسجيله تلقائياً كنص."""
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show:
            # تسجيل تلقائي للعناصر الشائعة كـ "نص"
            if isinstance(obj, (QLabel, QPushButton)):
                if not global_theme_manager.is_registered(obj):
                    global_theme_manager.register_widget(obj, "text")
        return super().eventFilter(obj, event)

class GlobalThemeManager(QObject):
    """
    مدير السمات المركزي (Singleton).
    - يطبق السمة على جميع العناصر المسجلة دفعة واحدة.
    - يرسل إشارة theme_changed للاستماع الخارجي.
    """
    theme_changed = Signal(str, str, dict)
    _instance = None

    def __init__(self):
        super().__init__()
        if GlobalThemeManager._instance is not None:
            raise RuntimeError("استخدم GlobalThemeManager.instance() بدلاً من إنشاء نسخة جديدة")
        GlobalThemeManager._instance = self

        self.current_theme = "blue"
        self.current_accent = "#056a51"
        self.current_options = {}

        self.themes = {
            "dark": {
                "bg": "#1a202c", "surface": "#2d3748", "border": "#4a5568",
                "text": "#ffffff", "text_title": "#ffffff", "text_body": "#ffffff", 
                "text_secondary": "#a0aec0", "text_muted": "#718096", "text_accent": "#ff6f00",
                "success": "#4ade80", "warning": "#fbbf24", "error": "#f87171",
                "toggle_bg_color": "#4a5568", "toggle_circle_color": "#ffffff", "toggle_active_color": "#ff6f00"
            },
            "light": {
                "bg": "#ffffff", "surface": "#f7fafc", "border": "#e2e8f0",
                "text": "#000000", "text_title": "#000000", "text_body": "#000000",
                "text_secondary": "#4a5568", "text_muted": "#718096", "text_accent": "#ff6f00",
                "success": "#2dd4bf", "warning": "#facc15", "error": "#f43f5e",
                "toggle_bg_color": "#e2e8f0", "toggle_circle_color": "#ffffff", "toggle_active_color": "#ff6f00"
            },
            "blue": {
                "bg": "#1a2332", "surface": "#2a4365", "border": "#4a5568",
                "text": "#ffffff", "text_title": "#ffffff", "text_body": "#ffffff",
                "text_secondary": "#a0aec0", "text_muted": "#718096", "text_accent": "#056a51",
                "success": "#38a169", "warning": "#f59e0b", "error": "#ef4444",
                "toggle_bg_color": "#4a5568", "toggle_circle_color": "#ffffff", "toggle_active_color": "#056a51"
            },
            "green": {
                "bg": "#1a3221", "surface": "#275432", "border": "#3f684a",
                "text": "#ffffff", "text_title": "#ffffff", "text_body": "#ffffff",
                "text_secondary": "#a0aec0", "text_muted": "#718096", "text_accent": "#38a169",
                "success": "#4ade80", "warning": "#facc15", "error": "#f87171",
                "toggle_bg_color": "#3f684a", "toggle_circle_color": "#ffffff", "toggle_active_color": "#38a169"
            },
            "purple": {
                "bg": "#2c1a32", "surface": "#4d2a54", "border": "#6b3f72",
                "text": "#ffffff", "text_title": "#ffffff", "text_body": "#ffffff",
                "text_secondary": "#a0aec0", "text_muted": "#718096", "text_accent": "#805ad5",
                "success": "#a78bfa", "warning": "#f59e0b", "error": "#f43f5e",
                "toggle_bg_color": "#6b3f72", "toggle_circle_color": "#ffffff", "toggle_active_color": "#805ad5"
            }
        }

        self.registered_widgets = []

        app = QApplication.instance()
        if app:
            app.installEventFilter(ThemeAwareFilter())

        self.load_theme_from_settings()

    @staticmethod
    def instance():
        if GlobalThemeManager._instance is None:
            GlobalThemeManager()
        return GlobalThemeManager._instance

    def load_theme_from_settings(self):
        """تحميل السمة من ملف الإعدادات."""
        try:
            settings_data = load_settings()
            self.current_theme = settings_data.get("theme", "blue")
            self.current_accent = settings_data.get("accent_color", "#056a51")
            for theme_data in self.themes.values():
                theme_data["text_accent"] = self.current_accent
        except Exception as e:
            error(f"⚠️ خطأ في تحميل السمة: {e}")
            self.current_theme = "blue"
            self.current_accent = "#056a51"

    def get_color(self, role: str) -> str:
        """إرجاع اللون المخصص لدور معين في السمة الحالية."""
        theme_colors = self.themes.get(self.current_theme, self.themes["dark"])
        return theme_colors.get(role, "#000000") # Default to black if role not found

    def get_current_colors(self):
        """إرجاع قاموس الألوان للسمة الحالية. (للتوافق مع الأنماط القديمة)"""
        return self.themes.get(self.current_theme, self.themes["dark"])

    def is_registered(self, widget: QWidget):
        """التحقق إن كان الويدجت مسجلاً مسبقاً."""
        return any(w['widget']() == widget for w in self.registered_widgets)

    def register_widget(self, widget: QWidget, role: str):
        """تسجيل عنصر بدور محدد (e.g., 'text', 'background') لتطبيق السمة عليه."""
        if not self.is_registered(widget):
            self.registered_widgets.append({
                "widget": weakref.ref(widget),
                "role": role
            })
            self.apply_theme(widget, role)

    def change_theme(self, theme_name, accent_color=None, options=None):
        """تغيير السمة الحالية وتحديث كل العناصر المسجلة."""
        if theme_name in self.themes:
            self.current_theme = theme_name

        if accent_color:
            self.current_accent = accent_color
            for theme_data in self.themes.values():
                theme_data["text_accent"] = self.current_accent

        if options:
            self.current_options = options

        self.registered_widgets = [ref for ref in self.registered_widgets if ref["widget"]()]

        for ref in self.registered_widgets:
            w = ref["widget"]()
            if w:
                self.apply_theme(w, ref["role"])

        self.theme_changed.emit(self.current_theme, self.current_accent, self.current_options)

    def save_theme_to_settings(self, theme_name: str = None, accent_color: str = None):
        """حفظ السمة الحالية في ملف الإعدادات."""
        try:
            update_setting("theme", theme_name or self.current_theme)
            update_setting("accent_color", accent_color or self.current_accent)
            if self.current_options:
                update_setting("ui_settings", self.current_options)
        except Exception as e:
            error(f"خطأ في حفظ السمة: {e}")

    def apply_theme(self, widget: QWidget, role_or_type: str):
        """
        تطبيق النمط على عنصر واجهة معين.
        يدعم الأدوار الجديدة ('text', 'background', 'surface') والأنواع القديمة من global_styles.
        """
        from src.ui.widgets.global_styles import get_widget_style
        from PySide6.QtCore import Qt

        style = ""
        # التحقق من الأدوار الجديدة أولاً
        if role_or_type == "text":
            style = f"color: {self.get_color('text')};"
        elif role_or_type == "background":
            style = f"background-color: {self.get_color('background')};"
        elif role_or_type == "surface":
            style = f"background-color: {self.get_color('surface')}; border: 1px solid {self.get_color('border')};"
        elif role_or_type == "button":
            # تحديث الزر عند تغيير السمة
            try:
                # الحصول على اسم الأيقونة من خاصية مخصصة (إذا كان زر أيقونة)
                icon_name = widget.property("icon_name")
                if icon_name:
                    from src.ui.widgets.svg_icon_button import create_colored_icon
                    # الحصول على حجم الأيقونة من خاصية مخصصة أو استخدام القيمة الافتراضية
                    icon_size = widget.property("icon_size") or 24
                    # إنشاء أيقونة ملونة جديدة وتعيينها للزر
                    colored_icon = create_colored_icon(icon_name, icon_size)
                    if colored_icon:
                        widget.setIcon(colored_icon)
            except Exception as e:
                error(f"خطأ في تحديث أيقونة الزر: {e}")
        
        try:
            if style:  # إذا كان دورًا بسيطًا، قم بتطبيقه مباشرة
                current_style = widget.styleSheet()
                if "color:" in current_style and role_or_type == "text":
                    import re
                    current_style = re.sub(r'color\s*:\s*#[0-9a-fA-F]{3,6}\s*;', '', current_style)
                widget.setStyleSheet(current_style + style)
            else:  # إذا لم يكن دورًا بسيطًا، افترض أنه نوع ويدجت قديم
                colors = self.get_current_colors()
                accent = self.current_accent
                style = get_widget_style(role_or_type, colors, accent)
                widget.setStyleSheet(style)

            # دعم الشفافية للعناصر الخاصة
            if role_or_type in ["buttons_transparent", "settings_page", "transparent_container", "group_box"]:
                widget.setAttribute(Qt.WA_TranslucentBackground, True)

            # تحديث وتلميع لضمان تطبيق النمط فوراً
            widget.style().unpolish(widget)
            widget.style().polish(widget)

        except RuntimeError:
            pass  # الويدجت تم حذفه
        except Exception as e:
            error(f"⚠️ خطأ في تطبيق السمة على {widget.objectName()} بدور '{role_or_type}': {e}")


global_theme_manager = GlobalThemeManager.instance()

def make_theme_aware(widget: QWidget, role: str):
    """تسجيل عنصر بحيث يتأثر دائماً بتغييرات السمة."""
    global_theme_manager.register_widget(widget, role)

def refresh_all_themes():
    """إعادة تحميل السمة من الإعدادات وتطبيقها على جميع العناصر."""
    try:
        manager = GlobalThemeManager.instance()
        manager.load_theme_from_settings()
        manager.change_theme(manager.current_theme, manager.current_accent)
    except Exception as e:
        error(f"خطأ في تحديث السمات: {e}")
