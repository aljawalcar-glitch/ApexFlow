# -*- coding: utf-8 -*-
"""
نظام التخزين المؤقت الذكي للصور والبيانات
Smart Caching System for Images and Data
"""

from PySide6.QtCore import QObject, Signal, QTimer, QThread
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
        
        # إعدادات التخزين المؤقت
        self.max_memory_items = max_memory_items
        self.max_memory_mb = max_memory_mb
        self.disk_cache_enabled = disk_cache_enabled
        
        # التخزين المؤقت في الذاكرة
        self.memory_cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.item_sizes: Dict[str, int] = {}
        self.total_memory_usage = 0
        
        # مجلد التخزين المؤقت على القرص
        if cache_dir is None:
            cache_dir = os.path.join(Path.home(), '.apexflow_cache')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # ملف فهرس التخزين المؤقت
        self.index_file = self.cache_dir / 'cache_index.json'
        self.disk_index: Dict[str, dict] = {}
        self._load_disk_index()
        
        # مؤقت التنظيف التلقائي
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._auto_cleanup)
        self.cleanup_timer.start(30000)  # كل 30 ثانية
        
        # إحصائيات
        self.stats = {
            'hits': 0,
            'misses': 0,
            'disk_hits': 0,
            'disk_misses': 0,
            'cleanups': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """الحصول على عنصر من التخزين المؤقت"""
        # البحث في الذاكرة أولاً
        if key in self.memory_cache:
            self.access_times[key] = time.time()
            self.stats['hits'] += 1
            self.cache_hit.emit(key)
            return self.memory_cache[key]
        
        # البحث في القرص إذا كان مفعلاً
        if self.disk_cache_enabled and key in self.disk_index:
            try:
                disk_item = self._load_from_disk(key)
                if disk_item is not None:
                    # إضافة للذاكرة للوصول السريع
                    self._add_to_memory(key, disk_item)
                    self.stats['disk_hits'] += 1
                    self.cache_hit.emit(key)
                    return disk_item
            except Exception as e:
                print(f"خطأ في تحميل من القرص: {e}")
                # إزالة الفهرس التالف
                if key in self.disk_index:
                    del self.disk_index[key]
        
        # لم يوجد العنصر
        self.stats['misses'] += 1
        self.cache_miss.emit(key)
        return default
    
    def put(self, key: str, value: Any, disk_cache: bool = True) -> bool:
        """إضافة عنصر للتخزين المؤقت"""
        try:
            # حساب حجم العنصر (تقدير)
            item_size = self._estimate_size(value)
            
            # إضافة للذاكرة
            self._add_to_memory(key, value, item_size)
            
            # إضافة للقرص إذا كان مطلوباً
            if disk_cache and self.disk_cache_enabled:
                self._save_to_disk(key, value, item_size)
            
            return True
            
        except Exception as e:
            print(f"خطأ في إضافة للتخزين المؤقت: {e}")
            return False
    
    def _add_to_memory(self, key: str, value: Any, size: int = None):
        """إضافة عنصر للذاكرة مع إدارة الحجم"""
        if size is None:
            size = self._estimate_size(value)
        
        # إزالة العنصر القديم إذا كان موجوداً
        if key in self.memory_cache:
            self.total_memory_usage -= self.item_sizes.get(key, 0)
        
        # فحص إذا كان هناك مساحة كافية
        while (len(self.memory_cache) >= self.max_memory_items or 
               self.total_memory_usage + size > self.max_memory_mb * 1024 * 1024):
            self._remove_lru_item()
        
        # إضافة العنصر الجديد
        self.memory_cache[key] = value
        self.access_times[key] = time.time()
        self.item_sizes[key] = size
        self.total_memory_usage += size
    
    def _remove_lru_item(self):
        """إزالة أقل عنصر استخداماً (LRU)"""
        if not self.access_times:
            return
        
        # العثور على أقدم عنصر
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # إزالة العنصر
        if oldest_key in self.memory_cache:
            del self.memory_cache[oldest_key]
            self.total_memory_usage -= self.item_sizes.get(oldest_key, 0)
        
        if oldest_key in self.access_times:
            del self.access_times[oldest_key]
        
        if oldest_key in self.item_sizes:
            del self.item_sizes[oldest_key]
    
    def _save_to_disk(self, key: str, value: Any, size: int):
        """حفظ عنصر على القرص"""
        try:
            # إنشاء اسم ملف آمن
            safe_key = hashlib.md5(key.encode()).hexdigest()
            file_path = self.cache_dir / f"{safe_key}.cache"
            
            # حفظ البيانات
            if isinstance(value, QPixmap):
                # حفظ QPixmap كصورة
                value.save(str(file_path), "PNG")
                file_type = "pixmap"
            else:
                # حفظ البيانات الأخرى كـ pickle
                with open(file_path, 'wb') as f:
                    pickle.dump(value, f)
                file_type = "pickle"
            
            # تحديث الفهرس
            self.disk_index[key] = {
                'file': safe_key,
                'type': file_type,
                'size': size,
                'timestamp': time.time()
            }
            
            self._save_disk_index()
            
        except Exception as e:
            print(f"خطأ في حفظ على القرص: {e}")
    
    def _load_from_disk(self, key: str) -> Any:
        """تحميل عنصر من القرص"""
        if key not in self.disk_index:
            return None
        
        try:
            item_info = self.disk_index[key]
            file_path = self.cache_dir / f"{item_info['file']}.cache"
            
            if not file_path.exists():
                # إزالة الفهرس التالف
                del self.disk_index[key]
                return None
            
            # تحميل البيانات
            if item_info['type'] == 'pixmap':
                return QPixmap(str(file_path))
            else:
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
                    
        except Exception as e:
            print(f"خطأ في تحميل من القرص: {e}")
            # إزالة الفهرس التالف
            if key in self.disk_index:
                del self.disk_index[key]
            return None
    
    def _load_disk_index(self):
        """تحميل فهرس القرص"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.disk_index = json.load(f)
        except Exception as e:
            print(f"خطأ في تحميل فهرس القرص: {e}")
            self.disk_index = {}
    
    def _save_disk_index(self):
        """حفظ فهرس القرص"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.disk_index, f, indent=2)
        except Exception as e:
            print(f"خطأ في حفظ فهرس القرص: {e}")
    
    def _estimate_size(self, value: Any) -> int:
        """تقدير حجم العنصر بالبايت"""
        if isinstance(value, QPixmap):
            # تقدير حجم QPixmap
            return value.width() * value.height() * 4  # 4 bytes per pixel (RGBA)
        elif isinstance(value, (str, bytes)):
            return len(value)
        elif isinstance(value, (list, tuple, dict)):
            return len(str(value))  # تقدير تقريبي
        else:
            return 1024  # تقدير افتراضي 1KB
    
    def _auto_cleanup(self):
        """تنظيف تلقائي للتخزين المؤقت"""
        current_time = time.time()
        cleanup_count = 0
        
        # تنظيف العناصر القديمة من الذاكرة (أكثر من ساعة)
        old_keys = [key for key, access_time in self.access_times.items() 
                   if current_time - access_time > 3600]
        
        for key in old_keys:
            if key in self.memory_cache:
                del self.memory_cache[key]
                self.total_memory_usage -= self.item_sizes.get(key, 0)
                cleanup_count += 1
            
            if key in self.access_times:
                del self.access_times[key]
            
            if key in self.item_sizes:
                del self.item_sizes[key]
        
        # تنظيف ملفات القرص القديمة (أكثر من يوم)
        if self.disk_cache_enabled:
            old_disk_keys = [key for key, info in self.disk_index.items()
                           if current_time - info.get('timestamp', 0) > 86400]
            
            for key in old_disk_keys:
                try:
                    item_info = self.disk_index[key]
                    file_path = self.cache_dir / f"{item_info['file']}.cache"
                    if file_path.exists():
                        file_path.unlink()
                    del self.disk_index[key]
                    cleanup_count += 1
                except Exception as e:
                    print(f"خطأ في حذف ملف التخزين المؤقت: {e}")
        
        if cleanup_count > 0:
            self.stats['cleanups'] += 1
            self.cache_cleaned.emit(cleanup_count)
            self._save_disk_index()
    
    def clear(self):
        """مسح جميع التخزين المؤقت"""
        # مسح الذاكرة
        self.memory_cache.clear()
        self.access_times.clear()
        self.item_sizes.clear()
        self.total_memory_usage = 0
        
        # مسح القرص
        if self.disk_cache_enabled:
            try:
                for item_info in self.disk_index.values():
                    file_path = self.cache_dir / f"{item_info['file']}.cache"
                    if file_path.exists():
                        file_path.unlink()
                
                self.disk_index.clear()
                self._save_disk_index()
                
            except Exception as e:
                print(f"خطأ في مسح التخزين المؤقت: {e}")
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات التخزين المؤقت"""
        hit_rate = 0
        if self.stats['hits'] + self.stats['misses'] > 0:
            hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) * 100
        
        return {
            **self.stats,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_items': len(self.memory_cache),
            'memory_usage_mb': round(self.total_memory_usage / (1024 * 1024), 2),
            'disk_items': len(self.disk_index),
            'cache_dir': str(self.cache_dir)
        }
    
    def cleanup(self):
        """تنظيف الموارد"""
        self.cleanup_timer.stop()
        self._save_disk_index()

# المثيلات العامة للاستخدام
image_cache = SmartCache(max_memory_items=100, max_memory_mb=150)
pdf_cache = SmartCache(max_memory_items=50, max_memory_mb=200)
general_cache = SmartCache(max_memory_items=200, max_memory_mb=50)
