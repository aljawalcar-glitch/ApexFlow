# -*- coding: utf-8 -*-
"""
نظام تشخيص النظام
System Diagnostics Module
"""
import os
import sys
import platform
import psutil
import subprocess
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QTabWidget, QWidget,
                              QTreeWidget, QTreeWidgetItem, QProgressBar,
                              QHeaderView, QSplitter)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor
from .theme_manager import apply_theme, global_theme_manager
from modules.translator import tr
from modules.logger import debug, info, warning, error
from modules.file_logger import log_debug, log_info, log_warning, log_error

class DiagnosticsWorker(QThread):
    """Worker thread for collecting diagnostics data."""
    system_info_ready = Signal(dict)
    performance_info_ready = Signal(dict)
    modules_info_ready = Signal(list)
    logs_ready = Signal(str)

    def run(self):
        """Collect all diagnostics data."""
        self.collect_system_info()
        self.collect_performance_info()
        self.collect_modules_info()
        self.collect_logs_info()

    def collect_system_info(self):
        """Collect system information."""
        info = {
            "os": f"{platform.system()} {platform.release()} ({platform.version()})",
            "processor": platform.processor(),
            "total_memory": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "total_disk": f"{psutil.disk_usage('/').total / (1024**3):.2f} GB",
            "python_version": platform.python_version(),
            "python_path": sys.executable,
            "app_path": os.path.abspath(os.path.dirname(sys.argv[0])),
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.system_info_ready.emit(info)

    def collect_performance_info(self):
        """Collect performance information."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        info = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": (disk.used / disk.total) * 100,
            "bytes_sent": network.bytes_sent / (1024**2),
            "bytes_recv": network.bytes_recv / (1024**2)
        }
        self.performance_info_ready.emit(info)

    def collect_modules_info(self):
        """Collect modules information."""
        modules = []
        requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "requirements.txt")
        if not os.path.exists(requirements_path):
            modules.append({"name": "requirements.txt", "status": "missing", "details": "file_not_found"})
        else:
            with open(requirements_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        package_name = line.split('==')[0].split('>')[0].split('<')[0].strip()
                        try:
                            __import__(package_name)
                            modules.append({"name": package_name, "status": "loaded", "details": "module_loaded_successfully"})
                        except ImportError:
                            modules.append({"name": package_name, "status": "missing", "details": "module_not_found"})
        self.modules_info_ready.emit(modules)

    def collect_logs_info(self):
        """Collect logs information."""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            if os.path.exists(log_dir):
                log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
                if log_files:
                    latest_log = os.path.join(log_dir, sorted(log_files)[-1])
                    with open(latest_log, 'r', encoding='utf-8') as f:
                        self.logs_ready.emit(f.read())
                else:
                    self.logs_ready.emit(tr("no_log_files_found"))
            else:
                self.logs_ready.emit(tr("log_directory_not_found"))
        except Exception as e:
            self.logs_ready.emit(f"{tr('error_loading_logs')}: {str(e)}")

class RequirementsInstaller(QThread):
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

class SystemDiagnosticsDialog(QDialog):
    """
    نافذة تشخيص النظام لعرض معلومات مفصلة عن حالة النظام والمشاكل المحتملة
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("system_diagnostics"))
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        apply_theme(self, "dialog")

        # تسجيل فتح نافذة التشخيص
        log_info("فتح نافذة تشخيص النظام")

        # إنشاء التخطيط الرئيسي
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # إنشاء علامات تبويب لتنظيم المعلومات
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # إنشاء علامات التبويب المختلفة
        self.create_system_info_tab()
        self.create_performance_tab()
        self.create_modules_tab()
        self.create_logs_tab()

        # إضافة أزرار التحكم
        button_layout = QHBoxLayout()

        # زر تحديث المعلومات
        refresh_button = QPushButton(tr("refresh"))
        apply_theme(refresh_button, "button")
        refresh_button.clicked.connect(self.refresh_all_info)
        button_layout.addWidget(refresh_button)

        # زر تصدير التقرير
        export_button = QPushButton(tr("export_report"))
        apply_theme(export_button, "button")
        export_button.clicked.connect(self.export_report)
        button_layout.addWidget(export_button)

        # زر الإغلاق
        close_button = QPushButton(tr("close_button"))
        apply_theme(close_button, "button")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # تحميل المعلومات عند بدء التشغيل
        QTimer.singleShot(100, self.refresh_all_info)

        # إعداد مؤقت لتحديث الأداء في الوقت الفعلي
        # self.performance_timer = QTimer(self)
        # self.performance_timer.timeout.connect(self.refresh_performance_info)
        # self.performance_timer.start(2000)  # تحديث كل 2 ثانية

        log_info("تم تهيئة نافذة تشخيص النظام بنجاح")



    def create_system_info_tab(self):
        """إنشاء علامة تبويب معلومات النظام"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # إنشاء شجرة لعرض المعلومات
        self.system_tree = QTreeWidget()
        self.system_tree.setHeaderLabels([tr("property"), tr("value")])
        self.system_tree.setColumnWidth(0, 200)
        apply_theme(self.system_tree, "tree_widget")

        # تطبيق السمة على أشرطة التمرير
        apply_theme(self.system_tree.verticalScrollBar(), "scrollbar")
        apply_theme(self.system_tree.horizontalScrollBar(), "scrollbar")

        layout.addWidget(self.system_tree)

        # إضافة علامة التبويب
        self.tabs.addTab(tab, tr("system_information"))



    def create_performance_tab(self):
        """إنشاء علامة تبويب أداء النظام"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # إنشاء شجرة لعرض معلومات الأداء
        self.performance_tree = QTreeWidget()
        self.performance_tree.setHeaderLabels([tr("metric"), tr("value"), tr("status")])
        self.performance_tree.setColumnWidth(0, 200)
        self.performance_tree.setColumnWidth(1, 150)
        apply_theme(self.performance_tree, "tree_widget")

        # تطبيق السمة على أشرطة التمرير
        apply_theme(self.performance_tree.verticalScrollBar(), "scrollbar")
        apply_theme(self.performance_tree.horizontalScrollBar(), "scrollbar")

        layout.addWidget(self.performance_tree)

        # إضافة شريط تقدم لاستخدام الموارد
        progress_layout = QHBoxLayout()

        # استخدام وحدة المعالجة المركزية
        cpu_layout = QVBoxLayout()
        cpu_label = QLabel(tr("cpu_usage"))
        cpu_layout.addWidget(cpu_label)
        self.cpu_progress = QProgressBar()
        cpu_layout.addWidget(self.cpu_progress)
        progress_layout.addLayout(cpu_layout)

        # استخدام الذاكرة
        memory_layout = QVBoxLayout()
        memory_label = QLabel(tr("memory_usage"))
        memory_layout.addWidget(memory_label)
        self.memory_progress = QProgressBar()
        memory_layout.addWidget(self.memory_progress)
        progress_layout.addLayout(memory_layout)

        # استخدام القرص
        disk_layout = QVBoxLayout()
        disk_label = QLabel(tr("disk_usage"))
        disk_layout.addWidget(disk_label)
        self.disk_progress = QProgressBar()
        disk_layout.addWidget(self.disk_progress)
        progress_layout.addLayout(disk_layout)

        layout.addLayout(progress_layout)

        # إضافة علامة التبويب
        self.tabs.addTab(tab, tr("performance"))



    def create_modules_tab(self):
        """إنشاء علامة تبويب حالة الوحدات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # إنشاء شجرة لعرض معلومات الوحدات
        self.modules_tree = QTreeWidget()
        self.modules_tree.setHeaderLabels([tr("module"), tr("status"), tr("details")])
        self.modules_tree.setColumnWidth(0, 200)
        self.modules_tree.setColumnWidth(1, 100)
        apply_theme(self.modules_tree, "tree_widget")

        # تطبيق السمة على أشرطة التمرير
        apply_theme(self.modules_tree.verticalScrollBar(), "scrollbar")
        apply_theme(self.modules_tree.horizontalScrollBar(), "scrollbar")

        layout.addWidget(self.modules_tree)

        # إضافة زر لتثبيت المتطلبات
        self.install_button = QPushButton(tr("install_requirements"))
        apply_theme(self.install_button, "button")
        self.install_button.clicked.connect(self.install_requirements)
        self.install_button.setEnabled(False)
        layout.addWidget(self.install_button)

        # إضافة علامة التبويب
        self.tabs.addTab(tab, tr("modules"))



    def create_logs_tab(self):
        """إنشاء علامة تبويب السجلات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # إنشاء مربع نص لعرض السجلات
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        apply_theme(self.logs_text, "text_edit")

        # تطبيق السمة على أشرطة التمرير
        apply_theme(self.logs_text.verticalScrollBar(), "scrollbar")
        apply_theme(self.logs_text.horizontalScrollBar(), "scrollbar")

        layout.addWidget(self.logs_text)

        # إضافة علامة التبويب
        self.tabs.addTab(tab, tr("logs"))


    def refresh_all_info(self):
        """تحديث جميع المعلومات في النافذة"""
        log_info("بدء تحديث جميع معلومات التشخيص")
        self.refresh_system_info()
        self.refresh_performance_info()
        self.refresh_modules_info()
        self.refresh_logs_info()
        log_info("تم تحديث جميع معلومات التشخيص بنجاح")


    def refresh_system_info(self):
        """تحديث معلومات النظام"""
        self.system_tree.clear()

        # معلومات النظام الأساسية
        system_item = QTreeWidgetItem(self.system_tree, [tr("system_information"), ""])

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
        python_item = QTreeWidgetItem(self.system_tree, [tr("python_information"), ""])

        # إصدار Python
        python_version = f"{platform.python_version()}"
        QTreeWidgetItem(python_item, [tr("python_version"), python_version])

        # مسار Python
        python_path = f"{sys.executable}"
        QTreeWidgetItem(python_item, [tr("python_path"), python_path])

        # معلومات التطبيق
        app_item = QTreeWidgetItem(self.system_tree, [tr("application_information"), ""])

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



    def refresh_performance_info(self):
        """تحديث معلومات الأداء"""
        self.performance_tree.clear()

        # معلومات وحدة المعالجة المركزية
        cpu_percent = psutil.cpu_percent(interval=1)
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
        self.cpu_progress.setValue(int(cpu_percent))

        # معلومات الذاكرة
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
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
        self.memory_progress.setValue(int(memory_percent))

        # معلومات القرص
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
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
        self.disk_progress.setValue(int(disk_percent))

        # معلومات الشبكة
        network = psutil.net_io_counters()
        bytes_sent = network.bytes_sent / (1024**2)  # تحويل إلى ميجابايت
        bytes_recv = network.bytes_recv / (1024**2)  # تحويل إلى ميجابايت
        QTreeWidgetItem(self.performance_tree, [tr("bytes_sent"), f"{bytes_sent:.2f} MB", tr("normal")])
        QTreeWidgetItem(self.performance_tree, [tr("bytes_received"), f"{bytes_recv:.2f} MB", tr("normal")])



    def refresh_modules_info(self):
        """تحديث معلومات الوحدات"""
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



    def refresh_logs_info(self):
        """تحديث معلومات السجلات"""
        self.logs_text.clear()

        # الحصول على مسار ملف السجل
        try:
            # محاولة العثور على ملف السجل
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

            # إضافة رسالة تصحيح الأخطاء
            debug(f"البحث عن مجلد السجلات في: {log_dir}")
            log_debug(f"البحث عن مجلد السجلات في: {log_dir}")

            # إنشاء مجلد السجلات إذا لم يكن موجودًا
            if not os.path.exists(log_dir):
                debug(f"مجلد السجلات غير موجود، جاري إنشاؤه: {log_dir}")
                log_debug(f"مجلد السجلات غير موجود، جاري إنشاؤه: {log_dir}")
                os.makedirs(log_dir)
                log_info(f"تم إنشاء مجلد السجلات: {log_dir}")
                self.logs_text.setText(tr("log_directory_created"))
                return

            # البحث عن ملفات السجل
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            debug(f"تم العثور على {len(log_files)} ملف سجل")
            log_debug(f"تم العثور على {len(log_files)} ملف سجل")

            if log_files:
                # فرز الملفات حسب تاريخ التعديل (الأحدث أولاً)
                log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
                latest_log = os.path.join(log_dir, log_files[0])
                debug(f"تحميل ملف السجل الأحدث: {latest_log}")
                log_debug(f"تحميل ملف السجل الأحدث: {latest_log}")

                with open(latest_log, 'r', encoding='utf-8') as f:
                    self.logs_text.setText(f.read())
                    self.logs_text.moveCursor(QTextCursor.End)
                log_info(f"تم عرض محتوى ملف السجل: {latest_log}")
            else:
                debug("لم يتم العثور على ملفات سجل")
                log_debug("لم يتم العثور على ملفات سجل")
                self.logs_text.setText(tr("no_log_files_found"))
        except Exception as e:
            error(f"خطأ في تحميل السجلات: {str(e)}")
            log_error(f"خطأ في تحميل السجلات: {str(e)}")
            self.logs_text.setText(f"{tr('error_loading_logs')}: {str(e)}")



    def export_report(self):
        """تصدير تقرير تشخيص النظام"""
        try:
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
                for i in range(self.system_tree.topLevelItemCount()):
                    item = self.system_tree.topLevelItem(i)
                    self._write_tree_item(f, item, 0)

                # معلومات الأداء
                f.write(f"\n=== {tr('performance')} ===\n")
                for i in range(self.performance_tree.topLevelItemCount()):
                    item = self.performance_tree.topLevelItem(i)
                    self._write_tree_item(f, item, 0)

                # معلومات الوحدات
                f.write(f"\n=== {tr('modules')} ===\n")
                for i in range(self.modules_tree.topLevelItemCount()):
                    item = self.modules_tree.topLevelItem(i)
                    self._write_tree_item(f, item, 0)

                # السجلات
                f.write(f"\n=== {tr('logs')} ===\n")
                f.write(self.logs_text.toPlainText())

            # إظهار رسالة نجاح
            from .notification_system import show_success
            show_success(tr("report_exported_successfully"))

        except Exception as e:
            # إظهار رسالة خطأ
            from .notification_system import show_error
            show_error(f"{tr('diagnostics_section', error_exporting_report='خطأ في تصدير التقرير')}: {str(e)}")


    def install_requirements(self):
        """Install missing requirements."""
        self.install_button.setEnabled(False)
        self.install_button.setText(tr("installing"))
        self.installer = RequirementsInstaller(self.requirements_path)
        self.installer.installation_finished.connect(self.on_installation_finished)
        self.installer.start()

    def on_installation_finished(self, success, output):
        """Handle installation finished signal."""
        from .notification_system import show_success, show_error
        if success:
            show_success(tr("requirements_installed_successfully"))
        else:
            show_error(tr("failed_to_install_requirements"), details=output)
        self.install_button.setText(tr("install_requirements"))
        self.refresh_modules_info()

    def _write_tree_item(self, file, item, level):
        """كتابة عنصر الشجرة إلى الملف"""
        indent = "  " * level
        file.write(f"{indent}{item.text(0)}: {item.text(1)}\n")

        # كتابة العناصر الفرعية
        for i in range(item.childCount()):
            self._write_tree_item(file, item.child(i), level + 1)
