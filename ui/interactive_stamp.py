# -*- coding: utf-8 -*-
"""
نظام الختم التفاعلي
Interactive Stamp System
"""

from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt, QRectF, Signal, QObject

class InteractiveStamp(QGraphicsPixmapItem):
    """ختم تفاعلي قابل للتحريك وتغيير الحجم"""
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        
        self.image_path = image_path
        self.original_pixmap = None
        self.scale_factor = 1.0
        self.opacity_value = 0.7  # شفافية افتراضية
        self.is_being_moved = False
        self.is_being_resized = False
        self.resize_handle_size = 10  # حجم مقابض مثل Foxit
        
        # تحميل الصورة
        self.load_stamp_image()
        
        # إعداد الخصائص
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setOpacity(self.opacity_value)
        
        # تفعيل تتبع الماوس
        self.setAcceptHoverEvents(True)
        
    def load_stamp_image(self):
        """تحميل صورة الختم مع حفظ المعلومات الأصلية"""
        try:
            self.original_pixmap = QPixmap(self.image_path)
            if not self.original_pixmap.isNull():
                # حفظ الأبعاد الأصلية
                self.original_width = self.original_pixmap.width()
                self.original_height = self.original_pixmap.height()

                # تحديد حجم العرض الافتراضي (100x100 بكسل كحد أقصى)
                display_pixmap = self.original_pixmap
                self.initial_scale_factor = 1.0

                if self.original_width > 100 or self.original_height > 100:
                    # حساب عامل التحجيم للعرض الأولي
                    scale_w = 100.0 / self.original_width
                    scale_h = 100.0 / self.original_height
                    self.initial_scale_factor = min(scale_w, scale_h)

                    display_pixmap = self.original_pixmap.scaled(
                        int(self.original_width * self.initial_scale_factor),
                        int(self.original_height * self.initial_scale_factor),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )

                self.setPixmap(display_pixmap)

            else:
                print(f"فشل في تحميل صورة الختم: {self.image_path}")
        except Exception as e:
            print(f"خطأ في تحميل صورة الختم: {e}")
    
    def boundingRect(self):
        """تحديد المنطقة المحيطة بالختم مع مقابض التحجيم"""
        rect = super().boundingRect()
        # إضافة مساحة لمقابض التحجيم
        return rect.adjusted(-self.resize_handle_size, -self.resize_handle_size, 
                           self.resize_handle_size, self.resize_handle_size)
    
    def paint(self, painter, option, widget):
        """رسم الختم بسيط"""
        # رسم الصورة الأساسية فقط
        super().paint(painter, option, widget)
    

    
    def zoom_in(self):
        """تكبير الختم"""
        new_scale = min(self.scale_factor + 0.03, 3.0)  # زيادة 3% مع حد أقصى 3x
        self.apply_scale(new_scale)

    def zoom_out(self):
        """تصغير الختم"""
        new_scale = max(self.scale_factor - 0.03, 0.2)  # تقليل 3% مع حد أدنى 0.2x
        self.apply_scale(new_scale)
    
    def mousePressEvent(self, event):
        """التعامل مع الضغط على الماوس - بسيط"""
        if event.button() == Qt.LeftButton:
            # تحديد الختم وتحريك عادي
            self.setSelected(True)
            self.is_being_moved = True
            self.setCursor(Qt.ClosedHandCursor)
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """التعامل مع حركة الماوس - بسيط"""
        if self.is_being_moved:
            super().mouseMoveEvent(event)
        else:
            # تغيير مؤشر الماوس بسيط
            if self.isSelected():
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        """التعامل مع تحرير الماوس"""
        self.is_being_moved = False
        self.setCursor(Qt.ArrowCursor)  # إعادة المؤشر العادي
        super().mouseReleaseEvent(event)

    def hoverMoveEvent(self, event):
        """التعامل مع حركة الماوس فوق الختم - بسيط"""
        if not self.is_being_moved and self.isSelected():
            self.setCursor(Qt.OpenHandCursor)  # مؤشر اليد للتحريك
        elif not self.isSelected():
            self.setCursor(Qt.ArrowCursor)  # مؤشر عادي عند عدم التحديد
        super().hoverMoveEvent(event)
    



    
    def apply_scale(self, new_scale):
        """تطبيق مقياس جديد على الختم مع حفظ دقيق للمعلومات"""
        if not self.original_pixmap:
            return

        self.scale_factor = new_scale

        # حساب الحجم النهائي بناءً على الحجم الأصلي والمقياس الكامل
        final_scale = self.initial_scale_factor * new_scale
        new_width = int(self.original_width * final_scale)
        new_height = int(self.original_height * final_scale)

        # تطبيق التحجيم من الصورة الأصلية للحصول على أفضل جودة
        scaled_pixmap = self.original_pixmap.scaled(
            new_width, new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)


    
    def set_opacity(self, opacity):
        """تعيين شفافية الختم"""
        self.opacity_value = max(0.1, min(1.0, opacity))
        self.setOpacity(self.opacity_value)
    
    def get_stamp_data(self):
        """الحصول على بيانات الختم للحفظ مع معلومات دقيقة"""
        # حساب المقياس النهائي الفعلي
        final_scale = self.initial_scale_factor * self.scale_factor if hasattr(self, 'initial_scale_factor') else self.scale_factor

        # الحصول على الأبعاد الحالية
        current_pixmap = self.pixmap()
        current_width = current_pixmap.width()
        current_height = current_pixmap.height()

        # تعديل الموضع لمعالجة مشكلة الانزياح للأسفل
        # معامل التحكم في الانزياح العمودي (يمكن تعديله حسب الحاجة)
        vertical_offset_factor = 50  # زيادة معامل الانزياح العمودي لجعل الختم ينزاح لأعلى بشكل أكبر
        
        pos_x = self.pos().x()
        pos_y = self.pos().y() - vertical_offset_factor  # تعديل الموضع العمودي باستخدام المعامل
        
        stamp_data = {
            'image_path': self.image_path,
            'position': (pos_x, pos_y),
            'scale': self.scale_factor,
            'opacity': self.opacity_value,
            # معلومات إضافية للحفظ الدقيق
            'original_width': getattr(self, 'original_width', current_width),
            'original_height': getattr(self, 'original_height', current_height),
            'initial_scale_factor': getattr(self, 'initial_scale_factor', 1.0),
            'final_scale': final_scale,
            'current_width': current_width,
            'current_height': current_height
        }

        print(f"بيانات الختم للحفظ: الموضع=({stamp_data['position'][0]:.1f}, {stamp_data['position'][1]:.1f}), المقياس النهائي={final_scale:.3f}")
        return stamp_data

class StampPreview(QGraphicsPixmapItem):
    """معاينة الختم الشفاف الذي يتبع الماوس"""
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        
        self.image_path = image_path
        self.setOpacity(0.5)  # شفافية للمعاينة
        
        # تحميل الصورة
        self.load_preview_image()
        
        # إخفاء المعاينة في البداية
        self.setVisible(False)
        
    def load_preview_image(self):
        """تحميل صورة المعاينة"""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # تحديد حجم مناسب للمعاينة
                if pixmap.width() > 80 or pixmap.height() > 80:
                    scaled_pixmap = pixmap.scaled(
                        80, 80, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.setPixmap(scaled_pixmap)
                else:
                    self.setPixmap(pixmap)
        except Exception as e:
            print(f"خطأ في تحميل معاينة الختم: {e}")
    
    def update_position(self, scene_pos):
        """تحديث موضع المعاينة"""
        # وضع المعاينة بحيث تكون وسط الصورة عند موضع الماوس
        pixmap_rect = self.pixmap().rect()
        self.setPos(scene_pos.x() - pixmap_rect.width()/2, 
                   scene_pos.y() - pixmap_rect.height()/2)
    
    def show_preview(self):
        """إظهار المعاينة"""
        self.setVisible(True)
    
    def hide_preview(self):
        """إخفاء المعاينة"""
        self.setVisible(False)
