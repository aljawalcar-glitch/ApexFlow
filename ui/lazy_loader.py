# -*- coding: utf-8 -*-
"""
نظام التحميل الكسول للصفحات والصور
Lazy Loading System for Pages and Images
"""

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QPixmap
from typing import Dict, Optional, List, Callable
import fitz
import os
import weakref

class LazyPageLoader(QObject):
    """محمل كسول للصفحات - يحمل الصفحات عند الحاجة فقط"""
    
    page_ready = Signal(int, QPixmap)  # رقم الصفحة، الصورة
    loading_started = Signal(int)  # رقم الصفحة
    error_occurred = Signal(int, str)  # رقم الصفحة، رسالة الخطأ
    
    def __init__(self, max_cached_pages: int = 10):
        super().__init__()
        self.file_path = ""
        self.doc = None
        self.total_pages = 0
        
        # تخزين مؤقت للصفحات المحملة
        self.page_cache: Dict[int, QPixmap] = {}
        self.max_cached_pages = max_cached_pages
        self.access_order: List[int] = []  # ترتيب الوصول للـ LRU
        
        # إعدادات التحميل
        self.default_matrix = fitz.Matrix(1.2, 1.2)  # دقة محسنة
        self.loading_queue: List[int] = []
        self.is_loading = False
        
        # مؤقت للتحميل المؤجل
        self.load_timer = QTimer()
        self.load_timer.setSingleShot(True)
        self.load_timer.timeout.connect(self._process_loading_queue)
    
    def set_pdf_file(self, file_path: str) -> bool:
        """تعيين ملف PDF الجديد"""
        try:
            # إغلاق الملف السابق
            if self.doc:
                self.doc.close()
            
            # مسح التخزين المؤقت
            self.clear_cache()
            
            # فتح الملف الجديد
            self.file_path = file_path
            self.doc = fitz.open(file_path)
            self.total_pages = len(self.doc)
            
            print(f"تم تحميل PDF: {os.path.basename(file_path)} ({self.total_pages} صفحة)")
            return True
            
        except Exception as e:
            print(f"خطأ في فتح PDF: {e}")
            return False
    
    def get_page(self, page_number: int, priority: bool = False) -> Optional[QPixmap]:
        """الحصول على صفحة - إما من التخزين المؤقت أو تحميل جديد"""
        if not self.doc or page_number >= self.total_pages or page_number < 0:
            return None
        
        # فحص التخزين المؤقت أولاً
        if page_number in self.page_cache:
            # تحديث ترتيب الوصول
            self._update_access_order(page_number)
            return self.page_cache[page_number]
        
        # إضافة للطابور إذا لم تكن محملة
        if page_number not in self.loading_queue:
            if priority:
                self.loading_queue.insert(0, page_number)  # أولوية عالية
            else:
                self.loading_queue.append(page_number)
        
        # بدء التحميل المؤجل
        if not self.load_timer.isActive():
            self.load_timer.start(50)  # 50ms تأخير
        
        return None
    
    def preload_pages(self, page_numbers: List[int]):
        """تحميل مسبق لصفحات محددة"""
        for page_num in page_numbers:
            if (page_num not in self.page_cache and 
                page_num not in self.loading_queue and
                0 <= page_num < self.total_pages):
                self.loading_queue.append(page_num)
        
        if not self.load_timer.isActive():
            self.load_timer.start(100)  # تأخير أطول للتحميل المسبق
    
    def _process_loading_queue(self):
        """معالجة طابور التحميل"""
        if not self.loading_queue or self.is_loading:
            return
        
        self.is_loading = True
        page_number = self.loading_queue.pop(0)
        
        try:
            self.loading_started.emit(page_number)
            
            # تحميل الصفحة
            page = self.doc[page_number]
            pixmap = page.get_pixmap(matrix=self.default_matrix, alpha=False)
            
            # تحويل إلى QPixmap
            img_data = pixmap.tobytes("ppm")
            from PySide6.QtGui import QImage
            qimg = QImage.fromData(img_data, "PPM")
            qpixmap = QPixmap.fromImage(qimg)
            
            # إضافة للتخزين المؤقت
            self._add_to_cache(page_number, qpixmap)
            
            # إرسال إشارة الانتهاء
            self.page_ready.emit(page_number, qpixmap)
            
        except Exception as e:
            error_msg = f"خطأ في تحميل الصفحة {page_number}: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(page_number, error_msg)
        
        finally:
            self.is_loading = False
            
            # معالجة الصفحة التالية إذا وجدت
            if self.loading_queue:
                self.load_timer.start(10)  # تأخير قصير للصفحة التالية
    
    def _add_to_cache(self, page_number: int, pixmap: QPixmap):
        """إضافة صفحة للتخزين المؤقت مع إدارة الحجم"""
        # إزالة الصفحات القديمة إذا امتلأ التخزين المؤقت
        while len(self.page_cache) >= self.max_cached_pages:
            # إزالة أقدم صفحة (LRU)
            oldest_page = self.access_order.pop(0)
            if oldest_page in self.page_cache:
                del self.page_cache[oldest_page]
        
        # إضافة الصفحة الجديدة
        self.page_cache[page_number] = pixmap
        self._update_access_order(page_number)
    
    def _update_access_order(self, page_number: int):
        """تحديث ترتيب الوصول للـ LRU"""
        if page_number in self.access_order:
            self.access_order.remove(page_number)
        self.access_order.append(page_number)
    
    def clear_cache(self):
        """مسح التخزين المؤقت"""
        self.page_cache.clear()
        self.access_order.clear()
        self.loading_queue.clear()
    
    def get_cache_info(self) -> dict:
        """معلومات التخزين المؤقت للتشخيص"""
        return {
            "cached_pages": len(self.page_cache),
            "max_pages": self.max_cached_pages,
            "queue_length": len(self.loading_queue),
            "total_pages": self.total_pages,
            "memory_usage_mb": len(self.page_cache) * 2  # تقدير تقريبي
        }
    
    def cleanup(self):
        """تنظيف الموارد"""
        self.load_timer.stop()
        self.clear_cache()
        if self.doc:
            self.doc.close()
            self.doc = None

class LazyImageLoader(QObject):
    """محمل كسول للصور"""
    
    image_ready = Signal(str, QPixmap)  # مسار الصورة، الصورة
    loading_started = Signal(str)  # مسار الصورة
    error_occurred = Signal(str, str)  # مسار الصورة، رسالة الخطأ
    
    def __init__(self, max_cached_images: int = 50):
        super().__init__()
        
        # تخزين مؤقت للصور
        self.image_cache: Dict[str, QPixmap] = {}
        self.max_cached_images = max_cached_images
        self.access_order: List[str] = []
        
        # طابور التحميل
        self.loading_queue: List[str] = []
        self.is_loading = False
        
        # إعدادات التحميل
        self.default_size = (90, 90)
        
        # مؤقت للتحميل المؤجل
        self.load_timer = QTimer()
        self.load_timer.setSingleShot(True)
        self.load_timer.timeout.connect(self._process_loading_queue)
    
    def get_image(self, image_path: str, size: tuple = None, priority: bool = False) -> Optional[QPixmap]:
        """الحصول على صورة - إما من التخزين المؤقت أو تحميل جديد"""
        if not os.path.exists(image_path):
            return None
        
        # استخدام الحجم الافتراضي إذا لم يُحدد
        if size is None:
            size = self.default_size
        
        # مفتاح التخزين المؤقت يتضمن الحجم
        cache_key = f"{image_path}_{size[0]}x{size[1]}"
        
        # فحص التخزين المؤقت
        if cache_key in self.image_cache:
            self._update_access_order(cache_key)
            return self.image_cache[cache_key]
        
        # إضافة للطابور
        queue_item = (image_path, size, cache_key)
        if queue_item not in [(item[0], item[1], item[2]) for item in self.loading_queue]:
            if priority:
                self.loading_queue.insert(0, queue_item)
            else:
                self.loading_queue.append(queue_item)
        
        # بدء التحميل المؤجل
        if not self.load_timer.isActive():
            self.load_timer.start(30)  # 30ms تأخير
        
        return None
    
    def _process_loading_queue(self):
        """معالجة طابور تحميل الصور"""
        if not self.loading_queue or self.is_loading:
            return
        
        self.is_loading = True
        image_path, size, cache_key = self.loading_queue.pop(0)
        
        try:
            self.loading_started.emit(image_path)
            
            # تحميل الصورة
            pixmap = QPixmap(image_path)
            
            if not pixmap.isNull():
                # تغيير الحجم مع تحسين الأداء
                scaled_pixmap = pixmap.scaled(
                    size[0], size[1],
                    aspectRatioMode=1,  # KeepAspectRatio
                    transformMode=1     # FastTransformation
                )
                
                # إضافة للتخزين المؤقت
                self._add_to_cache(cache_key, scaled_pixmap)
                
                # إرسال إشارة الانتهاء
                self.image_ready.emit(image_path, scaled_pixmap)
            else:
                self.error_occurred.emit(image_path, "فشل في تحميل الصورة")
                
        except Exception as e:
            error_msg = f"خطأ في تحميل الصورة: {str(e)}"
            self.error_occurred.emit(image_path, error_msg)
        
        finally:
            self.is_loading = False
            
            # معالجة الصورة التالية
            if self.loading_queue:
                self.load_timer.start(5)  # تأخير قصير
    
    def _add_to_cache(self, cache_key: str, pixmap: QPixmap):
        """إضافة صورة للتخزين المؤقت"""
        # إزالة الصور القديمة إذا امتلأ التخزين المؤقت
        while len(self.image_cache) >= self.max_cached_images:
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.image_cache:
                del self.image_cache[oldest_key]
        
        # إضافة الصورة الجديدة
        self.image_cache[cache_key] = pixmap
        self._update_access_order(cache_key)
    
    def _update_access_order(self, cache_key: str):
        """تحديث ترتيب الوصول"""
        if cache_key in self.access_order:
            self.access_order.remove(cache_key)
        self.access_order.append(cache_key)
    
    def clear_cache(self):
        """مسح التخزين المؤقت"""
        self.image_cache.clear()
        self.access_order.clear()
        self.loading_queue.clear()
    
    def cleanup(self):
        """تنظيف الموارد"""
        self.load_timer.stop()
        self.clear_cache()

# المثيلات العامة
global_page_loader = LazyPageLoader()
global_image_loader = LazyImageLoader()
