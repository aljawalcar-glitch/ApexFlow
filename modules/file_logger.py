
# -*- coding: utf-8 -*-
"""
نظام تسجيل السجلات لـ ApexFlow
Logging System for ApexFlow
"""
import os
import logging
from datetime import datetime
from pathlib import Path

class ApexFlowFileLogger:
    """فئة لتسجيل السجلات في الملفات"""

    def __init__(self):
        """تهيئة مسجل السجلات"""
        self.logger = logging.getLogger('ApexFlowFile')
        self.setup_logger()

    def setup_logger(self):
        """إعداد مسجل السجلات"""
        # تحديد مستوى التسجيل
        self.logger.setLevel(logging.DEBUG)

        # إزالة المعالجات الموجودة
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # إعداد تنسيق الرسائل
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # إنشاء مجلد السجلات
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # إنشاء اسم ملف السجل مع التاريخ
        log_file = os.path.join(log_dir, f"apexflow_{datetime.now().strftime('%Y%m%d')}.log")

        # إعداد معالج الملف
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # تسجيل معلومات عن ملف السجل
        self.logger.info(f"تم إنشاء ملف السجل: {log_file}")

    def debug(self, message):
        """تسجيل رسالة تصحيح"""
        self.logger.debug(message)

    def info(self, message):
        """تسجيل رسالة معلومات"""
        self.logger.info(message)

    def warning(self, message):
        """تسجيل رسالة تحذير"""
        self.logger.warning(message)

    def error(self, message):
        """تسجيل رسالة خطأ"""
        self.logger.error(message)

    def critical(self, message):
        """تسجيل رسالة خطأ حرج"""
        self.logger.critical(message)

# إنشاء مثيل مشترك
file_logger = ApexFlowFileLogger()

# دوال مختصرة للاستخدام السهل
def log_debug(message):
    """رسالة تشخيص"""
    file_logger.debug(message)

def log_info(message):
    """رسالة معلوماتية"""
    file_logger.info(message)

def log_warning(message):
    """رسالة تحذير"""
    file_logger.warning(message)

def log_error(message):
    """رسالة خطأ"""
    file_logger.error(message)

def log_critical(message):
    """رسالة خطأ حرج"""
    file_logger.critical(message)
