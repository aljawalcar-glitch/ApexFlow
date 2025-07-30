"""
واجهة الإعدادات بتصميم Step Wizard شفاف
Transparent Step Wizard Settings UI for ApexFlow
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QSpinBox, QSlider, QGroupBox,
    QFileDialog, QMessageBox, QFormLayout, QFrame, QScrollArea, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, Signal
from modules import settings
from .theme_manager import global_theme_manager, apply_theme_style
from .ui_helpers import FocusAwareComboBox
from .theme_aware_widget import ThemeAwareDialog
from .svg_icon_button import create_navigation_button

# حل مشكلة theme_manager
theme_manager = global_theme_manager

class StepIndicator(QWidget):
    """مؤشر الخطوات في الأعلى"""
    
    step_clicked = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 2  # البدء من المظهر (الفهرس 2)
        self.steps = ["حفظ", "الخطوط", "المظهر"]  # عكس الترتيب
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة مؤشر الخطوات"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(0)  # مسافة صفر بين الأزرار

        # إضافة مساحة مرنة في البداية لدفع الأزرار لليمين
        layout.addStretch()

        self.step_buttons = []

        for i, step_name in enumerate(self.steps):
            btn = QPushButton(step_name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, ui_idx=i: self.step_clicked.emit(ui_idx))

            # استخدام نظام السمات الموحد
            from .theme_manager import apply_theme
            apply_theme(btn, "button")

            self.step_buttons.append(btn)
            layout.addWidget(btn)
        
        # مؤشر الانزلاق المحسن
        self.slider_indicator = QFrame(self)

        # استخدام نظام السمات الموحد
        from .theme_manager import apply_theme
        apply_theme(self.slider_indicator, "frame")
        self.update_slider_position()

    def logical_to_ui_index(self, logical_index):
        """تحويل الفهرس المنطقي إلى فهرس الواجهة"""
        # المنطق: المظهر=0، العمليات=1، متقدم=2، حفظ=3
        # الواجهة: حفظ=0، متقدم=1، العمليات=2، المظهر=3
        mapping = {0: 3, 1: 2, 2: 1, 3: 0}  # منطقي: واجهة
        return mapping.get(logical_index, 0)

    def ui_to_logical_index(self, ui_index):
        """تحويل فهرس الواجهة إلى الفهرس المنطقي"""
        # عكس التحويل السابق
        mapping = {3: 0, 2: 1, 1: 2, 0: 3}  # واجهة: منطقي
        return mapping.get(ui_index, 0)
        
    def get_step_button_style(self, is_active=False):
        """تنسيق أزرار الخطوات"""
        if is_active:
            return """
                QPushButton {
                    background: transparent;
                    border: none;
                    outline: none;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 15px 25px;
                }
                QPushButton:hover {
                    background: transparent;
                    color: rgba(255, 255, 255, 0.9);
                }
            """
        else:
            return """
                QPushButton {
                    background: transparent;
                    border: none;
                    outline: none;
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 16px;
                    font-weight: normal;
                    padding: 15px 25px;
                }
                QPushButton:hover {
                    background: transparent;
                    color: rgba(255, 255, 255, 0.8);
                }
            """
    
    def set_current_step(self, step):
        """تعيين الخطوة الحالية"""
        self.current_step = step

        for i, btn in enumerate(self.step_buttons):
            # استخدام نظام السمات الموحد
            from .theme_manager import apply_theme
            apply_theme(btn, "button")
            btn.setChecked(i == step)

        self.update_slider_position()
    
    def update_slider_position(self):
        """تحديث موقع مؤشر الانزلاق"""
        if hasattr(self, 'slider_indicator') and self.step_buttons:
            if len(self.step_buttons) > self.current_step:
                btn = self.step_buttons[self.current_step]
                # تأخير التحديث للتأكد من أن الأزرار تم رسمها
                QTimer.singleShot(50, lambda: self.slider_indicator.setGeometry(
                    btn.x(), btn.y() + btn.height() - 6,
                    btn.width(), 6
                ))

class TransparentFrame(QFrame):
    """فريم شفاف للمحتوى"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
    
    def setup_style(self):
        """إعداد التنسيق الموحد للفريم"""
        # استخدام نظام السمات الموحد
        from .theme_manager import apply_theme
        apply_theme(self, "frame")

class SettingsUI(ThemeAwareDialog):
    """واجهة الإعدادات الرئيسية بتصميم Step Wizard"""

    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent, "settings_window")
        # self.setWindowFlags(Qt.FramelessWindowHint) # No longer a frameless window

        self.settings_data = settings.load_settings()
        self.original_settings = self.settings_data.copy()
        self.current_step = 2  # البدء من المظهر (الفهرس 2)
        self.has_unsaved_changes = False  # تتبع التغييرات غير المحفوظة

        # تتبع الصفحات المحملة للتحميل الكسول
        self.pages_loaded = [False, False, False]  # [حفظ، خطوط، مظهر]
        self.page_widgets = [None, None, None]  # تخزين الصفحات المحملة

        self.init_ui()

        # تحسين إضافي: تأخير تحميل العناصر الثقيلة
        QTimer.singleShot(50, self.delayed_initialization)

    def closeEvent(self, event):
        """حماية من الخروج بدون حفظ التغييرات"""
        if self.has_unsaved_changes:
            msg = QMessageBox(QMessageBox.Question, "تحذير",
                "لديك تغييرات غير محفوظة. ماذا تريد أن تفعل؟", parent=self)

            save_btn = msg.addButton("حفظ وإغلاق", QMessageBox.AcceptRole)
            discard_btn = msg.addButton("تجاهل التغييرات", QMessageBox.DestructiveRole)
            cancel_btn = msg.addButton("إلغاء", QMessageBox.RejectRole)

            apply_theme_style(msg, "dialog")
            msg.exec()

            if msg.clickedButton() == save_btn:
                # حفظ التغييرات ثم إغلاق
                if self.save_all_settings():
                    # استدعاء closeEvent الأصلي للتنظيف
                    super().closeEvent(event)
                else:
                    event.ignore()
            elif msg.clickedButton() == discard_btn:
                # تجاهل التغييرات وإغلاق
                super().closeEvent(event)
            else:
                # إلغاء الإغلاق
                event.ignore()
        else:
            # لا توجد تغييرات، إغلاق عادي
            super().closeEvent(event)

    # ===============================
    # دوال التهيئة والإعداد الأساسي
    # ===============================

    def init_ui(self):
        """إنشاء واجهة المستخدم"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # مؤشر الخطوات
        self.step_indicator = StepIndicator()
        self.step_indicator.step_clicked.connect(self.go_to_step)
        main_layout.addWidget(self.step_indicator)
        
        # المحتوى الرئيسي
        self.content_frame = TransparentFrame()
        # تطبيق السمة على الفريم الكبير
        from .theme_manager import apply_theme_style
        apply_theme_style(self.content_frame, "frame")
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # منطقة المحتوى المتغير - شفاف تماماً
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        self.create_step_pages()
        content_layout.addWidget(self.content_stack)
        
        # أزرار التنقل الداخلية مع أيقونات SVG - محاذاة مع عنوان "إعدادات المظهر"
        nav_layout = QHBoxLayout()

        # إضافة مسافة لمحاذاة الأزرار مع عنوان الصفحة (30px من اليسار)
        nav_layout.addSpacing(30)

        # زر التالي (يسار) - أيقونة سهم يسار مع لون السمة
        self.next_btn = create_navigation_button("prev", 24, "الخطوة التالية")
        self.next_btn.clicked.connect(self.next_step)
        nav_layout.addWidget(self.next_btn)

        # مسافة قليلة بين الأزرار
        nav_layout.addSpacing(15)

        # زر السابق (يمين) - أيقونة سهم يمين مع لون السمة
        self.prev_btn = create_navigation_button("next", 24, "الخطوة السابقة")
        self.prev_btn.clicked.connect(self.previous_step)
        self.prev_btn.setEnabled(False)  # معطل في البداية بدلاً من مخفي
        nav_layout.addWidget(self.prev_btn)

        # دفع باقي المحتوى لليمين
        nav_layout.addStretch()
        
        content_layout.addLayout(nav_layout)
        main_layout.addWidget(self.content_frame)
        
        # تعيين الصفحة الافتراضية والتحميل
        self.content_stack.setCurrentIndex(2)  # المظهر (الفهرس 2)
        self.update_navigation_buttons()

        # تحميل الإعدادات الحالية (بدلاً من الأصلية) لعرضها في الواجهة
        QTimer.singleShot(100, self.load_current_settings_to_ui)
        # تحديث الخط السفلي بعد رسم الواجهة
        QTimer.singleShot(200, lambda: self.step_indicator.set_current_step(2))
        # تحديث تقرير التغييرات بعد التحميل
        QTimer.singleShot(300, self.update_changes_report)

        # لا نحتاج تطبيق السمة هنا - السمة تُطبق تلقائياً من النظام المركزي

    # ===============================
    # دوال إنشاء الصفحات
    # ===============================

    def create_step_pages(self):
        """إنشاء صفحات الخطوات بالتحميل الكسول"""
        # إنشاء صفحات فارغة كعناصر نائبة
        for i in range(3):
            placeholder = QWidget()
            placeholder.setStyleSheet("background: transparent;")
            self.content_stack.addWidget(placeholder)

        # تحميل الصفحة الافتراضية (المظهر) فقط
        self.load_page_on_demand(self.current_step)

    def load_page_on_demand(self, page_index):
        """تحميل صفحة عند الحاجة فقط"""
        if not self.pages_loaded[page_index]:
            # إنشاء الصفحة المطلوبة
            if page_index == 0:  # حفظ
                page_widget = self.create_save_page()
            elif page_index == 1:  # خطوط
                page_widget = self.create_fonts_page()
            elif page_index == 2:  # مظهر
                page_widget = self.create_appearance_page()
            else:
                return

            # استبدال العنصر النائب بالصفحة الحقيقية
            old_widget = self.content_stack.widget(page_index)
            self.content_stack.removeWidget(old_widget)
            old_widget.deleteLater()

            self.content_stack.insertWidget(page_index, page_widget)
            self.page_widgets[page_index] = page_widget
            self.pages_loaded[page_index] = True

    def delayed_initialization(self):
        """تحميل مؤجل للعناصر الثقيلة لتحسين سرعة الفتح"""
        # يمكن إضافة تحميل العناصر الثقيلة هنا إذا لزم الأمر
        # مثل تحميل قوائم الخطوط أو الأيقونات الكبيرة
        pass

    # ===============================
    # دوال التنسيق والأنماط (تم نقلها إلى global_styles.py)
    # ===============================

    def create_appearance_page(self):
        """إنشاء صفحة إعدادات المظهر"""
        page = QWidget()
        page.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                border: none;
                outline: none;
            }
        """)
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # إنشاء منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(self.get_scroll_area_style())

        # المحتوى الداخلي
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(25)

        # عنوان الصفحة
        title = QLabel("إعدادات المظهر والسمات")
        apply_theme_style(title, "title_text", auto_register=True)
        layout.addWidget(title)

        # مجموعة السمة
        theme_group = QGroupBox("السمة والألوان")
        apply_theme_style(theme_group, "group_box", auto_register=True)
        theme_layout = QFormLayout(theme_group)
        theme_layout.setSpacing(15)

        # السمة
        self.theme_combo = FocusAwareComboBox()
        self.theme_combo.addItems(["dark", "light", "blue", "green", "purple"])
        apply_theme_style(self.theme_combo, "combo")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addRow("السمة:", self.theme_combo)

        # لون التمييز
        accent_layout = QHBoxLayout()
        self.accent_color_input = QLineEdit()
        self.accent_color_input.setPlaceholderText("#ff6f00")
        apply_theme_style(self.accent_color_input, "input", auto_register=True)
        self.accent_color_input.textChanged.connect(self.on_accent_color_changed)

        self.accent_color_btn = QPushButton("اختر اللون")
        apply_theme_style(self.accent_color_btn, "transparent_button")
        self.accent_color_btn.clicked.connect(self.choose_accent_color)

        accent_layout.addWidget(self.accent_color_input, 2)
        accent_layout.addWidget(self.accent_color_btn, 1)
        theme_layout.addRow("لون التمييز:", accent_layout)

        # ألوان النصوص
        text_colors_group = QGroupBox("ألوان النصوص")
        apply_theme_style(text_colors_group, "group_box", auto_register=True)
        text_colors_layout = QFormLayout(text_colors_group)
        text_colors_layout.setSpacing(10)

        # لون العناوين
        self.title_color_combo = FocusAwareComboBox()
        self.title_color_combo.addItems([
            "افتراضي",
            "أبيض",
            "أسود",
            "رمادي داكن",
            "أزرق داكن",
            "أخضر داكن"
        ])
        apply_theme_style(self.title_color_combo, "combo")
        self.title_color_combo.currentTextChanged.connect(self.on_text_color_changed)
        text_colors_layout.addRow("لون العناوين:", self.title_color_combo)

        # لون النص العادي
        self.body_color_combo = FocusAwareComboBox()
        self.body_color_combo.addItems([
            "افتراضي",
            "أبيض",
            "أسود",
            "رمادي فاتح",
            "رمادي داكن"
        ])
        apply_theme_style(self.body_color_combo, "combo")
        self.body_color_combo.currentTextChanged.connect(self.on_text_color_changed)
        text_colors_layout.addRow("لون النص العادي:", self.body_color_combo)

        # لون النص الثانوي
        self.secondary_color_combo = FocusAwareComboBox()
        self.secondary_color_combo.addItems([
            "افتراضي",
            "رمادي فاتح",
            "رمادي متوسط",
            "رمادي داكن"
        ])
        apply_theme_style(self.secondary_color_combo, "combo")
        self.secondary_color_combo.currentTextChanged.connect(self.on_text_color_changed)
        text_colors_layout.addRow("لون النص الثانوي:", self.secondary_color_combo)

        theme_layout.addRow(text_colors_group)

        # مستوى الشفافية
        transparency_layout = QHBoxLayout()
        transparency_label = QLabel("مستوى الشفافية:")
        apply_theme_style(transparency_label, "label", auto_register=True)
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(20, 95)
        self.transparency_slider.setValue(80)
        apply_theme_style(self.transparency_slider, "slider", auto_register=True)
        self.transparency_value = QLabel("80%")
        apply_theme_style(self.transparency_value, "label", auto_register=True)

        transparency_layout.addWidget(self.transparency_slider, 3)
        transparency_layout.addWidget(self.transparency_value, 1)
        theme_layout.addRow("الشفافية:", transparency_layout)

        # حجم العناصر
        self.size_combo = FocusAwareComboBox()
        self.size_combo.addItems([
            "صغير (مدمج)",
            "متوسط (افتراضي)",
            "كبير (مريح)",
            "كبير جداً (إمكانية وصول)"
        ])
        self.size_combo.setCurrentText("متوسط (افتراضي)")
        apply_theme_style(self.size_combo, "combo")
        theme_layout.addRow("حجم العناصر:", self.size_combo)

        # مستوى التباين
        self.contrast_combo = FocusAwareComboBox()
        self.contrast_combo.addItems([
            "منخفض (ناعم)",
            "عادي (متوازن)",
            "عالي (واضح)",
            "عالي جداً (إمكانية وصول)"
        ])
        self.contrast_combo.setCurrentText("عادي (متوازن)")
        apply_theme_style(self.contrast_combo, "combo")
        theme_layout.addRow("التباين:", self.contrast_combo)

        # ربط التغييرات بالمعاينة وتتبع التغييرات
        self.transparency_slider.valueChanged.connect(self.on_transparency_changed)
        self.transparency_slider.valueChanged.connect(self.mark_as_changed)
        self.size_combo.currentTextChanged.connect(self.on_theme_options_changed)
        self.size_combo.currentTextChanged.connect(self.mark_as_changed)
        self.contrast_combo.currentTextChanged.connect(self.on_theme_options_changed)
        self.contrast_combo.currentTextChanged.connect(self.mark_as_changed)

        layout.addWidget(theme_group)




        layout.addStretch()

        # ربط المحتوى بمنطقة التمرير
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return page

    def create_fonts_page(self):
        """إنشاء صفحة إعدادات الخطوط والنصوص"""
        page = QWidget()
        page.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                border: none;
                outline: none;
            }
        """)
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # إنشاء منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(self.get_scroll_area_style())

        # المحتوى الداخلي
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(25)

        # عنوان الصفحة
        title = QLabel("إعدادات الخطوط والنصوص")
        apply_theme_style(title, "title_text", auto_register=True)
        layout.addWidget(title)

        # مجموعة إعدادات الخط الأساسي
        font_group = QGroupBox("الخط الأساسي")
        apply_theme_style(font_group, "group_box", auto_register=True)
        font_layout = QFormLayout(font_group)
        font_layout.setSpacing(15)

        # حجم الخط (منقول من المظهر)
        font_size_layout = QHBoxLayout()
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(10, 24)
        self.font_size_slider.setValue(16)
        apply_theme_style(self.font_size_slider, "slider")

        self.font_size_label = QLabel("16")
        apply_theme_style(self.font_size_label, "label", auto_register=True)
        self.font_size_slider.valueChanged.connect(
            lambda v: self.font_size_label.setText(str(v))
        )
        self.font_size_slider.valueChanged.connect(self.mark_as_changed)

        font_size_layout.addWidget(self.font_size_slider, 3)
        font_size_layout.addWidget(self.font_size_label, 1)
        font_layout.addRow("حجم الخط:", font_size_layout)

        # نوع الخط
        self.font_family_combo = FocusAwareComboBox()
        self.font_family_combo.addItems([
            "النظام الافتراضي",
            "Arial",
            "Tahoma",
            "Segoe UI",
            "Cairo",
            "Amiri",
            "Noto Sans Arabic"
        ])
        # تطبيق النمط الموحد للقوائم المنسدلة
        apply_theme_style(self.font_family_combo, "combo")
        self.font_family_combo.currentTextChanged.connect(self.mark_as_changed)
        font_layout.addRow("نوع الخط:", self.font_family_combo)

        # وزن الخط
        self.font_weight_combo = FocusAwareComboBox()
        self.font_weight_combo.addItems([
            "عادي",
            "سميك",
            "سميك جداً"
        ])
        # تطبيق النمط الموحد للقوائم المنسدلة
        apply_theme_style(self.font_weight_combo, "combo")
        self.font_weight_combo.currentTextChanged.connect(self.mark_as_changed)
        font_layout.addRow("وزن الخط:", self.font_weight_combo)

        layout.addWidget(font_group)

        # مجموعة إعدادات النصوص (منقولة من المظهر)
        text_group = QGroupBox("إعدادات النصوص")
        apply_theme_style(text_group, "group_box", auto_register=True)
        text_layout = QFormLayout(text_group)
        text_layout.setSpacing(15)

        # إظهار التلميحات (منقول من المظهر)
        self.show_tooltips_check = QCheckBox("إظهار التلميحات")
        apply_theme_style(self.show_tooltips_check, "checkbox", auto_register=True)
        self.show_tooltips_check.stateChanged.connect(self.mark_as_changed)
        text_layout.addRow(self.show_tooltips_check)

        # تمكين الحركات (منقول من المظهر)
        self.enable_animations_check = QCheckBox("تمكين الحركات والتأثيرات")
        apply_theme_style(self.enable_animations_check, "checkbox", auto_register=True)
        self.enable_animations_check.setChecked(True)
        self.enable_animations_check.stateChanged.connect(self.mark_as_changed)
        text_layout.addRow(self.enable_animations_check)

        # اتجاه النص
        self.text_direction_combo = FocusAwareComboBox()
        self.text_direction_combo.addItems([
            "تلقائي",
            "من اليمين لليسار",
            "من اليسار لليمين"
        ])
        # تطبيق النمط الموحد للقوائم المنسدلة
        apply_theme_style(self.text_direction_combo, "combo")
        self.text_direction_combo.currentTextChanged.connect(self.mark_as_changed)
        text_layout.addRow("اتجاه النص:", self.text_direction_combo)

        layout.addWidget(text_group)

        # مجموعة معاينة الخط
        preview_group = QGroupBox("معاينة الخط")
        apply_theme_style(preview_group, "group_box")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setSpacing(15)

        # نص المعاينة
        self.font_preview_label = QLabel("هذا نص تجريبي لمعاينة الخط المحدد\nThis is a sample text to preview the selected font")
        self.font_preview_label.setStyleSheet("""
            QLabel {
                color: white;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                line-height: 1.5;
            }
        """)
        self.font_preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.font_preview_label)

        layout.addWidget(preview_group)
        layout.addStretch()

        # ربط المحتوى بمنطقة التمرير
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # ربط التحديثات بالمعاينة والتطبيق الفوري
        self.font_size_slider.valueChanged.connect(self.update_font_preview)
        self.font_family_combo.currentTextChanged.connect(self.update_font_preview)
        self.font_weight_combo.currentTextChanged.connect(self.update_font_preview)

        # تطبيق فوري للخطوط عند التغيير
        self.font_size_slider.valueChanged.connect(self.apply_fonts_immediately)
        self.font_family_combo.currentTextChanged.connect(self.apply_fonts_immediately)
        self.font_weight_combo.currentTextChanged.connect(self.apply_fonts_immediately)

        # تحديث المعاينة الأولية
        QTimer.singleShot(100, self.update_font_preview)

        return page

    def apply_fonts_immediately(self):
        """تطبيق إعدادات الخطوط فوراً على التطبيق"""
        try:
            # حفظ إعدادات الخطوط مؤقتاً
            from modules import settings
            settings_data = settings.load_settings()
            ui_settings = settings_data.get("ui_settings", {})

            if hasattr(self, 'font_size_slider'):
                ui_settings["font_size"] = self.font_size_slider.value()
            if hasattr(self, 'font_family_combo'):
                ui_settings["font_family"] = self.font_family_combo.currentText()
            if hasattr(self, 'font_weight_combo'):
                ui_settings["font_weight"] = self.font_weight_combo.currentText()

            settings_data["ui_settings"] = ui_settings
            settings.save_settings(settings_data)

            # تطبيق الخطوط فوراً
            from .theme_manager import refresh_all_fonts
            refresh_all_fonts()

        except Exception as e:
            print(f"خطأ في تطبيق الخطوط فوراً: {e}")

    def update_font_preview(self):
        """تحديث معاينة الخط"""
        try:
            if not hasattr(self, 'font_preview_label'):
                return

            # الحصول على القيم الحالية
            font_size = self.font_size_slider.value() if hasattr(self, 'font_size_slider') else 16
            font_family = self.font_family_combo.currentText() if hasattr(self, 'font_family_combo') else "النظام الافتراضي"
            font_weight = self.font_weight_combo.currentText() if hasattr(self, 'font_weight_combo') else "عادي"

            # تحويل نوع الخط
            if font_family == "النظام الافتراضي":
                font_family_css = "system-ui, -apple-system, sans-serif"
            else:
                font_family_css = font_family

            # تحويل وزن الخط
            weight_map = {
                "عادي": "normal",
                "سميك": "bold",
                "سميك جداً": "900"
            }
            font_weight_css = weight_map.get(font_weight, "normal")

            # تطبيق النمط
            style = f"""
                QLabel {{
                    color: white;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    line-height: 1.5;
                    font-family: {font_family_css};
                    font-size: {font_size}px;
                    font-weight: {font_weight_css};
                }}
            """

            self.font_preview_label.setStyleSheet(style)

        except Exception as e:
            print(f"خطأ في تحديث معاينة الخط: {e}")





    def create_save_page(self):
        """إنشاء صفحة الحفظ مع تقرير التغييرات"""
        page = QWidget()
        page.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                border: none;
                outline: none;
            }
        """)
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # إنشاء منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(self.get_scroll_area_style())

        # المحتوى الداخلي
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(25)

        # عنوان الصفحة
        title = QLabel("مراجعة وحفظ التغييرات")
        apply_theme_style(title, "title_text")
        layout.addWidget(title)

        # منطقة التقرير
        report_group = QGroupBox("ملخص التعديلات")
        apply_theme_style(report_group, "group_box")
        report_layout = QVBoxLayout(report_group)
        report_layout.setSpacing(10)

        # تقرير التغييرات
        self.changes_report = QLabel("جاري تحليل التغييرات...")
        self.changes_report.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 13px;
                line-height: 1.6;
                padding: 15px;
                background: rgba(255, 255, 255, 0.05);
                border: none;
                outline: none;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self.changes_report.setWordWrap(True)
        self.changes_report.setAlignment(Qt.AlignTop)
        report_layout.addWidget(self.changes_report)

        layout.addWidget(report_group)

        # أزرار الحفظ
        save_buttons_layout = QHBoxLayout()

        # زر إرجاع الإعدادات الافتراضية
        self.reset_defaults_btn = QPushButton("إرجاع الإعدادات الافتراضية")
        self.reset_defaults_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(108, 117, 125, 0.2);
                border: 1px solid rgba(108, 117, 125, 0.4);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background: rgba(108, 117, 125, 0.3);
                border: 1px solid rgba(108, 117, 125, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba(108, 117, 125, 0.1);
            }}
        """)
        self.reset_defaults_btn.clicked.connect(self.reset_to_defaults)

        # زر حفظ الإعدادات الحالية كافتراضية
        self.save_as_default_btn = QPushButton("حفظ كافتراضية")
        self.save_as_default_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(13, 110, 253, 0.2);
                border: 1px solid rgba(13, 110, 253, 0.4);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background: rgba(13, 110, 253, 0.3);
                border: 1px solid rgba(13, 110, 253, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba(13, 110, 253, 0.1);
            }}
        """)
        self.save_as_default_btn.clicked.connect(self.save_current_as_default)

        self.save_all_btn = QPushButton("حفظ جميع التغييرات")
        apply_theme_style(self.save_all_btn, "save_button")
        self.save_all_btn.clicked.connect(self.save_all_settings)

        self.cancel_btn = QPushButton("إلغاء التغييرات")
        apply_theme_style(self.cancel_btn, "cancel_button")
        self.cancel_btn.clicked.connect(self.cancel_changes)

        save_buttons_layout.addWidget(self.reset_defaults_btn)
        save_buttons_layout.addWidget(self.save_as_default_btn)
        save_buttons_layout.addStretch()
        save_buttons_layout.addWidget(self.cancel_btn)
        save_buttons_layout.addWidget(self.save_all_btn)

        layout.addLayout(save_buttons_layout)
        layout.addStretch()

        # ربط المحتوى بمنطقة التمرير
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return page

    def reset_to_defaults(self):
        """إرجاع جميع الإعدادات إلى الافتراضية"""
        from PySide6.QtWidgets import QMessageBox

        # تأكيد من المستخدم
        msg = QMessageBox(self)
        msg.setWindowTitle("تأكيد إرجاع الإعدادات")
        msg.setText("هل أنت متأكد من إرجاع جميع الإعدادات إلى الافتراضية؟")
        msg.setInformativeText("سيتم فقدان جميع الإعدادات المخصصة الحالية.")
        msg.setIcon(QMessageBox.Warning)

        reset_btn = msg.addButton("إرجاع الإعدادات", QMessageBox.AcceptRole)
        cancel_btn = msg.addButton("إلغاء", QMessageBox.RejectRole)
        msg.setDefaultButton(cancel_btn)

        # تطبيق نمط الرسالة
        apply_theme_style(msg, "dialog")

        msg.exec()

        if msg.clickedButton() == reset_btn:
            try:
                # إرجاع الإعدادات إلى الافتراضية
                from modules.default_settings import reset_to_defaults
                if reset_to_defaults():
                    # إعادة تحميل الإعدادات في الواجهة
                    self.load_current_settings_to_ui()

                    # تطبيق الإعدادات الافتراضية على التطبيق
                    from .theme_manager import refresh_all_fonts
                    from .theme_manager import global_theme_manager

                    # تطبيق السمة الافتراضية
                    global_theme_manager.change_theme("dark", "#ff6f00")
                    refresh_all_fonts()

                    # تحديث تقرير التغييرات
                    self.update_changes_report()

                    # رسالة نجاح
                    success_msg = QMessageBox(self)
                    success_msg.setWindowTitle("تم الإرجاع بنجاح")
                    success_msg.setText("تم إرجاع جميع الإعدادات إلى الافتراضية بنجاح!")
                    success_msg.setIcon(QMessageBox.Information)
                    apply_theme_style(success_msg, "dialog")
                    success_msg.exec()

                else:
                    # رسالة خطأ
                    error_msg = QMessageBox(self)
                    error_msg.setWindowTitle("خطأ")
                    error_msg.setText("حدث خطأ أثناء إرجاع الإعدادات الافتراضية.")
                    error_msg.setIcon(QMessageBox.Critical)
                    apply_theme_style(error_msg, "dialog")
                    error_msg.exec()

            except Exception as e:
                # رسالة خطأ
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("خطأ")
                error_msg.setText(f"حدث خطأ: {str(e)}")
                error_msg.setIcon(QMessageBox.Critical)
                apply_theme_style(error_msg, "dialog")
                error_msg.exec()

    def save_current_as_default(self):
        """حفظ الإعدادات الحالية كإعدادات افتراضية جديدة"""
        from PySide6.QtWidgets import QMessageBox

        # تأكيد من المستخدم
        msg = QMessageBox(self)
        msg.setWindowTitle("تأكيد حفظ الإعدادات الافتراضية")
        msg.setText("هل تريد حفظ الإعدادات الحالية كإعدادات افتراضية جديدة؟")
        msg.setInformativeText("سيتم استبدال الإعدادات الافتراضية الحالية.")
        msg.setIcon(QMessageBox.Question)

        save_btn = msg.addButton("حفظ كافتراضية", QMessageBox.AcceptRole)
        cancel_btn = msg.addButton("إلغاء", QMessageBox.RejectRole)
        msg.setDefaultButton(save_btn)

        # تطبيق نمط الرسالة
        apply_theme_style(msg, "dialog")

        msg.exec()

        if msg.clickedButton() == save_btn:
            try:
                # حفظ الإعدادات الحالية أولاً
                if self.save_all_settings():
                    # حفظ كإعدادات افتراضية
                    from modules.default_settings import save_current_as_default
                    if save_current_as_default():
                        # رسالة نجاح
                        success_msg = QMessageBox(self)
                        success_msg.setWindowTitle("تم الحفظ بنجاح")
                        success_msg.setText("تم حفظ الإعدادات الحالية كإعدادات افتراضية جديدة!")
                        success_msg.setIcon(QMessageBox.Information)
                        apply_theme_style(success_msg, "dialog")
                        success_msg.exec()
                    else:
                        # رسالة خطأ
                        error_msg = QMessageBox(self)
                        error_msg.setWindowTitle("خطأ")
                        error_msg.setText("حدث خطأ أثناء حفظ الإعدادات الافتراضية.")
                        error_msg.setIcon(QMessageBox.Critical)
                        apply_theme_style(error_msg, "dialog")
                        error_msg.exec()

            except Exception as e:
                # رسالة خطأ
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("خطأ")
                error_msg.setText(f"حدث خطأ: {str(e)}")
                error_msg.setIcon(QMessageBox.Critical)
                apply_theme_style(error_msg, "dialog")
                error_msg.exec()

    # ===============================
    # دوال معالجة الأحداث والتفاعل
    # ===============================

    def choose_accent_color(self):
        """اختيار لون التمييز"""
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor

        current_color = QColor(self.accent_color_input.text() or "#ff6f00")
        color = QColorDialog.getColor(current_color, self, "اختر لون التمييز")

        if color.isValid():
            self.accent_color_input.setText(color.name())

    def save_current_page_settings(self):
        """حفظ إعدادات الصفحة الحالية مؤقتاً للحفاظ عليها عند التنقل"""
        try:
            # حفظ جميع التغييرات الحالية من الواجهة مؤقتاً
            current_settings = self.get_current_settings()

            # تحديث البيانات المؤقتة (بدون حفظ نهائي)
            for key, value in current_settings.items():
                self.settings_data[key] = value

            print(f"تم حفظ الإعدادات مؤقتاً للتنقل بين الصفحات")

        except Exception as e:
            print(f"خطأ في حفظ الإعدادات المؤقتة: {e}")

    def go_to_step(self, step):
        """الانتقال إلى خطوة محددة مع حفظ التغييرات"""
        if 0 <= step < len(self.step_indicator.steps):
            # حفظ إعدادات الصفحة الحالية قبل الانتقال
            self.save_current_page_settings()

            # تحميل الصفحة المطلوبة إذا لم تكن محملة
            self.load_page_on_demand(step)

            self.current_step = step
            self.content_stack.setCurrentIndex(step)
            self.step_indicator.set_current_step(step)
            self.update_navigation_buttons()

            # تحديث تقرير التغييرات في صفحة الحفظ
            if step == 0:  # صفحة الحفظ (الفهرس 0)
                self.update_changes_report()

    def next_step(self):
        """الانتقال للخطوة التالية"""
        if self.current_step > 0:  # يمكن الانتقال للخطوة السابقة (فهرس أقل)
            self.go_to_step(self.current_step - 1)

    def previous_step(self):
        """الانتقال للخطوة السابقة"""
        if self.current_step < len(self.step_indicator.steps) - 1:  # يمكن الانتقال للخطوة التالية (فهرس أكبر)
            self.go_to_step(self.current_step + 1)

    def update_navigation_buttons(self):
        """تحديث حالة أزرار التنقل مع نظام السمة"""
        # الحصول على لون السمة الحالي
        try:
            from .theme_manager import global_theme_manager
            current_theme = global_theme_manager.get_current_theme()
            theme_color = current_theme.get('accent_color', '#ff6f00')
        except:
            theme_color = '#ff6f00'

        # زر التالي (← التالي) - شفاف مثل الصورة
        if self.current_step > 0:
            self.next_btn.setEnabled(True)
            self.next_btn.set_icon_color("#ffffff")  # أبيض شفاف
        else:
            self.next_btn.setEnabled(False)
            self.next_btn.set_icon_color("#666666")  # لون معطل

        # زر السابق (السابق →) - شفاف مثل الصورة
        if self.current_step < len(self.step_indicator.steps) - 1:
            self.prev_btn.setEnabled(True)
            self.prev_btn.set_icon_color("#ffffff")  # أبيض شفاف
        else:
            self.prev_btn.setEnabled(False)
            self.prev_btn.set_icon_color("#666666")  # لون معطل

    def update_changes_report(self):
        """تحديث تقرير التغييرات مع معالجة أخطاء محسنة"""
        try:
            current_settings = self.get_current_settings()
            changes = []

            # مقارنة الإعدادات مع معالجة آمنة
            try:
                if hasattr(self, 'theme_combo') and self.theme_combo:
                    original_theme = self.original_settings.get("theme", "dark")
                    current_theme = self.theme_combo.currentText()
                    if original_theme != current_theme:
                        changes.append(f"• السمة: {original_theme} ← {current_theme}")
            except Exception as e:
                print(f"خطأ في مقارنة السمة: {e}")

            try:
                if hasattr(self, 'accent_color_input') and self.accent_color_input:
                    original_color = self.original_settings.get("accent_color", "#ff6f00")
                    current_color = self.accent_color_input.text() or "#ff6f00"
                    if original_color != current_color:
                        changes.append(f"• لون التمييز: {original_color} ← {current_color}")
            except Exception as e:
                print(f"خطأ في مقارنة لون التمييز: {e}")

            # مقارنة إعدادات الخطوط الجديدة
            try:
                if hasattr(self, 'font_size_slider') and self.font_size_slider:
                    original_font_size = self.original_settings.get("ui_settings", {}).get("font_size", 16)
                    current_font_size = self.font_size_slider.value()
                    if original_font_size != current_font_size:
                        changes.append(f"• حجم الخط: {original_font_size} ← {current_font_size}")
            except Exception as e:
                print(f"خطأ في مقارنة حجم الخط: {e}")

            try:
                if hasattr(self, 'font_family_combo') and self.font_family_combo:
                    original_font_family = self.original_settings.get("ui_settings", {}).get("font_family", "النظام الافتراضي")
                    current_font_family = self.font_family_combo.currentText()
                    if original_font_family != current_font_family:
                        changes.append(f"• نوع الخط: {original_font_family} ← {current_font_family}")
            except Exception as e:
                print(f"خطأ في مقارنة نوع الخط: {e}")

            try:
                if hasattr(self, 'font_weight_combo') and self.font_weight_combo:
                    original_font_weight = self.original_settings.get("ui_settings", {}).get("font_weight", "عادي")
                    current_font_weight = self.font_weight_combo.currentText()
                    if original_font_weight != current_font_weight:
                        changes.append(f"• وزن الخط: {original_font_weight} ← {current_font_weight}")
            except Exception as e:
                print(f"خطأ في مقارنة وزن الخط: {e}")

            try:
                if hasattr(self, 'show_tooltips_check') and self.show_tooltips_check:
                    original_tooltips = self.original_settings.get("ui_settings", {}).get("show_tooltips", True)
                    current_tooltips = self.show_tooltips_check.isChecked()
                    if original_tooltips != current_tooltips:
                        status = "مُفعل" if current_tooltips else "مُعطل"
                        changes.append(f"• إظهار التلميحات: {status}")
            except Exception as e:
                print(f"خطأ في مقارنة التلميحات: {e}")

            try:
                if hasattr(self, 'enable_animations_check') and self.enable_animations_check:
                    original_animations = self.original_settings.get("ui_settings", {}).get("enable_animations", True)
                    current_animations = self.enable_animations_check.isChecked()
                    if original_animations != current_animations:
                        status = "مُفعل" if current_animations else "مُعطل"
                        changes.append(f"• الحركات والتأثيرات: {status}")
            except Exception as e:
                print(f"خطأ في مقارنة الحركات: {e}")

            try:
                if hasattr(self, 'text_direction_combo') and self.text_direction_combo:
                    original_direction = self.original_settings.get("ui_settings", {}).get("text_direction", "تلقائي")
                    current_direction = self.text_direction_combo.currentText()
                    if original_direction != current_direction:
                        changes.append(f"• اتجاه النص: {original_direction} ← {current_direction}")
            except Exception as e:
                print(f"خطأ في مقارنة اتجاه النص: {e}")

            # مقارنة إعدادات السمة المتقدمة
            try:
                if hasattr(self, 'transparency_slider') and self.transparency_slider:
                    original_transparency = self.original_settings.get("ui_settings", {}).get("transparency", 80)
                    current_transparency = self.transparency_slider.value()
                    if original_transparency != current_transparency:
                        changes.append(f"• مستوى الشفافية: {original_transparency}% ← {current_transparency}%")
            except Exception as e:
                print(f"خطأ في مقارنة الشفافية: {e}")

            try:
                if hasattr(self, 'size_combo') and self.size_combo:
                    original_size = self.original_settings.get("ui_settings", {}).get("size", "متوسط (افتراضي)")
                    current_size = self.size_combo.currentText()
                    if original_size != current_size:
                        changes.append(f"• حجم العناصر: {original_size} ← {current_size}")
            except Exception as e:
                print(f"خطأ في مقارنة حجم العناصر: {e}")

            try:
                if hasattr(self, 'contrast_combo') and self.contrast_combo:
                    original_contrast = self.original_settings.get("ui_settings", {}).get("contrast", "عادي (متوازن)")
                    current_contrast = self.contrast_combo.currentText()
                    if original_contrast != current_contrast:
                        changes.append(f"• مستوى التباين: {original_contrast} ← {current_contrast}")
            except Exception as e:
                print(f"خطأ في مقارنة التباين: {e}")

            # مقارنة الإعدادات المتقدمة
            try:
                if hasattr(self, 'max_memory_slider') and self.max_memory_slider:
                    original_memory = self.original_settings.get("advanced_settings", {}).get("max_memory", 512)
                    current_memory = self.max_memory_slider.value()
                    if original_memory != current_memory:
                        changes.append(f"• الحد الأقصى للذاكرة: {original_memory} ميجابايت ← {current_memory} ميجابايت")
            except Exception as e:
                print(f"خطأ في مقارنة الذاكرة: {e}")

            try:
                if hasattr(self, 'enable_backup_check') and self.enable_backup_check:
                    original_backup = self.original_settings.get("advanced_settings", {}).get("enable_backup", True)
                    current_backup = self.enable_backup_check.isChecked()
                    if original_backup != current_backup:
                        status = "مُفعل" if current_backup else "مُعطل"
                        changes.append(f"• النسخ الاحتياطي: {status}")
            except Exception as e:
                print(f"خطأ في مقارنة النسخ الاحتياطي: {e}")

            try:
                if hasattr(self, 'enable_password_check') and self.enable_password_check:
                    original_password = self.original_settings.get("security_settings", {}).get("enable_password_protection", False)
                    current_password = self.enable_password_check.isChecked()
                    if original_password != current_password:
                        status = "مُفعل" if current_password else "مُعطل"
                        changes.append(f"• حماية كلمة المرور: {status}")
            except Exception as e:
                print(f"خطأ في مقارنة حماية كلمة المرور: {e}")

            # إنشاء التقرير
            if changes:
                report = "التغييرات المطبقة:\n\n" + "\n".join(changes)
                report += f"\n\nإجمالي التغييرات: {len(changes)}"
            else:
                report = "لم يتم إجراء أي تغييرات على الإعدادات."

            if hasattr(self, 'changes_report') and self.changes_report:
                self.changes_report.setText(report)

        except Exception as e:
            error_msg = f"خطأ في تحليل التغييرات: {str(e)}"
            print(error_msg)
            if hasattr(self, 'changes_report') and self.changes_report:
                self.changes_report.setText(error_msg)

    def get_current_settings(self):
        """الحصول على الإعدادات الحالية من الواجهة"""
        current = {}

        try:
            if hasattr(self, 'theme_combo'):
                current["theme"] = self.theme_combo.currentText()
                current["accent_color"] = self.accent_color_input.text() or "#ff6f00"

                ui_settings = {}
                # إعدادات الخطوط
                if hasattr(self, 'font_size_slider'):
                    ui_settings["font_size"] = self.font_size_slider.value()
                if hasattr(self, 'font_family_combo'):
                    ui_settings["font_family"] = self.font_family_combo.currentText()
                if hasattr(self, 'font_weight_combo'):
                    ui_settings["font_weight"] = self.font_weight_combo.currentText()
                if hasattr(self, 'text_direction_combo'):
                    ui_settings["text_direction"] = self.text_direction_combo.currentText()

                # إعدادات النصوص
                if hasattr(self, 'show_tooltips_check'):
                    ui_settings["show_tooltips"] = self.show_tooltips_check.isChecked()
                if hasattr(self, 'enable_animations_check'):
                    ui_settings["enable_animations"] = self.enable_animations_check.isChecked()

                # إعدادات السمة المتقدمة
                if hasattr(self, 'transparency_slider'):
                    ui_settings["transparency"] = self.transparency_slider.value()
                if hasattr(self, 'size_combo'):
                    ui_settings["size"] = self.size_combo.currentText()
                if hasattr(self, 'contrast_combo'):
                    ui_settings["contrast"] = self.contrast_combo.currentText()

                current["ui_settings"] = ui_settings

            if hasattr(self, 'compression_slider'):
                current["compression_level"] = self.compression_slider.value()

                merge_settings = {}
                if hasattr(self, 'add_bookmarks_check'):
                    merge_settings["add_bookmarks"] = self.add_bookmarks_check.isChecked()
                if hasattr(self, 'preserve_metadata_check'):
                    merge_settings["preserve_metadata"] = self.preserve_metadata_check.isChecked()
                current["merge_settings"] = merge_settings

            if hasattr(self, 'max_memory_slider'):
                performance_settings = {
                    "max_memory_usage": self.max_memory_slider.value(),
                    "enable_multithreading": self.enable_multithreading_check.isChecked()
                }
                current["performance_settings"] = performance_settings

            if hasattr(self, 'enable_password_check'):
                security_settings = {
                    "enable_password_protection": self.enable_password_check.isChecked(),
                    "privacy_mode": self.privacy_mode_check.isChecked()
                }
                current["security_settings"] = security_settings

        except Exception as e:
            print(f"خطأ في الحصول على الإعدادات: {e}")

        return current

    # ===============================
    # دوال مساعدة لتقليل التكرار
    # ===============================

    def get_current_theme_settings(self):
        """الحصول على إعدادات السمة الحالية - دالة مساعدة"""
        if hasattr(self, 'theme_combo') and hasattr(self, 'accent_color_input'):
            return {
                'theme': self.theme_combo.currentText(),
                'accent_color': self.accent_color_input.text() or "#ff6f00"
            }
        return {'theme': 'dark', 'accent_color': '#ff6f00'}

    def apply_theme_safely(self, theme_name=None, accent_color=None):
        """تطبيق السمة بشكل آمن - دالة مساعدة"""
        try:
            if not theme_name or not accent_color:
                theme_settings = self.get_current_theme_settings()
                theme_name = theme_settings['theme']
                accent_color = theme_settings['accent_color']

            # التحقق من صحة اللون
            is_valid, _ = self.validate_color(accent_color)
            if not is_valid:
                accent_color = "#ff6f00"  # لون افتراضي آمن

            from .theme_manager import global_theme_manager
            global_theme_manager.change_theme(theme_name, accent_color)
            return True
        except Exception as e:
            print(f"خطأ في تطبيق السمة: {e}")
            return False

    def show_error_message(self, title, message, details=None):
        """عرض رسالة خطأ موحدة - دالة مساعدة"""
        full_message = message
        if details:
            full_message += f"\n\nتفاصيل: {details}"
        msg = QMessageBox(QMessageBox.Critical, title, full_message, parent=self)
        apply_theme_style(msg, "dialog")
        msg.exec()

    def show_success_message(self, title, message, details=None):
        """عرض رسالة نجاح موحدة - دالة مساعدة"""
        full_message = message
        if details:
            full_message += f"\n\n{details}"
        msg = QMessageBox(QMessageBox.Information, title, full_message, parent=self)
        apply_theme_style(msg, "dialog")
        msg.exec()

    # ===============================
    # دوال الحفظ والتحميل والإدارة
    # ===============================

    def save_all_settings(self):
        """
        حفظ جميع الإعدادات عن طريق تفويض المهمة إلى مدير الإعدادات.
        """
        try:
            # 1. الحصول على الإعدادات الحالية من الواجهة
            current_settings = self.get_current_settings()

            # 2. دمج الإعدادات الجديدة مع البيانات الحالية
            self.settings_data.update(current_settings)

            # 3. تفويض الحفظ والنسخ الاحتياطي والتحقق إلى مدير الإعدادات
            if settings.save_settings(self.settings_data, self.original_settings):
                
                # 4. تحديث السمة في مدير السمات مع الخيارات
                theme_name = self.theme_combo.currentText()
                accent_color = self.accent_color_input.text() or "#ff6f00"

                # جمع خيارات السمة من الواجهة
                options = {}
                if hasattr(self, 'transparency_slider'):
                    options["transparency"] = self.transparency_slider.value()
                if hasattr(self, 'size_combo'):
                    options["size"] = self.size_combo.currentText()
                if hasattr(self, 'contrast_combo'):
                    options["contrast"] = self.contrast_combo.currentText()
                if hasattr(self, 'font_size_slider'):
                    options["font_size"] = self.font_size_slider.value()

                # تطبيق السمة مع جميع الخيارات
                global_theme_manager.change_theme(theme_name, accent_color, options)

                # تطبيق إعدادات الخطوط على جميع العناصر
                from .theme_manager import refresh_all_fonts
                refresh_all_fonts()

                # 5. تحديث الحالة الداخلية للنافذة
                self.original_settings = self.settings_data.copy()
                self.has_unsaved_changes = False
                self.update_changes_report()
                
                # 6. إعلام باقي التطبيق بالتغييرات
                self.settings_changed.emit()

                # 7. عرض رسالة نجاح
                self.show_success_message("نجح", "تم حفظ جميع الإعدادات بنجاح!")
                return True
            else:
                # مدير الإعدادات فشل في الحفظ
                self.show_error_message("خطأ", "فشل في حفظ الإعدادات.", "يرجى مراجعة سجلات التطبيق.")
                return False

        except Exception as e:
            error_message = f"حدث خطأ غير متوقع أثناء الحفظ:\n{str(e)}"
            self.show_error_message("خطأ خطير", error_message)
            return False

    def cancel_changes(self):
        """إلغاء جميع التغييرات"""
        msg = QMessageBox(QMessageBox.Question, "تأكيد",
            "هل أنت متأكد من إلغاء جميع التغييرات؟",
            QMessageBox.Yes | QMessageBox.No, parent=self)
        msg.setDefaultButton(QMessageBox.No)
        apply_theme_style(msg, "dialog")
        reply = msg.exec()

        if reply == QMessageBox.Yes:
            self.load_original_settings()
            self.update_changes_report()
            self.has_unsaved_changes = False  # إعادة تعيين حالة التغييرات
            self.update_preview_only()  # تحديث المعاينة للإعدادات الأصلية
            msg = QMessageBox(QMessageBox.Information, "تم", "تم إلغاء جميع التغييرات!", parent=self)
            apply_theme_style(msg, "dialog")
            msg.exec()

    def load_original_settings(self):
        """تحميل الإعدادات الأصلية"""
        try:
            if hasattr(self, 'theme_combo'):
                # منع إرسال الإشارات أثناء التحميل
                self.theme_combo.blockSignals(True)
                self.accent_color_input.blockSignals(True)

                self.theme_combo.setCurrentText(self.original_settings.get("theme", "dark"))
                self.accent_color_input.setText(self.original_settings.get("accent_color", "#ff6f00"))

                # إعادة تفعيل الإشارات
                self.theme_combo.blockSignals(False)
                self.accent_color_input.blockSignals(False)

                ui_settings = self.original_settings.get("ui_settings", {})

                # تحميل إعدادات الخطوط الأصلية
                if hasattr(self, 'font_size_slider'):
                    self.font_size_slider.setValue(ui_settings.get("font_size", 16))
                if hasattr(self, 'font_family_combo'):
                    font_family = ui_settings.get("font_family", "النظام الافتراضي")
                    index = self.font_family_combo.findText(font_family)
                    if index >= 0:
                        self.font_family_combo.setCurrentIndex(index)
                if hasattr(self, 'font_weight_combo'):
                    font_weight = ui_settings.get("font_weight", "عادي")
                    index = self.font_weight_combo.findText(font_weight)
                    if index >= 0:
                        self.font_weight_combo.setCurrentIndex(index)
                if hasattr(self, 'text_direction_combo'):
                    text_direction = ui_settings.get("text_direction", "تلقائي")
                    index = self.text_direction_combo.findText(text_direction)
                    if index >= 0:
                        self.text_direction_combo.setCurrentIndex(index)

                # تحميل إعدادات النصوص الأصلية
                if hasattr(self, 'show_tooltips_check'):
                    self.show_tooltips_check.setChecked(ui_settings.get("show_tooltips", True))
                if hasattr(self, 'enable_animations_check'):
                    self.enable_animations_check.setChecked(ui_settings.get("enable_animations", True))

                # تحميل إعدادات السمة المتقدمة الأصلية
                if hasattr(self, 'transparency_slider'):
                    self.transparency_slider.setValue(ui_settings.get("transparency", 80))
                if hasattr(self, 'size_combo'):
                    size = ui_settings.get("size", "متوسط (افتراضي)")
                    index = self.size_combo.findText(size)
                    if index >= 0:
                        self.size_combo.setCurrentIndex(index)
                if hasattr(self, 'contrast_combo'):
                    contrast = ui_settings.get("contrast", "عادي (متوازن)")
                    index = self.contrast_combo.findText(contrast)
                    if index >= 0:
                        self.contrast_combo.setCurrentIndex(index)

            if hasattr(self, 'compression_slider'):
                self.compression_slider.setValue(self.original_settings.get("compression_level", 3))

                merge_settings = self.original_settings.get("merge_settings", {})
                if hasattr(self, 'add_bookmarks_check'):
                    self.add_bookmarks_check.setChecked(merge_settings.get("add_bookmarks", True))
                if hasattr(self, 'preserve_metadata_check'):
                    self.preserve_metadata_check.setChecked(merge_settings.get("preserve_metadata", True))

            if hasattr(self, 'max_memory_slider'):
                performance_settings = self.original_settings.get("performance_settings", {})
                self.max_memory_slider.setValue(performance_settings.get("max_memory_usage", 512))
                self.enable_multithreading_check.setChecked(performance_settings.get("enable_multithreading", True))

            if hasattr(self, 'enable_password_check'):
                security_settings = self.original_settings.get("security_settings", {})
                self.enable_password_check.setChecked(security_settings.get("enable_password_protection", False))
                self.privacy_mode_check.setChecked(security_settings.get("privacy_mode", False))

        except Exception as e:
            print(f"خطأ في تحميل الإعدادات الأصلية: {e}")

    def load_current_settings_to_ui(self):
        """تحميل الإعدادات المؤقتة إلى الواجهة"""
        try:
            if hasattr(self, 'theme_combo'):
                # منع إرسال الإشارات أثناء التحميل
                self.theme_combo.blockSignals(True)
                self.accent_color_input.blockSignals(True)

                # تحميل من البيانات المؤقتة (settings_data) التي تحتوي على التغييرات
                self.theme_combo.setCurrentText(self.settings_data.get("theme", "dark"))
                self.accent_color_input.setText(self.settings_data.get("accent_color", "#ff6f00"))

                # إعادة تفعيل الإشارات
                self.theme_combo.blockSignals(False)
                self.accent_color_input.blockSignals(False)

                print(f"تم تحميل الإعدادات المؤقتة: السمة={self.settings_data.get('theme')}, اللون={self.settings_data.get('accent_color')}")

                ui_settings = self.settings_data.get("ui_settings", {})

                # تحميل إعدادات الخطوط
                if hasattr(self, 'font_size_slider'):
                    self.font_size_slider.setValue(ui_settings.get("font_size", 16))
                if hasattr(self, 'font_family_combo'):
                    font_family = ui_settings.get("font_family", "النظام الافتراضي")
                    index = self.font_family_combo.findText(font_family)
                    if index >= 0:
                        self.font_family_combo.setCurrentIndex(index)
                if hasattr(self, 'font_weight_combo'):
                    font_weight = ui_settings.get("font_weight", "عادي")
                    index = self.font_weight_combo.findText(font_weight)
                    if index >= 0:
                        self.font_weight_combo.setCurrentIndex(index)
                if hasattr(self, 'text_direction_combo'):
                    text_direction = ui_settings.get("text_direction", "تلقائي")
                    index = self.text_direction_combo.findText(text_direction)
                    if index >= 0:
                        self.text_direction_combo.setCurrentIndex(index)

                # تحميل إعدادات النصوص
                if hasattr(self, 'show_tooltips_check'):
                    self.show_tooltips_check.setChecked(ui_settings.get("show_tooltips", True))
                if hasattr(self, 'enable_animations_check'):
                    self.enable_animations_check.setChecked(ui_settings.get("enable_animations", True))

                # تحميل إعدادات السمة المتقدمة
                if hasattr(self, 'transparency_slider'):
                    self.transparency_slider.setValue(ui_settings.get("transparency", 80))
                if hasattr(self, 'size_combo'):
                    size = ui_settings.get("size", "متوسط (افتراضي)")
                    index = self.size_combo.findText(size)
                    if index >= 0:
                        self.size_combo.setCurrentIndex(index)
                if hasattr(self, 'contrast_combo'):
                    contrast = ui_settings.get("contrast", "عادي (متوازن)")
                    index = self.contrast_combo.findText(contrast)
                    if index >= 0:
                        self.contrast_combo.setCurrentIndex(index)

            if hasattr(self, 'compression_slider'):
                self.compression_slider.setValue(self.settings_data.get("compression_level", 3))

                merge_settings = self.settings_data.get("merge_settings", {})
                if hasattr(self, 'add_bookmarks_check'):
                    self.add_bookmarks_check.setChecked(merge_settings.get("add_bookmarks", True))
                if hasattr(self, 'preserve_metadata_check'):
                    self.preserve_metadata_check.setChecked(merge_settings.get("preserve_metadata", True))

            # تحميل إعدادات الأمان
            security_settings = self.settings_data.get("security_settings", {})
            if hasattr(self, 'enable_password_check'):
                self.enable_password_check.setChecked(security_settings.get("enable_password_protection", False))

            # تحميل الألوان المخصصة وتطبيقها
            custom_colors = self.settings_data.get("custom_colors", {})
            if custom_colors:
                from .theme_manager import global_theme_manager
                current_theme = global_theme_manager.current_theme

                # تطبيق الألوان المخصصة على السمة الحالية
                if custom_colors.get("text_title") != "افتراضي":
                    global_theme_manager.themes[current_theme]["text_title"] = custom_colors.get("text_title")
                if custom_colors.get("text_body") != "افتراضي":
                    global_theme_manager.themes[current_theme]["text_body"] = custom_colors.get("text_body")
                if custom_colors.get("text_secondary") != "افتراضي":
                    global_theme_manager.themes[current_theme]["text_secondary"] = custom_colors.get("text_secondary")

                # تحديث القوائم المنسدلة للألوان
                if hasattr(self, 'title_color_combo'):
                    title_color_text = self.get_combo_text_from_color(custom_colors.get("text_title", "افتراضي"))
                    self.title_color_combo.setCurrentText(title_color_text)
                if hasattr(self, 'body_color_combo'):
                    body_color_text = self.get_combo_text_from_color(custom_colors.get("text_body", "افتراضي"))
                    self.body_color_combo.setCurrentText(body_color_text)
                if hasattr(self, 'secondary_color_combo'):
                    secondary_color_text = self.get_combo_text_from_color(custom_colors.get("text_secondary", "افتراضي"))
                    self.secondary_color_combo.setCurrentText(secondary_color_text)

        except Exception as e:
            print(f"خطأ في تحميل الإعدادات الحالية: {e}")

    def on_theme_changed(self, theme_name):
        """تحديث المعاينة فقط عند تغيير السمة - بدون تطبيق على البرنامج"""
        try:
            # تحديث المعاينة فقط
            self.update_preview_only()

            # حفظ في الذاكرة المؤقتة فقط
            self.settings_data["theme"] = theme_name
            self.has_unsaved_changes = True

            # تحديث تقرير التغييرات
            QTimer.singleShot(100, self.update_changes_report)

            print(f"تم تحديث المعاينة للسمة: {theme_name}")

        except Exception as e:
            print(f"خطأ في تحديث المعاينة: {e}")

    def on_accent_color_changed(self, color_text):
        """تحديث المعاينة فقط عند تغيير لون التمييز"""
        try:
            # التحقق من صحة اللون
            if color_text.startswith("#") and len(color_text) == 7:
                # تحديث المعاينة فقط
                self.update_preview_only()

                # حفظ في الذاكرة المؤقتة فقط
                self.settings_data["accent_color"] = color_text
                self.has_unsaved_changes = True

                # تحديث تقرير التغييرات
                QTimer.singleShot(100, self.update_changes_report)

                print(f"تم تحديث معاينة اللون: {color_text}")

        except Exception as e:
            print(f"خطأ في تحديث معاينة اللون: {e}")

    def mark_as_changed(self):
        """تسجيل أن هناك تغييرات غير محفوظة وتحديث التقرير"""
        self.has_unsaved_changes = True
        # تحديث تقرير التغييرات فوراً
        QTimer.singleShot(100, self.update_changes_report)

    def on_text_color_changed(self):
        """تطبيق ألوان النصوص المخصصة"""
        try:
            # الحصول على الألوان المختارة
            title_color = self.get_color_from_combo(self.title_color_combo.currentText())
            body_color = self.get_color_from_combo(self.body_color_combo.currentText())
            secondary_color = self.get_color_from_combo(self.secondary_color_combo.currentText())

            # تحديث ألوان النصوص في theme_manager
            from .theme_manager import global_theme_manager
            current_theme = global_theme_manager.current_theme

            if title_color != "افتراضي":
                global_theme_manager.themes[current_theme]["text_title"] = title_color
            if body_color != "افتراضي":
                global_theme_manager.themes[current_theme]["text_body"] = body_color
            if secondary_color != "افتراضي":
                global_theme_manager.themes[current_theme]["text_secondary"] = secondary_color

            # حفظ الألوان المخصصة في الإعدادات
            if not hasattr(self, 'settings_data') or self.settings_data is None:
                self.settings_data = {}

            self.settings_data["custom_colors"] = {
                "text_title": title_color,
                "text_body": body_color,
                "text_secondary": secondary_color
            }

            # حفظ في ملف الإعدادات فوراً
            from modules import settings
            settings.set_setting("custom_colors", self.settings_data["custom_colors"])

            # إشعار جميع العناصر بتغيير الألوان
            current_accent = global_theme_manager.current_accent
            global_theme_manager.change_theme(current_theme, current_accent)

            # إعادة تطبيق نمط الاسكرول في الصفحة الحالية
            current_page = self.content_stack.currentWidget()
            if current_page:
                # البحث عن QScrollArea في الصفحة الحالية
                scroll_areas = current_page.findChildren(QScrollArea)
                for scroll_area in scroll_areas:
                    scroll_area.setStyleSheet(self.get_scroll_area_style())

        except Exception as e:
            print(f"خطأ في تطبيق ألوان النصوص: {e}")

    def get_color_from_combo(self, combo_text):
        """تحويل نص الكومبو إلى كود لون"""
        color_map = {
            "افتراضي": "افتراضي",
            "أبيض": "#ffffff",
            "أسود": "#000000",
            "رمادي فاتح": "#e2e8f0",
            "رمادي متوسط": "#a0aec0",
            "رمادي داكن": "#4a5568",
            "أزرق داكن": "#2d3748",
            "أخضر داكن": "#1a202c"
        }
        return color_map.get(combo_text, "افتراضي")

    def get_combo_text_from_color(self, color_code):
        """تحويل كود اللون إلى نص الكومبو"""
        color_map = {
            "افتراضي": "افتراضي",
            "#ffffff": "أبيض",
            "#000000": "أسود",
            "#e2e8f0": "رمادي فاتح",
            "#a0aec0": "رمادي متوسط",
            "#4a5568": "رمادي داكن",
            "#2d3748": "أزرق داكن",
            "#1a202c": "أخضر داكن"
        }
        return color_map.get(color_code, "افتراضي")

    def apply_current_theme(self):
        """تطبيق السمة الحالية على النافذة فقط - بدون تغيير النظام العام"""
        try:
            # السمة الحالية يتم الحصول عليها من المدير العام مباشرة
            from .theme_manager import apply_theme_style
            apply_theme_style(
                widget=self,
                widget_type="settings_window",
                auto_register=False  # لا نريد تسجيل تلقائي
            )

            # تطبيق السمة على الفريم الكبير أيضاً
            if hasattr(self, 'content_frame'):
                apply_theme_style(self.content_frame, "frame", auto_register=False)

            theme_name = global_theme_manager.current_theme
            accent_color = global_theme_manager.current_accent
            print(f"تم تطبيق السمة على نافذة الإعدادات فقط: {theme_name}, {accent_color}")

        except Exception as e:
            print(f"خطأ في تطبيق السمة على النافذة: {e}")



    def update_preview_only(self):
        """تحديث المعاينة - مبسط بعد حذف عناصر المعاينة"""
        try:
            # التحقق من وجود العناصر الأساسية فقط
            if not all(hasattr(self, attr) for attr in [
                'theme_combo', 'accent_color_input'
            ]):
                return

            # حفظ الإعدادات في الذاكرة المؤقتة للمعاينة
            preview_theme = self.theme_combo.currentText()
            preview_accent = self.accent_color_input.text() or "#ff6f00"

            # تحديث البيانات المؤقتة
            self.settings_data["theme"] = preview_theme
            self.settings_data["accent_color"] = preview_accent

            # تحديث إعدادات UI إذا كانت متوفرة
            ui_settings = self.settings_data.get("ui_settings", {})
            if hasattr(self, 'transparency_slider'):
                ui_settings["transparency"] = self.transparency_slider.value()
            if hasattr(self, 'size_combo'):
                ui_settings["size"] = self.size_combo.currentText()
            if hasattr(self, 'contrast_combo'):
                ui_settings["contrast"] = self.contrast_combo.currentText()

            self.settings_data["ui_settings"] = ui_settings

        except Exception as e:
            print(f"خطأ في تحديث المعاينة: {e}")
            # في حالة الخطأ، تأكد من إعادة السمة الأصلية
            if 'original_theme' in locals():
                global_theme_manager.change_theme(original_theme, original_accent, original_options)

    def get_accent_button_style(self):
        """تنسيق زر بلون التمييز الزجاجي"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 180, 180, 0.25),
                    stop:0.5 rgba(180, 180, 180, 0.15),
                    stop:1 rgba(255, 111, 0, 0.6));
                border: 1px solid rgba(255, 111, 0, 0.8);
                border-radius: 12px;
                color: white;
                font-weight: bold;
                padding: 12px 20px;

            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 180, 180, 0.35),
                    stop:0.5 rgba(180, 180, 180, 0.25),
                    stop:1 rgba(255, 111, 0, 0.8));
                border: 1px solid rgba(255, 111, 0, 1.0);

            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 180, 180, 0.15),
                    stop:0.5 rgba(180, 180, 180, 0.05),
                    stop:1 rgba(255, 111, 0, 0.4));
                border: 1px solid rgba(255, 111, 0, 0.6);

            }
        """

    def on_transparency_changed(self, value):
        """تغيير مستوى الشفافية"""
        self.transparency_value.setText(f"{value}%")
        self.preview_current_theme()

    def on_theme_options_changed(self):
        """تغيير خيارات السمة - النظام الجديد"""
        try:
            theme_name = self.theme_combo.currentText()
            accent_color = self.accent_color_input.text() or "#ff6f00"

            # جمع الخيارات الجديدة
            options = {
                "transparency": self.transparency_slider.value(),
                "size": self.size_combo.currentText(),
                "contrast": self.contrast_combo.currentText()
            }

            # تطبيق فوري للخيارات الجديدة
            global_theme_manager.change_theme(theme_name, accent_color, options)

            # تحديث المعاينة أيضاً
            self.preview_current_theme()

        except Exception as e:
            print(f"خطأ في تطبيق خيارات السمة: {e}")

    def preview_current_theme(self):
        """معاينة السمة الحالية مع الخيارات"""
        try:
            theme_name = self.theme_combo.currentText()
            accent_color = self.accent_color_input.text() or "#ff6f00"
            transparency = self.transparency_slider.value()
            size = self.size_combo.currentText()
            contrast = self.contrast_combo.currentText()

            # تم تعطيل المعاينة لعدم وجود preview_widget
            # preview_style = self.generate_preview_style(theme_name, accent_color, transparency, size, contrast)
            # self.preview_widget.setStyleSheet(preview_style)

        except Exception as e:
            print(f"خطأ في معاينة السمة: {e}")

    def generate_preview_style(self, theme, accent, transparency, size, contrast):
        """توليد نمط المعاينة"""
        # تحويل النصوص إلى قيم
        transparency_value = transparency / 100.0

        size_values = {
            "صغير (مدمج)": {"font": 12, "padding": "6px 10px"},
            "متوسط (افتراضي)": {"font": 14, "padding": "8px 12px"},
            "كبير (مريح)": {"font": 16, "padding": "10px 14px"},
            "كبير جداً (إمكانية وصول)": {"font": 18, "padding": "12px 16px"}
        }

        contrast_values = {
            "منخفض (ناعم)": {"bg": 0.05, "border": 0.1, "text": 0.7},
            "عادي (متوازن)": {"bg": 0.08, "border": 0.15, "text": 0.9},
            "عالي (واضح)": {"bg": 0.12, "border": 0.25, "text": 1.0},
            "عالي جداً (إمكانية وصول)": {"bg": 0.2, "border": 0.4, "text": 1.0}
        }

        size_config = size_values.get(size, size_values["متوسط (افتراضي)"])
        contrast_config = contrast_values.get(contrast, contrast_values["عادي (متوازن)"])

        # ألوان السمة
        theme_colors = {
            "dark": {"bg": "#0a0a0a", "text": "255, 255, 255"},
            "light": {"bg": "#f5f5f5", "text": "45, 55, 72"},
            "blue": {"bg": "#0f1419", "text": "226, 232, 240"},
            "green": {"bg": "#0f1419", "text": "226, 232, 240"},
            "purple": {"bg": "#0f1419", "text": "226, 232, 240"}
        }

        colors = theme_colors.get(theme, theme_colors["dark"])

        return f"""
            QFrame {{
                background: rgba({colors["text"]}, {contrast_config["bg"] * transparency_value});
                border: 1px solid rgba({colors["text"]}, {contrast_config["border"] * transparency_value});
                border-radius: 8px;
            }}
            QLabel {{
                color: rgba({colors["text"]}, {contrast_config["text"]});
                font-size: {size_config["font"]}px;
                background: transparent;
                border: none;
            }}
            QPushButton {{
                background: rgba({colors["text"]}, {contrast_config["bg"] * transparency_value});
                border: 1px solid rgba({colors["text"]}, {contrast_config["border"] * transparency_value});
                border-radius: 6px;
                color: rgba({colors["text"]}, {contrast_config["text"]});
                font-size: {size_config["font"]}px;
                padding: {size_config["padding"]};
            }}
            QLineEdit, QComboBox {{
                background: rgba({colors["text"]}, {contrast_config["bg"] * transparency_value});
                border: 1px solid rgba({colors["text"]}, {contrast_config["border"] * transparency_value});
                border-radius: 6px;
                color: rgba({colors["text"]}, {contrast_config["text"]});
                font-size: {size_config["font"]}px;
                padding: {size_config["padding"]};
            }}
        """



    def get_scroll_area_style(self):
        """تنسيق منطقة التمرير - ربط مباشر بالمدير المركزي"""
        colors = global_theme_manager.get_current_colors()
        accent = global_theme_manager.current_accent
        return f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {accent};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['text_accent']};
            }}
            QScrollBar::handle:vertical:pressed {{
                background: {colors['text']};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """
