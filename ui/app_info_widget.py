# -*- coding: utf-8 -*-
"""
مكون معلومات البرنامج
App Info Widget Component
"""

import sys
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QDialog, QTextEdit, QFrame)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QIcon
from .svg_icon_button import SVGIconButton
from .theme_aware_widget import ThemeAwareDialog
from modules.translator import tr

# إضافة المجلد الجذر للمسار لاستيراد version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from version import VERSION, APP_NAME, APP_AUTHOR, get_about_text
except ImportError:
    VERSION = "v5.2.1"
    APP_NAME = "ApexFlow"
    APP_AUTHOR = "فريق ApexFlow"
    def get_about_text():
        return f"{APP_NAME} {VERSION}\nأداة شاملة لإدارة ومعالجة ملفات PDF"

class AboutDialog(ThemeAwareDialog):
    """نافذة حول البرنامج"""
    
    def __init__(self, parent=None):
        super().__init__(parent, widget_type="dialog_about")
        self.setWindowTitle(tr("about_dialog_title", app_name=APP_NAME))
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # منطقة الشعار والعنوان
        header_layout = QHBoxLayout()
        
        # الشعار
        logo_label = QLabel()
        logo_label.setFixedSize(64, 64)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # تحميل الشعار الفعلي للبرنامج
        try:
            # البحث عن الشعار الفعلي
            logo_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "ApexFlow.ico"),
                "assets/logo.png",
                "assets/icons/ApexFlow.ico"
            ]

            logo_loaded = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    from PySide6.QtGui import QIcon
                    icon = QIcon(logo_path)
                    pixmap = icon.pixmap(64, 64)
                    logo_label.setPixmap(pixmap)
                    logo_loaded = True
                    break

            if not logo_loaded:
                raise FileNotFoundError(tr("logo_not_found"))

        except Exception as e:
            # fallback للشعار المخصص
            try:
                logo_icon = SVGIconButton("logo", 64)
                logo_pixmap = logo_icon.icon().pixmap(64, 64)
                logo_label.setPixmap(logo_pixmap)
            except:
                logo_label.setText(tr("logo_fallback_text"))
                logo_label.setStyleSheet("font-size: 32px; color: #ff6f00; font-weight: bold;")
        
        # معلومات التطبيق
        info_layout = QVBoxLayout()
        
        # اسم التطبيق
        app_name_label = QLabel(APP_NAME)
        app_name_label.setObjectName("about_app_name")
        info_layout.addWidget(app_name_label)
        
        # الإصدار
        version_label = QLabel(tr("version_label", version=VERSION))
        version_label.setObjectName("about_version")
        info_layout.addWidget(version_label)
        
        # المطور
        author_label = QLabel(tr("author_label_dev", author=APP_AUTHOR))
        author_label.setObjectName("about_author")
        info_layout.addWidget(author_label)
        
        header_layout.addWidget(logo_label)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # خط فاصل
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("about_separator")
        layout.addWidget(separator)
        
        # منطقة النص التفصيلي
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setPlainText(get_about_text())
        layout.addWidget(about_text)
        
        # زر الإغلاق
        close_button = QPushButton(tr("close_button"))
        close_button.setObjectName("about_close_button")
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(100)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

class AppInfoWidget(QWidget):
    """مكون معلومات البرنامج أسفل الشريط الجانبي"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المكون"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(8)
        
        # خط فاصل علوي مع تدرج
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(2)
        separator.setObjectName("theme_separator")

        # تطبيق نمط السمة
        from .theme_manager import apply_theme
        apply_theme(separator, "theme_separator")
        layout.addWidget(separator)
        
        # منطقة الشعار واسم البرنامج
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # الشعار الصغير الفعلي مع تأثير توهج
        logo_button = QPushButton()
        logo_button.setFixedSize(28, 28)

        # تحميل الشعار الفعلي للمكون الصغير
        try:
            logo_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "ApexFlow.ico"),
                "assets/logo.png",
                "assets/icons/ApexFlow.ico"
            ]

            logo_loaded = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    from PySide6.QtGui import QIcon
                    icon = QIcon(logo_path)
                    logo_button.setIcon(icon)
                    logo_button.setIconSize(QSize(24, 24))
                    logo_loaded = True
                    break

            if not logo_loaded:
                # fallback للشعار المخصص
                logo_button = SVGIconButton("logo", 24)

        except Exception as e:
            # fallback للشعار المخصص
            logo_button = SVGIconButton("logo", 24)

        logo_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 2px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 111, 0, 0.1);
                border: 1px solid rgba(255, 111, 0, 0.3);
            }
        """)
        header_layout.addWidget(logo_button)
        
        # اسم البرنامج مع تنسيق نظيف
        app_name = QLabel(APP_NAME)
        app_name.setObjectName("company_name")

        # تطبيق نمط السمة
        from .theme_manager import apply_theme
        apply_theme(app_name, "company_name")
        header_layout.addWidget(app_name)
        
        header_layout.addStretch()
        
        # زر المعلومات
        self.info_button = SVGIconButton("info", 16, tr("about_button_tooltip"))
        self.info_button.set_icon_color("#cccccc")
        self.info_button.clicked.connect(self.show_about_dialog)
        self.info_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 2px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: rgba(255, 111, 0, 0.1);
            }
        """)
        header_layout.addWidget(self.info_button)
        
        layout.addLayout(header_layout)
        
        # معلومات الإصدار
        version_layout = QHBoxLayout()
        version_layout.setContentsMargins(28, 0, 0, 0)  # محاذاة مع النص
        
        version_label = QLabel(tr("version_info_label", version=VERSION))
        version_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 10px;
                background: transparent;
            }
        """)
        version_layout.addWidget(version_label)
        version_layout.addStretch()
        
        layout.addLayout(version_layout)
        
        # معلومات المطور
        author_layout = QHBoxLayout()
        author_layout.setContentsMargins(28, 0, 0, 0)  # محاذاة مع النص
        
        author_label = QLabel(tr("copyright_label", author=APP_AUTHOR))
        author_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 9px;
                background: transparent;
            }
        """)
        author_layout.addWidget(author_label)
        author_layout.addStretch()
        
        layout.addLayout(author_layout)
        
        # تطبيق نمط عام للمكون مع خلفية شفافة أنيقة
        self.setStyleSheet("""
            AppInfoWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 111, 0, 0.02),
                    stop:1 rgba(255, 111, 0, 0.05));
                border: none;
                border-radius: 8px;
                margin: 2px;
            }
        """)
    
    def show_about_dialog(self):
        """عرض نافذة حول البرنامج"""
        dialog = AboutDialog(self)
        dialog.exec()
