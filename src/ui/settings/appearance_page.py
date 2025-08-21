# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QHBoxLayout
)
from PySide6.QtCore import Qt
from utils.i18n import tr
from managers.theme_manager import make_theme_aware
from ui.widgets.ui_helpers import FocusAwareComboBox

class AppearancePage(QWidget):
    def __init__(self, settings_data, parent_ui):
        super().__init__()
        self.settings_data = settings_data
        self.parent_ui = parent_ui
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # مجموعة السمة والألوان
        theme_group = QGroupBox(tr("theme_and_colors_group"))
        make_theme_aware(theme_group, "group_box")
        theme_layout = QFormLayout(theme_group)
        theme_layout.setSpacing(15)

        # السمة
        self.theme_combo = self.parent_ui.theme_combo
        make_theme_aware(self.theme_combo, "combo")
        theme_label = QLabel(tr("theme_label"))
        make_theme_aware(theme_label, "label")
        theme_layout.addRow(theme_label, self.theme_combo)

        # اللغة
        self.language_combo = self.parent_ui.language_combo
        make_theme_aware(self.language_combo, "combo")
        language_label = QLabel(tr("language"))
        make_theme_aware(language_label, "label")
        theme_layout.addRow(language_label, self.language_combo)

        # لون التمييز
        accent_layout = QHBoxLayout()
        self.accent_color_input = self.parent_ui.accent_color_input
        self.accent_color_input.setPlaceholderText("#056a51")
        make_theme_aware(self.accent_color_input, "input")

        self.accent_color_btn = QPushButton(tr("choose_color_button"))
        make_theme_aware(self.accent_color_btn, "button")
        self.accent_color_btn.clicked.connect(self.parent_ui.choose_accent_color)

        accent_layout.addWidget(self.accent_color_input, 2)
        accent_layout.addWidget(self.accent_color_btn, 1)
        accent_color_label = QLabel(tr("accent_color_label"))
        make_theme_aware(accent_color_label, "label")
        theme_layout.addRow(accent_color_label, accent_layout)

        # مستوى الشفافية
        transparency_layout = QHBoxLayout()
        transparency_label = QLabel(tr("transparency_level_label"))
        make_theme_aware(transparency_label, "label")
        self.transparency_slider = self.parent_ui.transparency_slider
        self.transparency_slider.setRange(20, 95)
        make_theme_aware(self.transparency_slider, "slider")
        self.transparency_value = QLabel(f"{self.settings_data.get('ui_settings', {}).get('transparency', 80)}%")

        transparency_layout.addWidget(self.transparency_slider, 3)
        transparency_layout.addWidget(self.transparency_value, 1)
        transparency_label2 = QLabel(tr("transparency_label"))
        make_theme_aware(transparency_label2, "label")
        theme_layout.addRow(transparency_label2, transparency_layout)
        self.transparency_slider.valueChanged.connect(lambda v: self.transparency_value.setText(f"{v}%"))

        # حجم العناصر
        self.size_combo = self.parent_ui.size_combo
        make_theme_aware(self.size_combo, "combo")
        element_size_label = QLabel(tr("element_size_label"))
        make_theme_aware(element_size_label, "label")
        theme_layout.addRow(element_size_label, self.size_combo)

        # مستوى التباين
        self.contrast_combo = self.parent_ui.contrast_combo
        make_theme_aware(self.contrast_combo, "combo")
        contrast_label = QLabel(tr("contrast_label"))
        make_theme_aware(contrast_label, "label")
        theme_layout.addRow(contrast_label, self.contrast_combo)

        layout.addWidget(theme_group)
        layout.addStretch()
