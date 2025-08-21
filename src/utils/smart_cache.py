# -*- coding: utf-8 -*-
"""
نظام التخزين المؤقت الذكي للصور والبيانات
Smart Caching System for Images and Data
"""

from PySide6.QtCore import QObject, Signal, QTimer, QThread, QIODevice, QBuffer
from PySide6.QtGui import QPixmap
from typing import Dict, Optional, List, Any, Tuple
import os
import hashlib
import pickle
import json
from pathlib import Path
import time
import weakref

class SmartCache(QObject):
    """نظام تخزين مؤقت ذكي مع إدارة الذاكرة والقرص"""

    cache_hit = Signal(str)  # مفتاح التخزين المؤقت
    cache_miss = Signal(str)  # مفتاح التخزين المؤقت
    cache_cleaned = Signal(int)  # عدد العناصر المحذوفة

    def __init__(self,
                 max_memory_items: int = 100,
                 max_memory_mb: int = 200,
                 disk_cache_enabled: bool = True,
                 cache_dir: str = None):
        super().__init__()
        self.max_memory_items = max_memory_items
        self.max_memory_mb = max_memory_mb * 1024 * 1024  # Convert MB to bytes
        self.disk_cache_enabled = disk_cache_enabled
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".apexflow_cache"
        if self.disk_cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.memory_cache = {}
        self.access_times = {}
        self.total_memory_size = 0
        self.disk_cache_hits = 0

    def get(self, key: str, default=None):
        """الحصول على عنصر من التخزين المؤقت"""
        if key in self.memory_cache:
            self.access_times[key] = time.time()
            self.cache_hit.emit(key)
            
            # التحقق إذا كان العنصر هو QPixmap
            cached_item = self.memory_cache[key]
            if isinstance(cached_item, dict) and cached_item.get('type') == 'QPixmap':
                # إعادة بناء كائن QPixmap من البيانات المخزنة
                pixmap = QPixmap()
                pixmap.loadFromData(cached_item['data'])
                return pixmap
            
            return cached_item
        
        # البحث في التخزين على القرص إذا كان مفعلًا
        if self.disk_cache_enabled:
            cache_file = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.cache"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    self.memory_cache[key] = data
                    self.access_times[key] = time.time()
                    self.disk_cache_hits += 1
                    self.cache_hit.emit(key)
                    
                    # التحقق إذا كان العنصر هو QPixmap
                    if isinstance(data, dict) and data.get('type') == 'QPixmap':
                        # إعادة بناء كائن QPixmap من البيانات المخزنة
                        pixmap = QPixmap()
                        pixmap.loadFromData(data['data'])
                        return pixmap
                    
                    return data
                except Exception as e:
                    print(f"Error loading from disk cache: {e}")
        
        self.cache_miss.emit(key)
        return default
    
    def set(self, key: str, value: Any) -> None:
        """إضافة عنصر إلى التخزين المؤقت"""
        # تحديث أو إضافة العنصر
        if key in self.memory_cache:
            # حساب حجم العنصر القديم
            old_size = len(pickle.dumps(self.memory_cache[key]))
            self.total_memory_size -= old_size
        
        # حساب حجم العنصر الجديد
        if isinstance(value, QPixmap):
            # التعامل مع QPixmap بشكل خاص
            buffer = QBuffer()
            buffer.open(QIODevice.ReadWrite)
            value.save(buffer, "PNG")
            new_size = buffer.size()
            # تخزين الصورة كبيانات بدلاً من كائن QPixmap
            self.memory_cache[key] = {
                'type': 'QPixmap',
                'data': buffer.data().data()
            }
        else:
            # التعامل مع الأنواع الأخرى بشكل طبيعي
            new_size = len(pickle.dumps(value))
            self.memory_cache[key] = value
        
        self.total_memory_size += new_size
        self.access_times[key] = time.time()
        
        # التحقق من الحاجة لتنظيف الذاكرة
        self._clean_memory_if_needed()
        
        # حفظ على القرص إذا كان التخزين على القرص مفعلًا
        if self.disk_cache_enabled:
            try:
                cache_file = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.cache"
                with open(cache_file, 'wb') as f:
                    pickle.dump(self.memory_cache[key], f)
            except Exception as e:
                print(f"Error saving to disk cache: {e}")
    
    def put(self, key: str, value: Any) -> None:
        """إضافة عنصر إلى التخزين المؤقت (بديل لـ set)"""
        self.set(key, value)
    
    def clear(self) -> None:
        """مسح التخزين المؤقت"""
        self.memory_cache.clear()
        self.access_times.clear()
        self.total_memory_size = 0
        
        # مسح التخزين على القرص إذا كان مفعلًا
        if self.disk_cache_enabled and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    print(f"Error deleting cache file: {e}")
    
    def _clean_memory_if_needed(self) -> None:
        """تنظيف الذاكرة إذا تجاوزت الحدود المسموحة"""
        # التحقق من عدد العناصر
        while len(self.memory_cache) > self.max_memory_items:
            self._remove_oldest_item()
        
        # التحقق من حجم الذاكرة
        while self.total_memory_size > self.max_memory_mb:
            self._remove_oldest_item()
    
    def _remove_oldest_item(self) -> None:
        """إزالة أقدم عنصر من التخزين المؤقت"""
        if not self.access_times:
            return
        
        # البحث عن أقدم عنصر
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # حساب حجم العنصر وإزالته
        if oldest_key in self.memory_cache:
            item_size = len(pickle.dumps(self.memory_cache[oldest_key]))
            self.total_memory_size -= item_size
            del self.memory_cache[oldest_key]
        
        if oldest_key in self.access_times:
            del self.access_times[oldest_key]

# إنشاء نسخة عامة من نظام التخزين المؤقت لملفات PDF
pdf_cache = SmartCache()

# إنشاء نسخة عامة من نظام التخزين المؤقت للصور
image_cache = SmartCache()
