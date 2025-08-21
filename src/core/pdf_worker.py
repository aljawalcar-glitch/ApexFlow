# -*- coding: utf-8 -*-
"""
نظام Worker Threads لمعالجة PDF بدون تجميد الواجهة
PDF Worker Threads System for Non-blocking UI
"""

from PySide6.QtCore import QThread, QObject, Signal, QMutex, QWaitCondition, Qt
from PySide6.QtGui import QPixmap, QImage
import fitz
import os
from typing import List, Optional

class ThumbnailWorker(QObject):
    """Worker to generate thumbnails for multiple PDF files."""
    thumbnail_ready = Signal(str, QPixmap)
    finished = Signal()

    def __init__(self, file_paths: List[str]):
        super().__init__()
        self.file_paths = file_paths
        self.should_stop = False

    def run(self):
        for file_path in self.file_paths:
            if self.should_stop:
                break
            try:
                doc = fitz.open(file_path)
                if len(doc) > 0:
                    page = doc.load_page(0)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(img)
                    self.thumbnail_ready.emit(file_path, pixmap)
                doc.close()
            except Exception as e:
                print(f"Error generating thumbnail for {file_path}: {e}")
        self.finished.emit()

    def stop(self):
        self.should_stop = True

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
            if not os.path.exists(file_path):
                self.error_occurred.emit(f"File not found: {file_path}")
                self.loading_finished.emit(False, "File not found")
                return
                
            doc = fitz.open(file_path)
            total_pages = min(len(doc), max_pages)
            
            for page_num in range(total_pages):
                if self.should_stop:
                    break
                    
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                
                self.page_loaded.emit(page_num, pixmap)
                self.loading_progress.emit(page_num + 1, total_pages)
            
            doc.close()
            self.loading_finished.emit(True, "PDF loaded successfully")
            
        except Exception as e:
            self.error_occurred.emit(f"Error loading PDF: {str(e)}")
            self.loading_finished.emit(False, str(e))
    
    def stop(self):
        """إيقاف التحميل"""
        self.should_stop = True


class PDFWorkerManager(QObject):
    """مدير Workers لمعالجة PDF"""
    
    def __init__(self):
        super().__init__()
        self.workers = {}
        self.threads = {}
        self.mutex = QMutex()
        self.thumbnail_worker = None
        self.thumbnail_thread = None
    
    def load_pdf(self, file_path: str, max_pages: int = 50) -> PDFLoadWorker:
        """بدء تحميل PDF في خيط منفصل"""
        self.mutex.lock()
        
        try:
            # إيقاف أي worker قديم لنفس الملف
            if file_path in self.workers:
                self.stop_worker(file_path)
            
            # إنشاء worker و thread جديد
            worker = PDFLoadWorker()
            thread = QThread()
            
            worker.moveToThread(thread)
            
            # ربط الإشارات والوظائف
            thread.started.connect(lambda: worker.load_pdf(file_path, max_pages))
            worker.loading_finished.connect(lambda: self.cleanup_worker(file_path))
            
            # بدء التشغيل
            thread.start()
            
            # حفظ المراجع
            self.workers[file_path] = worker
            self.threads[file_path] = thread
            
            return worker
            
        finally:
            self.mutex.unlock()
    
    def stop_worker(self, file_path: str):
        """إيقاف worker معين"""
        if file_path in self.workers:
            worker = self.workers[file_path]
            worker.stop()
            self.cleanup_worker(file_path)
    
    def cleanup_worker(self, file_path: str):
        """تنظيف worker بعد الانتهاء"""
        if file_path in self.workers:
            worker = self.workers[file_path]
            thread = self.threads[file_path]
            
            # انتظار انتهاء التشغيل
            thread.quit()
            thread.wait(1000)  # انتظار ثانية واحدة كحد أقصى
            
            # حذف المراجع
            del self.workers[file_path]
            del self.threads[file_path]
    
    def cleanup(self):
        """Clean up resources"""
        for worker in self.workers.values():
            worker.stop()
        self.workers.clear()

    def start_thumbnail_generation(self, file_paths: List[str]) -> Optional[ThumbnailWorker]:
        """Start generating thumbnails for a list of PDF files."""
        self.stop_thumbnail_generation()  # Stop any existing thumbnail generation

        self.thumbnail_worker = ThumbnailWorker(file_paths)
        self.thumbnail_thread = QThread()
        self.thumbnail_worker.moveToThread(self.thumbnail_thread)

        self.thumbnail_thread.started.connect(self.thumbnail_worker.run)
        self.thumbnail_worker.finished.connect(self.stop_thumbnail_generation)

        self.thumbnail_thread.start()
        return self.thumbnail_worker

    def stop_thumbnail_generation(self):
        """Stop the thumbnail generation worker."""
        if self.thumbnail_worker:
            self.thumbnail_worker.stop()
        if self.thumbnail_thread:
            self.thumbnail_thread.quit()
            self.thumbnail_thread.wait(500)
            self.thumbnail_thread = None
            self.thumbnail_worker = None

# Create a global instance of the worker manager
global_worker_manager = PDFWorkerManager()
