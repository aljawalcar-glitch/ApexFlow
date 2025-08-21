from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QGridLayout, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QIcon
from PySide6.QtSvg import QSvgRenderer
import os
from utils.i18n import tr
from config.version import get_full_version_string
from managers.theme_manager import make_theme_aware

# هذا ليس ملف الواجهه الرئيسية - الواجهه الرئيسية هي Main.py
# تم حذف TransparentBorderLabel لأنه كان يسبب ظهور إطارات حول النصوص

def load_feature_icon(icon_name, size=32, color=None):
    """تحميل أيقونة الميزة باستخدام QSvgRenderer مع معالجة أخطاء محسنة"""
    import sys
    try:
        # تحديد المسار الصحيح بناءً على حالة التطبيق
        if getattr(sys, 'frozen', False):
            base_path = os.path.join(sys._MEIPASS, "assets", "icons")
        else:
            base_path = os.path.join("assets", "icons")
        
        # البحث عن الأيقونة بامتدادات مختلفة
        extensions = ['.svg', '.png', '.ico']
        icon_path = None
        
        # البحث في مجلد default أولاً
        for ext in extensions:
            test_path = os.path.join(base_path, "default", f"{icon_name}{ext}")
            if os.path.exists(test_path):
                icon_path = test_path
                break
        
        # إذا لم توجد، ابحث في المجلد الرئيسي
        if not icon_path:
            for ext in extensions:
                test_path = os.path.join(base_path, f"{icon_name}{ext}")
                if os.path.exists(test_path):
                    icon_path = test_path
                    break

        if not icon_path:
            return None

        # استخدام QSvgRenderer لتحميل SVG
        renderer = QSvgRenderer(icon_path)

        if renderer.isValid():
            # إنشاء pixmap بالحجم المطلوب
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor("transparent"))

            # رسم SVG على الـ pixmap
            painter = QPainter(pixmap)
            if painter.isActive():
                renderer.render(painter)

                # تطبيق اللون المطلوب، مع استخدام لون التمييز كافتراضي
                if color is None:
                    from managers.theme_manager import global_theme_manager
                    color = global_theme_manager.current_accent
                painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                painter.fillRect(pixmap.rect(), QColor(color))

                painter.end()
                return pixmap
            else:
                painter.end()

    except Exception as e:
        # تسجيل الخطأ بصمت دون إزعاج المستخدم
        pass

    return None

class WelcomePage(QWidget):
    # إشارات للتنقل إلى الصفحات المختلفة
    navigate_to_page = Signal(int)

    def __init__(self):
        super().__init__()
        self.icons_loaded = False  # تتبع حالة تحميل الأيقونات
        self.init_ui()
        self.setup_animations()

        # تطبيق التنسيق العام
        make_theme_aware(self, "main_window")

        # تحميل الأيقونات بشكل مؤجل لتسريع البدء
        from PySide6.QtCore import QTimer
        QTimer.singleShot(300, self.load_icons_delayed)
        
        # تفعيل السحب والإفلات
        self.setAcceptDrops(True)

    def showEvent(self, event):
        """تطبيق الأنماط الثابتة عند عرض الصفحة"""
        super().showEvent(event)
        # تطبيق الأنماط الثابتة على أزرار البدء السريع
        pass

    def init_ui(self):
        """إنشاء واجهة صفحة الترحيب"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # جعل خلفية الصفحة شفافة
        self.setStyleSheet("background: transparent;")

        # العنوان الرئيسي
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)

        # شعار التطبيق - نص مؤقت سيتم استبداله بالصورة لاحقاً
        self.logo_label = QLabel()
        self.logo_label.setText(tr("app_name"))
        make_theme_aware(self.logo_label, "welcome_logo_label")
        self.logo_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.logo_label)

        # اسم التطبيق
        app_title = QLabel(tr("app_name"))
        # استخدام نظام السمات الموحد
        make_theme_aware(app_title, "title_text")
        app_title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(app_title)

        # وصف التطبيق
        description = QLabel(tr("app_description"))
        # استخدام نظام السمات الموحد للنص الثانوي
        make_theme_aware(description, "secondary_text")
        description.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(description)

        main_layout.addLayout(title_layout)

        # قسم الميزات الرئيسية
        features_frame = QFrame()
        make_theme_aware(features_frame, "features_frame")

        features_layout = QVBoxLayout(features_frame)

        # عنوان الميزات
        features_title = QLabel(tr("key_features"))
        make_theme_aware(features_title, "title_text")
        features_title.setAlignment(Qt.AlignCenter)
        # إضافة هوامش للعنوان لزيادة المسافة من الأعلى والأسفل
        features_title.setContentsMargins(0, 15, 0, 25)
        features_layout.addWidget(features_title)

        # شبكة الميزات - سيتم ملؤها لاحقاً
        self.features_grid = QGridLayout()
        self.features_grid.setSpacing(20)
        # إضافة هوامش للشبكة لزيادة المسافة من الأسفل
        self.features_grid.setContentsMargins(20, 0, 20, 15)

        # حفظ قائمة الميزات للتحميل المؤجل
        self.features_data = [
            ("link", tr("feature_merge_title"), tr("feature_merge_desc")),
            ("scissors", tr("feature_split_title"), tr("feature_split_desc")),
            ("archive", tr("feature_compress_title"), tr("feature_compress_desc")),
            ("rotate-cw", tr("feature_rotate_title"), tr("feature_rotate_desc")),
            ("file-text", tr("feature_convert_title"), tr("feature_convert_desc")),
            ("settings", tr("feature_settings_title"), tr("feature_settings_desc"))
        ]

        # إنشاء بطاقات مؤقتة بنصوص بسيطة
        columns = 3
        for i, (icon, title, desc) in enumerate(self.features_data):
            placeholder_widget = self.create_placeholder_card(title, desc)
            row = i // columns
            col = i % columns
            self.features_grid.addWidget(placeholder_widget, row, col)

        features_layout.addLayout(self.features_grid)

        # Center the features frame and prevent it from stretching
        container = QWidget()
        centering_layout = QHBoxLayout(container)
        centering_layout.setContentsMargins(0, 0, 0, 0)
        centering_layout.addStretch()
        centering_layout.addWidget(features_frame)
        centering_layout.addStretch()
        
        main_layout.addWidget(container)

        # قسم البدء السريع
        quick_start_frame = QFrame()
        make_theme_aware(quick_start_frame, "transparent_frame")

        self.quick_start_layout = QVBoxLayout(quick_start_frame)

        quick_start_title = QLabel(tr("quick_start"))
        # استخدام نظام السمات بدلاً من الأنماط الثابتة
        make_theme_aware(quick_start_title, "title_text")
        quick_start_title.setAlignment(Qt.AlignCenter)
        self.quick_start_layout.addWidget(quick_start_title)

        # أزرار البدء السريع
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        buttons_layout.addStretch()

        quick_buttons = [
            (tr("quick_start_compress"), "quick_start_button_compress", 3),
            (tr("quick_start_split"), "quick_start_button_split", 2),
            (tr("quick_start_merge"), "quick_start_button_merge", 1),
        ]

        for text, style_type, page_index in quick_buttons:
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            make_theme_aware(btn, style_type)

            # ربط الزر بالصفحة المناسبة
            btn.clicked.connect(lambda checked, idx=page_index: self.navigate_to_page.emit(idx))
            buttons_layout.addWidget(btn)

        buttons_layout.addStretch()

        self.quick_start_layout.addLayout(buttons_layout)
        main_layout.addWidget(quick_start_frame)

        # مساحة مرنة في النهاية
        main_layout.addStretch()

        # معلومات الإصدار
        version_label = QLabel(get_full_version_string())
        # استخدام نظام السمات الموحد للنص المكتوم
        make_theme_aware(version_label, "muted_text")
        version_label.setAlignment(Qt.AlignCenter)

        # إضافة حاوية شفافة للنص
        version_container = QWidget()
        version_container_layout = QVBoxLayout(version_container)
        version_container_layout.setContentsMargins(0, 0, 0, 0)
        version_container_layout.addWidget(version_label)
        make_theme_aware(version_container, "transparent_frame")
        main_layout.addWidget(version_container)

    def create_placeholder_card(self, title, description):
        """إنشاء بطاقة ميزة مؤقتة بدون أيقونات"""
        card = QFrame()
        make_theme_aware(card, "feature_card")
        card.setFixedWidth(210)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # مساحة فارغة للأيقونة (سيتم ملؤها لاحقاً)
        icon_placeholder = QLabel()
        icon_placeholder.setFixedHeight(32)
        icon_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_placeholder)

        # العنوان
        title_label = QLabel(title)
        make_theme_aware(title_label, "feature_card_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # الوصف
        desc_label = QLabel(description)
        make_theme_aware(desc_label, "feature_card_desc")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        return card

    def load_icons_delayed(self):
        """تحميل الأيقونات والشعار بشكل مؤجل"""
        if self.icons_loaded:
            return

        try:
            # تحميل الشعار
            self.load_logo()

            # تحميل أيقونات الميزات
            self.load_feature_icons()

            self.icons_loaded = True
        except Exception as e:
            print(tr("error_loading_icons", e=e))

    def load_logo(self):
        """تحميل شعار التطبيق"""
        import sys
        try:
            # تحديد المسار الصحيح بناءً على حالة التطبيق
            if getattr(sys, 'frozen', False):
                logo_path = os.path.join(sys._MEIPASS, "assets", "logo.png")
            else:
                logo_path = os.path.join("assets", "logo.png")
            
            if os.path.exists(logo_path):
                from PySide6.QtGui import QIcon
                icon = QIcon(logo_path)
                device_ratio = self.devicePixelRatio() if hasattr(self, 'devicePixelRatio') else 1.0
                actual_size = int(72 * device_ratio)
                pixmap = icon.pixmap(actual_size, actual_size)
                pixmap.setDevicePixelRatio(device_ratio)
                self.logo_label.setPixmap(pixmap)
        except Exception as e:
            print(tr("error_loading_logo", e=e))

    def load_feature_icons(self):
        """تحميل أيقونات الميزات"""
        try:
            columns = 3
            for i, (icon, title, desc) in enumerate(self.features_data):
                # إنشاء بطاقة جديدة بالأيقونة
                new_card = self.create_feature_card(icon, title, desc)

                # استبدال البطاقة المؤقتة
                row = i // columns
                col = i % columns

                # إزالة البطاقة القديمة
                old_item = self.features_grid.itemAtPosition(row, col)
                if old_item:
                    old_widget = old_item.widget()
                    if old_widget:
                        self.features_grid.removeWidget(old_widget)
                        old_widget.setParent(None)

                # إضافة البطاقة الجديدة
                self.features_grid.addWidget(new_card, row, col)

        except Exception as e:
            print(tr("error_loading_feature_icons", e=e))

    def get_main_window(self):
        """الحصول على النافذة الرئيسية للتطبيق"""
        # البحث عن النافذة الرئيسية
        widget = self.parent()
        while widget:
            if widget.objectName() == "ApexFlow":
                return widget
            widget = widget.parent()
        return None

    def create_feature_card(self, icon, title, description):
        """إنشاء بطاقة ميزة"""
        card = QFrame()
        make_theme_aware(card, "feature_card")
        card.setFixedWidth(210)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # الأيقونة
        icon_label = QLabel()
        from managers.theme_manager import global_theme_manager
        
        # تحميل الأيقونة الحقيقية مع fallback محسن
        device_ratio = self.devicePixelRatio() if hasattr(self, 'devicePixelRatio') else 2.0
        high_res_size = int(32 * device_ratio)
        # استخدام لون التمييز من السمة الحالية
        icon_color = global_theme_manager.current_accent
        icon_pixmap = load_feature_icon(icon, size=high_res_size, color=icon_color)
        if icon_pixmap:
            icon_pixmap.setDevicePixelRatio(device_ratio)
            icon_label.setPixmap(icon_pixmap)
        else:
            # fallback نصي في حالة عدم وجود الأيقونة
            text_fallback = {
                "link": tr("feature_merge_title"),
                "scissors": tr("feature_split_title"),
                "archive": tr("feature_compress_title"),
                "rotate-cw": tr("feature_rotate_title"),
                "file-text": tr("feature_convert_title"),
                "settings": tr("feature_settings_title")
            }
            icon_label.setText(text_fallback.get(icon, tr("feature_card_fallback")))
            make_theme_aware(icon_label, "feature_card_icon_fallback")

        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # العنوان
        title_label = QLabel(title)
        make_theme_aware(title_label, "feature_card_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # الوصف
        desc_label = QLabel(description)
        make_theme_aware(desc_label, "feature_card_desc")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        return card

    def setup_animations(self):
        """إعداد الحركات المتحركة"""
        # يمكن إضافة حركات متحركة هنا لاحقاً
        pass

    def create_engraved_image(self, pixmap):
        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)

        # ظل داخلي وهمي
        offset = 2
        dark_pixmap = QPixmap(pixmap.size())
        dark_pixmap.fill(Qt.transparent)

        dark_painter = QPainter(dark_pixmap)
        dark_painter.setOpacity(0.25)
        dark_painter.drawPixmap(offset, offset, pixmap)
        dark_painter.end()

        painter.drawPixmap(0, 0, dark_pixmap)
        painter.drawPixmap(0, 0, pixmap)

        painter.end()
        return result

class EngravedLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        text = self.text()
        font = self.font()
        painter.setFont(font)

        # رسم النص كظل غائر
        painter.setPen(QColor("black"))
        painter.drawText(self.rect().translated(2, 2), Qt.AlignCenter, text)

        painter.setPen(QColor("#ddd"))
        painter.drawText(self.rect(), Qt.AlignCenter, text)

        painter.end()
