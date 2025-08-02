# -*- coding: utf-8 -*-
"""
First Run Setup Dialog
"""
import sys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap
from modules.translator import tr
from .theme_manager import apply_theme_style
from .notification_system import show_success, show_info

class FirstRunDialog(QDialog):
    """Dialog for first-time setup (Language and Theme)."""
    
    settings_chosen = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("مرحباً بك في ApexFlow")
        self.setModal(True)
        self.setFixedSize(450, 350)  # حجم أكبر قليلاً
        self.init_ui()
        apply_theme_style(self, "dialog")

        # إظهار رسالة ترحيب بعد تحميل الحوار
        QTimer.singleShot(500, self.show_welcome_notification)

    def init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Logo and Welcome Message
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # إذا لم يوجد الشعار، عرض نص بديل
            logo_label.setText("ApexFlow")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #056a51;")
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Welcome Message
        welcome_label = QLabel("مرحباً بك! يرجى اختيار إعداداتك المفضلة:")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setWordWrap(True)
        welcome_label.setStyleSheet("font-size: 14px; margin: 10px 0px;")
        main_layout.addWidget(welcome_label)

        # Language Selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("🌍 اللغة:")
        lang_label.setStyleSheet("font-weight: bold;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["🇸🇦 العربية", "🇺🇸 English"])
        self.lang_combo.setCurrentText("🇸🇦 العربية")  # تعيين العربية كافتراضية
        apply_theme_style(self.lang_combo, "combo")
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        main_layout.addLayout(lang_layout)

        # Theme Selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 السمة:")
        theme_label.setStyleSheet("font-weight: bold;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "🔵 أزرق (موصى به)",
            "⚫ داكن",
            "⚪ فاتح",
            "🟢 أخضر",
            "🟣 بنفسجي"
        ])
        self.theme_combo.setCurrentText("🔵 أزرق (موصى به)")  # تعيين السمة الزرقاء كافتراضية
        apply_theme_style(self.theme_combo, "combo")
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        main_layout.addLayout(theme_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("about_separator")
        main_layout.addWidget(separator)

        # Info Message
        info_label = QLabel("يمكنك تغيير هذه الإعدادات لاحقاً من قائمة الإعدادات")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 11px; color: #888; margin: 5px 0px;")
        main_layout.addWidget(info_label)

        # Start Button
        self.start_button = QPushButton("🚀 ابدأ استخدام ApexFlow")
        self.start_button.clicked.connect(self.on_start)
        self.start_button.setStyleSheet("""
            QPushButton {
                background: rgba(5, 106, 81, 0.2);
                border: 1px solid rgba(5, 106, 81, 0.4);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                color: white;
            }
            QPushButton:hover {
                background: rgba(5, 106, 81, 0.3);
                border: 1px solid rgba(5, 106, 81, 0.5);
            }
            QPushButton:pressed {
                background: rgba(5, 106, 81, 0.1);
            }
        """)
        main_layout.addWidget(self.start_button, 0, Qt.AlignCenter)

    def show_welcome_notification(self):
        """إظهار رسالة ترحيب مفيدة"""
        show_info("مرحباً بك في ApexFlow! يمكنك تغيير هذه الإعدادات لاحقاً من قائمة الإعدادات", duration=4000)

    def on_start(self):
        """Handle the start button click."""
        try:
            # استخراج اللغة من النص المختار
            lang_text = self.lang_combo.currentText()
            if "العربية" in lang_text:
                language = "ar"
            else:
                language = "en"

            # استخراج السمة من النص المختار
            theme_text = self.theme_combo.currentText()
            if "أزرق" in theme_text:
                theme = "blue"
            elif "داكن" in theme_text:
                theme = "dark"
            elif "فاتح" in theme_text:
                theme = "light"
            elif "أخضر" in theme_text:
                theme = "green"
            elif "بنفسجي" in theme_text:
                theme = "purple"
            else:
                theme = "blue"  # افتراضي

            # إشعار بحفظ الإعدادات
            show_success("تم حفظ الإعدادات بنجاح! مرحباً بك في ApexFlow", duration=3000)

            # تأخير قصير قبل إرسال الإشارة للسماح بظهور الإشعار
            QTimer.singleShot(1000, lambda: self.emit_settings_and_close(language, theme))

        except Exception as e:
            # في حالة حدوث خطأ، استخدم الإعدادات الافتراضية
            self.emit_settings_and_close("ar", "blue")

    def emit_settings_and_close(self, language, theme):
        """إرسال الإعدادات وإغلاق الحوار"""
        self.settings_chosen.emit(language, theme)
        self.accept()
