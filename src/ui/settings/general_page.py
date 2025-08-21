# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox, QFrame, QLabel
)
from utils.i18n import tr
from managers.theme_manager import make_theme_aware

class GeneralPage(QWidget):
    def __init__(self, settings_data, parent_ui):
        super().__init__()
        self.settings_data = settings_data
        self.parent_ui = parent_ui
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # مجموعة إعدادات البدء
        startup_group = QGroupBox(tr("startup_settings_group"))
        make_theme_aware(startup_group, "group_box")
        startup_layout = QVBoxLayout(startup_group)
        startup_layout.setSpacing(10)

        self.sequential_drops_checkbox = self.parent_ui.sequential_drops_checkbox
        startup_layout.addWidget(self.sequential_drops_checkbox)

        self.disable_welcome_checkbox = self.parent_ui.disable_welcome_checkbox
        startup_layout.addWidget(self.disable_welcome_checkbox)

        self.remember_state_checkbox = self.parent_ui.remember_state_checkbox
        startup_layout.addWidget(self.remember_state_checkbox)

        self.reset_to_defaults_checkbox = self.parent_ui.reset_to_defaults_checkbox
        startup_layout.addWidget(self.reset_to_defaults_checkbox)

        layout.addWidget(startup_group)

        # مجموعة إعدادات الإشعارات
        notifications_group = QGroupBox(tr("notifications_settings_group"))
        make_theme_aware(notifications_group, "group_box")
        notifications_layout = QVBoxLayout(notifications_group)
        notifications_layout.setSpacing(10)

        self.show_success_notifications_checkbox = self.parent_ui.show_success_notifications_checkbox
        notifications_layout.addWidget(self.show_success_notifications_checkbox)

        self.show_warning_notifications_checkbox = self.parent_ui.show_warning_notifications_checkbox
        notifications_layout.addWidget(self.show_warning_notifications_checkbox)

        self.show_error_notifications_checkbox = self.parent_ui.show_error_notifications_checkbox
        notifications_layout.addWidget(self.show_error_notifications_checkbox)

        self.show_info_notifications_checkbox = self.parent_ui.show_info_notifications_checkbox
        notifications_layout.addWidget(self.show_info_notifications_checkbox)
        
        self.do_not_save_notifications_checkbox = self.parent_ui.do_not_save_notifications_checkbox
        notifications_layout.addWidget(self.do_not_save_notifications_checkbox)

        layout.addWidget(notifications_group)
        layout.addStretch()
