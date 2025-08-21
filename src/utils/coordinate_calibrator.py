# -*- coding: utf-8 -*-
"""
معايرة الإحداثيات - تحويل دقيق بين إحداثيات العرض وإحداثيات PDF
Coordinate Calibrator - Accurate conversion between view and PDF coordinates
"""

import logging
import fitz
from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QTransform

# إعداد اللوجر
logger = logging.getLogger(__name__)
info = logger.info
error = logger.error
warning = logger.warning


class CoordinateCalibrator:
    """فئة معايرة الإحداثيات بين العرض والـ PDF"""
    
    def __init__(self, pdf_path=None, page_number=0):
        self.pdf_path = pdf_path
        self.page_number = page_number
        self.pdf_page_rect = None
        self.view_page_rect = None
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0
        
        if pdf_path:
            self.load_pdf_page_info()
    
    def load_pdf_page_info(self):
        """تحميل معلومات صفحة PDF"""
        try:
            doc = fitz.open(self.pdf_path)
            if self.page_number < len(doc):
                page = doc[self.page_number]
                self.pdf_page_rect = page.rect
                info(f"تم تحميل معلومات الصفحة {self.page_number + 1}: {self.pdf_page_rect.width:.1f} x {self.pdf_page_rect.height:.1f}")
            doc.close()
        except Exception as e:
            error(f"خطأ في تحميل معلومات PDF: {e}")
    
    def set_view_page_rect(self, view_rect):
        """تعيين مستطيل الصفحة في العرض"""
        self.view_page_rect = view_rect
        self.calculate_scale_factors()
    
    def calculate_scale_factors(self):
        """حساب عوامل التحجيم بين العرض والـ PDF"""
        if self.pdf_page_rect and self.view_page_rect:
            self.scale_factor_x = self.pdf_page_rect.width / self.view_page_rect.width()
            self.scale_factor_y = self.pdf_page_rect.height / self.view_page_rect.height()
            
            info(f"عوامل التحجيم المحسوبة:")
            info(f"  - X: {self.scale_factor_x:.4f}")
            info(f"  - Y: {self.scale_factor_y:.4f}")
    
    def view_to_pdf_coordinates(self, view_x, view_y):
        """تحويل إحداثيات العرض إلى إحداثيات PDF"""
        if not self.pdf_page_rect:
            return view_x, view_y
        
        # تحويل الإحداثيات مع مراعاة الاختلاف في نظام الإحداثيات
        pdf_x = view_x * self.scale_factor_x
        pdf_y = self.pdf_page_rect.height - (view_y * self.scale_factor_y)
        
        return pdf_x, pdf_y
    
    def pdf_to_view_coordinates(self, pdf_x, pdf_y):
        """تحويل إحداثيات PDF إلى إحداثيات العرض"""
        if not self.pdf_page_rect:
            return pdf_x, pdf_y
        
        # تحويل الإحداثيات العكسي
        view_x = pdf_x / self.scale_factor_x
        view_y = (self.pdf_page_rect.height - pdf_y) / self.scale_factor_y
        
        return view_x, view_y
    
    def scale_dimensions(self, view_width, view_height):
        """تحويل أبعاد العرض إلى أبعاد PDF"""
        pdf_width = view_width * self.scale_factor_x
        pdf_height = view_height * self.scale_factor_y
        return pdf_width, pdf_height
    
    def get_calibration_info(self):
        """الحصول على معلومات المعايرة"""
        return {
            'pdf_page_rect': self.pdf_page_rect,
            'view_page_rect': self.view_page_rect,
            'scale_factor_x': self.scale_factor_x,
            'scale_factor_y': self.scale_factor_y,
            'is_calibrated': self.pdf_page_rect is not None and self.view_page_rect is not None
        }


def create_calibrator_for_stamp_data(stamp_data, pdf_path, page_number, view_transform=None):
    """
    إنشاء معايرة مخصصة لبيانات ختم معين
    
    Args:
        stamp_data: بيانات الختم
        pdf_path: مسار ملف PDF
        page_number: رقم الصفحة
        view_transform: تحويل العرض (اختياري)
    
    Returns:
        dict: بيانات الختم المعايرة
    """
    try:
        calibrator = CoordinateCalibrator(pdf_path, page_number)
        
        # استخدام أبعاد الصفحة الافتراضية إذا لم يتم توفير تحويل العرض
        if view_transform:
            # حساب أبعاد العرض من التحويل
            view_rect = QRectF(0, 0, 
                             calibrator.pdf_page_rect.width / view_transform.m11(),
                             calibrator.pdf_page_rect.height / view_transform.m22())
        else:
            # استخدام أبعاد افتراضية
            view_rect = QRectF(0, 0, 800, 600)
        
        calibrator.set_view_page_rect(view_rect)
        
        # تحويل الإحداثيات
        position = stamp_data['position']
        pdf_x, pdf_y = calibrator.view_to_pdf_coordinates(position[0], position[1])
        
        # تحويل الأبعاد
        current_width = stamp_data.get('current_width', 100)
        current_height = stamp_data.get('current_height', 100)
        pdf_width, pdf_height = calibrator.scale_dimensions(current_width, current_height)
        
        # إنشاء بيانات معايرة
        calibrated_data = stamp_data.copy()
        calibrated_data.update({
            'calibrated_position': (pdf_x, pdf_y),
            'calibrated_width': pdf_width,
            'calibrated_height': pdf_height,
            'calibration_info': calibrator.get_calibration_info()
        })
        
        info(f"معايرة الختم:")
        info(f"  - الموضع الأصلي: ({position[0]:.1f}, {position[1]:.1f})")
        info(f"  - الموضع المعاير: ({pdf_x:.1f}, {pdf_y:.1f})")
        info(f"  - الأبعاد الأصلية: ({current_width} x {current_height})")
        info(f"  - الأبعاد المعايرة: ({pdf_width:.1f} x {pdf_height:.1f})")
        
        return calibrated_data
        
    except Exception as e:
        error(f"خطأ في معايرة بيانات الختم: {e}")
        return stamp_data


def auto_calibrate_view_scale(graphics_view):
    """
    معايرة تلقائية لعامل تحجيم العرض
    
    Args:
        graphics_view: عنصر QGraphicsView
    
    Returns:
        float: عامل التحجيم المحسوب
    """
    try:
        if hasattr(graphics_view, 'transform'):
            transform = graphics_view.transform()
            # استخدام المتوسط بين عوامل التحجيم الأفقي والعمودي
            scale_x = transform.m11()
            scale_y = transform.m22()
            average_scale = (scale_x + scale_y) / 2.0
            
            info(f"معايرة تلقائية للعرض:")
            info(f"  - تحجيم X: {scale_x:.4f}")
            info(f"  - تحجيم Y: {scale_y:.4f}")
            info(f"  - المتوسط: {average_scale:.4f}")
            
            return average_scale
        else:
            warning("تعذر الحصول على تحويل العرض، استخدام القيمة الافتراضية")
            return 1.0
            
    except Exception as e:
        error(f"خطأ في المعايرة التلقائية: {e}")
        return 1.0


def validate_coordinates(pdf_rect, x, y, width, height):
    """
    التحقق من صحة الإحداثيات وتصحيحها إذا لزم الأمر
    
    Args:
        pdf_rect: مستطيل صفحة PDF
        x, y: إحداثيات الموضع
        width, height: الأبعاد
    
    Returns:
        tuple: الإحداثيات والأبعاد المصححة
    """
    # التأكد من أن الختم داخل حدود الصفحة
    corrected_x = max(0, min(x, pdf_rect.width - width))
    corrected_y = max(0, min(y, pdf_rect.height - height))
    
    # التأكد من أن الأبعاد معقولة
    max_width = pdf_rect.width - corrected_x
    max_height = pdf_rect.height - corrected_y
    corrected_width = min(width, max_width)
    corrected_height = min(height, max_height)
    
    if (corrected_x != x or corrected_y != y or 
        corrected_width != width or corrected_height != height):
        info(f"تم تصحيح الإحداثيات:")
        info(f"  - الموضع: ({x:.1f}, {y:.1f}) → ({corrected_x:.1f}, {corrected_y:.1f})")
        info(f"  - الأبعاد: ({width:.1f} x {height:.1f}) → ({corrected_width:.1f} x {corrected_height:.1f})")
    
    return corrected_x, corrected_y, corrected_width, corrected_height
