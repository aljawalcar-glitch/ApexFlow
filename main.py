"""
ApexFlow - PDF file processing application
Main simplified and organized file (with smooth collapsible sidebar)
"""

# Basic library imports
import sys
import os

# Add src folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# استيرادات محسنة
from utils.sidebar_helpers import SidebarHelpers
from managers.theme_manager import refresh_all_themes

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout,
    QWidget, QListWidget, QListWidgetItem, QLabel, QScrollArea, QPushButton,
    QGridLayout, QDialog
)
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import (
    Qt, QSharedMemory, QSystemSemaphore, QTimer,
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSize, QProcess
)

# Local module imports
from utils.settings import load_settings, update_setting
from utils.logger import info, warning, error
from ui.pages.WelcomePage import WelcomePage
from managers.theme_manager import make_theme_aware
from managers.notification_system import NotificationBar
from ui.widgets.smart_drop_overlay import SmartDropOverlay
from managers.overlay_manager import OverlayManager
from utils.page_settings import page_settings
from managers.language_manager import language_manager
from utils.translator import tr
from ui.widgets.animated_stacked_widget import AnimatedStackedWidget
from config.version import get_full_version_string, APP_NAME
from utils.update_checker import check_for_updates
from ui.widgets.ui_helpers import get_icon_path
from utils.direction_auditor import audit_layout_directions

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
    # Class constants for better maintainability
    PAGE_NAMES = [
        "menu_home", "menu_merge_print", "menu_split",
        "menu_compress", "menu_stamp_rotate", "menu_convert",
        "menu_security", "menu_settings", "menu_help"
    ]
    
    # Page indices that don't accept drops
    NO_DROP_PAGES = {0, 7, 8}  # Welcome, Settings, Help
    
    def __init__(self):
        super().__init__()
        self._settings_ui_module = None
        self.is_page_transitioning = False
        
        # Track unfinished work in pages
        self._has_unfinished_work = {}  # Dictionary to track unfinished work per page
        
        # Initialize all pages as having no unfinished work
        self._has_unfinished_work = {i: False for i in range(len(self.PAGE_NAMES))}

        # Load settings once and cache them
        self.settings_data = load_settings()

        # Sidebar state
        self.sidebar_expanded = self.settings_data.get("ui_settings", {}).get("sidebar_expanded", True)
        self.sidebar_width_expanded = 190
        self.sidebar_width_collapsed = 80
        self._sidebar_anim = None
        self._icon_anim = None
        self._logo_anim_min = None
        self._logo_anim_max = None

        # Create all required managers
        self._setup_managers()
        
        # حفظ مرجع واحد لمدير العمليات
        self._operations_manager_ref = None

        # Apply unified window properties
        self._set_window_properties(get_full_version_string())
        self.setGeometry(200, 100, 1000, 600)
        self.setAcceptDrops(True)

        # تعيين الحد الأدنى والأقصى للنافذة الرئيسية
        self.setMinimumSize(850, 550)

        # Create interface first
        self.initUI()

        # Make the main window theme-aware
        make_theme_aware(self, "main_window")
        
        # Create overlay manager after UI is created
        if not hasattr(self, 'overlay_manager'):
            self.overlay_manager = OverlayManager(self)

        # Apply theme and settings in a deferred manner
        QTimer.singleShot(100, self._initialize_delayed)

    # -----------------------------
    # Window / events
    # -----------------------------
    def closeEvent(self, event):
        """Handle the window close event for resource cleanup."""
        # Check for unfinished work before closing
        if self.has_any_unfinished_work():
            pages_with_work = self.get_pages_with_work()
            message = tr("exit_with_work_warning", pages=", ".join(pages_with_work))
            
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle(tr("confirm_exit"))
            confirm_dialog.setText(message)
            confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm_dialog.setDefaultButton(QMessageBox.No)
            try:
                make_theme_aware(confirm_dialog, "dialog")
            except Exception as e:
                error(f"Error applying theme to dialog: {e}")

            if confirm_dialog.exec() == QMessageBox.No:
                event.ignore()
                return

        if hasattr(self, 'worker_manager') and self.worker_manager:
            self.worker_manager.cleanup()

        # تنظيف الملفات المؤقتة
        try:
            from utils.temp_cleaner import cleanup_on_exit
            cleanup_on_exit()
        except Exception as e:
            warning(f"Error cleaning temp files: {e}")

        event.accept()

    def resizeEvent(self, event):
        """تحديث حجم الطبقة الذكية عند تغيير حجم النافذة"""
        super().resizeEvent(event)
        if hasattr(self, 'smart_drop_overlay') and self.smart_drop_overlay:
            self.smart_drop_overlay.resize(self.size())

    def dragEnterEvent(self, event):
        """Handle drag enter events for the main window."""
        current_index = self.stack.currentIndex()
        if current_index in self.NO_DROP_PAGES:
            event.ignore()
            return

        if self.smart_drop_overlay and event.mimeData().hasUrls():
            self._update_smart_drop_mode_for_page(current_index)
            self.smart_drop_overlay.handle_drag_enter(event)
            if event.isAccepted() and hasattr(self, 'overlay_manager'):
                self.overlay_manager.active_overlay = self.smart_drop_overlay
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave events for the main window."""
        if self.smart_drop_overlay and self.smart_drop_overlay.isVisible():
            self.smart_drop_overlay.handle_drag_leave(event)
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events for the main window."""
        if self.smart_drop_overlay and self.smart_drop_overlay.isVisible():
            self.smart_drop_overlay.handle_drop(event)
            event.accept()
        else:
            event.ignore()

    # -----------------------------
    # Setup / managers / settings
    # -----------------------------
    def _set_window_properties(self, version_string):
        """Sets the window title and icon."""
        self.setWindowTitle(f"ApexFlow {version_string}")
        try:
            icon_path = get_icon_path("ApexFlow.ico")
            if icon_path and os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                # Fallback to default icon paths
                fallback_paths = [
                    "assets/icons/ApexFlow.ico",
                    "assets/ApexFlow.ico",
                    "ApexFlow.ico"
                ]
                for path in fallback_paths:
                    if os.path.exists(path):
                        self.setWindowIcon(QIcon(path))
                        break
        except Exception as e:
            warning(f"Could not set window icon: {e}")

    def _setup_managers(self):
        """Setup all required managers"""
        # Basic managers
        from managers.theme_manager import global_theme_manager
        from managers.operations_manager import FileManager, MessageManager
        from managers.notification_system import global_notification_manager
        from core.pdf_worker import PDFWorkerManager

        self.file_manager = FileManager(self)
        self.message_manager = MessageManager(self)

        # Defer creating OperationsManager until needed
        self.operations_manager = None
        self._operations_manager_creation_attempted = False

        # Specialized managers
        self.theme_manager = global_theme_manager
        self.notification_manager = global_notification_manager
        self.worker_manager = PDFWorkerManager()
        
        # The SmartDropOverlay will be created in _create_main_content
        self.smart_drop_overlay = None

        # Setup page manager
        self.pages_loaded = [True, False, False, False, False, False, False, False]

    def get_operations_manager(self):
        """Create or return OperationsManager (lazy loading)"""
        if self._operations_manager_ref is None:
            if self.operations_manager is None and not self._operations_manager_creation_attempted:
                self._operations_manager_creation_attempted = True
                try:
                    from managers.operations_manager import OperationsManager
                    self.operations_manager = OperationsManager(self, self.file_manager, self.message_manager)
                except Exception as e:
                    error(f"Error creating OperationsManager: {e}")
                    self.operations_manager = self._create_dummy_operations_manager()
            self._operations_manager_ref = self.operations_manager
        return self._operations_manager_ref

    # -----------------------------
    # Work-state helpers
    # -----------------------------
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
        pages_with_work = []
        for page_index, has_work in self._has_unfinished_work.items():
            if has_work:
                page_name = tr(self.PAGE_NAMES[page_index]) if 0 <= page_index < len(self.PAGE_NAMES) else f"Page {page_index}"
                pages_with_work.append(page_name)
        return pages_with_work

    # -----------------------------
    # Delayed init / layout / theme
    # -----------------------------
    def _initialize_delayed(self):
        """Delayed initialization of heavy components"""
        # Load theme from settings
        self.theme_manager.load_theme_from_settings()

        # Apply interface direction
        self.apply_layout_direction()

        # Validate settings
        self._validate_settings_delayed()

        # تعطيل إشارة تغيير اللغة لمنع التطبيق التلقائي
        # language_manager.language_changed.connect(self.on_language_changed)

    def apply_layout_direction(self):
        """Apply interface direction based on current language"""
        self.setLayoutDirection(language_manager.get_direction())

    def _validate_settings_delayed(self):
        """Validate settings in a deferred manner using managers"""
        try:
            if not self._validate_settings(self.settings_data):
                self.notification_manager.show_notification(
                    self, tr("settings_issues_detected"),
                    "warning"
                )
                self.settings_data = self._get_default_settings()
            from utils.settings import print_settings_info
            print_settings_info()
        except Exception as e:
            error(f"Error in deferred settings validation: {e}")

    @property
    def settings_ui(self):
        """Load settings interface when needed"""
        if self._settings_ui_module is None:
            from src.ui.pages.settings_ui import SettingsUI
            self._settings_ui_module = SettingsUI
        return self._settings_ui_module

    # -----------------------------
    # Sidebar (collapsible)
    # -----------------------------
    def _create_sidebar(self):
        """Creates the sidebar widget with icons and collapse button."""
        self.sidebar_widget = QWidget()

        # مهم: ما نستعمل setFixedWidth عشان الأنيميشن يشتغل
        # بدلاً عنها نحدد حدود دنيا/قصوى، ونحرّكهم بالأنيميشن
        self.sidebar_widget.setMinimumWidth(self.sidebar_width_collapsed)
        self.sidebar_widget.setMaximumWidth(self.sidebar_width_expanded)

        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # زر الطي/التوسيع
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedHeight(35)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.toggle_btn)

        # القائمة
        self.menu_list = QListWidget()
        self.menu_list.setFocusPolicy(Qt.NoFocus)
        self.menu_list.setSelectionMode(QListWidget.SingleSelection)
        # حجم أيقونة ابتدائي (صغير في وضع التوسيع)
        self.menu_list.setIconSize(QSize(16, 16))
        make_theme_aware(self.menu_list, "menu")
        sidebar_layout.addWidget(self.menu_list)

        # الشعار/المعلومات أسفل
        from ui.widgets.app_info_widget import AppInfoWidget
        self.app_info = AppInfoWidget(self.settings_data)
        make_theme_aware(self.app_info, "app_info")
        sidebar_layout.addWidget(self.app_info)

        # نخلي العرض الحالي Expanded مبدئياً
        initial_width = self.sidebar_width_expanded if self.sidebar_expanded else self.sidebar_width_collapsed
        self.sidebar_widget.setMinimumWidth(initial_width)
        self.sidebar_widget.setMaximumWidth(initial_width)

        # تحديث فوري للحالة المرئية عند البدء
        QTimer.singleShot(0, self._apply_initial_sidebar_state)

        return self.sidebar_widget

    def _get_app_logo_label(self):
        """يحاول يلقى لوجو (QLabel عندو Pixmap) جوة AppInfoWidget."""
        if not hasattr(self, 'app_info') or self.app_info is None:
            return None
        for lbl in self.app_info.findChildren(QLabel):
            try:
                if lbl.pixmap() is not None:
                    return lbl
            except Exception:
                pass
        return None

    def _apply_initial_sidebar_state(self):
        """تطبيق الحالة الأولية للشريط الجانبي بدون انيميشن"""
        # هذه الدالة تضمن أن الواجهة تعكس الإعدادات المحفوظة عند بدء التشغيل
        if not self.sidebar_expanded:
            # تطبيق حالة الطي مباشرة
            self.menu_list.setIconSize(QSize(24, 24))
            for i in range(self.menu_list.count()):
                self.menu_list.item(i).setText("")

            # إخفاء النصوص فقط، وإبقاء الشعار والأيقونات
            company_name_label = self.app_info.findChild(QLabel, "company_name")
            if company_name_label:
                company_name_label.setVisible(False)
            
            # إخفاء التخطيطات بالكامل
            if hasattr(self.app_info, 'version_layout'):
                for i in range(self.app_info.version_layout.count()):
                    widget = self.app_info.version_layout.itemAt(i).widget()
                    if widget:
                        widget.setVisible(False)
            
            if hasattr(self.app_info, 'author_layout'):
                for i in range(self.app_info.author_layout.count()):
                    widget = self.app_info.author_layout.itemAt(i).widget()
                    if widget:
                        widget.setVisible(False)
            
            logo = self._get_app_logo_label()
            if logo:
                logo.setMinimumSize(QSize(48, 48))
                logo.setMaximumSize(QSize(48, 48))

    def toggle_sidebar(self):
        """طي وتوسيع البنل بطريقة سموز + تكبير/تصغير الأيقونات + إخفاء/إظهار نصوص"""
        collapsing = self.sidebar_expanded  # لو كنا Expanded هسه، فنحن حنطوي
        
        #
        start_w = self.sidebar_widget.width()
        end_w = self.sidebar_width_collapsed if collapsing else self.sidebar_width_expanded

        # --------- أنيميشن العرض (نحرك min/max سوا) ----------
        anim_min = QPropertyAnimation(self.sidebar_widget, b"minimumWidth")
        anim_min.setDuration(300)
        anim_min.setStartValue(start_w)
        anim_min.setEndValue(end_w)
        anim_min.setEasingCurve(QEasingCurve.InOutCubic)

        anim_max = QPropertyAnimation(self.sidebar_widget, b"maximumWidth")
        anim_max.setDuration(300)
        anim_max.setStartValue(start_w)
        anim_max.setEndValue(end_w)
        anim_max.setEasingCurve(QEasingCurve.InOutCubic)

        group = QParallelAnimationGroup()
        group.addAnimation(anim_min)
        group.addAnimation(anim_max)

        # --------- أنيميشن حجم أيقونات القائمة ----------
        icon_from = self.menu_list.iconSize()
        icon_to = QSize(24, 24) if collapsing else QSize(16, 16)
        icon_anim = QPropertyAnimation(self.menu_list, b"iconSize")
        icon_anim.setDuration(250)
        icon_anim.setStartValue(icon_from)
        icon_anim.setEndValue(icon_to)
        icon_anim.setEasingCurve(QEasingCurve.InOutCubic)
        group.addAnimation(icon_anim)

        # --------- لوجو الأسفل (لو موجود) نعمل له بوب بسيط ----------
        logo = self._get_app_logo_label()
        if logo is not None:
            # نستعمل min/max size للوجو عشان يتحرّك بسلاسة
            logo_start = logo.maximumSize() if logo.maximumSize().width() > 0 else QSize(40, 40)
            logo_end = QSize(48, 48) if collapsing else QSize(40, 40)

            self._logo_anim_min = QPropertyAnimation(logo, b"minimumSize")
            self._logo_anim_min.setDuration(250)
            self._logo_anim_min.setStartValue(logo_start)
            self._logo_anim_min.setEndValue(logo_end)
            self._logo_anim_min.setEasingCurve(QEasingCurve.InOutCubic)

            self._logo_anim_max = QPropertyAnimation(logo, b"maximumSize")
            self._logo_anim_max.setDuration(250)
            self._logo_anim_max.setStartValue(logo_start)
            self._logo_anim_max.setEndValue(logo_end)
            self._logo_anim_max.setEasingCurve(QEasingCurve.InOutCubic)

            group.addAnimation(self._logo_anim_min)
            group.addAnimation(self._logo_anim_max)

        # --------- النصوص (القائمة + أسفل) ----------
        # ملاحظة: ما في طريقة سهلة نعمل Fade لنص QListWidgetItem بدون Delegate،
        # فحنخليها on/off مع الأنيميشن.
        def apply_text_visibility():
            if collapsing:
                # إخفاء نص العناصر
                for i in range(self.menu_list.count()):
                    self.menu_list.item(i).setText("")
                
                # إخفاء النصوص فقط في app_info، وترك الشعار والأيقونات
                company_name_label = self.app_info.findChild(QLabel, "company_name")
                if company_name_label:
                    company_name_label.setVisible(False)
                
                svg_wordmark = self.app_info.findChild(QWidget, "company_name_svg")
                if svg_wordmark:
                    svg_wordmark.setVisible(False)

                if hasattr(self.app_info, 'version_layout'):
                    for i in range(self.app_info.version_layout.count()):
                        widget = self.app_info.version_layout.itemAt(i).widget()
                        if widget:
                            widget.setVisible(False)
                
                if hasattr(self.app_info, 'author_layout'):
                    for i in range(self.app_info.author_layout.count()):
                        widget = self.app_info.author_layout.itemAt(i).widget()
                        if widget:
                            widget.setVisible(False)
            else:
                # رجّع النصوص حسب الترجمة
                keys = [
                    "menu_home","menu_merge_print","menu_split",
                    "menu_compress","menu_stamp_rotate","menu_convert",
                    "menu_security","menu_settings","menu_help"
                ]
                for i in range(self.menu_list.count()):
                    if i < len(keys):
                        self.menu_list.item(i).setText(tr(keys[i]))
                # لا نظهر عناصر app_info هنا، سنظهرها بعد انتهاء الانيميشن
                pass

        # نطبّق النصوص مع بداية الحركة عشان الإحساس يكون متماسك
        apply_text_visibility()

        # ثبّت المراجع عشان GC ما يوقف الأنيميشن
        self._sidebar_anim = group
        self._icon_anim = icon_anim

        def on_finished():
            # بعد ما نكمّل، نخلي القيود min/max تساوي الوضع النهائي
            self.sidebar_widget.setMinimumWidth(end_w)
            self.sidebar_widget.setMaximumWidth(end_w)
            self.sidebar_expanded = not collapsing

            # إذا كنا في وضع التوسيع، أظهر عناصر app_info بعد انتهاء الانيميشن
            if not collapsing:
                # إظهار اسم الشركة والأزرار
                company_name_label = self.app_info.findChild(QLabel, "company_name")
                if company_name_label:
                    company_name_label.setVisible(True)

                svg_wordmark = self.app_info.findChild(QWidget, "company_name_svg")
                if svg_wordmark:
                    svg_wordmark.setVisible(True)
                
                for button in self.app_info.findChildren(QPushButton):
                    button.setVisible(True)

                # إظهار تخطيطات الإصدار والمؤلف
                if hasattr(self.app_info, 'version_layout'):
                    for i in range(self.app_info.version_layout.count()):
                        widget = self.app_info.version_layout.itemAt(i).widget()
                        if widget:
                            widget.setVisible(True)
                
                if hasattr(self.app_info, 'author_layout'):
                    for i in range(self.app_info.author_layout.count()):
                        widget = self.app_info.author_layout.itemAt(i).widget()
                        if widget:
                            widget.setVisible(True)
                
                # تحديث الأنماط لضمان تطبيق السمة
                self.app_info.style().unpolish(self.app_info)
                self.app_info.style().polish(self.app_info)

                # تحديث التخطيط بالكامل لضمان إعادة الحساب الصحيح
                self.app_info.updateGeometry()
                self.sidebar_widget.updateGeometry()

        group.finished.connect(on_finished)
        group.start()

    # -----------------------------
    # Main content / pages
    # -----------------------------
    def _create_main_content(self):
        """Creates the main content area with the stacked widget and notification bar."""
        self.stack = AnimatedStackedWidget()
        self.stack.setStyleSheet("background: transparent;")

        # Welcome page
        self.welcome_page = WelcomePage()
        self.welcome_page.navigate_to_page.connect(self.navigate_to_page)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.welcome_page)
        # نخلي السمة للـ ScrollArea
        make_theme_aware(scroll, "scroll")
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
        self.smart_drop_overlay.reset_mode()

        # Notification System
        self.notification_bar = NotificationBar(right_panel_widget)
        make_theme_aware(self.notification_bar, "notification")
        right_panel_layout.addWidget(self.notification_bar, 0, 0, alignment=Qt.AlignTop)
        self.notification_manager.register_widgets(self, self.notification_bar)

        return right_panel_widget

    def initUI(self):
        """Initializes the main user interface."""
        if self.centralWidget():
            old_widget = self.centralWidget()
            old_widget.setParent(None)
            old_widget.deleteLater()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background: transparent;")

        # Remove duplicate icon setting - handled in _set_window_properties

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

        # Populate sidebar and arrange layout now that all components exist
        self._update_sidebar()
        self.menu_list.setCurrentRow(0)
        
    def arrange_layout(self):
        """ترتيب التخطيط حسب اللغة"""
        if not hasattr(self, 'main_layout') or not hasattr(self, 'sidebar_widget'):
            return
        if not hasattr(self, 'stack'):
            return
        
        # مسح العناصر من التخطيط
        self.main_layout.removeWidget(self.sidebar_widget)
        self.main_layout.removeWidget(self.right_panel_widget)
        
        # إضافة العناصر بالترتيب الصحيح (RightToLeft بنحافظ على نفس الترتيب هنا)
        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.right_panel_widget, 1)
    
    def update_scrollbars_direction(self):
        """تحديث اتجاه شريط التمرير في جميع الصفحات"""
        direction = language_manager.get_direction()
        
        # تحديث جميع QScrollArea في التطبيق
        for i in range(self.stack.count()):
            page = self.stack.widget(i)
            if isinstance(page, QScrollArea):
                page.setLayoutDirection(direction)

        # إعداد اختصارات لوحة المفاتيح (بدون تحميل الوحدات)
        self.setup_keyboard_shortcuts_lazy()

    # -----------------------------
    # Navigation / pages loading
    # -----------------------------
    def navigate_to_page(self, page_identifier):
        """التنقل إلى صفحة معينة من صفحة الترحيب"""
        if isinstance(page_identifier, int):
            index = page_identifier
        else:
            page_mapping = {
                "merge": 1, "split": 2, "compress": 3,
                "rotate": 4, "convert": 5, "security": 6,
                "settings": 7, "help": 8
            }
            index = page_mapping.get(page_identifier, 0)

        if index > 0:
            if hasattr(self, 'smart_drop_overlay') and self.smart_drop_overlay and self.smart_drop_overlay.isVisible():
                self.smart_drop_overlay.close()
            self.menu_list.setCurrentRow(index)
            self.load_page_on_demand(index)
        else:
            self.stack.fade_to_index(index)

    def handle_menu_selection(self, item):
        """Handles menu selection simply and directly."""
        desired_row = self.menu_list.row(item)
        current_index = self.stack.currentIndex()
        
        if self.is_page_transitioning:
            return
        
        if current_index == desired_row:
            return
            
        page_names = [
            tr("menu_home"), tr("menu_merge_print"), tr("menu_split"),
            tr("menu_compress"), tr("menu_stamp_rotate"), tr("menu_convert"),
            tr("menu_security"), tr("menu_settings"), tr("menu_help")
        ]
        
        current_page_name = page_names[current_index] if current_index < len(page_names) else f"Page {current_index}"
        target_page_name = page_names[desired_row] if desired_row < len(page_names) else f"Page {desired_row}"

        if self.get_page_has_work(current_index):
            message = tr("navigation_with_work_warning", 
                        current_page=current_page_name, 
                        target_page=target_page_name)
            
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle(tr("confirm_navigation"))
            confirm_dialog.setText(message)
            confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm_dialog.setDefaultButton(QMessageBox.Yes)
            try:
                make_theme_aware(confirm_dialog, "dialog")
            except Exception:
                pass
                
            if confirm_dialog.exec() == QMessageBox.Yes:
                current_page_widget = self.stack.widget(current_index)
                if current_index == 7:  # Settings page
                    try:
                        if hasattr(current_page_widget, 'widget'):
                            settings_widget = current_page_widget.widget()
                        else:
                            settings_widget = current_page_widget
                        if hasattr(settings_widget, 'cancel_changes'):
                            settings_widget.cancel_changes()
                        else:
                            if hasattr(settings_widget, 'reset_ui'):
                                settings_widget.reset_ui()
                    except Exception as e:
                        error(f"Error calling cancel_changes: {e}")
                        if hasattr(current_page_widget, 'reset_ui'):
                            current_page_widget.reset_ui()
                        elif hasattr(current_page_widget, 'widget') and hasattr(current_page_widget.widget(), 'reset_ui'):
                            current_page_widget.widget().reset_ui()
                else:
                    if hasattr(current_page_widget, 'reset_ui'):
                        current_page_widget.reset_ui()
                    elif hasattr(current_page_widget, 'widget') and hasattr(current_page_widget.widget(), 'reset_ui'):
                        current_page_widget.widget().reset_ui()
            else:
                self.menu_list.blockSignals(True)
                self.menu_list.setCurrentRow(current_index)
                self.menu_list.blockSignals(False)
                return

        if hasattr(self, 'smart_drop_overlay') and self.smart_drop_overlay and self.smart_drop_overlay.isVisible():
            self.smart_drop_overlay.close()
        self.load_page_on_demand(desired_row)
        self.menu_list.setCurrentRow(desired_row)
        self._update_smart_drop_mode_for_page(desired_row)

    def load_page_on_demand(self, index):
        """تحميل الصفحات عند الطلب باستخدام المدراء"""
        if index < 0 or index >= len(self.pages_loaded):
            return

        if index == 0:
            self.stack.fade_to_index(0)
            return

        if self.pages_loaded[index]:
            self.is_page_transitioning = True
            self.stack.fade_to_index(index)
            return

        try:
            page = self._create_page(index)
            if page:
                self._replace_page_safely(index, page)
                self.pages_loaded[index] = True
                make_theme_aware(page, "dialog")
        except Exception as e:
            error(f"Error creating page {index}: {e}")
            self._handle_page_load_error(index, e)

        self.is_page_transitioning = True
        self.stack.fade_to_index(index)

    def on_page_transition_finished(self):
        """Slot to be called when the page transition animation is finished."""
        self.is_page_transitioning = False

    def get_page_index(self, page_widget):
        """Gets the index of a given page widget in the stack."""
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            # The page might be wrapped in a QScrollArea
            if widget is page_widget or (hasattr(widget, 'widget') and widget.widget() is page_widget):
                return i
        return -1

    def _reset_all_loaded_pages(self):
        """Resets all loaded pages."""
        try:
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

    # -----------------------------
    # Page factories
    # -----------------------------
    def _create_merge_page(self):
        from ui.pages.merge_page import MergePage
        operations_manager = self.get_operations_manager()
        return MergePage(self.file_manager, operations_manager, self.notification_manager)

    def _create_split_page(self):
        from ui.pages.split_page import SplitPage
        return SplitPage(self.file_manager, self.get_operations_manager(), self.notification_manager)

    def _create_compress_page(self):
        from ui.pages.compress_page import CompressPage
        return CompressPage(self.file_manager, self.get_operations_manager(), self.notification_manager)

    def _create_rotate_page(self):
        from ui.pages.rotate_page import RotatePage
        return RotatePage(self.notification_manager, file_path=None, parent=self)

    def _create_convert_page(self):
        from ui.pages.convert_page import ConvertPage
        return ConvertPage(self.file_manager, self.get_operations_manager(), self.notification_manager, parent=self)

    def _create_security_page(self):
        from ui.pages.security_page import SecurityPage
        return SecurityPage(self.file_manager, self.get_operations_manager(), self.notification_manager)

    def _create_settings_page(self):
        SettingsUI = self.settings_ui
        if SettingsUI:
            settings_widget = SettingsUI(self)
            settings_widget.settings_changed.connect(self.on_settings_changed)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(settings_widget)
            # تأكد من تطبيق سمة الـ ScrollArea
            make_theme_aware(scroll_area, "scroll")
            from managers.theme_manager import global_theme_manager
            global_theme_manager.change_theme(global_theme_manager.current_theme, global_theme_manager.current_accent)
            return scroll_area
        else:
            return self._create_error_widget(tr("error_loading_settings_page"))

    def _create_help_page(self):
        from ui.pages.help_page import HelpPage
        return HelpPage(self)

    # -----------------------------
    # Errors / notifications
    # -----------------------------
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

        self.notification_manager.show_notification(
            tr("error_loading_page", page_name=page_name, error=str(error_obj)), "error"
        )
        error(f"Error loading page {page_name} (index {index}): {error_obj}")
        self._create_error_page(index, f"خطأ في تحميل {page_name}", str(error_obj))

    def _create_error_page(self, index, title, message):
        """إنشاء صفحة خطأ باستخدام المدراء"""
        error_page = QWidget()
        error_layout = QVBoxLayout(error_page)
        error_layout.setAlignment(Qt.AlignCenter)
        error_layout.setSpacing(20)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ff6b6b; font-size: 18px; font-weight: bold;")

        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        message_label.setWordWrap(True)

        from ui.widgets.svg_icon_button import create_action_button
        retry_button = create_action_button("reset", 24, tr("retry_button"))
        retry_button.clicked.connect(lambda: self._retry_load_page(index))

        error_layout.addWidget(title_label)
        error_layout.addWidget(message_label)
        error_layout.addWidget(retry_button)

        make_theme_aware(error_page, "dialog")

        self.stack.removeWidget(self.stack.widget(index))
        self.stack.insertWidget(index, error_page)

    def _retry_load_page(self, index):
        """إعادة محاولة تحميل الصفحة مع إشعار"""
        self.pages_loaded[index] = False
        self.notification_manager.show_notification(tr("reloading_page"), "info")
        self.load_page_on_demand(index)

    # -----------------------------
    # Theming / settings helpers
    # -----------------------------
    def _validate_settings(self, settings_data):
        """التحقق من صحة بيانات الإعدادات"""
        if not isinstance(settings_data, dict):
            error("الإعدادات ليست من نوع dictionary")
            return False

        required_keys = {
            "theme": str,
            "accent_color": str,
            "ui_settings": dict,
            "keyboard_shortcuts": dict
        }

        for key, expected_type in required_keys.items():
            if key not in settings_data:
                warning(f"مفتاح مفقود في الإعدادات: {key}")
                return False
            if not isinstance(settings_data[key], expected_type):
                warning(f"نوع بيانات خاطئ للمفتاح {key}: متوقع {expected_type.__name__}")
                return False

        ui_settings = settings_data.get("ui_settings", {})
        if "font_size" in ui_settings:
            font_size = ui_settings["font_size"]
            if not isinstance(font_size, (int, float)) or font_size < 8 or font_size > 24:
                warning(f"حجم خط غير صالح: {font_size}")
                return False

        accent_color = settings_data.get("accent_color", "")
        if not self._is_valid_hex_color(accent_color):
            warning(f"لون تمييز غير صالح: {accent_color}")
            return False

        return True
        
    # -----------------------------
    # Smart drop actions
    # -----------------------------
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
            QTimer.singleShot(100, lambda: self.add_files_to_current_page(files))
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
        if current_page_index > 0 and self.pages_loaded[current_page_index]:
            current_page = self.stack.widget(current_page_index)
            if hasattr(current_page, 'widget'):
                current_page = current_page.widget()
            has_files = False
            if hasattr(current_page, 'has_files'):
                has_files = current_page.has_files()
            elif hasattr(current_page, 'file_list_frame') and hasattr(current_page.file_list_frame, 'has_files'):
                has_files = current_page.file_list_frame.has_files()
            self.set_page_has_work(current_page_index, has_files)
        
    def add_files_to_current_page(self, files):
        """إضافة الملفات إلى الصفحة الحالية"""
        ops = self.get_operations_manager()
        current_page, current_index = ops.get_current_page_widget()
        if current_page and ops.add_files_to_page(current_page, files):
            self.set_page_has_work(current_index, True)
                
    def execute_action_now(self, action, files):
        """تنفيذ الإجراء فورًا على الملفات"""
        ops = self.get_operations_manager()
        current_index = self.stack.currentIndex()
        target_page = ops.get_page_index_for_action(action)
        if target_page is not None and current_index != target_page:
            self.navigate_to_page(target_page)
            def execute_delayed():
                self._execute_action_on_loaded_page(action, files)
            QTimer.singleShot(300, execute_delayed)
        else:
            self._execute_action_on_loaded_page(action, files)
        
    def _execute_action_on_loaded_page(self, action, files):
        """تنفيذ الإجراء على الصفحة بعد تحميلها"""
        ops = self.get_operations_manager()
        current_page, current_index = ops.get_current_page_widget()
        if current_page:
            ops.add_files_to_page(current_page, files)
            self.set_page_has_work(current_index, True)
            ops.execute_page_action(current_page, action)
        self.setEnabled(True)

    # -----------------------------
    # Defaults / replace / shortcuts
    # -----------------------------
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
            if index < 0 or index >= self.stack.count():
                error(f"فهرس غير صالح: {index}")
                return

            old_widget = self.stack.widget(index)
            if old_widget is None:
                self.stack.insertWidget(index, new_page)
                return

            self.stack.removeWidget(old_widget)
            self.stack.insertWidget(index, new_page)

            old_widget.setParent(None)
            old_widget.deleteLater()
        except Exception as e:
            error(f"خطأ في استبدال الصفحة {index}: {e}")
            try:
                old_widget = self.stack.widget(index)
                if old_widget:
                    self.stack.removeWidget(old_widget)
                self.stack.insertWidget(index, new_page)
            except Exception as fallback_error:
                error(f"خطأ في الطريقة البديلة: {fallback_error}")
                self.stack.addWidget(new_page)

    def setup_keyboard_shortcuts_lazy(self):
        """إعداد اختصارات لوحة المفاتيح بدون تحميل الوحدات"""
        shortcuts = self.settings_data.get("keyboard_shortcuts", {})
        if shortcuts.get("open_settings"):
            settings_shortcut = QShortcut(QKeySequence(shortcuts["open_settings"]), self)
            settings_shortcut.activated.connect(lambda: self.menu_list.setCurrentRow(7))

    # -----------------------------
    # Sidebar builder / updater
    # -----------------------------
    def _update_sidebar(self):
        """Updates sidebar menu items with current language and theme icons."""
        if SidebarHelpers.update_menu_items(self.menu_list):
            self._set_window_properties(get_full_version_string())
            self.arrange_layout()
            self.update_scrollbars_direction()

    def on_language_changed(self):
        """Update UI elements when the language changes."""
        # تعطيل هذه الدالة مؤقتاً لمنع التطبيق التلقائي للغة
        pass

    def on_settings_changed(self):
        """Handles settings changes - do nothing to prevent any automatic application."""
        # لا نفعل شيئاً لمنع أي تطبيق تلقائي
        pass
    
    def apply_settings_immediately(self):
        """Apply settings immediately (called after restart confirmation)."""
        try:
            self.settings_data = load_settings(force_reload=True)
            new_language = self.settings_data.get("ui_settings", {}).get("language", "ar")
            
            # تطبيق اللغة فقط عند إعادة التشغيل
            language_manager.set_language(new_language)
            self._update_sidebar()

            if hasattr(self, 'app_info') and hasattr(self.app_info, 'update_language'):
                self.app_info.update_language()

            refresh_all_themes()

            self.notification_manager.show_notification(
                tr("settings_applied_successfully"), "success"
            )
        except Exception as e:
            error(f"Error applying settings: {e}")

    def handle_settings_save_only(self):
        """حفظ الإعدادات فقط بدون تطبيق"""
        try:
            # حفظ الإعدادات في الملف بدون تطبيق
            from utils.settings import save_settings
            # الحصول على الإعدادات من واجهة الإعدادات
            settings_page = self.stack.widget(7)
            if hasattr(settings_page, 'widget') and hasattr(settings_page.widget(), 'get_current_settings'):
                current_settings = settings_page.widget().get_current_settings()
                save_settings(current_settings)
            
            self.notification_manager.show_notification(
                tr("settings_saved_restart_required"), "info"
            )
        except Exception as e:
            error(f"Error saving settings: {e}")
            self.notification_manager.show_notification(
                tr("error_saving_settings"), "error"
            )
    
    def handle_settings_save_and_restart(self):
        """Saves settings and restarts the application without applying immediate UI changes."""
        try:
            # Save settings without applying them to the current UI
            from utils.settings import save_settings
            settings_page = self.stack.widget(7)
            if hasattr(settings_page, 'widget') and hasattr(settings_page.widget(), 'get_current_settings'):
                current_settings = settings_page.widget().get_current_settings()
                save_settings(current_settings)
            
            # Restart after a short delay to ensure settings are written
            QTimer.singleShot(200, self.restart_application)
        except Exception as e:
            error(f"Error in save and restart: {e}")
            self.restart_application()
    
    def handle_settings_reset_defaults(self):
        """إرجاع الإعدادات الافتراضية"""
        try:
            from utils.settings import save_settings
            default_settings = self._get_default_settings()
            save_settings(default_settings)
            self.notification_manager.show_notification(
                tr("settings_reset_to_defaults"), "success"
            )
        except Exception as e:
            error(f"Error resetting settings: {e}")
            self.notification_manager.show_notification(
                tr("error_resetting_settings"), "error"
            )
    
    def handle_settings_cancel(self):
        """إلغاء جميع التغييرات"""
        try:
            # إعادة تحميل الإعدادات من الملف
            self.settings_data = load_settings(force_reload=True)
            self.notification_manager.show_notification(
                tr("settings_changes_cancelled"), "info"
            )
        except Exception as e:
            error(f"Error cancelling settings: {e}")
    
    def restart_application(self):
        """Restarts the application safely."""
        # Use a flag to indicate a restart is in progress
        update_setting("restart_in_progress", True)
        
        # Get the application instance and schedule the restart
        app = QApplication.instance()
        app.quit()  # Quit the application event loop
        
        # The restart will be handled by the main script execution flow
        QProcess.startDetached(sys.executable, sys.argv)
    
    def _create_dummy_operations_manager(self):
        """Create a dummy operations manager for fallback"""
        class DummyOperationsManager:
            def get_available_printers(self):
                return ["Microsoft Print to PDF"]
            def print_files(self, files, printer_name=None, parent_widget=None):
                return False
            def merge_files(self, parent_widget):
                return False
            def get_current_page_widget(self):
                return None, -1
            def add_files_to_page(self, page, files):
                return False
            def execute_page_action(self, page, action):
                return False
            def get_page_index_for_action(self, action):
                return None
        return DummyOperationsManager()
    
    def _is_valid_hex_color(self, color_string):
        """Validate hex color format and characters using regex"""
        import re
        if not isinstance(color_string, str):
            return False
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        return bool(hex_pattern.match(color_string))

# -----------------------------
# Entry point
# -----------------------------
def main():
    """Main function to run the application."""
    app = SingleApplication(sys.argv)
    
    # بدء منظف الملفات المؤقتة في الخلفية
    try:
        from src.utils.background_cleaner import background_cleaner
        background_cleaner.start()
    except Exception as e:
        warning(f"Failed to start background cleaner: {e}")
    
    try:
        from src.managers.notification_system import global_notification_manager, NotificationBar, check_and_notify_missing_libraries
        if not global_notification_manager.notification_bar:
            from PySide6.QtWidgets import QMainWindow
            temp_window = QMainWindow()
            notification_bar = NotificationBar(parent=temp_window)
            global_notification_manager.register_widgets(temp_window, notification_bar)
        check_and_notify_missing_libraries()
    except ImportError as e:
        QMessageBox.critical(None, "Fatal Error", f"A critical module is missing: {e}\nPlease reinstall the application.")
        sys.exit(1)
    except Exception as e:
        warning(f"Error during library check: {e}")

    try:
        from utils.default_settings import setup_first_run
        setup_first_run()
    except Exception as e:
        warning(f"Error in first run setup: {e}")

    # Set application direction using the language manager
    language_manager.apply_application_direction()

    if app.is_running():
        QMessageBox.warning(None, tr("warning"), tr("app_already_running_warning"))
        sys.exit(1)

    window = ApexFlow()
    window.show()

    # تعطيل مراجعة اتجاه التخطيط مؤقتاً
    # QTimer.singleShot(1000, audit_layout_directions)

    try:
        result = app.exec()
    finally:
        # تنظيف عند الخروج
        try:
            from src.utils.background_cleaner import background_cleaner
            background_cleaner.stop()
        except Exception as e:
            warning(f"Error stopping background cleaner: {e}")
    
    sys.exit(result)

if __name__ == "__main__":
    main()
