"""
العناصر الذكية التي تستمع لتغييرات السمة
Theme-Aware Widgets that automatically respond to theme changes
"""

from PySide6.QtWidgets import QWidget, QDialog, QMainWindow
from PySide6.QtCore import QObject
from modules.logger import debug, info, warning, error
from .theme_manager import global_theme_manager

class ThemeAwareWidget(QObject):
    """كلاس أساسي لكل عنصر يريد أن يكون جزء من فريق السمات"""
    
    def __init__(self, widget, widget_type="default"):
        super().__init__()
        self.widget = widget
        self.widget_type = widget_type
        
        # تسجيل تلقائي في الفريق
        global_theme_manager.register_widget(widget, widget_type)
        
        # استمع للتغييرات
        global_theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # طبق السمة الحالية
        self.apply_current_theme()
        
        debug(f"عضو جديد في الفريق: {widget_type}")

    def on_theme_changed(self, theme_name, accent_color, options):
        """ماذا أفعل عند تغيير السمة؟"""
        debug(f"{self.widget_type}: استلمت إشارة تغيير السمة إلى {theme_name}")
        self.apply_theme(theme_name, accent_color, options)
    
    def apply_theme(self, theme_name, accent_color, options):
        """كل عنصر يعرف كيف يطبق السمة على نفسه"""
        try:
            from .theme_manager import apply_theme_style
            apply_theme_style(
                self.widget, self.widget_type, auto_register=False
            )
            debug(f"{self.widget_type}: تم تطبيق السمة {theme_name}")
        except Exception as e:
            error(f"{self.widget_type}: خطأ في تطبيق السمة: {e}")
    
    def apply_current_theme(self):
        """تطبيق السمة الحالية"""
        self.apply_theme(
            global_theme_manager.current_theme,
            global_theme_manager.current_accent,
            {}  # خيارات فارغة افتراضياً
        )
    
    def __del__(self):
        """إلغاء التسجيل عند الحذف"""
        try:
            global_theme_manager.unregister_widget(self.widget)
        except:
            pass

class ThemeAwareMainWindow(QMainWindow):
    """نافذة رئيسية ذكية"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme_handler = ThemeAwareWidget(self, "main_window")
    
    def closeEvent(self, event):
        """تنظيف عند الإغلاق"""
        try:
            global_theme_manager.unregister_widget(self)
        except:
            pass
        super().closeEvent(event)

class ThemeAwareDialog(QDialog):
    """حوار ذكي"""
    
    def __init__(self, parent=None, widget_type="dialog"):
        super().__init__(parent)
        self.theme_handler = ThemeAwareWidget(self, widget_type)
    
    def closeEvent(self, event):
        """تنظيف عند الإغلاق"""
        try:
            global_theme_manager.unregister_widget(self)
        except:
            pass
        super().closeEvent(event)

class ThemeAwareWidget_Simple(QWidget):
    """عنصر بسيط ذكي"""
    
    def __init__(self, parent=None, widget_type="default"):
        super().__init__(parent)
        self.theme_handler = ThemeAwareWidget(self, widget_type)
    
    def closeEvent(self, event):
        """تنظيف عند الإغلاق"""
        try:
            global_theme_manager.unregister_widget(self)
        except:
            pass
        super().closeEvent(event)

def make_theme_aware(widget, widget_type="default"):
    """تحويل أي عنصر موجود إلى عنصر ذكي"""
    return ThemeAwareWidget(widget, widget_type)

def apply_theme_to_widget(widget, widget_type="default"):
    """تطبيق السمة على عنصر مباشرة"""
    from .theme_manager import apply_theme_style
    return apply_theme_style(widget, widget_type, auto_register=False)