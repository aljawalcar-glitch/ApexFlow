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
    QFileDialog, QMessageBox, QFormLayout, QFrame, QScrollArea, QStackedWidget,
    QApplication, QDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from modules import settings
from .theme_manager import global_theme_manager, apply_theme_style
from .ui_helpers import FocusAwareComboBox
from .theme_aware_widget import ThemeAwareDialog
from .svg_icon_button import create_navigation_button
from .notification_system import show_success, show_warning, show_error, show_info
from modules.translator import tr, reload_translations

# حل مشكلة theme_manager
theme_manager = global_theme_manager

class StepIndicator(QWidget):
    """مؤشر الخطوات في الأعلى"""
    
    step_clicked = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 3  # البدء من المظهر (الفهرس 3)
        self.steps = [tr("step_save"), tr("step_general_settings"), tr("step_fonts"), tr("step_appearance")]  # عكس الترتيب
        self.setup_ui()
        
    def _style_step_button(self, btn, is_current_step=False):
        """Applies the standard style to a step button."""
        from .theme_manager import apply_theme, global_theme_manager
        from .global_styles import get_font_settings
        font_settings = get_font_settings()
        apply_theme(btn, "button")

        if global_theme_manager.current_theme == "light":
            text_color = "#333333" 
            hover_bg = "rgba(0, 0, 0, 0.1)"
        else:
            text_color = "#ffffff"
            hover_bg = "rgba(255, 255, 255, 0.1)"

        btn.setStyleSheet(f'''
            QPushButton {{
                background: transparent;
                border: none;
                outline: none;
                font-size: {font_settings['size']}px;
                font-weight: {"bold" if is_current_step else "normal"};
                padding: 15px 25px;
                color: {text_color};
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
        ''')

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
            
            self._style_step_button(btn, is_current_step=False)

            self.step_buttons.append(btn)
            layout.addWidget(btn)
        
        # مؤشر الانزلاق المحسن
        self.slider_indicator = QFrame(self)

        # استخدام نظام السمات الموحد
        from .theme_manager import apply_theme
        apply_theme(self.slider_indicator, "slider_indicator")
        self.update_slider_position()


        

    
    def set_current_step(self, step):
        """تعيين الخطوة الحالية"""
        self.current_step = step

        for i, btn in enumerate(self.step_buttons):
            is_current = (i == step)
            self._style_step_button(btn, is_current_step=is_current)
            btn.setChecked(is_current)

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
        try:
            super().__init__(parent, "settings_window")
            self.setWindowTitle(tr("settings_window_title"))

            # إعداد المدراء
            self._setup_managers(parent)

            # تحميل الإعدادات
            self.settings_data = settings.load_settings()
            self.original_settings = self.settings_data.copy()
            self.current_step = 3  # البدء من المظهر
            self.has_unsaved_changes = False
            self.is_loading = True

            # تتبع الصفحات
            self.page_widgets = []

            # إنشاء جميع العناصر مباشرة (إزالة التحميل الكسول المعقد)
            self._create_all_widgets()
            self.init_ui()

            # تحميل الإعدادات في الواجهة
            QTimer.singleShot(50, self._load_settings_to_ui)

            # إشعار ترحيب بعد تحميل الواجهة
            QTimer.singleShot(1000, self._show_welcome_notification)

            # Set loading to false after a delay
            QTimer.singleShot(500, self.finish_loading)

        except Exception as e:
            print(f"خطأ في تهيئة واجهة الإعدادات: {e}")
            import traceback
            traceback.print_exc()

    def _get_main_window(self):
        """الحصول على النافذة الرئيسية للتطبيق"""
        # محاولة الحصول على النافذة الرئيسية من خلال التسلسل الهرمي للعناصر
        parent = self.parent()
        while parent:
            # التحقق إذا كان الأصل هو النافذة الرئيسية للتطبيق
            if parent.__class__.__name__ == 'ApexFlow':
                return parent
            parent = parent.parent()

        # إذا لم يتم العثور على النافذة الرئيسية، محاولة البحث عنها في التطبيق
        from PySide6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ApexFlow':
                return widget

        # إذا لم يتم العثور على النافذة الرئيسية، إرجاع None
        return None

    def _show_welcome_notification(self):
        """إظهار رسالة ترحيب مفيدة عند فتح الإعدادات"""
        # التحقق من إعداد إلغاء رسالة الترحيب
        settings_data = settings.load_settings()
        if settings_data.get("disable_welcome_message", False):
            return
            
        # استخدام النافذة الرئيسية بدلاً من نافذة الإعدادات لعرض الإشعار
        main_window = self._get_main_window()
        if main_window:
            main_window.notification_manager.show_notification(tr("settings_welcome_message"), "info", 4000)
        else:
            # استخدام الإشعار العام بدلاً من الإشعار الخاص بالنافذة
            show_info(tr("settings_welcome_message"), duration=4000)

    def _setup_managers(self, parent):
        """إعداد المدراء المطلوبة مع معالجة الأخطاء"""
        try:
            # إعداد مدير الإشعارات
            if parent and hasattr(parent, 'notification_manager'):
                self.notification_manager = parent.notification_manager
            else:
                from ui.notification_system import global_notification_manager
                self.notification_manager = global_notification_manager
        except Exception as e:
            print(f"خطأ في إعداد مدير الإشعارات: {e}")
            self.notification_manager = None

        try:
            # إعداد مدير الرسائل
            if parent and hasattr(parent, 'message_manager'):
                self.message_manager = parent.message_manager
            else:
                from modules.app_utils import MessageManager
                self.message_manager = MessageManager(self)
        except Exception as e:
            print(f"خطأ في إعداد مدير الرسائل: {e}")
            self.message_manager = None

    def _create_all_widgets(self):
        """إنشاء جميع العناصر مباشرة"""
        # إنشاء عناصر المظهر
        self.theme_combo = FocusAwareComboBox()
        self.theme_combo.addItems(["dark", "light", "blue", "green", "purple"])

        self.accent_color_input = QLineEdit()
        self.language_combo = FocusAwareComboBox()
        self.language_combo.addItems(["العربية", "English"])

        # إنشاء عناصر الخطوط
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(8, 24)
        self.font_size_slider.setValue(12)  # حجم مثالي للقراءة

        # أحجام خطوط منفصلة
        self.title_font_size_slider = QSlider(Qt.Horizontal)
        self.title_font_size_slider.setRange(16, 32)
        self.title_font_size_slider.setValue(18)

        self.menu_font_size_slider = QSlider(Qt.Horizontal)
        self.menu_font_size_slider.setRange(10, 20)
        self.menu_font_size_slider.setValue(15)

        self.font_family_combo = FocusAwareComboBox()
        self.font_family_combo.addItems([tr("system_default_font"), "Arial", "Tahoma", "Segoe UI", "Cairo", "Amiri", "Noto Sans Arabic"])

        self.font_weight_combo = FocusAwareComboBox()
        self.font_weight_combo.addItems([tr("font_weight_normal"), tr("font_weight_bold"), tr("font_weight_extrabold")])

        self.text_direction_combo = FocusAwareComboBox()
        self.text_direction_combo.addItems([tr("text_direction_auto"), tr("text_direction_rtl"), tr("text_direction_ltr")])

        # إنشاء عناصر النصوص
        self.show_tooltips_check = QCheckBox(tr("show_tooltips_check"))
        self.enable_animations_check = QCheckBox(tr("enable_animations_check"))

        # إنشاء عناصر السمة المتقدمة
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(0, 100)
        self.transparency_slider.setValue(80)

        self.size_combo = FocusAwareComboBox()
        self.size_combo.addItems([tr("size_small"), tr("size_medium"), tr("size_large"), tr("size_xlarge")])

        self.contrast_combo = FocusAwareComboBox()
        self.contrast_combo.addItems([tr("contrast_low"), tr("contrast_normal"), tr("contrast_high"), tr("contrast_xhigh")])

        # إنشاء عناصر أخرى
        self.font_preview_label = QLabel(tr("font_preview_text"))
        self.changes_report = QLabel()

        # --- إنشاء عناصر الإعدادات العامة ---
        self.disable_welcome_checkbox = QCheckBox(tr("disable_welcome_message_option"))
        self.remember_state_checkbox = QCheckBox(tr("remember_settings_on_exit_option"))
        self.reset_to_defaults_checkbox = QCheckBox(tr("reset_to_defaults_next_time_option"))
        self.show_exit_warning_checkbox = QCheckBox(tr("show_exit_warning_option"))
        self.remember_exit_choice_checkbox = QCheckBox(tr("remember_exit_choice_option"))
        self.dont_ask_again_checkbox = QCheckBox(tr("dont_ask_again_and_discard_option"))
        self.show_success_notifications_checkbox = QCheckBox(tr("show_success_notifications"))
        self.show_warning_notifications_checkbox = QCheckBox(tr("show_warning_notifications"))
        self.show_error_notifications_checkbox = QCheckBox(tr("show_error_notifications"))
        self.show_info_notifications_checkbox = QCheckBox(tr("show_info_notifications"))

        # --- إنشاء عناصر صفحة الحفظ ---
        self.reset_defaults_btn = QPushButton(tr("reset_to_defaults_button"))
        self.save_as_default_btn = QPushButton(tr("save_as_default_button"))
        self.save_all_btn = QPushButton(tr("save_all_changes_button"))
        self.cancel_btn = QPushButton(tr("cancel_changes_button"))

        # ربط الإشارات
        self._connect_signals()

    def _connect_signals(self):
        """ربط جميع الإشارات"""
        # إشارات المظهر
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        self.accent_color_input.textChanged.connect(self._on_accent_changed)
        self.language_combo.currentTextChanged.connect(self._on_language_changed)

        # إشارات الخطوط
        self.font_size_slider.valueChanged.connect(self._on_font_changed)
        self.title_font_size_slider.valueChanged.connect(self._on_font_changed)
        self.menu_font_size_slider.valueChanged.connect(self._on_font_changed)
        self.font_family_combo.currentTextChanged.connect(self._on_font_changed)
        self.font_weight_combo.currentTextChanged.connect(self._on_font_changed)

        # إشارات السمة المتقدمة
        self.transparency_slider.valueChanged.connect(self._on_advanced_changed)
        self.size_combo.currentTextChanged.connect(self._on_advanced_changed)
        self.contrast_combo.currentTextChanged.connect(self._on_advanced_changed)

        # --- ربط إشارات الإعدادات العامة ---
        self.disable_welcome_checkbox.stateChanged.connect(self.mark_as_changed)
        self.remember_state_checkbox.stateChanged.connect(self.mark_as_changed)
        self.reset_to_defaults_checkbox.stateChanged.connect(self.mark_as_changed)
        self.reset_to_defaults_checkbox.stateChanged.connect(self.on_reset_defaults_changed)
        self.show_exit_warning_checkbox.stateChanged.connect(self.mark_as_changed)
        self.remember_exit_choice_checkbox.stateChanged.connect(self.mark_as_changed)
        self.dont_ask_again_checkbox.stateChanged.connect(self.mark_as_changed)
        self.show_success_notifications_checkbox.stateChanged.connect(self.mark_as_changed)
        self.show_warning_notifications_checkbox.stateChanged.connect(self.mark_as_changed)
        self.show_error_notifications_checkbox.stateChanged.connect(self.mark_as_changed)
        self.show_info_notifications_checkbox.stateChanged.connect(self.mark_as_changed)

        # --- ربط إشارات صفحة الحفظ ---
        self.reset_defaults_btn.clicked.connect(self.reset_to_defaults)
        self.save_as_default_btn.clicked.connect(self.save_current_as_default)
        self.save_all_btn.clicked.connect(self.save_all_settings)
        self.cancel_btn.clicked.connect(self.cancel_changes)

    def _on_theme_changed(self):
        """معالجة تغيير السمة"""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
        if not self.has_unsaved_changes:
            self.show_info_message(tr("theme_changed_notification"))
        self.has_unsaved_changes = True
        self.update_preview_only()

    def _on_accent_changed(self):
        """معالجة تغيير لون التمييز"""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
        if not self.has_unsaved_changes:
            self.show_info_message(tr("accent_color_changed_notification"))
        self.has_unsaved_changes = True
        self.update_preview_only()

    def _on_language_changed(self):
        """معالجة تغيير اللغة"""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
        self.has_unsaved_changes = True

    def _on_font_changed(self):
        """معالجة تغيير الخطوط"""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
        if not self.has_unsaved_changes:
            self.show_info_message(tr("font_changed_notification"))
        self.has_unsaved_changes = True
        self.update_font_preview()

    def _on_advanced_changed(self):
        """معالجة تغيير الإعدادات المتقدمة"""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
        self.has_unsaved_changes = True
        self.update_preview_only()

        # ربط تغيير السمة بتحديث الأنماط الخاصة
        global_theme_manager.theme_changed.connect(self.update_special_styles)


    def _show_save_confirmation(self):
        """عرض رسالة تأكيد الحفظ"""
        try:
            # محاولة استخدام MessageManager إذا كان متاحاً
            if hasattr(self.message_manager, 'show_question'):
                return self.message_manager.show_question(
                    self,
                    tr("warning"),
                    tr("unsaved_changes_prompt"),
                    buttons=["save", "discard", "cancel"]
                )
            else:
                # استخدام QMessageBox كبديل
                msg = QMessageBox(QMessageBox.Question, tr("warning"),
                    tr("unsaved_changes_prompt"), parent=self)

                save_btn = msg.addButton(tr("save_and_close"), QMessageBox.AcceptRole)
                discard_btn = msg.addButton(tr("discard_changes"), QMessageBox.DestructiveRole)
                cancel_btn = msg.addButton(tr("cancel"), QMessageBox.RejectRole)

                apply_theme_style(msg, "dialog")

                # تخصيص ألوان الأزرار
                save_btn.setStyleSheet(self.get_special_button_style("40, 167, 69"))  # أخضر للحفظ
                discard_btn.setStyleSheet(self.get_special_button_style("255, 193, 7"))  # أصفر للتراجع
                cancel_btn.setStyleSheet(self.get_special_button_style("220, 53, 69"))  # أحمر للإلغاء
                msg.exec()

                if msg.clickedButton() == save_btn:
                    return "save"
                elif msg.clickedButton() == discard_btn:
                    return "discard"
                else:
                    return "cancel"
        except Exception as e:
            print(f"خطأ في عرض رسالة التأكيد: {e}")
            return "cancel"

    # ===============================
    # دوال التهيئة والإعداد الأساسي
    # ===============================

    def finish_loading(self):
        """Finalize the loading process."""
        self.is_loading = False
        self.has_unsaved_changes = False
        self.update_changes_report()
        self.update_save_buttons_state()

    def get_special_button_style(self, color_rgb="13, 110, 253"):
        """Generate a special button style with a given color."""
        from .global_styles import get_font_settings
        font_settings = get_font_settings()
        return f"""
            QPushButton {{
                background: rgba({color_rgb}, 0.2);
                border: 1px solid rgba({color_rgb}, 0.4);
                border-radius: 8px;
                font-size: {font_settings['size']}px;
                font-weight: bold;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background: rgba({color_rgb}, 0.3);
                border: 1px solid rgba({color_rgb}, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba({color_rgb}, 0.1);
            }}
        """

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
        
        # أزرار التنقل الداخلية مع أيقونات SVG
        # استخدام حاوية TransparentFrame مع الحفاظ على النمط
        nav_container = TransparentFrame()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(15)

        # إضافة مسافة لمحاذاة الأزرار مع عنوان الصفحة
        nav_layout.addSpacing(30)

        # إنشاء الأزرار
        self.prev_btn = create_navigation_button("prev", 24, tr("previous_step"))
        self.prev_btn.clicked.connect(self.previous_step)
        self.prev_btn.setEnabled(False)

        self.next_btn = create_navigation_button("next", 24, tr("next_step"))
        self.next_btn.clicked.connect(self.next_step)

        # تعيين اتجاه الحاوية وترتيب الأزرار حسب اللغة
        lang_code = self.settings_data.get("language", "ar")
        nav_layout.addStretch()

        if lang_code == "en":
            # في الإنجليزية: الترتيب (التالي ثم السابق) مع الأزرار على اليمين
            nav_layout.addWidget(self.next_btn)
            nav_layout.addWidget(self.prev_btn)
            nav_container.setLayoutDirection(Qt.RightToLeft)
        else:
            # في العربية: الترتيب (السابق ثم التالي) مع الأزرار على اليسار
            nav_layout.addWidget(self.prev_btn)
            nav_layout.addWidget(self.next_btn)
            nav_container.setLayoutDirection(Qt.LeftToRight)

        content_layout.addWidget(nav_container)
        main_layout.addWidget(self.content_frame)
        
        # تعيين الصفحة الافتراضية والتحميل
        self.content_stack.setCurrentIndex(3)  # المظهر (الفهرس 3)
        self.update_navigation_buttons()

        # تحميل الإعدادات الحالية (بدلاً من الأصلية) لعرضها في الواجهة
        QTimer.singleShot(100, self.load_current_settings_to_ui)
        # تحديث الخط السفلي بعد رسم الواجهة
        QTimer.singleShot(200, lambda: self.step_indicator.set_current_step(3))
        # تحديث تقرير التغييرات بعد التحميل
        QTimer.singleShot(300, self.update_changes_report)

        # لا نحتاج تطبيق السمة هنا - السمة تُطبق تلقائياً من النظام المركزي

    # ===============================
    # دوال إنشاء الصفحات
    # ===============================

    def _create_scrollable_page(self, title_text):
        """دالة مساعدة لإنشاء صفحة قابلة للتمرير مع تخطيط أساسي"""
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(self.get_scroll_area_style())

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(25)

        title = QLabel(title_text)
        apply_theme_style(title, "title_text", auto_register=True)
        layout.addWidget(title)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return page, layout

    def create_step_pages(self):
        """إنشاء وإضافة جميع صفحات الإعدادات إلى الـ StackedWidget"""
        # تم إنشاء العناصر مسبقاً، هنا ننشئ الصفحات ونضيفها
        self.page_widgets = [
            self.create_save_page(),
            self.create_general_settings_page(),
            self.create_fonts_page(),
            self.create_appearance_page()
        ]
        for widget in self.page_widgets:
            self.content_stack.addWidget(widget)



    # ===============================
    # دوال التنسيق والأنماط (تم نقلها إلى global_styles.py)
    # ===============================

    def create_appearance_page(self):
        """إنشاء صفحة إعدادات المظهر"""
        page, layout = self._create_scrollable_page(tr("appearance_settings_title"))

        # مجموعة السمة
        theme_group = QGroupBox(tr("theme_and_colors_group"))
        apply_theme_style(theme_group, "group_box", auto_register=True)
        theme_layout = QFormLayout(theme_group)
        theme_layout.setSpacing(15)

        # السمة (استخدام العنصر الموجود)
        apply_theme_style(self.theme_combo, "combo")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_label = QLabel(tr("theme_label"))
        apply_theme_style(theme_label, "label")
        theme_layout.addRow(theme_label, self.theme_combo)

        # اللغة (استخدام العنصر الموجود)
        apply_theme_style(self.language_combo, "combo")
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        language_label = QLabel(tr("language"))
        apply_theme_style(language_label, "label")
        theme_layout.addRow(language_label, self.language_combo)

        # لون التمييز
        accent_layout = QHBoxLayout()
        self.accent_color_input = QLineEdit()
        self.accent_color_input.setPlaceholderText("#056a51")
        apply_theme_style(self.accent_color_input, "input", auto_register=True)
        self.accent_color_input.textChanged.connect(self.on_accent_color_changed)

        self.accent_color_btn = QPushButton(tr("choose_color_button"))
        self.accent_color_btn.setStyleSheet(self.get_special_button_style())
        self.accent_color_btn.clicked.connect(self.choose_accent_color)
        # ربط تغيير اللون بتسجيل التغييرات
        self.accent_color_btn.clicked.connect(lambda: self.mark_as_changed())

        accent_layout.addWidget(self.accent_color_input, 2)
        accent_layout.addWidget(self.accent_color_btn, 1)
        accent_color_label = QLabel(tr("accent_color_label"))
        apply_theme_style(accent_color_label, "label")
        theme_layout.addRow(accent_color_label, accent_layout)

        # تم إزالة إعدادات ألوان النصوص لتبسيط الواجهة
        # The text color settings have been removed to simplify the interface

        # مستوى الشفافية
        transparency_layout = QHBoxLayout()
        transparency_label = QLabel(tr("transparency_level_label"))
        apply_theme_style(transparency_label, "label", auto_register=True)
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(20, 95)
        self.transparency_slider.setValue(80)
        apply_theme_style(self.transparency_slider, "slider", auto_register=True)
        self.transparency_value = QLabel("80%")
        apply_theme_style(self.transparency_value, "label", auto_register=True)

        transparency_layout.addWidget(self.transparency_slider, 3)
        transparency_layout.addWidget(self.transparency_value, 1)
        transparency_label2 = QLabel(tr("transparency_label"))
        apply_theme_style(transparency_label2, "label")
        theme_layout.addRow(transparency_label2, transparency_layout)

        # حجم العناصر
        self.size_combo = FocusAwareComboBox()
        self.size_combo.addItems([
            tr("size_small"), tr("size_medium"),
            tr("size_large"), tr("size_xlarge")
        ])
        self.size_combo.setCurrentText(tr("size_medium"))
        apply_theme_style(self.size_combo, "combo")
        element_size_label = QLabel(tr("element_size_label"))
        apply_theme_style(element_size_label, "label")
        theme_layout.addRow(element_size_label, self.size_combo)

        # مستوى التباين
        self.contrast_combo = FocusAwareComboBox()
        self.contrast_combo.addItems([
            tr("contrast_low"), tr("contrast_normal"),
            tr("contrast_high"), tr("contrast_xhigh")
        ])
        self.contrast_combo.setCurrentText(tr("contrast_normal"))
        apply_theme_style(self.contrast_combo, "combo")
        contrast_label = QLabel(tr("contrast_label"))
        apply_theme_style(contrast_label, "label")
        theme_layout.addRow(contrast_label, self.contrast_combo)

        # ربط التغييرات بالمعاينة وتتبع التغييرات
        self.transparency_slider.valueChanged.connect(self.on_transparency_changed)
        self.transparency_slider.valueChanged.connect(self.mark_as_changed)
        self.size_combo.currentTextChanged.connect(self.on_theme_options_changed)
        self.size_combo.currentTextChanged.connect(self.mark_as_changed)
        self.contrast_combo.currentTextChanged.connect(self.on_theme_options_changed)
        self.contrast_combo.currentTextChanged.connect(self.mark_as_changed)

        layout.addWidget(theme_group)
        layout.addStretch()
        return page

    def create_fonts_page(self):
        """إنشاء صفحة إعدادات الخطوط والنصوص"""
        page, layout = self._create_scrollable_page(tr("fonts_and_text_settings_title"))

        # مجموعة إعدادات الخط الأساسي
        font_group = QGroupBox(tr("primary_font_group"))
        apply_theme_style(font_group, "group_box", auto_register=True)
        font_layout = QFormLayout(font_group)
        font_layout.setSpacing(15)

        # حجم الخط (استخدام العنصر الموجود)
        font_size_layout = QHBoxLayout()
        apply_theme_style(self.font_size_slider, "slider")

        self.font_size_label = QLabel(str(self.font_size_slider.value()))
        apply_theme_style(self.font_size_label, "label", auto_register=True)
        self.font_size_slider.valueChanged.connect(
            lambda v: self.font_size_label.setText(str(v))
        )
        self.font_size_slider.valueChanged.connect(self.mark_as_changed)

        font_size_layout.addWidget(self.font_size_slider, 3)
        font_size_layout.addWidget(self.font_size_label, 1)
        font_size_label2 = QLabel(tr("font_size_label"))
        apply_theme_style(font_size_label2, "label", auto_register=True)
        font_layout.addRow(font_size_label2, font_size_layout)

        # حجم خط العناوين
        title_font_size_layout = QHBoxLayout()
        apply_theme_style(self.title_font_size_slider, "slider")

        self.title_font_size_label = QLabel(str(self.title_font_size_slider.value()))
        apply_theme_style(self.title_font_size_label, "label", auto_register=True)
        self.title_font_size_slider.valueChanged.connect(
            lambda v: self.title_font_size_label.setText(str(v))
        )
        self.title_font_size_slider.valueChanged.connect(self.mark_as_changed)

        title_font_size_layout.addWidget(self.title_font_size_slider, 3)
        title_font_size_layout.addWidget(self.title_font_size_label, 1)
        title_font_size_label2 = QLabel(tr("title_font_size_label"))
        apply_theme_style(title_font_size_label2, "label", auto_register=True)
        font_layout.addRow(title_font_size_label2, title_font_size_layout)

        # حجم خط القوائم
        menu_font_size_layout = QHBoxLayout()
        apply_theme_style(self.menu_font_size_slider, "slider")

        self.menu_font_size_label = QLabel(str(self.menu_font_size_slider.value()))
        apply_theme_style(self.menu_font_size_label, "label", auto_register=True)
        self.menu_font_size_slider.valueChanged.connect(
            lambda v: self.menu_font_size_label.setText(str(v))
        )
        self.menu_font_size_slider.valueChanged.connect(self.mark_as_changed)

        menu_font_size_layout.addWidget(self.menu_font_size_slider, 3)
        menu_font_size_layout.addWidget(self.menu_font_size_label, 1)
        menu_font_size_label2 = QLabel(tr("menu_font_size_label"))
        apply_theme_style(menu_font_size_label2, "label", auto_register=True)
        font_layout.addRow(menu_font_size_label2, menu_font_size_layout)

        # نوع الخط (استخدام العنصر الموجود)
        apply_theme_style(self.font_family_combo, "combo")
        self.font_family_combo.currentTextChanged.connect(self.mark_as_changed)
        font_family_label = QLabel(tr("font_family_label"))
        apply_theme_style(font_family_label, "label")
        font_layout.addRow(font_family_label, self.font_family_combo)

        # وزن الخط (استخدام العنصر الموجود)
        apply_theme_style(self.font_weight_combo, "combo")
        self.font_weight_combo.currentTextChanged.connect(self.mark_as_changed)
        font_weight_label = QLabel(tr("font_weight_label"))
        apply_theme_style(font_weight_label, "label")
        font_layout.addRow(font_weight_label, self.font_weight_combo)

        layout.addWidget(font_group)

        # مجموعة إعدادات النصوص (منقولة من المظهر)
        text_group = QGroupBox(tr("text_settings_group"))
        apply_theme_style(text_group, "group_box", auto_register=True)
        text_layout = QFormLayout(text_group)
        text_layout.setSpacing(15)

        # إظهار التلميحات (استخدام العنصر الموجود)
        apply_theme_style(self.show_tooltips_check, "checkbox", auto_register=True)
        self.show_tooltips_check.stateChanged.connect(self.mark_as_changed)
        text_layout.addRow(self.show_tooltips_check)

        # تمكين الحركات (استخدام العنصر الموجود)
        apply_theme_style(self.enable_animations_check, "checkbox", auto_register=True)
        self.enable_animations_check.setChecked(True)
        self.enable_animations_check.stateChanged.connect(self.mark_as_changed)
        text_layout.addRow(self.enable_animations_check)

        # اتجاه النص (معطل حالياً)
        apply_theme_style(self.text_direction_combo, "combo")
        self.text_direction_combo.setEnabled(False)  # تعطيل الخيار
        self.text_direction_combo.setToolTip(tr("feature_disabled_tooltip"))
        self.text_direction_combo.currentTextChanged.connect(self.mark_as_changed)
        text_direction_label = QLabel(tr("text_direction_label"))
        apply_theme_style(text_direction_label, "label")
        text_layout.addRow(text_direction_label, self.text_direction_combo)

        layout.addWidget(text_group)

        # مجموعة معاينة الخط
        preview_group = QGroupBox(tr("font_preview_group"))
        apply_theme_style(preview_group, "group_box")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setSpacing(15)

        # نص المعاينة
        self.font_preview_label = QLabel(tr("font_preview_text"))
        apply_theme_style(self.font_preview_label, "label", auto_register=False) # No auto-register, handled manually
        # The style is now set in update_font_preview to be theme-aware
        self.font_preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.font_preview_label)

        layout.addWidget(preview_group)
        layout.addStretch()

        # ربط التحديثات بالمعاينة والتطبيق الفوري
        self.font_size_slider.valueChanged.connect(self.update_font_preview)
        self.title_font_size_slider.valueChanged.connect(self.update_font_preview)
        self.menu_font_size_slider.valueChanged.connect(self.update_font_preview)
        self.font_family_combo.currentTextChanged.connect(self.update_font_preview)
        self.font_weight_combo.currentTextChanged.connect(self.update_font_preview)

        # تطبيق فوري للخطوط عند التغيير
        self.font_size_slider.valueChanged.connect(self._on_font_changed)
        self.title_font_size_slider.valueChanged.connect(self._on_font_changed)
        self.menu_font_size_slider.valueChanged.connect(self._on_font_changed)
        self.font_family_combo.currentTextChanged.connect(self._on_font_changed)
        self.font_weight_combo.currentTextChanged.connect(self._on_font_changed)

        # تحديث المعاينة الأولية
        QTimer.singleShot(100, self.update_font_preview)
        return page



    def update_font_preview(self):
        """تحديث معاينة الخط (مبسط)"""
        try:
            if not hasattr(self, 'font_preview_label'):
                return

            # تطبيق السمة الحالية على المعاينة
            apply_theme_style(self.font_preview_label, "label")

            # تحديث النص
            font_size = self.font_size_slider.value()
            font_family = self.font_family_combo.currentText()
            font_weight = self.font_weight_combo.currentText()

            preview_text = tr("font_preview_dynamic_text", family=font_family, size=font_size, weight=font_weight)
            self.font_preview_label.setText(preview_text)

        except Exception as e:
            print(f"خطأ في تحديث معاينة الخط: {e}")





    def create_general_settings_page(self):
        """إنشاء صفحة الإعدادات العامة"""
        page, layout = self._create_scrollable_page(tr("general_settings_title"))

        # مجموعة إعدادات بدء التشغيل
        startup_group = QGroupBox(tr("startup_settings_group"))
        apply_theme_style(startup_group, "group_box", auto_register=True)
        startup_layout = QVBoxLayout(startup_group)
        startup_layout.setSpacing(10)

        # إضافة العناصر التي تم إنشاؤها مسبقاً
        apply_theme_style(self.disable_welcome_checkbox, "checkbox", auto_register=True)
        self.disable_welcome_checkbox.setChecked(self.settings_data.get("disable_welcome_message", False))
        startup_layout.addWidget(self.disable_welcome_checkbox)

        apply_theme_style(self.remember_state_checkbox, "checkbox", auto_register=True)
        self.remember_state_checkbox.setChecked(self.settings_data.get("remember_settings_on_exit", False))
        startup_layout.addWidget(self.remember_state_checkbox)

        apply_theme_style(self.reset_to_defaults_checkbox, "checkbox", auto_register=True)
        self.reset_to_defaults_checkbox.setChecked(self.settings_data.get("reset_to_defaults_next_time", False))
        startup_layout.addWidget(self.reset_to_defaults_checkbox)

        layout.addWidget(startup_group)

        # مجموعة إعدادات الرسائل والتحذيرات
        messages_group = QGroupBox(tr("messages_and_warnings_settings_group"))
        apply_theme_style(messages_group, "group_box", auto_register=True)
        messages_layout = QVBoxLayout(messages_group)
        messages_layout.setSpacing(10)

        apply_theme_style(self.show_exit_warning_checkbox, "checkbox", auto_register=True)
        self.show_exit_warning_checkbox.setChecked(self.settings_data.get("show_exit_warning", True))
        messages_layout.addWidget(self.show_exit_warning_checkbox)

        apply_theme_style(self.remember_exit_choice_checkbox, "checkbox", auto_register=True)
        self.remember_exit_choice_checkbox.setChecked(self.settings_data.get("remember_exit_choice", False))
        messages_layout.addWidget(self.remember_exit_choice_checkbox)

        apply_theme_style(self.dont_ask_again_checkbox, "checkbox", auto_register=True)
        self.dont_ask_again_checkbox.setChecked(self.settings_data.get("dont_ask_again_and_discard", False))
        messages_layout.addWidget(self.dont_ask_again_checkbox)

        layout.addWidget(messages_group)

        # مجموعة إعدادات الإشعارات
        notifications_group = QGroupBox(tr("notifications_settings_group"))
        apply_theme_style(notifications_group, "group_box", auto_register=True)
        notifications_layout = QVBoxLayout(notifications_group)
        notifications_layout.setSpacing(10)

        apply_theme_style(self.show_success_notifications_checkbox, "checkbox", auto_register=True)
        self.show_success_notifications_checkbox.setChecked(self.settings_data.get("notification_settings", {}).get("success", True))
        notifications_layout.addWidget(self.show_success_notifications_checkbox)

        apply_theme_style(self.show_warning_notifications_checkbox, "checkbox", auto_register=True)
        self.show_warning_notifications_checkbox.setChecked(self.settings_data.get("notification_settings", {}).get("warning", True))
        notifications_layout.addWidget(self.show_warning_notifications_checkbox)

        apply_theme_style(self.show_error_notifications_checkbox, "checkbox", auto_register=True)
        self.show_error_notifications_checkbox.setChecked(self.settings_data.get("notification_settings", {}).get("error", True))
        notifications_layout.addWidget(self.show_error_notifications_checkbox)

        apply_theme_style(self.show_info_notifications_checkbox, "checkbox", auto_register=True)
        self.show_info_notifications_checkbox.setChecked(self.settings_data.get("notification_settings", {}).get("info", True))
        notifications_layout.addWidget(self.show_info_notifications_checkbox)

        layout.addWidget(notifications_group)
        layout.addStretch()
        return page

    def create_save_page(self):
        """إنشاء صفحة الحفظ مع تقرير التغييرات"""
        page, layout = self._create_scrollable_page(tr("review_and_save_title"))

        # منطقة التقرير
        report_group = QGroupBox(tr("summary_of_changes_group"))
        apply_theme_style(report_group, "group_box", auto_register=True)
        report_layout = QVBoxLayout(report_group)
        report_layout.setSpacing(10)

        # تقرير التغييرات
        self.changes_report = QLabel(tr("analyzing_changes_text"))
        # The style is now set in update_special_styles to be theme-aware
        apply_theme_style(self.changes_report, "label", auto_register=False) # No auto-register, handled manually
        self.changes_report.setWordWrap(True)
        self.changes_report.setAlignment(Qt.AlignTop)
        report_layout.addWidget(self.changes_report)

        layout.addWidget(report_group)



        # أزرار الحفظ
        save_buttons_layout = QHBoxLayout()

        # تطبيق الأنماط على الأزرار التي تم إنشاؤها مسبقاً
        self.reset_defaults_btn.setStyleSheet(self.get_special_button_style("255, 193, 7"))  # أصفر
        self.save_as_default_btn.setStyleSheet(self.get_special_button_style("40, 167, 69"))  # أخضر
        self.save_all_btn.setStyleSheet(self.get_special_button_style("40, 167, 69"))  # أخضر
        self.cancel_btn.setStyleSheet(self.get_special_button_style("220, 53, 69"))  # أحمر

        # إضافة الأزرار إلى التخطيط
        save_buttons_layout.addWidget(self.reset_defaults_btn)
        save_buttons_layout.addWidget(self.save_as_default_btn)
        save_buttons_layout.addStretch()
        save_buttons_layout.addWidget(self.cancel_btn)
        save_buttons_layout.addWidget(self.save_all_btn)

        layout.addLayout(save_buttons_layout)
        layout.addStretch()
        return page

    def reset_to_defaults(self):
        """إرجاع جميع الإعدادات إلى الافتراضية"""
        from PySide6.QtWidgets import QMessageBox

        # تأكيد من المستخدم
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("confirm_reset_title"))
        msg.setText(tr("confirm_reset_message"))
        msg.setInformativeText(tr("confirm_reset_informative"))
        msg.setIcon(QMessageBox.Warning)

        reset_btn = msg.addButton(tr("reset_settings_button"), QMessageBox.AcceptRole)
        cancel_btn = msg.addButton(tr("cancel"), QMessageBox.RejectRole)
        msg.setDefaultButton(cancel_btn)

        # تطبيق نمط الرسالة
        apply_theme_style(msg, "dialog")

        # تخصيص ألوان الأزرار
        reset_btn.setStyleSheet(self.get_special_button_style("255, 193, 7"))  # أصفر للتراجع
        cancel_btn.setStyleSheet(self.get_special_button_style("220, 53, 69"))  # أحمر للإلغاء

        msg.exec()

        if msg.clickedButton() == reset_btn:
            try:
                # إرجاع الإعدادات إلى الافتراضية
                from modules.default_settings import reset_to_defaults
                if reset_to_defaults():
                    # إعادة تحميل الإعدادات في الواجهة
                    self.load_current_settings_to_ui()

                    # تطبيق الإعدادات الافتراضية على التطبيق
                    from .theme_manager import refresh_all_themes

                    # إعادة تطبيق السمة على جميع العناصر والنوافذ
                    refresh_all_themes()

                    # تحديث تقرير التغييرات
                    self.update_changes_report()

                    # رسالة نجاح
                    success_msg = QMessageBox(self)
                    success_msg.setWindowTitle(tr("reset_success_title"))
                    success_msg.setText(tr("reset_success_message"))
                    success_msg.setIcon(QMessageBox.Information)
                    apply_theme_style(success_msg, "dialog")
                    success_msg.exec()

                else:
                    # رسالة خطأ
                    error_msg = QMessageBox(self)
                    error_msg.setWindowTitle(tr("error_title"))
                    error_msg.setText(tr("reset_error_message"))
                    error_msg.setIcon(QMessageBox.Critical)
                    apply_theme_style(error_msg, "dialog")
                    error_msg.exec()

            except Exception as e:
                # رسالة خطأ
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle(tr("error_title"))
                error_msg.setText(f"حدث خطأ: {str(e)}")
                error_msg.setIcon(QMessageBox.Critical)
                apply_theme_style(error_msg, "dialog")
                error_msg.exec()

    def save_current_as_default(self):
        """حفظ الإعدادات الحالية كإعدادات افتراضية جديدة"""
        from PySide6.QtWidgets import QMessageBox

        # تأكيد من المستخدم
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("confirm_save_default_title"))
        msg.setText(tr("confirm_save_default_message"))
        msg.setInformativeText(tr("confirm_save_default_informative"))
        msg.setIcon(QMessageBox.Question)

        save_btn = msg.addButton(tr("save_as_default_button"), QMessageBox.AcceptRole)
        cancel_btn = msg.addButton(tr("cancel"), QMessageBox.RejectRole)
        msg.setDefaultButton(save_btn)

        # تطبيق نمط الرسالة
        apply_theme_style(msg, "dialog")

        # تخصيص ألوان الأزرار
        save_btn.setStyleSheet(self.get_special_button_style("40, 167, 69"))  # أخضر للحفظ
        cancel_btn.setStyleSheet(self.get_special_button_style("220, 53, 69"))  # أحمر للإلغاء

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
                        success_msg.setWindowTitle(tr("save_success_title"))
                        success_msg.setText(tr("save_default_success_message"))
                        success_msg.setIcon(QMessageBox.Information)
                        apply_theme_style(success_msg, "dialog")
                        success_msg.exec()
                    else:
                        # رسالة خطأ
                        error_msg = QMessageBox(self)
                        error_msg.setWindowTitle(tr("error_title"))
                        error_msg.setText(tr("save_default_error_message"))
                        error_msg.setIcon(QMessageBox.Critical)
                        apply_theme_style(error_msg, "dialog")
                        error_msg.exec()

            except Exception as e:
                # رسالة خطأ
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle(tr("error_title"))
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

        current_color = QColor(self.accent_color_input.text() or "#056a51")
        color = QColorDialog.getColor(current_color, self, tr("choose_accent_color_dialog_title"))

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

        except Exception as e:
            print(f"خطأ في حفظ الإعدادات المؤقتة: {e}")

    def go_to_step(self, step):
        """الانتقال إلى خطوة محددة مع حفظ التغييرات"""
        if 0 <= step < len(self.step_indicator.steps):
            # حفظ إعدادات الصفحة الحالية قبل الانتقال
            self.save_current_page_settings()

            self.current_step = step
            self.content_stack.setCurrentIndex(step)
            self.step_indicator.set_current_step(step)
            self.update_navigation_buttons()

            # تحديث تقرير التغييرات في صفحة الحفظ
            if step == 0:  # صفحة الحفظ (الفهرس 0)
                self.update_changes_report()

    def next_step(self):
        """الانتقال للخطوة التالية"""
        lang = settings.load_settings().get("language", "ar")
        if lang == "ar":
            # RTL: Next means decreasing index (moving left)
            if self.current_step > 0:
                self.go_to_step(self.current_step - 1)
        else:
            # LTR: Next means increasing index (moving right)
            if self.current_step < len(self.step_indicator.steps) - 1:
                self.go_to_step(self.current_step + 1)

    def previous_step(self):
        """الانتقال للخطوة السابقة"""
        lang = settings.load_settings().get("language", "ar")
        if lang == "ar":
            # RTL: Previous means increasing index (moving right)
            if self.current_step < len(self.step_indicator.steps) - 1:
                self.go_to_step(self.current_step + 1)
        else:
            # LTR: Previous means decreasing index (moving left)
            if self.current_step > 0:
                self.go_to_step(self.current_step - 1)

    def update_navigation_buttons(self):
        """تحديث حالة أزرار التنقل مع نظام السمة"""
        lang = settings.load_settings().get("language", "ar")
        num_steps = len(self.step_indicator.steps)

        # الحصول على لون السمة الحالي
        try:
            from .theme_manager import global_theme_manager
            current_theme = global_theme_manager.get_current_theme()
            theme_color = current_theme.get('accent_color', '#ff6f00')
        except:
            theme_color = '#ff6f00'

        # تحديد لون الأيقونة حسب السمة
        if global_theme_manager.current_theme == "light":
            active_color = "#333333"
        else:
            active_color = "#ffffff"
        disabled_color = "#666666"

        if lang == "ar":
            # RTL Logic
            can_go_next = self.current_step > 0
            can_go_prev = self.current_step < num_steps - 1
        else:
            # LTR Logic
            can_go_next = self.current_step < num_steps - 1
            can_go_prev = self.current_step > 0

        self.next_btn.setEnabled(can_go_next)
        self.next_btn.set_icon_color(active_color if can_go_next else disabled_color)

        self.prev_btn.setEnabled(can_go_prev)
        self.prev_btn.set_icon_color(active_color if can_go_prev else disabled_color)

    def update_save_buttons_state(self):
        """تحديث حالة أزرار الحفظ والإلغاء بناءً على وجود تغييرات"""
        try:
            # التحقق من وجود أزرار الحفظ والإلغاء
            if hasattr(self, 'save_all_btn') and hasattr(self, 'cancel_btn'):
                # تفعيل أو تعطيل الأزرار بناءً على وجود تغييرات
                has_changes = getattr(self, 'has_unsaved_changes', False)
                self.save_all_btn.setEnabled(has_changes)
                self.cancel_btn.setEnabled(has_changes)
        except Exception as e:
            print(f"خطأ في تحديث حالة أزرار الحفظ: {e}")

    def update_changes_report(self):
        """تحديث تقرير التغييرات مع معالجة أخطاء محسنة"""
        try:
            current_settings = self.get_current_settings()
            changes = []

            # مقارنة الإعدادات مع معالجة آمنة
            original_theme = self.original_settings.get("theme", "dark")
            current_theme = self.theme_combo.currentText()
            if original_theme != current_theme:
                changes.append(f"السمة: {original_theme} ← {current_theme}")

            original_color = self.original_settings.get("accent_color", "#ff6f00")
            current_color = self.accent_color_input.text() or "#ff6f00"
            if original_color != current_color:
                changes.append(f"لون التمييز: {original_color} ← {current_color}")

            # مقارنة إعدادات الخطوط الجديدة
            original_font_size = self.original_settings.get("ui_settings", {}).get("font_size", 14)
            current_font_size = self.font_size_slider.value()
            if original_font_size != current_font_size:
                changes.append(tr("change_report_font_size", original=original_font_size, current=current_font_size))

            original_font_family = self.original_settings.get("ui_settings", {}).get("font_family", tr("system_default_font"))
            current_font_family = self.font_family_combo.currentText()
            if original_font_family != current_font_family:
                changes.append(tr("change_report_font_family", original=original_font_family, current=current_font_family))

            original_font_weight = self.original_settings.get("ui_settings", {}).get("font_weight", tr("font_weight_normal"))
            current_font_weight = self.font_weight_combo.currentText()
            if original_font_weight != current_font_weight:
                changes.append(tr("change_report_font_weight", original=original_font_weight, current=current_font_weight))

            original_tooltips = self.original_settings.get("ui_settings", {}).get("show_tooltips", True)
            current_tooltips = self.show_tooltips_check.isChecked()
            if original_tooltips != current_tooltips:
                status = tr("status_enabled") if current_tooltips else tr("status_disabled")
                changes.append(tr("change_report_tooltips", status=status))

            original_animations = self.original_settings.get("ui_settings", {}).get("enable_animations", True)
            current_animations = self.enable_animations_check.isChecked()
            if original_animations != current_animations:
                status = tr("status_enabled") if current_animations else tr("status_disabled")
                changes.append(tr("change_report_animations", status=status))

            original_direction = self.original_settings.get("ui_settings", {}).get("text_direction", tr("text_direction_auto"))
            current_direction = self.text_direction_combo.currentText()
            if original_direction != current_direction:
                changes.append(tr("change_report_text_direction", original=original_direction, current=current_direction))

            # مقارنة إعدادات السمة المتقدمة
            original_transparency = self.original_settings.get("ui_settings", {}).get("transparency", 80)
            current_transparency = self.transparency_slider.value()
            if original_transparency != current_transparency:
                changes.append(tr("change_report_transparency", original=original_transparency, current=current_transparency))

            original_size = self.original_settings.get("ui_settings", {}).get("size", tr("size_medium"))
            current_size = self.size_combo.currentText()
            if original_size != current_size:
                changes.append(tr("change_report_element_size", original=original_size, current=current_size))

            original_contrast = self.original_settings.get("ui_settings", {}).get("contrast", tr("contrast_normal"))
            current_contrast = self.contrast_combo.currentText()
            if original_contrast != current_contrast:
                changes.append(tr("change_report_contrast", original=original_contrast, current=current_contrast))

            # إنشاء التقرير
            if changes:
                report = tr("changes_applied_report_header") + "\n".join(changes)
                report += tr("total_changes_report_footer", count=len(changes))
            else:
                report = tr("no_changes_report")

            self.changes_report.setText(report)
            
            # تحديث حالة أزرار الحفظ والإلغاء
            self.update_save_buttons_state()

        except Exception as e:
            error_msg = tr("error_analyzing_changes", e=str(e))
            print(error_msg)
            self.changes_report.setText(error_msg)

    def get_current_settings(self):
        """الحصول على الإعدادات الحالية من الواجهة (محسن بدون hasattr مفرط)"""
        current = {}

        try:
            # إعدادات المظهر الأساسية (مضمونة الوجود)
            current["theme"] = self.theme_combo.currentText()
            current["accent_color"] = self.accent_color_input.text() or "#ff6f00"
            current["language"] = "ar" if self.language_combo.currentText() == "العربية" else "en"

            # إعدادات الواجهة (مضمونة الوجود)
            ui_settings = {
                # إعدادات الخطوط
                "font_size": self.font_size_slider.value(),
                "title_font_size": self.title_font_size_slider.value(),
                "menu_font_size": self.menu_font_size_slider.value(),
                "font_family": self.font_family_combo.currentText(),
                "font_weight": self.font_weight_combo.currentText(),
                "text_direction": self.text_direction_combo.currentText(),

                # إعدادات النصوص
                "show_tooltips": self.show_tooltips_check.isChecked(),
                "enable_animations": self.enable_animations_check.isChecked(),

                # إعدادات السمة المتقدمة
                "transparency": self.transparency_slider.value(),
                "size": self.size_combo.currentText(),
                "contrast": self.contrast_combo.currentText()
            }
            current["ui_settings"] = ui_settings

            # إعدادات رسائل الترحيب
            current["disable_welcome_message"] = self.disable_welcome_checkbox.isChecked()

            # إعدادات تذكر الحالة
            current["remember_settings_on_exit"] = self.remember_state_checkbox.isChecked()

            # إعدادات العودة للإعدادات الافتراضية
            current["reset_to_defaults_next_time"] = self.reset_to_defaults_checkbox.isChecked()

            # إعدادات إظهار رسالة التحذير عند الخروج
            current["show_exit_warning"] = self.show_exit_warning_checkbox.isChecked()

            # إعدادات تذكر اختيار المستخدم في رسالة التحذير
            current["remember_exit_choice"] = self.remember_exit_choice_checkbox.isChecked()

            # إعدادات عدم السؤال مرة أخرى وتجاهل التغييرات
            current["dont_ask_again_and_discard"] = self.dont_ask_again_checkbox.isChecked()

            # إعدادات الإشعارات
            current["notification_settings"] = {
                "success": self.show_success_notifications_checkbox.isChecked(),
                "warning": self.show_warning_notifications_checkbox.isChecked(),
                "error": self.show_error_notifications_checkbox.isChecked(),
                "info": self.show_info_notifications_checkbox.isChecked()
            }

        except Exception as e:
            print(f"خطأ في قراءة الإعدادات: {e}")
            # عرض إشعار خطأ
            show_error(f"{tr('error_reading_settings')}: {str(e)}", duration=5000)

        return current

    def on_reset_defaults_changed(self, state):
        """معالجة تغيير حالة خيار العودة للإعدادات الافتراضية"""
        # إذا تم تفعيل خيار العودة للإعدادات الافتراضية
        if state == Qt.Checked:
            # تعطيل الخيارات الأخرى مؤقتاً
            if hasattr(self, 'remember_state_checkbox'):
                self.remember_state_checkbox.setEnabled(False)
            if hasattr(self, 'disable_welcome_checkbox'):
                self.disable_welcome_checkbox.setEnabled(False)
            # إظهار رسالة توضيحية
            self.show_info_message(tr("reset_defaults_info_message"))
        else:
            # تفعيل الخيارات الأخرى
            if hasattr(self, 'remember_state_checkbox'):
                self.remember_state_checkbox.setEnabled(True)
            if hasattr(self, 'disable_welcome_checkbox'):
                self.disable_welcome_checkbox.setEnabled(True)

    def closeEvent(self, event):
        """معالجة حدث إغلاق النافذة"""
        # التحقق من وجود تغييرات غير محفوظة
        if hasattr(self, 'has_unsaved_changes') and self.has_unsaved_changes:
            # التحقق من إعدادات إظهار رسالة التحذير
            show_warning = True
            if hasattr(self, 'show_exit_warning_checkbox'):
                show_warning = self.show_exit_warning_checkbox.isChecked()

            if show_warning:
                # إنشاء رسالة تحذير مخصصة باستخدام الثيم الحالي
                dialog = QDialog(self)
                dialog.setWindowTitle(tr("unsaved_changes_warning"))
                dialog.setMinimumWidth(400)

                # تطبيق الثيم على مربع الحوار
                apply_theme_style(dialog, "dialog")

                # إنشاء تخطيط مربع الحوار
                layout = QVBoxLayout(dialog)
                layout.setSpacing(15)
                layout.setContentsMargins(20, 20, 20, 20)

                # إضافة رسالة التحذير
                message_label = QLabel(tr("unsaved_changes_prompt"))
                message_label.setWordWrap(True)
                apply_theme_style(message_label, "label")
                layout.addWidget(message_label)

                # إضافة خيار تذكر الاختيار (إذا كان الخيار مفعلاً)
                remember_checkbox = None
                if hasattr(self, 'remember_exit_choice_checkbox') and self.remember_exit_choice_checkbox.isChecked():
                    remember_checkbox = QCheckBox(tr("remember_my_choice"))
                    apply_theme_style(remember_checkbox, "checkbox")
                    layout.addWidget(remember_checkbox)

                # إضافة أزرار الخيارات
                buttons_layout = QHBoxLayout()

                save_button = QPushButton(tr("save_and_close"))
                apply_theme_style(save_button, "button")
                save_button.clicked.connect(lambda: self.save_and_close(dialog, remember_checkbox))
                buttons_layout.addWidget(save_button)

                discard_button = QPushButton(tr("discard_changes"))
                apply_theme_style(discard_button, "button")
                discard_button.clicked.connect(lambda: self.discard_and_close(dialog, remember_checkbox))
                buttons_layout.addWidget(discard_button)

                cancel_button = QPushButton(tr("cancel_button"))
                apply_theme_style(cancel_button, "button")
                cancel_button.clicked.connect(dialog.reject)
                buttons_layout.addWidget(cancel_button)

                layout.addLayout(buttons_layout)

                # عرض مربع الحوار ومنع إغلاق النافذة الأصلية
                dialog.exec_()

                # منع إغلاق النافذة إذا تم إلغاء العملية
                event.ignore()
                return

        # إذا لم تكن هناك تغييرات أو تم تعطيل رسالة التحذير، أغلق النافذة بشكل طبيعي
        super().closeEvent(event)

    def save_and_close(self, dialog, remember_checkbox):
        """حفظ التغييرات وإغلاق النافذة"""
        # تذكر اختيار المستخدم إذا كان الخيار مفعلاً
        if remember_checkbox and remember_checkbox.isChecked():
            # حفظ اختيار المستخدم (حفظ التغييرات دائمًا)
            settings_data = settings.load_settings()
            settings_data["always_save_on_exit"] = True
            settings_data["show_exit_warning"] = False  # تعطيل الرسالة في المستقبل
            settings.save_settings(settings_data)

        # حفظ الإعدادات الحالية
        self.save_all_settings()

        # إغلاق مربع الحوار والنافذة
        dialog.accept()
        self.accept()

    def discard_and_close(self, dialog, remember_checkbox):
        """تجاهل التغييرات وإغلاق النافذة"""
        # تذكر اختيار المستخدم إذا كان الخيار مفعلاً
        if remember_checkbox and remember_checkbox.isChecked():
            # حفظ اختيار المستخدم (تجاهل التغييرات دائمًا)
            settings_data = settings.load_settings()
            settings_data["always_discard_on_exit"] = True
            settings_data["show_exit_warning"] = False  # تعطيل الرسالة في المستقبل
            settings.save_settings(settings_data)

        # إغلاق مربع الحوار والنافذة
        dialog.accept()
        self.reject()

    # ===============================
    # دوال مساعدة لتقليل التكرار
    # ===============================

    def get_current_theme_settings(self):
        """الحصول على إعدادات السمة الحالية - دالة مساعدة"""
        if hasattr(self, 'theme_combo') and hasattr(self, 'accent_color_input'):
            return {
                'theme': self.theme_combo.currentText(),
                'accent_color': self.accent_color_input.text() or "#056a51"
            }
        return {'theme': 'blue', 'accent_color': '#056a51'}

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
                accent_color = "#056a51"  # لون افتراضي آمن

            from .theme_manager import global_theme_manager
            global_theme_manager.change_theme(theme_name, accent_color)
            return True
        except Exception as e:
            print(tr("error_applying_theme", e=e))
            return False

    def show_error_message(self, message, details=None):
        """عرض رسالة خطأ باستخدام نظام الإشعارات المحسن"""
        full_message = message
        if details:
            full_message += f" - {details}"
        show_error(full_message, duration=5000)

    def show_success_message(self, message, details=None):
        """عرض رسالة نجاح باستخدام نظام الإشعارات المحسن"""
        full_message = message
        if details:
            full_message += f" - {details}"
        show_success(full_message, duration=4000)

    def show_warning_message(self, message, details=None):
        """عرض رسالة تحذير باستخدام نظام الإشعارات المحسن"""
        full_message = message
        if details:
            full_message += f" - {details}"
        show_warning(full_message, duration=4000)

    def show_info_message(self, message, details=None):
        """عرض رسالة معلومات باستخدام نظام الإشعارات المحسن"""
        full_message = message
        if details:
            full_message += f" - {details}"
        show_info(full_message, duration=3000)

    def _load_settings_to_ui(self):
        """تحميل الإعدادات إلى الواجهة (محسن بدون hasattr مفرط)"""
        try:
            # منع إرسال الإشارات أثناء التحميل
            self._block_signals(True)

            # تحميل إعدادات المظهر الأساسية
            self.theme_combo.setCurrentText(self.settings_data.get("theme", "blue"))
            self.accent_color_input.setText(self.settings_data.get("accent_color", "#056a51"))

            # تحميل اللغة
            current_lang = self.settings_data.get("language", "ar")
            self.language_combo.setCurrentText("العربية" if current_lang == "ar" else "English")

            # تحميل إعدادات الواجهة
            ui_settings = self.settings_data.get("ui_settings", {})

            # إعدادات الخطوط
            self.font_size_slider.setValue(ui_settings.get("font_size", 12))
            self.title_font_size_slider.setValue(ui_settings.get("title_font_size", 18))
            self.menu_font_size_slider.setValue(ui_settings.get("menu_font_size", 12))

            font_family = ui_settings.get("font_family", tr("system_default_font"))
            index = self.font_family_combo.findText(font_family)
            if index >= 0:
                self.font_family_combo.setCurrentIndex(index)

            font_weight = ui_settings.get("font_weight", tr("font_weight_normal"))
            index = self.font_weight_combo.findText(font_weight)
            if index >= 0:
                self.font_weight_combo.setCurrentIndex(index)

            text_direction = ui_settings.get("text_direction", tr("text_direction_auto"))
            index = self.text_direction_combo.findText(text_direction)
            if index >= 0:
                self.text_direction_combo.setCurrentIndex(index)

            # إعدادات النصوص
            self.show_tooltips_check.setChecked(ui_settings.get("show_tooltips", True))
            self.enable_animations_check.setChecked(ui_settings.get("enable_animations", True))

            # إعدادات السمة المتقدمة
            self.transparency_slider.setValue(ui_settings.get("transparency", 80))

            size = ui_settings.get("size", tr("size_medium"))
            index = self.size_combo.findText(size)
            if index >= 0:
                self.size_combo.setCurrentIndex(index)

            contrast = ui_settings.get("contrast", tr("contrast_normal"))
            index = self.contrast_combo.findText(contrast)
            if index >= 0:
                self.contrast_combo.setCurrentIndex(index)

            # تحديث معاينة الخط
            self.update_font_preview()

            # إعادة تفعيل الإشارات
            self._block_signals(False)

        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
            show_error(f"{tr('error_loading_settings')}: {str(e)}", duration=5000)

    def _block_signals(self, block):
        """منع أو تفعيل إشارات العناصر"""
        widgets = [
            self.theme_combo, self.accent_color_input, self.language_combo,
            self.font_size_slider, self.title_font_size_slider, self.menu_font_size_slider,
            self.font_family_combo, self.font_weight_combo,
            self.text_direction_combo, self.show_tooltips_check, self.enable_animations_check,
            self.transparency_slider, self.size_combo, self.contrast_combo
        ]

        for widget in widgets:
            widget.blockSignals(block)

    # ===============================
    # دوال الحفظ والتحميل والإدارة
    # ===============================

    def save_all_settings(self):
        """
        حفظ جميع الإعدادات عن طريق تفويض المهمة إلى مدير الإعدادات.
        """
        try:
            # إشعار بدء عملية الحفظ
            self.show_info_message(tr("saving_settings_notification"))

            # 1. الحصول على الإعدادات الحالية من الواجهة
            current_settings = self.get_current_settings()

            # 2. دمج الإعدادات الجديدة مع البيانات الحالية
            self.settings_data.update(current_settings)

            # 3. تفويض الحفظ والنسخ الاحتياطي والتحقق إلى مدير الإعدادات
            if settings.save_settings(self.settings_data, self.original_settings):
                
                # 4. تحديث السمة في مدير السمات مع الخيارات
                theme_name = self.theme_combo.currentText()
                accent_color = self.accent_color_input.text() or "#056a51"

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

                # تطبيق إعدادات الخطوط والسمة على جميع العناصر
                from .theme_manager import refresh_all_themes
                refresh_all_themes()

                # 5. تحديث الحالة الداخلية للنافذة
                self.original_settings = self.settings_data.copy()
                self.has_unsaved_changes = False
                self.update_changes_report()
                
                # 6. تطبيق إعدادات الإشعارات مباشرة
                if "notification_settings" in self.settings_data:
                    from .notification_system import global_notification_manager
                    global_notification_manager.update_notification_settings(self.settings_data["notification_settings"])

                # 7. إعلام باقي التطبيق بالتغييرات
                self.settings_changed.emit()

                # 8. عرض رسالة نجاح مفصلة
                success_message = tr("all_settings_saved_successfully")
                self.show_success_message(success_message)

                # إشعار إضافي للتأكيد
                # استخدام النافذة الرئيسية بدلاً من نافذة الإعدادات لعرض الإشعار
                main_window = self._get_main_window()
                if main_window:
                    QTimer.singleShot(1000, lambda: main_window.notification_manager.show_notification(tr("settings_applied_notification"), "info", 2000))
                else:
                    QTimer.singleShot(1000, lambda: show_info(tr("settings_applied_notification"), duration=2000))
                return True
            else:
                # مدير الإعدادات فشل في الحفظ
                self.show_error_message(tr("error_title"), tr("settings_save_failed"), tr("check_logs_details"))
                return False

        except Exception as e:
            error_message = tr("unexpected_save_error", e=str(e))
            self.show_error_message(tr("critical_error_title"), error_message)
            return False

    def cancel_changes(self):
        """إلغاء جميع التغييرات"""
        if not self.has_unsaved_changes:
            self.show_info_message(tr("no_changes_to_cancel"))
            return

        # إلغاء التغييرات مباشرة مع إشعار
        self.load_original_settings()
        self.update_changes_report()
        self.has_unsaved_changes = False  # إعادة تعيين حالة التغييرات
        self.update_preview_only()  # تحديث المعاينة للإعدادات الأصلية
        self.update_save_buttons_state()  # تحديث حالة أزرار الحفظ والإلغاء

        self.show_success_message(tr("all_changes_canceled_message"))

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
                    self.font_size_slider.setValue(ui_settings.get("font_size", 14))
                if hasattr(self, 'font_family_combo'):
                    font_family = ui_settings.get("font_family", tr("system_default_font"))
                    index = self.font_family_combo.findText(font_family)
                    if index >= 0:
                        self.font_family_combo.setCurrentIndex(index)
                if hasattr(self, 'font_weight_combo'):
                    font_weight = ui_settings.get("font_weight", tr("font_weight_normal"))
                    index = self.font_weight_combo.findText(font_weight)
                    if index >= 0:
                        self.font_weight_combo.setCurrentIndex(index)
                if hasattr(self, 'text_direction_combo'):
                    text_direction = ui_settings.get("text_direction", tr("text_direction_auto"))
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
                    size = ui_settings.get("size", tr("size_medium"))
                    index = self.size_combo.findText(size)
                    if index >= 0:
                        self.size_combo.setCurrentIndex(index)
                if hasattr(self, 'contrast_combo'):
                    contrast = ui_settings.get("contrast", tr("contrast_normal"))
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
            print(tr("error_loading_original_settings", e=e))

    def on_language_changed(self, language_text):
        """Handle language change from the settings UI."""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
        lang_code = "ar" if language_text == "العربية" else "en"
        
        # Update internal state, do not save immediately
        self.settings_data["language"] = lang_code
        
        # Apply layout direction immediately
        app = QApplication.instance()
        if lang_code == "ar":
            app.setLayoutDirection(Qt.RightToLeft)
        else:
            app.setLayoutDirection(Qt.LeftToRight)

        # Force the settings window to re-polish its style and update layout
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
        # Mark changes and show restart message
        self.mark_as_changed()

        # إشعار جميع المكونات بتغيير اللغة لإعادة ترتيب الأزرار
        reload_translations()

        self.show_info_message(tr("language_changed_message"))

    def load_current_settings_to_ui(self):
        """تحميل الإعدادات المؤقتة إلى الواجهة"""
        try:
            if hasattr(self, 'theme_combo'):
                # منع إرسال الإشارات أثناء التحميل
                self.theme_combo.blockSignals(True)
                self.accent_color_input.blockSignals(True)
                self.language_combo.blockSignals(True)

                # تحميل من البيانات المؤقتة (settings_data) التي تحتوي على التغييرات
                self.theme_combo.setCurrentText(self.settings_data.get("theme", "dark"))
                self.accent_color_input.setText(self.settings_data.get("accent_color", "#ff6f00"))
                
                # تحميل اللغة
                current_lang = self.settings_data.get("language", "ar")
                self.language_combo.setCurrentText("العربية" if current_lang == "ar" else "English")

                # إعادة تفعيل الإشارات
                self.theme_combo.blockSignals(False)
                self.accent_color_input.blockSignals(False)
                self.language_combo.blockSignals(False)

                print(f"تم تحميل الإعدادات المؤقتة: السمة={self.settings_data.get('theme')}, اللون={self.settings_data.get('accent_color')}")

                ui_settings = self.settings_data.get("ui_settings", {})

                # تحميل إعدادات الخطوط
                if hasattr(self, 'font_size_slider'):
                    self.font_size_slider.blockSignals(True)
                    self.font_size_slider.setValue(ui_settings.get("font_size", 14))
                    self.font_size_slider.blockSignals(False)
                if hasattr(self, 'font_family_combo'):
                    self.font_family_combo.blockSignals(True)
                    font_family = ui_settings.get("font_family", tr("system_default_font"))
                    index = self.font_family_combo.findText(font_family)
                    if index >= 0:
                        self.font_family_combo.setCurrentIndex(index)
                    self.font_family_combo.blockSignals(False)
                if hasattr(self, 'font_weight_combo'):
                    self.font_weight_combo.blockSignals(True)
                    font_weight = ui_settings.get("font_weight", tr("font_weight_normal"))
                    index = self.font_weight_combo.findText(font_weight)
                    if index >= 0:
                        self.font_weight_combo.setCurrentIndex(index)
                    self.font_weight_combo.blockSignals(False)
                if hasattr(self, 'text_direction_combo'):
                    self.text_direction_combo.blockSignals(True)
                    text_direction = ui_settings.get("text_direction", tr("text_direction_auto"))
                    index = self.text_direction_combo.findText(text_direction)
                    if index >= 0:
                        self.text_direction_combo.setCurrentIndex(index)
                    self.text_direction_combo.blockSignals(False)

                # تحميل إعدادات النصوص
                if hasattr(self, 'show_tooltips_check'):
                    self.show_tooltips_check.setChecked(ui_settings.get("show_tooltips", True))
                if hasattr(self, 'enable_animations_check'):
                    self.enable_animations_check.setChecked(ui_settings.get("enable_animations", True))

                # تحميل إعدادات السمة المتقدمة
                if hasattr(self, 'transparency_slider'):
                    self.transparency_slider.setValue(ui_settings.get("transparency", 80))
                if hasattr(self, 'size_combo'):
                    size = ui_settings.get("size", tr("size_medium"))
                    index = self.size_combo.findText(size)
                    if index >= 0:
                        self.size_combo.setCurrentIndex(index)
                if hasattr(self, 'contrast_combo'):
                    contrast = ui_settings.get("contrast", tr("contrast_normal"))
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

        except Exception as e:
            print(tr("error_loading_current_settings", e=e))

    def on_theme_changed(self, theme_name):
        """تحديث المعاينة فقط عند تغيير السمة - بدون تطبيق على البرنامج"""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
        try:
            # تحديث المعاينة فقط
            self.update_preview_only()

            # حفظ في الذاكرة المؤقتة فقط
            self.settings_data["theme"] = theme_name
            self.has_unsaved_changes = True

            # تحديث تقرير التغييرات
            QTimer.singleShot(100, self.update_changes_report)

        except Exception as e:
            print(tr("error_updating_preview", e=e))

    def on_accent_color_changed(self, color_text):
        """تحديث المعاينة فقط عند تغيير لون التمييز"""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
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

        except Exception as e:
            print(tr("error_updating_preview", e=e))

    def mark_as_changed(self):
        """تسجيل أن هناك تغييرات غير محفوظة وتحديث التقرير"""
        if hasattr(self, 'is_loading') and self.is_loading:
            return
        if not self.has_unsaved_changes:
            # إشعار أول تغيير فقط
            self.show_info_message(tr("settings_modified_notification"))

        self.has_unsaved_changes = True
        # تحديث تقرير التغييرات فوراً
        QTimer.singleShot(100, self.update_changes_report)
        # تحديث حالة أزرار الحفظ والإلغاء
        QTimer.singleShot(150, self.update_save_buttons_state)

    # تم إزالة الدوال المتعلقة بألوان النصوص المخصصة
    # Functions related to custom text colors have been removed.

    def update_special_styles(self):
        """Update styles for widgets that need custom, theme-aware styling."""
        try:
            from .theme_manager import global_theme_manager
            from .global_styles import get_font_settings
            from PySide6.QtGui import QColor
            font_settings = get_font_settings()
            colors = global_theme_manager.get_current_colors()
            text_color_q = QColor(colors.get('text', '#ffffff'))

            # Style for changes_report
            if hasattr(self, 'changes_report') and self.changes_report:
                self.changes_report.setStyleSheet(f"""
                    QLabel {{
                        font-size: {int(font_settings['size'] * 0.9)}px;
                        line-height: 1.6;
                        padding: 15px;
                        background: rgba({text_color_q.red()}, {text_color_q.green()}, {text_color_q.blue()}, 0.05);
                        border: 1px solid rgba({text_color_q.red()}, {text_color_q.green()}, {text_color_q.blue()}, 0.1);
                        border-radius: 6px;
                        color: {colors.get('text_body', '#ffffff')};
                    }}
                """)
            
            # Style for font_preview_label (by calling its update function)
            if hasattr(self, 'font_preview_label'):
                self.update_font_preview()

        except Exception as e:
            print(f"Error updating special styles: {e}")

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

            # تحديث الأنماط الخاصة
            self.update_special_styles()

            theme_name = global_theme_manager.current_theme
            accent_color = global_theme_manager.current_accent

        except Exception as e:
            print(tr("error_applying_window_theme", e=e))



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
            print(tr("error_updating_preview", e=e))
            # في حالة الخطأ، عرض إشعار
            show_error(f"{tr('error_updating_preview')}: {str(e)}", duration=4000)

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
        
        # إشعار بأن ميزة الشفافية ستكون متوفرة قريباً
        self.show_info_message(tr("transparency_feature_coming_soon"))

        # إشعار عند تغيير الشفافية بشكل كبير
        if value <= 30:
            self.show_info_message(tr("low_transparency_warning"))
        elif value >= 90:
            self.show_info_message(tr("high_transparency_info"))

    def on_theme_options_changed(self):
        """تغيير خيارات السمة - النظام الجديد"""
        try:
            theme_name = self.theme_combo.currentText()
            accent_color = self.accent_color_input.text() or "#056a51"

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
            print(tr("error_applying_theme_options", e=e))

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
            print(tr("error_previewing_theme", e=e))

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
