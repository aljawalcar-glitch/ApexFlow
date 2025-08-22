# -*- coding: utf-8 -*-
"""
مكون معلومات البرنامج
App Info Widget Component
"""

import sys
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QDialog, QTextEdit, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize, QEvent, QByteArray
from PySide6.QtGui import QFont, QPixmap, QPainter, QIcon, QFontMetrics, QPainterPath, QColor
from .svg_icon_button import SVGIconButton
from managers.theme_manager import make_theme_aware, global_theme_manager
try:
    from PySide6.QtSvgWidgets import QSvgWidget
    HAS_SVG = True
except Exception:
    HAS_SVG = False
from utils.i18n import tr
from utils.update_checker import check_for_updates
from PySide6.QtCore import QTimer
from config.version import (
    VERSION, APP_NAME, APP_AUTHOR_AR, APP_AUTHOR_EN, get_about_text
)

class CustomLabel(QLabel):
    """
    A custom QLabel that dynamically recalculates its minimum size hint
    whenever its style is changed. This ensures that even if the font
    changes during a resize or theme update, the label will request
    the correct amount of space to prevent text truncation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def event(self, e):
        # When the style is changed (e.g., stylesheet re-applied),
        # we need to invalidate the old size hint.
        if e.type() == QEvent.StyleChange:
            self.updateGeometry()
        return super().event(e)

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        required_width = fm.horizontalAdvance(self.text())
        return QSize(required_width + 10, super().sizeHint().height())

class WordmarkVector(QWidget):
    """ يرسم نص كـ Vector Path — ما بيتقص وبيكبر بنعومة """
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self._text = text
        self._color = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

    def setText(self, text):
        self._text = text
        self.update()

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        return QSize(fm.horizontalAdvance(self._text) + 16, fm.height() + 8)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        path = QPainterPath()
        f = self.font()
        f.setKerning(True)
        fm = QFontMetrics(f)
        baseline = (self.height() + fm.ascent() - fm.descent()) / 2
        path.addText(0, baseline, f, self._text)
        br = path.boundingRect()
        if br.width() > 0 and br.height() > 0:
            margin = 6
            sx = (self.width() - margin*2) / br.width()
            sy = (self.height() - margin*2) / br.height()
            s = min(sx, sy)
            p.translate(margin - br.x()*s, margin - br.y()*s)
            p.scale(s, s)
        color = self.palette().highlight().color()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawPath(path)
        p.end()

class AboutDialog(QDialog):
    """نافذة حول البرنامج"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        make_theme_aware(self, "dialog_about")
        self.settings = settings
        self.setWindowTitle(tr("about_dialog_title", app_name=APP_NAME))
        self.setFixedSize(550, 450)
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setFixedSize(64, 64)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setObjectName("about_logo_label")
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
                    icon = QIcon(logo_path)
                    pixmap = icon.pixmap(64, 64)
                    logo_label.setPixmap(pixmap)
                    logo_loaded = True
                    break
            if not logo_loaded:
                raise FileNotFoundError(tr("logo_not_found"))
        except Exception:
            try:
                logo_icon = SVGIconButton("logo", 64)
                logo_pixmap = logo_icon.icon().pixmap(64, 64)
                logo_label.setPixmap(logo_pixmap)
            except:
                logo_label.setText(tr("logo_fallback_text"))
                logo_label.setStyleSheet("font-size: 32px; color: #ff6f00; font-weight: bold;")
        
        make_theme_aware(logo_label, "about_logo_label")
        
        info_layout = QVBoxLayout()
        app_name_label = QLabel(APP_NAME)
        app_name_label.setObjectName("about_app_name")
        make_theme_aware(app_name_label, "about_app_name")
        info_layout.addWidget(app_name_label)
        version_label = QLabel(tr("version_label", version=VERSION))
        version_label.setObjectName("about_version")
        make_theme_aware(version_label, "about_version")
        info_layout.addWidget(version_label)
        from src.managers.language_manager import language_manager
        author = APP_AUTHOR_AR if language_manager.get_language() == "ar" else APP_AUTHOR_EN
        author_label = QLabel(tr("author_label", author=author))
        author_label.setObjectName("about_author")
        make_theme_aware(author_label, "about_author")
        info_layout.addWidget(author_label)
        header_layout.addWidget(logo_label)
        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("about_separator")
        make_theme_aware(separator, "about_separator")
        layout.addWidget(separator)
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setMarkdown(get_about_text())
        about_text.setObjectName("about_text")
        make_theme_aware(about_text, "about_text")
        layout.addWidget(about_text)
        button_layout = QHBoxLayout()
        self.update_button = QPushButton(tr("check_for_updates_button"))
        self.update_button.setObjectName("about_update_button")
        make_theme_aware(self.update_button, "about_update_button")
        self.update_button.clicked.connect(self.manual_check_for_updates)
        button_layout.addWidget(self.update_button)
        button_layout.addStretch()
        close_button = QPushButton(tr("close_button"))
        close_button.setObjectName("about_close_button")
        make_theme_aware(close_button, "about_close_button")
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(100)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def manual_check_for_updates(self):
        self.update_button.setText(tr("checking_for_updates_message"))
        self.update_button.setEnabled(False)
        QTimer.singleShot(100, self._perform_update_check)

    def _perform_update_check(self):
        is_available, new_version = check_for_updates()
        
        # إنشاء QMessageBox مخصص
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(tr("update_check"))
        
        # تطبيق ألوان السمة
        colors = global_theme_manager.get_current_colors()
        accent_color = global_theme_manager.current_accent
        
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {colors.get('surface', '#2d3748')};
            }}
            QLabel {{
                color: {colors.get('text_body', '#ffffff')};
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {global_theme_manager.get_color('accent_hover') if 'accent_hover' in colors else '#067a61'};
            }}
        """)

        if is_available:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(tr("new_version_available", latest_version=new_version))
        else:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(tr("app_is_up_to_date"))
            
        msg_box.exec()

        self.update_button.setText(tr("check_for_updates_button"))
        self.update_button.setEnabled(True)

class AppInfoWidget(QWidget):
    """مكون معلومات البرنامج أسفل الشريط الجانبي"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.update_available = False
        self.setup_ui()
        QTimer.singleShot(2000, self.initial_update_check)
    
    def initial_update_check(self):
        self.update_available, _ = check_for_updates()
        if self.update_available:
            self.show_update_indicator(True)

    def show_update_indicator(self, show=True):
        self.info_button.setProperty("update_available", show)
        self.info_button.style().unpolish(self.info_button)
        self.info_button.style().polish(self.info_button)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(8)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(2)
        separator.setObjectName("theme_separator")
        make_theme_aware(separator, "theme_separator")
        layout.addWidget(separator)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        logo_button = QPushButton()
        logo_button.setFixedSize(28, 28)
        make_theme_aware(logo_button, "icon_button")
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
                    icon = QIcon(logo_path)
                    logo_button.setIcon(icon)
                    logo_button.setIconSize(QSize(24, 24))
                    logo_loaded = True
                    break
            if not logo_loaded:
                logo_button = SVGIconButton("logo", 24)
        except Exception:
            logo_button = SVGIconButton("logo", 24)

        self.wordmark_widget = None
        wordmark_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "wordmark.svg"),
            "assets/wordmark.svg"
        ]
        svg_file = next((p for p in wordmark_paths if os.path.exists(p)), None)

        if HAS_SVG and svg_file:
            self.wordmark_widget = QSvgWidget(svg_file)
            self.wordmark_widget.setObjectName("company_name_svg")
            self.wordmark_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.wordmark_widget.setMinimumWidth(0)
            make_theme_aware(self.wordmark_widget, "company_name")
        else:
            self.wordmark_widget = WordmarkVector(APP_NAME, self)
            self.wordmark_widget.setObjectName("company_name_svg")
            make_theme_aware(self.wordmark_widget, "company_name")

        self.info_button = SVGIconButton("info", 16, tr("about_button_tooltip"))
        self.info_button.clicked.connect(self.show_about_dialog)
        self.info_button.setObjectName("about_info_button")
        self.info_button.setProperty("icon_name", "info")
        self.info_button.setProperty("icon_size", 16)
        make_theme_aware(self.info_button, "about_info_button")
        header_layout.addWidget(logo_button, 0, Qt.AlignLeft)
        header_layout.addWidget(self.wordmark_widget, 1)
        header_layout.addWidget(self.info_button, 0, Qt.AlignRight)
        layout.addLayout(header_layout)
        dummy_label = QLabel("")
        dummy_label.setVisible(False)
        layout.addWidget(dummy_label)
        self.version_layout = QHBoxLayout()
        self.version_layout.setObjectName("version_layout")
        self.version_layout.setContentsMargins(28, 0, 0, 0)
        version_label = CustomLabel(tr("version_info_label", version=VERSION))
        version_label.setObjectName("version_label")
        make_theme_aware(version_label, "version_label")
        self.version_layout.addWidget(version_label)
        layout.addLayout(self.version_layout)
        self.author_layout = QHBoxLayout()
        self.author_layout.setObjectName("author_layout")
        self.author_layout.setContentsMargins(28, 0, 0, 0)
        from src.managers.language_manager import language_manager
        author = APP_AUTHOR_AR if language_manager.get_language() == "ar" else APP_AUTHOR_EN
        author_label = CustomLabel(tr("copyright_label", author=author))
        author_label.setObjectName("author_label")
        make_theme_aware(author_label, "author_label")
        self.author_layout.addWidget(author_label)
        layout.addLayout(self.author_layout)
        make_theme_aware(self, "app_info_widget")
    
    def show_about_dialog(self):
        dialog = AboutDialog(self.settings, self)
        dialog.exec()

    def update_language(self):
        """Updates language-dependent text like the author's name."""
        from src.managers.language_manager import language_manager
        author = APP_AUTHOR_AR if language_manager.get_language() == "ar" else APP_AUTHOR_EN
        
        author_label = self.findChild(CustomLabel, "author_label")
        if author_label:
            author_label.setText(tr("copyright_label", author=author))
        
        version_label = self.findChild(CustomLabel, "version_label")
        if version_label:
            version_label.setText(tr("version_info_label", version=VERSION))
            
        self.info_button.setToolTip(tr("about_button_tooltip"))

        # Also need to update the wordmark if it's the vector version
        if isinstance(self.wordmark_widget, WordmarkVector):
            self.wordmark_widget.setText(APP_NAME)
