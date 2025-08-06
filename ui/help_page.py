
"""
واجهة المساعدة
Help UI for ApexFlow
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton,
    QTabWidget, QStackedWidget, QScrollArea, QFrame, QGridLayout, QGroupBox, QCheckBox,
    QSpinBox, QComboBox, QFormLayout, QTreeWidget, QTreeWidgetItem, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt

from .theme_manager import apply_theme_style
from modules.translator import tr
from PySide6.QtCore import Signal, QTimer

class HelpStepIndicator(QWidget):
    """مؤشر التبويبات في الأعلى"""

    step_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0  # البدء من تبويب المساعدة
        self.steps = [tr("help_tab"), tr("notification_center_tab"), tr("notification_settings_tab"), tr("diagnostics_tab")]
        self.setup_ui()

    def _style_step_button(self, btn, is_current_step=False):
        """Applies the standard style to a step button."""
        from .theme_manager import apply_theme_style, global_theme_manager
        from .global_styles import get_font_settings
        font_settings = get_font_settings()
        apply_theme_style(btn, "button")

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
        """إعداد واجهة مؤشر التبويبات"""
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
        apply_theme_style(self.slider_indicator, "slider_indicator")
        self.update_slider_position()

    def set_current_step(self, step):
        """تعيين التبويب الحالي"""
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


class HelpPage(QWidget):
    """صفحة المساعدة"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """إعداد واجهة المستخدم لصفحة المساعدة"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # تخطيط أفقي للعنوان ومؤشر التبويبات مع مراعاة اتجاه اللغة
        header_content_layout = QHBoxLayout()
        header_content_layout.setSpacing(20)

        # عنوان الصفحة - بنفس تنسيق صفحة التحويل
        from .ui_helpers import create_title
        title_label = create_title(tr("help_title"))

        # إنشاء مؤشر التبويبات
        self.step_indicator = HelpStepIndicator()
        self.step_indicator.step_clicked.connect(self.on_step_clicked)

        # ترتيب العنوان والتبويبات حسب اتجاه اللغة
        from modules.translator import get_current_language
        current_lang = get_current_language()

        if current_lang == "ar":  # العربية: العنوان يمين، التبويبات يسار
            header_content_layout.addWidget(self.step_indicator)
            header_content_layout.addStretch()
            header_content_layout.addWidget(title_label)
        else:  # الإنجليزية: العنوان يسار، التبويبات يمين
            header_content_layout.addWidget(title_label)
            header_content_layout.addStretch()
            header_content_layout.addWidget(self.step_indicator)

        main_layout.addLayout(header_content_layout)

        # إنشاء حاوية التبويبات
        self.tabs_container = QStackedWidget()
        apply_theme_style(self.tabs_container, "widget")

        # إزالة الحدود اليمنى واليسرى والسفلية فقط
        self.tabs_container.setStyleSheet("QStackedWidget { border-left: none; border-right: none; border-bottom: none; }")

        # تبويب المساعدة
        self.help_tab = QWidget()
        self.tabs_container.addWidget(self.help_tab)
        # سيتم إعداده عند أول طلب للعرض

        # تبويب مركز الإشعارات
        self.notification_center_tab = QWidget()
        self.tabs_container.addWidget(self.notification_center_tab)
        # سيتم إعداده عند أول طلب للعرض

        # تبويب إعدادات الإشعارات
        self.notification_settings_tab = QWidget()
        self.tabs_container.addWidget(self.notification_settings_tab)
        # سيتم إعداده عند أول طلب للعرض

        # تبويب التشخيص
        self.diagnostics_tab = QWidget()
        self.tabs_container.addWidget(self.diagnostics_tab)
        # سيتم إعداده عند أول طلب للعرض

        # متغيرات لتتبع حالة التحميل
        self.help_tab_loaded = False
        self.notification_center_tab_loaded = False
        self.notification_settings_tab_loaded = False
        self.diagnostics_tab_loaded = False

        main_layout.addWidget(self.tabs_container)

        # تطبيق السمة
        apply_theme_style(self, "dialog")
        
        # تعيين التبويب الافتراضي وتحميله فوراً
        self.step_indicator.set_current_step(0)
        self.tabs_container.setCurrentIndex(0)
        # تحميل تبويب المساعدة فوراً كونه التبويب الافتراضي
        self.setup_help_tab()
        self.help_tab_loaded = True

    def on_step_clicked(self, step_index):
        """التعامل مع النقر على زر التبويب - مع تحميل التبويب عند الحاجة"""
        self.step_indicator.set_current_step(step_index)
        self.tabs_container.setCurrentIndex(step_index)

        # تحميل التبويب عند أول طلب فقط
        if step_index == 0 and not self.help_tab_loaded:
            self.setup_help_tab()
            self.help_tab_loaded = True
        elif step_index == 1 and not self.notification_center_tab_loaded:
            self.setup_notification_center_tab()
            self.notification_center_tab_loaded = True
        elif step_index == 2 and not self.notification_settings_tab_loaded:
            self.setup_notification_settings_tab()
            self.notification_settings_tab_loaded = True
        elif step_index == 3 and not self.diagnostics_tab_loaded:
            self.setup_diagnostics_tab()
            self.diagnostics_tab_loaded = True

    def setup_help_tab(self):
        """إعداد تبويب المساعدة"""
        # إنشاء حاوية قابلة للتمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        apply_theme_style(scroll_area, "graphics_view")
        
        # إنشاء ويدجت المحتوى
        content_widget = QWidget()
        apply_theme_style(content_widget, "widget")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # إضافة المحتوى إلى منطقة التمرير
        scroll_area.setWidget(content_widget)
        
        # إضافة منطقة التمرير إلى التبويب
        tab_layout = QVBoxLayout(self.help_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        # محتوى المساعدة - تحميل متأخر لتحسين الأداء
        help_content = QTextBrowser()
        layout.addWidget(help_content)

        # تطبيق السمة وتحميل المحتوى بشكل متأخر لتسريع العرض الأولي
        QTimer.singleShot(150, lambda: [
            apply_theme_style(help_content, "text_browser"),
            self.typewriter_effect(help_content, tr("help_content"))
        ])

    def typewriter_effect(self, text_browser, html_content, speed=20):
        """تأثير الكتابة الآلية للنص مع الحفاظ على التنسيق"""
        # إخفاء النص أولاً
        text_browser.setHtml("")
        text_browser.setVisible(True)

        # تطبيق تأثير الكتابة مع الحفاظ على التنسيق
        self.typewriter_index = 0
        self.typewriter_html = html_content
        self.typewriter_browser = text_browser
        self.typewriter_speed = speed

        # بدء المؤقت لتأثير الكتابة
        self.typewriter_timer = QTimer()
        self.typewriter_timer.timeout.connect(self.typewriter_next_char)
        self.typewriter_timer.start(speed)

    def typewriter_next_char(self):
        """عرض الحرف التالي في تأثير الكتابة مع الحفاظ على التنسيق"""
        if self.typewriter_index < len(self.typewriter_html):
            # عرض النص حتى الحرف الحالي مع الحفاظ على تنسيق HTML
            current_html = self.typewriter_html[:self.typewriter_index + 1]

            # التأكد من أننا لا نقطع وسم HTML
            last_open_tag = current_html.rfind('<')
            last_close_tag = current_html.rfind('>')

            if last_open_tag > last_close_tag:
                # إذا كنا داخل وسم، نعود إلى بداية الوسم
                current_html = current_html[:last_open_tag]

            self.typewriter_browser.setHtml(current_html)
            self.typewriter_index += 1
        else:
            # انتهى النص، إيقاف المؤقت
            self.typewriter_timer.stop()

    def setup_notification_center_tab(self):
        """إعداد تبويب مركز الإشعارات"""
        # إنشاء حاوية قابلة للتمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        apply_theme_style(scroll_area, "graphics_view")
        
        # إنشاء ويدجت المحتوى
        content_widget = QWidget()
        apply_theme_style(content_widget, "widget")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # إضافة المحتوى إلى منطقة التمرير
        scroll_area.setWidget(content_widget)
        
        # إضافة منطقة التمرير إلى التبويب
        tab_layout = QVBoxLayout(self.notification_center_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        # عنوان التبويب
        title = QLabel("سجل الإشعارات - عرض جميع الإشعارات السابقة")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        apply_theme_style(title, "subtitle")
        layout.addWidget(title)

        # جلب مركز الإشعارات الفعلي
        try:
            from ui.notification_system import NotificationCenter
            self.notification_center = NotificationCenter(self.parent())
            apply_theme_style(self.notification_center, "notification_center")
            layout.addWidget(self.notification_center)
        except Exception as e:
            # في حالة وجود خطأ، عرض رسالة خطأ
            error_widget = QLabel(tr("error_loading_notification_center", error=str(e)))
            error_widget.setStyleSheet("color: #ff6b6b; padding: 20px;")
            apply_theme_style(error_widget, "error_label")
            layout.addWidget(error_widget)

    def setup_notification_settings_tab(self):
        """إعداد تبويب إعدادات الإشعارات"""
        # إنشاء حاوية قابلة للتمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        apply_theme_style(scroll_area, "graphics_view")
        
        # إنشاء ويدجت المحتوى
        content_widget = QWidget()
        apply_theme_style(content_widget, "widget")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # إضافة المحتوى إلى منطقة التمرير
        scroll_area.setWidget(content_widget)
        
        # إضافة منطقة التمرير إلى التبويب
        tab_layout = QVBoxLayout(self.notification_settings_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        # عنوان التبويب
        title = QLabel("إعدادات الإشعارات - التحكم في طريقة عرض وحفظ الإشعارات")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        apply_theme_style(title, "subtitle")
        layout.addWidget(title)

        # جلب إعدادات الإشعارات الفعلية
        try:
            from ui.notification_settings import NotificationSettingsWidget
            self.notification_settings = NotificationSettingsWidget(self.parent())
            apply_theme_style(self.notification_settings, "widget")
            layout.addWidget(self.notification_settings)
        except Exception as e:
            # في حالة وجود خطأ، لا تعرض رسالة الخطأ
            # إعدادات الإشعارات
            settings_layout = QVBoxLayout()
            settings_layout.setSpacing(20)
            settings_layout.setContentsMargins(0, 0, 0, 0)

            # إعدادات عرض الإشعارات
            visibility_title = QLabel(tr("notification_visibility_settings"))
            apply_theme_style(visibility_title, "title_text")
            settings_layout.addWidget(visibility_title)

            visibility_layout = QVBoxLayout()
            visibility_layout.setSpacing(10)
            visibility_layout.setContentsMargins(20, 10, 20, 10)

            # الحصول على إعدادات الإشعارات الحالية
            try:
                from ui.notification_system import global_notification_manager
                current_settings = global_notification_manager.get_notification_settings()
            except:
                current_settings = {"success": True, "warning": True, "error": True, "info": True, "do_not_save": False}

            self.notification_checkboxes = {}
            notification_types = ["success", "warning", "error", "info"]

            for notif_type in notification_types:
                checkbox = QCheckBox(tr(f"show_{notif_type}_notifications"))
                checkbox.setChecked(current_settings.get(notif_type, True))
                apply_theme_style(checkbox, "checkbox")
                visibility_layout.addWidget(checkbox)
                self.notification_checkboxes[notif_type] = checkbox

            settings_layout.addLayout(visibility_layout)

            # إعدادات حفظ الإشعارات
            memory_title = QLabel(tr("notification_storage_settings"))
            apply_theme_style(memory_title, "title_text")
            settings_layout.addWidget(memory_title)

            memory_layout = QVBoxLayout()
            memory_layout.setSpacing(10)
            memory_layout.setContentsMargins(20, 10, 20, 10)

            memory_checkbox = QCheckBox(tr("do_not_save_notifications"))
            memory_checkbox.setChecked(current_settings.get("do_not_save", False))
            apply_theme_style(memory_checkbox, "checkbox")
            memory_layout.addWidget(memory_checkbox)
            self.notification_checkboxes["do_not_save"] = memory_checkbox

            settings_layout.addLayout(memory_layout)

            # إعدادات عامة
            general_title = QLabel(tr("notification_general_settings"))
            apply_theme_style(general_title, "title_text")
            settings_layout.addWidget(general_title)

            general_layout = QFormLayout()
            general_layout.setSpacing(15)
            general_layout.setLabelAlignment(Qt.AlignRight)
            general_layout.setContentsMargins(20, 10, 20, 10)
            settings_layout.addLayout(general_layout)

            # خيارات الإشعارات
            self.enable_notifications = QCheckBox(tr("enable_notifications"))
            self.enable_notifications.setChecked(True)
            apply_theme_style(self.enable_notifications, "checkbox")
            general_layout.addRow(self.enable_notifications)

            # صوت الإشعارات
            notification_sound_layout = QHBoxLayout()
            notification_sound_layout.setSpacing(10)

            notification_sound_label = QLabel(tr("notification_sound"))
            apply_theme_style(notification_sound_label, "label")
            notification_sound_label.setMinimumWidth(160)  # تحديد عرض ثابت للنص
            notification_sound_layout.addWidget(notification_sound_label)

            self.notification_sound = QComboBox()
            self.notification_sound.addItems([tr("notification_sound_default"), tr("notification_sound_none")])
            self.notification_sound.setMinimumWidth(150)  # تحديد عرض أدنى لتحسين التناسق
            apply_theme_style(self.notification_sound, "combo")
            notification_sound_layout.addWidget(self.notification_sound)

            notification_sound_layout.addStretch()
            general_layout.addRow(notification_sound_layout)

            # مدة عرض الإشعار
            notification_duration_layout = QHBoxLayout()
            notification_duration_layout.setSpacing(10)

            notification_duration_label = QLabel(tr("notification_duration"))
            apply_theme_style(notification_duration_label, "label")
            notification_duration_label.setMinimumWidth(160)  # تحديد عرض ثابت للنص
            notification_duration_layout.addWidget(notification_duration_label)

            self.notification_duration = QSpinBox()
            self.notification_duration.setRange(1, 10)
            self.notification_duration.setValue(3)
            self.notification_duration.setSuffix(tr("seconds_suffix"))
            self.notification_duration.setMinimumWidth(80)  # تحديد عرض أدنى لتحسين التناسق
            apply_theme_style(self.notification_duration, "spin_box")
            notification_duration_layout.addWidget(self.notification_duration)

            notification_duration_layout.addStretch()
            general_layout.addRow(notification_duration_layout)

            # أزرار الحفظ والإلغاء
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(15)

            save_button = QPushButton(tr("save_all_changes_button"))
            apply_theme_style(save_button, "button")
            save_button.clicked.connect(self.save_notification_settings)
            buttons_layout.addWidget(save_button)

            cancel_button = QPushButton(tr("cancel_changes_button"))
            apply_theme_style(cancel_button, "button")
            cancel_button.clicked.connect(self.reset_notification_settings)
            buttons_layout.addWidget(cancel_button)

            settings_layout.addLayout(buttons_layout)
            layout.addLayout(settings_layout)
            layout.addStretch()

    def save_notification_settings(self):
        """حفظ إعدادات الإشعارات"""
        try:
            from ui.notification_system import global_notification_manager

            new_settings = {}
            for notif_type, checkbox in self.notification_checkboxes.items():
                new_settings[notif_type] = checkbox.isChecked()

            global_notification_manager.update_notification_settings(new_settings)

            # عرض إشعار نجاح
            try:
                global_notification_manager.show_notification(
                    self.parent(), tr("notification_settings_saved"), "success"
                )
            except:
                pass
        except Exception as e:
            # عرض إشعار خطأ
            try:
                from ui.notification_system import global_notification_manager
                global_notification_manager.show_notification(
                    self.parent(), tr("error_saving_notification_settings", error=str(e)), "error"
                )
            except:
                pass

    def reset_notification_settings(self):
        """إعادة تعيين إعدادات الإشعارات"""
        try:
            from ui.notification_system import global_notification_manager
            current_settings = global_notification_manager.get_notification_settings()

            for notif_type, checkbox in self.notification_checkboxes.items():
                checkbox.setChecked(current_settings.get(notif_type, 
                    False if notif_type == "do_not_save" else True))
        except Exception as e:
            pass

    def setup_diagnostics_tab(self):
        """إعداد تبويب التشخيص"""
        # إنشاء حاوية قابلة للتمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        apply_theme_style(scroll_area, "graphics_view")
        
        # إنشاء ويدجت المحتوى
        content_widget = QWidget()
        apply_theme_style(content_widget, "widget")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # إضافة المحتوى إلى منطقة التمرير
        scroll_area.setWidget(content_widget)
        
        # إضافة منطقة التمرير إلى التبويب
        tab_layout = QVBoxLayout(self.diagnostics_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        # تم إزالة العنوان حسب الطلب

        # تم إزالة الأزرار حسب الطلب
        
        # تم إزالة الأزرار حسب الطلب
        
        # تم إزالة الأزرار حسب الطلب
        
        # تم إزالة العنوان والأزرار حسب الطلب
        
        # إنشاء تخطيط مخصص للتبويبات
        tabs_container = QHBoxLayout()

        # إنشاء منطقة الأزرار على اليمين
        self.diagnostics_buttons_widget = QWidget()
        self.diagnostics_buttons_widget.setFixedWidth(150)
        buttons_layout = QVBoxLayout(self.diagnostics_buttons_widget)
        buttons_layout.setContentsMargins(5, 5, 5, 5)
        buttons_layout.setSpacing(5)

        # إنشاء QStackedWidget لعرض المحتوى
        self.diagnostics_stack = QStackedWidget()

        # إضافة العناصر للتخطيط
        tabs_container.addWidget(self.diagnostics_stack)
        tabs_container.addWidget(self.diagnostics_buttons_widget)

        # إضافة التخطيط للتخطيط الرئيسي
        layout.addLayout(tabs_container)

        # قائمة لحفظ أزرار التبويبات
        self.diagnostics_tab_buttons = []
        
        # إنشاء علامات التبويب المختلفة
        self.create_diagnostics_system_info_tab()
        self.create_diagnostics_performance_tab()
        self.create_diagnostics_modules_tab()
        self.create_diagnostics_logs_tab()
        
        # تحميل المعلومات عند بدء التشغيل
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.refresh_diagnostics_info)

    def run_diagnostics_action(self):
        """تشغيل التشخيص"""
        # الانتقال إلى تبويب التشخيص وتحديث المعلومات
        try:
            # الانتقال إلى تبويب التشخيص
            self.tabs_container.setCurrentWidget(self.diagnostics_tab)
            self.step_indicator.set_current_step(3)  # تبويب التشخيص هو الرابع (الفهرس 3)
            # تحديث المعلومات
            self.refresh_diagnostics_info()
        except Exception as e:
            error_widget = QLabel(tr("error_running_diagnostics", error=str(e)))
            error_widget.setStyleSheet("color: #ff6b6b; padding: 20px;")
            apply_theme_style(error_widget, "error_label")
            # عرض رسالة الخطأ في التبويب
            layout = self.diagnostics_tab.layout()
            layout.addWidget(error_widget)

    def export_diagnostics_action(self):
        """تصدير نتائج التشخيص"""
        try:
            from modules.diagnostics import run_diagnostics, export_diagnostics
            results = run_diagnostics()

            # تصدير النتائج
            file_path = export_diagnostics(results)

            # إعلام المستخدم بنجاح التصدير
            from PySide6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self.parent())
            msg_box.setWindowTitle(tr("export_success"))
            msg_box.setText(tr("diagnostics_exported_successfully", path=file_path))
            msg_box.setIcon(QMessageBox.Information)
            apply_theme_style(msg_box, "message_box")
            msg_box.exec_()
        except Exception as e:
            error_widget = QLabel(tr("error_exporting_diagnostics", error=str(e)))
            error_widget.setStyleSheet("color: #ff6b6b; padding: 20px;")
            apply_theme_style(error_widget, "error_label")
            # عرض رسالة الخطأ في التبويب
            layout = self.diagnostics_tab.layout()
            layout.addWidget(error_widget)
            
    def create_diagnostics_system_info_tab(self):
        """إنشاء تبويب معلومات النظام"""
        tab = QWidget()
        apply_theme_style(tab, "widget")
        layout = QVBoxLayout(tab)
        
        # إنشاء شجرة لعرض المعلومات
        self.diagnostics_system_tree = QTreeWidget()
        self.diagnostics_system_tree.setHeaderLabels([tr("property"), tr("value")])
        self.diagnostics_system_tree.setColumnWidth(0, 200)
        apply_theme_style(self.diagnostics_system_tree, "tree_widget")
        layout.addWidget(self.diagnostics_system_tree)
        
        # إضافة علامة التبويب
        self.diagnostics_stack.addWidget(tab)
        
        # إنشاء الزر الجانبي للتبويب
        button = QPushButton(tr("system_information"))
        button.setCheckable(True)
        button.clicked.connect(lambda: self.on_diagnostics_step_clicked(0))
        button.setStyleSheet("text-align: right; padding: 8px;")
        apply_theme_style(button, "tab_button")
        self.diagnostics_buttons_widget.layout().addWidget(button)
        self.diagnostics_tab_buttons.append(button)
        
        # تعيين الزر الأول كنشط
        if len(self.diagnostics_tab_buttons) == 1:
            button.setChecked(True)
        
    def create_diagnostics_performance_tab(self):
        """إنشاء تبويب أداء النظام"""
        tab = QWidget()
        apply_theme_style(tab, "widget")
        layout = QVBoxLayout(tab)
        
        # إنشاء شجرة لعرض معلومات الأداء
        self.diagnostics_performance_tree = QTreeWidget()
        self.diagnostics_performance_tree.setHeaderLabels([tr("metric"), tr("value"), tr("status")])
        self.diagnostics_performance_tree.setColumnWidth(0, 200)
        self.diagnostics_performance_tree.setColumnWidth(1, 150)
        apply_theme_style(self.diagnostics_performance_tree, "tree_widget")
        layout.addWidget(self.diagnostics_performance_tree)
        
        # إضافة شريط تقدم لاستخدام الموارد
        progress_layout = QHBoxLayout()
        
        # استخدام وحدة المعالجة المركزية
        cpu_layout = QVBoxLayout()
        cpu_label = QLabel(tr("cpu_usage"))
        apply_theme_style(cpu_label, "label")
        cpu_layout.addWidget(cpu_label)
        self.diagnostics_cpu_progress = QProgressBar()
        apply_theme_style(self.diagnostics_cpu_progress, "progress_bar")
        cpu_layout.addWidget(self.diagnostics_cpu_progress)
        progress_layout.addLayout(cpu_layout)
        
        # استخدام الذاكرة
        memory_layout = QVBoxLayout()
        memory_label = QLabel(tr("memory_usage"))
        apply_theme_style(memory_label, "label")
        memory_layout.addWidget(memory_label)
        self.diagnostics_memory_progress = QProgressBar()
        apply_theme_style(self.diagnostics_memory_progress, "progress_bar")
        memory_layout.addWidget(self.diagnostics_memory_progress)
        progress_layout.addLayout(memory_layout)
        
        # استخدام القرص
        disk_layout = QVBoxLayout()
        disk_label = QLabel(tr("disk_usage"))
        apply_theme_style(disk_label, "label")
        disk_layout.addWidget(disk_label)
        self.diagnostics_disk_progress = QProgressBar()
        apply_theme_style(self.diagnostics_disk_progress, "progress_bar")
        disk_layout.addWidget(self.diagnostics_disk_progress)
        progress_layout.addLayout(disk_layout)
        
        layout.addLayout(progress_layout)
        
        # إضافة علامة التبويب
        self.diagnostics_stack.addWidget(tab)
        
        # إنشاء الزر الجانبي للتبويب
        button = QPushButton(tr("performance"))
        button.setCheckable(True)
        button.clicked.connect(lambda: self.on_diagnostics_step_clicked(1))
        button.setStyleSheet("text-align: right; padding: 8px;")
        apply_theme_style(button, "tab_button")
        self.diagnostics_buttons_widget.layout().addWidget(button)
        self.diagnostics_tab_buttons.append(button)
        
    def create_diagnostics_modules_tab(self):
        """إنشاء تبويب حالة الوحدات"""
        tab = QWidget()
        apply_theme_style(tab, "widget")
        layout = QVBoxLayout(tab)
        
        # إنشاء شجرة لعرض معلومات الوحدات
        self.diagnostics_modules_tree = QTreeWidget()
        self.diagnostics_modules_tree.setHeaderLabels([tr("module"), tr("status"), tr("details")])
        self.diagnostics_modules_tree.setColumnWidth(0, 200)
        self.diagnostics_modules_tree.setColumnWidth(1, 100)
        apply_theme_style(self.diagnostics_modules_tree, "tree_widget")
        layout.addWidget(self.diagnostics_modules_tree)
        
        # إضافة زر لتثبيت المتطلبات
        self.diagnostics_install_button = QPushButton(tr("install_requirements"))
        apply_theme_style(self.diagnostics_install_button, "button")
        self.diagnostics_install_button.clicked.connect(self.install_diagnostics_requirements)
        self.diagnostics_install_button.setEnabled(False)
        layout.addWidget(self.diagnostics_install_button)
        
        # إضافة علامة التبويب
        self.diagnostics_stack.addWidget(tab)
        
        # إنشاء الزر الجانبي للتبويب
        button = QPushButton(tr("modules"))
        button.setCheckable(True)
        button.clicked.connect(lambda: self.on_diagnostics_step_clicked(2))
        button.setStyleSheet("text-align: right; padding: 8px;")
        apply_theme_style(button, "tab_button")
        self.diagnostics_buttons_widget.layout().addWidget(button)
        self.diagnostics_tab_buttons.append(button)
        
    def create_diagnostics_logs_tab(self):
        """إنشاء تبويب السجلات"""
        tab = QWidget()
        apply_theme_style(tab, "widget")
        layout = QVBoxLayout(tab)
        
        # إنشاء مربع نص لعرض السجلات
        self.diagnostics_logs_text = QTextEdit()
        self.diagnostics_logs_text.setReadOnly(True)
        apply_theme_style(self.diagnostics_logs_text, "text_edit")
        layout.addWidget(self.diagnostics_logs_text)
        
        # إضافة علامة التبويب
        self.diagnostics_stack.addWidget(tab)
        
        # إنشاء الزر الجانبي للتبويب
        button = QPushButton(tr("logs"))
        button.setCheckable(True)
        button.clicked.connect(lambda: self.on_diagnostics_step_clicked(3))
        button.setStyleSheet("text-align: right; padding: 8px;")
        apply_theme_style(button, "tab_button")
        self.diagnostics_buttons_widget.layout().addWidget(button)
        self.diagnostics_tab_buttons.append(button)
        
    def on_diagnostics_step_clicked(self, step_index):
        """التعامل مع النقر على زر التبويب الفرعي"""
        # تحديث حالة الأزرار
        for i, button in enumerate(self.diagnostics_tab_buttons):
            button.setChecked(i == step_index)
        
        # تحديث التبويب المعروض
        self.diagnostics_stack.setCurrentIndex(step_index)

    def refresh_diagnostics_info(self):
        """تحديث جميع معلومات التشخيص"""
        self.refresh_diagnostics_system_info()
        self.refresh_diagnostics_performance_info()
        self.refresh_diagnostics_modules_info()
        self.refresh_diagnostics_logs_info()
        
    def refresh_diagnostics_system_info(self):
        """تحديث معلومات النظام"""
        import platform
        import psutil
        import sys
        import os
        from datetime import datetime
        from PySide6.QtWidgets import QTreeWidgetItem
        from PySide6.QtCore import Qt
        
        self.diagnostics_system_tree.clear()
        
        # معلومات النظام الأساسية
        system_item = QTreeWidgetItem(self.diagnostics_system_tree, [tr("system_information"), ""])
        
        # نظام التشغيل
        os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
        QTreeWidgetItem(system_item, [tr("operating_system"), os_info])
        
        # معلومات المعالج
        cpu_info = f"{platform.processor()}"
        QTreeWidgetItem(system_item, [tr("processor"), cpu_info])
        
        # معلومات الذاكرة
        memory = psutil.virtual_memory()
        memory_info = f"{memory.total / (1024**3):.2f} GB"
        QTreeWidgetItem(system_item, [tr("total_memory"), memory_info])
        
        # معلومات القرص
        disk = psutil.disk_usage('/')
        disk_info = f"{disk.total / (1024**3):.2f} GB"
        QTreeWidgetItem(system_item, [tr("total_disk_space"), disk_info])
        
        # معلومات Python
        python_item = QTreeWidgetItem(self.diagnostics_system_tree, [tr("python_information"), ""])
        
        # إصدار Python
        python_version = f"{platform.python_version()}"
        QTreeWidgetItem(python_item, [tr("python_version"), python_version])
        
        # مسار Python
        python_path = f"{sys.executable}"
        QTreeWidgetItem(python_item, [tr("python_path"), python_path])
        
        # معلومات التطبيق
        app_item = QTreeWidgetItem(self.diagnostics_system_tree, [tr("application_information"), ""])
        
        # مسار التطبيق
        app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        QTreeWidgetItem(app_item, [tr("application_path"), app_path])
        
        # وقت التشغيل
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        QTreeWidgetItem(app_item, [tr("start_time"), start_time])
        
        # توسيع العناصر الرئيسية
        system_item.setExpanded(True)
        python_item.setExpanded(True)
        app_item.setExpanded(True)
        
    def refresh_diagnostics_performance_info(self):
        """تحديث معلومات الأداء"""
        import psutil
        from PySide6.QtWidgets import QTreeWidgetItem
        from PySide6.QtCore import Qt
        
        self.diagnostics_performance_tree.clear()
        
        # معلومات وحدة المعالجة المركزية
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_status = tr("good") if cpu_percent < 70 else tr("warning") if cpu_percent < 90 else tr("critical")
        cpu_item = QTreeWidgetItem(self.diagnostics_performance_tree, [tr("cpu_usage"), f"{cpu_percent}%", cpu_status])
        
        # تعيين لون الحالة
        if cpu_status == tr("good"):
            cpu_item.setForeground(2, Qt.green)
        elif cpu_status == tr("warning"):
            cpu_item.setForeground(2, Qt.yellow)
        else:
            cpu_item.setForeground(2, Qt.red)
        
        # تحديث شريط التقدم
        self.diagnostics_cpu_progress.setValue(int(cpu_percent))
        
        # معلومات الذاكرة
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_status = tr("good") if memory_percent < 70 else tr("warning") if memory_percent < 90 else tr("critical")
        memory_item = QTreeWidgetItem(self.diagnostics_performance_tree, [tr("memory_usage"), f"{memory_percent}%", memory_status])
        
        # تعيين لون الحالة
        if memory_status == tr("good"):
            memory_item.setForeground(2, Qt.green)
        elif memory_status == tr("warning"):
            memory_item.setForeground(2, Qt.yellow)
        else:
            memory_item.setForeground(2, Qt.red)
        
        # تحديث شريط التقدم
        self.diagnostics_memory_progress.setValue(int(memory_percent))
        
        # معلومات القرص
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_status = tr("good") if disk_percent < 70 else tr("warning") if disk_percent < 90 else tr("critical")
        disk_item = QTreeWidgetItem(self.diagnostics_performance_tree, [tr("disk_usage"), f"{disk_percent:.1f}%", disk_status])
        
        # تعيين لون الحالة
        if disk_status == tr("good"):
            disk_item.setForeground(2, Qt.green)
        elif disk_status == tr("warning"):
            disk_item.setForeground(2, Qt.yellow)
        else:
            disk_item.setForeground(2, Qt.red)
        
        # تحديث شريط التقدم
        self.diagnostics_disk_progress.setValue(int(disk_percent))
        
        # معلومات الشبكة
        network = psutil.net_io_counters()
        bytes_sent = network.bytes_sent / (1024**2)  # تحويل إلى ميجابايت
        bytes_recv = network.bytes_recv / (1024**2)  # تحويل إلى ميجابايت
        QTreeWidgetItem(self.diagnostics_performance_tree, [tr("bytes_sent"), f"{bytes_sent:.2f} MB", tr("normal")])
        QTreeWidgetItem(self.diagnostics_performance_tree, [tr("bytes_received"), f"{bytes_recv:.2f} MB", tr("normal")])
        
    def refresh_diagnostics_modules_info(self):
        """تحديث معلومات الوحدات"""
        import os
        from PySide6.QtWidgets import QTreeWidgetItem
        from PySide6.QtCore import Qt
        
        self.diagnostics_modules_tree.clear()
        self.diagnostics_install_button.setEnabled(False)
        missing_modules = False
        
        # المسار إلى ملف requirements.txt
        self.diagnostics_requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "requirements.txt")
        
        if not os.path.exists(self.diagnostics_requirements_path):
            item = QTreeWidgetItem(self.diagnostics_modules_tree, ["requirements.txt", tr("missing"), tr("file_not_found")])
            item.setForeground(1, Qt.red)
            return
        
        # Mapping from package name to import name
        import_map = {
            "PyMuPDF": "fitz",
            "pycryptodome": "Crypto",
            "python-bidi": "bidi",
            "pywin32": "win32api",
            "arabic_reshaper": "arabic_reshaper",
            "Pillow": "PIL"
        }
        
        with open(self.diagnostics_requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # استخراج اسم الحزمة
                    package_name = line.split('==')[0].split('>')[0].split('<')[0].strip()
                    import_name = import_map.get(package_name, package_name)
                    try:
                        __import__(import_name)
                        status = tr("loaded")
                        details = tr("module_loaded_successfully")
                        item = QTreeWidgetItem(self.diagnostics_modules_tree, [package_name, status, details])
                        item.setForeground(1, Qt.green)
                    except ImportError:
                        status = tr("missing")
                        details = tr("module_not_found")
                        item = QTreeWidgetItem(self.diagnostics_modules_tree, [package_name, status, details])
                        item.setForeground(1, Qt.red)
                        missing_modules = True
        
        if missing_modules:
            self.diagnostics_install_button.setEnabled(True)
            
    def refresh_diagnostics_logs_info(self):
        """تحديث معلومات السجلات"""
        import os
        from PySide6.QtGui import QTextCursor
        
        self.diagnostics_logs_text.clear()
        
        # الحصول على مسار ملف السجل
        try:
            # محاولة العثور على ملف السجل
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            
            # إنشاء مجلد السجلات إذا لم يكن موجودًا
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                self.diagnostics_logs_text.setText(tr("log_directory_created"))
                return
            
            # البحث عن ملفات السجل
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            
            if log_files:
                # فرز الملفات حسب تاريخ التعديل (الأحدث أولاً)
                log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
                latest_log = os.path.join(log_dir, log_files[0])
                
                with open(latest_log, 'r', encoding='utf-8') as f:
                    self.diagnostics_logs_text.setText(f.read())
                    self.diagnostics_logs_text.moveCursor(QTextCursor.End)
            else:
                self.diagnostics_logs_text.setText(tr("no_log_files_found"))
        except Exception as e:
            self.diagnostics_logs_text.setText(f"{tr('error_loading_logs')}: {str(e)}")
            
    def export_diagnostics_report(self):
        """تصدير تقرير تشخيص النظام"""
        try:
            import os
            from datetime import datetime
            from PySide6.QtCore import QTextCursor
            
            # تحديد مسار حفظ التقرير
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # إنشاء اسم الملف
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(reports_dir, f"system_diagnostics_{timestamp}.txt")
            
            # كتابة التقرير
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"=== {tr('system_diagnostics_report')} ===\n")
                f.write(f"{tr('generated_at')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # معلومات النظام
                f.write(f"=== {tr('system_information')} ===\n")
                for i in range(self.diagnostics_system_tree.topLevelItemCount()):
                    item = self.diagnostics_system_tree.topLevelItem(i)
                    self._write_diagnostics_tree_item(f, item, 0)
                
                # معلومات الأداء
                f.write(f"\n=== {tr('performance')} ===\n")
                for i in range(self.diagnostics_performance_tree.topLevelItemCount()):
                    item = self.diagnostics_performance_tree.topLevelItem(i)
                    self._write_diagnostics_tree_item(f, item, 0)
                
                # معلومات الوحدات
                f.write(f"\n=== {tr('modules')} ===\n")
                for i in range(self.diagnostics_modules_tree.topLevelItemCount()):
                    item = self.diagnostics_modules_tree.topLevelItem(i)
                    self._write_diagnostics_tree_item(f, item, 0)
                
                # السجلات
                f.write(f"\n=== {tr('logs')} ===\n")
                f.write(self.diagnostics_logs_text.toPlainText())
            
            # إظهار رسالة نجاح
            from PySide6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self.parent())
            msg_box.setWindowTitle(tr("export_success"))
            msg_box.setText(tr("report_exported_successfully"))
            msg_box.setIcon(QMessageBox.Information)
            apply_theme_style(msg_box, "message_box")
            msg_box.exec_()
            
        except Exception as e:
            # إظهار رسالة خطأ
            from PySide6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self.parent())
            msg_box.setWindowTitle(tr("error_title"))
            msg_box.setText(tr("error_exporting_report", error=str(e)))
            msg_box.setIcon(QMessageBox.Critical)
            apply_theme_style(msg_box, "message_box")
            msg_box.exec_()
            
    def install_diagnostics_requirements(self):
        """تثبيت المتطلبات المفقودة"""
        import sys
        import subprocess
        from PySide6.QtCore import QThread, Signal
        from PySide6.QtWidgets import QMessageBox
        
        class DiagnosticsRequirementsInstaller(QThread):
            """Worker thread for installing requirements."""
            installation_finished = Signal(bool, str)
            
            def __init__(self, requirements_path):
                super().__init__()
                self.requirements_path = requirements_path
            
            def run(self):
                """Install requirements using pip."""
                try:
                    command = [sys.executable, "-m", "pip", "install", "-r", self.requirements_path]
                    result = subprocess.run(command, capture_output=True, text=True, check=True)
                    self.installation_finished.emit(True, result.stdout)
                except subprocess.CalledProcessError as e:
                    self.installation_finished.emit(False, e.stderr)
                except FileNotFoundError:
                    self.installation_finished.emit(False, "pip is not installed or not in PATH.")
        
        def on_installation_finished(success, output):
            """Handle installation finished signal."""
            if success:
                msg_box = QMessageBox(self.parent())
                msg_box.setWindowTitle(tr("success_title"))
                msg_box.setText(tr("requirements_installed_successfully"))
                msg_box.setIcon(QMessageBox.Information)
                apply_theme_style(msg_box, "message_box")
                msg_box.exec_()
            else:
                msg_box = QMessageBox(self.parent())
                msg_box.setWindowTitle(tr("error_title"))
                msg_box.setText(tr("failed_to_install_requirements"))
                msg_box.setDetailedText(output)
                msg_box.setIcon(QMessageBox.Critical)
                apply_theme_style(msg_box, "message_box")
                msg_box.exec_()
            
            self.diagnostics_install_button.setText(tr("install_requirements"))
            self.refresh_diagnostics_modules_info()
        
        self.diagnostics_install_button.setEnabled(False)
        self.diagnostics_install_button.setText(tr("installing"))
        self.installer = DiagnosticsRequirementsInstaller(self.diagnostics_requirements_path)
        self.installer.installation_finished.connect(on_installation_finished)
        self.installer.start()
        
    def _write_diagnostics_tree_item(self, file, item, level):
        """كتابة عنصر الشجرة إلى الملف"""
        indent = "  " * level
        file.write(f"{indent}{item.text(0)}: {item.text(1)}\n")
        
        # كتابة العناصر الفرعية
        for i in range(item.childCount()):
            self._write_diagnostics_tree_item(file, item.child(i), level + 1)
