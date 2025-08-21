# -*- coding: utf-8 -*-
"""
Background Temp File Cleaner
منظف الملفات المؤقتة في الخلفية
"""

import os
import time
import threading
from .temp_cleaner import clean_temp_files
from .logger import info, warning

class BackgroundCleaner:
    """منظف الملفات المؤقتة في الخلفية"""
    
    def __init__(self, interval=300):  # 5 دقائق
        self.interval = interval
        self.running = False
        self.thread = None
        self._load_settings()
        
    def start(self):
        """بدء التنظيف في الخلفية"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.thread.start()
            info("تم بدء منظف الملفات المؤقتة في الخلفية")
    
    def stop(self):
        """إيقاف التنظيف في الخلفية"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        info("تم إيقاف منظف الملفات المؤقتة في الخلفية")
    
    def _load_settings(self):
        """تحميل إعدادات التنظيف"""
        try:
            from .settings import get_setting
            self.enabled = get_setting("auto_cleanup_enabled", True)
            interval_minutes = get_setting("cleanup_interval_minutes", 5)
            self.interval = interval_minutes * 60
        except Exception:
            self.enabled = True
            self.interval = 300
    
    def _cleanup_loop(self):
        """حلقة التنظيف الرئيسية"""
        while self.running:
            # تحميل الإعدادات في بداية كل حلقة
            self._load_settings()
            
            if self.enabled:
                try:
                    # تنظيف صامت بدون رسائل تحذير
                    clean_temp_files()
                except Exception:
                    # تجاهل الأخطاء بصمت
                    pass
            
            # انتظار للفترة المحددة
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)

# إنشاء مثيل عام
background_cleaner = BackgroundCleaner()