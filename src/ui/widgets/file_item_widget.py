"""
File Item Widget Module
نسخة محسنة لإزالة الخطوط وحل مشاكل التخطيط
"""

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont
from managers.theme_manager import make_theme_aware
from utils.i18n import tr


class FileItemWidget(QWidget):
    """A widget for displaying a file."""

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        make_theme_aware(self, "file_item")
        self.file_path = file_path
        self.is_valid = True
        self.error_message = ""
        self.file_size = 0

        # تحديث بيانات الملف
        self.update_file_info()

        # إعداد الحجم والتخطيط
        self.setMinimumHeight(40)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 0, 4, 0)  # إزالة أي حواف
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignVCenter)

        # أيقونة الملف
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        from src.managers.language_manager import language_manager
        self.icon_label.setAlignment(Qt.AlignVCenter | (Qt.AlignLeft if not language_manager.is_rtl() else Qt.AlignRight))
        self.icon_label.setStyleSheet("border: none; margin: 0px; padding: 0px;")
        
        # اسم الملف
        self.file_name_label = QLabel()
        self.file_name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.file_name_label.setAlignment(Qt.AlignVCenter | (Qt.AlignLeft if not language_manager.is_rtl() else Qt.AlignRight))
        self.file_name_label.setStyleSheet("border: none; margin: 0px; padding: 0px;")

        # حجم الملف
        self.size_label = QLabel()
        self.size_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.size_label.setAlignment(Qt.AlignVCenter | (Qt.AlignRight if not language_manager.is_rtl() else Qt.AlignLeft))
        self.size_label.setStyleSheet("border: none; margin: 0px; padding: 0px;")

        # الخطوط
        font = QFont()
        font.setPointSize(10)
        font.setStyleStrategy(QFont.PreferAntialias)
        self.file_name_label.setFont(font)
        self.size_label.setFont(font)

        # إضافة العناصر إلى التخطيط
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.file_name_label, 1)
        self.layout.addWidget(self.size_label, 0)

        # تحديث العرض
        self.update_display()

    def update_file_info(self):
        """Update file information."""
        try:
            if os.path.exists(self.file_path):
                self.file_size = os.path.getsize(self.file_path)
                if self.file_path.lower().endswith('.pdf'):
                    self.is_valid = self.validate_pdf()
                else:
                    self.is_valid = True
            else:
                self.is_valid = False
                self.error_message = tr("file_not_found")
        except Exception as e:
            self.is_valid = False
            self.error_message = tr("error_reading_file", e=str(e))

    def validate_pdf(self):
        """Validate a PDF file."""
        try:
            with open(self.file_path, 'rb') as file:
                header = file.read(8)
                if not header.startswith(b'%PDF-'):
                    self.error_message = tr("invalid_pdf_file")
                    return False
            return True
        except Exception as e:
            self.error_message = tr("error_checking_pdf", e=str(e))
            return False

    def update_display(self):
        """Update the display of the widget."""
        file_name = os.path.basename(self.file_path)
        size_text = self.format_file_size(self.file_size)

        if self.is_valid:
            font_metrics = self.file_name_label.fontMetrics()
            elided_text = font_metrics.elidedText(file_name, Qt.ElideMiddle, self.file_name_label.width())
            self.file_name_label.setText(elided_text)
            self.size_label.setText(size_text)
            self.icon_label.setPixmap(QIcon.fromTheme("application-pdf").pixmap(22, 22))
            self.setToolTip(self.file_path)
        else:
            self.file_name_label.setText(f"{tr('error_label')} {file_name}")
            self.size_label.setText(self.error_message)
            self.icon_label.setPixmap(QIcon.fromTheme("dialog-error").pixmap(22, 22))
            self.setToolTip(f"{tr('error_label')} {self.error_message}")

    def format_file_size(self, size_bytes):
        """Format file size."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def resizeEvent(self, event):
        """Ensure file name text updates correctly when resized."""
        super().resizeEvent(event)
        file_name = os.path.basename(self.file_path)
        font_metrics = self.file_name_label.fontMetrics()
        elided_text = font_metrics.elidedText(file_name, Qt.ElideMiddle, self.file_name_label.width())
        self.file_name_label.setText(elided_text)
