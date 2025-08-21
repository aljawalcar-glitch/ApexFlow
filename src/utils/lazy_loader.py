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

class LazyImageLoader(QObject):
    """محمل كسول للصور - يحمل الصور عند الحاجة فقط"""
    image_ready = Signal(str, QPixmap)

    def __init__(self):
        super().__init__()
        self.image_cache: Dict[str, QPixmap] = {}

    def get_image(self, image_path: str):
        if image_path in self.image_cache:
            self.image_ready.emit(image_path, self.image_cache[image_path])
            return

        try:
            pixmap = QPixmap(image_path)
            self.image_cache[image_path] = pixmap
            self.image_ready.emit(image_path, pixmap)
        except Exception:
            # Handle error, maybe emit a signal
            pass

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

    def set_pdf_file(self, file_path: str) -> bool:
        """Sets or changes the PDF file to be loaded."""
        try:
            if self.doc:
                self.doc.close()
            
            self.page_cache.clear()
            self.file_path = file_path
            self.doc = fitz.open(self.file_path)
            self.total_pages = len(self.doc)
            return True
        except Exception as e:
            self.error_occurred.emit(0, f"Failed to load PDF: {e}")
            self.doc = None
            self.total_pages = 0
            return False

    def get_page(self, page_num: int, priority: bool = False):
        """Loads a specific page and emits it when ready."""
        if not self.doc or not (0 <= page_num < self.total_pages):
            self.error_occurred.emit(page_num, "Invalid page number or no PDF loaded.")
            return

        if page_num in self.page_cache:
            self.page_ready.emit(page_num, self.page_cache[page_num])
            return

        self.loading_started.emit(page_num)
        try:
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap()
            q_pixmap = QPixmap()
            q_pixmap.loadFromData(pix.tobytes("ppm"))

            # Cache the loaded page
            self.page_cache[page_num] = q_pixmap
            if len(self.page_cache) > self.max_cached_pages:
                # Simple FIFO cache eviction
                oldest_page = next(iter(self.page_cache))
                del self.page_cache[oldest_page]

            self.page_ready.emit(page_num, q_pixmap)
        except Exception as e:
            self.error_occurred.emit(page_num, f"Error loading page: {e}")

    def preload_pages(self, pages: List[int]):
        """Preloads a list of pages into the cache."""
        for page_num in pages:
            if self.doc and (0 <= page_num < self.total_pages) and page_num not in self.page_cache:
                # This can be expanded to use a thread pool for concurrent loading
                self.get_page(page_num)

global_page_loader = LazyPageLoader()
global_image_loader = LazyImageLoader()
