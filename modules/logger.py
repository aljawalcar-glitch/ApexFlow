"""
نظام التسجيل المحسن لـ ApexFlow
Enhanced Logging System for ApexFlow
"""

import logging
import os
from pathlib import Path

# إعدادات التسجيل
DEBUG_MODE = True  # تغيير إلى True للتطوير
LOG_TO_FILE = True  # تغيير إلى True لحفظ السجلات في ملف

class ApexFlowLogger:
    """مدير التسجيل الموحد لـ ApexFlow"""
    
    def __init__(self):
        self.logger = logging.getLogger('ApexFlow')
        self.setup_logger()
    
    def setup_logger(self):
        """إعداد نظام التسجيل"""
        # تحديد مستوى التسجيل
        if DEBUG_MODE:
            level = logging.DEBUG
        else:
            level = logging.WARNING  # فقط التحذيرات والأخطاء في الإنتاج
        
        self.logger.setLevel(level)
        
        # إزالة المعالجات الموجودة
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # إعداد تنسيق الرسائل
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # معالج وحدة التحكم (للأخطاء فقط في الإنتاج)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # معالج الملف (اختياري)
        if LOG_TO_FILE:
            self.setup_file_handler(formatter)
    
    def setup_file_handler(self, formatter):
        """إعداد حفظ السجلات في ملف"""
        try:
            # إنشاء مجلد السجلات
            log_dir = Path.home() / 'AppData' / 'Roaming' / 'ApexFlow' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # ملف السجل
            log_file = log_dir / 'apexflow.log'
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            self.logger.warning(f"فشل في إعداد ملف السجل: {e}")
    
    def debug(self, message):
        """رسالة تشخيص (تظهر فقط في وضع التطوير)"""
        self.logger.debug(message)
    
    def info(self, message):
        """رسالة معلوماتية"""
        self.logger.info(message)
    
    def warning(self, message):
        """رسالة تحذير"""
        self.logger.warning(message)
    
    def error(self, message):
        """رسالة خطأ"""
        self.logger.error(message)
    
    def critical(self, message):
        """رسالة خطأ حرج"""
        self.logger.critical(message)

# إنشاء مثيل مشترك
apex_logger = ApexFlowLogger()

# دوال مختصرة للاستخدام السهل
def debug(message):
    """رسالة تشخيص (وضع التطوير فقط)"""
    apex_logger.debug(message)

def info(message):
    """رسالة معلوماتية"""
    apex_logger.info(message)

def warning(message):
    """رسالة تحذير"""
    apex_logger.warning(message)

def error(message):
    """رسالة خطأ"""
    apex_logger.error(message)

def critical(message):
    """رسالة خطأ حرج"""
    apex_logger.critical(message)

def set_debug_mode(enabled=True):
    """تفعيل/إلغاء وضع التشخيص"""
    global DEBUG_MODE
    DEBUG_MODE = enabled
    apex_logger.setup_logger()

def set_file_logging(enabled=True):
    """تفعيل/إلغاء حفظ السجلات في ملف"""
    global LOG_TO_FILE
    LOG_TO_FILE = enabled
    apex_logger.setup_logger()

# دالة للتوافق مع الكود القديم
def print_debug(message):
    """دالة للتوافق مع print() القديمة"""
    if DEBUG_MODE:
        print(message)
    else:
        debug(message)
