# -*- coding: utf-8 -*-
"""
ودجت الإشعارات المبسط
"""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, QSize
from PySide6.QtGui import QColor
from src.ui.widgets.icon_utils import create_colored_icon_button
from src.ui.widgets.svg_icon_button import load_svg_icon
from src.managers.theme_manager import make_theme_aware, global_theme_manager
from src.utils.translator import tr

class NotificationWidget(QFrame):
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NotificationWidget")
        make_theme_aware(self, "notification_bar")
        self.setFixedHeight(0)
        self.setFrameShape(QFrame.NoFrame)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        self.message_label = QLabel()
        make_theme_aware(self.message_label, "notification_text")
        layout.addWidget(self.message_label, 1)

        self.history_button = create_colored_icon_button("history", 20, "", tr("notification_history_tooltip"))
        self.history_button.setFixedSize(28, 28)
        self.history_button.setIconSize(QSize(20, 20))
        layout.addWidget(self.history_button)

        self.close_button = create_colored_icon_button("x", 18, "", tr("close_button"))
        self.close_button.setFixedSize(28, 28)
        self.close_button.setIconSize(QSize(18, 18))
        self.close_button.clicked.connect(self.hide_notification)
        layout.addWidget(self.close_button)

        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_notification)

    def show_message(self, message, notification_type="info", duration=5000):
        bg_color = QColor(global_theme_manager.get_color("surface"))
        bg_color.setAlpha(210)

        type_styles = {
            "success": ("check-circle", global_theme_manager.get_color("success")),
            "warning": ("alert-triangle", global_theme_manager.get_color("warning")),
            "error": ("x-circle", global_theme_manager.get_color("error")),
            "info": ("info", global_theme_manager.get_color("text_accent"))
        }
        icon_name, icon_color = type_styles.get(notification_type, type_styles["info"])
        
        icon_pixmap = load_svg_icon(f"assets/icons/default/{icon_name}.svg", 20, icon_color)
        if icon_pixmap:
            self.icon_label.setPixmap(icon_pixmap)

        self.setStyleSheet(f"""
            #NotificationWidget {{
                background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                border-radius: 6px;
                margin: 0 4px;
            }}
        """)

        self.message_label.setText(message.replace('\n', ' ').strip())
        self.message_label.setToolTip(message)

        self.animation.setStartValue(self.height())
        self.animation.setEndValue(45)
        self.animation.start()

        if duration > 0:
            self.hide_timer.start(duration)

    def hide_notification(self):
        self.hide_timer.stop()
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.closed.emit)
        self.animation.start()
