
"""
واجهة التشخيص
Diagnostics UI for ApexFlow
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton,
    QTabWidget, QScrollArea, QFrame, QGridLayout, QGroupBox, QCheckBox,
    QSpinBox, QComboBox, QFormLayout, QProgressBar
)
from PySide6.QtCore import Qt, QThread, pyqtSignal
from PySide6.QtGui import QTextCursor

from .theme_manager import apply_theme_style
from modules.translator import tr
from modules.diagnostics import run_diagnostics, export_diagnostics

class DiagnosticsWorker(QThread):
    """
    عامل تشغيل التشخيص في خلفية منفصلة
    """
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            results = run_diagnostics()
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class DiagnosticsPage(QWidget):
    """صفحة التشخيص"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.diagnostics_worker = None

    def setup_ui(self):
        """إعداد واجهة المستخدم لصفحة التشخيص"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # عنوان الصفحة
        title_label = QLabel(tr("diagnostics_title"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        apply_theme_style(title_label, "title")
        main_layout.addWidget(title_label)

        # منطقة عرض نتائج التشخيص
        self.results_area = QTextBrowser()
        self.results_area.setReadOnly(True)
        self.results_area.setPlaceholderText(tr("diagnostics_placeholder"))
        apply_theme_style(self.results_area, "text_browser")
        main_layout.addWidget(self.results_area)

        # شريط التقدم (يظهر عند تشغيل التشخيص)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        apply_theme_style(self.progress_bar, "progress_bar")
        main_layout.addWidget(self.progress_bar)

        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.run_button = QPushButton(tr("run_diagnostics_button"))
        apply_theme_style(self.run_button, "button")
        self.run_button.clicked.connect(self.run_diagnostics)
        buttons_layout.addWidget(self.run_button)

        self.export_button = QPushButton(tr("export_diagnostics_button"))
        apply_theme_style(self.export_button, "button")
        self.export_button.clicked.connect(self.export_diagnostics)
        self.export_button.setEnabled(False)  # تعطيل حتى يتم تشغيل التشخيص
        buttons_layout.addWidget(self.export_button)

        main_layout.addLayout(buttons_layout)

        # تطبيق السمة على الصفحة
        apply_theme_style(self, "dialog")

    def run_diagnostics(self):
        """تشغيل التشخيص في خلفية منفصلة"""
        # تعطيل الأزرار أثناء التشغيل
        self.run_button.setEnabled(False)
        self.export_button.setEnabled(False)

        # إظهار شريط التقدم
        self.progress_bar.setVisible(True)
        self.results_area.clear()
        self.results_area.setPlaceholderText(tr("diagnostics_running"))

        # إنشاء وتشغيل عامل التشخيص
        self.diagnostics_worker = DiagnosticsWorker()
        self.diagnostics_worker.finished.connect(self.on_diagnostics_finished)
        self.diagnostics_worker.error.connect(self.on_diagnostics_error)
        self.diagnostics_worker.start()

    def on_diagnostics_finished(self, results):
        """معالجة نتائج التشخيص"""
        # إخفاء شريط التقدم
        self.progress_bar.setVisible(False)

        # عرض النتائج
        self.results_area.setPlainText(results)

        # تفعيل الأزرار
        self.run_button.setEnabled(True)
        self.export_button.setEnabled(True)

        # التمرير إلى الأعلى
        cursor = self.results_area.textCursor()
        cursor.setPosition(0)
        self.results_area.setTextCursor(cursor)

    def on_diagnostics_error(self, error_message):
        """معالجة خطأ التشخيص"""
        # إخفاء شريط التقدم
        self.progress_bar.setVisible(False)

        # عرض رسالة الخطأ
        self.results_area.setPlainText(tr("diagnostics_error", error=error_message))

        # تفعيل زر التشغيل فقط
        self.run_button.setEnabled(True)
        self.export_button.setEnabled(False)

    def export_diagnostics(self):
        """تصدير نتائج التشخيص"""
        try:
            # الحصول على النتائج الحالية
            results = self.results_area.toPlainText()

            if not results or results == tr("diagnostics_placeholder"):
                from PySide6.QtWidgets import QMessageBox
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(tr("export_error"))
                msg_box.setText(tr("no_diagnostics_to_export"))
                msg_box.setIcon(QMessageBox.Warning)
                apply_theme_style(msg_box, "message_box")
                msg_box.exec_()
                return

            # تصدير النتائج
            file_path = export_diagnostics(results)

            # إعلام المستخدم بنجاح التصدير
            from PySide6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(tr("export_success"))
            msg_box.setText(tr("diagnostics_exported_successfully", path=file_path))
            msg_box.setIcon(QMessageBox.Information)
            apply_theme_style(msg_box, "message_box")
            msg_box.exec_()
        except Exception as e:
            # إعلام المستخدم بفشل التصدير
            from PySide6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(tr("export_error"))
            msg_box.setText(tr("diagnostics_export_failed", error=str(e)))
            msg_box.setIcon(QMessageBox.Critical)
            apply_theme_style(msg_box, "message_box")
            msg_box.exec_()
