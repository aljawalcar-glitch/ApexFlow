# -*- coding: utf-8 -*-
"""
نظام الإشعارات المدمج الجديد
New Integrated Notification System
"""
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, 
                               QFrame, QStackedWidget, QListWidget, QListWidgetItem,
                               QDialog, QDialogButtonBox, QApplication, QCheckBox)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal, QSize
from PySide6.QtGui import QIcon, QColor, QPainter, QPainterPath
import os
from modules.logger import debug
from modules.translator import tr
from .theme_manager import apply_theme, global_theme_manager
from modules.settings import get_setting, set_setting

# --- 1. Notification Bar (The "Toast") ---

class NotificationBar(QFrame):
    """
    شريط إشعار يظهر في الجزء السفلي من النافذة الرئيسية.
    A notification bar that appears at the bottom of the main window.
    """
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setObjectName("NotificationBar")
        self.setFixedHeight(0) # Start hidden
        self.setFrameShape(QFrame.NoFrame)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(10)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)

        # Message
        self.message_label = QLabel()
        apply_theme(self.message_label, "notification_text")
        self.message_label.setStyleSheet("background-color: transparent; border: none;")
        layout.addWidget(self.message_label, 1)

        # History Button
        self.history_button = QPushButton()
        apply_theme(self.history_button, "notification_history_button")
        self.history_button.setFixedSize(28, 28)
        self.history_button.setIconSize(QSize(18, 18))
        # استخدام إعدادات التلميحات
        from modules.settings import should_show_tooltips
        if should_show_tooltips():
            self.history_button.setToolTip(tr("notification_history_tooltip"))
        layout.addWidget(self.history_button)

        # Close Button
        self.close_button = QPushButton("✕")
        apply_theme(self.close_button, "notification_close_button")
        self.close_button.setFixedSize(28, 28)
        self.close_button.clicked.connect(self.hide_notification)
        layout.addWidget(self.close_button)

        # Animation
        from modules.settings import should_enable_animations
        if should_enable_animations():
            self.animation = QPropertyAnimation(self, b"maximumHeight")
            self.animation.setDuration(250)
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        else:
            self.animation = None

        # Hide timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_notification)

    def show_message(self, message, notification_type="info", duration=5000):
        """Displays a notification message using the current theme."""
        theme_colors = global_theme_manager.get_current_colors()
        
        # Base background from theme, with transparency
        bg_color = QColor(theme_colors.get("frame_bg", "#2D3748"))
        bg_color.setAlpha(210) # ~82% opacity for a glassy effect
        
        # Icon and border colors
        type_styles = {
            "success": ("✓", theme_colors.get("success", "#4ade80")),
            "warning": ("⚠", theme_colors.get("warning", "#fbbf24")),
            "error": ("✗", theme_colors.get("error", "#f87171")),
            "info": ("ℹ", theme_colors.get("accent", "#60a5fa"))
        }
        icon_text, border_color = type_styles.get(notification_type, type_styles["info"])

        # Apply styles
        self.setStyleSheet(f"""
            #NotificationBar {{
                background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                border-radius: 6px;
                margin: 0 4px;
            }}
            #NotificationBar > QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }}
            #NotificationBar > QPushButton:hover {{
                background-color: rgba(255, 255, 255, 25);
            }}
            #NotificationBar > QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 15);
            }}
        """)
        self.icon_label.setText(icon_text)
        self.icon_label.setStyleSheet(f"color: {border_color}; font-size: 18px; font-weight: bold; background-color: transparent; border: none;")
        self.message_label.setText(message)

        # Show animation
        if self.animation:
            self.animation.setStartValue(self.height())
            self.animation.setEndValue(45) # Target height
            self.animation.start()
        else:
            # بدون حركات، قم بتعيين الارتفاع مباشرة
            self.setMaximumHeight(45)

        # Start hide timer
        if duration > 0:
            self.hide_timer.start(duration)

    def hide_notification(self):
        """Hides the notification bar with an animation."""
        self.hide_timer.stop()
        if self.animation:
            self.animation.setStartValue(self.height())
            self.animation.setEndValue(0)
            self.animation.start()
            self.animation.finished.connect(self.on_hide_finished)
        else:
            # بدون حركات، قم بإخفاء الإشعار مباشرة
            self.setMaximumHeight(0)
            self.on_hide_finished()

    def on_hide_finished(self):
        # فصل الإشارة فقط إذا كانت هناك حركات
        if self.animation:
            self.animation.finished.disconnect(self.on_hide_finished)
        self.closed.emit()

# --- 2. Notification Center (The History) ---

class NotificationCenter(QDialog):
    """
    A dialog window to display a history of all notifications.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("notification_center_title"))
        self.setMinimumSize(500, 400)
        self.setMaximumSize(800, 600)
        self.resize(500, 400)
        apply_theme(self, "dialog")
        
        # تطبيق السمة عند تغييرها
        global_theme_manager.theme_changed.connect(self._apply_theme)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # List for notifications
        self.history_list = QListWidget()
        from PySide6.QtWidgets import QAbstractItemView, QScrollArea
        self.history_list.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        self.history_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.history_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        apply_theme(self.history_list, "list_widget")
        layout.addWidget(self.history_list)

        # Buttons
        button_layout = QHBoxLayout()
        
        # Settings button
        settings_button = QPushButton(tr("settings"))
        apply_theme(settings_button, "button")
        settings_button.clicked.connect(self.show_settings_dialog)
        button_layout.addWidget(settings_button)
        
        # Clear button
        clear_button = QPushButton(tr("clear_all"))
        apply_theme(clear_button, "button")
        clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_button)
        
        # Close button
        close_button = QPushButton(tr("close_button"))
        apply_theme(close_button, "button")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        # Add stretch to push buttons to the right in LTR mode
        button_layout.addStretch()
        
        # تم ربط الأحداث سابقاً عند إنشاء الأزرار
        
        # Add button layout to main layout
        layout.addLayout(button_layout)

    def show_settings_dialog(self):
        """Opens the notification settings dialog."""
        settings_dialog = NotificationSettingsDialog(self)
        settings_dialog.exec()
        
    def clear_history(self):
        """مسح جميع الإشعارات من التاريخ"""
        self.history_list.clear()

    def _apply_theme(self):
        """تطبيق السمة الحالية على النافذة"""
        apply_theme(self, "dialog")
        apply_theme(self.history_list, "list_widget")
        
        # تحديث الألوان في العناصر الموجودة
        theme_colors = global_theme_manager.get_current_colors()
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            # استخراج نوع الإشعار من النص
            text = item.text()
            if text.startswith("✓ "):
                color = theme_colors.get("success", "#4ade80")
            elif text.startswith("⚠ "):
                color = theme_colors.get("warning", "#fbbf24")
            elif text.startswith("✗ "):
                color = theme_colors.get("error", "#f87171")
            else:
                color = theme_colors.get("accent", "#60a5fa")
            item.setForeground(QColor(color))
    
    def add_notification(self, message, notification_type):
        """Adds a new notification to the history list."""
        # استخدام طريقة بسيطة ومباشرة لعرض الإشعارات
        theme_colors = global_theme_manager.get_current_colors()
        type_styles = {
            "success": ("✓", theme_colors.get("success", "#4ade80")),
            "warning": ("⚠", theme_colors.get("warning", "#fbbf24")),
            "error": ("✗", theme_colors.get("error", "#f87171")),
            "info": ("ℹ", theme_colors.get("accent", "#60a5fa"))
        }
        icon_text, icon_color = type_styles.get(notification_type, type_styles["info"])
        
        # إنشاء نص الإشعار مع الأيقونة
        display_text = f"{icon_text} {message}"
        
        # إنشاء عنصر القائمة مباشرة
        item = QListWidgetItem(display_text)
        item.setForeground(QColor(icon_color))
        
        # إضافة العنصر إلى القائمة
        self.history_list.insertItem(0, item)

# --- Custom Widget for Notification Items ---
class NotificationItemWidget(QWidget):
    def __init__(self, message, notification_type, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent; border: none;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        theme_colors = global_theme_manager.get_current_colors()
        type_styles = {
            "success": ("✓", theme_colors.get("success", "#4ade80")),
            "warning": ("⚠", theme_colors.get("warning", "#fbbf24")),
            "error": ("✗", theme_colors.get("error", "#f87171")),
            "info": ("ℹ", theme_colors.get("accent", "#60a5fa"))
        }
        icon_text, icon_color = type_styles.get(notification_type, type_styles["info"])

        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet(f"color: {icon_color}; font-size: 16px; font-weight: bold;")
        layout.addWidget(icon_label)

        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        apply_theme(self.message_label, "list_item_text")
        self.message_label.setStyleSheet("background-color: transparent; border: none;")
        layout.addWidget(self.message_label, 1)

    def sizeHint(self):
        # Calculate the optimal height for the given width
        if self.parent() and hasattr(self.parent(), "viewport"):
            width = self.parent().viewport().width()
        else:
            width = 400
        # Subtract margins and spacing
        text_width = width - 20 - 30 # (margins + icon width)
        height = self.message_label.heightForWidth(text_width)
        return QSize(width, height + 10) # Add padding



# --- 2.5. Notification Settings Dialog ---

class NotificationSettingsDialog(QDialog):
    """
    A dialog for configuring notification visibility.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("notification_settings_title"))
        apply_theme(self, "dialog")
        self.setMinimumWidth(350)

        self.manager = global_notification_manager
        current_settings = self.manager.get_notification_settings()

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        self.checkboxes = {}
        notification_types = ["success", "warning", "error", "info"]
        
        for notif_type in notification_types:
            checkbox = QCheckBox(tr(f"show_{notif_type}_notifications"))
            checkbox.setChecked(current_settings.get(notif_type, True))
            apply_theme(checkbox, "checkbox")
            layout.addWidget(checkbox)
            self.checkboxes[notif_type] = checkbox

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def save_settings(self):
        """Saves the settings to the notification manager."""
        new_settings = {}
        for notif_type, checkbox in self.checkboxes.items():
            new_settings[notif_type] = checkbox.isChecked()
        self.manager.update_notification_settings(new_settings)
        self.accept()

# --- 3. Notification Manager (The Conductor) ---

class NotificationManager:
    """
    Manages the notification bar and the notification center.
    """
    def __init__(self):
        self.notification_bar = None
        self.notification_center = None
        self.load_settings()

    def load_settings(self):
        """Loads notification settings from the global settings manager."""
        default_settings = {
            "success": True,
            "warning": True,
            "error": True,
            "info": True
        }
        self.notification_settings = get_setting("notification_settings", default_settings)
        debug(f"Notification settings loaded: {self.notification_settings}")

    def register_widgets(self, main_window, notification_bar):
        """Registers the main UI components with the manager."""
        self.notification_bar = notification_bar
        self.notification_center = NotificationCenter(main_window)
        
        # Connect the history button on the bar to show the center
        if self.notification_bar:
            self.notification_bar.history_button.clicked.connect(self.show_notification_center)

    def get_notification_settings(self):
        """Returns the current notification settings."""
        return self.notification_settings

    def update_notification_settings(self, new_settings):
        """Updates and saves the notification settings."""
        self.notification_settings.update(new_settings)
        set_setting("notification_settings", self.notification_settings)
        debug(f"Notification settings updated and saved: {self.notification_settings}")

    def show_notification_center(self):
        """Shows the notification history dialog."""
        if self.notification_center:
            self.notification_center.exec()

    def show_notification(self, message, notification_type="info", duration=5000):
        """
        Shows a message on the notification bar and adds it to the history,
        respecting the user's settings.
        """
        # Add to history regardless of settings, so it's always logged
        if self.notification_center:
            self.notification_center.add_notification(message, notification_type)
        
        # Check if this type of notification is enabled
        if not self.notification_settings.get(notification_type, True):
            debug(f"Notification hidden by settings: [{notification_type}] {message}")
            return

        # Ensure widgets are registered for showing the bar
        if not self.notification_bar:
            debug("Notification bar not registered. Aborting display.")
            return

        # Show on the bar
        self.notification_bar.show_message(message, notification_type, duration)
        
        debug(f"Notification shown: [{notification_type}] {message}")

# --- Global Instance and Helper Functions ---

global_notification_manager = NotificationManager()

def show_notification(message, notification_type="info", duration=5000):
    """Helper function to show notifications."""
    global_notification_manager.show_notification(message, notification_type, duration)

def show_success(message, duration=4000):
    """Shows a success notification."""
    show_notification(message, "success", duration)

def show_warning(message, duration=5000):
    """Shows a warning notification."""
    show_notification(message, "warning", duration)

def show_error(message, duration=6000):
    """Shows an error notification."""
    show_notification(message, "error", duration)

def show_info(message, duration=4000):
    """Shows an info notification."""
    show_notification(message, "info", duration)
