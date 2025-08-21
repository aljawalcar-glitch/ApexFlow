# -*- coding: utf-8 -*-
"""
مساعدات للحصول على مسارات الموارد
Resource path helpers for both development and frozen application
"""

import os
import sys

def get_resource_path(relative_path):
    """
    الحصول على المسار الصحيح للموارد سواء في بيئة التطوير أو التطبيق المجمد
    Get correct resource path for both development and frozen application
    
    Args:
        relative_path (str): المسار النسبي للمورد
        
    Returns:
        str: المسار المطلق للمورد
    """
    if getattr(sys, 'frozen', False):
        # التطبيق مجمد (PyInstaller)
        base_path = sys._MEIPASS
    else:
        # بيئة التطوير
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    return os.path.join(base_path, relative_path)

def get_icon_resource_path(icon_name, theme="default"):
    """
    الحصول على مسار أيقونة مع البحث في امتدادات مختلفة
    Get icon path with search for different extensions
    
    Args:
        icon_name (str): اسم الأيقونة بدون امتداد
        theme (str): سمة الأيقونة
        
    Returns:
        str: مسار الأيقونة أو None إذا لم توجد
    """
    base_path = get_resource_path("assets/icons")
    extensions = ['.svg', '.png', '.ico']
    
    # البحث في السمة المحددة أولاً
    for ext in extensions:
        icon_path = os.path.join(base_path, theme, f"{icon_name}{ext}")
        if os.path.exists(icon_path):
            return icon_path
    
    # البحث في السمة الافتراضية
    for ext in extensions:
        icon_path = os.path.join(base_path, "default", f"{icon_name}{ext}")
        if os.path.exists(icon_path):
            return icon_path
    
    # البحث في المجلد الرئيسي للأيقونات
    for ext in extensions:
        icon_path = os.path.join(base_path, f"{icon_name}{ext}")
        if os.path.exists(icon_path):
            return icon_path
    
    return None

def get_image_resource_path(image_name):
    """
    الحصول على مسار صورة
    Get image resource path
    
    Args:
        image_name (str): اسم الصورة مع الامتداد
        
    Returns:
        str: مسار الصورة
    """
    return get_resource_path(f"assets/{image_name}")

def get_sound_resource_path(sound_name):
    """
    الحصول على مسار ملف صوتي
    Get sound resource path
    
    Args:
        sound_name (str): اسم الملف الصوتي مع الامتداد
        
    Returns:
        str: مسار الملف الصوتي
    """
    return get_resource_path(f"assets/sounds/{sound_name}")