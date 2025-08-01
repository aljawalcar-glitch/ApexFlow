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
    QWidget, QStackedWidget, QListWidget, QLabel, QScrollArea
)
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QSharedMemory, QSystemSemaphore

# Local module imports
from modules.settings import load_settings, set_setting  # Direct import to avoid loading PDF modules
from modules.app_utils import get_icon_path
from modules.logger import debug, info, warning, error
from ui import WelcomePage, apply_theme_style
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
        """إعادة تطبيق السمة على النافذة الرئيسية وجميع عناصرها"""
        try:
            # إعادة تحميل الإعدادات
            self.settings_data = load_settings()

            # تطبيق السمة على النافذة الرئيسية
            apply_theme_style(self, "main_window", auto_register=True)

            # تطبيق السمة على القائمة الجانبية
            if hasattr(self, 'menu_list'):
                apply_theme_style(self.menu_list, "menu", auto_register=True)

            # تطبيق السمة على معلومات التطبيق
            if hasattr(self, 'app_info'):
                apply_theme_style(self.app_info, "info_widget", auto_register=True)

            # تطبيق السمة على المحتوى المكدس
            if hasattr(self, 'stacked_widget'):
                apply_theme_style(self.stacked_widget, "stacked_widget", auto_register=True)

                # تطبيق السمة على جميع الصفحات
                for i in range(self.stacked_widget.count()):
                    page = self.stacked_widget.widget(i)
                    if page:
                        apply_theme_style(page, "page", auto_register=True)
                        # تطبيق السمة على جميع العناصر الفرعية
                        for child in page.findChildren(object):
                            if hasattr(child, 'setStyleSheet'):
                                try:
                                    apply_theme_style(child, "auto", auto_register=True)
                                except:
                                    pass

            debug("تم إعادة تطبيق السمة على النافذة الرئيسية")

        except Exception as e:
            error(f"خطأ في إعادة تطبيق السمة على النافذة الرئيسية: {e}")

    def _validate_settings_delayed(self):
        """Validate settings in a deferred manner using managers"""
        try:
            # Validate settings
            if not self._validate_settings(self.settings_data):
                self.notification_manager.show_notification(
                    self, "Settings issues detected, default values will be used",
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

    def initUI(self):
        # Clear old layout if it exists
        if hasattr(self, 'centralWidget') and self.centralWidget():
            old_widget = self.centralWidget()
            old_widget.setParent(None)
            old_widget.deleteLater()
            QApplication.processEvents()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background: transparent;")

        # Set icon path correctly
        icon_path = get_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create sidebar with program information
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

        # Selection and interaction settings
        self.menu_list.setFocusPolicy(Qt.NoFocus)
        self.menu_list.setSelectionMode(QListWidget.SingleSelection)

        # Set first item as default selection
        self.menu_list.setCurrentRow(0)

        # Connect change signal
        self.menu_list.currentRowChanged.connect(self.on_menu_selection_changed)

        # Use unified theme system
        apply_theme_style(self.menu_list, "menu")

        # Add menu to sidebar
        sidebar_layout.addWidget(self.menu_list)

        # Add program information below menu
        from ui.app_info_widget import AppInfoWidget
        self.app_info = AppInfoWidget()
        sidebar_layout.addWidget(self.app_info)

        # إنشاء منطقة المحتوى مع التحميل الكسول
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")

        # إنشاء صفحة الترحيب فقط (الصفحة الافتراضية)
        self.welcome_page = WelcomePage()
        self.welcome_page.navigate_to_page.connect(self.navigate_to_page)

        # إنشاء scroll area لصفحة الترحيب
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.welcome_page)
        


        # استخدام نظام السمات الموحد مع خلفية شفافة
        apply_theme_style(scroll, "graphics_view")
        scroll.viewport().setStyleSheet("background: transparent;")



        # إضافة صفحة الترحيب إلى المكدس
        self.stack.addWidget(scroll)  # الفهرس 0

        # إنشاء صفحات نائبة مع محتوى بسيط
        page_names = [
            tr("menu_merge_print"), tr("menu_split"), tr("menu_compress"),
            tr("menu_stamp_rotate"), tr("menu_convert"), tr("menu_security"),
            tr("menu_settings")
        ]

        # إضافة عناصر نائبة للصفحات الأخرى (سيتم تحميلها عند الحاجة)
        # عدد الصفحات ديناميكي: صفحة الترحيب + الصفحات الأخرى
        self.pages_loaded = [True] + [False] * len(page_names)  # تتبع الصفحات المحملة
        for page_name in page_names:
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            layout.setAlignment(Qt.AlignCenter)

            label = QLabel(tr("loading_page_message", page_name=page_name))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: normal;")
            layout.addWidget(label)

            self.stack.addWidget(placeholder)

        # ربط القائمة بالتحميل الكسول
        self.menu_list.currentRowChanged.connect(self.load_page_on_demand)

        # حفظ مراجع العناصر
        self.sidebar_widget = sidebar_widget
        self.main_layout = main_layout
        
        # إضافة العناصر للتخطيط الرئيسي بالترتيب الافتراضي أولاً (للعربية)
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.stack)
        
        # ترتيب التخطيط حسب اللغة
        self.arrange_layout()
        
        # تحديث اتجاه شريط التمرير
        self.update_scrollbars_direction()
        
    def arrange_layout(self):
        """ترتيب التخطيط حسب اللغة"""
        if not hasattr(self, 'main_layout') or not hasattr(self, 'sidebar_widget'):
            return
        
        if not hasattr(self, 'stack'):
            return
            
        language = self.settings_data.get("language", "ar")
        
        # مسح العناصر من التخطيط
        self.main_layout.removeWidget(self.stack)
        self.main_layout.removeWidget(self.sidebar_widget)
        
        # إضافة العناصر بالترتيب الصحيح (مع مراعاة RightToLeft)
        if language == "ar":
            # في RightToLeft: العنصر الأول يظهر يميناً، الثاني يساراً
            self.main_layout.addWidget(self.sidebar_widget)  # البنل أولاً (يظهر يميناً)
            self.main_layout.addWidget(self.stack)  # المحتوى ثانياً (يظهر يساراً)
        else:
            # في LeftToRight: العنصر الأول يظهر يساراً، الثاني يميناً
            self.main_layout.addWidget(self.sidebar_widget)  # البنل أولاً (يظهر يساراً)
            self.main_layout.addWidget(self.stack)  # المحتوى ثانياً (يظهر يميناً)
    
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

    def on_menu_selection_changed(self, current_row):
        """التعامل مع تغيير التحديد في القائمة"""
        if current_row >= 0:
            self.load_page_on_demand(current_row)



    def load_page_on_demand(self, index):
        """تحميل الصفحات عند الطلب باستخدام المدراء"""
        if index < 0 or index >= len(self.pages_loaded):
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
        """إعادة تعيين جميع الصفحات المحملة عند التنقل بين التبويبات"""
        try:
            for i in range(1, self.stack.count()):
                if self.pages_loaded[i]:
                    widget = self.stack.widget(i)
                    if widget and hasattr(widget, 'widget'):
                        # إذا كان scroll area، احصل على الويدجت الداخلي
                        inner_widget = widget.widget()
                        if inner_widget and hasattr(inner_widget, 'reset_ui'):
                            inner_widget.reset_ui()
                    elif widget and hasattr(widget, 'reset_ui'):
                        # إذا كان الويدجت مباشرة
                        widget.reset_ui()
        except Exception as e:
            debug(f"خطأ في إعادة تعيين الصفحات: {e}")

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
        return MergePage(self.file_manager, operations_manager)

    def _create_split_page(self):
        from ui.split_page import SplitPage
        return SplitPage(self.file_manager, self.get_operations_manager())

    def _create_compress_page(self):
        from ui.compress_page import CompressPage
        return CompressPage(self.file_manager, self.get_operations_manager())

    def _create_rotate_page(self):
        from ui.rotate_page import RotatePage
        return RotatePage(file_path=None, parent=self)

    def _create_convert_page(self):
        from ui.convert_page import ConvertPage
        return ConvertPage(self.file_manager, self.get_operations_manager())

    def _create_security_page(self):
        from ui.security_page import SecurityPage
        return SecurityPage(self.file_manager, self.get_operations_manager())

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
            self, f"خطأ في تحميل {page_name}: {str(error)}", "error"
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
        self.notification_manager.show_notification(self, "جاري إعادة تحميل الصفحة...", "info")
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
            self, "تم تطبيق الإعدادات بنجاح", "success"
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
                self, f"خطأ في تطبيق الإعدادات: {str(e)}", "error"
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
        from ui.first_run_dialog import FirstRunDialog
        
        first_run_dialog = FirstRunDialog()
        
        def on_settings_chosen(language, theme):
            set_setting("language", language)
            set_setting("theme", theme)

            # إعادة تحميل الترجمات لضمان تطبيق اللغة المختارة
            import importlib
            from modules import translator
            importlib.reload(translator)
            
            # تطبيق الاتجاه فورًا
            if language == "ar":
                app.setLayoutDirection(Qt.RightToLeft)
            else:
                app.setLayoutDirection(Qt.LeftToRight)

        first_run_dialog.settings_chosen.connect(on_settings_chosen)
        if not first_run_dialog.exec():
            sys.exit(0) # Exit if the user closes the dialog

    # --- تطبيق اتجاه الواجهة قبل إنشاء أي نافذة ---
    settings_data = load_settings()
    language = settings_data.get("language", "ar")
    
    # تعيين اللغة في المترجم (الترجمة تعتمد على الإعدادات عند التحميل)
    
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
