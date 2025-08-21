# -*- coding: utf-8 -*-
"""
نظام الإشعارات المبسط الجديد
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QScrollArea, QDialogButtonBox, QCheckBox, QFrame
from PySide6.QtCore import Qt, QTimer, QSize, QByteArray, QUrl
from PySide6.QtGui import QIcon, QColor, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtMultimedia import QSoundEffect
import os
import json
from src.utils.translator import tr
from src.managers.theme_manager import make_theme_aware, global_theme_manager
from src.utils.settings import get_setting, update_setting
from src.ui.widgets.notification_widget import NotificationWidget as NotificationBar

# --- Notification Center ---
class NotificationCenter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("notification_center_title"))
        self.setMinimumSize(500, 350)
        self.setMaximumSize(700, 550)
        self.resize(550, 400)
        make_theme_aware(self, "dialog")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.notification_tree = QTreeWidget()
        self.notification_tree.setHeaderHidden(True)
        make_theme_aware(self.notification_tree, "tree_widget")
        layout.addWidget(self.notification_tree)
        
        self.create_notification_categories()

        button_layout = QHBoxLayout()
        clear_button = QPushButton(tr("clear_all"))
        make_theme_aware(clear_button, "button")
        clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_button)
        layout.addLayout(button_layout)

    def create_notification_categories(self):
        self.categories = {}
        
        system_item = QTreeWidgetItem(self.notification_tree)
        system_item.setText(0, f"{tr('system_notifications')} (0)")
        self.categories["system"] = {"item": system_item, "notifications": {}}

    def clear_history(self):
        self.notification_tree.clear()

    def add_notification(self, message, notification_type):
        pass

# --- Notification Manager ---
class NotificationManager:
    def __init__(self):
        self.notification_bar = None
        self.notification_center = None
        self.load_settings()

    def load_settings(self):
        default_settings = {
            "success": True,
            "warning": True,
            "error": True,
            "info": True,
            "sounds_enabled": True
        }
        self.notification_settings = get_setting("notification_settings", default_settings)

    def register_widgets(self, main_window, notification_bar):
        self.notification_bar = notification_bar
        self.notification_center = NotificationCenter(main_window)
        
        if self.notification_bar:
            self.notification_bar.history_button.clicked.connect(self.show_notification_center)

    def get_notification_settings(self):
        return self.notification_settings

    def update_notification_settings(self, new_settings):
        self.notification_settings.update(new_settings)
        update_setting("notification_settings", self.notification_settings)

    def show_notification_center(self):
        if self.notification_center:
            self.notification_center.exec()

    def show_notification(self, message, notification_type="info", duration=5000):
        if not self.notification_settings.get(notification_type, True):
            return

        if not self.notification_bar:
            return

        self.notification_bar.show_message(message, notification_type, duration)

global_notification_manager = NotificationManager()

def show_notification(message, notification_type="info", duration=5000):
    global_notification_manager.show_notification(message, notification_type, duration)

def show_success(message, duration=4000):
    show_notification(message, "success", duration)

def show_warning(message, duration=5000):
    show_notification(message, "warning", duration)

def show_error(message, details="", duration=6000):
    full_message = message
    if details:
        full_message += f"\n\n{tr('details')}:\n{details}"
    show_notification(full_message, "error", duration)

def show_info(message, duration=4000):
    show_notification(message, "info", duration)

def check_and_notify_missing_libraries():
    return True