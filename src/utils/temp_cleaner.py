# -*- coding: utf-8 -*-
"""
وحدة تنظيف الملفات المؤقتة
Temporary Files Cleaner Module
"""

import os
import shutil
import tempfile
import glob
import time
from pathlib import Path
from .logger import info, warning, error

def get_temp_directories():
    """الحصول على مجلدات الملفات المؤقتة"""
    temp_dirs = []
    
    # مجلد temp النظام
    temp_dirs.append(tempfile.gettempdir())
    
    # مجلد temp المستخدم
    user_temp = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
    if os.path.exists(user_temp):
        temp_dirs.append(user_temp)
    
    # مجلد temp التطبيق
    app_temp = os.path.join(tempfile.gettempdir(), "ApexFlow")
    if os.path.exists(app_temp):
        temp_dirs.append(app_temp)
    
    return temp_dirs

def is_file_in_use(file_path):
    """تحقق من استخدام الملف"""
    try:
        # محاولة فتح الملف للكتابة
        with open(file_path, 'r+b'):
            return False
    except (IOError, OSError, PermissionError):
        return True

def safe_remove_file(file_path):
    """حذف آمن للملف بدون رسائل تحذير"""
    try:
        if os.path.isfile(file_path) and not is_file_in_use(file_path):
            size = os.path.getsize(file_path)
            os.remove(file_path)
            return True, size
    except Exception:
        pass
    return False, 0

def clean_temp_files():
    """تنظيف الملفات المؤقتة للتطبيق فقط"""
    cleaned_files = 0
    cleaned_size = 0
    
    # التركيز على ملفات ApexFlow وملفات PyMuPDF المؤقتة
    apexflow_patterns = [
        "ApexFlow_*",
        "pdf_temp_*", 
        "merge_temp_*",
        "split_temp_*",
        "compress_temp_*",
        "rotate_temp_*",
        "stamp_temp_*"
    ]
    
    for temp_dir in get_temp_directories():
        try:
            # تنظيف ملفات ApexFlow المحددة
            for pattern in apexflow_patterns:
                files = glob.glob(os.path.join(temp_dir, pattern))
                for file_path in files:
                    try:
                        if os.path.isfile(file_path):
                            success, size = safe_remove_file(file_path)
                            if success:
                                cleaned_files += 1
                                cleaned_size += size
                        elif os.path.isdir(file_path) and not is_file_in_use(file_path):
                            try:
                                size = get_dir_size(file_path)
                                shutil.rmtree(file_path)
                                cleaned_files += 1
                                cleaned_size += size
                            except Exception:
                                pass
                    except Exception:
                        continue
            
            # تنظيف ملفات PyMuPDF المؤقتة (UUID format) بصمت
            try:
                cleaned_uuid, size_uuid = clean_pymupdf_temp_files(temp_dir)
                cleaned_files += cleaned_uuid
                cleaned_size += size_uuid
            except Exception:
                pass
            
        except Exception:
            continue
    
    if cleaned_files > 0:
        size_mb = cleaned_size / (1024 * 1024)
        info(f"تم تنظيف {cleaned_files} ملف مؤقت ({size_mb:.2f} MB)")
    
    return cleaned_files, cleaned_size

def get_dir_size(path):
    """حساب حجم المجلد"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except:
        pass
    return total

def clean_pymupdf_temp_files(temp_dir):
    """تنظيف ملفات PyMuPDF المؤقتة بصيغة UUID"""
    import re
    cleaned_files = 0
    cleaned_size = 0
    
    # نمط UUID: 8-4-4-4-12 أحرف hex
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.tmp$', re.IGNORECASE)
    # نمط ملفات Windows المؤقتة
    win_temp_pattern = re.compile(r'^~DF[0-9A-F]+\.TMP$', re.IGNORECASE)
    
    try:
        for filename in os.listdir(temp_dir):
            if uuid_pattern.match(filename) or win_temp_pattern.match(filename):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        # تحقق من عمر الملف (أكثر من 5 دقائق)
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > 300:  # 5 دقائق
                            success, size = safe_remove_file(file_path)
                            if success:
                                cleaned_files += 1
                                cleaned_size += size
                except Exception:
                    continue
    except Exception:
        pass
    
    return cleaned_files, cleaned_size

def cleanup_on_exit():
    """تنظيف عند إغلاق التطبيق"""
    try:
        clean_temp_files()
    except Exception as e:
        error(f"خطأ في التنظيف عند الإغلاق: {e}")