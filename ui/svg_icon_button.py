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
        from modules.settings import should_show_tooltips
        if should_show_tooltips():
            self.setToolTip(tooltip)
        self.setIconSize(QSize(size, size))
        
        # تحميل الأيقونة
        self.load_icon()

        # تطبيق نمط شفاف مثل أزرار الإعدادات
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 8px;
                border-radius: 6px;
                min-width: 32px;
                min-height: 32px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:disabled {
                opacity: 0.4;
                background: rgba(102, 102, 102, 0.1);
            }
        """)
    
    def load_icon(self, color="#ffffff"):
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

        icon_path = os.path.join(base_path, self.icon_theme, f"{self.icon_name}.svg")
        
        # fallback إلى السمة الافتراضية
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_path, "default", f"{self.icon_name}.svg")
        
        return icon_path
    
    def create_colored_icon(self, svg_path, color):
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

            # إنشاء QPixmap بحجم مضاعف ثم تصغيره لتحسين الدقة
            high_dpi_size = self.icon_size * 2
            pixmap = QPixmap(high_dpi_size, high_dpi_size)
            pixmap.fill(Qt.transparent)

            # رسم SVG على QPixmap بدقة عالية
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing, True)  # تحسين جودة الحواف
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)  # تحسين جودة التحويل
            renderer.render(painter)
            painter.end()
            
            # تصغير الصورة للحجم الأصلي مع الحفاظ على الجودة
            final_pixmap = pixmap.scaled(
                self.icon_size, self.icon_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            return QIcon(final_pixmap)

        except Exception as e:
            print(f"خطأ في تحميل أيقونة SVG {svg_path}: {e}")
            return None
    
    def apply_icon_button_style(self, theme_color=None):
        """تطبيق نمط الزر مع الأيقونة - شفاف مثل أزرار الإعدادات"""
        # خلفية شفافة بدون أي لون (مثل أزرار الإعدادات)
        hover_bg = "rgba(255, 255, 255, 0.1)"      # أبيض شفاف للتمرير
        pressed_bg = "rgba(255, 255, 255, 0.2)"    # أبيض شفاف للضغط
        hover_border = "rgba(255, 255, 255, 0.3)"  # حدود بيضاء شفافة
        pressed_border = "rgba(255, 255, 255, 0.4)" # حدود بيضاء شفافة

        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: transparent;
                padding: 8px;
                border-radius: 6px;
                min-width: 32px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
                border: 1px solid {hover_border};
            }}
            QPushButton:pressed {{
                background: {pressed_bg};
                border: 1px solid {pressed_border};
            }}
            QPushButton:disabled {{
                opacity: 0.4;
                background: rgba(102, 102, 102, 0.1);
            }}
        """)
    
    def set_icon_color(self, color):
        """تغيير لون الأيقونة"""
        self.load_icon(color)
    
    def set_icon_theme(self, theme):
        """تغيير سمة الأيقونة"""
        self.icon_theme = theme
        self.load_icon()

    def hex_to_rgba(self, hex_color, alpha):
        """تحويل لون hex إلى rgba مع شفافية"""
        try:
            # إزالة # إذا كانت موجودة
            hex_color = hex_color.lstrip('#')

            # تحويل إلى RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            return f"rgba({r}, {g}, {b}, {alpha})"
        except:
            # fallback في حالة خطأ
            return f"rgba(255, 111, 0, {alpha})"

    def update_theme_colors(self, theme_color=None):
        """تحديث ألوان السمة للزر - شفاف مثل الإعدادات"""
        # لا تفعل شيء - الأزرار شفافة بالافتراض
        pass

# دوال مساعدة لإنشاء أزرار شائعة
def create_navigation_button(direction, size=24, tooltip=""):
    """إنشاء زر تنقل (التالي/السابق) مع لون السمة"""
    icon_name = "chevron-right" if direction == "next" else "chevron-left"
    default_tooltip = "التالي" if direction == "next" else "السابق"
    button = SVGIconButton(icon_name, size, tooltip or default_tooltip)
    # السمة تطبق تلقائياً في constructor
    return button

def create_rotation_button(direction, size=24, tooltip=""):
    """إنشاء زر تدوير (يمين/يسار) مع لون السمة"""
    icon_name = "rotate-cw" if direction == "right" else "rotate-ccw"
    default_tooltip = "تدوير يمين" if direction == "right" else "تدوير يسار"
    button = SVGIconButton(icon_name, size, tooltip or default_tooltip)
    # السمة تطبق تلقائياً في constructor
    return button

def create_action_button(action, size=24, tooltip=""):
    """إنشاء زر إجراء (حفظ، حذف، إلخ) مع لون السمة"""
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
    button = SVGIconButton(icon_name, size, tooltip or default_tooltip)

    # تطبيق لون خاص للأزرار الخطيرة
    if action == "delete":
        button.set_icon_color("#dc3545")  # أحمر للحذف
        button.apply_icon_button_style("#dc3545")  # خلفية حمراء شفافة
    # السمة تطبق تلقائياً في constructor للأزرار العادية

    return button

# دالة عامة لتحديث جميع الأزرار عند تغيير السمة
def update_all_theme_buttons(parent_widget, new_theme_color=None):
    """تحديث جميع أزرار الأيقونات في widget معين عند تغيير السمة"""
    if new_theme_color is None:
        try:
            from .theme_manager import global_theme_manager
            current_theme = global_theme_manager.get_current_theme()
            new_theme_color = current_theme.get('accent_color', '#ff6f00')
        except:
            new_theme_color = '#ff6f00'

    # البحث عن جميع أزرار SVGIconButton في الـ widget
    for child in parent_widget.findChildren(SVGIconButton):
        # تحديث الأزرار العادية فقط (ليس أزرار الحذف)
        if hasattr(child, 'icon_name') and child.icon_name != 'trash-2':
            child.update_theme_colors(new_theme_color)
