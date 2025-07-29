"""
الإعدادات الافتراضية للتطبيق
تحتوي على جميع الإعدادات الافتراضية التي يمكن الرجوع إليها
"""

# الإعدادات الافتراضية الحالية للتطبيق
DEFAULT_SETTINGS = {
    "theme": "dark",
    "accent_color": "#ff6f00",
    "transparency": 80,
    "contrast": "عادي",
    "ui_settings": {
        "font_size": 14,
        "font_family": "النظام الافتراضي",
        "font_weight": "عادي",
        "text_direction": "تلقائي"
    },
    "custom_colors": {
        "text_title": "افتراضي",
        "text_body": "افتراضي", 
        "text_secondary": "افتراضي"
    },
    "security_settings": {
        "enable_password_protection": False,
        "privacy_mode": False
    },
    "performance_settings": {
        "max_memory": 512,
        "enable_multithreading": True
    },
    "app_settings": {
        "auto_save": True,
        "backup_enabled": True,
        "check_updates": True,
        "language": "ar"
    }
}

def get_default_settings():
    """الحصول على نسخة من الإعدادات الافتراضية"""
    import copy
    return copy.deepcopy(DEFAULT_SETTINGS)

def save_current_as_default():
    """حفظ الإعدادات الحالية كإعدادات افتراضية جديدة"""
    try:
        import copy
        from . import settings
        current_settings = settings.load_settings()

        # تحديث الإعدادات الافتراضية
        global DEFAULT_SETTINGS
        DEFAULT_SETTINGS = copy.deepcopy(current_settings)
        
        # حفظ في ملف منفصل للإعدادات الافتراضية
        import json
        import os
        
        default_file = os.path.join(os.path.dirname(__file__), "default_settings.json")
        with open(default_file, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"خطأ في حفظ الإعدادات الافتراضية: {e}")
        return False

def load_default_settings():
    """تحميل الإعدادات الافتراضية من الملف إن وجد"""
    try:
        import json
        import os
        
        default_file = os.path.join(os.path.dirname(__file__), "default_settings.json")
        if os.path.exists(default_file):
            with open(default_file, 'r', encoding='utf-8') as f:
                loaded_defaults = json.load(f)
                global DEFAULT_SETTINGS
                DEFAULT_SETTINGS = loaded_defaults
                return loaded_defaults
    except Exception as e:
        print(f"خطأ في تحميل الإعدادات الافتراضية: {e}")
    
    return get_default_settings()

def reset_to_defaults():
    """إرجاع الإعدادات إلى الافتراضية"""
    try:
        from . import settings
        default_settings = get_default_settings()
        settings.save_settings(default_settings)
        return True
    except Exception as e:
        print(f"خطأ في إرجاع الإعدادات الافتراضية: {e}")
        return False
