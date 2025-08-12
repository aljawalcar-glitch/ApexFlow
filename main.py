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
    QWidget, QListWidget, QListWidgetItem, QLabel, QScrollArea, QPushButton,
    QGridLayout
)
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QSharedMemory, QSystemSemaphore, QTimer

# Local module imports
from modules.settings import load_settings, set_setting  # Direct import to avoid loading PDF modules
from modules.app_utils import get_icon_path
from modules.logger import info, warning, error
from ui import WelcomePage, apply_theme_style
from ui.notification_system import NotificationBar
from ui.first_run_dialog import FirstRunDialog
from ui.smart_drop_overlay import SmartDropOverlay
from ui.overlay_manager import OverlayManager
from modules.page_settings import page_settings
from modules.translator import tr
from ui.animated_stacked_widget import AnimatedStackedWidget

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
        self.is_page_transitioning = False
        
        # Track unfinished work in pages
        self._has_unfinished_work = {}  # Dictionary to track unfinished work per page
        
        # Initialize all pages as having no unfinished work
        for i in range(8):  # We have 8 pages (0-7)
            self._has_unfinished_work[i] = False

        # Load basic settings only (speed up startup)
        self.settings_data = load_settings()

        # Create all required managers
        self._setup_managers()

        # Apply unified window properties
        self.window_manager.set_window_properties(self, tr("main_window_title"))
        self.setGeometry(200, 100, 1000, 600)
        self.setAcceptDrops(True)

        # Create interface first
        self.initUI()
        
        # Create overlay manager after UI is created
        if not hasattr(self, 'overlay_manager'):
            self.overlay_manager = OverlayManager(self)

        # Apply theme and settings in a deferred manner
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._initialize_delayed)

    def closeEvent(self, event):
        """Handle the window close event for resource cleanup."""
        # Check for unfinished work before closing
        if self.has_any_unfinished_work():
            pages_with_work = self.get_pages_with_work()
            
            # Format the message with the names of pages that have unsaved work
            message = tr("exit_with_work_warning", pages=", ".join(pages_with_work))
            
            # Create a confirmation dialog
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle(tr("confirm_exit"))
            confirm_dialog.setText(message)
            confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm_dialog.setDefaultButton(QMessageBox.No)
            
            # Apply theme to the dialog
            try:
                from ui.theme_manager import apply_theme
                apply_theme(confirm_dialog, "dialog")
            except Exception as e:
                error(f"Error applying theme to dialog: {e}")

            # If the user chooses not to exit, ignore the close event
            if confirm_dialog.exec() == QMessageBox.No:
                event.ignore()
                return

        # Stop all worker threads before closing
        if hasattr(self, 'worker_manager') and self.worker_manager:
            self.worker_manager.cleanup()

        # Accept the close event and close the application
        event.accept()

    def resizeEvent(self, event):
        """تحديث حجم الطبقة الذكية عند تغيير حجم النافذة"""
        super().resizeEvent(event)
        if hasattr(self, 'smart_drop_overlay') and self.smart_drop_overlay:
            self.smart_drop_overlay.resize(self.size())

    def dragEnterEvent(self, event):
        """Handle drag enter events for the main window."""
        current_index = self.stack.currentIndex()
        if current_index in [0, 7, 8]:  # Welcome, Settings, Help
            event.ignore()
            return

        if self.smart_drop_overlay and event.mimeData().hasUrls():
            self._update_smart_drop_mode_for_page(current_index)
            self.smart_drop_overlay.handle_drag_enter(event)
            if event.isAccepted():
                if hasattr(self, 'overlay_manager'):
                    self.overlay_manager.active_overlay = self.smart_drop_overlay
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave events for the main window."""
        # حدث مغادرة السحب في النافذة الرئيسية
        # تمرير الحدث إلى الطبقة الذكية لمعالجته
        if self.smart_drop_overlay and self.smart_drop_overlay.isVisible():
            self.smart_drop_overlay.handle_drag_leave(event)
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events for the main window."""
        # حدث الإفلات في النافذة الرئيسية
        overlay_visible = self.smart_drop_overlay and self.smart_drop_overlay.isVisible()
        # واجهة الإسقاط مرئية
        if overlay_visible:
            self.smart_drop_overlay.handle_drop(event)
            # قبول الحدث
            # قبول حدث الإفلات في النافذة الرئيسية
            event.accept()
        else:
            event.ignore()

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
        
        # The SmartDropOverlay will be created in _create_main_content
        self.smart_drop_overlay = None

        # Setup page manager (use existing variables)
        self.pages_loaded = [True, False, False, False, False, False, False, False]

    def get_operations_manager(self):
        """Create or return OperationsManager (lazy loading)"""
        if self.operations_manager is None and not self._operations_manager_creation_attempted:
            self._operations_manager_creation_attempted = True
            try:
                from modules.app_utils import OperationsManager
                self.operations_manager = OperationsManager(self, self.file_manager, self.message_manager)
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

    def set_page_has_work(self, page_index, has_work):
        """تعيين حالة العمل لصفحة معينة"""
        if 0 <= page_index < len(self._has_unfinished_work):
            self._has_unfinished_work[page_index] = has_work
    
    def get_page_has_work(self, page_index):
        """الحصول على حالة العمل لصفحة معينة"""
        return self._has_unfinished_work.get(page_index, False)
    
    def has_any_unfinished_work(self):
        """التحقق من وجود أي عمل غير منجز في أي صفحة"""
        return any(self._has_unfinished_work.values())
    
    def get_pages_with_work(self):
        """الحصول على قائمة بأسماء الصفحات التي تحتوي على عمل غير منجز"""
        page_names = [
            tr("menu_home"), tr("menu_merge_print"), tr("menu_split"),
            tr("menu_compress"), tr("menu_stamp_rotate"), tr("menu_convert"),
            tr("menu_security"), tr("menu_settings")
        ]
        
        pages_with_work = []
        for page_index, has_work in self._has_unfinished_work.items():
            if has_work:
                page_name = page_names[page_index] if page_index < len(page_names) else f"Page {page_index}"
                pages_with_work.append(page_name)
        return pages_with_work

    def get_page_index(self, page):
        """Gets the index of a page widget in the stack."""
        return self.stack.indexOf(page)

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
        # Restore original menu items including Help
        menu_items = [
            tr("menu_home"), tr("menu_merge_print"), tr("menu_split"),
            tr("menu_compress"), tr("menu_stamp_rotate"), tr("menu_convert"),
            tr("menu_security"), tr("menu_settings"), tr("menu_help")
        ]
        
        for item_text in menu_items:
            self.menu_list.addItem(item_text)
        
        self.menu_list.setFocusPolicy(Qt.NoFocus)
        self.menu_list.setSelectionMode(QListWidget.SingleSelection)
        self.menu_list.setCurrentRow(0)
        apply_theme_style(self.menu_list, "menu")
        sidebar_layout.addWidget(self.menu_list)

        # App info widget
        from ui.app_info_widget import AppInfoWidget
        self.app_info = AppInfoWidget(self.settings_data)
        sidebar_layout.addWidget(self.app_info)

        return sidebar_widget

    def _create_main_content(self):
        """Creates the main content area with the stacked widget and notification bar."""
        # Create the stacked widget for pages
        self.stack = AnimatedStackedWidget()
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
            tr("menu_settings"), tr("menu_help")
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

        # Create smart drop overlay as a child of the stack
        self.smart_drop_overlay = SmartDropOverlay(self, self.stack)
        self.smart_drop_overlay.action_selected.connect(self.handle_smart_drop_action)
        self.smart_drop_overlay.cancelled.connect(self.handle_smart_drop_cancel)
        
        # تعيين الوضع الافتراضي للطبقة الذكية
        self.smart_drop_overlay.reset_mode()

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

        # Connect menu selection directly
        self.menu_list.itemClicked.connect(self.handle_menu_selection)
        self.stack.animationFinished.connect(self.on_page_transition_finished)

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
        
        # إضافة العناصر بالترتيب الصحيح
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
                "settings": 7,
                "help": 8
            }
            index = page_mapping.get(page_identifier, 0)

        if index > 0:
            # إغلاق التراكب النشط قبل تغيير الصفحة
            if hasattr(self, 'smart_drop_overlay') and self.smart_drop_overlay and self.smart_drop_overlay.isVisible():
                self.smart_drop_overlay.close()
                
            self.menu_list.setCurrentRow(index)
            self.load_page_on_demand(index)
        else:
            self.stack.fade_to_index(index)

    def handle_menu_selection(self, item):
        """
        Handles menu selection simply and directly.
        """
        # Get the row immediately after click
        desired_row = self.menu_list.row(item)
        current_index = self.stack.currentIndex()
        
        if self.is_page_transitioning:
            return
        
        # Return if same page is selected
        if current_index == desired_row:
            return
            
        # Get page names for confirmation message
        page_names = [
            tr("menu_home"), tr("menu_merge_print"), tr("menu_split"),
            tr("menu_compress"), tr("menu_stamp_rotate"), tr("menu_convert"),
            tr("menu_security"), tr("menu_settings"), tr("menu_help")
        ]
        
        current_page_name = page_names[current_index] if current_index < len(page_names) else f"Page {current_index}"
        target_page_name = page_names[desired_row] if desired_row < len(page_names) else f"Page {desired_row}"

        # If current page has unfinished work, show confirmation dialog
        if self.get_page_has_work(current_index):
            message = tr("navigation_with_work_warning", 
                        current_page=current_page_name, 
                        target_page=target_page_name)
            
            from PySide6.QtWidgets import QMessageBox
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle(tr("confirm_navigation"))
            confirm_dialog.setText(message)
            confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm_dialog.setDefaultButton(QMessageBox.Yes)
            
            try:
                from ui.theme_manager import apply_theme
                apply_theme(confirm_dialog, "dialog")
            except Exception as e:
                pass
                
            if confirm_dialog.exec() == QMessageBox.Yes:
                # Reset the current page's UI before navigating away
                current_page_widget = self.stack.widget(current_index)

                # If the current page is settings page (index 7), call cancel_changes
                if current_index == 7:  # Settings page
                    try:
                        # Get the actual settings widget (inside scroll area)
                        if hasattr(current_page_widget, 'widget'):
                            settings_widget = current_page_widget.widget()
                        else:
                            settings_widget = current_page_widget

                        # Check if it has cancel_changes method
                        if hasattr(settings_widget, 'cancel_changes'):
                            settings_widget.cancel_changes()
                        else:
                            # Fallback to reset_ui if cancel_changes doesn't exist
                            if hasattr(settings_widget, 'reset_ui'):
                                settings_widget.reset_ui()
                    except Exception as e:
                        error(f"Error calling cancel_changes: {e}")
                        # Fallback to original behavior
                        if hasattr(current_page_widget, 'reset_ui'):
                            current_page_widget.reset_ui()
                        elif hasattr(current_page_widget, 'widget') and hasattr(current_page_widget.widget(), 'reset_ui'):
                            current_page_widget.widget().reset_ui()
                else:
                    # For other pages, use the original behavior
                    if hasattr(current_page_widget, 'reset_ui'):
                        current_page_widget.reset_ui()
                    elif hasattr(current_page_widget, 'widget') and hasattr(current_page_widget.widget(), 'reset_ui'): # For QScrollArea
                        current_page_widget.widget().reset_ui()
            else:
                # Reset selection to current page
                self.menu_list.blockSignals(True)
                self.menu_list.setCurrentRow(current_index)
                self.menu_list.blockSignals(False)
                return

        # Proceed with navigation
        # إغلاق التراكب النشط قبل تغيير الصفحة
        if hasattr(self, 'smart_drop_overlay') and self.smart_drop_overlay and self.smart_drop_overlay.isVisible():
            self.smart_drop_overlay.close()
            
        self.load_page_on_demand(desired_row)
        self.menu_list.setCurrentRow(desired_row)
        # تحديث وضع الطبقة الذكية بناءً على الصفحة الجديدة
        self._update_smart_drop_mode_for_page(desired_row)
            

    def load_page_on_demand(self, index):
        """تحميل الصفحات عند الطلب باستخدام المدراء"""
        if index < 0 or index >= len(self.pages_loaded):
            return
            
        # عند بدء التطبيق (الفهرس 0)، لا تقم بتحميل الصفحة أو إعادة تعيين الصفحات
        # هذا يمنع تحميل الصفحات غير الضرورية عند الفتح
        if index == 0:
            # الصفحة 0 (صفحة الترحيب) محملة بالفعل، فقط انتقل إليها
            self.stack.fade_to_index(0)
            return

        # إذا كانت الصفحة محملة بالفعل، انتقل إليها مباشرة
        if self.pages_loaded[index]:
            self.is_page_transitioning = True
            self.stack.fade_to_index(index)
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
            error(f"Error creating page {index}: {e}")
            self._handle_page_load_error(index, e)

        # الانتقال إلى الصفحة
        self.is_page_transitioning = True
        self.stack.fade_to_index(index)

    def on_page_transition_finished(self):
        """Slot to be called when the page transition animation is finished."""
        self.is_page_transitioning = False

    def _reset_all_loaded_pages(self):
        """Resets all loaded pages."""
        try:
            # Proceed to reset all other pages
            for i in range(1, self.stack.count()):
                if self.pages_loaded[i]:
                    widget = self.stack.widget(i)
                    inner_widget = widget.widget() if hasattr(widget, 'widget') else widget
                    if hasattr(inner_widget, 'reset_ui'):
                        inner_widget.reset_ui()
        except Exception as e:
            error(f"Error resetting loaded pages: {e}")

    def _create_page(self, index):
        """إنشاء الصفحة المطلوبة"""
        page_creators = {
            1: lambda: self._create_merge_page(),
            2: lambda: self._create_split_page(),
            3: lambda: self._create_compress_page(),
            4: lambda: self._create_rotate_page(),
            5: lambda: self._create_convert_page(),
            6: lambda: self._create_security_page(),
            7: lambda: self._create_settings_page(),
            8: lambda: self._create_help_page()
        }

        creator = page_creators.get(index)
        return creator() if creator else None
        
    def _update_smart_drop_mode_for_page(self, page_index):
        """تحديث وضع الطبقة الذكية بناءً على الصفحة الحالية"""
        # تحديث وضع الطبقة الذكية للصفحة
        page_titles = [
            tr("menu_home"), tr("menu_merge_print"), tr("menu_split"),
            tr("menu_compress"), tr("menu_stamp_rotate"), tr("menu_convert"),
            tr("menu_security"), tr("menu_settings"), tr("menu_help")
        ]
        page_contexts = [
            'welcome', 'merge', 'split', 'compress', 'rotate', 'convert', 'security', 'settings', 'help'
        ]
        
        context = page_contexts[page_index] if 0 <= page_index < len(page_contexts) else 'welcome'
        title = page_titles[page_index] if 0 <= page_index < len(page_titles) else tr("menu_home")

        if self.smart_drop_overlay:
            self.smart_drop_overlay.update_context(context, title)
            
            # تحديث إعدادات الصفحة في واجهة الإسقاط
            page_key_map = {
                'welcome': None,
                'merge': 'merge_print',
                'split': 'split',
                'compress': 'compress',
                'rotate': 'stamp_rotate',
                'convert': 'convert',
                'security': 'protect_properties',
                'settings': None,
                'help': None
            }
            
            page_key = page_key_map.get(context)
            if page_key and page_key in page_settings:
                self.smart_drop_overlay.update_page_settings(page_settings[page_key])

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

    def _create_help_page(self):
        from ui.help_page import HelpPage
        return HelpPage(self)

    def _create_error_widget(self, message):
        """إنشاء ويدجت خطأ بسيط"""
        error_widget = QWidget()
        layout = QVBoxLayout(error_widget)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(label)
        return error_widget

    def _handle_page_load_error(self, index, error_obj):
        """معالجة أخطاء تحميل الصفحات باستخدام NotificationManager"""
        page_names = [
            "", tr("menu_merge_print"), tr("menu_split"), tr("menu_compress"),
            tr("menu_stamp_rotate"), tr("menu_convert"), tr("menu_security"),
            tr("menu_settings"), tr("menu_help")
        ]
        page_name = page_names[index] if index < len(page_names) else f"Page {index}"

        # عرض إشعار خطأ
        self.notification_manager.show_notification(
            tr("error_loading_page", page_name=page_name, error=str(error_obj)), "error"
        )

        # تسجيل الخطأ
        error(f"Error loading page {page_name} (index {index}): {error_obj}")

        # إنشاء صفحة خطأ
        self._create_error_page(index, f"خطأ في تحميل {page_name}", str(error_obj))

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
            # عرض إشعار خطأ للمستخدم
            self.notification_manager.show_notification(
                tr("error_refreshing_theme"), "error"
            )

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

        return True
        
    def handle_smart_drop_action(self, action_type, files):
        """معالجة الإجراء المحدد من الطبقة الذكية"""
        self.setEnabled(True)
        self.activateWindow()
        self.raise_()

        page_mapping = {
            "merge": 1, "split": 2, "compress": 3,
            "rotate": 4, "convert": 5, "security": 6
        }
        target_page_index = page_mapping.get(action_type)

        if action_type == "add_to_list":
            self.add_files_to_current_page(files)
        elif target_page_index is not None:
            self.navigate_to_page(target_page_index)
            QTimer.singleShot(150, lambda: self.add_files_to_current_page(files))
        else:
            current_page = self.stack.currentWidget()
            if hasattr(current_page, 'widget'):
                current_page = current_page.widget()
            
            if hasattr(current_page, 'handle_smart_drop_action'):
                current_page.handle_smart_drop_action(action_type, files)
            
    def handle_smart_drop_cancel(self):
        """معالجة إلغاء السحب والإفلات"""
        self.setEnabled(True)
        self.activateWindow()
        self.raise_()

    def update_work_status_after_file_removal(self):
        """تحديث حالة العمل بعد إزالة الملفات"""
        current_page_index = self.stack.currentIndex()

        # التحقق من وجود عمل غير مكتمل في الصفحة الحالية
        if current_page_index > 0 and self.pages_loaded[current_page_index]:
            # الحصول على الصفحة الحالية
            current_page = self.stack.widget(current_page_index)

            # إذا كانت الصفحة داخل QScrollArea، احصل على الودجت الداخلي
            if hasattr(current_page, 'widget'):
                current_page = current_page.widget()

            # التحقق من وجود دالة للتحقق من وجود ملفات في الصفحة
            has_files = False
            if hasattr(current_page, 'has_files'):
                has_files = current_page.has_files()
            elif hasattr(current_page, 'file_list_frame') and hasattr(current_page.file_list_frame, 'has_files'):
                has_files = current_page.file_list_frame.has_files()

            # تحديث حالة العمل غير المكتمل للصفحة الحالية
            self.set_page_has_work(current_page_index, has_files)
        
    def add_files_to_current_page(self, files):
        """إضافة الملفات إلى الصفحة الحالية"""
        current_page_index = self.stack.currentIndex()
        
        if current_page_index > 0 and self.pages_loaded[current_page_index]:
            # الحصول على الصفحة الحالية
            current_page = self.stack.widget(current_page_index)
            
            # إذا كانت الصفحة داخل QScrollArea، احصل على الودجت الداخلي
            if hasattr(current_page, 'widget'):
                current_page = current_page.widget()
            
            # التحقق من وجود دالة إضافة الملفات في الصفحة
            if hasattr(current_page, 'add_files'):
                current_page.add_files(files)
            elif hasattr(current_page, 'file_list_frame') and hasattr(current_page.file_list_frame, 'add_files'):
                current_page.file_list_frame.add_files(files)

            # تعيين حالة العمل غير المكتمل للصفحة الحالية
            self.set_page_has_work(current_page_index, True)
                
    def execute_action_now(self, action, files):
        """تنفيذ الإجراء فورًا على الملفات"""
        current_page_index = self.stack.currentIndex()
        
        # الانتقال إلى الصفحة المناسبة إذا لم نكن فيها بالفعل
        page_mapping = {
            "merge": 1,
            "split": 2,
            "compress": 3,
            "rotate": 4,
            "convert": 5,
            "security": 6
        }
        
        target_page = page_mapping.get(action)
        if target_page is not None and current_page_index != target_page:
            self.navigate_to_page(target_page)
            
        # انتظر حتى يتم تحميل الصفحة ثم قم بتنفيذ الإجراء
        QTimer.singleShot(500, lambda: self._execute_action_on_loaded_page(action, files))
        
    def _execute_action_on_loaded_page(self, action, files):
        """تنفيذ الإجراء على الصفحة بعد تحميلها"""
        current_page_index = self.stack.currentIndex()
        
        if current_page_index > 0 and self.pages_loaded[current_page_index]:
            # الحصول على الصفحة الحالية
            current_page = self.stack.widget(current_page_index)
            
            # إذا كانت الصفحة داخل QScrollArea، احصل على الودجت الداخلي
            if hasattr(current_page, 'widget'):
                current_page = current_page.widget()
            
            # إضافة الملفات أولاً
            if hasattr(current_page, 'add_files'):
                current_page.add_files(files)
            elif hasattr(current_page, 'file_list_frame') and hasattr(current_page.file_list_frame, 'add_files'):
                current_page.file_list_frame.add_files(files)
            
            # تعيين حالة العمل غير المكتمل للصفحة الحالية
            self.set_page_has_work(current_page_index, True)

            # تنفيذ الإجراء المناسب
            if action == "merge" and hasattr(current_page, 'execute_merge'):
                current_page.execute_merge()
            elif action == "split" and hasattr(current_page, 'execute_split'):
                current_page.execute_split()
            elif action == "compress" and hasattr(current_page, 'execute_compress'):
                current_page.execute_compress()
            elif action == "rotate" and hasattr(current_page, 'execute_rotate'):
                current_page.execute_rotate()
            elif action == "convert" and hasattr(current_page, 'execute_convert'):
                current_page.execute_convert()
            elif action == "security" and hasattr(current_page, 'execute_security'):
                current_page.execute_security()

            # إعادة تفعيل النافذة الرئيسية بعد تنفيذ الإجراء
            self.setEnabled(True)

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
                return

            # استبدال الويدجت بطريقة مباشرة وآمنة
            self.stack.removeWidget(old_widget)
            self.stack.insertWidget(index, new_page)

            # تنظيف الويدجت القديم
            old_widget.setParent(None)
            old_widget.deleteLater()


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
    """Main function to run the application."""
    app = SingleApplication(sys.argv)
    
    # Register the notification system before checking for libraries
    try:
        from ui.notification_system import global_notification_manager, NotificationBar, check_and_notify_missing_libraries
        
        # Create a temporary notification bar if not already registered
        if not global_notification_manager.notification_bar:
            from PySide6.QtWidgets import QMainWindow
            temp_window = QMainWindow()
            notification_bar = NotificationBar(temp_window)
            global_notification_manager.register_widgets(temp_window, notification_bar)
            
        # Check for missing libraries and notify the user
        if not check_and_notify_missing_libraries():
            # If essential libraries are missing, exit gracefully
            sys.exit(1)
            
    except ImportError as e:
        # Handle cases where even basic modules are missing
        QMessageBox.critical(None, "Fatal Error", f"A critical module is missing: {e}\nPlease reinstall the application.")
        sys.exit(1)
    except Exception as e:
        warning(f"Error during library check: {e}")

    # Set up the first run of the application
    try:
        from modules.default_settings import setup_first_run
        setup_first_run()
    except Exception as e:
        warning(f"Error in first run setup: {e}")

    # التحقق من التشغيل الأول
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
