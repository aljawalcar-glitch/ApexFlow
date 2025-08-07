import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QSpinBox, QComboBox, QFormLayout
)
from PySide6.QtCore import Qt
from .theme_manager import apply_theme_style
from modules.translator import tr

class NotificationSettingsWidget(QWidget):
    """Widget for configuring notification settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface for notification settings."""
        from PySide6.QtWidgets import QFrame
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.notification_checkboxes = {}

        # --- General Settings ---
        general_title = QLabel(tr("notification_general_settings"))
        apply_theme_style(general_title, "title_text")
        layout.addWidget(general_title)

        general_frame = QFrame()
        general_layout = QHBoxLayout(general_frame)
        general_layout.setContentsMargins(10, 5, 10, 5)
        general_layout.setSpacing(15)
        apply_theme_style(general_frame, "hlayout")

        self.enable_notifications = QCheckBox(tr("enable_notifications"))
        self.enable_notifications.setLayoutDirection(Qt.RightToLeft)
        apply_theme_style(self.enable_notifications, "checkbox")
        general_layout.addWidget(self.enable_notifications)
        
        general_layout.addStretch()

        notification_sound_label = QLabel(tr("notification_sound"))
        apply_theme_style(notification_sound_label, "label")
        self.notification_sound = QComboBox()
        self.notification_sound.addItems([tr("notification_sound_default"), tr("notification_sound_none")])
        apply_theme_style(self.notification_sound, "combo")
        general_layout.addWidget(notification_sound_label)
        general_layout.addWidget(self.notification_sound)

        notification_duration_label = QLabel(tr("notification_duration"))
        apply_theme_style(notification_duration_label, "label")
        self.notification_duration = QSpinBox()
        self.notification_duration.setRange(1, 10)
        self.notification_duration.setSuffix(f" {tr('seconds_suffix')}")
        apply_theme_style(self.notification_duration, "spin_box")
        general_layout.addWidget(notification_duration_label)
        general_layout.addWidget(self.notification_duration)
        
        layout.addWidget(general_frame)

        # --- Visibility Settings ---
        visibility_title = QLabel(tr("notification_visibility_settings"))
        apply_theme_style(visibility_title, "title_text")
        layout.addWidget(visibility_title)

        visibility_frame = QFrame()
        visibility_layout = QHBoxLayout(visibility_frame)
        visibility_layout.setContentsMargins(10, 5, 10, 5)
        visibility_layout.setSpacing(15)
        apply_theme_style(visibility_frame, "hlayout")

        notification_types = ["success", "warning", "error", "info"]
        for notif_type in notification_types:
            checkbox = QCheckBox(tr(f"show_{notif_type}_notifications"))
            checkbox.setLayoutDirection(Qt.RightToLeft)
            apply_theme_style(checkbox, "checkbox")
            visibility_layout.addWidget(checkbox)
            self.notification_checkboxes[notif_type] = checkbox
        visibility_layout.addStretch()
        layout.addWidget(visibility_frame)

        # --- Storage Settings ---
        memory_title = QLabel(tr("notification_storage_settings"))
        apply_theme_style(memory_title, "title_text")
        layout.addWidget(memory_title)

        memory_frame = QFrame()
        memory_layout = QHBoxLayout(memory_frame)
        memory_layout.setContentsMargins(10, 5, 10, 5)
        apply_theme_style(memory_frame, "hlayout")
        
        memory_checkbox = QCheckBox(tr("do_not_save_notifications"))
        memory_checkbox.setLayoutDirection(Qt.RightToLeft)
        apply_theme_style(memory_checkbox, "checkbox")
        memory_layout.addWidget(memory_checkbox)
        self.notification_checkboxes["do_not_save"] = memory_checkbox
        memory_layout.addStretch()
        layout.addWidget(memory_frame)

        # Save and Cancel Buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(15)
        apply_theme_style(buttons_frame, "hlayout")
        save_button = QPushButton(tr("save_all_changes_button"))
        apply_theme_style(save_button, "button")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton(tr("cancel_changes_button"))
        apply_theme_style(cancel_button, "button")
        cancel_button.clicked.connect(self.load_settings)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        layout.addStretch()

    def load_settings(self):
        """Load notification settings and update the UI."""
        try:
            from ui.notification_system import global_notification_manager
            current_settings = global_notification_manager.get_notification_settings()

            for notif_type, checkbox in self.notification_checkboxes.items():
                checkbox.setChecked(current_settings.get(notif_type, True if notif_type != "do_not_save" else False))
            
            self.enable_notifications.setChecked(current_settings.get("enabled", True))
            self.notification_sound.setCurrentText(current_settings.get("sound", tr("notification_sound_default")))
            self.notification_duration.setValue(current_settings.get("duration", 3))

        except Exception as e:
            print(f"Error loading notification settings: {e}")

    def save_settings(self):
        """Save the current notification settings."""
        try:
            from ui.notification_system import global_notification_manager
            new_settings = {}
            for notif_type, checkbox in self.notification_checkboxes.items():
                new_settings[notif_type] = checkbox.isChecked()

            new_settings["enabled"] = self.enable_notifications.isChecked()
            new_settings["sound"] = self.notification_sound.currentText()
            new_settings["duration"] = self.notification_duration.value()

            global_notification_manager.update_notification_settings(new_settings)
            global_notification_manager.show_notification(
                tr("notification_settings_saved"), "success"
            )
        except Exception as e:
            from ui.notification_system import global_notification_manager
            global_notification_manager.show_notification(
                tr("error_saving_notification_settings", error=str(e)), "error"
            )
