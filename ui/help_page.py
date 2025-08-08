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
    QTabWidget, QStackedWidget, QScrollArea, QFrame, QMessageBox, QComboBox, QTextEdit,
    QFormLayout, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QTextCursor

from .svg_icon_button import create_action_button
from .theme_manager import apply_theme_style
from .notification_system import show_success, show_info, show_error
from modules.translator import tr
from modules.file_logger import clear_all_logs, get_latest_log_content, log_info
from modules.settings import get_setting, set_setting
from modules.logger import debug, info, warning, error

class DiagnosticsWorker(QThread):
    """Worker thread for collecting diagnostics data."""
    system_info_ready = Signal(dict)
    performance_info_ready = Signal(dict)
    modules_info_ready = Signal(list)
    logs_ready = Signal(str)

    def run(self):
        """Collect all diagnostics data with immediate feedback."""
        # إرسال معلومات النظام أولاً لأنها الأسرع
        self.collect_system_info()

        # استخدام QTimer لتأخير جمع المعلومات الأخرى لإعطاء النظام وقتاً للاستجابة
        from PySide6.QtCore import QTimer
        # تقليل التأخير بشكل كبير لتحسين سرعة الاستجابة
        QTimer.singleShot(10, self.collect_performance_info)
        QTimer.singleShot(20, self.collect_modules_info)
        QTimer.singleShot(30, self.collect_logs_info)

    def collect_system_info(self):
        """Collect system information - optimized for performance."""
        import platform
        import psutil
        from datetime import datetime

        # تجميع المعلومات الأساسية فقط
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            info = {
                "os": f"{platform.system()} {platform.release()}",
                "processor": platform.processor(),
                "total_memory": f"{memory.total / (1024**3):.1f} GB",
                "total_disk": f"{disk.total / (1024**3):.1f} GB",
                "python_version": platform.python_version(),
                "python_path": sys.executable,
                "app_path": os.path.abspath(os.path.dirname(sys.argv[0])),
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception:
            # في حالة وجود خطأ، استخدام معلومات أساسية
            info = {
                "os": platform.system(),
                "python_version": platform.python_version(),
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        self.system_info_ready.emit(info)

    def collect_performance_info(self):
        """Collect performance information - optimized for maximum speed."""
        import psutil

        try:
            # استخدام قيمة المعالج السابقة إذا كانت متاحة لتجنب الانتظار
            cpu_percent = psutil.cpu_percent(interval=None)  # الحصول على القيمة الفورية دون انتظار

            # الحصول على معلومات الذاكرة والقرص بشكل متواز
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # تخطي معلومات الشبكة في البداية لتحسين السرعة
            bytes_sent = 0
            bytes_received = 0

            info = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "bytes_sent": bytes_sent,
                "bytes_received": bytes_received
            }
        except Exception:
            # في حالة وجود خطأ، استخدام قيم افتراضية
            info = {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "bytes_sent": 0,
                "bytes_received": 0
            }
        self.performance_info_ready.emit(info)

    def collect_modules_info(self):
        """Collect modules information - optimized for faster loading."""
        import os
        import importlib

        # المسار إلى ملف requirements.txt
        requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "requirements.txt")
        modules = []

        if not os.path.exists(requirements_path):
            modules.append({
                "name": "requirements.txt",
                "status": "missing",
                "details": "file_not_found"
            })
            self.modules_info_ready.emit(modules)
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

        # استخدام find_spec بدلاً من __import__ للتحقق أسرع
        with open(requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # استخراج اسم الحزمة
                    package_name = line.split('==')[0].split('>')[0].split('<')[0].strip()
                    import_name = import_map.get(package_name, package_name)
                    try:
                        # استخدام find_spec بدلاً من __import__ للتحقق الأسرع
                        spec = importlib.util.find_spec(import_name)
                        if spec is not None:
                            modules.append({
                                "name": package_name,
                                "status": "loaded",
                                "details": "module_loaded_successfully"
                            })
                        else:
                            modules.append({
                                "name": package_name,
                                "status": "missing",
                                "details": "module_not_found"
                            })
                    except Exception:
                        modules.append({
                            "name": package_name,
                            "status": "missing",
                            "details": "module_not_found"
                        })

        self.modules_info_ready.emit(modules)

    def collect_logs_info(self):
        """Collect logs information - optimized for performance."""
        import os

        # الحصول على مسار ملف السجل
        try:
            # محاولة العثور على ملف السجل
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

            # إنشاء مجلد السجلات إذا لم يكن موجودًا
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                self.logs_ready.emit(tr("log_directory_created"))
                return

            # البحث عن ملفات السجل
            try:
                log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            except:
                log_files = []

            if log_files:
                # فرز الملفات حسب تاريخ التعديل (الأحدث أولاً)
                try:
                    log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
                    latest_log = os.path.join(log_dir, log_files[0])

                    # قراءة جزء من السجل فقط (آخر 50 سطرًا) لتقليل استهلاك الذاكرة
                    with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        if len(lines) > 50:
                            content = "".join(lines[-50:])
                            content = "... " + tr('showing_last_lines', count=50) + " ...\n\n" + content
                        else:
                            content = "".join(lines)
                        self.logs_ready.emit(content)
                except Exception:
                    self.logs_ready.emit(tr("error_reading_log_file"))
            else:
                self.logs_ready.emit(tr("no_log_files_found"))
        except Exception:
            self.logs_ready.emit(tr("error_loading_logs"))

class RequirementsInstaller(QThread):
    """Thread for installing Python requirements."""
    installation_finished = Signal(bool, str)  # success, output

    def __init__(self, requirements_path):
        super().__init__()
        self.requirements_path = requirements_path

    def run(self):
        """Install requirements using pip."""
        try:
            import subprocess
            import sys

            # Build the command
            cmd = [sys.executable, "-m", "pip", "install", "-r", self.requirements_path]

            # Run the command
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )

            # Capture output
            output = []
            for line in process.stdout:
                output.append(line)

            # Wait for completion
            process.wait()

            # Check result
            success = process.returncode == 0
            self.installation_finished.emit(success, "\n".join(output))

        except Exception as e:
            self.installation_finished.emit(False, str(e))

class HelpStepIndicator(QWidget):
    """مؤشر التبويبات في الأعلى"""

    step_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0  # البدء من تبويب المساعدة
        self.steps = ["help_tab", "notification_center_tab", "notification_settings_tab", "diagnostics_tab"]
        self.setup_ui()

    def retranslate_ui(self):
        """Retranslates the UI elements."""
        for i, key in enumerate(self.steps):
            if i < len(self.step_buttons):
                self.step_buttons[i].setText(tr(key))

    def _style_step_button(self, btn, is_current_step=False):
        """Applies the standard style to a step button."""
        apply_theme_style(btn, "tab_button")
        font_weight = "bold" if is_current_step else "normal"

        # تطبيق نمط إضافي للزر النشط
        if is_current_step:
            # إنشاء تأثير ظل للزر النشط
            btn.setStyleSheet(btn.styleSheet() + f"font-weight: {font_weight}; border-bottom: 3px solid #4a86e8; background-color: rgba(74, 134, 232, 0.1);")
        else:
            btn.setStyleSheet(btn.styleSheet() + f"font-weight: {font_weight};")

    def setup_ui(self):
        """إعداد واجهة مؤشر التبويبات"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(0)  # مسافة صفر بين الأزرار

        # إضافة مساحة مرنة في البداية لدفع الأزرار لليمين
        layout.addStretch()

        self.step_buttons = []

        for i, step_key in enumerate(self.steps):
            btn = QPushButton(tr(step_key))
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

    def closeEvent(self, event):
        """معالج حدث إغلاق النافذة - لتنظيف الموارد قبل الإغلاق"""
        # تنظيف جميع العمال الخيطيين
        self.cleanup_workers()

        # قبول حدث الإغلاق
        event.accept()

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
        QTimer.singleShot(0, self.step_indicator.retranslate_ui) # Defer translation

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
        
        # Refresh diagnostics logs if the tab is selected
        if step_index == 3:
            self.refresh_all_info()

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
        self.help_content_browser = QTextBrowser()
        layout.addWidget(self.help_content_browser)

        # تطبيق السمة وتحميل المحتوى بشكل متأخر لتسريع العرض الأولي
        QTimer.singleShot(150, lambda: [
            apply_theme_style(self.help_content_browser, "text_browser"),
            self.typewriter_effect(self.help_content_browser, tr("help_content"))
        ])

    def typewriter_effect(self, text_browser, html_content, speed=20):
        """تأثير الكتابة الآلية للنص مع الحفاظ على التنسيق"""
        # الحصول على إعدادات حركة النص
        enable_animation = get_setting("enable_text_animation", True)
        animation_speed = get_setting("text_animation_speed", 20)
        
        # إذا كانت حركة النص معطلة، عرض النص كاملاً مباشرة
        if not enable_animation:
            text_browser.setHtml(html_content)
            text_browser.setVisible(True)
            return
            
        # إخفاء النص أولاً
        text_browser.setHtml("")
        text_browser.setVisible(True)

        # تطبيق تأثير الكتابة مع الحفاظ على التنسيق
        self.typewriter_index = 0
        self.typewriter_html = html_content
        self.typewriter_browser = text_browser
        self.typewriter_speed = animation_speed

        # بدء المؤقت لتأثير الكتابة
        self.typewriter_timer = QTimer()
        self.typewriter_timer.timeout.connect(self.typewriter_next_char)
        self.typewriter_timer.start(animation_speed)

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
        self.notification_center_title = QLabel(tr("notification_center_title"))
        apply_theme_style(self.notification_center_title, "title_text")
        layout.addWidget(self.notification_center_title)

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
        self.notification_settings_title = QLabel(tr("notification_settings_title"))
        apply_theme_style(self.notification_settings_title, "title_text")
        layout.addWidget(self.notification_settings_title)

        # جلب إعدادات الإشعارات الفعلية
        try:
            from ui.notification_settings import NotificationSettingsWidget
            self.notification_settings = NotificationSettingsWidget(self.parent())
            apply_theme_style(self.notification_settings, "widget")
            layout.addWidget(self.notification_settings)
        except ImportError as e:
            # في حالة وجود خطأ في الاستيراد، عرض رسالة خطأ واضحة
            error_widget = QLabel(tr("error_loading_notification_settings", error=str(e)))
            error_widget.setStyleSheet("color: #ff6b6b; padding: 20px;")
            apply_theme_style(error_widget, "error_label")
            layout.addWidget(error_widget)
        except Exception as e:
            # في حالة وجود خطأ آخر، عرض رسالة خطأ عامة
            error_widget = QLabel(tr("error_loading_notification_settings", error=str(e)))
            error_widget.setStyleSheet("color: #ff6b6b; padding: 20px;")
            apply_theme_style(error_widget, "error_label")
            layout.addWidget(error_widget)

        # إعدادات حركة النص
        text_animation_title = QLabel(tr("text_animation_settings"))
        apply_theme_style(text_animation_title, "title_text")
        layout.addWidget(text_animation_title)

        # حاوية أفقية لعناصر التحكم
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(10, 5, 10, 5)
        controls_layout.setSpacing(15)

        # خيار تفعيل/تعطيل حركة النص مع النص المدمج
        self.enable_text_animation = QCheckBox(tr("enable_text_animation"))
        self.enable_text_animation.setChecked(get_setting("enable_text_animation", True))
        self.enable_text_animation.stateChanged.connect(self.save_text_animation_settings)
        
        # تطبيق السمة أولاً
        apply_theme_style(self.enable_text_animation, "checkbox")
        
        # فرض اتجاه التخطيط واللون الصحيحين
        from .theme_manager import global_theme_manager
        current_colors = global_theme_manager.get_current_colors()
        text_color = current_colors.get("text_body", "white")
        
        self.enable_text_animation.setLayoutDirection(Qt.RightToLeft)
        self.enable_text_animation.setStyleSheet(
            self.enable_text_animation.styleSheet() + f"color: {text_color}; background: transparent;"
        )
        
        controls_layout.addWidget(self.enable_text_animation)

        # فاصل بصري
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        apply_theme_style(separator, "separator")
        controls_layout.addWidget(separator)

        # خيار سرعة حركة النص
        speed_label = QLabel(tr("text_animation_speed"))
        apply_theme_style(speed_label, "label")
        controls_layout.addWidget(speed_label)

        self.text_animation_speed = QSpinBox()
        self.text_animation_speed.setRange(1, 100)
        self.text_animation_speed.setValue(get_setting("text_animation_speed", 20))
        apply_theme_style(self.text_animation_speed, "spin_box")
        self.text_animation_speed.valueChanged.connect(self.save_text_animation_settings)
        controls_layout.addWidget(self.text_animation_speed)

        ms_label = QLabel(tr("milliseconds"))
        apply_theme_style(ms_label, "label")
        controls_layout.addWidget(ms_label)

        # مساحة مرنة لدفع زر المعاينة إلى اليمين
        controls_layout.addStretch()

        # زر معاينة تأثير حركة النص باستخدام أيقونة SVG
        self.preview_button = create_action_button("play", tooltip=tr("preview_text_animation"))
        self.preview_button.clicked.connect(self.preview_text_animation)
        controls_layout.addWidget(self.preview_button)

        layout.addWidget(controls_frame)

    def setup_diagnostics_tab(self):
        """إعداد تبويب التشخيص عن طريق تضمين واجهة التشخيص الكاملة"""
        layout = QVBoxLayout(self.diagnostics_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            # استيراد الواجهة الفعلية للتشخيص
            # تم نقل وظائف التشخيص مباشرة إلى هذا الملف
            # لم نعد بحاجة لاستيراد SystemDiagnosticsDialog
            
            # تم بناء واجهة التشخيص مباشرة في هذا التبويب
            
            # إنشاء حاوية رئيسية للتبويبات الأفقية
            tabs_container = QWidget()
            tabs_layout = QHBoxLayout(tabs_container)
            tabs_layout.setContentsMargins(10, 10, 10, 10)
            tabs_layout.setSpacing(15)

            # إنشاء أزرار التبويبات الأفقية في اليمين
            buttons_container = QWidget()
            buttons_layout = QVBoxLayout(buttons_container)
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            buttons_layout.setSpacing(5)

            # إنشاء الأزرار
            self.system_info_btn = QPushButton(tr("system_information"))
            self.performance_btn = QPushButton(tr("performance"))
            self.modules_btn = QPushButton(tr("modules"))
            self.logs_btn = QPushButton(tr("logs"))

            # جعل الأزرار قابلة للتحقق
            self.system_info_btn.setCheckable(True)
            self.performance_btn.setCheckable(True)
            self.modules_btn.setCheckable(True)
            self.logs_btn.setCheckable(True)

            # تطبيق السمة على الأزرار
            apply_theme_style(self.system_info_btn, "tab_button")
            apply_theme_style(self.performance_btn, "tab_button")
            apply_theme_style(self.modules_btn, "tab_button")
            apply_theme_style(self.logs_btn, "tab_button")

            # تعيين الزر الأول كزر نشط
            self._style_diag_tab_button(self.system_info_btn, is_active=True)

            # تفعيل التبويب الافتراضي عند الفتح
            self.system_info_btn.setChecked(True)

            # إضافة الأزرار إلى التخطيط
            buttons_layout.addWidget(self.system_info_btn)
            buttons_layout.addWidget(self.performance_btn)
            buttons_layout.addWidget(self.modules_btn)
            buttons_layout.addWidget(self.logs_btn)
            buttons_layout.addStretch()

            # إنشاء حاوية للمحتوى
            self.diag_content = QStackedWidget()
            apply_theme_style(self.diag_content, "widget")

            # QStackedWidget لا يحتوي على أشرطة تمرير مباشرة
            # سيتم تطبيق السمات على أشرطة التمرير داخل كل تبويب على حدة

            # ربط الأزرار بالوظائف
            self.system_info_btn.clicked.connect(lambda: self._switch_diag_tab(0))
            self.performance_btn.clicked.connect(lambda: self._switch_diag_tab(1))
            self.modules_btn.clicked.connect(lambda: self._switch_diag_tab(2))
            self.logs_btn.clicked.connect(lambda: self._switch_diag_tab(3))

            # إضافة الحاويات إلى التخطيط الرئيسي - الأزرار على اليمين والمحتوى على اليسار
            tabs_layout.addWidget(self.diag_content)  # المحتوى أولاً (على اليسار)
            tabs_layout.addWidget(buttons_container)  # الأزرار ثانياً (على اليمين)
            
            # جعل المحتوى يأخذ مساحة أكبر
            tabs_layout.setStretchFactor(self.diag_content, 3)
            tabs_layout.setStretchFactor(buttons_container, 1)

            # إضافة الحاوية إلى التخطيط الرئيسي للتبويب
            layout.addWidget(tabs_container)

            # متغير لتتبع التبويبات التي تم تحميلها
            self.tabs_loaded = [False, False, False, False]




            

            


            # تحميل التبويب الافتراضي فقط عند بدء التشغيل
            QTimer.singleShot(100, lambda: self._switch_diag_tab(0))

        except ImportError:
            error_label = QLabel(tr("error_loading_diagnostics"))
            apply_theme_style(error_label, "error_label")
            layout.addWidget(error_label)
        except Exception as e:
            error_label = QLabel(tr("error_loading_diagnostics_details", error=str(e)))
            apply_theme_style(error_label, "error_label")
            layout.addWidget(error_label)

    def create_system_info_tab(self):
        from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.system_tree = QTreeWidget()
        self.system_tree.setObjectName("system_tree")
        self.system_tree.setHeaderLabels([tr("property"), tr("value")])
        self.system_tree.setColumnWidth(0, 200)
        apply_theme_style(self.system_tree, "tree_widget")



        layout.addWidget(self.system_tree)
        self.diag_content.addWidget(tab)  # استخدام addWidget بدلاً من addTab

    def create_performance_tab(self):
        from PySide6.QtWidgets import QTreeWidget, QProgressBar
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.performance_tree = QTreeWidget()
        self.performance_tree.setObjectName("performance_tree")
        self.performance_tree.setHeaderLabels([tr("metric"), tr("value"), tr("status")])
        self.performance_tree.setColumnWidth(0, 200)
        apply_theme_style(self.performance_tree, "tree_widget")
        layout.addWidget(self.performance_tree)
        
        progress_layout = QHBoxLayout()
        cpu_layout = QVBoxLayout()
        cpu_label = QLabel(tr("cpu_usage"))
        apply_theme_style(cpu_label, "label")
        cpu_layout.addWidget(cpu_label)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setObjectName("cpu_progress")
        apply_theme_style(self.cpu_progress, "progress_bar")
        cpu_layout.addWidget(self.cpu_progress)
        progress_layout.addLayout(cpu_layout)
        
        memory_layout = QVBoxLayout()
        memory_label = QLabel(tr("memory_usage"))
        apply_theme_style(memory_label, "label")
        memory_layout.addWidget(memory_label)
        self.memory_progress = QProgressBar()
        self.memory_progress.setObjectName("memory_progress")
        apply_theme_style(self.memory_progress, "progress_bar")
        memory_layout.addWidget(self.memory_progress)
        progress_layout.addLayout(memory_layout)
        
        disk_layout = QVBoxLayout()
        disk_label = QLabel(tr("disk_usage"))
        apply_theme_style(disk_label, "label")
        disk_layout.addWidget(disk_label)
        self.disk_progress = QProgressBar()
        self.disk_progress.setObjectName("disk_progress")
        apply_theme_style(self.disk_progress, "progress_bar")
        disk_layout.addWidget(self.disk_progress)
        progress_layout.addLayout(disk_layout)
        
        layout.addLayout(progress_layout)



        self.diag_content.addWidget(tab)  # استخدام addWidget بدلاً من addTab

    def create_modules_tab(self):
        from PySide6.QtWidgets import QTreeWidget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.modules_tree = QTreeWidget()
        self.modules_tree.setObjectName("modules_tree")
        self.modules_tree.setHeaderLabels([tr("module"), tr("status"), tr("details")])
        self.modules_tree.setColumnWidth(0, 200)
        apply_theme_style(self.modules_tree, "tree_widget")
        layout.addWidget(self.modules_tree)
        self.install_button = QPushButton(tr("install_requirements"))
        apply_theme_style(self.install_button, "button")
        self.install_button.clicked.connect(self.install_requirements)
        self.install_button.setEnabled(False)
        layout.addWidget(self.install_button)



        self.diag_content.addWidget(tab)  # استخدام addWidget بدلاً من addTab

    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        controls_layout = QHBoxLayout()
        refresh_logs_button = QPushButton(tr("refresh"))
        apply_theme_style(refresh_logs_button, "button")
        refresh_logs_button.clicked.connect(self.refresh_logs_info)
        controls_layout.addWidget(refresh_logs_button)
        clear_logs_button = QPushButton(tr("clear_logs"))
        apply_theme_style(clear_logs_button, "button")
        clear_logs_button.clicked.connect(self.handle_clear_logs)
        controls_layout.addWidget(clear_logs_button)
        controls_layout.addStretch()
        retention_label = QLabel(tr("log_retention_period"))
        apply_theme_style(retention_label, "label")
        controls_layout.addWidget(retention_label)
        self.retention_combo = QComboBox()
        self.retention_combo.addItems([tr("7_days"), tr("15_days"), tr("30_days"), tr("90_days"), tr("forever")])
        apply_theme_style(self.retention_combo, "combo")
        self.retention_combo.currentTextChanged.connect(self.save_log_retention_setting)
        controls_layout.addWidget(self.retention_combo)
        layout.addLayout(controls_layout)
        self.logs_text = QTextEdit()
        self.logs_text.setObjectName("logs_text")
        self.logs_text.setReadOnly(True)
        apply_theme_style(self.logs_text, "text_edit")

        # تطبيق نظام السمات المدمج على أشرطة التمرير
        from .theme_manager import apply_theme
        apply_theme(self.logs_text.verticalScrollBar(), "scrollbar")
        apply_theme(self.logs_text.horizontalScrollBar(), "scrollbar")

        layout.addWidget(self.logs_text)
        self.diag_content.addWidget(tab)  # استخدام addWidget بدلاً من addTab
        self.load_log_retention_setting()

    def refresh_all_info(self):
        # إيقاف أي عامل تشخيص قائم بالفعل
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.quit()
            if not self.worker.wait(500):  # تقليل وقت الانتظار
                self.worker.terminate()  # إنهاء بالقوة إذا لم يتوقف
                self.worker.wait(200)    # تقليل وقت الانتظار للإنهاء

        # إنشاء عامل تشخيص جديد - تحميل أقل للنظام
        self.worker = DiagnosticsWorker()
        self.worker.system_info_ready.connect(self.update_system_info)
        self.worker.performance_info_ready.connect(self.update_performance_info)
        self.worker.modules_info_ready.connect(self.update_modules_info)
        self.worker.logs_ready.connect(self.update_logs_info)

        # عرض رسالة تحميل للمستخدم
        if hasattr(self, "system_tree") and self.system_tree:
            self.system_tree.clear()
            from PySide6.QtWidgets import QTreeWidgetItem
            QTreeWidgetItem(self.system_tree, [tr("loading"), tr("please_wait")])

        if hasattr(self, "performance_tree") and self.performance_tree:
            self.performance_tree.clear()
            from PySide6.QtWidgets import QTreeWidgetItem
            QTreeWidgetItem(self.performance_tree, [tr("loading"), tr("please_wait")])

        if hasattr(self, "modules_tree") and self.modules_tree:
            self.modules_tree.clear()
            from PySide6.QtWidgets import QTreeWidgetItem
            QTreeWidgetItem(self.modules_tree, [tr("loading"), tr("please_wait")])

        if hasattr(self, "logs_text") and self.logs_text:
            self.logs_text.setText(tr("loading_logs"))

        # تقليل الأولوية لتحسين الأداء
        self.worker.start(QThread.LowPriority)

    def _on_diagnostics_complete(self):
        """يتم استدعاؤها عند اكتمال جمع معلومات التشخيص"""
        from .notification_system import show_success
        show_success(tr("diagnostics_update_complete"))

    def _style_diag_tab_button(self, btn, is_active=False):
        """تنسيق أزرار التبويبات في قسم التشخيص باستخدام نفس أسلوب التبويبات الكبيرة"""
        # الحصول على النمط الأساسي أولاً
        base_style = ""
        try:
            # إنشاء زر مؤقت للحصول على النمط الأساسي
            temp_btn = QPushButton()
            apply_theme_style(temp_btn, "tab_button")
            base_style = temp_btn.styleSheet()
            temp_btn.deleteLater()
        except:
            base_style = ""

        font_weight = "bold" if is_active else "normal"

        # تطبيق النمط الكامل مرة واحدة بدلاً من إضافته إلى النمط الحالي
        if is_active:
            # إنشاء تأثير مماثل للتبويبات الكبيرة
            btn.setStyleSheet(base_style + f"font-weight: {font_weight}; border-bottom: 3px solid #4a86e8; background-color: rgba(74, 134, 232, 0.1);")
        else:
            btn.setStyleSheet(base_style + f"font-weight: {font_weight};")

    def _switch_diag_tab(self, index):
        """تبديل التبويبات في قسم التشخيص"""
        # تحديث حالة الأزرار أولاً
        buttons = [self.system_info_btn, self.performance_btn, self.modules_btn, self.logs_btn]
        for i, btn in enumerate(buttons):
            is_active = (i == index)
            self._style_diag_tab_button(btn, is_active=is_active)
            btn.setChecked(is_active)

        # إنشاء التبويب إذا لم يتم تحميله بعد
        if not self.tabs_loaded[index]:
            if index == 0:
                self.create_system_info_tab()
            elif index == 1:
                self.create_performance_tab()
            elif index == 2:
                self.create_modules_tab()
            elif index == 3:
                self.create_logs_tab()

            # تحديث حالة التحميل
            self.tabs_loaded[index] = True

        # تحديث المحتوى بعد التأكد من تحميل التبويب
        self.diag_content.setCurrentIndex(index)

        # تحديث معلومات التبويب عند النقر عليه
        if index == 0:
            self.refresh_all_info()
        elif index == 1:
            # تحديث معلومات الأداء مباشرة
            if hasattr(self, 'worker') and self.worker:
                self.worker.collect_performance_info()
        elif index == 2:
            # تحديث معلومات الوحدات مباشرة
            if hasattr(self, 'worker') and self.worker:
                self.worker.collect_modules_info()
        elif index == 3:
            # تحديث معلومات السجلات مباشرة
            if hasattr(self, 'worker') and self.worker:
                self.worker.collect_logs_info()

    def update_system_info(self, info):
        from PySide6.QtWidgets import QTreeWidgetItem

        # استخدام self.system_tree مباشرة
        if hasattr(self, "system_tree") and self.system_tree:
            self.system_tree.clear()

            # معلومات النظام الأساسية
            system_item = QTreeWidgetItem(self.system_tree, [tr("system_information"), ""])

            # عرض المعلومات الأساسية أولاً ثم إضافة المعلومات التفصيلية لاحقاً
            # نظام التشغيل
            os_info = info.get("os", "N/A")
            QTreeWidgetItem(system_item, [tr("operating_system"), os_info])

            # معلومات المعالج
            cpu_info = info.get("processor", "N/A")
            QTreeWidgetItem(system_item, [tr("processor"), cpu_info])

            # معلومات الذاكرة
            memory_info = info.get("total_memory", "N/A")
            QTreeWidgetItem(system_item, [tr("total_memory"), memory_info])

            # معلومات القرص
            disk_info = info.get("total_disk", "N/A")
            QTreeWidgetItem(system_item, [tr("total_disk_space"), disk_info])

            # معلومات Python
            python_item = QTreeWidgetItem(self.system_tree, [tr("python_information"), ""])

            # إصدار Python
            python_version = info.get("python_version", "N/A")
            QTreeWidgetItem(python_item, [tr("python_version"), python_version])

            # مسار Python
            python_path = info.get("python_path", "N/A")
            QTreeWidgetItem(python_item, [tr("python_path"), python_path])

            # معلومات التطبيق
            app_item = QTreeWidgetItem(self.system_tree, [tr("application_information"), ""])

            # مسار التطبيق
            app_path = info.get("app_path", "N/A")
            QTreeWidgetItem(app_item, [tr("application_path"), app_path])

            # وقت التشغيل
            start_time = info.get("start_time", "N/A")
            QTreeWidgetItem(app_item, [tr("start_time"), start_time])

            # توسيع العناصر الرئيسية
            system_item.setExpanded(True)
            python_item.setExpanded(True)
            app_item.setExpanded(True)

    def update_performance_info(self, info):
        from PySide6.QtWidgets import QTreeWidgetItem, QProgressBar
        from PySide6.QtCore import Qt

        # استخدام self.performance_tree مباشرة
        if hasattr(self, "performance_tree") and self.performance_tree:
            self.performance_tree.clear()

            # الحصول على القيم من القاموس الممرر بدلاً من إعادة حسابها
            cpu_percent = info.get("cpu_percent", 0)
            memory_percent = info.get("memory_percent", 0)
            disk_percent = info.get("disk_percent", 0)

            # معلومات وحدة المعالجة المركزية
            cpu_status = tr("good") if cpu_percent < 70 else tr("warning") if cpu_percent < 90 else tr("critical")
            cpu_item = QTreeWidgetItem(self.performance_tree, [tr("cpu_usage"), f"{cpu_percent}%", cpu_status])

            # تعيين لون الحالة
            if cpu_status == tr("good"):
                cpu_item.setForeground(2, Qt.green)
            elif cpu_status == tr("warning"):
                cpu_item.setForeground(2, Qt.yellow)
            else:
                cpu_item.setForeground(2, Qt.red)

            # تحديث شريط التقدم
            if hasattr(self, "cpu_progress"):
                self.cpu_progress.setValue(int(cpu_percent))

            # معلومات الذاكرة
            memory_status = tr("good") if memory_percent < 70 else tr("warning") if memory_percent < 90 else tr("critical")
            memory_item = QTreeWidgetItem(self.performance_tree, [tr("memory_usage"), f"{memory_percent}%", memory_status])

            # تعيين لون الحالة
            if memory_status == tr("good"):
                memory_item.setForeground(2, Qt.green)
            elif memory_status == tr("warning"):
                memory_item.setForeground(2, Qt.yellow)
            else:
                memory_item.setForeground(2, Qt.red)

            # تحديث شريط التقدم
            if hasattr(self, "memory_progress"):
                self.memory_progress.setValue(int(memory_percent))

            # معلومات القرص
            disk_status = tr("good") if disk_percent < 70 else tr("warning") if disk_percent < 90 else tr("critical")
            disk_item = QTreeWidgetItem(self.performance_tree, [tr("disk_usage"), f"{disk_percent:.1f}%", disk_status])

            # تعيين لون الحالة
            if disk_status == tr("good"):
                disk_item.setForeground(2, Qt.green)
            elif disk_status == tr("warning"):
                disk_item.setForeground(2, Qt.yellow)
            else:
                disk_item.setForeground(2, Qt.red)

            # تحديث شريط التقدم
            if hasattr(self, "disk_progress"):
                self.disk_progress.setValue(int(disk_percent))

            # معلومات الشبكة - استخدام القيم من القاموس
            bytes_sent = info.get("bytes_sent", 0)
            bytes_recv = info.get("bytes_received", 0)
            QTreeWidgetItem(self.performance_tree, [tr("bytes_sent"), f"{bytes_sent:.2f} MB", tr("normal")])
            QTreeWidgetItem(self.performance_tree, [tr("bytes_received"), f"{bytes_recv:.2f} MB", tr("normal")])

    def update_modules_info(self, modules):
        from PySide6.QtWidgets import QTreeWidgetItem, QTreeWidget
        from PySide6.QtCore import Qt
        import os

        # استخدام self.modules_tree مباشرة
        if hasattr(self, "modules_tree") and self.modules_tree:
            self.modules_tree.clear()
            self.install_button.setEnabled(False)
            missing_modules = False

            # المسار إلى ملف requirements.txt
            self.requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "requirements.txt")

            if not os.path.exists(self.requirements_path):
                item = QTreeWidgetItem(self.modules_tree, ["requirements.txt", tr("missing"), tr("file_not_found")])
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

            with open(self.requirements_path, 'r') as f:
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
                            item = QTreeWidgetItem(self.modules_tree, [package_name, status, details])
                            item.setForeground(1, Qt.green)
                        except ImportError:
                            status = tr("missing")
                            details = tr("module_not_found")
                            item = QTreeWidgetItem(self.modules_tree, [package_name, status, details])
                            item.setForeground(1, Qt.red)
                            missing_modules = True

            if missing_modules:
                self.install_button.setEnabled(True)

    def update_logs_info(self, content):
        # استخدام self.logs_text مباشرة
        if hasattr(self, "logs_text") and self.logs_text:
            self.logs_text.setText(content)
            self.logs_text.moveCursor(QTextCursor.End)

    def refresh_logs_info(self):
        """تحديث معلومات السجلات"""
        self.logs_text.clear()

        # الحصول على مسار ملف السجل
        try:
            # محاولة العثور على ملف السجل
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

            # إضافة رسالة تصحيح الأخطاء

            # إنشاء مجلد السجلات إذا لم يكن موجودًا
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                info(f"تم إنشاء مجلد السجلات: {log_dir}")
                self.logs_text.setText(tr("log_directory_created"))
                show_success(tr("log_directory_created"))
                return

            # البحث عن ملفات السجل
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]

            if log_files:
                # فرز الملفات حسب تاريخ التعديل (الأحدث أولاً)
                log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
                latest_log = os.path.join(log_dir, log_files[0])

                with open(latest_log, 'r', encoding='utf-8') as f:
                    self.logs_text.setText(f.read())
                    self.logs_text.moveCursor(QTextCursor.End)
                info(f"تم عرض محتوى ملف السجل: {latest_log}")
                # إظهار إشعار النجاح
                show_success(tr("logs_refreshed_successfully"))
            else:
                self.logs_text.setText(tr("no_log_files_found"))
                # إظهار إشعار معلومات (ليس خطأ)
                show_info(tr("no_log_files_found"))
        except Exception as e:
            error(f"خطأ في تحميل السجلات: {str(e)}")
            self.logs_text.setText(f"{tr('error_loading_logs')}: {str(e)}")
            # إظهار إشعار الخطأ
            show_error(tr("error_refreshing_logs"))

    def export_report(self):
        from modules.diagnostics import export_diagnostics
        content = []
        for i in range(self.system_tree.topLevelItemCount()):
            item = self.system_tree.topLevelItem(i)
            content.append(f"{item.text(0)}: {item.text(1)}")
            for j in range(item.childCount()):
                child = item.child(j)
                content.append(f"  {child.text(0)}: {child.text(1)}")
        # ... and so on for other tabs
        report_path = export_diagnostics("\n".join(content))
        from .notification_system import show_success
        show_success(tr("report_exported_successfully", path=report_path))

    def install_requirements(self):
        requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "requirements.txt")

        # إيقاف أي مثبت قائم بالفعل
        if hasattr(self, 'installer') and self.installer and self.installer.isRunning():
            self.installer.quit()
            if not self.installer.wait(1000):  # انتظار ثانية واحدة
                self.installer.terminate()  # إنهاء بالقوة إذا لم يتوقف
                self.installer.wait(500)    # انتظار نصف ثانية للتأكد من الإنهاء

        # إنشاء مثبت جديد
        self.installer = RequirementsInstaller(requirements_path)
        self.installer.installation_finished.connect(self.on_installation_finished)
        self.installer.start()

    def on_installation_finished(self, success, output):
        from .notification_system import show_success, show_error
        if success:
            show_success(tr("requirements_installed_successfully"))
        else:
            show_error(tr("failed_to_install_requirements"), details=output)
        self.refresh_modules_info()

    def handle_clear_logs(self):
        """Handles the clear logs button click."""
        reply = QMessageBox.question(self, tr("confirm_clear_logs_title"),
                                     tr("confirm_clear_logs_message"),
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            info("User confirmed clearing all logs.")
            try:
                # الحصول على مسار مجلد السجلات
                log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

                # التحقق من وجود المجلد
                if not os.path.exists(log_dir):
                    from .notification_system import show_info
                    show_info(tr("no_log_files_found"))
                    self.refresh_logs_info()
                    return

                # حذف ملفات السجل
                deleted_count = 0
                for filename in os.listdir(log_dir):
                    if filename.endswith(".log"):
                        file_path = os.path.join(log_dir, filename)
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            error(f"فشل في حذف ملف السجل {file_path}: {str(e)}")

                if deleted_count > 0:
                    info(f"تم حذف {deleted_count} ملف سجل بنجاح")
                    from .notification_system import show_success
                    show_success(tr("logs_cleared_successfully"))
                else:
                    from .notification_system import show_info
                    show_info(tr("no_log_files_found"))
            except Exception as e:
                error(f"خطأ في مسح السجلات: {str(e)}")
                from .notification_system import show_error
                show_error(f"{tr('failed_to_clear_logs')}: {str(e)}")

            self.refresh_logs_info()

    def load_log_retention_setting(self):
        """Loads the log retention setting and updates the combo box."""
        if hasattr(self, 'retention_combo'):
            days = get_setting("log_retention_days", 7) # Default to 7 days
            text_map = { 7: tr("7_days"), 15: tr("15_days"), 30: tr("30_days"), 90: tr("90_days"), 0: tr("forever") }
            self.retention_combo.setCurrentText(text_map.get(days, tr("7_days")))

    def save_log_retention_setting(self, text):
        """Saves the selected log retention period."""
        days_map = { tr("7_days"): 7, tr("15_days"): 15, tr("30_days"): 30, tr("90_days"): 90, tr("forever"): 0 }
        days = days_map.get(text, 7)
        set_setting("log_retention_days", days)
        log_info(f"Log retention period set to {days} days.")
        from .notification_system import show_info
        show_info(tr("log_retention_setting_saved"))

    def save_text_animation_settings(self):
        """حفظ إعدادات حركة النص"""
        enabled = self.enable_text_animation.isChecked()
        speed = self.text_animation_speed.value()
        
        set_setting("enable_text_animation", enabled)
        set_setting("text_animation_speed", speed)
        
        # تطبيق الإعدادات على تأثير الكتابة الحالي إذا كان نشطاً
        if hasattr(self, "typewriter_timer") and self.typewriter_timer.isActive():
            self.typewriter_timer.stop()
            if enabled:
                self.typewriter_timer.start(speed)
                
        from .notification_system import show_success
        show_success(tr("text_animation_settings_saved"))
        
    def cancel_text_animation_settings(self):
        """إلغاء التغييرات في إعدادات حركة النص واستعادة القيم الأصلية"""
        # استعادة القيم الأصلية من الإعدادات
        original_enabled = get_setting("enable_text_animation", True)
        original_speed = get_setting("text_animation_speed", 20)
        
        # تحديث واجهة المستخدم بالقيم الأصلية
        self.enable_text_animation.setChecked(original_enabled)
        self.text_animation_speed.setValue(original_speed)
        
        from .notification_system import show_info
        show_info(tr("changes_canceled"))
        
    def preview_text_animation(self):
        """معاينة تأثير حركة النص بالانتقال إلى تبويب المساعدة وتشغيل التأثير"""
        # حفظ الإعدادات الحالية أولاً
        self.save_text_animation_settings()
        
        # الانتقال إلى تبويب المساعدة وتحديث المؤشر
        if hasattr(self, "tabs_container") and hasattr(self, "step_indicator"):
            self.step_indicator.set_current_step(0)
            self.tabs_container.setCurrentIndex(0)
        
        # التأكد من تحميل تبويب المساعدة
        if not self.help_tab_loaded:
            self.setup_help_tab()
            self.help_tab_loaded = True
        
        # العثور على عنصر عرض النص في تبويب المساعدة وتشغيل التأثير
        if hasattr(self, "help_content_browser") and self.help_content_browser:
            # إعادة تعيين التأثير الحالي إذا كان نشطاً
            if hasattr(self, "typewriter_timer") and self.typewriter_timer.isActive():
                self.typewriter_timer.stop()
            
            # تطبيق تأثير الكتابة الجديد
            self.typewriter_effect(self.help_content_browser, tr("help_content"))
        
        from .notification_system import show_info
        show_info(tr("previewing_text_animation"))
        
    def cleanup_workers(self):
        """تنظيف جميع العمال الخيطيين عند إغلاق التبويب"""
        # إيقاف عامل التشخيص
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.quit()
            if not self.worker.wait(1000):  # انتظار ثانية واحدة
                self.worker.terminate()  # إنهاء بالقوة إذا لم يتوقف
                self.worker.wait(500)    # انتظار نصف ثانية للتأكد من الإنهاء
            self.worker.deleteLater()
            self.worker = None

        # إيقاف مثبت المتطلبات
        if hasattr(self, 'installer') and self.installer and self.installer.isRunning():
            self.installer.quit()
            if not self.installer.wait(1000):  # انتظار ثانية واحدة
                self.installer.terminate()  # إنهاء بالقوة إذا لم يتوقف
                self.installer.wait(500)    # انتظار نصف ثانية للتأكد من الإنهاء
            self.installer.deleteLater()
            self.installer = None
