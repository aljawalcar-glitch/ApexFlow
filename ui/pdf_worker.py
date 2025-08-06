# -*- coding: utf-8 -*-
"""
نظام Worker Threads لمعالجة PDF بدون تجميد الواجهة
PDF Worker Threads System for Non-blocking UI
"""

from PySide6.QtCore import QThread, QObject, Signal, QMutex, QWaitCondition
from PySide6.QtGui import QPixmap, QImage
import fitz
import os
from typing import List, Optional

class PDFLoadWorker(QObject):
    """Worker لتحميل ملفات PDF في خيط منفصل"""
    
    # الإشارات
    page_loaded = Signal(int, object)  # رقم الصفحة، pixmap
    loading_progress = Signal(int, int)  # الصفحة الحالية، المجموع
    loading_finished = Signal(bool, str)  # نجح، رسالة
    error_occurred = Signal(str)  # رسالة خطأ
    
    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.should_stop = False
        self.mutex = QMutex()
        
    def load_pdf(self, file_path: str, max_pages: int = 50):
        """تحميل PDF مع حد أقصى للصفحات لتجنب استهلاك الذاكرة"""
        self.file_path = file_path
        self.should_stop = False
        
        try:
            doc = fitz.open(file_path)
            total_pages = min(len(doc), max_pages)  # حد أقصى للصفحات
            
            self.loading_progress.emit(0, total_pages)
            
            # تحميل الصفحات تدريجياً
            for page_num in range(total_pages):
                # فحص إذا تم طلب الإيقاف
                self.mutex.lock()
                if self.should_stop:
                    self.mutex.unlock()
                    break
                self.mutex.unlock()
                
                try:
                    page = doc[page_num]
                    
                    # تحميل بدقة محسنة (ليس عالية جداً)
                    matrix = fitz.Matrix(1.2, 1.2)  # 1.2x بدلاً من 2.0x
                    pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                    
                    # تحويل إلى QPixmap
                    img_data = pixmap.tobytes("ppm")
                    qimg = QImage.fromData(img_data, "PPM")
                    qpixmap = QPixmap.fromImage(qimg)
                    
                    # إرسال الصفحة المحملة
                    self.page_loaded.emit(page_num, qpixmap)
                    self.loading_progress.emit(page_num + 1, total_pages)
                    
                    # إعطاء فرصة للخيط الرئيسي
                    QThread.msleep(10)  # 10ms راحة
                    
                except Exception as e:
                    print(f"خطأ في تحميل الصفحة {page_num}: {e}")
                    continue
            
            doc.close()
            self.loading_finished.emit(True, f"تم تحميل {total_pages} صفحة بنجاح")
            
        except Exception as e:
            error_msg = f"خطأ في تحميل PDF: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.loading_finished.emit(False, error_msg)
    
    def stop_loading(self):
        """إيقاف عملية التحميل"""
        self.mutex.lock()
        self.should_stop = True
        self.mutex.unlock()

class ImageLoadWorker(QObject):
    """Worker لتحميل الصور في خيط منفصل"""
    
    # الإشارات
    image_loaded = Signal(str, QPixmap)  # مسار الصورة، QPixmap
    loading_finished = Signal()
    error_occurred = Signal(str, str)  # مسار الصورة، رسالة خطأ
    
    def __init__(self):
        super().__init__()
        self.image_queue = []
        self.should_stop = False
        self.mutex = QMutex()
    
    def load_images(self, image_paths: List[str], target_size: tuple = (90, 90)):
        """تحميل قائمة من الصور"""
        self.image_queue = image_paths.copy()
        self.should_stop = False
        
        for image_path in self.image_queue:
            # فحص إذا تم طلب الإيقاف
            self.mutex.lock()
            if self.should_stop:
                self.mutex.unlock()
                break
            self.mutex.unlock()
            
            try:
                if os.path.exists(image_path):
                    # تحميل الصورة
                    pixmap = QPixmap(image_path)
                    
                    if not pixmap.isNull():
                        # تغيير الحجم مع تحسين الأداء
                        scaled_pixmap = pixmap.scaled(
                            target_size[0], target_size[1],
                            aspectRatioMode=1,  # KeepAspectRatio
                            transformMode=1     # FastTransformation بدلاً من SmoothTransformation
                        )
                        
                        self.image_loaded.emit(image_path, scaled_pixmap)
                    else:
                        self.error_occurred.emit(image_path, "فشل في تحميل الصورة")
                else:
                    self.error_occurred.emit(image_path, "الملف غير موجود")
                
                # راحة قصيرة
                QThread.msleep(5)
                
            except Exception as e:
                self.error_occurred.emit(image_path, f"خطأ: {str(e)}")
        
        self.loading_finished.emit()
    
    def stop_loading(self):
        """إيقاف عملية التحميل"""
        self.mutex.lock()
        self.should_stop = True
        self.mutex.unlock()

class PDFProcessWorker(QObject):
    """Worker لمعالجة PDF (ضغط، تدوير، إلخ) في خيط منفصل"""
    
    # الإشارات
    process_progress = Signal(int, int)  # التقدم الحالي، المجموع
    process_finished = Signal(bool, str)  # نجح، رسالة
    error_occurred = Signal(str)  # رسالة خطأ
    
    def __init__(self):
        super().__init__()
        self.should_stop = False
        self.mutex = QMutex()
    
    def compress_pdf(self, input_file: str, output_file: str, compression_level: int = 3):
        """ضغط PDF في خيط منفصل"""
        self.should_stop = False
        
        try:
            self.process_progress.emit(0, 100)
            
            # فتح الملف
            doc = fitz.open(input_file)
            total_pages = len(doc)
            
            self.process_progress.emit(20, 100)
            
            # إعدادات الضغط حسب المستوى
            compression_settings = {
                1: {"garbage": 1, "deflate": True},
                2: {"garbage": 2, "deflate": True, "clean": True},
                3: {"garbage": 3, "deflate": True, "clean": True, "linear": True},
                4: {"garbage": 4, "deflate": True, "clean": True, "linear": True},
                5: {"garbage": 4, "deflate": True, "clean": True, "linear": True, "ascii": True}
            }
            
            options = compression_settings.get(compression_level, compression_settings[3])
            
            self.process_progress.emit(50, 100)
            
            # فحص إذا تم طلب الإيقاف
            self.mutex.lock()
            if self.should_stop:
                self.mutex.unlock()
                doc.close()
                return
            self.mutex.unlock()
            
            # حفظ الملف المضغوط
            doc.save(output_file, **options)
            doc.close()
            
            self.process_progress.emit(100, 100)
            
            # حساب نسبة الضغط
            original_size = os.path.getsize(input_file)
            compressed_size = os.path.getsize(output_file)
            compression_ratio = ((original_size - compressed_size) / original_size) * 100
            
            success_msg = f"تم الضغط بنجاح! توفير {compression_ratio:.1f}% من الحجم"
            self.process_finished.emit(True, success_msg)
            
        except Exception as e:
            error_msg = f"خطأ في ضغط PDF: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.process_finished.emit(False, error_msg)
    
    def stop_process(self):
        """إيقاف عملية المعالجة"""
        self.mutex.lock()
        self.should_stop = True
        self.mutex.unlock()

class WorkerManager:
    """مدير العمال - يدير جميع الخيوط"""
    
    def __init__(self):
        self.pdf_thread = None
        self.pdf_worker = None
        self.image_thread = None
        self.image_worker = None
        self.process_thread = None
        self.process_worker = None
    
    def start_pdf_loading(self, file_path: str, max_pages: int = 50):
        """بدء تحميل PDF"""
        self.stop_pdf_loading()  # إيقاف أي عملية سابقة
        
        self.pdf_thread = QThread()
        self.pdf_worker = PDFLoadWorker()
        self.pdf_worker.moveToThread(self.pdf_thread)
        
        # ربط الإشارات
        self.pdf_thread.started.connect(lambda: self.pdf_worker.load_pdf(file_path, max_pages))
        self.pdf_worker.loading_finished.connect(self.pdf_thread.quit)
        self.pdf_thread.finished.connect(self.pdf_thread.deleteLater)
        
        self.pdf_thread.start()
        return self.pdf_worker
    
    def stop_pdf_loading(self):
        """إيقاف تحميل PDF"""
        if self.pdf_worker:
            self.pdf_worker.stop_loading()
        if self.pdf_thread and self.pdf_thread.isRunning():
            self.pdf_thread.quit()
            if not self.pdf_thread.wait(3000):  # انتظار 3 ثواني
                # إذا لم يتوقف الخيط، قم بإنهائه بالقوة
                self.pdf_thread.terminate()
                self.pdf_thread.wait(1000)  # انتظار ثانية واحدة للتأكد من الإنهاء
            # تنظيف المراجع
            if self.pdf_worker:
                self.pdf_worker.deleteLater()
                self.pdf_worker = None
    
    def start_image_loading(self, image_paths: List[str], target_size: tuple = (90, 90)):
        """بدء تحميل الصور"""
        self.stop_image_loading()  # إيقاف أي عملية سابقة
        
        self.image_thread = QThread()
        self.image_worker = ImageLoadWorker()
        self.image_worker.moveToThread(self.image_thread)
        
        # ربط الإشارات
        self.image_thread.started.connect(lambda: self.image_worker.load_images(image_paths, target_size))
        self.image_worker.loading_finished.connect(self.image_thread.quit)
        self.image_thread.finished.connect(self.image_thread.deleteLater)
        
        self.image_thread.start()
        return self.image_worker
    
    def stop_image_loading(self):
        """إيقاف تحميل الصور"""
        if self.image_worker:
            self.image_worker.stop_loading()
        if self.image_thread and self.image_thread.isRunning():
            self.image_thread.quit()
            if not self.image_thread.wait(3000):  # انتظار 3 ثواني
                # إذا لم يتوقف الخيط، قم بإنهائه بالقوة
                self.image_thread.terminate()
                self.image_thread.wait(1000)  # انتظار ثانية واحدة للتأكد من الإنهاء
            # تنظيف المراجع
            if self.image_worker:
                self.image_worker.deleteLater()
                self.image_worker = None
    
    def cleanup(self):
        """تنظيف جميع الخيوط"""
        self.stop_pdf_loading()
        self.stop_image_loading()

        # التأكد من تنظيف أي خيوط معالجة متبقية
        if hasattr(self, 'process_thread') and self.process_thread:
            if self.process_thread.isRunning():
                self.process_thread.quit()
                if not self.process_thread.wait(3000):
                    self.process_thread.terminate()
                    self.process_thread.wait(1000)
            if hasattr(self, 'process_worker') and self.process_worker:
                self.process_worker.deleteLater()
                self.process_worker = None
            self.process_thread.deleteLater()
            self.process_thread = None

# المثيل العام
global_worker_manager = WorkerManager()
