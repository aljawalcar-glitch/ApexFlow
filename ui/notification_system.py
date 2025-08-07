# -*- coding: utf-8 -*-
"""
نظام الإشعارات المدمج الجديد
New Integrated Notification System
"""
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, 
                               QFrame, QStackedWidget, QListWidget, QListWidgetItem,
                               QDialog, QDialogButtonBox, QApplication, QCheckBox,
                               QTreeWidget, QTreeWidgetItem, QAbstractItemView, QScrollArea)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal, QSize, QByteArray
from PySide6.QtGui import QIcon, QColor, QPainter, QPainterPath, QPixmap
from PySide6.QtSvg import QSvgRenderer
import os
import json
from modules.logger import debug
from modules.translator import tr
from .theme_manager import apply_theme, global_theme_manager
from modules.settings import get_setting, set_setting
# تم إزالة استيراد SystemDiagnosticsDialog لأننا نستخدم تبويب التشخيص في نافذة المساعدة بدلاً من ذلك

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

        # إنشاء نسخة من سطر واحد ومختصرة للرسالة لتناسب شريط الإشعارات
        single_line_message = message.replace('\n', ' ').replace('  ', ' ').strip()
        
        # اختصار النص ليتناسب مع العرض المتاح
        # هذا الحساب تقريبي
        available_width = self.parent_widget.width() - 150 if self.parent_widget else 500
        fm = self.message_label.fontMetrics()
        elided_message = fm.elidedText(single_line_message, Qt.ElideRight, available_width)
        
        self.message_label.setText(elided_message)
        # إظهار الرسالة الأصلية الكاملة في التلميح
        self.message_label.setToolTip(message)

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
        
    def show_message_with_action(self, message, notification_type="info", duration=5000, action_button=None):
        """Displays a notification message with an action button using the current theme."""
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

        # The message processing is now handled in the show_message method,
        # which is called by this method. No need to repeat the logic here.
        pass

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

    def show_message_with_action(self, message, notification_type="info", duration=5000, action_button=None):
        """Displays a notification message with an action button using the current theme."""
        # استدعاء الدالة الأصلية أولاً
        self.show_message(message, notification_type, duration)
        
        # إضافة زر الإجراء إذا تم توفيره
        if action_button:
            # إخفاء زر التاريخ مؤقتاً واستبداله بزر الإجراء
            self.history_button.hide()
            action_button.setParent(self)
            self.layout().insertWidget(3, action_button)  # إضافته قبل زر الإغلاق

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

# --- 2. Notification Detail Dialog ---

class NotificationDetailDialog(QDialog):
    """
    نافذة حوارية لعرض تفاصيل الإشعار بشكل كامل
    """
    def _darken_color(self, color, factor=0.2):
        """تغميق اللون"""
        from PySide6.QtGui import QColor
        color = QColor(color)
        h, s, l, a = color.getHsl()
        l = max(0, int(l * (1 - factor)))
        color.setHsl(h, s, l, a)
        return color.name()
        
    def __init__(self, notification_data, parent=None):
        super().__init__(parent)
        self.notification_data = notification_data
        self.setWindowTitle(tr("notification_details"))
        self.setMinimumSize(400, 300)
        # تعيين الحجم الأقصى لمنع النافذة من أن تكون كبيرة جدًا
        self.setMaximumSize(800, 600)
        # السماح بتغيير الحجم تلقائيًا حسب المحتوى
        self.setSizeGripEnabled(True)
        apply_theme(self, "dialog")

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # تم حذف عنوان الإشعار لمنع التكرار
        
        # تم حذف عنوان الإشعار لمنع التكرار
        
        # تم حذف الجزء الأخير من العنوان

        # نص الإشعار
        self.message_text = QLabel(self.notification_data.get("message", ""))
        self.message_text.setWordWrap(True)
        self.message_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.message_text.setStyleSheet("background-color: transparent; border: none; padding: 10px;")
        # إضافة التمرير للنصوص الطويلة
        scroll = QScrollArea()
        scroll.setWidget(self.message_text)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # تطبيق السمة على شريط التمرير
        theme_colors = global_theme_manager.get_current_colors()
        accent_color = global_theme_manager.current_accent
        scrollbar_style = f"""
            QScrollBar:vertical {{
                background: {theme_colors["surface"]};
                width: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {theme_colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self._darken_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {theme_colors["surface"]};
                height: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {theme_colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {self._darken_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """
        scroll.setStyleSheet(scroll.styleSheet() + scrollbar_style)
        
        layout.addWidget(scroll, 1)

        # معلومات الإشعار
        info_layout = QHBoxLayout()
        self.time_label = QLabel(self.notification_data.get("time", ""))
        self.time_label.setStyleSheet("color: #888; font-size: 10px;")
        info_layout.addWidget(self.time_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # زر الإغلاق
        close_button = QPushButton(tr("close_button"))
        apply_theme(close_button, "button")
        close_button.clicked.connect(self.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # تحديث الحجم بعد عرض النافذة
        QTimer.singleShot(100, self.adjustSize)


# --- 3. Notification Center (The History) ---

class NotificationCenter(QDialog):
    """
    A dialog window to display a history of all notifications.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("notification_center_title"))
        self.setMinimumSize(500, 350)
        self.setMaximumSize(700, 550)
        self.resize(550, 400)
        apply_theme(self, "dialog")
        
        # تطبيق السمة عند تغييرها
        global_theme_manager.theme_changed.connect(self._apply_theme)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # شجرة الإشعارات (الفهرس الرئيسي)
        self.notification_tree = QTreeWidget()
        self.notification_tree.setHeaderHidden(True)
        self.notification_tree.setExpandsOnDoubleClick(True)
        self.notification_tree.setAnimated(True)
        self.notification_tree.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.notification_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        apply_theme(self.notification_tree, "tree_widget")
        
        # ربط النقر المزدوج بعرض التفاصيل
        self.notification_tree.itemDoubleClicked.connect(self.show_notification_details)
        
        layout.addWidget(self.notification_tree)
        
        # إنشاء فئات الإشعارات
        self.create_notification_categories()

        # Buttons
        button_layout = QHBoxLayout()
        
        # Settings button removed - moved to notification settings tab

        # Clear button
        clear_button = QPushButton(tr("clear_all"))
        apply_theme(clear_button, "button")
        clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_button)

        # Add stretch to separate button groups
        button_layout.addStretch()

        # Diagnostics button removed
        
        # Close button removed
        
        # Add button layout to main layout
        layout.addLayout(button_layout)

    def show_settings_dialog(self):
        """Opens the notification settings dialog."""
        settings_dialog = NotificationSettingsDialog(self)
        settings_dialog.exec()
        
    def show_diagnostics(self):
        """Opens the help window with diagnostics tab."""
        from .help_page import HelpPage
        help_page = HelpPage(self.parent())
        help_page.show()
        # فتح تبويب التشخيص مباشرة
        help_page.help_tabs.setCurrentIndex(help_page.help_tabs.count() - 1)  # تبويب التشخيص هو عادة التبويب الأخير
        
    def clear_history(self):
        """مسح جميع الإشعارات من التاريخ"""
        self.notification_tree.clear()
        self.save_notifications_to_file()
    
    def save_notifications_to_file(self):
        """حفظ الإشعارات في ملف JSON"""
        if get_setting("notification_settings", {}).get("do_not_save", False):
            return
            
        try:
            # تحويل الإشعارات إلى تنسيق قابل للحفظ
            notifications_data = {}
            for category, data in self.categories.items():
                notifications_data[category] = data["notifications"]
            
            # تحديد مسار الملف
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            file_path = os.path.join(data_dir, "notifications.json")
            
            # حفظ البيانات في الملف
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(notifications_data, f, ensure_ascii=False, indent=2)
                
            debug(f"Notifications saved to {file_path}")
        except Exception as e:
            debug(f"Error saving notifications: {str(e)}")

    def _darken_color(self, color, factor=0.2):
        """تغميق اللون"""
        from PySide6.QtGui import QColor
        color = QColor(color)
        h, s, l, a = color.getHsl()
        l = max(0, int(l * (1 - factor)))
        color.setHsl(h, s, l, a)
        return color.name()
        
    def _apply_theme(self):
        """تطبيق السمة الحالية على النافذة"""
        apply_theme(self, "dialog")
        apply_theme(self.notification_tree, "tree_widget")
        

        theme_colors = global_theme_manager.get_current_colors()
        accent_color = global_theme_manager.current_accent
        
        # تم حذف كود شريط التمرير اليدوي - نستخدم الآن النمط الموحد من global_styles.py
        
        # تحديث الألوان في عناصر الشجرة
        # سيتم تحديث الألوان عند إضافة العناصر الجديدة
    
    def load_notifications_from_file(self):
        """تحميل الإشعارات من ملف JSON"""
        try:
            # تحديد مسار الملف
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            file_path = os.path.join(data_dir, "notifications.json")
            
            # التحقق من وجود الملف
            if not os.path.exists(file_path):
                return
                
            # قراءة البيانات من الملف
            with open(file_path, "r", encoding="utf-8") as f:
                notifications_data = json.load(f)
                
            debug(f"Notifications loaded from {file_path}")
            
            # استعادة الإشعارات في الفئات
            for category, notifications in notifications_data.items():
                if category in self.categories:
                    for notification_id, notification_data in notifications.items():
                        # إنشاء عنصر جديد للإشعار
                        notification_item = QTreeWidgetItem(self.categories[category]["item"])
                        notification_item.setText(0, notification_data.get("title", ""))
                        notification_item.setData(0, Qt.UserRole, notification_data)
                        
                        # إضافة الإشعار إلى قائمة إشعارات الفئة
                        self.categories[category]["notifications"][notification_id] = notification_data
                        
                    # تحديث عداد الإشعارات للفئة
                        self.update_category_counter(category)
                    
        except Exception as e:
            debug(f"Error loading notifications: {str(e)}")
    
    def create_notification_categories(self):
        """إنشاء فئات الإشعارات في الفهرس الرئيسي"""
        theme_colors = global_theme_manager.get_current_colors()
        accent_color = global_theme_manager.current_accent

        def create_themed_icon(svg_path, color):
            """Creates a QIcon from an SVG file with a specific color."""
            try:
                with open(svg_path, 'r', encoding='utf-8') as f:
                    svg_data = f.read()
                
                # Replace currentColor with the actual theme color
                colored_svg_data = svg_data.replace('currentColor', color)
                
                # Use QByteArray for QSvgRenderer
                byte_array = QByteArray(colored_svg_data.encode('utf-8'))
                renderer = QSvgRenderer(byte_array)

                # Create a pixmap to render on
                pixmap = QPixmap(renderer.defaultSize())
                pixmap.fill(Qt.transparent)
                
                # Create a painter to draw the SVG
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                
                return QIcon(pixmap)
            except Exception as e:
                debug(f"Failed to create themed icon from {svg_path}: {e}")
                return QIcon() # Return empty icon on failure

        # Define icon paths
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        icon_path = lambda name: os.path.join(project_root, 'assets', 'icons', 'default', name)

        # Since new icons cannot be created, we'll reuse existing ones
        # and assign them thematically.
        icons = {
            "system": create_themed_icon(icon_path("info.svg"), accent_color),
            "tasks": create_themed_icon(icon_path("archive.svg"), accent_color),
            "alerts": create_themed_icon(icon_path("info.svg"), theme_colors.get("error", "#f87171")),
            "warnings": create_themed_icon(icon_path("info.svg"), theme_colors.get("warning", "#fbbf24"))
        }

        # إنشاء فئات الإشعارات الرئيسية
        self.categories = {}
        
        # 1. إشعارات النظام
        system_item = QTreeWidgetItem(self.notification_tree)
        system_item.setIcon(0, icons["system"])
        system_item.setText(0, f"{tr('system_notifications')} (0)")
        system_item.setData(0, Qt.UserRole, "system")
        self.categories["system"] = {"item": system_item, "notifications": {}}
        
        # 2. إشعارات المهام
        tasks_item = QTreeWidgetItem(self.notification_tree)
        tasks_item.setIcon(0, icons["tasks"])
        tasks_item.setText(0, f"{tr('tasks_notifications')} (0)")
        tasks_item.setData(0, Qt.UserRole, "tasks")
        self.categories["tasks"] = {"item": tasks_item, "notifications": {}}
        
        # 3. إشعارات التنبيه
        alerts_item = QTreeWidgetItem(self.notification_tree)
        alerts_item.setIcon(0, icons["alerts"])
        alerts_item.setText(0, f"{tr('alerts_notifications')} (0)")
        alerts_item.setData(0, Qt.UserRole, "alerts")
        self.categories["alerts"] = {"item": alerts_item, "notifications": {}}
        
        # 4. رسائل التحذير
        warnings_item = QTreeWidgetItem(self.notification_tree)
        warnings_item.setIcon(0, icons["warnings"])
        warnings_item.setText(0, f"{tr('warning_messages')} (0)")
        warnings_item.setData(0, Qt.UserRole, "warnings")
        self.categories["warnings"] = {"item": warnings_item, "notifications": {}}

        # Apply general styles
        self.notification_tree.setStyleSheet(f"""
            QTreeWidget::item {{
                padding: 8px 4px; /* Increased padding for icon */
            }}
            QScrollBar:vertical {{
                background: {theme_colors["surface"]};
                width: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {theme_colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self._darken_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {theme_colors["surface"]};
                height: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {theme_colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {self._darken_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """)
        
        # طي جميع الفئات افتراضيًا
        self.notification_tree.collapseAll()
        
        # تحميل الإشعارات المحفوظة
        self.load_notifications_from_file()
    
    def update_category_counter(self, category):
        """تحديث عداد الإشعارات لفئة معينة"""
        if category not in self.categories:
            return
            
        count = len(self.categories[category]["notifications"])
        # استخدام طريقة آمنة للحصول على اسم الفئة المترجم
        try:
            # The key for translation is like 'system_notifications', 'tasks_notifications', etc.
            if category == "warnings":
                 category_name = tr("warning_messages")
            else:
                category_name = tr(f"{category}_notifications")
        except Exception:
            category_name = category.capitalize()
        
        # تحديث نص الفئة مع العداد الجديد
        self.categories[category]["item"].setText(0, f"{category_name} ({count})")
    
    def show_notification_details(self, item):
        """عرض تفاصيل الإشعار عند النقر المزدوج"""
        # الحصول على بيانات الإشعار
        notification_data = item.data(0, Qt.UserRole)
        
        # إذا كان العنصر فئة وليس إشعارًا، لا تفعل شيئًا
        if not isinstance(notification_data, dict):
            return
            
        # إنشاء وعرض نافذة التفاصيل
        details_dialog = NotificationDetailDialog(notification_data, self)
        details_dialog.exec()
    
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
        

        
        # تحديد الفئة المناسبة
        category = "info"  # فئة افتراضية
        if notification_type == "error":
            category = "alerts"
        elif notification_type == "warning":
            category = "warnings"
        elif notification_type == "success":
            category = "tasks"
            
        # التحقق من وجود الفئات
        if not hasattr(self, "categories") or not self.categories:
            # إنشاء الفئات إذا لم تكن موجودة
            self.create_notification_categories()
            
        # التحقق من وجود الفئة المحددة
        if category not in self.categories:
            # استخدام فئة النظام كبديل
            category = "system"
            
        # إنشاء عنصر الإشعار تحت الفئة المناسبة
        notification_item = QTreeWidgetItem(self.categories[category]["item"])
        
        # استخدام الويدجت المخصص لعرض الإشعار
        item_widget = NotificationItemWidget(message, notification_type)
        self.notification_tree.setItemWidget(notification_item, 0, item_widget)
        
        # حفظ بيانات الإشعار
        import datetime
        notification_data = {
            "icon": icon_text,
            "color": icon_color,
            "title": display_text,
            "message": message,
            "type": notification_type,
            "category": category,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "read": False
        }
        
        # تخزين البيانات في العنصر
        notification_item.setData(0, Qt.UserRole, notification_data)
        
        # إضافة الإشعار إلى قائمة إشعارات الفئة
        notification_id = f"{category}_{len(self.categories[category]['notifications']) + 1}"
        self.categories[category]["notifications"][notification_id] = notification_data
        
        # تحديث عداد الإشعارات للفئة
        self.update_category_counter(category)
        
        # حفظ الإشعارات في الملف
        self.save_notifications_to_file()

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
        
        # إضافة خيار عدم حفظ الإشعارات في الذاكرة
        layout.addSpacing(10)
        separator = QLabel()
        separator.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        layout.addWidget(separator)
        layout.addSpacing(10)
        
        memory_checkbox = QCheckBox(tr("do_not_save_notifications"))
        memory_checkbox.setChecked(current_settings.get("do_not_save", False))
        apply_theme(memory_checkbox, "checkbox")
        layout.addWidget(memory_checkbox)
        self.checkboxes["do_not_save"] = memory_checkbox

        # Buttons
        button_box = QDialogButtonBox()
        save_button = button_box.addButton(tr("save_all_changes_button"), QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton(tr("cancel_changes_button"), QDialogButtonBox.RejectRole)
        apply_theme(save_button, "button")
        apply_theme(cancel_button, "button")
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
            "info": True,
            "do_not_save": False
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
        # Add to history only if not disabled in settings
        if self.notification_center and not self.notification_settings.get("do_not_save", False):
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
        
    def show_notification_with_action(self, notification_data):
        """
        Shows a notification with an action button.
        """
        message = notification_data.get("message", "")
        notification_type = notification_data.get("type", "info")
        duration = notification_data.get("duration", 5000)
        action_button = notification_data.get("action_button")
        details = notification_data.get("details", {})
        
        # Add to history only if not disabled in settings
        if self.notification_center and not self.notification_settings.get("do_not_save", False):
            # Add details to the notification
            full_message = message
            if isinstance(details, list) and details:
                full_message += "\nالمكتبات المفقودة:\n"
                for lib, install_cmd, desc, category in details:
                    full_message += f"- {lib}: {desc}\n"
            
            self.notification_center.add_notification(full_message, notification_type)

        # Check if this type of notification is enabled
        if not self.notification_settings.get(notification_type, True):
            debug(f"Notification hidden by settings: [{notification_type}] {message}")
            return

        # Ensure widgets are registered for showing the bar
        if not self.notification_bar:
            debug("Notification bar not registered. Aborting display.")
            return

        # Show on the bar with action button
        self.notification_bar.show_message_with_action(message, notification_type, duration, action_button)

        debug(f"Notification with action shown: [{notification_type}] {message}")

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

def show_error(message, details="", duration=6000):
    """Shows an error notification."""
    full_message = message
    if details:
        full_message += f"\n\n{tr('details')}:\n{details}"
    show_notification(full_message, "error", duration)

def show_info(message, duration=4000):
    """Shows an info notification."""
    show_notification(message, "info", duration)

def check_required_libraries():
    """التحقق من المكتبات المطلوبة للتطبيق"""
    required_libs = [
        ('PySide6', 'pip install PySide6==6.8.0.2', 'مكتبة واجهة المستخدم الرسومية', 'core'),
        ('pypdf', 'pip install pypdf==5.0.0', 'مكتبة معالجة ملفات PDF', 'core'),
        ('fitz', 'pip install PyMuPDF==1.26.3', 'مكتبة معالجة متقدمة لملفات PDF', 'core'),
        ('PIL', 'pip install Pillow==11.3.0', 'مكتبة معالجة الصور', 'core'),
        ('arabic_reshaper', 'pip install arabic-reshaper==3.0.0', 'مكتبة إعادة تشكيل النص العربي', 'arabic'),
        ('bidi.algorithm', 'pip install python-bidi==0.6.6', 'مكتبة دعم النصوص ثنائية الاتجاه', 'arabic'),
        ('psutil', 'pip install psutil==6.0.0', 'مكتبة مراقبة النظام', 'system'),
        ('win32api', 'pip install pywin32==306', 'مكتبة وظائف ويندوز', 'system')
    ]
    
    missing_libs = []
    for lib, install_cmd, desc, category in required_libs:
        try:
            __import__(lib)
        except ImportError:
            missing_libs.append((lib, install_cmd, desc, category))
    
    return missing_libs

def install_missing_libraries(missing_libs):
    """تثبيت المكتبات المفقودة"""
    import subprocess
    import sys
    from PySide6.QtCore import QThread, Signal
    
    class InstallThread(QThread):
        finished = Signal(bool)
        progress = Signal(str)
        
        def __init__(self, libs):
            super().__init__()
            self.libs = libs
        
        def run(self):
            success = True
            for lib, install_cmd, desc, category in self.libs:
                try:
                    self.progress.emit(f"جاري تثبيت {lib}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install"] + install_cmd.split()[1:])
                    self.progress.emit(f"تم تثبيت {lib} بنجاح")
                except subprocess.CalledProcessError as e:
                    self.progress.emit(f"فشل تثبيت {lib}: {e}")
                    success = False
            
            self.finished.emit(success)
    
    # إنشاء وتشغيل خيط التثبيت
    install_thread = InstallThread(missing_libs)
    
    # عرض إشعار التقدم
    from PySide6.QtWidgets import QProgressDialog, QApplication
    progress_dialog = QProgressDialog("جاري تثبيت المكتبات...", "إلغاء", 0, len(missing_libs))
    progress_dialog.setWindowModality(Qt.WindowModal)
    progress_dialog.show()
    
    # ربط الإشارات
    def update_progress(message):
        progress_dialog.setLabelText(message)
        QApplication.processEvents()
    
    def on_install_finished(success):
        progress_dialog.close()
        if success:
            show_success("تم تثبيت جميع المكتبات بنجاح. يرجى إعادة تشغيل التطبيق.", duration=10000)
        else:
            show_error("فشل تثبيت بعض المكتبات. يرجى التثبيت يدوياً.", duration=10000)
    
    install_thread.progress.connect(update_progress)
    install_thread.finished.connect(on_install_finished)
    
    # بدء التثبيت
    install_thread.start()
    
    return install_thread

def check_and_notify_missing_libraries():
    """التحقق من المكتبات المفقودة وإعلام المستخدم"""
    missing_libs = check_required_libraries()
    
    if missing_libs:
        # تعريف دالة رد الاتصال لتثبيت المكتبات
        def install_callback():
            install_missing_libraries(missing_libs)
        
        # عرض الإشعار مع خيار التثبيت
        show_library_missing_notification(missing_libs, install_callback)
        
        return False
    
    return True

def show_library_missing_notification(missing_libs, auto_install_callback=None):
    """عرض إشعار للمكتبات المفقودة مع خيارات التثبيت"""
    from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget
    
    # إنشاء رسالة الإشعار
    message = "بعض المكتبات المطلوبة غير متوفرة. "
    message += f"عدد المكتبات المفقودة: {len(missing_libs)}"
    
    # إنشاء زر التثبيت التلقائي
    if auto_install_callback:
        install_btn = QPushButton("تثبيت الآن")
        install_btn.clicked.connect(auto_install_callback)
        
        # إضافة الزر إلى الإشعار
        notification_data = {
            "message": message,
            "type": "warning",
            "duration": 0,  # لا يختفي تلقائياً
            "action_button": install_btn,
            "details": missing_libs
        }
        
        global_notification_manager.show_notification_with_action(notification_data)
    else:
        show_warning(message, duration=0)  # لا يختفي تلقائياً
    
    return True
