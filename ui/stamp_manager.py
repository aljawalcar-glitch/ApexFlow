# -*- coding: utf-8 -*-
"""
نافذة إدارة الأختام
Stamp Manager Window
"""

import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget,
    QLabel, QPushButton, QFileDialog, QMessageBox, QFrame
)
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt, QSize, Signal
from .svg_icon_button import create_action_button
from .theme_aware_widget import make_theme_aware
from .notification_system import show_success, show_warning, show_error, show_info

# استيراد النظام الجديد للتحميل السريع
from .lazy_loader import global_image_loader
from .smart_cache import image_cache

def get_stamps_folder():
    """الحصول على مسار مجلد الأختام الصحيح"""
    if getattr(sys, 'frozen', False):
        # في حالة الملف التنفيذي
        app_dir = os.path.dirname(sys.executable)
    else:
        # في حالة بيئة التطوير
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    stamps_folder = os.path.join(app_dir, "data", "stamps")
    return stamps_folder

class StampItem(QLabel):
    """عنصر الختم القابل للنقر"""
    
    clicked = Signal()
    double_clicked = Signal()
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.selected = False
        
        # إعداد العرض
        self.setFixedSize(100, 100)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid transparent;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
                padding: 5px;
            }
            QLabel:hover {
                border: 2px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        
        # تحميل وعرض الصورة
        self.load_image()
        
    def load_image(self):
        """تحميل وعرض الصورة مع تحسين الأداء"""
        try:
            # محاولة الحصول على الصورة من التخزين المؤقت أولاً
            cache_key = f"{self.image_path}_90x90"
            cached_pixmap = image_cache.get(cache_key)

            if cached_pixmap:
                self.setPixmap(cached_pixmap)
                return

            # تحميل مباشر مع تحسين (أسرع من النظام الكسول للأختام الصغيرة)
            if os.path.exists(self.image_path):
                pixmap = QPixmap(self.image_path)
                if not pixmap.isNull():
                    # تغيير حجم مع تحسين الأداء
                    scaled_pixmap = pixmap.scaled(
                        90, 90,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.FastTransformation  # أسرع من SmoothTransformation
                    )

                    self.setPixmap(scaled_pixmap)
                    # إضافة للتخزين المؤقت
                    image_cache.put(cache_key, scaled_pixmap)
                    return

            # إذا فشل التحميل
            self.setText("خطأ في\nالصورة")
            print(f"فشل في تحميل الصورة: {self.image_path}")

        except Exception as e:
            self.setText("خطأ في\nالتحميل")
            print(f"خطأ في تحميل الصورة {self.image_path}: {e}")
    
    def mousePressEvent(self, event):
        """التعامل مع النقر"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """التعامل مع النقر المزدوج"""
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)
    
    def set_selected(self, selected):
        """تعيين حالة التحديد"""
        self.selected = selected
        if selected:
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #ff6f00;
                    border-radius: 8px;
                    background: rgba(255, 111, 0, 0.2);
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid transparent;
                    border-radius: 8px;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 5px;
                }
                QLabel:hover {
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    background: rgba(255, 255, 255, 0.15);
                }
            """)

class StampManager(QDialog):
    """نافذة إدارة الأختام"""
    
    stamp_selected = Signal(str)  # إشارة اختيار الختم
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_handler = make_theme_aware(self, "stamp_manager")

        # الحصول على مسار مجلد الأختام الصحيح
        self.stamps_folder = get_stamps_folder()
        self.selected_stamp = None
        self.stamp_items = []

        # إنشاء مجلد الأختام إذا لم يكن موجوداً
        try:
            os.makedirs(self.stamps_folder, exist_ok=True)
            print(f"مجلد الأختام: {self.stamps_folder}")
        except Exception as e:
            print(f"خطأ في إنشاء مجلد الأختام: {e}")
            # استخدام مجلد مؤقت كبديل
            import tempfile
            self.stamps_folder = os.path.join(tempfile.gettempdir(), "ApexFlow_Stamps")
            os.makedirs(self.stamps_folder, exist_ok=True)
        
        self.setup_ui()
        self.load_stamps()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("إدارة الأختام")
        self.setFixedSize(450, 200)  # حجم مناسب لعرض 3-4 أختام
        self.setModal(True)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # منطقة عرض الأختام مع سكرول أفقي
        self.scroll_area = QScrollArea()
        self.scroll_area.setFixedHeight(120)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        
        # ويدجت الأختام
        self.stamps_widget = QWidget()
        self.stamps_layout = QHBoxLayout(self.stamps_widget)
        self.stamps_layout.setContentsMargins(5, 5, 5, 5)
        self.stamps_layout.setSpacing(10)
        self.stamps_layout.addStretch()  # مساحة مرنة في النهاية
        
        self.scroll_area.setWidget(self.stamps_widget)
        
        # تطبيق نمط السكرول
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.3);
            }
            QScrollBar:horizontal {
                background: rgba(45, 55, 72, 0.3);
                height: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: rgba(255, 255, 255, 0.4);
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(255, 255, 255, 0.6);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
                background: none;
            }
        """)
        
        # شريط الأزرار
        buttons_layout = QHBoxLayout()
        
        # أزرار اليسار (إضافة وحذف)
        self.add_btn = create_action_button("add", 24, "إضافة ختم")
        self.add_btn.clicked.connect(self.add_stamp)
        
        self.delete_btn = create_action_button("delete", 24, "حذف الختم المحدد")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_stamp)
        
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()  # مساحة مرنة في الوسط
        
        # زر اليمين (استخدام)
        self.use_btn = create_action_button("play", 24, "استخدام هذا الختم")
        self.use_btn.setEnabled(False)
        self.use_btn.clicked.connect(self.use_stamp)
        
        buttons_layout.addWidget(self.use_btn)
        
        # إضافة العناصر للتخطيط الرئيسي
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(buttons_layout)
        
    def load_stamps(self):
        """تحميل الأختام من المجلد باستخدام النظام المحسن"""
        # مسح الأختام الحالية
        for item in self.stamp_items:
            item.setParent(None)
        self.stamp_items.clear()

        # البحث عن ملفات الصور
        supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']

        try:
            if not os.path.exists(self.stamps_folder):
                print(f"مجلد الأختام غير موجود: {self.stamps_folder}")
                return

            print(f"البحث عن الأختام في: {self.stamps_folder}")

            # جمع مسارات الصور أولاً
            image_paths = []
            for filename in os.listdir(self.stamps_folder):
                if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                    file_path = os.path.join(self.stamps_folder, filename)
                    if os.path.exists(file_path):
                        image_paths.append(file_path)

            # إنشاء عناصر الأختام مع التحميل المباشر
            for file_path in image_paths:
                self.add_stamp_item(file_path)

            print(f"تم تحميل {len(image_paths)} ختم بنجاح")

        except Exception as e:
            print(f"خطأ في تحميل الأختام: {e}")
            self.notification_manager.show_notification(f"{tr('stamps_load_error')}: {str(e)}", "error")
    
    def add_stamp_item(self, image_path):
        """إضافة عنصر ختم جديد"""
        stamp_item = StampItem(image_path)
        stamp_item.clicked.connect(lambda: self.select_stamp(stamp_item))
        stamp_item.double_clicked.connect(lambda: self.use_stamp_directly(stamp_item))
        
        # إدراج قبل المساحة المرنة
        self.stamps_layout.insertWidget(len(self.stamp_items), stamp_item)
        self.stamp_items.append(stamp_item)
    
    def select_stamp(self, stamp_item):
        """تحديد ختم"""
        # إلغاء تحديد الأختام الأخرى
        for item in self.stamp_items:
            item.set_selected(False)
        
        # تحديد الختم الحالي
        stamp_item.set_selected(True)
        self.selected_stamp = stamp_item
        
        # تفعيل أزرار الحذف والاستخدام
        self.delete_btn.setEnabled(True)
        self.use_btn.setEnabled(True)
    
    def use_stamp_directly(self, stamp_item):
        """استخدام الختم مباشرة (دبل كليك)"""
        self.stamp_selected.emit(stamp_item.image_path)
        self.accept()
    
    def add_stamp(self):
        """إضافة ختم جديد"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "اختر صورة الختم",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)"
        )
        
        if file_path:
            try:
                # نسخ الملف إلى مجلد الأختام
                import shutil
                filename = os.path.basename(file_path)
                destination = os.path.join(self.stamps_folder, filename)
                
                # تجنب الكتابة فوق ملف موجود
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(destination):
                    filename = f"{base_name}_{counter}{ext}"
                    destination = os.path.join(self.stamps_folder, filename)
                    counter += 1
                
                shutil.copy2(file_path, destination)
                
                # إضافة الختم للواجهة
                self.add_stamp_item(destination)
                
                self.notification_manager.show_notification(tr("stamp_added_successfully"), "success", duration=4000)

            except Exception as e:
                self.notification_manager.show_notification(f"{tr('stamp_add_error')}: {str(e)}", "error")
    
    def delete_stamp(self):
        """حذف الختم المحدد"""
        if not self.selected_stamp:
            return
        
        reply = QMessageBox.question(
            self, "تأكيد الحذف", 
            "هل أنت متأكد من حذف هذا الختم؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # حذف الملف
                os.remove(self.selected_stamp.image_path)
                
                # إزالة من الواجهة
                self.selected_stamp.setParent(None)
                self.stamp_items.remove(self.selected_stamp)
                self.selected_stamp = None
                
                # تعطيل الأزرار
                self.delete_btn.setEnabled(False)
                self.use_btn.setEnabled(False)
                
                self.notification_manager.show_notification(tr("stamp_deleted_successfully"), "success", duration=4000)

            except Exception as e:
                self.notification_manager.show_notification(f"{tr('stamp_delete_error')}: {str(e)}", "error")
    
    def use_stamp(self):
        """استخدام الختم المحدد"""
        if self.selected_stamp:
            self.stamp_selected.emit(self.selected_stamp.image_path)
            self.accept()
