# -*- coding: utf-8 -*-
"""
First Run Setup Dialog
"""
import sys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QFont
from modules.translator import tr, set_language
from .theme_manager import apply_theme_style, set_theme
from .notification_system import show_success, show_info

class FirstRunDialog(QDialog):
    """Dialog for first-time setup (Language and Theme)."""
    
    settings_chosen = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("welcome_to_apexflow"))
        self.setModal(True)
        self.setFixedSize(700, 500)  # حجم أكبر

        # إضافة أيقونة النافذة
        self.setWindowIcon(self.get_app_icon())

        # متغيرات لتخزين الإعدادات المختارة
        self.selected_language = "en"
        self.selected_theme = "blue"

        self.init_ui()
        apply_theme_style(self, "dialog")

        # إظهار رسالة ترحيب بعد تحميل الحوار
        QTimer.singleShot(500, self.show_welcome_notification)

    def get_app_icon(self):
        """الحصول على أيقونة التطبيق"""
        from PySide6.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def init_ui(self):
        """Initialize the UI components."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        # قسم الشعار والمعلومات (على اليمين)
        right_section = QVBoxLayout()
        right_section.setSpacing(15)

        # الشعار
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            # استخدام الشعار بدقة كاملة
            pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # إذا لم يوجد الشعار، عرض نص بديل
            self.logo_label.setText("ApexFlow")
            self.logo_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        self.logo_label.setAlignment(Qt.AlignCenter)
        right_section.addWidget(self.logo_label)

        # معلومات الشركة والإصدار
        company_label = QLabel("ApexFlow Solutions")
        company_label.setObjectName("company_label")
        company_label.setAlignment(Qt.AlignCenter)
        company_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_section.addWidget(company_label)

        version_label = QLabel("Version 1.0.0")
        version_label.setObjectName("version_label")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 14px;")
        right_section.addWidget(version_label)

        # معلومات حول التطبيق
        about_frame = QFrame()
        about_frame.setFrameShape(QFrame.StyledPanel)
        about_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border-radius: 8px;")
        about_layout = QVBoxLayout(about_frame)

        about_title = QLabel(tr("about_apexflow"))
        about_title.setObjectName("about_title")
        about_title.setAlignment(Qt.AlignCenter)
        about_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        about_layout.addWidget(about_title)

        about_text = QLabel(tr("apexflow_description"))
        about_text.setObjectName("about_text")
        about_text.setAlignment(Qt.AlignCenter)
        about_text.setWordWrap(True)
        about_text.setStyleSheet("font-size: 12px;")
        about_layout.addWidget(about_text)

        right_section.addWidget(about_frame)
        right_section.addStretch()

        # قسم الإعدادات (على اليسار)
        left_section = QVBoxLayout()
        left_section.setSpacing(20)

        # عنوان الإعدادات
        settings_title = QLabel(tr("initial_settings"))
        settings_title.setObjectName("settings_title")
        settings_title.setAlignment(Qt.AlignCenter)
        settings_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        left_section.addWidget(settings_title)

        # قسم اللغة
        lang_frame = QFrame()
        lang_frame.setFrameShape(QFrame.StyledPanel)
        lang_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border-radius: 8px;")
        lang_layout = QVBoxLayout(lang_frame)

        lang_title = QLabel(tr("select_language"))
        lang_title.setObjectName("lang_title")
        lang_title.setAlignment(Qt.AlignCenter)
        lang_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        lang_layout.addWidget(lang_title)

        # أزرار اللغة
        lang_buttons_layout = QHBoxLayout()

        self.en_button = QPushButton("🇺🇸 English")
        self.en_button.setCheckable(True)
        self.en_button.setChecked(True)  # الإنجليزية كافتراضية
        self.en_button.clicked.connect(lambda: self.change_language("en"))
        self.en_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #2980b9;
                border: 2px solid #ffffff;
            }
        """)
        lang_buttons_layout.addWidget(self.en_button)

        self.ar_button = QPushButton("🇸🇦 العربية")
        self.ar_button.setCheckable(True)
        self.ar_button.clicked.connect(lambda: self.change_language("ar"))
        self.ar_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #2980b9;
                border: 2px solid #ffffff;
            }
        """)
        lang_buttons_layout.addWidget(self.ar_button)

        lang_layout.addLayout(lang_buttons_layout)
        left_section.addWidget(lang_frame)

        # قسم السمات
        theme_frame = QFrame()
        theme_frame.setFrameShape(QFrame.StyledPanel)
        theme_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border-radius: 8px;")
        theme_layout = QVBoxLayout(theme_frame)

        theme_title = QLabel(tr("select_theme"))
        theme_title.setObjectName("theme_title")
        theme_title.setAlignment(Qt.AlignCenter)
        theme_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        theme_layout.addWidget(theme_title)

        # أزرار السمات
        themes_grid_layout = QVBoxLayout()

        # صف أول من الأزرار
        first_row_layout = QHBoxLayout()

        self.blue_button = QPushButton("🔵 " + tr("blue_theme"))
        self.blue_button.setCheckable(True)
        self.blue_button.setChecked(True)  # الأزرق كافتراضي
        self.blue_button.clicked.connect(lambda: self.change_theme("blue"))
        self.blue_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                border: 2px solid #ffffff;
            }
        """)
        first_row_layout.addWidget(self.blue_button)

        self.dark_button = QPushButton("⚫ " + tr("dark_theme"))
        self.dark_button.setCheckable(True)
        self.dark_button.clicked.connect(lambda: self.change_theme("dark"))
        self.dark_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                border: 2px solid #ffffff;
            }
        """)
        first_row_layout.addWidget(self.dark_button)

        themes_grid_layout.addLayout(first_row_layout)

        # صف ثاني من الأزرار
        second_row_layout = QHBoxLayout()

        self.light_button = QPushButton("⚪ " + tr("light_theme"))
        self.light_button.setCheckable(True)
        self.light_button.clicked.connect(lambda: self.change_theme("light"))
        self.light_button.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                border: 2px solid #3498db;
            }
        """)
        second_row_layout.addWidget(self.light_button)

        self.green_button = QPushButton("🟢 " + tr("green_theme"))
        self.green_button.setCheckable(True)
        self.green_button.clicked.connect(lambda: self.change_theme("green"))
        self.green_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                border: 2px solid #ffffff;
            }
        """)
        second_row_layout.addWidget(self.green_button)

        themes_grid_layout.addLayout(second_row_layout)

        # صف ثالث من الأزرار
        third_row_layout = QHBoxLayout()

        self.purple_button = QPushButton("🟣 " + tr("purple_theme"))
        self.purple_button.setCheckable(True)
        self.purple_button.clicked.connect(lambda: self.change_theme("purple"))
        self.purple_button.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                border: 2px solid #ffffff;
            }
        """)
        third_row_layout.addWidget(self.purple_button)

        themes_grid_layout.addLayout(third_row_layout)

        theme_layout.addLayout(themes_grid_layout)
        left_section.addWidget(theme_frame)

        # زر البدء في الزاوية اليمنى السفلية
        left_section.addStretch()

        finish_layout = QHBoxLayout()
        finish_layout.addStretch()

        self.finish_button = QPushButton(tr("finish"))
        self.finish_button.setObjectName("finish_button")
        self.finish_button.clicked.connect(self.on_start)
        self.finish_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        finish_layout.addWidget(self.finish_button)

        left_section.addLayout(finish_layout)

        # إضافة القسمين للتخطيط الرئيسي
        main_layout.addLayout(left_section, 1)
        main_layout.addLayout(right_section, 1)

    def show_welcome_notification(self):
        """إظهار رسالة ترحيب مفيدة"""
        show_info(tr("welcome_to_apexflow_info"), duration=4000)

    def change_language(self, lang):
        """تغيير لغة التطبيق"""
        self.selected_language = lang
        set_language(lang)

        # تحديث حالة الأزرار
        if lang == "en":
            self.en_button.setChecked(True)
            self.ar_button.setChecked(False)
        else:
            self.en_button.setChecked(False)
            self.ar_button.setChecked(True)

        # إعادة تحميل الواجهة باللغة الجديدة
        self.reload_ui_texts()

        # إشعار بتغيير اللغة
        show_success(tr("language_changed"), duration=2000)

    def change_theme(self, theme):
        """تغيير سمة التطبيق"""
        self.selected_theme = theme
        set_theme(theme)

        # تحديث حالة الأزرار
        self.blue_button.setChecked(theme == "blue")
        self.dark_button.setChecked(theme == "dark")
        self.light_button.setChecked(theme == "light")
        self.green_button.setChecked(theme == "green")
        self.purple_button.setChecked(theme == "purple")

        # إشعار بتغيير السمة
        show_success(tr("theme_changed"), duration=2000)

    def reload_ui_texts(self):
        """إعادة تحميل نصوص الواجهة بعد تغيير اللغة"""
        self.setWindowTitle(tr("welcome_to_apexflow"))

        # تحديث النصوص في القسم الأيمن
        company_label = self.findChild(QLabel, "company_label")
        if company_label:
            company_label.setText("ApexFlow Solutions")

        version_label = self.findChild(QLabel, "version_label")
        if version_label:
            version_label.setText("Version 1.0.0")

        about_title = self.findChild(QLabel, "about_title")
        if about_title:
            about_title.setText(tr("about_apexflow"))

        about_text = self.findChild(QLabel, "about_text")
        if about_text:
            about_text.setText(tr("apexflow_description"))

        # تحديث النصوص في القسم الأيسر
        settings_title = self.findChild(QLabel, "settings_title")
        if settings_title:
            settings_title.setText(tr("initial_settings"))

        lang_title = self.findChild(QLabel, "lang_title")
        if lang_title:
            lang_title.setText(tr("select_language"))

        theme_title = self.findChild(QLabel, "theme_title")
        if theme_title:
            theme_title.setText(tr("select_theme"))

        # تحديث نصوص أزرار السمات
        self.blue_button.setText("🔵 " + tr("blue_theme"))
        self.dark_button.setText("⚫ " + tr("dark_theme"))
        self.light_button.setText("⚪ " + tr("light_theme"))
        self.green_button.setText("🟢 " + tr("green_theme"))
        self.purple_button.setText("🟣 " + tr("purple_theme"))

        # تحديث نص زر الإنهاء
        self.finish_button.setText(tr("finish_button"))

    def on_start(self):
        """Handle the start button click."""
        try:
            # استخدام الإعدادات المختارة مسبقاً
            language = self.selected_language
            theme = self.selected_theme

            # إشعار بحفظ الإعدادات
            show_success(tr("settings_saved_successfully"), duration=3000)

            # تأخير قصير قبل إرسال الإشارة للسماح بظهور الإشعار
            QTimer.singleShot(1000, lambda: self.emit_settings_and_close(language, theme))

        except Exception as e:
            # في حالة حدوث خطأ، استخدم الإعدادات الافتراضية
            self.emit_settings_and_close("en", "blue")

    def emit_settings_and_close(self, language, theme):
        """إرسال الإعدادات وإغلاق الحوار"""
        self.settings_chosen.emit(language, theme)
        self.accept()
