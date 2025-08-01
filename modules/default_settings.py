"""
إدارة الإعدادات الافتراضية للتطبيق - ApexFlow
Default Settings Management for Installation and First Run
"""

import os
import json
from datetime import datetime
from typing import Dict, Any

# ===============================
# الإعدادات الافتراضية للتثبيت
# Installation Default Settings
# ===============================

INSTALLATION_DEFAULTS = {
    # إعدادات المظهر الأساسية
    "theme": "blue",
    "accent_color": "#056a51",
    "language": "ar",

    # إعدادات النافذة المحسنة للتثبيت
    "window_geometry": {
        "width": 1200,  # عرض أكبر
        "height": 700,  # ارتفاع أكبر
        "x": 100,
        "y": 50
    },

    # إعدادات الواجهة المحسنة
    "ui_settings": {
        "show_tooltips": True,
        "enable_animations": True,
        "font_size": 12,  # حجم الخط الأساسي (مثالي للقراءة)
        "title_font_size": 18,  # حجم خط العناوين (بارز وواضح)
        "menu_font_size": 12,  # حجم خط القوائم (مطابق للأساسي)
        "font_family": "system_default",
        "font_weight": "normal",
        "text_direction": "auto",
        "transparency": 85,  # شفافية أعلى
        "size": "medium",
        "contrast": "normal"
    },

    # إعدادات الأداء المحسنة
    "performance_settings": {
        "max_memory_usage": 1024,  # ذاكرة أكبر
        "enable_multithreading": True,
        "thread_count": 6,  # خيوط أكثر
        "cache_size": 200,  # تخزين مؤقت أكبر
        "auto_cleanup": True,
        "cleanup_interval": 12,
        "enable_gpu_acceleration": True,  # تفعيل GPU
        "preview_quality": "high"  # جودة عالية
    },

    # إعدادات الأمان المحسنة
    "security_settings": {
        "enable_password_protection": False,
        "privacy_mode": False,
        "audit_log": True,
        "secure_delete": True,  # حذف آمن
        "encryption_level": "AES-256",  # تشفير أقوى
        "password_timeout": 60
    },

    # إعدادات المعالجة
    "compression_level": 4,  # ضغط أفضل
    "auto_backup": True,
    "max_file_size": 500,  # حجم أكبر
    "save_mode": "dynamic",
    "save_path": "",  # سيتم تحديده تلقائياً
    "backup_path": "",

    # إعدادات التقسيم والدمج
    "split_settings": {
        "prefix": "page",
        "pages_per_file": 1,
        "create_subfolders": True  # مجلدات فرعية
    },
    "merge_settings": {
        "add_bookmarks": True,
        "preserve_metadata": True,
        "optimize_size": True  # تحسين الحجم
    },

    # اختصارات لوحة المفاتيح
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

    "recent_files": []
}

def get_default_settings():
    """الحصول على نسخة من الإعدادات الافتراضية"""
    import copy
    return copy.deepcopy(INSTALLATION_DEFAULTS)

def save_current_as_default():
    """حفظ الإعدادات الحالية كإعدادات افتراضية جديدة"""
    try:
        import copy
        from . import settings
        current_settings = settings.load_settings()

        # تحديث الإعدادات الافتراضية
        global INSTALLATION_DEFAULTS
        INSTALLATION_DEFAULTS = copy.deepcopy(current_settings)
        
        # حفظ في ملف منفصل للإعدادات الافتراضية
        import json
        import os

        default_file = os.path.join(os.path.dirname(__file__), "default_settings.json")
        with open(default_file, 'w', encoding='utf-8') as f:
            json.dump(INSTALLATION_DEFAULTS, f, ensure_ascii=False, indent=2)
            
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
                global INSTALLATION_DEFAULTS
                INSTALLATION_DEFAULTS = loaded_defaults
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

# ===============================
# دوال إدارة التثبيت
# Installation Management Functions
# ===============================

def setup_default_paths():
    """إعداد المسارات الافتراضية حسب نظام التشغيل"""
    try:
        # تحديد مجلد المستندات
        if os.name == 'nt':  # Windows
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        else:  # Linux/Mac
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")

        # إنشاء مجلد ApexFlow في المستندات
        apexflow_folder = os.path.join(documents_path, "ApexFlow")
        os.makedirs(apexflow_folder, exist_ok=True)

        # إنشاء مجلدات فرعية
        output_folder = os.path.join(apexflow_folder, "Output")
        backup_folder = os.path.join(apexflow_folder, "Backups")

        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(backup_folder, exist_ok=True)

        print(f"✅ تم إنشاء المجلدات الافتراضية:")
        print(f"   📁 الإخراج: {output_folder}")
        print(f"   📁 النسخ الاحتياطية: {backup_folder}")

        return output_folder, backup_folder

    except Exception as e:
        print(f"❌ خطأ في إعداد المسارات الافتراضية: {e}")
        return "", ""

def apply_installation_defaults():
    """تطبيق الإعدادات الافتراضية للتثبيت"""
    try:
        from . import settings

        # إعداد المسارات
        output_path, backup_path = setup_default_paths()

        # نسخ الإعدادات الافتراضية المحسنة
        installation_settings = INSTALLATION_DEFAULTS.copy()

        # تحديث المسارات
        if output_path:
            installation_settings["save_path"] = output_path
        if backup_path:
            installation_settings["backup_path"] = backup_path

        # حفظ الإعدادات
        success = settings.save_settings(installation_settings)

        if success:
            print("✅ تم تطبيق الإعدادات الافتراضية للتثبيت بنجاح")
            print(f"   🎨 السمة: {installation_settings['theme']}")
            print(f"   🌈 لون التمييز: {installation_settings['accent_color']}")
            print(f"   💾 مسار الحفظ: {installation_settings['save_path']}")
            return True
        else:
            print("❌ فشل في حفظ الإعدادات الافتراضية")
            return False

    except Exception as e:
        print(f"❌ خطأ في تطبيق الإعدادات الافتراضية: {e}")
        return False

def is_first_run():
    """فحص إذا كان هذا أول تشغيل للتطبيق"""
    try:
        from . import settings
        settings_file = settings.get_settings_file_path()
        return not os.path.exists(settings_file)
    except Exception:
        return True

def setup_first_run():
    """إعداد أول تشغيل للتطبيق"""
    try:
        if is_first_run():
            print("🚀 أول تشغيل للتطبيق - إعداد الإعدادات الافتراضية...")
            success = apply_installation_defaults()

            if success:
                print("🎉 تم إعداد التطبيق بنجاح! مرحباً بك في ApexFlow")
                return True
            else:
                print("❌ فشل في إعداد التطبيق")
                return False
        else:
            print("📱 التطبيق معد مسبقاً")
            return True

    except Exception as e:
        print(f"❌ خطأ في إعداد أول تشغيل: {e}")
        return False

def create_settings_backup(settings_data):
    """إنشاء نسخة احتياطية من الإعدادات"""
    try:
        from . import settings

        # إنشاء مجلد النسخ الاحتياطية
        backup_dir = os.path.join(settings.get_settings_directory(), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # اسم الملف مع التاريخ والوقت
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"settings_backup_{timestamp}.json")

        # حفظ النسخة الاحتياطية
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=2)

        print(f"✅ تم إنشاء نسخة احتياطية: {backup_file}")
        return True

    except Exception as e:
        print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
        return False

# ===============================
# دوال مساعدة للتطوير
# Development Helper Functions
# ===============================

def print_current_settings():
    """طباعة الإعدادات الحالية للمراجعة"""
    try:
        from . import settings
        current = settings.load_settings()

        print("📋 الإعدادات الحالية:")
        print(f"   🎨 السمة: {current.get('theme', 'غير محدد')}")
        print(f"   🌈 لون التمييز: {current.get('accent_color', 'غير محدد')}")
        print(f"   🌍 اللغة: {current.get('language', 'غير محدد')}")
        print(f"   📐 حجم النافذة: {current.get('window_geometry', {}).get('width', 'غير محدد')}x{current.get('window_geometry', {}).get('height', 'غير محدد')}")
        print(f"   💾 مسار الحفظ: {current.get('save_path', 'غير محدد')}")

        return current

    except Exception as e:
        print(f"❌ خطأ في قراءة الإعدادات: {e}")
        return None

if __name__ == "__main__":
    # اختبار الدوال
    print("🧪 اختبار إدارة الإعدادات الافتراضية...")

    # اختبار إعداد أول تشغيل
    setup_first_run()

    # طباعة الإعدادات الحالية
    print_current_settings()

    print("✅ انتهى الاختبار")
