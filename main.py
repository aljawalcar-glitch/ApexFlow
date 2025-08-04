"""
ApexFlow - PDF file processing application
Main simplified and organized file
"""

# Basic library imports
import sys
import os

# Add config folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout,
    QWidget, QStackedWidget, QListWidget, QLabel, QScrollArea, QPushButton,
    QGridLayout
)
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QSharedMemory, QSystemSemaphore

# Local module imports
from modules.settings import load_settings, set_setting  # Direct import to avoid loading PDF modules
from modules.app_utils import get_icon_path
from modules.logger import debug, info, warning, error
from ui import WelcomePage, apply_theme_style
from ui.notification_system import NotificationBar
from ui.first_run_dialog import FirstRunDialog
from modules.translator import tr

# ===============================
# Main application classes
# ===============================

class SingleApplication(QApplication):
    """Single window application only"""

    def __init__(self, argv):
        super().__init__(argv)

        # Create unique identifier for the application
        self._key = "ApexFlow_SingleInstance_Key"
        self._memory = QSharedMemory(self._key)
        self._semaphore = QSystemSemaphore(self._key, 1)

        # Try to create shared memory
        if self._memory.attach():
            # Application is already running
            self._is_running = True
        else:
            # First time running the application
            self._is_running = False
            if not self._memory.create(1):
                self._is_running = True

    def is_running(self):
        """Check if the application is already running"""
        return self._is_running

class ApexFlow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._settings_ui_module = None

        # Load basic settings only (speed up startup)
        self.settings_data = load_settings()

        # Create all required managers
        self._setup_managers()

        # Apply unified window properties
        self.window_manager.set_window_properties(self, tr("main_window_title"))
        self.setGeometry(200, 100, 1000, 600)

        # Create interface first
        self.initUI()

        # Apply theme and settings in a deferred manner
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._initialize_delayed)

    def _setup_managers(self):
        """Setup all required managers"""
        # Basic managers
        from ui.theme_manager import WindowManager, global_theme_manager
        from modules.app_utils import FileManager, MessageManager
        from ui.notification_system import global_notification_manager
        from ui.pdf_worker import WorkerManager

        self.window_manager = WindowManager(self)
        self.file_manager = FileManager(self)
        self.message_manager = MessageManager(self)

        # Defer creating OperationsManager until needed (to avoid pywin32 error messages)
        self.operations_manager = None
        self._operations_manager_creation_attempted = False

        # Specialized managers
        self.theme_manager = global_theme_manager
        self.notification_manager = global_notification_manager
        self.worker_manager = WorkerManager()

        # Setup page manager (use existing variables)
        self.pages_loaded = [True, False, False, False, False, False, False, False]

    def get_operations_manager(self):
        """Create or return OperationsManager (lazy loading)"""
        if self.operations_manager is None and not self._operations_manager_creation_attempted:
            self._operations_manager_creation_attempted = True
            try:
                from modules.app_utils import OperationsManager
                self.operations_manager = OperationsManager(self, self.file_manager, self.message_manager)
                debug("OperationsManager created successfully (lazy)")
            except Exception as e:
                error(f"Error creating OperationsManager: {e}")
                # Create dummy operations manager
                class DummyOperationsManager:
                    """Dummy operations manager in case of pywin32 failure"""
                    def get_available_printers(self):
                        return ["Microsoft Print to PDF"]
                    def print_files(self, files, printer_name=None, parent_widget=None):
                        # Dummy manager - doesn't actually print
                        return False
                    def merge_files(self, parent_widget):
                        # Dummy manager - doesn't actually merge
                        return False
                self.operations_manager = DummyOperationsManager()

        return self.operations_manager

    def _initialize_delayed(self):
        """Delayed initialization of heavy components"""
        # Load theme from settings
        self.theme_manager.load_theme_from_settings()

        # Apply interface direction
        self.apply_layout_direction()

        # Validate settings
        self._validate_settings_delayed()

    def apply_layout_direction(self):
        """Apply interface direction based on current language"""
        language = self.settings_data.get("language", "ar")
        if language == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

    def refresh_main_window_theme(self):
        """Refreshes the theme of the main window and all its components using the ThemeManager."""
        try:
            self.settings_data = load_settings()
            
            # Use the theme manager to re-apply the theme to all registered widgets
            self.theme_manager.change_theme(self.settings_data.get("theme"), self.settings_data.get("accent_color"))

            # Specifically refresh pages that might have been loaded
            self.refresh_all_loaded_pages()

            debug("Theme re-applied to the main window via ThemeManager.")

        except Exception as e:
            error(f"Error refreshing main window theme: {e}")

    def _validate_settings_delayed(self):
        """Validate settings in a deferred manner using managers"""
        try:
            # Validate settings
            if not self._validate_settings(self.settings_data):
                self.notification_manager.show_notification(
                    self, tr("settings_issues_detected"),
                    "warning"
                )
                self.settings_data = self._get_default_settings()

            # Print settings information (deferred)
            from modules.settings import print_settings_info
            print_settings_info()

            debug("Settings validated in deferred manner")
        except Exception as e:
            error(f"Error in deferred settings validation: {e}")

    @property
    def settings_ui(self):
        """Load settings interface when needed"""
        if self._settings_ui_module is None:
            from ui.settings_ui import SettingsUI
            self._settings_ui_module = SettingsUI
        return self._settings_ui_module

    def _create_sidebar(self):
        """Creates the sidebar widget."""
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Sidebar menu
        self.menu_list = QListWidget()
        self.menu_list.addItems([
            tr("menu_home"), tr("menu_merge_print"), tr("menu_split"),
            tr("menu_compress"), tr("menu_stamp_rotate"), tr("menu_convert"),
            tr("menu_security"), tr("menu_settings")
        ])
        self.menu_list.setFocusPolicy(Qt.NoFocus)
        self.menu_list.setSelectionMode(QListWidget.SingleSelection)
        self.menu_list.setCurrentRow(0)
        apply_theme_style(self.menu_list, "menu")
        sidebar_layout.addWidget(self.menu_list)

        # App info widget
        from ui.app_info_widget import AppInfoWidget
        self.app_info = AppInfoWidget()
        sidebar_layout.addWidget(self.app_info)

        # Notification history button
        self.notification_history_button = QPushButton(tr("notifications_button"))
        apply_theme_style(self.notification_history_button, "button")
        self.notification_history_button.clicked.connect(self.notification_manager.show_notification_center)
        sidebar_layout.addWidget(self.notification_history_button)

        return sidebar_widget

    def _create_main_content(self):
        """Creates the main content area with the stacked widget and notification bar."""
        # Create the stacked widget for pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")

        # Welcome page
        self.welcome_page = WelcomePage()
        self.welcome_page.navigate_to_page.connect(self.navigate_to_page)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.welcome_page)
        apply_theme_style(scroll, "graphics_view")
        scroll.viewport().setStyleSheet("background: transparent;")
        self.stack.addWidget(scroll)
        self.stack.setCurrentIndex(0)

        # Placeholder pages
        page_names = [
            tr("menu_merge_print"), tr("menu_split"), tr("menu_compress"),
            tr("menu_stamp_rotate"), tr("menu_convert"), tr("menu_security"),
            tr("menu_settings")
        ]
        self.pages_loaded = [True] + [False] * len(page_names)
        for page_name in page_names:
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            layout.setAlignment(Qt.AlignCenter)
            label = QLabel(tr("loading_page_message", page_name=page_name))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: normal;")
            layout.addWidget(label)
            self.stack.addWidget(placeholder)

        # Right panel to hold the stack and notification bar overlay
        right_panel_widget = QWidget()
        right_panel_layout = QGridLayout(right_panel_widget)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(0)
        right_panel_layout.addWidget(self.stack, 0, 0)

        # Notification System
        self.notification_bar = NotificationBar(right_panel_widget)
        right_panel_layout.addWidget(self.notification_bar, 0, 0, alignment=Qt.AlignBottom)
        self.notification_manager.register_widgets(self, self.notification_bar)

        return right_panel_widget

    def initUI(self):
        """Initializes the main user interface."""
        # Clear old layout if it exists
        if self.centralWidget():
            old_widget = self.centralWidget()
            old_widget.setParent(None)
            old_widget.deleteLater()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background: transparent;")

        # Set window icon
        icon_path = get_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Main layout
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Create UI components
        self.sidebar_widget = self._create_sidebar()
        self.right_panel_widget = self._create_main_content()

        # Connect signals after UI creation
        self.menu_list.currentRowChanged.connect(self.handle_menu_selection)

        # Add widgets to the main layout
        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.right_panel_widget, 1)

        # Arrange layout based on language and update scrollbars
        self.arrange_layout()
        self.update_scrollbars_direction()
        
    def arrange_layout(self):
        """ترتيب التخطيط حسب اللغة"""
        if not hasattr(self, 'main_layout') or not hasattr(self, 'sidebar_widget'):
            return
        
        if not hasattr(self, 'stack'):
            return
            
        language = self.settings_data.get("language", "ar")
        
        # مسح العناصر من التخطيط
        self.main_layout.removeWidget(self.sidebar_widget)
        self.main_layout.removeWidget(self.right_panel_widget)
        
        # إضافة العناصر بالترتيب الصحيح (مع مراعاة RightToLeft)
        if language == "ar":
            # في RightToLeft: العنصر الأول يظهر يميناً، الثاني يساراً
            self.main_layout.addWidget(self.sidebar_widget)
            self.main_layout.addWidget(self.right_panel_widget, 1)
        else:
            # في LeftToRight: العنصر الأول يظهر يساراً، الثاني يميناً
            self.main_layout.addWidget(self.sidebar_widget)
            self.main_layout.addWidget(self.right_panel_widget, 1)
    
    def update_scrollbars_direction(self):
        """تحديث اتجاه شريط التمرير في جميع الصفحات"""
        language = self.settings_data.get("language", "ar")
        direction = Qt.RightToLeft if language == "ar" else Qt.LeftToRight
        
        # تحديث جميع QScrollArea في التطبيق
        for i in range(self.stack.count()):
            page = self.stack.widget(i)
            if isinstance(page, QScrollArea):
                page.setLayoutDirection(direction)

        # إعداد اختصارات لوحة المفاتيح (بدون تحميل الوحدات)
        self.setup_keyboard_shortcuts_lazy()

    def navigate_to_page(self, page_identifier):
        """التنقل إلى صفحة معينة من صفحة الترحيب"""
        # إذا كان المعرف رقم، استخدمه مباشرة
        if isinstance(page_identifier, int):
            index = page_identifier
        else:
            # إذا كان نص، حوله إلى رقم
            page_mapping = {
                "merge": 1,
                "split": 2,
                "compress": 3,
                "rotate": 4,
                "convert": 5,
                "security": 6,
                "settings": 7
            }
            index = page_mapping.get(page_identifier, 0)

        if index > 0:
            self.menu_list.setCurrentRow(index)
            self.load_page_on_demand(index)

    def handle_menu_selection(self, desired_row):
        """
        Handles menu selection with a confirmation dialog for unsaved changes,
        preventing visual glitches by managing selection flow correctly.
        """
        current_index = self.stack.currentIndex()
        if current_index == desired_row:
            return

        page_container = self.stack.widget(current_index)
        page = page_container.widget() if hasattr(page_container, 'widget') else page_container
        has_changes = hasattr(page, 'has_unsaved_changes') and page.has_unsaved_changes
        has_files = hasattr(page, 'file_list_frame') and page.file_list_frame is not None and page.file_list_frame.get_valid_files()

        if not (has_changes or has_files):
            self.load_page_on_demand(desired_row)
            return

        # --- Changes exist, must confirm ---

        # 1. Reset selection visually to prevent jumpiness
        self.menu_list.blockSignals(True)
        self.menu_list.setCurrentRow(current_index)
        self.menu_list.blockSignals(False)

        # 2. Ask for confirmation
        can_navigate = False
        # Special case for settings page (index 7)
        if current_index == 7:
            result, dont_ask_again = self._show_custom_unsaved_changes_dialog()
            if dont_ask_again:
                set_setting("dont_ask_again_and_discard", True)
                if hasattr(page, 'load_original_settings'): page.load_original_settings()
                page.has_unsaved_changes = False
                can_navigate = True
            elif result == "save":
                if hasattr(page, 'save_all_settings'): page.save_all_settings()
                can_navigate = True
            elif result == "discard":
                if hasattr(page, 'load_original_settings'): page.load_original_settings()
                page.has_unsaved_changes = False
                can_navigate = True
        # Standard confirmation for all other pages
        else:
            from PySide6.QtWidgets import QMessageBox
            from ui.theme_manager import apply_theme
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(tr("warning"))
            msg_box.setText(tr("unsaved_work_warning"))
            msg_box.setStandardButtons(QMessageBox.Discard | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Cancel)
            msg_box.button(QMessageBox.Discard).setText(tr("discard_changes"))
            msg_box.button(QMessageBox.Cancel).setText(tr("cancel_button"))
            apply_theme(msg_box, "dialog")
            reply = msg_box.exec()
            if reply == QMessageBox.Discard:
                if hasattr(page, 'reset_ui'): page.reset_ui()
                page.has_unsaved_changes = False
                can_navigate = True

        # 3. Navigate if confirmed by the user
        if can_navigate:
            # This will trigger load_page_on_demand
            self.menu_list.setCurrentRow(desired_row)
        # If not confirmed, do nothing. The selection is already correct.

    def _show_custom_unsaved_changes_dialog(self):
        """Shows a theme-aware custom dialog for unsaved changes."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QSpacerItem, QSizePolicy
        from modules.translator import tr
        from ui import apply_theme_style

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("warning"))
        dialog.setModal(True)
        apply_theme_style(dialog, "dialog")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        message_label = QLabel(tr("unsaved_changes_prompt"))
        message_label.setWordWrap(True)
        apply_theme_style(message_label, "label")
        layout.addWidget(message_label)

        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons
        buttons_layout = QHBoxLayout()
        discard_button = QPushButton(tr("discard_changes"))
        save_button = QPushButton(tr("save_and_close"))
        back_button = QPushButton(tr("go_back"))
        
        apply_theme_style(discard_button, "button")
        apply_theme_style(save_button, "button")
        apply_theme_style(back_button, "button")

        buttons_layout.addWidget(discard_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(back_button)
        layout.addLayout(buttons_layout)
        
        # Checkbox
        dont_ask_checkbox = QCheckBox(tr("dont_ask_again_and_discard_option"))
        apply_theme_style(dont_ask_checkbox, "checkbox")
        layout.addWidget(dont_ask_checkbox)

        # Result variables
        result = "back"  # Default to "back" if dialog is closed
        
        def on_save():
            nonlocal result
            result = "save"
            dialog.accept()

        def on_discard():
            nonlocal result
            result = "discard"
            dialog.accept()

        def on_back():
            nonlocal result
            result = "back"
            dialog.reject()

        save_button.clicked.connect(on_save)
        discard_button.clicked.connect(on_discard)
        back_button.clicked.connect(on_back)

        dialog.exec()

        return result, dont_ask_checkbox.isChecked()

    def on_menu_selection_changed(self, current_row):
        """دالة قديمة للحفاظ على التوافق مع الإشارات القديمة"""
        # دالة محجوبة الآن، يتم استخدام handle_menu_selection بدلاً منها
        # تم تعطيل هذا الاستدعاء لتجنب الاستدعاء المزدوج
        pass



    def load_page_on_demand(self, index):
        """تحميل الصفحات عند الطلب باستخدام المدراء"""
        if index < 0 or index >= len(self.pages_loaded):
            return
            
        # عند بدء التطبيق (الفهرس 0)، لا تقم بتحميل الصفحة أو إعادة تعيين الصفحات
        # هذا يمنع تحميل الصفحات غير الضرورية عند الفتح
        if index == 0:
            # الصفحة 0 (صفحة الترحيب) محملة بالفعل، فقط انتقل إليها
            self.stack.setCurrentIndex(0)
            return
            
        # إعادة تعيين جميع الصفحات المحملة عند التنقل
        self._reset_all_loaded_pages()

        # إذا كانت الصفحة محملة بالفعل، انتقل إليها مباشرة
        if self.pages_loaded[index]:
            self.stack.setCurrentIndex(index)
            return

        # تحميل الصفحة باستخدام WorkerManager للصفحات الثقيلة
        try:
            page = self._create_page(index)

            if page:
                self._replace_page_safely(index, page)
                self.pages_loaded[index] = True
                # تطبيق السمة باستخدام ThemeManager
                self.theme_manager.apply_theme(page, "dialog")

        except Exception as e:
            self._handle_page_load_error(index, e)

        # الانتقال إلى الصفحة
        self.stack.setCurrentIndex(index)

    def _reset_all_loaded_pages(self):
        """Resets all loaded pages, checking for unsaved changes first."""
        try:
            current_index = self.stack.currentIndex()
            if current_index > 0 and self.pages_loaded[current_index]:
                widget = self.stack.widget(current_index)
                inner_widget = widget.widget() if hasattr(widget, 'widget') else widget

                if hasattr(inner_widget, 'has_unsaved_changes') and inner_widget.has_unsaved_changes:
                    from modules import settings
                    from PySide6.QtWidgets import QDialog

                    settings_data = settings.load_settings()
                    if settings_data.get("dont_ask_again_and_discard", False):
                        pass  # Continue to reset
                    else:
                        result = self.message_manager.ask_for_save_confirmation(inner_widget)
                        if result == QDialog.Rejected:
                            return  # User cancelled, do not reset pages

            # Proceed to reset all other pages
            for i in range(1, self.stack.count()):
                if self.pages_loaded[i]:
                    widget = self.stack.widget(i)
                    inner_widget = widget.widget() if hasattr(widget, 'widget') else widget
                    if hasattr(inner_widget, 'reset_ui'):
                        inner_widget.reset_ui()
        except Exception as e:
            debug(f"Error resetting pages: {e}")

    def _create_page(self, index):
        """إنشاء الصفحة المطلوبة"""
        page_creators = {
            1: lambda: self._create_merge_page(),
            2: lambda: self._create_split_page(),
            3: lambda: self._create_compress_page(),
            4: lambda: self._create_rotate_page(),
            5: lambda: self._create_convert_page(),
            6: lambda: self._create_security_page(),
            7: lambda: self._create_settings_page()
        }

        creator = page_creators.get(index)
        return creator() if creator else None

    def _create_merge_page(self):
        from ui.merge_page import MergePage
        # استخدام التحميل الكسول لـ OperationsManager
        operations_manager = self.get_operations_manager()
        return MergePage(self.file_manager, operations_manager, self.notification_manager)

    def _create_split_page(self):
        from ui.split_page import SplitPage
        return SplitPage(self.file_manager, self.get_operations_manager(), self.notification_manager)

    def _create_compress_page(self):
        from ui.compress_page import CompressPage
        return CompressPage(self.file_manager, self.get_operations_manager(), self.notification_manager)

    def _create_rotate_page(self):
        from ui.rotate_page import RotatePage
        return RotatePage(self.notification_manager, file_path=None, parent=self)

    def _create_convert_page(self):
        from ui.convert_page import ConvertPage
        return ConvertPage(self.file_manager, self.get_operations_manager(), self.notification_manager, parent=self)

    def _create_security_page(self):
        from ui.security_page import SecurityPage
        return SecurityPage(self.file_manager, self.get_operations_manager(), self.notification_manager)

    def _create_settings_page(self):
        SettingsUI = self.settings_ui
        if SettingsUI:
            settings_widget = SettingsUI(self)
            settings_widget.settings_changed.connect(self.on_settings_changed)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(settings_widget)
            apply_theme_style(scroll_area, "scroll")
            return scroll_area
        else:
            return self._create_error_widget(tr("error_loading_settings_page"))

    def _create_error_widget(self, message):
        """إنشاء ويدجت خطأ بسيط"""
        error_widget = QWidget()
        layout = QVBoxLayout(error_widget)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(label)
        return error_widget

    def _handle_page_load_error(self, index, error):
        """معالجة أخطاء تحميل الصفحات باستخدام NotificationManager"""
        page_names = [
            "", tr("menu_merge_print"), tr("menu_split"), tr("menu_compress"),
            tr("menu_stamp_rotate"), tr("menu_convert"), tr("menu_security"),
            tr("menu_settings")
        ]
        page_name = page_names[index] if index < len(page_names) else f"Page {index}"

        # عرض إشعار خطأ
        self.notification_manager.show_notification(
            tr("error_loading_page", page_name=page_name, error=str(error)), "error"
        )

        # تسجيل الخطأ
        error(f"Error loading page {page_name} (index {index}): {error}")

        # إنشاء صفحة خطأ
        self._create_error_page(index, f"خطأ في تحميل {page_name}", str(error))

    def _create_error_page(self, index, title, message):
        """إنشاء صفحة خطأ باستخدام المدراء"""
        error_page = QWidget()
        error_layout = QVBoxLayout(error_page)
        error_layout.setAlignment(Qt.AlignCenter)
        error_layout.setSpacing(20)

        # عنوان الخطأ
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ff6b6b; font-size: 18px; font-weight: bold;")

        # رسالة الخطأ
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        message_label.setWordWrap(True)

        # زر إعادة المحاولة
        from ui.svg_icon_button import create_action_button
        retry_button = create_action_button("reset", 24, tr("retry_button"))
        retry_button.clicked.connect(lambda: self._retry_load_page(index))

        error_layout.addWidget(title_label)
        error_layout.addWidget(message_label)
        error_layout.addWidget(retry_button)

        # تطبيق السمة باستخدام ThemeManager
        self.theme_manager.apply_theme(error_page, "dialog")

        self.stack.removeWidget(self.stack.widget(index))
        self.stack.insertWidget(index, error_page)

    def _retry_load_page(self, index):
        """إعادة محاولة تحميل الصفحة مع إشعار"""
        self.pages_loaded[index] = False
        self.notification_manager.show_notification(tr("reloading_page"), "info")
        self.load_page_on_demand(index)

    def refresh_all_loaded_pages(self):
        """إعادة تطبيق السمة على جميع الصفحات باستخدام ThemeManager"""
        try:
            # تطبيق السمة على القائمة الجانبية
            self.theme_manager.apply_theme(self.menu_list, "menu")

            # تطبيق السمة على جميع الصفحات المحملة
            for i in range(1, self.stack.count()):
                if self.pages_loaded[i]:
                    widget = self.stack.widget(i)
                    self.theme_manager.apply_theme(widget, "dialog")

            info("تم إعادة تطبيق السمة على جميع الصفحات المحملة")
        except Exception as e:
            error(f"خطأ في إعادة تطبيق السمة على الصفحات: {e}")

    def _validate_settings(self, settings_data):
        """التحقق من صحة بيانات الإعدادات"""
        if not isinstance(settings_data, dict):
            error("الإعدادات ليست من نوع dictionary")
            return False

        # المفاتيح المطلوبة مع القيم الافتراضية
        required_keys = {
            "theme": str,
            "accent_color": str,
            "ui_settings": dict,
            "keyboard_shortcuts": dict
        }

        # فحص وجود المفاتيح المطلوبة ونوع البيانات
        for key, expected_type in required_keys.items():
            if key not in settings_data:
                warning(f"مفتاح مفقود في الإعدادات: {key}")
                return False

            if not isinstance(settings_data[key], expected_type):
                warning(f"نوع بيانات خاطئ للمفتاح {key}: متوقع {expected_type.__name__}")
                return False

        # فحص إعدادات الواجهة
        ui_settings = settings_data.get("ui_settings", {})
        if "font_size" in ui_settings:
            font_size = ui_settings["font_size"]
            if not isinstance(font_size, (int, float)) or font_size < 8 or font_size > 24:
                warning(f"حجم خط غير صالح: {font_size}")
                return False

        # فحص لون التمييز
        accent_color = settings_data.get("accent_color", "")
        if not accent_color.startswith("#") or len(accent_color) != 7:
            warning(f"لون تمييز غير صالح: {accent_color}")
            return False

        debug("تم التحقق من صحة الإعدادات بنجاح")
        return True

    def _get_default_settings(self):
        """الحصول على الإعدادات الافتراضية"""
        return {
            "theme": "blue",
            "accent_color": "#056a51",
            "ui_settings": {
                "font_size": 12,
                "language": "ar"
            },
            "keyboard_shortcuts": {
                "open_settings": "Ctrl+,"
            }
        }

    def _replace_page_safely(self, index, new_page):
        """استبدال صفحة في المكدس بطريقة آمنة للذاكرة"""
        try:
            # التحقق من صحة الفهرس
            if index < 0 or index >= self.stack.count():
                error(f"فهرس غير صالح: {index}")
                return

            # الحصول على الويدجت الحالي
            old_widget = self.stack.widget(index)

            # التحقق من وجود الويدجت القديم
            if old_widget is None:
                # إذا لم يكن هناك ويدجت، أضف الجديد مباشرة
                self.stack.insertWidget(index, new_page)
                debug(f"تم إدراج صفحة جديدة في الفهرس {index}")
                return

            # استبدال الويدجت بطريقة مباشرة وآمنة
            self.stack.removeWidget(old_widget)
            self.stack.insertWidget(index, new_page)

            # تنظيف الويدجت القديم
            old_widget.setParent(None)
            old_widget.deleteLater()

            debug(f"تم استبدال الصفحة {index} بنجاح")

        except Exception as e:
            error(f"خطأ في استبدال الصفحة {index}: {e}")
            # في حالة الفشل، استخدم الطريقة البسيطة
            try:
                old_widget = self.stack.widget(index)
                if old_widget:
                    self.stack.removeWidget(old_widget)
                self.stack.insertWidget(index, new_page)
            except Exception as fallback_error:
                error(f"خطأ في الطريقة البديلة: {fallback_error}")
                # كحل أخير، أضف الصفحة في النهاية
                self.stack.addWidget(new_page)

    def setup_keyboard_shortcuts_lazy(self):
        """إعداد اختصارات لوحة المفاتيح بدون تحميل الوحدات"""
        shortcuts = self.settings_data.get("keyboard_shortcuts", {})

        # اختصار الإعدادات (لا يحتاج وحدات)
        if shortcuts.get("open_settings"):
            settings_shortcut = QShortcut(QKeySequence(shortcuts["open_settings"]), self)
            settings_shortcut.activated.connect(lambda: self.menu_list.setCurrentRow(7))

        # باقي الاختصارات ستُحمل عند تحميل الوحدات

    def on_settings_changed(self):
        """التعامل مع تغيير الإعدادات باستخدام المدراء"""
        # إعادة تحميل الإعدادات
        self.settings_data = load_settings()

        # إعادة تحميل وحدة الترجمة لتطبيق اللغة الجديدة فوراً
        import importlib
        from modules import translator
        importlib.reload(translator)

        # تطبيق اتجاه الواجهة الجديد
        language = self.settings_data.get("language", "ar")
        if language == "ar":
            QApplication.instance().setLayoutDirection(Qt.RightToLeft)
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            QApplication.instance().setLayoutDirection(Qt.LeftToRight)
            self.setLayoutDirection(Qt.LeftToRight)

        # إعادة بناء الواجهة الرئيسية
        self.initUI()
        self.arrange_layout()
        self.update_scrollbars_direction()

        # تطبيق الإعدادات الجديدة باستخدام المدراء
        self._apply_ui_settings()

        # إعادة تطبيق السمة على جميع العناصر المحملة
        self.refresh_all_loaded_pages()

        # عرض إشعار نجاح
        self.notification_manager.show_notification(
            tr("settings_applied_successfully"), "success"
        )

    def _apply_ui_settings(self):
        """تطبيق إعدادات الواجهة باستخدام ThemeManager"""
        ui_settings = self.settings_data.get("ui_settings", {})
        font_size = ui_settings.get("font_size", 12)

        # تحديد حجم العناصر بناءً على حجم الخط الأساسي
        if font_size <= 10:
            size_option = "صغير جداً (مدمج)"
        elif font_size <= 12:
            size_option = "صغير (افتراضي)"
        elif font_size <= 14:
            size_option = "متوسط (مريح)"
        elif font_size <= 16:
            size_option = "كبير (واضح)"
        else:
            size_option = "كبير جداً (إمكانية وصول)"

        # تطبيق السمة مع الخيارات المحدثة
        theme = self.settings_data.get("theme", "blue")
        accent_color = self.settings_data.get("accent_color", "#056a51")

        options = {
            "transparency": 80,
            "size": size_option,
            "contrast": "عادي (متوازن)"
        }

        try:
            # تحديث السمة باستخدام ThemeManager
            self.theme_manager.change_theme(theme, accent_color, options)

            # تطبيق النمط على النافذة الرئيسية
            self.theme_manager.apply_theme(self, "main_window")

            # إعادة تطبيق السمة على جميع العناصر
            self.refresh_all_loaded_pages()

            info(f"تم تطبيق إعدادات الواجهة بنجاح: {theme}, {accent_color}, {size_option}")

        except Exception as e:
            error(f"خطأ في تطبيق إعدادات الواجهة: {e}")
            # عرض إشعار خطأ
            self.notification_manager.show_notification(
                tr("error_applying_settings", error=str(e)), "error"
            )

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    app = SingleApplication(sys.argv)

    # إعداد أول تشغيل للتطبيق
    try:
        from modules.default_settings import setup_first_run
        setup_first_run()
    except Exception as e:
        print(f"تحذير: خطأ في إعداد أول تشغيل: {e}")

    # التحقق من التشغيل الأول وعرض واجهة الإعداد
    settings_data = load_settings()
    if not settings_data:
        # Create and show first run dialog
        first_run_dialog = FirstRunDialog()
        # The dialog is modal and should handle saving the settings itself.
        if not first_run_dialog.exec():
            sys.exit(0)  # Exit if the user closes the dialog
        # Reload settings after the first run dialog has presumably saved them.
        settings_data = load_settings()

    # --- تطبيق اتجاه الواجهة قبل إنشاء أي نافذة ---
    language = settings_data.get("language", "ar")
    
    if language == "ar":
        app.setLayoutDirection(Qt.RightToLeft)
    else:
        app.setLayoutDirection(Qt.LeftToRight)
    # -----------------------------------------

    # فحص إذا كان التطبيق يعمل بالفعل
    if app.is_running():
        QMessageBox.warning(None, tr("warning"), tr("app_already_running_warning"))
        sys.exit(1)

    # إنشاء النافذة الرئيسية
    window = ApexFlow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
