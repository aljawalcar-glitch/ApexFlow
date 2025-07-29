from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QGridLayout, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QIcon
from PySide6.QtSvg import QSvgRenderer
import os
from .global_styles import apply_global_style

# استيراد معلومات الإصدار
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from version import get_full_version_string
except ImportError:
    def get_full_version_string():
        return "الإصدار v5.2.1 - تطوير فريق ApexFlow"

# تم حذف TransparentBorderLabel لأنه كان يسبب ظهور إطارات حول النصوص

def load_feature_icon(icon_name, size=32, color="#ff6f00"):
    """تحميل أيقونة الميزة باستخدام QSvgRenderer مع معالجة أخطاء محسنة"""
    try:
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "menu_icons", f"{icon_name}.svg")

        if not os.path.exists(icon_path):
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

                # تطبيق اللون المطلوب
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
        apply_global_style(self)

        # تحميل الأيقونات بشكل مؤجل لتسريع البدء
        from PySide6.QtCore import QTimer
        QTimer.singleShot(300, self.load_icons_delayed)

    def init_ui(self):
        """إنشاء واجهة صفحة الترحيب"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # العنوان الرئيسي
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)

        # شعار التطبيق - نص مؤقت سيتم استبداله بالصورة لاحقاً
        self.logo_label = QLabel()
        self.logo_label.setText("ApexFlow")
        self.logo_label.setStyleSheet("""
            font-size: 36px;
            color: #ff6f00;
            font-weight: bold;
        """)

        self.logo_label.setStyleSheet(self.logo_label.styleSheet() + """
            margin-bottom: 10px;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 8px;
        """)
        self.logo_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.logo_label)

        # اسم التطبيق
        app_title = QLabel("ApexFlow")
        # استخدام نظام السمات الموحد
        from .theme_manager import apply_theme
        apply_theme(app_title, "title_text")
        app_title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(app_title)

        # وصف التطبيق
        description = QLabel("أداة شاملة لإدارة ومعالجة ملفات PDF")
        # استخدام نظام السمات الموحد للنص الثانوي
        apply_theme(description, "secondary_text")
        description.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(description)

        main_layout.addLayout(title_layout)

        # قسم الميزات الرئيسية
        features_frame = QFrame()

        # استخدام نظام السمات الموحد للفريم فقط
        from .theme_manager import apply_theme_style
        apply_theme_style(features_frame, "frame")

        features_layout = QVBoxLayout(features_frame)

        # عنوان الميزات
        features_title = QLabel("الميزات الرئيسية")
        features_title.setStyleSheet("""
            font-size: 24px !important;
            font-weight: bold !important;
            color: #e2e8f0 !important;
            margin-bottom: 20px !important;
            text-align: center !important;
            background: transparent !important;
            border: none !important;
        """)
        features_title.setAlignment(Qt.AlignCenter)
        features_layout.addWidget(features_title)

        # شبكة الميزات - سيتم ملؤها لاحقاً
        self.features_grid = QGridLayout()
        self.features_grid.setSpacing(10)

        # حفظ قائمة الميزات للتحميل المؤجل
        self.features_data = [
            ("link", "دمج الملفات", "دمج عدة ملفات PDF في ملف واحد"),
            ("scissors", "تقسيم الملفات", "تقسيم ملف PDF إلى ملفات منفصلة"),
            ("archive", "ضغط الملفات", "تقليل حجم ملفات PDF"),
            ("rotate-cw", "تدوير الصفحات", "تدوير صفحات PDF بزوايا مختلفة"),
            ("file-text", "تحويل الملفات", "تحويل PDF إلى صور أو نصوص والعكس"),
            ("settings", "إعدادات متقدمة", "تخصيص التطبيق حسب احتياجاتك")
        ]

        # إنشاء بطاقات مؤقتة بنصوص بسيطة
        columns = 3
        for i, (icon, title, desc) in enumerate(self.features_data):
            placeholder_widget = self.create_placeholder_card(title, desc)
            row = i // columns
            col = i % columns
            self.features_grid.addWidget(placeholder_widget, row, col)

        features_layout.addLayout(self.features_grid)
        main_layout.addWidget(features_frame)

        # قسم البدء السريع
        quick_start_frame = QFrame()

        # استخدام نظام السمات الموحد للفريم فقط
        apply_theme_style(quick_start_frame, "frame")

        quick_start_layout = QVBoxLayout(quick_start_frame)

        quick_start_title = QLabel("البدء السريع")
        quick_start_title.setStyleSheet("""
            font-size: 20px !important;
            font-weight: bold !important;
            color: #e2e8f0 !important;
            margin-bottom: 15px !important;
            text-align: center !important;
            background: transparent !important;
            border: none !important;
        """)
        quick_start_title.setAlignment(Qt.AlignCenter)
        quick_start_layout.addWidget(quick_start_title)

        # أزرار البدء السريع
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        quick_buttons = [
            ("ضغط ملف", "#ed8936", 3),     # الفهرس 3 لصفحة الضغط
            ("تقسيم ملف", "#48bb78", 2),  # الفهرس 2 لصفحة التقسيم
            ("دمج ملفات", "#4299e1", 1),  # الفهرس 1 لصفحة الدمج
        ]

        for text, color, page_index in quick_buttons:
            btn = QPushButton(text)
            # تطبيق نمط مخصص للأزرار مع !important لضمان عدم تأثر بنمط الفريم
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color} !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 8px !important;
                    padding: 12px 24px !important;
                    font-size: 14px !important;
                    font-weight: bold !important;
                    min-width: 120px !important;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)} !important;
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 0.3)} !important;
                }}
            """)
            # ربط الزر بالصفحة المناسبة
            btn.clicked.connect(lambda checked, idx=page_index: self.navigate_to_page.emit(idx))
            buttons_layout.addWidget(btn)

        quick_start_layout.addLayout(buttons_layout)
        main_layout.addWidget(quick_start_frame)

        # مساحة مرنة في النهاية
        main_layout.addStretch()

        # معلومات الإصدار
        version_label = QLabel(get_full_version_string())
        # استخدام نظام السمات الموحد للنص المكتوم
        apply_theme(version_label, "muted_text")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(version_label.styleSheet() + """
            background: transparent !important;
            border: none !important;
            padding: 0px !important;
            margin-top: 10px !important;
        """)
        main_layout.addWidget(version_label)

    def create_placeholder_card(self, title, description):
        """إنشاء بطاقة ميزة مؤقتة بدون أيقونات"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 32, 44, 0.7);
                border: 1px solid rgba(45, 55, 72, 0.8);
                border-radius: 10px;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #ff6f00;
                background-color: rgba(45, 55, 72, 0.8);
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # مساحة فارغة للأيقونة (سيتم ملؤها لاحقاً)
        icon_placeholder = QLabel()
        icon_placeholder.setFixedHeight(32)
        icon_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_placeholder)

        # العنوان
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: white;
            text-align: center;
            background: transparent;
            border: none;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # الوصف
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 11px;
            color: #a0aec0;
            text-align: center;
            background: transparent;
            border: none;
        """)
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
            print(f"خطأ في تحميل الأيقونات المؤجل: {e}")

    def load_logo(self):
        """تحميل شعار التطبيق"""
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
            if os.path.exists(logo_path):
                from PySide6.QtGui import QIcon
                icon = QIcon(logo_path)
                device_ratio = self.devicePixelRatio() if hasattr(self, 'devicePixelRatio') else 1.0
                actual_size = int(72 * device_ratio)
                pixmap = icon.pixmap(actual_size, actual_size)
                pixmap.setDevicePixelRatio(device_ratio)
                self.logo_label.setPixmap(pixmap)
        except Exception as e:
            print(f"خطأ في تحميل الشعار: {e}")

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
            print(f"خطأ في تحميل أيقونات الميزات: {e}")

    def create_feature_card(self, icon, title, description):
        """إنشاء بطاقة ميزة"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 32, 44, 0.7);
                border: 1px solid rgba(45, 55, 72, 0.8);
                border-radius: 10px;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #ff6f00;
                background-color: rgba(45, 55, 72, 0.8);
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # الأيقونة
        icon_label = QLabel()

        # تحميل الأيقونة الحقيقية مع fallback محسن
        device_ratio = self.devicePixelRatio() if hasattr(self, 'devicePixelRatio') else 2.0
        high_res_size = int(32 * device_ratio)
        icon_pixmap = load_feature_icon(icon, size=high_res_size, color="white")
        if icon_pixmap:
            icon_pixmap.setDevicePixelRatio(device_ratio)
            icon_label.setPixmap(icon_pixmap)
        else:
            # fallback نصي في حالة عدم وجود الأيقونة
            text_fallback = {
                "link": "دمج",
                "scissors": "تقسيم",
                "archive": "ضغط",
                "rotate-cw": "تدوير",
                "file-text": "تحويل",
                "settings": "إعدادات"
            }
            icon_label.setText(text_fallback.get(icon, "PDF"))
            icon_label.setStyleSheet("""
                font-size: 16px;
                color: #ff6f00;
                text-align: center;
                font-weight: bold;
                border: 2px solid #ff6f00;
                border-radius: 8px;
                padding: 8px;
            """)

        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # العنوان
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #e2e8f0;
            text-align: center;
            margin: 5px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # الوصف
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #a0aec0;
            text-align: center;
            line-height: 1.4;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        return card

    def darken_color(self, color, factor=0.2):
        """تغميق اللون"""
        from PySide6.QtGui import QColor
        color = QColor(color)
        h, s, l, a = color.getHsl()
        l = max(0, int(l * (1 - factor)))
        color.setHsl(h, s, l, a)
        return color.name()

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