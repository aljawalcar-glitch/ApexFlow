# -*- coding: utf-8 -*-
"""
First Run Setup Dialog
"""
import sys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from modules.translator import tr
from .theme_manager import apply_theme_style

class FirstRunDialog(QDialog):
    """Dialog for first-time setup (Language and Theme)."""
    
    settings_chosen = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to ApexFlow")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.init_ui()
        apply_theme_style(self, "dialog")

    def init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Language Selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel(tr("language", "Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["العربية", "English"])
        apply_theme_style(self.lang_combo, "combo")
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        main_layout.addLayout(lang_layout)

        # Theme Selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel(tr("theme_label", "Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        apply_theme_style(self.theme_combo, "combo")
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        main_layout.addLayout(theme_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("about_separator")
        main_layout.addWidget(separator)

        # Start Button
        self.start_button = QPushButton(tr("next_step", "Start"))
        self.start_button.clicked.connect(self.on_start)
        apply_theme_style(self.start_button, "button")
        main_layout.addWidget(self.start_button, 0, Qt.AlignCenter)

    def on_start(self):
        """Handle the start button click."""
        language = "ar" if self.lang_combo.currentText() == "العربية" else "en"
        theme = self.theme_combo.currentText()
        self.settings_chosen.emit(language, theme)
        self.accept()
