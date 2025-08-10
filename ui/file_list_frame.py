"""
File List Frame Module
وحدة فريم قائمة الملفات

مكون موحد لعرض وإدارة الملفات المختارة في جميع نوافذ التطبيق
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QListWidget, QListWidgetItem, QFrame,
                               QSizePolicy, QApplication)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QDrag, QPixmap, QIcon
from .svg_icon_button import create_action_button
from .theme_manager import make_theme_aware
from .notification_system import show_success, show_warning, show_error, show_info
from modules.translator import tr
from .file_item_widget import FileItemWidget

class FileListItem(QListWidgetItem):
    """Custom list widget item to hold a reference to the file path."""
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path

class DraggableListWidget(QListWidget):
    """قائمة قابلة للسحب والإفلات"""
    
    files_reordered = Signal(list)  # إشارة عند إعادة ترتيب الملفات
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        make_theme_aware(self, "list_widget")
        
        self.setStyleSheet("""
            QListWidget::item {
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QListWidget::item:selected {
                background: rgba(66, 153, 225, 0.2);
            }
        """)
    
    def dropEvent(self, event):
        super().dropEvent(event)
        file_paths = []
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, FileListItem):
                file_paths.append(item.file_path)
        self.files_reordered.emit(file_paths)

class FileListFrame(QFrame):
    """فريم موحد لعرض وإدارة الملفات المختارة"""
    
    files_changed = Signal(list)
    file_removed = Signal(str)
    files_reordered = Signal(list)
    clear_button_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        self.setup_ui()
        self.hide()

        from .theme_manager import make_theme_aware
        make_theme_aware(self.title_label, "file_list_title")
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)
        
        self.title_label = QLabel(tr("selected_files_title"))
        self.title_label.setObjectName("fileListTitle")
        from .global_styles import get_file_list_title_style
        from .theme_manager import global_theme_manager
        colors = global_theme_manager.get_current_colors()
        accent = global_theme_manager.current_accent
        self.title_label.setStyleSheet(get_file_list_title_style(colors, accent))
        layout.addWidget(self.title_label)
        
        self.file_list = DraggableListWidget()
        self.file_list.setMinimumHeight(120)
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_list.files_reordered.connect(self.on_files_reordered)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.file_list)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        self.clear_all_btn = create_action_button("delete", 16, tr("clear_all_files_tooltip"))
        self.clear_all_btn.setMaximumWidth(40)
        self.clear_all_btn.clicked.connect(self.on_clear_all_clicked)
        
        buttons_layout.addWidget(self.clear_all_btn)
        buttons_layout.addStretch()
        
        self.count_label = QLabel(tr("file_count_plural", count=0))
        self.count_label.setStyleSheet("""
            QLabel {
                color: #a0aec0;
                font-size: 12px;
                padding: 4px;
            }
        """)
        buttons_layout.addWidget(self.count_label)
        
        layout.addLayout(buttons_layout)
        
        self.setStyleSheet("""
            QFrame {
                background: transparent;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 0px;
            }
        """)

        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def add_files(self, file_paths):
        new_files_added = False
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)
                item = FileListItem(file_path)
                widget = FileItemWidget(file_path)
                item.setSizeHint(widget.sizeHint())
                self.file_list.addItem(item)
                self.file_list.setItemWidget(item, widget)
                widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
                new_files_added = True

        if new_files_added:
            self.update_display()
            self.files_changed.emit(self.files)
    
    def remove_file(self, file_path):
        if file_path in self.files:
            self.files.remove(file_path)
            
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                if item and isinstance(item, FileListItem) and item.file_path == file_path:
                    self.file_list.takeItem(i)
                    break
            
            self.update_display()
            self.file_removed.emit(file_path)
            self.files_changed.emit(self.files)
    
    def on_clear_all_clicked(self):
        self.clear_all_files()
        self.clear_button_clicked.emit()

    def clear_all_files(self):
        if not self.files:
            return
            
        self.files.clear()
        self.file_list.clear()
        self.update_display()
        self.files_changed.emit(self.files)
    
    def on_files_reordered(self, new_order):
        self.files = new_order
        self.files_reordered.emit(self.files)
        self.files_changed.emit(self.files)
    
    def update_display(self):
        count = len(self.files)
        self.count_label.setText(tr("file_count_single") if count == 1 else tr("file_count_plural", count=count))
        
        if count > 0:
            if self.isHidden():
                self.setMaximumHeight(0)
                self.show()
                self.animate_show()
        else:
            if not self.isHidden():
                self.animate_hide()
    
    def animate_show(self):
        from modules.settings import should_enable_animations
        if should_enable_animations():
            target_height = 220
            
            self.animation = QPropertyAnimation(self, b"maximumHeight")
            self.animation.setDuration(300)
            self.animation.setStartValue(0)
            self.animation.setEndValue(target_height)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.start()
        else:
            self.setMaximumHeight(220)
            self.show()

    def animate_hide(self):
        from modules.settings import should_enable_animations
        if should_enable_animations():
            current_height = self.height()
            
            self.animation = QPropertyAnimation(self, b"maximumHeight")
            self.animation.setDuration(300)
            self.animation.setStartValue(current_height)
            self.animation.setEndValue(0)
            self.animation.setEasingCurve(QEasingCurve.InCubic)
            
            self.animation.finished.connect(self.hide)
            self.animation.start()
        else:
            self.hide()
    
    def get_files(self):
        return self.files.copy()
    
    def get_valid_files(self):
        valid_files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget and widget.is_valid:
                valid_files.append(widget.file_path)
        return valid_files

    def on_item_double_clicked(self, item):
        if isinstance(item, FileListItem):
            self.remove_file(item.file_path)

    def contextMenuEvent(self, event):
        from PySide6.QtWidgets import QMenu

        item = self.file_list.itemAt(self.file_list.mapFromGlobal(event.globalPos()))
        if isinstance(item, FileListItem):
            menu = QMenu(self)

            remove_action = menu.addAction(tr("remove_file_context_menu"))
            remove_action.triggered.connect(lambda: self.remove_file(item.file_path))

            info_action = menu.addAction(tr("file_info_context_menu"))
            info_action.triggered.connect(lambda: self.show_file_info(item))

            menu.exec_(event.globalPos())

    def show_file_info(self, item):
        widget = self.file_list.itemWidget(item)
        if not widget:
            return

        info_text = f"{tr('file_info_name')} {os.path.basename(widget.file_path)}\n"
        info_text += f"{tr('file_info_path')} {widget.file_path}\n"
        info_text += f"{tr('file_info_size')} {widget.format_file_size(widget.file_size)}\n"
        info_text += f"{tr('file_info_status')} {tr('file_info_status_valid') if widget.is_valid else tr('file_info_status_invalid')}"

        if not widget.is_valid:
            info_text += f"\n{tr('file_info_error')} {widget.error_message}"
            show_warning(info_text, duration=6000)
        else:
            show_info(info_text, duration=5000)

    def refresh_files(self):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget:
                widget.update_file_info()
                widget.update_display()
        self.update_display()
