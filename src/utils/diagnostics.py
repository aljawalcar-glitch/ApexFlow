
"""
وحدة التشخيص
Diagnostics module for ApexFlow
"""
import os
import sys
import platform
import datetime
from pathlib import Path

def run_diagnostics():
    """
    تشغيل التشخيص وجمع المعلومات حول النظام والتطبيق
    Returns:
        str: نص يحتوي على نتائج التشخيص
    """
    results = []

    # معلومات النظام
    results.append("=== معلومات النظام ===")
    results.append(f"نظام التشغيل: {platform.system()} {platform.release()}")
    results.append(f"الإصدار: {platform.version()}")
    results.append(f"المعالج: {platform.processor()}")
    results.append(f"البنية: {platform.machine()}")
    results.append(f"اسم الحاسوب: {platform.node()}")
    results.append(f"المستخدم: {os.getlogin()}")

    # معلومات بايثون
    results.append("\n=== معلومات بايثون ===")
    results.append(f"إصدار بايثون: {platform.python_version()}")
    results.append(f"مسار بايثون: {sys.executable}")
    results.append(f"مسارات البحث:")
    for path in sys.path:
        results.append(f"  - {path}")

    # معلومات المتطلبات
    results.append("\n=== المتطلبات المثبتة ===")
    try:
        import pkg_resources
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        for package, version in sorted(installed_packages.items()):
            results.append(f"  - {package}=={version}")
    except ImportError:
        results.append("مكتبة pkg_resources غير متوفرة, لا يمكن عرض المتطلبات.")
    except Exception as e:
        results.append(f"خطأ في الحصول على المتطلبات: {str(e)}")

    # معلومات التطبيق
    results.append("\n=== معلومات التطبيق ===")
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        results.append(f"مسار التطبيق: {app_dir}")

        # التحقق من وجود الملفات المهمة
        important_files = ["main.py", "ui/__init__.py", "modules/__init__.py"]
        results.append("\nالتحقق من الملفات المهمة:")
        for file in important_files:
            file_path = os.path.join(os.path.dirname(app_dir), file)
            exists = "موجود" if os.path.exists(file_path) else "غير موجود"
            results.append(f"  - {file}: {exists}")

        # التحقق من وجود مجلدات مهمة
        important_dirs = ["ui", "modules", "resources"]
        results.append("\nالتحقق من المجلدات المهمة:")
        for dir_name in important_dirs:
            dir_path = os.path.join(os.path.dirname(app_dir), dir_name)
            exists = "موجود" if os.path.exists(dir_path) else "غير موجود"
            results.append(f"  - {dir_name}: {exists}")

    except Exception as e:
        results.append(f"خطأ في الحصول على معلومات التطبيق: {str(e)}")

    # معلومات الذاكرة والمعالج
    try:
        import psutil
        results.append("\n=== معلومات الأداء ===")
        memory = psutil.virtual_memory()
        results.append(f"الذاكرة الإجمالية: {memory.total / (1024**3):.2f} GB")
        results.append(f"الذاكرة المتوفرة: {memory.available / (1024**3):.2f} GB")
        results.append(f"نسبة استخدام الذاكرة: {memory.percent}%")

        cpu_percent = psutil.cpu_percent(interval=1)
        results.append(f"نسبة استخدام المعالج: {cpu_percent}%")

        disk = psutil.disk_usage('/')
        results.append(f"مساحة القرص الإجمالية: {disk.total / (1024**3):.2f} GB")
        results.append(f"مساحة القرص المتوفرة: {disk.free / (1024**3):.2f} GB")
        results.append(f"نسبة استخدام القرص: {disk.percent}%")
    except ImportError:
        results.append("\n=== معلومات الأداء ===")
        results.append("مكتبة psutil غير متوفرة")
    except Exception as e:
        results.append(f"خطأ في الحصول على معلومات الأداء: {str(e)}")

    # تاريخ التشخيص
    results.append(f"\n=== تاريخ التشخيص ===")
    results.append(f"التوقيت: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(results)

def export_diagnostics(diagnostics_text):
    """
    تصدير نتائج التشخيص إلى ملف
    Args:
        diagnostics_text (str): نص نتائج التشخيص
    Returns:
        str: مسار الملف الذي تم تصدير النتائج إليه
    """
    try:
        # إنشاء مجلد التشخيص إذا لم يكن موجودًا
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        diagnostics_dir = os.path.join(app_dir, "diagnostics")

        if not os.path.exists(diagnostics_dir):
            os.makedirs(diagnostics_dir)

        # إنشاء اسم الملف مع التاريخ والوقت
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"apexflow_diagnostics_{timestamp}.txt"
        file_path = os.path.join(diagnostics_dir, file_name)

        # كتابة النتائج إلى الملف
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(diagnostics_text)

        return file_path
    except Exception as e:
        raise Exception(f"خطأ في تصدير نتائج التشخيص: {str(e)}")
