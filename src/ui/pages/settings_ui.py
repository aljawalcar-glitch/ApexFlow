"""
واجهة الإعدادات بتصميم Step Wizard شفاف
Transparent Step Wizard Settings UI for ApexFlow
"""
import sys
import os
import copy

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QFrame, QScrollArea, QStackedWidget,
    QApplication, QDialog, QMessageBox
)
from src.ui.widgets.labeled_toggle_switch import LabeledToggleSwitch
from PySide6.QtCore import Qt, QTimer, Signal
from utils import settings
from managers.theme_manager import global_theme_manager, make_theme_aware
from ui.widgets.ui_helpers import FocusAwareComboBox
from ui.widgets.icon_utils import create_colored_icon_button
from managers.notification_system import show_success, show_warning, show_error, show_info
from utils.i18n import tr
from utils.translator import reload_translations
from managers.language_manager import language_manager

# Import new page classes
from src.ui.settings.appearance_page import AppearancePage
from src.ui.settings.fonts_page import FontsPage
from src.ui.settings.general_page import GeneralPage
from src.ui.settings.save_page import SavePage
from src.ui.settings.step_indicator import StepIndicator


class TransparentFrame(QFrame):
    """فريم شفاف للمحتوى"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
    
    def setup_style(self):
        """إعداد التنسيق الموحد للفريم"""
        make_theme_aware(self, "surface")

class SettingsUI(QDialog):
    """واجهة الإعدادات الرئيسية بتصميم Step Wizard"""

    settings_changed = Signal()

    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setStyleSheet("background-color: transparent;")
            self.setWindowTitle(tr("settings_window_title"))

            self._setup_managers(parent)
            self.settings_data = settings.load_settings()
            self.original_settings = copy.deepcopy(self.settings_data)
            self.temporary_settings = copy.deepcopy(self.settings_data)
            self.current_step = 0
            self.has_unsaved_changes = False
            self.is_loading = True

            self._create_all_widgets()
            self.init_ui()

            QTimer.singleShot(50, self._load_settings_to_ui)
            QTimer.singleShot(1000, self._show_welcome_notification)
            QTimer.singleShot(500, self.finish_loading)

        except Exception as e:
            print(f"خطأ في تهيئة واجهة الإعدادات: {e}")
            import traceback
            traceback.print_exc()

    def _get_main_window(self):
        parent = self.parent()
        while parent:
            if parent.__class__.__name__ == 'ApexFlow':
                return parent
            parent = parent.parent()
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ApexFlow':
                return widget
        return None

    def _show_welcome_notification(self):
        settings_data = settings.load_settings()
        if settings_data.get("disable_welcome_message", False):
            return
        main_window = self._get_main_window()
        if main_window:
            main_window.notification_manager.show_notification(tr("settings_welcome_message"), "info", 4000)
        else:
            show_info(tr("settings_welcome_message"), duration=4000)

    def _setup_managers(self, parent):
        if parent and hasattr(parent, 'notification_manager'):
            self.notification_manager = parent.notification_manager
        else:
            from managers.notification_system import global_notification_manager
            self.notification_manager = global_notification_manager

    def _create_all_widgets(self):
        # Appearance
        self.theme_combo = FocusAwareComboBox()
        self.theme_combo.addItems(["dark", "light", "blue", "green", "purple"])
        self.accent_color_input = QLineEdit()
        self.language_combo = FocusAwareComboBox()
        self.language_combo.addItems(["العربية", "English"])
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.size_combo = FocusAwareComboBox()
        self.size_combo.addItems([tr("size_small"), tr("size_medium"), tr("size_large"), tr("size_xlarge")])
        self.contrast_combo = FocusAwareComboBox()
        self.contrast_combo.addItems([tr("contrast_low"), tr("contrast_normal"), tr("contrast_high"), tr("contrast_xhigh")])

        # Fonts
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(8, 24)
        self.title_font_size_slider = QSlider(Qt.Horizontal)
        self.title_font_size_slider.setRange(16, 32)
        self.menu_font_size_slider = QSlider(Qt.Horizontal)
        self.menu_font_size_slider.setRange(10, 20)
        self.font_family_combo = FocusAwareComboBox()
        self.font_family_combo.addItems([tr("system_default_font"), "Arial", "Tahoma", "Segoe UI", "Cairo", "Amiri", "Noto Sans Arabic"])
        self.font_weight_combo = FocusAwareComboBox()
        self.font_weight_combo.addItems([tr("font_weight_normal"), tr("font_weight_bold"), tr("font_weight_extrabold")])
        self.text_direction_combo = FocusAwareComboBox()
        self.text_direction_combo.addItems([tr("text_direction_auto"), tr("text_direction_rtl"), tr("text_direction_ltr")])
        self.show_tooltips_check = LabeledToggleSwitch(tr("show_tooltips_check"))
        self.enable_animations_check = LabeledToggleSwitch(tr("enable_animations_check"))
        self.font_preview_label = QLabel(tr("font_preview_text"))

        # General
        self.sequential_drops_checkbox = LabeledToggleSwitch(tr("allow_sequential_drops_option"))
        self.disable_welcome_checkbox = LabeledToggleSwitch(tr("disable_welcome_message_option"))
        self.remember_state_checkbox = LabeledToggleSwitch(tr("remember_settings_on_exit_option"))
        self.reset_to_defaults_checkbox = LabeledToggleSwitch(tr("reset_to_defaults_next_time_option"))
        self.show_success_notifications_checkbox = LabeledToggleSwitch(tr("show_success_notifications"))
        self.show_warning_notifications_checkbox = LabeledToggleSwitch(tr("show_warning_notifications"))
        self.show_error_notifications_checkbox = LabeledToggleSwitch(tr("show_error_notifications"))
        self.show_info_notifications_checkbox = LabeledToggleSwitch(tr("show_info_notifications"))
        self.do_not_save_notifications_checkbox = LabeledToggleSwitch(tr("do_not_save_notifications"))

        # Save
        self.changes_report = QLabel()
        self.reset_defaults_btn = QPushButton(tr("reset_to_defaults_button"))
        self.save_only_btn = QPushButton(tr("save_only_button"))
        self.save_restart_btn = QPushButton(tr("save_and_restart_button"))
        self.cancel_btn = QPushButton(tr("cancel_changes_button"))

        self._connect_signals()

    def _connect_signals(self):
        # Connect signals that trigger changes
        all_widgets = [
            self.theme_combo, self.accent_color_input, self.language_combo, self.transparency_slider,
            self.size_combo, self.contrast_combo, self.font_size_slider, self.title_font_size_slider,
            self.menu_font_size_slider, self.font_family_combo, self.font_weight_combo, self.text_direction_combo,
            self.show_tooltips_check, self.enable_animations_check, self.sequential_drops_checkbox,
            self.disable_welcome_checkbox, self.remember_state_checkbox, self.reset_to_defaults_checkbox,
            self.show_success_notifications_checkbox, self.show_warning_notifications_checkbox,
            self.show_error_notifications_checkbox, self.show_info_notifications_checkbox,
            self.do_not_save_notifications_checkbox
        ]
        for widget in all_widgets:
            if isinstance(widget, (LabeledToggleSwitch, QSlider)):
                widget.stateChanged.connect(self.mark_as_changed) if isinstance(widget, LabeledToggleSwitch) else widget.valueChanged.connect(self.mark_as_changed)
            else:
                widget.currentTextChanged.connect(self.mark_as_changed) if hasattr(widget, 'currentTextChanged') else widget.textChanged.connect(self.mark_as_changed)

        # Special connections
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        self.reset_to_defaults_checkbox.stateChanged.connect(self.on_reset_defaults_changed)
        
        # Font preview updates
        for font_widget in [self.font_size_slider, self.title_font_size_slider, self.menu_font_size_slider, self.font_family_combo, self.font_weight_combo]:
            font_widget.valueChanged.connect(self.update_font_preview) if hasattr(font_widget, 'valueChanged') else font_widget.currentTextChanged.connect(self.update_font_preview)

        # Save/Cancel buttons
        self.reset_defaults_btn.clicked.connect(self.reset_to_defaults)
        self.save_only_btn.clicked.connect(self.save_only)
        self.save_restart_btn.clicked.connect(self.save_and_restart)
        self.cancel_btn.clicked.connect(self.cancel_changes)

    def finish_loading(self):
        self.is_loading = False
        self.has_unsaved_changes = False
        self.update_changes_report()
        self.update_save_buttons_state()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.step_indicator = StepIndicator()
        self.step_indicator.step_clicked.connect(self.go_to_step)
        main_layout.addWidget(self.step_indicator)
        
        self.content_frame = TransparentFrame()
        make_theme_aware(self.content_frame, "surface")
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: transparent;")
        self.create_step_pages()
        content_layout.addWidget(self.content_stack)
        
        self.nav_container = TransparentFrame()
        nav_layout = QHBoxLayout(self.nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(15)
        nav_layout.addSpacing(30)

        # تحديد الاتجاه بناءً على اللغة المحددة في الإعدادات
        current_language = self.settings_data.get("language", "ar")
        is_rtl = current_language == "ar"
        prev_icon = "chevron-right" if is_rtl else "chevron-left"
        next_icon = "chevron-left" if is_rtl else "chevron-right"

        self.prev_btn = create_colored_icon_button(prev_icon, 24, "", tr("previous_step"))
        self.prev_btn.clicked.connect(self.previous_step)
        self.next_btn = create_colored_icon_button(next_icon, 24, "", tr("next_step"))
        self.next_btn.clicked.connect(self.next_step)

        # فرض اتجاه التخطيط على الحاوية
        from PySide6.QtCore import Qt
        if is_rtl:
            self.nav_container.setLayoutDirection(Qt.RightToLeft)
        else:
            self.nav_container.setLayoutDirection(Qt.LeftToRight)
            
        # ضع الأزرار بنفس الترتيب ودع Qt يتعامل مع الاتجاه
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()

        content_layout.addWidget(self.nav_container)
        main_layout.addWidget(self.content_frame)
        
        self.go_to_step(0)

    def create_step_pages(self):
        # Instantiate pages and add them to the stack
        self.page_widgets = [
            AppearancePage(self.settings_data, self),
            FontsPage(self.settings_data, self),
            GeneralPage(self.settings_data, self),
            SavePage(self.settings_data, self)
        ]
        for widget in self.page_widgets:
            scroll_area = QScrollArea()
            make_theme_aware(scroll_area, "scroll_area")
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setWidget(widget)
            self.content_stack.addWidget(scroll_area)

    def update_font_preview(self):
        try:
            font_size = self.font_size_slider.value()
            font_family = self.font_family_combo.currentText()
            font_weight = self.font_weight_combo.currentText()
            preview_text = tr("font_preview_dynamic_text", family=font_family, size=font_size, weight=font_weight)
            self.font_preview_label.setText(preview_text)
        except Exception as e:
            print(f"خطأ في تحديث معاينة الخط: {e}")

    def reset_to_defaults(self):
        from utils.default_settings import reset_to_defaults
        if reset_to_defaults():
            self.settings_data = settings.load_settings(force_reload=True)
            self._load_settings_to_ui()
            from managers.theme_manager import refresh_all_themes
            refresh_all_themes()
            self.update_changes_report()
            show_success(tr("reset_success_message"))
        else:
            show_error(tr("reset_error_message"))

    def save_current_as_default(self):
        if self.save_all_settings():
            from utils.default_settings import save_current_as_default
            if save_current_as_default():
                show_success(tr("save_default_success_message"))
            else:
                show_error(tr("save_default_error_message"))

    def choose_accent_color(self):
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor
        current_color = QColor(self.accent_color_input.text() or "#056a51")
        color = QColorDialog.getColor(current_color, self, tr("choose_accent_color_dialog_title"))
        if color.isValid():
            self.accent_color_input.setText(color.name())

    def go_to_step(self, step):
        if 0 <= step < self.content_stack.count():
            self.current_step = step
            self.content_stack.setCurrentIndex(step)
            self.step_indicator.set_current_step(step)
            self.update_navigation_buttons()
            if step == self.content_stack.count() - 1:
                self.update_changes_report()

    def next_step(self):
        self.go_to_step(self.current_step + 1)

    def previous_step(self):
        self.go_to_step(self.current_step - 1)

    def update_navigation_buttons(self):
        num_steps = self.content_stack.count()
        self.next_btn.setEnabled(self.current_step < num_steps - 1)
        self.prev_btn.setEnabled(self.current_step > 0)

    def update_save_buttons_state(self):
        if hasattr(self, 'save_only_btn') and hasattr(self, 'cancel_btn'):
            has_changes = getattr(self, 'has_unsaved_changes', False)
            self.save_only_btn.setEnabled(has_changes)
            self.save_restart_btn.setEnabled(has_changes)
            self.cancel_btn.setEnabled(has_changes)

    def update_changes_report(self):
        """Updates the changes report by comparing temporary settings with original settings."""
        if not self.has_unsaved_changes:
            self.changes_report.setText(tr("no_unsaved_changes"))
            return

        report_lines = []

        def translate_value(value):
            if isinstance(value, bool):
                return tr("true") if value else tr("false")
            # محاولة ترجمة القيم الشائعة
            value_str = str(value)
            
            # ترجمة القيم الخاصة بالسمات
            theme_translations = {
                "dark": tr("theme_dark", default_value="Dark"),
                "light": tr("theme_light", default_value="Light"), 
                "blue": tr("theme_blue", default_value="Blue"),
                "green": tr("theme_green", default_value="Green"),
                "purple": tr("theme_purple", default_value="Purple")
            }
            
            # ترجمة أحجام الخط
            size_translations = {
                "Small (Compact)": tr("size_small"),
                "Medium (Default)": tr("size_medium"),
                "Large (Comfortable)": tr("size_large"),
                "Extra Large (Accessibility)": tr("size_xlarge")
            }
            
            # ترجمة مستويات التباين
            contrast_translations = {
                "Low (Soft)": tr("contrast_low"),
                "Normal (Balanced)": tr("contrast_normal"),
                "High (Clear)": tr("contrast_high"),
                "Extra High (Accessibility)": tr("contrast_xhigh")
            }
            
            # ترجمة أوزان الخط
            weight_translations = {
                "Normal": tr("font_weight_normal"),
                "Bold": tr("font_weight_bold"),
                "Extra Bold": tr("font_weight_extrabold")
            }
            
            # ترجمة اتجاه النص
            direction_translations = {
                "Auto": tr("text_direction_auto"),
                "Right-to-Left": tr("text_direction_rtl"),
                "Left-to-Right": tr("text_direction_ltr")
            }
            
            # البحث في جميع القواميس
            all_translations = {
                **theme_translations,
                **size_translations, 
                **contrast_translations,
                **weight_translations,
                **direction_translations
            }
            
            if value_str in all_translations:
                return all_translations[value_str]
            
            # محاولة ترجمة عامة
            translated = tr(value_str.lower().replace(" ", "_"))
            return translated if translated != value_str.lower().replace(" ", "_") else value_str

        def find_diffs(temp_dict, orig_dict, parent_key=''):
            for key, temp_value in temp_dict.items():
                # Path for nested keys, used for translation keys
                full_key_path = f"{parent_key}.{key}" if parent_key else key
                
                orig_value = orig_dict.get(key)

                if isinstance(temp_value, dict) and isinstance(orig_value, dict):
                    # Recurse into nested dictionaries
                    find_diffs(temp_value, orig_value, parent_key=key)
                elif temp_value != orig_value:
                    # Values are different, add to report
                    # Use the simple key for translation as that's how they are stored in i18n
                    translated_key = tr(key)
                    report_lines.append(
                        f"<li><b>{translated_key}:</b> {tr('from')} "
                        f"<i>{translate_value(orig_value)}</i> {tr('to')} "
                        f"<i>{translate_value(temp_value)}</i></li>"
                    )

        find_diffs(self.temporary_settings, self.original_settings)

        if report_lines:
            report_html = f"<h3>{tr('summary_of_changes')}</h3><ul>" + "".join(report_lines) + "</ul>"
            self.changes_report.setText(report_html)
        else:
            # This case might happen if a change was reverted before saving
            self.changes_report.setText(tr("no_unsaved_changes"))
            self.has_unsaved_changes = False
            self.update_save_buttons_state()

    def _update_temporary_settings_from_ui(self):
        """يجمع الإعدادات الحالية من واجهة المستخدم ويحدث القاموس المؤقت"""
        try:
            self.temporary_settings["theme"] = self.theme_combo.currentText()
            self.temporary_settings["accent_color"] = self.accent_color_input.text() or "#ff6f00"
            self.temporary_settings["language"] = "ar" if self.language_combo.currentText() == "العربية" else "en"
            
            ui_settings = self.temporary_settings.get("ui_settings", {})
            ui_settings.update({
                "font_size": self.font_size_slider.value(),
                "title_font_size": self.title_font_size_slider.value(),
                "menu_font_size": self.menu_font_size_slider.value(),
                "font_family": self.font_family_combo.currentText(),
                "font_weight": self.font_weight_combo.currentText(),
                "text_direction": self.text_direction_combo.currentText(),
                "show_tooltips": self.show_tooltips_check.isChecked(),
                "enable_animations": self.enable_animations_check.isChecked(),
                "transparency": self.transparency_slider.value(),
                "size": self.size_combo.currentText(),
                "contrast": self.contrast_combo.currentText()
            })
            self.temporary_settings["ui_settings"] = ui_settings
            
            self.temporary_settings["allow_sequential_drops"] = self.sequential_drops_checkbox.isChecked()
            self.temporary_settings["disable_welcome_message"] = self.disable_welcome_checkbox.isChecked()
            self.temporary_settings["remember_settings_on_exit"] = self.remember_state_checkbox.isChecked()
            self.temporary_settings["reset_to_defaults_next_time"] = self.reset_to_defaults_checkbox.isChecked()
            
            notification_settings = self.temporary_settings.get("notification_settings", {})
            notification_settings.update({
                "success": self.show_success_notifications_checkbox.isChecked(),
                "warning": self.show_warning_notifications_checkbox.isChecked(),
                "error": self.show_error_notifications_checkbox.isChecked(),
                "info": self.show_info_notifications_checkbox.isChecked(),
                "do_not_save": self.do_not_save_notifications_checkbox.isChecked()
            })
            self.temporary_settings["notification_settings"] = notification_settings
            
        except Exception as e:
            print(f"خطأ في تحديث الإعدادات المؤقتة: {e}")

    def get_current_settings(self):
        # This method remains the same, collecting data from all self.widgets
        current = {}
        try:
            current["theme"] = self.theme_combo.currentText()
            current["accent_color"] = self.accent_color_input.text() or "#ff6f00"
            current["language"] = "ar" if self.language_combo.currentText() == "العربية" else "en"
            ui_settings = {
                "font_size": self.font_size_slider.value(),
                "title_font_size": self.title_font_size_slider.value(),
                "menu_font_size": self.menu_font_size_slider.value(),
                "font_family": self.font_family_combo.currentText(),
                "font_weight": self.font_weight_combo.currentText(),
                "text_direction": self.text_direction_combo.currentText(),
                "show_tooltips": self.show_tooltips_check.isChecked(),
                "enable_animations": self.enable_animations_check.isChecked(),
                "transparency": self.transparency_slider.value(),
                "size": self.size_combo.currentText(),
                "contrast": self.contrast_combo.currentText()
            }
            current["ui_settings"] = ui_settings
            current["allow_sequential_drops"] = self.sequential_drops_checkbox.isChecked()
            current["disable_welcome_message"] = self.disable_welcome_checkbox.isChecked()
            current["remember_settings_on_exit"] = self.remember_state_checkbox.isChecked()
            current["reset_to_defaults_next_time"] = self.reset_to_defaults_checkbox.isChecked()
            current["notification_settings"] = {
                "success": self.show_success_notifications_checkbox.isChecked(),
                "warning": self.show_warning_notifications_checkbox.isChecked(),
                "error": self.show_error_notifications_checkbox.isChecked(),
                "info": self.show_info_notifications_checkbox.isChecked(),
                "do_not_save": self.do_not_save_notifications_checkbox.isChecked()
            }
        except Exception as e:
            print(f"خطأ في قراءة الإعدادات: {e}")
        return current

    def on_reset_defaults_changed(self, state):
        is_checked = state == Qt.Checked
        self.remember_state_checkbox.setEnabled(not is_checked)
        self.disable_welcome_checkbox.setEnabled(not is_checked)
        if is_checked:
            show_info(tr("reset_defaults_info_message"))

    def _load_settings_to_ui(self):
        """تحميل الإعدادات إلى واجهة المستخدم"""
        try:
            self.is_loading = True
            
            # Appearance Settings
            self.theme_combo.setCurrentText(self.temporary_settings.get("theme", "dark"))
            self.accent_color_input.setText(self.temporary_settings.get("accent_color", "#ff6f00"))
            self.language_combo.setCurrentText("العربية" if self.temporary_settings.get("language", "en") == "ar" else "English")

            # UI Settings (Nested)
            ui_settings = self.temporary_settings.get("ui_settings", {})
            self.transparency_slider.setValue(ui_settings.get("transparency", 50))
            self.size_combo.setCurrentText(ui_settings.get("size", tr("size_medium")))
            self.contrast_combo.setCurrentText(ui_settings.get("contrast", tr("contrast_normal")))
            self.font_size_slider.setValue(ui_settings.get("font_size", 12))
            self.title_font_size_slider.setValue(ui_settings.get("title_font_size", 20))
            self.menu_font_size_slider.setValue(ui_settings.get("menu_font_size", 14))
            self.font_family_combo.setCurrentText(ui_settings.get("font_family", tr("system_default_font")))
            self.font_weight_combo.setCurrentText(ui_settings.get("font_weight", tr("font_weight_normal")))
            self.text_direction_combo.setCurrentText(ui_settings.get("text_direction", tr("text_direction_auto")))
            self.show_tooltips_check.setChecked(ui_settings.get("show_tooltips", True))
            self.enable_animations_check.setChecked(ui_settings.get("enable_animations", True))

            # General Settings
            self.sequential_drops_checkbox.setChecked(self.temporary_settings.get("allow_sequential_drops", False))
            self.disable_welcome_checkbox.setChecked(self.temporary_settings.get("disable_welcome_message", False))
            self.remember_state_checkbox.setChecked(self.temporary_settings.get("remember_settings_on_exit", True))
            self.reset_to_defaults_checkbox.setChecked(self.temporary_settings.get("reset_to_defaults_next_time", False))

            # Notification Settings (Nested)
            notification_settings = self.temporary_settings.get("notification_settings", {})
            self.show_success_notifications_checkbox.setChecked(notification_settings.get("success", True))
            self.show_warning_notifications_checkbox.setChecked(notification_settings.get("warning", True))
            self.show_error_notifications_checkbox.setChecked(notification_settings.get("error", True))
            self.show_info_notifications_checkbox.setChecked(notification_settings.get("info", True))
            self.do_not_save_notifications_checkbox.setChecked(notification_settings.get("do_not_save", False))

        except Exception as e:
            print(f"خطأ أثناء تحميل الإعدادات إلى الواجهة: {e}")
        finally:
            # Use QTimer to ensure this runs after the current event loop cycle
            QTimer.singleShot(0, self.finish_loading)

    def adjust_navigation_buttons(self):
        """تعديل اتجاه الأزرار السفلية بناءً على اللغة"""
        is_rtl = self.language_combo.currentText() == "العربية"
        
        prev_icon = "chevron-right" if is_rtl else "chevron-left"
        next_icon = "chevron-left" if is_rtl else "chevron-right"

        # تحديث الأيقونات
        from ui.widgets.icon_utils import create_colored_icon_button
        self.prev_btn.setIcon(create_colored_icon_button(prev_icon, 24).icon())
        self.next_btn.setIcon(create_colored_icon_button(next_icon, 24).icon())

        # فرض اتجاه التخطيط على الحاوية
        from PySide6.QtCore import Qt
        if is_rtl:
            self.nav_container.setLayoutDirection(Qt.RightToLeft)
        else:
            self.nav_container.setLayoutDirection(Qt.LeftToRight)

        # إعادة إنشاء التخطيط بالكامل
        old_layout = self.nav_container.layout()
        if old_layout:
            old_layout.setParent(None)
            
        from PySide6.QtWidgets import QHBoxLayout
        new_layout = QHBoxLayout(self.nav_container)
        new_layout.setContentsMargins(0, 0, 0, 0)
        new_layout.setSpacing(15)
        new_layout.addSpacing(30)
        
        # في جميع الحالات، ضع الأزرار بنفس الترتيب ودع Qt يتعامل مع الاتجاه
        new_layout.addWidget(self.prev_btn)
        new_layout.addWidget(self.next_btn)
        new_layout.addStretch()

    def on_language_changed(self, language_text):
        """
        Handles the language selection change.
        This method only marks the setting as changed and updates the temporary settings.
        No UI changes are applied immediately to prevent instability.
        The application must be restarted for the language change to take effect.
        """
        if self.is_loading:
            return
        
        # Only mark the setting as changed. The actual change will be applied on restart.
        self.mark_as_changed()

    def mark_as_changed(self):
        if self.is_loading: return
        if not self.has_unsaved_changes:
            show_info(tr("settings_modified_notification"))
        self.has_unsaved_changes = True
        self._update_temporary_settings_from_ui()
        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(7, True)
        QTimer.singleShot(100, self.update_changes_report)
        self.update_save_buttons_state()
        
    def save_only(self):
        """حفظ الإعدادات فقط بدون تطبيق"""
        if self._perform_save():
            main_window = self._get_main_window()
            if main_window:
                main_window.handle_settings_save_only()
    
    def save_and_restart(self):
        """حفظ الإعدادات وإعادة التشغيل"""
        if self._perform_save():
            main_window = self._get_main_window()
            if main_window:
                main_window.handle_settings_save_and_restart()
    
    def _perform_save(self):
        """المنطق الفعلي لحفظ الإعدادات"""
        try:
            self.settings_data.update(self.temporary_settings)
            if settings.save_settings(self.settings_data):
                self.original_settings = copy.deepcopy(self.settings_data)
                self.has_unsaved_changes = False
                self.update_changes_report()
                self.update_save_buttons_state()
                main_window = self._get_main_window()
                if main_window:
                    main_window.set_page_has_work(7, False)
                return True
            else:
                show_error(tr("settings_save_failed"))
                return False
        except Exception as e:
            print(f"خطأ في حفظ الإعدادات: {e}")
            show_error(tr("settings_save_error"))
            return False


            
    def cancel_changes(self):
        """إلغاء التغييرات والعودة للإعدادات الأصلية"""
        if self.has_unsaved_changes:
            self.temporary_settings = copy.deepcopy(self.original_settings)
            self._load_settings_to_ui()
            self.has_unsaved_changes = False
            self.update_changes_report()
            self.update_save_buttons_state()
            main_window = self._get_main_window()
            if main_window:
                main_window.set_page_has_work(7, False)
            show_info(tr("changes_canceled_message"))
        QTimer.singleShot(150, self.update_save_buttons_state)
