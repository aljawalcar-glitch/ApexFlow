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
from src.managers.theme_manager import make_theme_aware
from src.utils.translator import tr

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
        make_theme_aware(general_title, "title_text")
        layout.addWidget(general_title)

        general_frame = QFrame()
        general_layout = QHBoxLayout(general_frame)
        general_layout.setContentsMargins(10, 5, 10, 5)
        general_layout.setSpacing(15)
        make_theme_aware(general_frame, "hlayout")

        from src.ui.widgets.toggle_switch import ToggleSwitch
        
        enable_label = QLabel(tr("enable_notifications"))
        make_theme_aware(enable_label, "label")
        self.enable_notifications = ToggleSwitch()
        self.enable_notifications.setFixedSize(32, 16)  # تصغير الحجم
        general_layout.addWidget(enable_label)
        general_layout.addWidget(self.enable_notifications)
        
        general_layout.addStretch()
        general_layout.addStretch()

        notification_sound_label = QLabel(tr("notification_sound"))
        make_theme_aware(notification_sound_label, "label")
        self.notification_sound = QComboBox()
        self.notification_sound.addItems([tr("notification_sound_default"), tr("notification_sound_none")])
        make_theme_aware(self.notification_sound, "combo")
        general_layout.addWidget(notification_sound_label)
        general_layout.addWidget(self.notification_sound)
        general_layout.addWidget(self.notification_sound)

        notification_duration_label = QLabel(tr("notification_duration"))
        make_theme_aware(notification_duration_label, "label")
        self.notification_duration = QSpinBox()
        self.notification_duration.setRange(1, 10)
        self.notification_duration.setSuffix(f" {tr('seconds_suffix')}")
        make_theme_aware(self.notification_duration, "spin_box")
        general_layout.addWidget(notification_duration_label)
        general_layout.addWidget(self.notification_duration)
        
        layout.addWidget(general_frame)

        # --- Visibility Settings ---
        visibility_title = QLabel(tr("notification_visibility_settings"))
        make_theme_aware(visibility_title, "title_text")
        layout.addWidget(visibility_title)

        visibility_frame = QFrame()
        visibility_layout = QHBoxLayout(visibility_frame)
        visibility_layout.setContentsMargins(10, 5, 10, 5)
        visibility_layout.setSpacing(15)
        make_theme_aware(visibility_frame, "hlayout")

        notification_types = ["success", "warning", "error", "info"]
        for notif_type in notification_types:
            type_layout = QVBoxLayout()
            label = QLabel(tr(f"show_{notif_type}_notifications"))
            make_theme_aware(label, "label")
            toggle = ToggleSwitch()
            toggle.setFixedSize(32, 16)  # تصغير الحجم
            type_layout.addWidget(label)
            type_layout.addWidget(toggle)
            visibility_layout.addLayout(type_layout)
            self.notification_checkboxes[notif_type] = toggle
        visibility_layout.addStretch()
        layout.addWidget(visibility_frame)

        # --- Storage Settings ---
        memory_title = QLabel(tr("notification_storage_settings"))
        make_theme_aware(memory_title, "title_text")
        layout.addWidget(memory_title)

        memory_frame = QFrame()
        memory_frame = QFrame()
        memory_layout = QHBoxLayout(memory_frame)
        memory_layout.setContentsMargins(10, 5, 10, 5)
        make_theme_aware(memory_frame, "hlayout")
        
        memory_label = QLabel(tr("do_not_save_notifications"))
        make_theme_aware(memory_label, "label")
        memory_toggle = ToggleSwitch()
        memory_toggle.setFixedSize(32, 16)  # تصغير الحجم
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(memory_toggle)
        self.notification_checkboxes["do_not_save"] = memory_toggle
        memory_layout.addStretch()
        layout.addWidget(memory_frame)

    def load_settings(self):
        """Load notification settings and update the UI."""
        try:
            from src.managers.notification_system import global_notification_manager
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
            from src.managers.notification_system import global_notification_manager
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
            from src.managers.notification_system import global_notification_manager
            global_notification_manager.show_notification(
                tr("error_saving_notification_settings", error=str(e)), "error"
            )

    def clear_notifications(self):
        """مسح جميع الإشعارات."""
        try:
            from src.managers.notification_system import global_notification_manager
            global_notification_manager.clear_all_notifications()
            print(tr("notifications_cleared"))
        except Exception as e:
            print(f"Error clearing notifications: {e}")
