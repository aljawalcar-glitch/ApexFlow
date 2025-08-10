"""
File Item Widget Module
"""

import os
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont
from modules.translator import tr

class FileItemWidget(QWidget):
    """A widget for displaying a file."""
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.is_valid = True
        self.error_message = ""
        self.file_size = 0
        
        self.update_file_info()
        
        self.setMinimumHeight(40)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setAlignment(Qt.AlignVCenter)
        
        self.icon_label = QLabel()
        self.file_name_label = QLabel()
        self.size_label = QLabel()
        
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.file_name_label)
        self.layout.addStretch()
        self.layout.addWidget(self.size_label)
        
        font = QFont()
        font.setPointSize(10)
        self.file_name_label.setFont(font)
        self.size_label.setFont(font)
        
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
