"""
Overlay Manager Module
Manages overlays and popups in the application
"""

from PySide6.QtCore import QObject


class OverlayManager(QObject):
    """مدير التراكبات للتعامل مع نافذة الإسقاط الذكية وغيرها من التراكبات"""

    def __init__(self, main_panel):
        """
        تهيئة مدير التراكبات

        Args:
            main_panel: البنل الرئيسي للتطبيق
        """
        super().__init__()
        self.main_panel = main_panel
        self.active_overlay = None  # التراكب النشط حاليًا

        # ربط إشارة تغيير الصفحة بدالة المعالجة
        if hasattr(self.main_panel, 'stack'):
            # استخدام QStackedWidget.currentChanged للتعامل مع تغيير الصفحة
            self.main_panel.stack.currentChanged.connect(self.on_page_changed)

    def show_overlay(self, overlay):
        """
        عرض تراكب جديد

        Args:
            overlay: كائن التراكب الذي سيتم عرضه
        """
        # إغلاق أي تراكب نشط حاليًا
        if self.active_overlay:
            self.active_overlay.close()

        # تعيين التراكب الجديد كتراكب نشط وعرضه
        self.active_overlay = overlay
        self.active_overlay.show()

    def close_active_overlay(self):
        """إغلاق التراكب النشط حاليًا"""
        if self.active_overlay:
            self.active_overlay.close()
            self.active_overlay = None

    def on_page_changed(self, new_page_index):
        """
        معالجة حدث تغيير الصفحة

        Args:
            new_page_index: فهرس الصفحة الجديدة
        """
        # إغلاق التراكب النشط عند تغيير الصفحة
        self.close_active_overlay()

    def is_overlay_active(self):
        """
        التحقق من وجود تراكب نشط

        Returns:
            bool: True إذا كان هناك تراكب نشط، False خلاف ذلك
        """
        return self.active_overlay is not None
