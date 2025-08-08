"""
File List Frame Module
وحدة فريم قائمة الملفات

مكون موحد لعرض وإدارة الملفات المختارة في جميع نوافذ التطبيق
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QListWidgetItem, QFrame,
                               QSizePolicy, QApplication)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QDrag, QPainter, QPixmap, QIcon, QFont
from .svg_icon_button import create_action_button
from .theme_manager import make_theme_aware
from .notification_system import show_success, show_warning, show_error, show_info
from modules.translator import tr

class AnimatedFileItemWidget(QWidget):
    """A widget for displaying a file with hover animations."""
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.is_valid = True
        self.error_message = ""
        self.file_size = 0
        
        self.update_file_info()
        
        self.setMinimumHeight(40)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        
        self.icon_label = QLabel()
        self.file_name_label = QLabel()
        self.size_label = QLabel()
        
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.file_name_label, 1)
        self.layout.addWidget(self.size_label)
        
        self.update_display()
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def enterEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-5, -5, 5, 5))
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(5, 5, -5, -5))
        self.animation.start()
        super().leaveEvent(event)

    def update_file_info(self):
        """Update file information."""
        try:
            if os.path.exists(self.file_path):
                self.file_size = os.path.getsize(self.file_path)
                if self.file_path.lower().endswith('.pdf'):
                    self.is_valid = self.validate_pdf()
                else:
                    self.is_valid = True
            else:
                self.is_valid = False
                self.error_message = tr("file_not_found")
        except Exception as e:
            self.is_valid = False
            self.error_message = tr("error_reading_file", e=str(e))

    def validate_pdf(self):
        """Validate a PDF file."""
        try:
            with open(self.file_path, 'rb') as file:
                header = file.read(8)
                if not header.startswith(b'%PDF-'):
                    self.error_message = tr("invalid_pdf_file")
                    return False
            return True
        except Exception as e:
            self.error_message = tr("error_checking_pdf", e=str(e))
            return False

    def update_display(self):
        """Update the display of the widget."""
        file_name = os.path.basename(self.file_path)
        size_text = self.format_file_size(self.file_size)
        
        if self.is_valid:
            self.file_name_label.setText(file_name)
            self.size_label.setText(size_text)
            self.icon_label.setPixmap(QIcon.fromTheme("application-pdf").pixmap(22, 22))
            self.setToolTip(self.file_path)
        else:
            self.file_name_label.setText(f"{tr('error_label')} {file_name}")
            self.size_label.setText(self.error_message)
            self.icon_label.setPixmap(QIcon.fromTheme("dialog-error").pixmap(22, 22))
            self.setToolTip(f"{tr('error_label')} {self.error_message}")

    def format_file_size(self, size_bytes):
        """Format file size."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

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
        self.drag_start_position = QPoint()
        make_theme_aware(self, "list_widget")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return
        
        # بدء عملية السحب
        item = self.itemAt(self.drag_start_position)
        if item:
            widget = self.itemWidget(item)
            if widget:
                self.start_drag(item, widget)
    
    def start_drag(self, item, widget):
        """Start the drag operation with visual effects."""
        drag = QDrag(self)
        mime_data = QMimeData()
        # Use the file path for the mime data to ensure uniqueness
        mime_data.setText(widget.file_path)
        drag.setMimeData(mime_data)

        # Create a pixmap of the widget for the drag cursor
        pixmap = QPixmap(widget.size())
        widget.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))

        # Execute the drag
        drop_action = drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        """عند دخول عنصر مسحوب"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # The visual feedback for drag-and-drop should be handled by the theme or a more dynamic approach.
            # For now, we remove the hardcoded style change to allow the theme to work correctly.

    def dragLeaveEvent(self, event):
        """عند خروج عنصر مسحوب"""
        # Restore original style by reapplying the theme
        make_theme_aware(self, "list_widget")
    
    def dropEvent(self, event):
        super().dropEvent(event)
        # إرسال إشارة بالترتيب الجديد
        file_paths = []
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, FileListItem):
                file_paths.append(item.file_path)
        self.files_reordered.emit(file_paths)

class FileListFrame(QFrame):
    """فريم موحد لعرض وإدارة الملفات المختارة"""
    
    # الإشارات
    files_changed = Signal(list)  # عند تغيير قائمة الملفات
    file_removed = Signal(str)    # عند حذف ملف
    files_reordered = Signal(list)  # عند إعادة ترتيب الملفات
    clear_button_clicked = Signal() # عند الضغط على زر السلة
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []  # قائمة مسارات الملفات
        self.setup_ui()
        self.hide()  # مخفي افتراضياً

        # تسجيل العنوان للاستجابة لتغييرات السمة
        from .theme_manager import make_theme_aware
        make_theme_aware(self.title_label, "file_list_title")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # التخطيط الرئيسي
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)
        
        # عنوان الفريم
        self.title_label = QLabel(tr("selected_files_title"))
        self.title_label.setObjectName("fileListTitle")
        from .global_styles import get_file_list_title_style
        from .theme_manager import global_theme_manager
        colors = global_theme_manager.get_current_colors()
        accent = global_theme_manager.current_accent
        self.title_label.setStyleSheet(get_file_list_title_style(colors, accent))
        layout.addWidget(self.title_label)
        
        # قائمة الملفات - مساحة أكبر
        self.file_list = DraggableListWidget()
        self.file_list.setMinimumHeight(120)  # حد أدنى للارتفاع
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_list.files_reordered.connect(self.on_files_reordered)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.file_list)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        # استخدام زر أيقونة SVG لمسح الكل (سيطبق اللون الأحمر تلقائياً)
        self.clear_all_btn = create_action_button("delete", 16, tr("clear_all_files_tooltip"))
        self.clear_all_btn.setMaximumWidth(40)
        self.clear_all_btn.clicked.connect(self.on_clear_all_clicked)
        
        buttons_layout.addWidget(self.clear_all_btn)
        buttons_layout.addStretch()
        
        # عداد الملفات
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
        
        # تخصيص مظهر الفريم
        self.setStyleSheet("""
            QFrame {
                background: transparent;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 0px;
            }
        """)

        # إضافة تأثير الظهور التدريجي
        self.setGraphicsEffect(None)  # بدون تأثيرات افتراضياً
        
        # تحديد الحد الأدنى للارتفاع
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def add_files(self, file_paths):
        """إضافة ملفات جديدة"""
        # التأكد من أن القائمة مرئية قبل إضافة الملفات
        if self.isHidden():
            self.show()
            self.animate_show()
        else:
            # إذا كانت القائمة مرئية بالفعل، تأكد من تحديثها
            self.raise_()
            self.repaint()

        for file_path in file_paths:
            # تجنب إضافة الملفات المكررة
            if file_path not in self.files:
                self.files.append(file_path)
                item = FileListItem(file_path)
                widget = AnimatedFileItemWidget(file_path)
                item.setSizeHint(widget.sizeHint())
                self.file_list.addItem(item)
                self.file_list.setItemWidget(item, widget)

        # تحديث العرض وإرسال الإشارة بعد إضافة جميع الملفات
        self.update_display()
        self.files_changed.emit(self.files)
        
        # فرض تحديث الواجهة الرسومية لضمان ظهور العناصر
        QApplication.processEvents()
        
        # التأكد من أن النافذة الأصل مرئية ومحدثة
        parent = self.parent()
        while parent:
            parent.raise_()
            parent.repaint()
            parent = parent.parent()
    
    def remove_file(self, file_path):
        """حذف ملف محدد"""
        if file_path in self.files:
            self.files.remove(file_path)
            
            # حذف العنصر من القائمة
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                if item and self.file_list.itemWidget(item).file_path == file_path:
                    self.file_list.takeItem(i)
                    break
            
            self.update_display()
            self.file_removed.emit(file_path)
            self.files_changed.emit(self.files)
    
    def on_clear_all_clicked(self):
        """عند الضغط على زر مسح الكل"""
        self.clear_all_files()
        self.clear_button_clicked.emit()

    def clear_all_files(self):
        """مسح جميع الملفات"""
        if not self.files:
            return  # لا تفعل شيئًا إذا كانت القائمة فارغة بالفعل
            
        self.files.clear()
        self.file_list.clear()
        self.update_display()
        self.files_changed.emit(self.files)
    
    def on_files_reordered(self, new_order):
        """معالجة إعادة ترتيب الملفات"""
        self.files = new_order
        self.files_reordered.emit(self.files)
        self.files_changed.emit(self.files)
    
    def update_display(self):
        """تحديث العرض"""
        count = len(self.files)
        self.count_label.setText(tr("file_count_single") if count == 1 else tr("file_count_plural", count=count))
        
        # إظهار/إخفاء الفريم
        if count > 0:
            if self.isHidden():
                self.show()
                self.animate_show()
        else:
            if not self.isHidden():
                self.animate_hide()
    
    def animate_show(self):
        """تحريك الظهور"""
        from modules.settings import should_enable_animations
        if should_enable_animations():
            self.animation = QPropertyAnimation(self, b"maximumHeight")
            self.animation.setDuration(400)  # مدة أطول قليلاً للحجم الأكبر
            self.animation.setStartValue(0)
            self.animation.setEndValue(220)  # الحجم الجديد
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.start()
        else:
            # بدون حركات، قم بتعيين الارتفاع مباشرة
            self.setMaximumHeight(220)

    def animate_hide(self):
        """تحريك الاختفاء"""
        from modules.settings import should_enable_animations
        if should_enable_animations():
            self.animation = QPropertyAnimation(self, b"maximumHeight")
            self.animation.setDuration(400)  # مدة أطول قليلاً
            self.animation.setStartValue(220)  # الحجم الجديد
            self.animation.setEndValue(0)
            self.animation.setEasingCurve(QEasingCurve.InCubic)
            self.animation.finished.connect(self.hide)
            self.animation.start()
        else:
            # بدون حركات، قم بإخفاء العنصر مباشرة
            self.hide()
    
    def get_files(self):
        """الحصول على قائمة الملفات"""
        return self.files.copy()
    
    def get_valid_files(self):
        """الحصول على الملفات الصالحة فقط"""
        valid_files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget and widget.is_valid:
                valid_files.append(widget.file_path)
        return valid_files

    def on_item_double_clicked(self, item):
        """معالجة النقر المزدوج على عنصر - حذف الملف"""
        widget = self.file_list.itemWidget(item)
        if widget:
            self.remove_file(widget.file_path)

    def contextMenuEvent(self, event):
        """قائمة السياق للنقر بالزر الأيمن"""
        from PySide6.QtWidgets import QMenu

        item = self.file_list.itemAt(self.file_list.mapFromGlobal(event.globalPos()))
        if isinstance(item, FileListItem):
            menu = QMenu(self)

            # حذف الملف
            remove_action = menu.addAction(tr("remove_file_context_menu"))
            remove_action.triggered.connect(lambda: self.remove_file(item.file_path))

            # معلومات الملف
            info_action = menu.addAction(tr("file_info_context_menu"))
            info_action.triggered.connect(lambda: self.show_file_info(item))

            menu.exec_(event.globalPos())

    def show_file_info(self, item):
        """عرض معلومات الملف"""
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
        """تحديث معلومات جميع الملفات"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget:
                widget.update_file_info()
                widget.update_display()
        self.update_display()
