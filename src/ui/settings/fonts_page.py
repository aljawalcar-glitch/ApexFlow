# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QSlider,
    QHBoxLayout, QCheckBox
)
from PySide6.QtCore import Qt
from utils.i18n import tr
from managers.theme_manager import make_theme_aware
from ui.widgets.ui_helpers import FocusAwareComboBox

class FontsPage(QWidget):
    def __init__(self, settings_data, parent_ui):
        super().__init__()
        self.settings_data = settings_data
        self.parent_ui = parent_ui
        self.init_ui()
        self.load_initial_settings()

    def load_initial_settings(self):
        """Loads the current settings into the UI elements when the page is created."""
        self.font_size_slider.setValue(self.settings_data.get("font_size", 12))
        self.font_size_label.setText(str(self.settings_data.get("font_size", 12)))
        
        self.title_font_size_slider.setValue(self.settings_data.get("title_font_size", 16))
        self.title_font_size_label.setText(str(self.settings_data.get("title_font_size", 16)))

        self.menu_font_size_slider.setValue(self.settings_data.get("menu_font_size", 12))
        self.menu_font_size_label.setText(str(self.settings_data.get("menu_font_size", 12)))

        font_family = self.settings_data.get("font_family", "Arial")
        font_family_index = self.font_family_combo.findText(font_family)
        if font_family_index != -1:
            self.font_family_combo.setCurrentIndex(font_family_index)

        font_weight = self.settings_data.get("font_weight", "Normal")
        font_weight_index = self.font_weight_combo.findText(font_weight)
        if font_weight_index != -1:
            self.font_weight_combo.setCurrentIndex(font_weight_index)

        self.show_tooltips_check.setChecked(self.settings_data.get("show_tooltips", True))
        self.enable_animations_check.setChecked(self.settings_data.get("enable_animations", True))

        text_direction = self.settings_data.get("text_direction", "LTR")
        text_direction_index = self.text_direction_combo.findText(text_direction)
        if text_direction_index != -1:
            self.text_direction_combo.setCurrentIndex(text_direction_index)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # مجموعة الخطوط الأساسية
        font_group = QGroupBox(tr("primary_font_group"))
        make_theme_aware(font_group, "group_box")
        font_layout = QFormLayout(font_group)
        font_layout.setSpacing(15)

        # حجم الخط
        font_size_layout = QHBoxLayout()
        self.font_size_slider = self.parent_ui.font_size_slider
        make_theme_aware(self.font_size_slider, "slider")
        self.font_size_label = QLabel(str(self.font_size_slider.value()))
        make_theme_aware(self.font_size_label, "value_label")
        self.font_size_slider.valueChanged.connect(
            lambda v: self.font_size_label.setText(str(v))
        )
        font_size_layout.addWidget(self.font_size_slider, 3)
        font_size_layout.addWidget(self.font_size_label, 1)
        font_size_label2 = QLabel(tr("font_size_label"))
        make_theme_aware(font_size_label2, "label")
        font_layout.addRow(font_size_label2, font_size_layout)

        # حجم خط العناوين
        title_font_size_layout = QHBoxLayout()
        self.title_font_size_slider = self.parent_ui.title_font_size_slider
        make_theme_aware(self.title_font_size_slider, "slider")
        self.title_font_size_label = QLabel(str(self.title_font_size_slider.value()))
        make_theme_aware(self.title_font_size_label, "value_label")
        self.title_font_size_slider.valueChanged.connect(
            lambda v: self.title_font_size_label.setText(str(v))
        )
        title_font_size_layout.addWidget(self.title_font_size_slider, 3)
        title_font_size_layout.addWidget(self.title_font_size_label, 1)
        title_font_size_label2 = QLabel(tr("title_font_size_label"))
        make_theme_aware(title_font_size_label2, "label")
        font_layout.addRow(title_font_size_label2, title_font_size_layout)

        # حجم خط القوائم
        menu_font_size_layout = QHBoxLayout()
        self.menu_font_size_slider = self.parent_ui.menu_font_size_slider
        make_theme_aware(self.menu_font_size_slider, "slider")
        self.menu_font_size_label = QLabel(str(self.menu_font_size_slider.value()))
        make_theme_aware(self.menu_font_size_label, "value_label")
        self.menu_font_size_slider.valueChanged.connect(
            lambda v: self.menu_font_size_label.setText(str(v))
        )
        menu_font_size_layout.addWidget(self.menu_font_size_slider, 3)
        menu_font_size_layout.addWidget(self.menu_font_size_label, 1)
        menu_font_size_label2 = QLabel(tr("menu_font_size_label"))
        make_theme_aware(menu_font_size_label2, "label")
        font_layout.addRow(menu_font_size_label2, menu_font_size_layout)

        # نوع الخط
        self.font_family_combo = self.parent_ui.font_family_combo
        make_theme_aware(self.font_family_combo, "combo")
        font_family_label = QLabel(tr("font_family_label"))
        make_theme_aware(font_family_label, "label")
        font_layout.addRow(font_family_label, self.font_family_combo)

        # وزن الخط
        self.font_weight_combo = self.parent_ui.font_weight_combo
        make_theme_aware(self.font_weight_combo, "combo")
        font_weight_label = QLabel(tr("font_weight_label"))
        make_theme_aware(font_weight_label, "label")
        font_layout.addRow(font_weight_label, self.font_weight_combo)

        layout.addWidget(font_group)

        # مجموعة إعدادات النصوص
        text_group = QGroupBox(tr("text_settings_group"))
        make_theme_aware(text_group, "group_box")
        text_layout = QFormLayout(text_group)
        text_layout.setSpacing(15)

        # إظهار التلميحات
        self.show_tooltips_check = self.parent_ui.show_tooltips_check
        text_layout.addRow(self.show_tooltips_check)

        # تمكين الحركات
        self.enable_animations_check = self.parent_ui.enable_animations_check
        text_layout.addRow(self.enable_animations_check)

        # اتجاه النص
        self.text_direction_combo = self.parent_ui.text_direction_combo
        make_theme_aware(self.text_direction_combo, "combo")
        self.text_direction_combo.setEnabled(False)
        self.text_direction_combo.setToolTip(tr("feature_disabled_tooltip"))
        text_direction_label = QLabel(tr("text_direction_label"))
        make_theme_aware(text_direction_label, "label")
        text_layout.addRow(text_direction_label, self.text_direction_combo)

        layout.addWidget(text_group)

        # مجموعة معاينة الخط
        preview_group = QGroupBox(tr("font_preview_group"))
        make_theme_aware(preview_group, "group_box")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setSpacing(15)

        self.font_preview_label = self.parent_ui.font_preview_label
        make_theme_aware(self.font_preview_label, "preview_label")
        self.font_preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.font_preview_label)

        layout.addWidget(preview_group)
        layout.addStretch()
