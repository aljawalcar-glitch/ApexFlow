"""
ApexFlow - تطبيق معالجة ملفات PDF
الملف الرئيسي المبسط والمنظم
"""

# استيرادات المكتبات الأساسية
import sys
import os
import traceback

# استيرادات PySide6
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout,
    QWidget, QStackedWidget, QListWidget, QLabel, QScrollArea
)
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QSharedMemory, QSystemSemaphore

# استيرادات الوحدات المحلية
from modules.settings import load_settings  # استيراد مباشر لتجنب تحميل وحدات PDF
from modules.app_utils import get_icon_path
from modules.logger import debug, info, warning, error
from ui import WelcomePage, apply_theme_style

# ===============================
# فئات التطبيق الرئيسية
# ===============================

class SingleApplication(QApplication):
    """تطبيق بنافذة واحدة فقط"""

    def __init__(self, argv):
        super().__init__(argv)

        # إنشاء معرف فريد للتطبيق
        self._key = "ApexFlow_SingleInstance_Key"
        self._memory = QSharedMemory(self._key)
        self._semaphore = QSystemSemaphore(self._key, 1)

        # محاولة إنشاء shared memory
        if self._memory.attach():
            # التطبيق يعمل بالفعل
            self._is_running = True
        else:
            # أول مرة يتم تشغيل التطبيق
            self._is_running = False
            if not self._memory.create(1):
                self._is_running = True

    def is_running(self):
        """فحص إذا كان التطبيق يعمل بالفعل"""
        return self._is_running

class ApexFlow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._settings_ui_module = None

        # تحميل الإعدادات الأساسية فقط (تسريع البدء)
        self.settings_data = load_settings()

        # تأجيل التحقق من صحة الإعدادات وطباعة المعلومات
        from PySide6.QtCore import QTimer
        QTimer.singleShot(200, self.validate_settings_delayed)

        # إنشاء المدراء الموحدين
        from ui.theme_manager import WindowManager
        from modules.app_utils import FileManager, MessageManager, OperationsManager

        self.window_manager = WindowManager(self)
        self.file_manager = FileManager(self)
        self.message_manager = MessageManager(self)
        self.operations_manager = OperationsManager(self, self.file_manager, self.message_manager)

        # تطبيق خصائص النافذة الموحدة
        self.window_manager.set_window_properties(self, "أداة معالجة ملفات PDF")
        self.setGeometry(200, 100, 1000, 600)

        # حفظ إعدادات السمة للتطبيق المؤجل (تسريع البدء)
        self.theme = self.settings_data.get("theme", "dark")
        self.accent_color = self.settings_data.get("accent_color", "#ff6f00")

        # إنشاء الواجهة أولاً
        self.initUI()

        # تطبيق السمة بعد إنشاء الواجهة (تحسين الأداء)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.apply_theme_delayed)  # تأجيل 100ms

    def apply_theme_delayed(self):
        """تطبيق السمة بشكل مؤجل لتحسين سرعة البدء"""
        try:
            # تحديث السمة في المدير المركزي أولاً
            from ui.theme_manager import global_theme_manager
            global_theme_manager.change_theme(self.theme, self.accent_color)

            # تسجيل النافذة في النظام الذكي
            from ui import make_theme_aware
            self.theme_handler = make_theme_aware(self, "main_window")

            print(f"تم تطبيق السمة {self.theme} على النافذة الرئيسية (مؤجل)")

        except Exception as e:
            print(f"خطأ في تطبيق السمة المؤجلة: {e}")

    def validate_settings_delayed(self):
        """التحقق من صحة الإعدادات بشكل مؤجل"""
        try:
            # التحقق من صحة الإعدادات
            if not self.validate_settings(self.settings_data):
                warning("تم اكتشاف مشاكل في الإعدادات، سيتم استخدام القيم الافتراضية")
                self.settings_data = self.get_default_settings()

            # طباعة معلومات الإعدادات (مؤجل)
            from modules.settings import print_settings_info
            print_settings_info()

            debug("تم التحقق من الإعدادات بشكل مؤجل")
        except Exception as e:
            error(f"خطأ في التحقق المؤجل من الإعدادات: {e}")

    @property
    def settings_ui(self):
        """تحميل واجهة الإعدادات عند الحاجة"""
        if self._settings_ui_module is None:
            from ui.settings_ui import SettingsUI
            self._settings_ui_module = SettingsUI
        return self._settings_ui_module

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # تحديد مسار الأيقونة بشكل صحيح
        icon_path = get_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # تخطيط أفقي رئيسي
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # إنشاء الشريط الجانبي مع معلومات البرنامج
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # القائمة الجانبية
        self.menu_list = QListWidget()
        self.menu_list.addItems(["الرئيسية", "دمج وطباعة", "تقسيم", "ضغط", "ختم وتدوير", "تحويل", "حماية وخصائص", "الإعدادات"])
        self.menu_list.setLayoutDirection(Qt.RightToLeft)

        # إعدادات التحديد والتفاعل
        self.menu_list.setFocusPolicy(Qt.NoFocus)
        self.menu_list.setSelectionMode(QListWidget.SingleSelection)

        # تعيين العنصر الأول كمحدد افتراضياً
        self.menu_list.setCurrentRow(0)

        # ربط إشارة التغيير
        self.menu_list.currentRowChanged.connect(self.on_menu_selection_changed)

        # استخدام نظام السمات الموحد
        apply_theme_style(self.menu_list, "menu")

        # تعطيل تأثير اللمعان مؤقتاً لحل مشكلة التحليل
        # self.setup_shine_effect()

        # إضافة القائمة للشريط الجانبي
        sidebar_layout.addWidget(self.menu_list)

        # إضافة معلومات البرنامج أسفل القائمة
        from ui.app_info_widget import AppInfoWidget
        self.app_info = AppInfoWidget()
        sidebar_layout.addWidget(self.app_info)

        # إنشاء منطقة المحتوى مع التحميل الكسول
        self.stack = QStackedWidget()

        # إنشاء صفحة الترحيب فقط (الصفحة الافتراضية)
        self.welcome_page = WelcomePage()
        self.welcome_page.navigate_to_page.connect(self.navigate_to_page)

        # إنشاء scroll area لصفحة الترحيب
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.welcome_page)

        # استخدام نظام السمات الموحد
        apply_theme_style(scroll, "scroll")

        # إضافة صفحة الترحيب إلى المكدس
        self.stack.addWidget(scroll)  # الفهرس 0

        # إضافة عناصر نائبة للصفحات الأخرى (سيتم تحميلها عند الحاجة)
        self.pages_loaded = [True, False, False, False, False, False, False, False]  # تتبع الصفحات المحملة

        # إنشاء صفحات نائبة مع محتوى بسيط
        page_names = ["الدمج", "التقسيم", "الضغط", "التدوير", "التحويل", "حماية وخصائص", "الإعدادات"]
        for page_name in page_names:
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            layout.setAlignment(Qt.AlignCenter)

            label = QLabel(f"جاري تحميل صفحة {page_name}...")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #cccccc; font-size: 16px; font-weight: normal;")
            layout.addWidget(label)

            self.stack.addWidget(placeholder)

        # ربط القائمة بالتحميل الكسول
        self.menu_list.currentRowChanged.connect(self.load_page_on_demand)

        # إضافة العناصر للتخطيط الرئيسي
        main_layout.addWidget(self.stack)
        main_layout.addWidget(sidebar_widget)

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

    def setup_shine_effect(self):
        """إعداد تأثير اللمعان المتحرك مع الماوس"""
        from PySide6.QtCore import QTimer

        # تفعيل تتبع الماوس
        self.menu_list.setMouseTracking(True)

        # ربط أحداث الماوس
        self.menu_list.mouseMoveEvent = self.on_mouse_move
        self.menu_list.enterEvent = self.on_mouse_enter
        self.menu_list.leaveEvent = self.on_mouse_leave

        # متغيرات تأثير اللمعان
        self.shine_position = 0
        self.shine_timer = QTimer()
        self.shine_timer.timeout.connect(self.update_shine)

    def on_mouse_move(self, event):
        """تحديث موقع اللمعان مع حركة الماوس"""
        if hasattr(event, 'position'):
            mouse_x = event.position().x()
        else:
            mouse_x = event.x()

        # حساب موقع اللمعان كنسبة مئوية
        widget_width = self.menu_list.width()
        if widget_width > 0:
            self.shine_position = (mouse_x / widget_width) * 100
            self.update_shine_style()

    def on_mouse_enter(self, event):
        """بدء تأثير اللمعان عند دخول الماوس"""
        del event  # تجاهل المتغير لتجنب التحذير
        self.shine_timer.start(16)  # 60 FPS

    def on_mouse_leave(self, event):
        """إيقاف تأثير اللمعان عند خروج الماوس"""
        del event  # تجاهل المتغير لتجنب التحذير
        self.shine_timer.stop()
        # إزالة تأثير اللمعان
        self.menu_list.setStyleSheet(self.menu_list.styleSheet().replace(
            self.get_shine_style(), ""
        ))

    def update_shine(self):
        """تحديث تأثير اللمعان"""
        self.update_shine_style()

    def update_shine_style(self):
        """تحديث نمط اللمعان بناءً على موقع الماوس"""
        try:
            shine_style = self.get_shine_style()

            # إزالة النمط القديم وإضافة الجديد
            current_style = self.menu_list.styleSheet()
            # إزالة أي نمط لمعان سابق
            lines = current_style.split('\n')
            filtered_lines = [line for line in lines if 'shine-gradient' not in line]
            base_style = '\n'.join(filtered_lines)

            # تطبيق النمط الجديد مع معالجة الأخطاء
            new_style = base_style + shine_style
            self.menu_list.setStyleSheet(new_style)
        except Exception as e:
            print(f"خطأ في تحديث نمط اللمعان: {e}")
            # في حالة الخطأ، استخدم النمط الأساسي فقط
            try:
                from ui.theme_manager import apply_theme_style
                apply_theme_style(self.menu_list, "menu")
            except:
                pass

    def get_shine_style(self):
        """إنشاء نمط اللمعان بسيط بلون أبيض واحد"""
        # تبسيط التدرج لتجنب أخطاء التحليل
        start_pos = max(0.0, (self.shine_position - 10) / 100)
        shine_pos = self.shine_position / 100
        end_pos = min(1.0, (self.shine_position + 10) / 100)

        return f"""
            QListWidget::item:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0.0 transparent,
                    stop:{start_pos:.2f} transparent,
                    stop:{shine_pos:.2f} rgba(255, 255, 255, 0.4),
                    stop:{end_pos:.2f} transparent,
                    stop:1.0 transparent) !important; /* shine-gradient */
            }}
        """

    def load_page_on_demand(self, index):
        """تحميل الصفحات عند الطلب (التحميل الكسول)"""
        if index < 0 or index >= len(self.pages_loaded):
            return

        # إذا كانت الصفحة محملة بالفعل، انتقل إليها مباشرة
        if self.pages_loaded[index]:
            self.stack.setCurrentIndex(index)
            return

        # تحميل الصفحة المطلوبة
        try:
            page = None

            if index == 1:  # صفحة الدمج
                from ui.merge_page import MergePage
                page = MergePage(self.file_manager, self.operations_manager)

            elif index == 2:  # صفحة التقسيم
                from ui.split_page import SplitPage
                page = SplitPage(self.file_manager, self.operations_manager)

            elif index == 3:  # صفحة الضغط
                from ui.compress_page import CompressPage
                page = CompressPage(self.file_manager, self.operations_manager)

            elif index == 4:  # صفحة التدوير
                from ui.rotate_page import RotatePage
                # إنشاء صفحة التدوير مع parent للتناسق مع باقي الصفحات
                page = RotatePage(file_path=None, parent=self)

            elif index == 5:  # صفحة التحويل
                from ui.convert_page import ConvertPage
                page = ConvertPage(self.operations_manager)

            elif index == 6:  # صفحة الحماية
                from ui.security_page import SecurityPage
                page = SecurityPage(self.file_manager, self.operations_manager)

            elif index == 7:  # صفحة الإعدادات
                SettingsUI = self.settings_ui
                if SettingsUI:
                    settings_widget = SettingsUI(self) # Pass parent
                    settings_widget.settings_changed.connect(self.on_settings_changed)

                    # إنشاء منطقة تمرير لجعل المحتوى ديناميكيًا
                    scroll_area = QScrollArea()
                    scroll_area.setWidgetResizable(True)
                    scroll_area.setWidget(settings_widget)
                    apply_theme_style(scroll_area, "scroll") # تطبيق نمط التمرير
                    page = scroll_area
                else:
                    # إنشاء صفحة خطأ
                    error_widget = QWidget()
                    layout = QVBoxLayout(error_widget)
                    label = QLabel("خطأ في تحميل صفحة الإعدادات")
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("color: white; font-size: 16px;")
                    layout.addWidget(label)
                    page = error_widget

            # استبدال الصفحة بطريقة آمنة للذاكرة
            if page:
                self._replace_page_safely(index, page)
                self.pages_loaded[index] = True

                # تطبيق السمة الحالية على الصفحة الجديدة
                self._apply_current_theme_to_page(page, index)

        except ImportError as e:
            page_names = ["", "الدمج", "التقسيم", "الضغط", "التدوير", "التحويل", "حماية وخصائص", "الإعدادات"]
            page_name = page_names[index] if index < len(page_names) else f"الصفحة {index}"
            error(f"خطأ في استيراد وحدة صفحة {page_name} (الفهرس {index}): {e}")
            error(f"تفاصيل الخطأ: {type(e).__name__} - {str(e)}")
            self._create_error_page(index, f"فشل في تحميل وحدة صفحة {page_name}",
                                  f"تعذر استيراد الوحدة المطلوبة.\nالخطأ: {str(e)}\nتأكد من وجود الملف المطلوب.")
        except AttributeError as e:
            page_names = ["", "الدمج", "التقسيم", "الضغط", "التدوير", "التحويل", "حماية وخصائص", "الإعدادات"]
            page_name = page_names[index] if index < len(page_names) else f"الصفحة {index}"
            error(f"خطأ في خصائص صفحة {page_name} (الفهرس {index}): {e}")
            error(f"تفاصيل الخطأ: {type(e).__name__} - {str(e)}")
            self._create_error_page(index, f"خطأ في بنية صفحة {page_name}",
                                  f"مشكلة في خصائص أو دوال الصفحة.\nالخطأ: {str(e)}\nقد تحتاج الصفحة إلى تحديث.")
        except Exception as e:
            page_names = ["", "الدمج", "التقسيم", "الضغط", "التدوير", "التحويل", "حماية وخصائص", "الإعدادات"]
            page_name = page_names[index] if index < len(page_names) else f"الصفحة {index}"
            error(f"خطأ عام في تحميل صفحة {page_name} (الفهرس {index}): {e}")
            error(f"تفاصيل الخطأ: {type(e).__name__} - {str(e)}")
            error(f"تتبع الخطأ: {traceback.format_exc()}")
            self._create_error_page(index, f"خطأ غير متوقع في صفحة {page_name}",
                                  f"حدث خطأ غير متوقع أثناء تحميل الصفحة.\nالخطأ: {str(e)}\nيرجى إعادة تشغيل التطبيق.")

        # الانتقال إلى الصفحة
        self.stack.setCurrentIndex(index)

    def _create_error_page(self, index, title, message):
        """إنشاء صفحة خطأ موحدة مع معلومات مفصلة"""
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
        message_label.setStyleSheet("color: #cccccc; font-size: 14px;")
        message_label.setWordWrap(True)

        # زر إعادة المحاولة - نفس طريقة أزرار الإعدادات
        from ui.svg_icon_button import create_action_button
        retry_button = create_action_button("reset", 24, "إعادة المحاولة")
        retry_button.update_theme_colors()  # نفس ما يحدث في الإعدادات
        retry_button.clicked.connect(lambda: self.retry_load_page(index))

        error_layout.addWidget(title_label)
        error_layout.addWidget(message_label)
        error_layout.addWidget(retry_button)

        self.stack.removeWidget(self.stack.widget(index))
        self.stack.insertWidget(index, error_page)

    def retry_load_page(self, index):
        """إعادة محاولة تحميل الصفحة"""
        self.pages_loaded[index] = False  # إعادة تعيين حالة التحميل
        self.load_page_on_demand(index)  # محاولة التحميل مرة أخرى

    def refresh_all_loaded_pages(self):
        """إعادة تطبيق السمة على جميع الصفحات والعناصر المحملة"""
        try:
            # تطبيق السمة على القائمة الجانبية
            apply_theme_style(self.menu_list, "menu")

            # الأزرار بيضاء شفافة بالافتراض

            # تطبيق السمة على جميع الصفحات المحملة في المكدس
            for i in range(self.stack.count()):
                widget = self.stack.widget(i)
                if widget and (self.pages_loaded[i] if i < len(self.pages_loaded) else False):
                    # الأزرار بيضاء شفافة بالافتراض - لا حاجة لتحديث

                    # تحديد نوع الصفحة وتطبيق السمة المناسبة
                    if i == 0:  # صفحة الترحيب
                        # لا تطبق السمة على صفحة الترحيب - تبقى كما هي
                        pass
                    elif i == 1:  # صفحة الدمج
                        # لا تطبق السمة - الأزرار شفافة بالافتراض
                        pass
                    elif i == 2:  # صفحة التقسيم
                        # لا تطبق السمة - الأزرار شفافة بالافتراض
                        pass
                    elif i == 3:  # صفحة الضغط
                        # لا تطبق السمة - الأزرار شفافة بالافتراض
                        pass
                    elif i == 4:  # صفحة التدوير
                        # لا تطبق السمة - الأزرار شفافة بالافتراض
                        pass
                    elif i == 5:  # صفحة التحويل
                        # لا تطبق السمة - الأزرار شفافة بالافتراض
                        pass
                    elif i == 6:  # صفحة الحماية
                        # لا تطبق السمة - الأزرار شفافة بالافتراض
                        pass
                    elif i == 7:  # صفحة الإعدادات
                        apply_theme_style(widget, "scroll")

            info("تم إعادة تطبيق السمة على جميع الصفحات المحملة")

        except Exception as e:
            error(f"خطأ في إعادة تطبيق السمة على الصفحات: {e}")

    def _refresh_page_theme(self, page_widget, page_type):
        """إعادة تطبيق السمة على صفحة معينة"""
        try:
            from ui.theme_manager import apply_theme_style

            # تطبيق السمة على الصفحة نفسها
            apply_theme_style(page_widget, page_type, auto_register=False)

            # تطبيق السمة على العناصر الفرعية
            from PySide6.QtWidgets import QPushButton, QFrame

            # تطبيق السمة على جميع الأزرار
            for button in page_widget.findChildren(QPushButton):
                apply_theme_style(button, "button", auto_register=False)

            # تطبيق السمة على التسميات مع الحفاظ على العناوين
            for label in page_widget.findChildren(QLabel):
                # فحص إذا كانت التسمية عنوان (حجم خط كبير أو خط عريض)
                if self._is_title_label(label):
                    apply_theme_style(label, "title_text", auto_register=False)
                else:
                    apply_theme_style(label, "label", auto_register=False)

            # تطبيق السمة على جميع الإطارات
            for frame in page_widget.findChildren(QFrame):
                apply_theme_style(frame, "frame", auto_register=False)

        except Exception as e:
            error(f"خطأ في إعادة تطبيق السمة على {page_type}: {e}")

    def _is_title_label(self, label):
        """فحص إذا كانت التسمية عنوان بناءً على خصائصها"""
        try:
            # فحص النمط الحالي للتسمية
            style = label.styleSheet()

            # إذا كان حجم الخط كبير (18px أو أكثر) أو الخط عريض
            if ("font-size: 2" in style or "font-size: 3" in style or
                "font-weight: bold" in style or "font-weight: 700" in style):
                return True

            # فحص خصائص الخط
            font = label.font()
            if font.pointSize() >= 18 or font.bold():
                return True

            # فحص النص - إذا كان قصير ويحتوي على كلمات مثل "صفحة" أو أسماء الوظائف
            text = label.text()
            title_keywords = ["صفحة", "دمج", "تقسيم", "ضغط", "تدوير", "تحويل", "PDF"]
            if any(keyword in text for keyword in title_keywords) and len(text) < 50:
                return True

            return False

        except Exception:
            return False



    def _apply_current_theme_to_page(self, page, index):
        """تطبيق السمة الحالية على صفحة جديدة تم تحميلها"""
        try:
            # تحديد نوع الصفحة وتطبيق السمة المناسبة
            if index == 0:  # صفحة الترحيب
                # لا تطبق السمة على صفحة الترحيب - تبقى كما هي
                pass
            elif index == 1:  # صفحة الدمج
                # لا تطبق السمة - الأزرار شفافة بالافتراض
                pass
            elif index == 2:  # صفحة التقسيم
                # لا تطبق السمة - الأزرار شفافة بالافتراض
                pass
            elif index == 3:  # صفحة الضغط
                # لا تطبق السمة - الأزرار شفافة بالافتراض
                pass
            elif index == 4:  # صفحة التدوير
                # لا تطبق السمة - الأزرار شفافة بالافتراض
                pass
            elif index == 5:  # صفحة التحويل
                # لا تطبق السمة - الأزرار شفافة بالافتراض
                pass
            elif index == 6:  # صفحة الحماية
                # لا تطبق السمة - الأزرار شفافة بالافتراض
                pass
            elif index == 7:  # صفحة الإعدادات
                apply_theme_style(page, "scroll")

            debug(f"تم تطبيق السمة الحالية على الصفحة الجديدة {index}")

        except Exception as e:
            error(f"خطأ في تطبيق السمة على الصفحة الجديدة {index}: {e}")

    def validate_settings(self, settings_data):
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

    def get_default_settings(self):
        """الحصول على الإعدادات الافتراضية"""
        return {
            "theme": "dark",
            "accent_color": "#ff6f00",
            "ui_settings": {
                "font_size": 14,
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
        """التعامل مع تغيير الإعدادات"""
        # إعادة تحميل الإعدادات
        self.settings_data = load_settings()

        # تطبيق الإعدادات الجديدة على الواجهة
        self.apply_ui_settings()

        # إعادة تطبيق السمة على جميع العناصر المحملة
        self.refresh_all_loaded_pages()

    def apply_ui_settings(self):
        """تطبيق إعدادات الواجهة باستخدام النظام المحسن"""
        ui_settings = self.settings_data.get("ui_settings", {})

        # تحضير خيارات السمة مع حجم الخط
        font_size = ui_settings.get("font_size", 16)

        # تحديد حجم العناصر بناءً على حجم الخط
        if font_size <= 12:
            size_option = "صغير (مدمج)"
        elif font_size <= 14:
            size_option = "متوسط (افتراضي)"
        elif font_size <= 16:
            size_option = "كبير (مريح)"
        else:
            size_option = "كبير جداً (إمكانية وصول)"

        # تطبيق السمة مع الخيارات المحدثة
        theme = self.settings_data.get("theme", "dark")
        accent_color = self.settings_data.get("accent_color", "#ff6f00")

        options = {
            "transparency": 80,
            "size": size_option,
            "contrast": "عادي (متوازن)"
        }

        try:
            # تحديث السمة في المدير المركزي أولاً
            from ui.theme_manager import global_theme_manager
            global_theme_manager.change_theme(theme, accent_color, options)

            # تطبيق النمط على النافذة الرئيسية
            apply_theme_style(
                widget=self,
                widget_type="main_window",
                auto_register=False  # لا نحتاج تسجيل مرة أخرى
            )

            # إعادة تطبيق السمة على جميع العناصر
            self.refresh_all_loaded_pages()
            info(f"تم تطبيق إعدادات الواجهة بنجاح:")
            info(f"  - السمة: {theme}")
            info(f"  - لون التمييز: {accent_color}")
            info(f"  - حجم الخط: {font_size}px")
            info(f"  - حجم العناصر: {size_option}")
            debug(f"خيارات السمة المطبقة: {options}")
        except Exception as e:
            error(f"خطأ في تطبيق إعدادات الواجهة:")
            error(f"  - نوع الخطأ: {type(e).__name__}")
            error(f"  - رسالة الخطأ: {str(e)}")
            error(f"  - السمة المحاولة: {theme}")
            error(f"  - لون التمييز المحاول: {accent_color}")
            error(f"تتبع الخطأ: {traceback.format_exc()}")

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    app = SingleApplication(sys.argv)

    # فحص إذا كان التطبيق يعمل بالفعل
    if app.is_running():
        QMessageBox.warning(None, "تحذير", "التطبيق يعمل بالفعل!")
        sys.exit(1)

    # إنشاء النافذة الرئيسية
    window = ApexFlow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":

    main()
