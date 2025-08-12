
# -*- coding: utf-8 -*-
"""
نظام تسجيل السجلات لـ ApexFlow
Logging System for ApexFlow
"""
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from .settings import get_setting, set_setting

def get_log_dir():
    """Returns the path to the log directory."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

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

    def get_log_dir(self):
        """Returns the path to the log directory."""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

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

def clear_all_logs():
    """
    Deletes all .log files from the log directory.
    Returns True on success, False on failure.
    """
    try:
        log_dir = get_log_dir()
        if not os.path.exists(log_dir):
            return True # Nothing to clear

        for filename in os.listdir(log_dir):
            if filename.endswith(".log"):
                file_path = os.path.join(log_dir, filename)
                os.remove(file_path)
        
        log_info("All log files have been cleared.")
        return True
    except Exception as e:
        log_error(f"Failed to clear log files: {e}")
        return False

def get_latest_log_content():
    """
    Finds the most recent log file, reads its content, and returns it.
    Returns a tuple (content, status_message_key).
    """
    try:
        log_dir = get_log_dir()
        if not os.path.exists(log_dir):
            return None, "no_logs_found"

        log_files = [f for f in os.listdir(log_dir) if f.startswith("apexflow_") and f.endswith(".log")]
        if not log_files:
            return None, "no_logs_found"

        # Find the latest log file based on the date in the filename
        latest_log_file = max(log_files, key=lambda f: datetime.strptime(f.split('_')[1].split('.')[0], '%Y%m%d'))
        
        log_path = os.path.join(log_dir, latest_log_file)
        
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content, "log_content_loaded"
    except Exception as e:
        log_error(f"Failed to read latest log file: {e}")
        return None, "failed_to_read_log"

def prune_old_logs():
    """
    Deletes log files older than the retention period specified in settings.
    """
    try:
        retention_days = get_setting("log_retention_days", 7) # Default to 7 days
        if retention_days <= 0:
            log_info("Log retention is set to 'Forever'. No logs will be pruned.")
            return # 0 or less means keep forever

        log_dir = get_log_dir()
        if not os.path.exists(log_dir):
            return

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for filename in os.listdir(log_dir):
            if filename.startswith("apexflow_") and filename.endswith(".log"):
                try:
                    # Extract date from filename like 'apexflow_YYYYMMDD.log'
                    date_str = filename.split('_')[1].split('.')[0]
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    if file_date < cutoff_date:
                        file_path = os.path.join(log_dir, filename)
                        os.remove(file_path)
                        log_info(f"Pruned old log file: {filename}")
                except (IndexError, ValueError):
                    # Ignore files with incorrect name format
                    continue
    except Exception as e:
        log_error(f"Error during log pruning: {e}")
