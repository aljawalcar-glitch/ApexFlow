# -*- coding: utf-8 -*-
"""
نظام الأزرار مع أيقونات SVG
SVG Icon Button System
"""

import os
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import QSize, Qt
from PySide6.QtSvg import QSvgRenderer

class SVGIconButton(QPushButton):
    """
    زر مخصص مع أيقونات SVG قابلة للتخصيص
    Custom button with customizable SVG icons
    """
    
    def __init__(self, icon_name, size=24, tooltip="", theme="default", parent=None):
        super().__init__(parent)
        
        self.icon_name = icon_name
        self.icon_size = size
        self.icon_theme = theme
        
        # إعداد الزر
        # استخدام إعدادات التلميحات
        from src.utils.settings import should_show_tooltips
        if should_show_tooltips():
            self.setToolTip(tooltip)
        self.setIconSize(QSize(size, size))
        
        # تحميل الأيقونة
        self.load_icon("#ffffff") # تحميل الأيقونة باللون الأبيض الافتراضي

        # تطبيق نمط شفاف مثل أزرار الإعدادات
        # سيتم تحديث النمط لاحقًا باستخدام مدير السمات
        from src.managers.theme_manager import make_theme_aware
        make_theme_aware(self, "icon_button")
    
    def load_icon(self, color):
        """
        تحميل أيقونة SVG مع إمكانية تخصيص اللون
        Load SVG icon with color customization
        """
        icon_path = self.get_icon_path()
        
        if os.path.exists(icon_path):
            # إنشاء أيقونة ملونة من SVG
            colored_icon = self.create_colored_icon(icon_path, color)
            if colored_icon:
                self.setIcon(colored_icon)
                return True
        
        # fallback: نص بسيط
        self.setText(self.icon_name[:2].upper())
        return False
    
    def get_icon_path(self):
        """الحصول على مسار الأيقونة الصحيح سواء كان التطبيق مجمداً أم لا"""
        import sys

        # التحقق إذا كان التطبيق يعمل كملف تنفيذي
        if getattr(sys, 'frozen', False):
            # المسار داخل الملف التنفيذي
            base_path = os.path.join(sys._MEIPASS, "assets", "icons")
        else:
            # المسار في بيئة التطوير
            base_path = "assets/icons"

        # البحث عن الأيقونة بامتدادات مختلفة
        extensions = ['.svg', '.png', '.ico']
        
        # البحث في السمة المحددة أولاً
        for ext in extensions:
            icon_path = os.path.join(base_path, self.icon_theme, f"{self.icon_name}{ext}")
            if os.path.exists(icon_path):
                return icon_path
        
        # fallback إلى السمة الافتراضية
        for ext in extensions:
            icon_path = os.path.join(base_path, "default", f"{self.icon_name}{ext}")
            if os.path.exists(icon_path):
                return icon_path
        
        # إرجاع المسار الافتراضي حتى لو لم توجد الأيقونة
        return os.path.join(base_path, "default", f"{self.icon_name}.svg")
    
    def create_colored_icon(self, svg_path, color, size=None):
        """
        إنشاء أيقونة ملونة من ملف SVG
        Create colored icon from SVG file
        """
        try:
            # قراءة محتوى SVG
            with open(svg_path, 'r', encoding='utf-8') as file:
                svg_content = file.read()

            # استبدال currentColor باللون المطلوب
            svg_content = svg_content.replace('currentColor', color)

            # إنشاء QSvgRenderer
            renderer = QSvgRenderer()
            renderer.load(svg_content.encode('utf-8'))

            # استخدام الحجم الممرر أو حجم الزر الافتراضي
            icon_size = size if size is not None else self.icon_size
            # إنشاء QPixmap بالحجم المطلوب مباشرة
            pixmap = QPixmap(icon_size, icon_size)
            pixmap.fill(Qt.transparent)

            # رسم SVG على QPixmap بدقة عالية مع تحسينات إضافية
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing, True)  # تحسين جودة الحواف
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)  # تحسين جودة التحويل
            painter.setRenderHint(QPainter.TextAntialiasing, True)  # تحسين جودة النصوص
            painter.setRenderHint(QPainter.LosslessImageRendering, True)  # رسم بدون فقدان جودة
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)

        except Exception as e:
            print(f"خطأ في تحميل أيقونة SVG {svg_path}: {e}")
            return None
    
    def set_icon_color(self, color):
        """تغيير لون الأيقونة"""
        self.load_icon(color)
    
    def set_icon_theme(self, theme):
        """تغيير سمة الأيقونة"""
        self.icon_theme = theme
        # Re-apply all themes to reflect the change
        from src.managers.theme_manager import refresh_all_themes
        refresh_all_themes()

    def set_icon_name(self, icon_name):
        """تغيير أيقونة الزر"""
        self.icon_name = icon_name
        # Re-apply all themes to reflect the change
        from src.managers.theme_manager import refresh_all_themes
        refresh_all_themes()

# دوال مساعدة لإنشاء أزرار شائعة
def create_navigation_button(direction, size=24, tooltip=""):
    """إنشاء زر تنقل (التالي/السابق) مع لون السمة"""
    icon_name = "chevron-right" if direction == "next" else "chevron-left"
    default_tooltip = "التالي" if direction == "next" else "السابق"
    button = SVGIconButton(icon_name, size, tooltip or default_tooltip)
    # تطبيق السمة على الزر
    from src.managers.theme_manager import make_theme_aware
    make_theme_aware(button, "button")
    return button

def create_rotation_button(direction, size=24, tooltip=""):
    """إنشاء زر تدوير (يمين/يسار) مع لون السمة"""
    icon_name = "rotate-cw" if direction == "right" else "rotate-ccw"
    default_tooltip = "تدوير يمين" if direction == "right" else "تدوير يسار"
    button = SVGIconButton(icon_name, size, tooltip or default_tooltip)
    # السمة تطبق تلقائياً في constructor
    return button

def load_svg_icon(icon_name, size=24, color="#ffffff", theme="default"):
    """
    تحميل أيقونة SVG وإرجاعها كـ QPixmap
    Load SVG icon and return it as QPixmap
    """
    import sys
    import os
    from PySide6.QtGui import QPixmap, QPainter
    from PySide6.QtCore import Qt
    from PySide6.QtSvg import QSvgRenderer
    
    # التحقق أولاً مما إذا كان icon_name مسارًا كاملاً وموجودًا
    if os.path.exists(icon_name):
        icon_path = icon_name
    else:
        # الحصول على مسار الأيقونة
        if getattr(sys, 'frozen', False):
            # المسار داخل الملف التنفيذي
            base_path = os.path.join(sys._MEIPASS, "assets", "icons")
        else:
            # المسار في بيئة التطوير
            base_path = "assets/icons"
        
        # البحث عن الأيقونة بامتدادات مختلفة
        extensions = ['.svg', '.png', '.ico']
        icon_path = None
        
        # البحث في السمة المحددة أولاً
        for ext in extensions:
            test_path = os.path.join(base_path, theme, f"{icon_name}{ext}")
            if os.path.exists(test_path):
                icon_path = test_path
                break
        
        # fallback إلى السمة الافتراضية
        if not icon_path:
            for ext in extensions:
                test_path = os.path.join(base_path, "default", f"{icon_name}{ext}")
                if os.path.exists(test_path):
                    icon_path = test_path
                    break
        
        # إذا لم توجد، استخدم المسار الافتراضي
        if not icon_path:
            icon_path = os.path.join(base_path, "default", f"{icon_name}.svg")
    
    if not os.path.exists(icon_path):
        return None
    
    try:
        # قراءة محتوى SVG
        with open(icon_path, 'r', encoding='utf-8') as file:
            svg_content = file.read()
        
        # استبدال currentColor باللون المطلوب
        svg_content = svg_content.replace('currentColor', color)
        
        # إنشاء QSvgRenderer
        renderer = QSvgRenderer()
        renderer.load(svg_content.encode('utf-8'))
        
        # إنشاء QPixmap بالحجم المطلوب مباشرة لتجنب فقدان الجودة
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        # رسم SVG على QPixmap بدقة عالية مع تحسينات إضافية
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)  # تحسين جودة الحواف
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)  # تحسين جودة التحويل
        painter.setRenderHint(QPainter.TextAntialiasing, True)  # تحسين جودة النصوص
        painter.setRenderHint(QPainter.LosslessImageRendering, True)  # رسم بدون فقدان جودة
        renderer.render(painter)
        painter.end()
        
        return pixmap
    
    except Exception as e:
        print(f"خطأ في تحميل أيقونة SVG {icon_path}: {e}")
        return None


def create_action_button(action, size=24, text=""):
    """إنشاء زر إجراء (حفظ، حذف، إلخ) مع لون السمة"""
    from src.managers.theme_manager import make_theme_aware
    action_icons = {
        "save": "save",
        "delete": "trash-2",
        "reset": "refresh-cw",
        "add": "plus",
        "folder": "folder-open",
        "merge": "merge",
        "split": "scissors",
        "compress": "archive",
        "settings": "settings",
        "play": "play",
        "stamp": "stamp",
        "stamp-zoom-in": "stamp-zoom-in",
        "stamp-zoom-out": "stamp-zoom-out"
    }

    action_tooltips = {
        "save": "حفظ",
        "delete": "حذف",
        "reset": "إعادة تعيين",
        "add": "إضافة",
        "folder": "اختر ملف",
        "merge": "دمج",
        "split": "تقسيم",
        "compress": "ضغط",
        "settings": "إعدادات",
        "play": "تنفيذ",
        "stamp": "إضافة ختم",
        "stamp-zoom-in": "تكبير الختم",
        "stamp-zoom-out": "تصغير الختم"
    }

    icon_name = action_icons.get(action, action)
    default_tooltip = action_tooltips.get(action, action)
    button = SVGIconButton(icon_name, size, text or default_tooltip)

    # تطبيق لون خاص للأزرار الخطيرة وتسجيلها
    if action == "delete":
        make_theme_aware(button, "icon_button_danger")
    else:
        # تسجيل جميع الأزرار الأخرى
        make_theme_aware(button, "icon_button")

    return button


def create_colored_icon(icon_name, size=24, theme="default"):
    """
    إنشاء أيقونة ملونة باستخدام لون التمييز الحالي من السمة
    
    Args:
        icon_name: اسم الأيقونة (بدون امتداد)
        size: حجم الأيقونة بالبكسل
        theme: سمة الأيقونة (افتراضي: "default")
        
    Returns:
        QIcon: أيقونة ملونة
    """
    # الحصول على لون التمييز الحالي
    from src.managers.theme_manager import global_theme_manager
    accent_color = global_theme_manager.current_accent
    
    # الحصول على مسار الأيقونة
    import sys
    import os
    
    # التحقق أولاً مما إذا كان icon_name مسارًا كاملاً وموجودًا
    if os.path.exists(icon_name):
        icon_path = icon_name
    else:
        # الحصول على مسار الأيقونة
        if getattr(sys, 'frozen', False):
            # المسار داخل الملف التنفيذي
            base_path = os.path.join(sys._MEIPASS, "assets", "icons")
        else:
            # المسار في بيئة التطوير
            base_path = "assets/icons"

        # البحث عن الأيقونة بامتدادات مختلفة
        extensions = ['.svg', '.png', '.ico']
        icon_path = None
        
        # البحث في السمة المحددة أولاً
        for ext in extensions:
            test_path = os.path.join(base_path, theme, f"{icon_name}{ext}")
            if os.path.exists(test_path):
                icon_path = test_path
                break

        # fallback إلى السمة الافتراضية
        if not icon_path:
            for ext in extensions:
                test_path = os.path.join(base_path, "default", f"{icon_name}{ext}")
                if os.path.exists(test_path):
                    icon_path = test_path
                    break
        
        # إذا لم توجد، استخدم المسار الافتراضي
        if not icon_path:
            icon_path = os.path.join(base_path, "default", f"{icon_name}.svg")
    
    # إنشاء زر وهمي للوصول إلى دوال إنشاء الأيقونات
    dummy_button = SVGIconButton(icon_name, size, theme=theme)
    
    # إنشاء الأيقونة الملونة بالحجم المطلوب
    icon_path = dummy_button.get_icon_path()
    return dummy_button.create_colored_icon(icon_path, accent_color, size)

def create_themed_icon(icon_name, size=24, color=None, theme="default"):
    """
    إنشاء أيقونة ملونة باستخدام لون محدد أو لون التمييز الحالي
    
    Args:
        icon_name: اسم الأيقونة (بدون امتداد)
        size: حجم الأيقونة بالبكسل
        color: اللون المطلوب (اختياري، افتراضيًا لون التمييز)
        theme: سمة الأيقونة (افتراضي: "default")
        
    Returns:
        QIcon: أيقونة ملونة
    """
    # الحصول على اللون
    if color is None:
        from src.managers.theme_manager import global_theme_manager
        color = global_theme_manager.current_accent
    
    # إنشاء زر وهمي للوصول إلى دوال إنشاء الأيقونات
    dummy_button = SVGIconButton(icon_name, size, theme=theme)
    
    # إنشاء الأيقونة الملونة بالحجم المطلوب
    icon_path = dummy_button.get_icon_path()
    return dummy_button.create_colored_icon(icon_path, color, size)
