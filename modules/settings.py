"""
Settings Module
وحدة الإعدادات
This module handles application settings and configuration.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from .logger import debug, info, warning, error

def get_settings_directory():
    """
    Get the appropriate directory for storing settings.
    الحصول على المجلد المناسب لحفظ الإعدادات
    """
    if sys.platform == "win32":
        # Windows: استخدام مجلد AppData
        appdata = os.environ.get('APPDATA')
        if appdata:
            settings_dir = os.path.join(appdata, 'ApexFlow')
        else:
            # fallback إلى مجلد المستخدم
            settings_dir = os.path.join(os.path.expanduser('~'), 'ApexFlow')
    else:
        # Linux/Mac: استخدام مجلد المستخدم
        settings_dir = os.path.join(os.path.expanduser('~'), '.apexflow')

    # إنشاء المجلد إذا لم يكن موجوداً
    try:
        os.makedirs(settings_dir, exist_ok=True)
        return settings_dir
    except Exception as e:
        print(f"تعذر إنشاء مجلد الإعدادات: {e}")
        # fallback إلى المجلد الحالي
        return os.getcwd()

def get_settings_file_path():
    """
    Get the full path to the settings file.
    الحصول على المسار الكامل لملف الإعدادات
    """
    settings_dir = get_settings_directory()
    return os.path.join(settings_dir, "settings.json")

def check_write_permissions(file_path):
    """
    Check if we have write permissions to a file/directory.
    التحقق من صلاحيات الكتابة لملف/مجلد
    """
    try:
        # التحقق من المجلد
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # محاولة كتابة ملف تجريبي
        test_file = os.path.join(directory, "test_write.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True

    except Exception as e:
        print(f"لا توجد صلاحيات كتابة في: {directory}")
        print(f"الخطأ: {e}")
        return False

# الإعدادات الافتراضية
DEFAULT_SETTINGS = {
    "save_mode": "dynamic",  # "dynamic" أو "fixed"
    "save_path": "",  # مسار الحفظ الثابت
    "compression_level": 3,  # مستوى الضغط (1-5)
    "rotation_angle": 90,  # زاوية التدوير الافتراضية
    "language": "ar",  # اللغة
    "theme": "blue",  # السمة (dark, light, blue, green, purple)
    "accent_color": "#056a51",  # لون التمييز
    "auto_backup": True,  # النسخ الاحتياطي التلقائي
    "backup_path": "",  # مسار النسخ الاحتياطي
    "max_file_size": 100,  # الحد الأقصى لحجم الملف (ميجابايت)
    "recent_files": [],  # الملفات الأخيرة
    "window_geometry": {
        "width": 1000,
        "height": 600,
        "x": 200,
        "y": 100
    },
    "split_settings": {
        "prefix": "page",  # بادئة أسماء الملفات المقسمة
        "pages_per_file": 1,  # عدد الصفحات لكل ملف
        "create_subfolders": False  # إنشاء مجلدات فرعية
    },
    "merge_settings": {
        "add_bookmarks": True,  # إضافة إشارات مرجعية
        "preserve_metadata": True,  # الحفاظ على البيانات الوصفية
        "optimize_size": False  # تحسين الحجم بعد الدمج
    },
    "ui_settings": {
        "show_tooltips": True,  # إظهار التلميحات
        "animation_speed": 300,  # سرعة الحركة (مللي ثانية)
        "font_size": 12,  # حجم الخط الأساسي (مثالي للقراءة)
        "title_font_size": 18,  # حجم خط العناوين
        "menu_font_size": 12,  # حجم خط القوائم
        "show_progress": True  # إظهار شريط التقدم
    },
    "security_settings": {
        "enable_password_protection": False,  # تفعيل حماية كلمة المرور
        "default_password": "",  # كلمة المرور الافتراضية للملفات
        "auto_encrypt": False,  # التشفير التلقائي للملفات
        "encryption_level": "AES-128",  # مستوى التشفير
        "remember_passwords": False,  # تذكر كلمات المرور
        "password_timeout": 30,  # انتهاء صلاحية كلمة المرور (دقائق)
        "secure_delete": False,  # الحذف الآمن للملفات المؤقتة
        "audit_log": True,  # تسجيل العمليات
        "privacy_mode": False  # وضع الخصوصية
    },
    "performance_settings": {
        "max_memory_usage": 512,  # الحد الأقصى لاستخدام الذاكرة (ميجابايت)
        "enable_multithreading": True,  # تفعيل المعالجة المتعددة
        "thread_count": 4,  # عدد الخيوط
        "cache_size": 100,  # حجم التخزين المؤقت (ميجابايت)
        "auto_cleanup": True,  # التنظيف التلقائي للملفات المؤقتة
        "cleanup_interval": 24,  # فترة التنظيف (ساعات)
        "enable_gpu_acceleration": False,  # تفعيل تسريع GPU
        "preview_quality": "medium"  # جودة المعاينة (low, medium, high)
    },
    "keyboard_shortcuts": {
        "merge_files": "Ctrl+M",
        "split_file": "Ctrl+Shift+S",
        "compress_file": "Ctrl+Shift+C",
        "rotate_file": "Ctrl+R",
        "convert_file": "Ctrl+T",
        "open_settings": "Ctrl+,",
        "save_file": "Ctrl+S",
        "open_file": "Ctrl+O",
        "quit_app": "Ctrl+Q",
        "new_project": "Ctrl+N"
    },
    "notification_settings": {
        "success": True,
        "warning": True,
        "error": True,
        "info": True
    }
}

def migrate_old_settings():
    """
    Migrate settings from old location to new location.
    نقل الإعدادات من الموقع القديم إلى الجديد
    """
    old_settings_file = "settings.json"  # الموقع القديم
    new_settings_file = get_settings_file_path()  # الموقع الجديد

    # إذا كان الملف القديم موجود والجديد غير موجود
    if os.path.exists(old_settings_file) and not os.path.exists(new_settings_file):
        try:
            print(f"نقل الإعدادات من {old_settings_file} إلى {new_settings_file}")

            # قراءة الإعدادات القديمة
            with open(old_settings_file, 'r', encoding='utf-8') as old_file:
                old_settings = json.load(old_file)

            # التأكد من وجود المجلد الجديد
            new_settings_dir = os.path.dirname(new_settings_file)
            os.makedirs(new_settings_dir, exist_ok=True)

            # حفظ في الموقع الجديد
            with open(new_settings_file, 'w', encoding='utf-8') as new_file:
                json.dump(old_settings, new_file, indent=4, ensure_ascii=False)

            print("تم نقل الإعدادات بنجاح")
            return True

        except Exception as e:
            print(f"خطأ في نقل الإعدادات: {e}")
            return False

    return False

def load_settings() -> Dict[str, Any]:
    """
    Load application settings from file.
    تحميل إعدادات التطبيق من الملف

    Returns:
        Dictionary containing application settings
    """
    try:
        # محاولة نقل الإعدادات القديمة أولاً
        migrate_old_settings()

        settings_file = get_settings_file_path()
        debug(f"محاولة تحميل الإعدادات من: {settings_file}")

        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as file:
                loaded_settings = json.load(file)

                # دمج الإعدادات المحملة مع الافتراضية
                settings = DEFAULT_SETTINGS.copy()
                settings.update(loaded_settings)

                # التحقق من صحة الإعدادات
                settings = validate_settings(settings)

                debug("تم تحميل الإعدادات بنجاح")
                return settings
        else:
            debug(f"لم يتم العثور على ملف الإعدادات في: {settings_file}")
            debug("سيتم استخدام الإعدادات الافتراضية وحفظها")
            # حفظ الإعدادات الافتراضية في المسار الجديد
            default_settings = DEFAULT_SETTINGS.copy()
            save_settings(default_settings)
            return default_settings

    except Exception as e:
        error(f"خطأ في تحميل الإعدادات: {str(e)}")
        warning("سيتم استخدام الإعدادات الافتراضية")
        return DEFAULT_SETTINGS.copy()

def create_backup(original_settings: Dict[str, Any]) -> Tuple[bool, str]:
    """
    إنشاء نسخة احتياطية من الإعدادات
    """
    try:
        # إنشاء مجلد النسخ الاحتياطية
        backup_dir = os.path.join(get_settings_directory(), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # اسم الملف مع التاريخ والوقت
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"settings_backup_{timestamp}.json")

        # حفظ النسخة الاحتياطية
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(original_settings, f, ensure_ascii=False, indent=2)

        return True, backup_file
    except Exception as e:
        return False, str(e)

def save_settings(settings: Dict[str, Any], original_settings: Optional[Dict[str, Any]] = None) -> bool:
    """
    Save application settings to file with automatic backup.
    حفظ إعدادات التطبيق في الملف مع نسخ احتياطي تلقائي
    
    Args:
        settings: Dictionary containing new settings to save
        original_settings: Optional dictionary containing the settings before changes, for backup.
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # إنشاء نسخة احتياطية إذا تم توفير الإعدادات الأصلية
        if original_settings:
            backup_success, backup_info = create_backup(original_settings)
            if not backup_success:
                # يمكن إضافة منطق هنا لسؤال المستخدم إذا كان يريد المتابعة بدون نسخ احتياطي
                print(f"تحذير: فشل في إنشاء نسخة احتياطية: {backup_info}")

        # التحقق من صحة الإعدادات قبل الحفظ
        validated_settings = validate_settings(settings)

        settings_file = get_settings_file_path()
        debug(f"محاولة حفظ الإعدادات في: {settings_file}")

        # التحقق من صلاحيات الكتابة
        if not check_write_permissions(settings_file):
            error("تعذر الحفظ: لا توجد صلاحيات كتابة")
            return False

        # التأكد من وجود المجلد
        settings_dir = os.path.dirname(settings_file)
        os.makedirs(settings_dir, exist_ok=True)

        with open(settings_file, 'w', encoding='utf-8') as file:
            json.dump(validated_settings, file, indent=4, ensure_ascii=False)

        debug("تم حفظ الإعدادات بنجاح")
        return True

    except Exception as e:
        error(f"خطأ في حفظ الإعدادات: {str(e)}")
        return False

def get_settings_info() -> Dict[str, str]:
    """
    Get information about settings location and status.
    الحصول على معلومات حول موقع الإعدادات وحالتها
    """
    settings_file = get_settings_file_path()
    settings_dir = get_settings_directory()

    info = {
        "settings_file": settings_file,
        "settings_directory": settings_dir,
        "file_exists": "نعم" if os.path.exists(settings_file) else "لا",
        "directory_exists": "نعم" if os.path.exists(settings_dir) else "لا",
        "write_permissions": "نعم" if check_write_permissions(settings_file) else "لا"
    }

    return info

def print_settings_info():
    """
    Print settings information for debugging.
    طباعة معلومات الإعدادات للتشخيص
    """
    info = get_settings_info()
    print("\n=== معلومات الإعدادات ===")
    print(f"مجلد الإعدادات: {info['settings_directory']}")
    print(f"ملف الإعدادات: {info['settings_file']}")
    print(f"المجلد موجود: {info['directory_exists']}")
    print(f"الملف موجود: {info['file_exists']}")
    print(f"صلاحيات الكتابة: {info['write_permissions']}")
    print("========================\n")

def validate_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and correct settings values.
    التحقق من صحة قيم الإعدادات وتصحيحها
    
    Args:
        settings: Settings dictionary to validate
        
    Returns:
        Validated settings dictionary
    """
    validated = settings.copy()
    
    try:
        # التحقق من وضع الحفظ
        if validated.get("save_mode") not in ["dynamic", "fixed"]:
            validated["save_mode"] = "dynamic"
        
        # التحقق من مستوى الضغط
        compression_level = validated.get("compression_level", 3)
        if not isinstance(compression_level, int) or not 1 <= compression_level <= 5:
            validated["compression_level"] = 3
        
        # التحقق من زاوية التدوير
        rotation_angle = validated.get("rotation_angle", 90)
        valid_angles = [90, 180, 270, -90, -180, -270]
        if rotation_angle not in valid_angles:
            validated["rotation_angle"] = 90
        
        # التحقق من اللغة
        if validated.get("language") not in ["ar", "en"]:
            validated["language"] = "ar"
        
        # التحقق من السمة
        if validated.get("theme") not in ["dark", "light", "blue", "green", "purple"]:
            validated["theme"] = "blue"

        # التحقق من لون التمييز
        accent_color = validated.get("accent_color", "#056a51")
        if not isinstance(accent_color, str) or not accent_color.startswith("#"):
            validated["accent_color"] = "#056a51"
        
        # التحقق من الحد الأقصى لحجم الملف
        max_size = validated.get("max_file_size", 100)
        if not isinstance(max_size, (int, float)) or max_size <= 0:
            validated["max_file_size"] = 100
        
        # التحقق من قائمة الملفات الأخيرة
        recent_files = validated.get("recent_files", [])
        if not isinstance(recent_files, list):
            validated["recent_files"] = []
        else:
            # الاحتفاظ بآخر 10 ملفات فقط
            validated["recent_files"] = recent_files[:10]
        
        # التحقق من أبعاد النافذة
        geometry = validated.get("window_geometry", {})
        if not isinstance(geometry, dict):
            validated["window_geometry"] = DEFAULT_SETTINGS["window_geometry"].copy()
        else:
            default_geo = DEFAULT_SETTINGS["window_geometry"]
            for key in ["width", "height", "x", "y"]:
                if key not in geometry or not isinstance(geometry[key], int):
                    geometry[key] = default_geo[key]
        
        # التحقق من إعدادات التقسيم
        split_settings = validated.get("split_settings", {})
        if not isinstance(split_settings, dict):
            validated["split_settings"] = DEFAULT_SETTINGS["split_settings"].copy()
        
        # التحقق من إعدادات الدمج
        merge_settings = validated.get("merge_settings", {})
        if not isinstance(merge_settings, dict):
            validated["merge_settings"] = DEFAULT_SETTINGS["merge_settings"].copy()
        
        # التحقق من إعدادات الواجهة
        ui_settings = validated.get("ui_settings", {})
        if not isinstance(ui_settings, dict):
            validated["ui_settings"] = DEFAULT_SETTINGS["ui_settings"].copy()

        # التحقق من إعدادات الأمان
        security_settings = validated.get("security_settings", {})
        if not isinstance(security_settings, dict):
            validated["security_settings"] = DEFAULT_SETTINGS["security_settings"].copy()
        else:
            # التحقق من مستوى التشفير
            encryption_level = security_settings.get("encryption_level", "AES-128")
            if encryption_level not in ["AES-128", "AES-192", "AES-256"]:
                security_settings["encryption_level"] = "AES-128"

            # التحقق من مهلة كلمة المرور
            password_timeout = security_settings.get("password_timeout", 30)
            if not isinstance(password_timeout, int) or password_timeout < 1:
                security_settings["password_timeout"] = 30

        # التحقق من إعدادات الأداء
        performance_settings = validated.get("performance_settings", {})
        if not isinstance(performance_settings, dict):
            validated["performance_settings"] = DEFAULT_SETTINGS["performance_settings"].copy()
        else:
            # التحقق من استخدام الذاكرة
            max_memory = performance_settings.get("max_memory_usage", 512)
            if not isinstance(max_memory, int) or max_memory < 128:
                performance_settings["max_memory_usage"] = 512

            # التحقق من عدد الخيوط
            thread_count = performance_settings.get("thread_count", 4)
            if not isinstance(thread_count, int) or thread_count < 1 or thread_count > 16:
                performance_settings["thread_count"] = 4

        # التحقق من اختصارات لوحة المفاتيح
        keyboard_shortcuts = validated.get("keyboard_shortcuts", {})
        if not isinstance(keyboard_shortcuts, dict):
            validated["keyboard_shortcuts"] = DEFAULT_SETTINGS["keyboard_shortcuts"].copy()

        # التحقق من إعدادات الإشعارات
        notification_settings = validated.get("notification_settings", {})
        if not isinstance(notification_settings, dict):
            validated["notification_settings"] = DEFAULT_SETTINGS["notification_settings"].copy()
        else:
            default_notif = DEFAULT_SETTINGS["notification_settings"]
            for key in ["success", "warning", "error", "info"]:
                if key not in notification_settings or not isinstance(notification_settings[key], bool):
                    notification_settings[key] = default_notif[key]

        return validated
        
    except Exception as e:
        print(f"خطأ في التحقق من الإعدادات: {str(e)}")
        return DEFAULT_SETTINGS.copy()

def reset_settings() -> bool:
    """
    Reset settings to default values.
    إعادة تعيين الإعدادات إلى القيم الافتراضية
    
    Returns:
        bool: True if reset was successful, False otherwise
    """
    try:
        return save_settings(DEFAULT_SETTINGS.copy())
    except Exception as e:
        print(f"خطأ في إعادة تعيين الإعدادات: {str(e)}")
        return False

def get_setting(key: str, default_value: Any = None) -> Any:
    """
    Get a specific setting value.
    الحصول على قيمة إعداد محدد
    
    Args:
        key: Setting key (supports dot notation for nested keys)
        default_value: Default value if key not found
        
    Returns:
        Setting value or default value
    """
    try:
        settings = load_settings()
        
        # دعم النقطة للمفاتيح المتداخلة (مثل "ui_settings.font_size")
        if '.' in key:
            keys = key.split('.')
            value = settings
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default_value
            return value
        else:
            return settings.get(key, default_value)
            
    except Exception as e:
        print(f"خطأ في الحصول على الإعداد {key}: {str(e)}")
        return default_value

def set_setting(key: str, value: Any) -> bool:
    """
    Set a specific setting value.
    تعيين قيمة إعداد محدد
    
    Args:
        key: Setting key (supports dot notation for nested keys)
        value: Value to set
        
    Returns:
        bool: True if setting was saved successfully, False otherwise
    """
    try:
        settings = load_settings()
        
        # دعم النقطة للمفاتيح المتداخلة
        if '.' in key:
            keys = key.split('.')
            current = settings
            for k in keys[:-1]:
                if k not in current or not isinstance(current[k], dict):
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        else:
            settings[key] = value
        
        return save_settings(settings)
        
    except Exception as e:
        print(f"خطأ في تعيين الإعداد {key}: {str(e)}")
        return False

def add_recent_file(file_path: str) -> bool:
    """
    Add a file to the recent files list.
    إضافة ملف إلى قائمة الملفات الأخيرة
    
    Args:
        file_path: Path to the file to add
        
    Returns:
        bool: True if file was added successfully, False otherwise
    """
    try:
        settings = load_settings()
        recent_files = settings.get("recent_files", [])
        
        # إزالة الملف إذا كان موجوداً مسبقاً
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # إضافة الملف في المقدمة
        recent_files.insert(0, file_path)
        
        # الاحتفاظ بآخر 10 ملفات فقط
        recent_files = recent_files[:10]
        
        settings["recent_files"] = recent_files
        return save_settings(settings)
        
    except Exception as e:
        print(f"خطأ في إضافة الملف الأخير: {str(e)}")
        return False

def get_recent_files() -> list:
    """
    Get the list of recent files.
    الحصول على قائمة الملفات الأخيرة
    
    Returns:
        List of recent file paths
    """
    try:
        settings = load_settings()
        recent_files = settings.get("recent_files", [])
        
        # التحقق من وجود الملفات وإزالة غير الموجودة
        existing_files = []
        for file_path in recent_files:
            if os.path.exists(file_path):
                existing_files.append(file_path)
        
        # تحديث القائمة إذا تغيرت
        if len(existing_files) != len(recent_files):
            settings["recent_files"] = existing_files
            save_settings(settings)
        
        return existing_files
        
    except Exception as e:
        print(f"خطأ في الحصول على الملفات الأخيرة: {str(e)}")
        return []

def export_settings(export_path: str) -> bool:
    """
    Export settings to a file.
    تصدير الإعدادات إلى ملف
    
    Args:
        export_path: Path to export the settings file
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        settings = load_settings()
        
        with open(export_path, 'w', encoding='utf-8') as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)
        
        print(f"تم تصدير الإعدادات إلى: {export_path}")
        return True
        
    except Exception as e:
        print(f"خطأ في تصدير الإعدادات: {str(e)}")
        return False

def import_settings(import_path: str) -> bool:
    """
    Import settings from a file.
    استيراد الإعدادات من ملف

    Args:
        import_path: Path to the settings file to import

    Returns:
        bool: True if import was successful, False otherwise
    """
    try:
        if not os.path.exists(import_path):
            raise FileNotFoundError(f"ملف الإعدادات غير موجود: {import_path}")

        with open(import_path, 'r', encoding='utf-8') as file:
            imported_settings = json.load(file)

        # التحقق من صحة الإعدادات المستوردة
        validated_settings = validate_settings(imported_settings)

        # حفظ الإعدادات المستوردة
        if save_settings(validated_settings):
            print(f"تم استيراد الإعدادات من: {import_path}")
            return True
        else:
            return False

    except Exception as e:
        print(f"خطأ في استيراد الإعدادات: {str(e)}")
        return False

def clear_recent_files() -> bool:
    """
    Clear all recent files from the list.
    مسح جميع الملفات الأخيرة من القائمة

    Returns:
        bool: True if clearing was successful, False otherwise
    """
    try:
        settings_data = load_settings()
        settings_data["recent_files"] = []
        return save_settings(settings_data)
    except Exception as e:
        print(f"خطأ في مسح الملفات الأخيرة: {str(e)}")
        return False

def remove_recent_file(file_path: str) -> bool:
    """
    Remove a specific file from the recent files list.
    إزالة ملف محدد من قائمة الملفات الأخيرة

    Args:
        file_path: Path to the file to remove

    Returns:
        bool: True if removal was successful, False otherwise
    """
    try:
        settings_data = load_settings()
        recent_files = settings_data.get("recent_files", [])

        if file_path in recent_files:
            recent_files.remove(file_path)
            settings_data["recent_files"] = recent_files
            return save_settings(settings_data)

        return True  # File wasn't in the list, so "removal" is successful

    except Exception as e:
        print(f"خطأ في إزالة الملف من القائمة الأخيرة: {str(e)}")
        return False

# مثال على الاستخدام
if __name__ == "__main__":
    # تحميل الإعدادات
    settings = load_settings()
    print("الإعدادات الحالية:")
    print(json.dumps(settings, indent=2, ensure_ascii=False))
    
    # تعيين إعداد محدد
    # set_setting("compression_level", 4)
    # set_setting("ui_settings.font_size", 18)
    
    # الحصول على إعداد محدد
    # compression_level = get_setting("compression_level", 3)
    # font_size = get_setting("ui_settings.font_size", 14)
    
    # إضافة ملف أخير
    # add_recent_file("example.pdf")
    
    print("وحدة الإعدادات تم تحميلها بنجاح")

def should_show_tooltips():
    """التحقق مما إذا كان يجب عرض التلميحات بناءً على إعدادات المستخدم"""
    return get_setting("ui_settings.show_tooltips", True)

def should_enable_animations():
    """التحقق مما إذا كان يجب تفعيل الحركات بناءً على إعدادات المستخدم"""
    return get_setting("ui_settings.enable_animations", True)

def get_default_settings():
    """إرجاع نسخة من الإعدادات الافتراضية"""
    return DEFAULT_SETTINGS.copy()
