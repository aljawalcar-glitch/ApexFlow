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

class FileListItem(QListWidgetItem):
    """عنصر ملف مخصص مع معلومات إضافية"""
    
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.is_valid = True
        self.error_message = ""
        self.file_size = 0
        
        # تحديث معلومات الملف
        self.update_file_info()
        self.update_display()
    
    def update_file_info(self):
        """تحديث معلومات الملف"""
        try:
            if os.path.exists(self.file_path):
                self.file_size = os.path.getsize(self.file_path)
                # التحقق من صحة ملف PDF
                if self.file_path.lower().endswith('.pdf'):
                    self.is_valid = self.validate_pdf()
                else:
                    self.is_valid = True
            else:
                self.is_valid = False
                self.error_message = "الملف غير موجود"
        except Exception as e:
            self.is_valid = False
            self.error_message = f"خطأ في قراءة الملف: {str(e)}"
    
    def validate_pdf(self):
        """التحقق من صحة ملف PDF"""
        try:
            with open(self.file_path, 'rb') as file:
                header = file.read(8)
                if not header.startswith(b'%PDF-'):
                    self.error_message = "ملف PDF غير صالح"
                    return False
            return True
        except Exception as e:
            self.error_message = f"خطأ في فحص PDF: {str(e)}"
            return False
    
    def update_display(self):
        """تحديث عرض العنصر"""
        file_name = os.path.basename(self.file_path)
        size_text = self.format_file_size(self.file_size)
        
        if self.is_valid:
            # الحجم على اليسار واسم الملف على اليمين
            display_text = f"الحجم: {size_text}                                                    {file_name}"
            self.setToolTip(self.file_path)
        else:
            display_text = f"{self.error_message}                                                    خطأ: {file_name}"
            self.setToolTip(f"خطأ: {self.error_message}")
        
        self.setText(display_text)
    
    def format_file_size(self, size_bytes):
        """تنسيق حجم الملف"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

class DraggableListWidget(QListWidget):
    """قائمة قابلة للسحب والإفلات"""
    
    files_reordered = Signal(list)  # إشارة عند إعادة ترتيب الملفات
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.drag_start_position = QPoint()
        
        # تخصيص المظهر مع تأثيرات محسنة
        self.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 55, 72, 0.3),
                    stop:1 rgba(26, 32, 44, 0.5));
                border: 1px solid rgba(255, 111, 0, 0.2);
                border-radius: 8px;
                outline: none;
                selection-background-color: transparent;
                padding: 4px;
            }
            QListWidget::item {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(45, 55, 72, 0.8),
                    stop:1 rgba(45, 55, 72, 0.6));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                margin: 3px;
                color: #e2e8f0;
                font-weight: 500;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 111, 0, 0.3),
                    stop:1 rgba(255, 111, 0, 0.1));
                border: 1px solid rgba(255, 111, 0, 0.6);
                color: white;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 111, 0, 0.5),
                    stop:1 rgba(255, 111, 0, 0.3));
                border: 2px solid #ff6f00;
                color: white;
                font-weight: bold;
            }
            QScrollBar:vertical {
                background: rgba(45, 55, 72, 0.5);
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6f00,
                    stop:1 #e65100);
                min-height: 20px;
                border-radius: 4px;
                margin: 1px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff8f00,
                    stop:1 #ff6f00);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
    
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
            self.start_drag(item)
    
    def start_drag(self, item):
        """بدء عملية السحب مع التأثيرات البصرية"""
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(item.text())
        drag.setMimeData(mime_data)

        # إنشاء صورة شفافة للسحب
        rect = self.visualItemRect(item)
        pixmap = QPixmap(rect.size())
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setOpacity(0.7)

        # رسم خلفية العنصر
        painter.fillRect(pixmap.rect(), Qt.darkGray)
        painter.setPen(Qt.white)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, os.path.basename(item.file_path) if hasattr(item, 'file_path') else item.text())
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))

        # تنفيذ السحب
        drop_action = drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        """عند دخول عنصر مسحوب"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet(self.styleSheet() + """
                QListWidget {
                    border: 2px dashed #ff6f00;
                    background: rgba(255, 111, 0, 0.1);
                }
            """)

    def dragLeaveEvent(self, event):
        """عند خروج عنصر مسحوب"""
        self.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
                selection-background-color: rgba(255, 111, 0, 0.3);
            }
            QListWidget::item {
                background: rgba(45, 55, 72, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px;
                margin: 2px;
                color: #e2e8f0;
            }
            QListWidget::item:hover {
                background: rgba(255, 111, 0, 0.2);
                border-color: rgba(255, 111, 0, 0.5);
            }
            QListWidget::item:selected {
                background: rgba(255, 111, 0, 0.3);
                border-color: #ff6f00;
            }
        """)
    
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []  # قائمة مسارات الملفات
        self.setup_ui()
        self.hide()  # مخفي افتراضياً
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # التخطيط الرئيسي
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)
        
        # عنوان الفريم
        self.title_label = QLabel("الملفات المختارة")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ff6f00;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                border-bottom: 1px solid rgba(255, 111, 0, 0.3);
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(self.title_label)
        
        # قائمة الملفات - مساحة أكبر
        self.file_list = DraggableListWidget()
        self.file_list.setMaximumHeight(180)  # ارتفاع أكبر (زيادة 60px)
        self.file_list.setMinimumHeight(120)  # حد أدنى للارتفاع
        self.file_list.files_reordered.connect(self.on_files_reordered)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.file_list)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        # استخدام زر أيقونة SVG لمسح الكل (سيطبق اللون الأحمر تلقائياً)
        self.clear_all_btn = create_action_button("delete", 16, "مسح جميع الملفات")
        self.clear_all_btn.setMaximumWidth(40)
        self.clear_all_btn.clicked.connect(self.clear_all_files)
        
        buttons_layout.addWidget(self.clear_all_btn)
        buttons_layout.addStretch()
        
        # عداد الملفات
        self.count_label = QLabel("0 ملف")
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
        
        # تحديد الحد الأدنى والأقصى للارتفاع - مساحة أكبر
        self.setMinimumHeight(220)  # زيادة 60px
        self.setMaximumHeight(220)
    
    def add_files(self, file_paths):
        """إضافة ملفات جديدة"""
        added_files = []
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)
                item = FileListItem(file_path)
                self.file_list.addItem(item)
                added_files.append(file_path)

        if added_files:
            self.update_display()
            self.files_changed.emit(self.files)

            # إظهار رسالة تأكيد
            count = len(added_files)
            if count == 1:
                self.title_label.setText(f"تم إضافة ملف واحد")
            else:
                self.title_label.setText(f"تم إضافة {count} ملف")

            # إعادة العنوان الأصلي بعد 3 ثوان
            QTimer.singleShot(3000, lambda: self.title_label.setText("الملفات المختارة"))
    
    def remove_file(self, file_path):
        """حذف ملف محدد"""
        if file_path in self.files:
            self.files.remove(file_path)
            
            # حذف العنصر من القائمة
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                if isinstance(item, FileListItem) and item.file_path == file_path:
                    self.file_list.takeItem(i)
                    break
            
            self.update_display()
            self.file_removed.emit(file_path)
            self.files_changed.emit(self.files)
    
    def clear_all_files(self):
        """مسح جميع الملفات"""
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
        self.count_label.setText(f"{count} ملف" if count != 1 else "ملف واحد")
        
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
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(400)  # مدة أطول قليلاً للحجم الأكبر
        self.animation.setStartValue(0)
        self.animation.setEndValue(220)  # الحجم الجديد
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def animate_hide(self):
        """تحريك الاختفاء"""
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(400)  # مدة أطول قليلاً
        self.animation.setStartValue(220)  # الحجم الجديد
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(self.hide)
        self.animation.start()
    
    def get_files(self):
        """الحصول على قائمة الملفات"""
        return self.files.copy()
    
    def get_valid_files(self):
        """الحصول على الملفات الصالحة فقط"""
        valid_files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if isinstance(item, FileListItem) and item.is_valid:
                valid_files.append(item.file_path)
        return valid_files

    def on_item_double_clicked(self, item):
        """معالجة النقر المزدوج على عنصر - حذف الملف"""
        if isinstance(item, FileListItem):
            self.remove_file(item.file_path)

    def contextMenuEvent(self, event):
        """قائمة السياق للنقر بالزر الأيمن"""
        from PySide6.QtWidgets import QMenu

        item = self.file_list.itemAt(self.file_list.mapFromGlobal(event.globalPos()))
        if isinstance(item, FileListItem):
            menu = QMenu(self)

            # حذف الملف
            remove_action = menu.addAction("حذف الملف")
            remove_action.triggered.connect(lambda: self.remove_file(item.file_path))

            # معلومات الملف
            info_action = menu.addAction("معلومات الملف")
            info_action.triggered.connect(lambda: self.show_file_info(item))

            menu.exec_(event.globalPos())

    def show_file_info(self, item):
        """عرض معلومات الملف"""
        from PySide6.QtWidgets import QMessageBox

        info_text = f"""
        اسم الملف: {os.path.basename(item.file_path)}
        المسار: {item.file_path}
        الحجم: {item.format_file_size(item.file_size)}
        الحالة: {'صالح' if item.is_valid else 'غير صالح'}
        """

        if not item.is_valid:
            info_text += f"\nالخطأ: {item.error_message}"

        QMessageBox.information(self, "معلومات الملف", info_text)

    def refresh_files(self):
        """تحديث معلومات جميع الملفات"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if isinstance(item, FileListItem):
                item.update_file_info()
                item.update_display()
        self.update_display()