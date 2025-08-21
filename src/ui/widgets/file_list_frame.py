"""
File List Frame Module — Single File (Responsive Fixed)

- صف الملف بالكامل قابل للنقر (اسم/حجم/أزرار في سطر واحد).
- توزيع مساحات دقيق باستخدام QHBoxLayout.setStretch:
    [Icon:fixed] [Name:stretch=6] [Size:stretch=1] [Actions:fixed]
- لا تداخل عند تغيير الحجم؛ النص يُقلم (elide) تلقائياً.
- سحب وإفلات لإعادة الترتيب + إشارات للتغيّر.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QFrame, QSizePolicy, QApplication, QPushButton, QStyle, QMenu
)
from PySide6.QtCore import (
    Qt, Signal, QMimeData, QPoint, QPropertyAnimation, QEasingCurve, QSize
)
from PySide6.QtGui import QDrag, QIcon, QFontMetrics, QAction

# احتفظ بهذه الواردات إن كانت موجودة في مشروعك
from src.ui.widgets.svg_icon_button import create_action_button
from src.managers.theme_manager import make_theme_aware
from src.managers.notification_system import show_success, show_warning, show_error, show_info
from src.utils.translator import tr
from .global_styles import get_file_list_title_style
from src.managers.theme_manager import global_theme_manager
from src.utils.settings import should_enable_animations
from managers.language_manager import language_manager

# --------------------------- File Item Widget (Inline) ---------------------------

class FileItemWidget(QFrame):
    """
    عنصر صف ملف بسطـر واحد:
    [Icon] [Name (elided)] [Size] [Actions...]

    - الصف كله قابل للنقر.
    - اسم الملف يتم تقليمه تلقائياً حسب العرض.
    - الحجم ثابت بصرياً ولكن مع نسبة تمدد صغيرة لتمنع التزاحم.
    """

    rowClicked = Signal()            # انبعاث عند النقر على الصف
    removeRequested = Signal(str)    # طلب إزالة ملف
    infoRequested = Signal()         # طلب معلومات

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_size = self._get_file_size(file_path)
        self.is_valid = os.path.exists(file_path) and os.path.isfile(file_path)
        self.error_message = "" if self.is_valid else tr("file_not_found")

        self.setObjectName("FileItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setMinimumHeight(40)

        make_theme_aware(self, "file_item")

        # ===== Layouts
        root = QHBoxLayout(self)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(8)

        # Icon (fixed)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setScaledContents(True)
        self._set_file_icon()
        root.addWidget(self.icon_label, 0)

        # Name (expanding with elide)
        self.name_label = QLabel(os.path.basename(file_path))
        self.name_label.setObjectName("FileName")
        self.name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        root.addWidget(self.name_label, 6)  # stretch=6

        # Size (small stretch to keep in same row)
        self.size_label = QLabel(self.format_file_size(self.file_size))
        self.size_label.setObjectName("FileSize")
        self.size_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter if language_manager.is_rtl() else Qt.AlignRight | Qt.AlignVCenter)
        self.size_label.setMinimumWidth(70)
        self.size_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        root.addWidget(self.size_label, 1)  # stretch=1

        # Actions (fixed)
        self.actions_container = QHBoxLayout()
        self.actions_container.setContentsMargins(0, 0, 0, 0)
        self.actions_container.setSpacing(4)

        # Remove button (uses your svg_icon_button factory if available)
        try:
            self.btn_remove = create_action_button("delete", 16, tr("remove_file_context_menu"))
        except Exception:
            self.btn_remove = QPushButton()
            self.btn_remove.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
            self.btn_remove.setFixedSize(28, 28)
            self.btn_remove.setToolTip(tr("remove_file_context_menu"))

        self.btn_remove.clicked.connect(lambda: self.removeRequested.emit(self.file_path))
        self.actions_container.addWidget(self.btn_remove)

        # Info button
        try:
            self.btn_info = create_action_button("info", 16, tr("file_info_context_menu"))
        except Exception:
            self.btn_info = QPushButton()
            self.btn_info.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
            self.btn_info.setFixedSize(28, 28)
            self.btn_info.setToolTip(tr("file_info_context_menu"))
        self.btn_info.clicked.connect(self.infoRequested.emit)
        self.actions_container.addWidget(self.btn_info)

        # Wrap actions in a dummy widget to keep them fixed
        actions_wrap = QWidget()
        actions_wrap.setLayout(self.actions_container)
        actions_wrap.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        root.addWidget(actions_wrap, 0)  # fixed block

        # Styling
        self.setStyleSheet("""
            #FileItem {
                border-radius: 8px;
            }
            #FileItem:hover {
                background: rgba(125, 125, 125, 0.10);
            }
            QLabel#FileName {
                font-size: 13px;
            }
            QLabel#FileSize {
                font-size: 12px;
                color: rgba(160, 174, 192, 1);
                padding-left: 8px;
            }
        """)

    # --- Behavior

    def mousePressEvent(self, event):
        # الصف بأكمله قابل للنقر
        if event.button() == Qt.LeftButton:
            self.rowClicked.emit()
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        act_info = QAction(tr("file_info_context_menu"), self)
        act_remove = QAction(tr("remove_file_context_menu"), self)
        act_info.triggered.connect(self.infoRequested.emit)
        act_remove.triggered.connect(lambda: self.removeRequested.emit(self.file_path))
        menu.addAction(act_info)
        menu.addAction(act_remove)
        menu.exec_(event.globalPos())

    def resizeEvent(self, event):
        # تقليم اسم الملف ليتناسب مع العرض المتاح
        fm = QFontMetrics(self.name_label.font())
        elided = fm.elidedText(os.path.basename(self.file_path), Qt.ElideRight, self.name_label.width())
        self.name_label.setText(elided)
        super().resizeEvent(event)

    # --- Helpers
    
    def _set_file_icon(self):
        """تحديد أيقونة الملف حسب نوعه"""
        try:
            from src.ui.widgets.svg_icon_button import load_svg_icon
            from src.managers.theme_manager import global_theme_manager
            
            icon_color = global_theme_manager.get_color("text_accent")
            file_ext = os.path.splitext(self.file_path)[1].lower()
            
            # تحديد الأيقونة حسب نوع الملف
            if file_ext == '.pdf':
                icon_name = "file-text"
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                icon_name = "image"
            elif file_ext in ['.txt', '.md', '.rtf']:
                icon_name = "file-text"
            else:
                icon_name = "file"
            
            # تحميل الأيقونة
            icon = load_svg_icon(f"assets/icons/default/{icon_name}.svg", 24, icon_color)
            if icon:
                self.icon_label.setPixmap(icon)
            else:
                # fallback للأيقونة الافتراضية
                self.icon_label.setPixmap(self.style().standardIcon(QStyle.SP_FileIcon).pixmap(24, 24))
        except Exception:
            # في حالة الخطأ، استخدم الأيقونة الافتراضية
            self.icon_label.setPixmap(self.style().standardIcon(QStyle.SP_FileIcon).pixmap(24, 24))

    @staticmethod
    def _get_file_size(path: str) -> int:
        try:
            return os.path.getsize(path)
        except Exception:
            return 0

    @staticmethod
    def format_file_size(size: int) -> str:
        # تنسيق مختصر ودقيق
        units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        s = float(size)
        while s >= 1024 and i < len(units) - 1:
            s /= 1024.0
            i += 1
        # دقة أعلى للأحجام الصغيرة
        return f"{s:.0f}{units[i]}" if i == 0 else f"{s:.2f}{units[i]}"

    def update_file_info(self):
        self.file_size = self._get_file_size(self.file_path)
        self.is_valid = os.path.exists(self.file_path) and os.path.isfile(self.file_path)
        if not self.is_valid:
            self.error_message = tr("file_not_found")
        self.size_label.setText(self.format_file_size(self.file_size))

    def update_display(self):
        # لو أردت إبراز حالة invalid يمكنك تعديل النغمة هنا
        if not self.is_valid:
            self.setStyleSheet(self.styleSheet() + """
                #FileItem { background: rgba(255, 59, 48, 0.08); }
                QLabel#FileName { color: #ff3b30; }
            """)
        else:
            pass

    # API متوافقة مع الكود الأصلي
    def handle_click(self):
        self.rowClicked.emit()


# --------------------------- List Item Wrapper ---------------------------

class FileListItem(QListWidgetItem):
    """عنصر حامل لمسار الملف داخل QListWidget."""
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path


# --------------------------- Draggable List ---------------------------

class DraggableListWidget(QListWidget):
    """قائمة قابلة للسحب والإفلات مع دعم نقر الصف بالكامل."""
    files_reordered = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QListWidget.SingleSelection)
        make_theme_aware(self, "list_widget")

        self.setStyleSheet("""
            QListWidget::item { border: none; margin: 0; padding: 0; }
            QListWidget::item:selected { background: rgba(66, 153, 225, 0.2); }
        """)

    def dropEvent(self, event):
        super().dropEvent(event)
        file_paths = []
        for i in range(self.count()):
            it = self.item(i)
            if isinstance(it, FileListItem):
                file_paths.append(it.file_path)
        self.files_reordered.emit(file_paths)


# --------------------------- File List Frame ---------------------------

class FileListFrame(QFrame):
    """فريم موحّد لعرض وإدارة الملفات المختارة (Responsive + Precise Spacing)."""

    files_changed = Signal(list)
    file_removed = Signal(str)
    files_reordered = Signal(list)
    clear_button_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        self.setup_ui()
        self.hide()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(6)

        # Title
        self.title_label = QLabel(tr("selected_files_title"))
        self.title_label.setObjectName("fileListTitle")
        self.title_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.title_label)

        # List
        self.file_list = DraggableListWidget()
        self.file_list.setMinimumHeight(120)
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_list.files_reordered.connect(self.on_files_reordered)
        layout.addWidget(self.file_list)

        # Footer (actions + count)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(6)

        self.clear_all_btn = create_action_button("delete", 16, tr("clear_all_files_tooltip"))
        self.clear_all_btn.setMaximumWidth(40)
        self.clear_all_btn.clicked.connect(self.on_clear_all_clicked)
        buttons_layout.addWidget(self.clear_all_btn)

        buttons_layout.addStretch()

        self.count_label = QLabel(tr("file_count_plural", count=0))
        self.count_label.setStyleSheet("""
            QLabel { color: #a0aec0; font-size: 12px; padding: 4px; }
        """)
        buttons_layout.addWidget(self.count_label)

        layout.addLayout(buttons_layout)

        # Frame style
        self.setStyleSheet("""
            QFrame {
                background: transparent;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # ----------------- Public API -----------------

    def add_files(self, file_paths):
        new_files_added = False
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)

                item = FileListItem(file_path)
                widget = FileItemWidget(file_path)
                # وصل إشارات العنصر
                widget.rowClicked.connect(lambda fp=file_path: self._on_row_clicked(fp))
                widget.removeRequested.connect(self.remove_file)
                widget.infoRequested.connect(lambda it=item: self.show_file_info(it))

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
                it = self.file_list.item(i)
                if isinstance(it, FileListItem) and it.file_path == file_path:
                    self.file_list.takeItem(i)
                    break
            self.update_display()
            self.file_removed.emit(file_path)
            self.files_changed.emit(self.files)

    def clear_all_files(self):
        if not self.files:
            return
        self.files.clear()
        self.file_list.clear()
        self.update_display()
        self.files_changed.emit(self.files)

    def get_files(self):
        return self.files.copy()

    def get_valid_files(self):
        valid_files = []
        for i in range(self.file_list.count()):
            it = self.file_list.item(i)
            w = self.file_list.itemWidget(it)
            if w and w.is_valid:
                valid_files.append(w.file_path)
        return valid_files

    # ----------------- Internal -----------------

    def _on_row_clicked(self, file_path):
        # حالياً: تحديد العنصر بالنقر؛ يمكنك استبدالها بفتح الملف أو المعاينة
        for i in range(self.file_list.count()):
            it = self.file_list.item(i)
            if isinstance(it, FileListItem) and it.file_path == file_path:
                self.file_list.setCurrentItem(it)
                break

    def on_clear_all_clicked(self):
        self.clear_all_files()
        self.clear_button_clicked.emit()

    def on_files_reordered(self, new_order):
        self.files = new_order
        self.files_reordered.emit(self.files)
        self.files_changed.emit(self.files)

    def update_display(self):
        count = len(self.files)
        self.count_label.setText(tr("file_count_single") if count == 1
                                 else tr("file_count_plural", count=count))
        if count > 0:
            if self.isHidden():
                self.setMaximumHeight(0)
                self.show()
                self.animate_show()
        else:
            if not self.isHidden():
                self.animate_hide()

    def animate_show(self):
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

    # ------ Context menu on list (maps to item widgets) ------
    def contextMenuEvent(self, event):
        pos_in_list = self.file_list.mapFromGlobal(event.globalPos())
        item = self.file_list.itemAt(pos_in_list)
        if isinstance(item, FileListItem):
            menu = QMenu(self)
            act_remove = menu.addAction(tr("remove_file_context_menu"))
            act_info = menu.addAction(tr("file_info_context_menu"))
            act_remove.triggered.connect(lambda: self.remove_file(item.file_path))
            act_info.triggered.connect(lambda it=item: self.show_file_info(it))
            menu.exec_(event.globalPos())

    def show_file_info(self, item: QListWidgetItem):
        widget = self.file_list.itemWidget(item)
        if not widget:
            return
        info_text = (
            f"{tr('file_info_name')} {os.path.basename(widget.file_path)}\n"
            f"{tr('file_info_path')} {widget.file_path}\n"
            f"{tr('file_info_size')} {widget.format_file_size(widget.file_size)}\n"
            f"{tr('file_info_status')} "
            f"{tr('file_info_status_valid') if widget.is_valid else tr('file_info_status_invalid')}"
        )
        if not widget.is_valid:
            info_text += f"\n{tr('file_info_error')} {widget.error_message}"
            show_warning(info_text, duration=6000)
        else:
            show_info(info_text, duration=5000)

    def refresh_files(self):
        for i in range(self.file_list.count()):
            it = self.file_list.item(i)
            w = self.file_list.itemWidget(it)
            if w:
                w.update_file_info()
                w.update_display()
        self.update_display()
