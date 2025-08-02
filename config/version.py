#!/usr/bin/env python3
"""
ApexFlow Version Information
معلومات إصدار ApexFlow
"""

# معلومات الإصدار الحالي
VERSION = "v5.3.0"
VERSION_INFO = (5, 3, 0, "stable")

# معلومات التطبيق
APP_NAME = "ApexFlow"
APP_DESCRIPTION_AR = "أداة شاملة لإدارة ومعالجة ملفات PDF"
APP_DESCRIPTION_EN = "A comprehensive tool for managing and processing PDF files"
APP_AUTHOR_AR = "فريق ApexFlow"
APP_AUTHOR_EN = "ApexFlow Team"
APP_COPYRIGHT_AR = "© 2024 فريق ApexFlow"
APP_COPYRIGHT_EN = "© 2024 ApexFlow Team"

# معلومات البناء
BUILD_DATE = "2025-01-22"
BUILD_TYPE = "Stable"
BUILD_INCLUDES = [
    "ملفات الترجمة (عربي/إنجليزي)",
    "إعدادات الخطوط والسمات",
    "جميع الأيقونات والأصول",
    "نظام الأختام التفاعلي",
    "إعدادات افتراضية محسنة",
    "ملفات التوثيق والترخيص"
]

# سجل التغييرات للإصدار الحالي
CHANGELOG = {
    "v5.3.0": [
        "• إصلاح خطأ `RuntimeError` في نظام الإشعارات.",
        "• تحديث رقم الإصدار في جميع ملفات المشروع.",
        "• تحسينات طفيفة في الأداء والاستقرار.",
        "• إصلاح مشكلة عدم ظهور نافذة \"إضافة مجلد\" في النسخة المجمّعة."
    ],
    "v5.2.2": [
        "• إضافة نظام أختام PDF تفاعلي متقدم",
        "• أزرار تكبير وتصغير الأختام مع أيقونات SVG",
        "• تحكم دقيق في حجم الأختام (3% لكل ضغطة)",
        "• إخفاء/إظهار ذكي للأزرار حسب تحديد الختم",
        "• تحسين نظام معايرة الإحداثيات للأختام",
        "• إضافة معالج الأختام المحسن",
        "• تحسين دقة حفظ الأختام في ملفات PDF",
        "• إزالة الرسائل المزعجة من الكونسول",
        "• تحسين واجهة المستخدم للأختام",
        "• إضافة أيقونات + و - بسيطة وواضحة"
    ],
    "v5.2.1": [
        "• إصدار مستقر جديد مع تحسينات شاملة",
        "• تحسين نظام السمات والألوان الموحد",
        "• إضافة تأثيرات بصرية متقدمة للقوائم والأزرار",
        "• تطوير صفحة الضغط مع شريط تقدم ذكي",
        "• تحسين صفحة التقسيم مع مسار حفظ تلقائي",
        "• إضافة تأثيرات لمعان وتمرير للواجهة",
        "• تحسين قائمة الملفات مع تدرجات لونية",
        "• إصلاح مشاكل تحليل الأنماط والتوافق",
        "• تحسين شريط التمرير مع تصميم عصري",
        "• إضافة شفافية للبطاقات والعناصر",
        "• تحديث نظام الإصدارات الموحد"
    ],
    "Beta v4.6.12": [
        "• استبدال الإيموجي بأيقونات حقيقية عالية الجودة",
        "• تحسين معالجة الأخطاء في جميع العمليات",
        "• إضافة شريط التقدم للعمليات الطويلة",
        "• تحسين مراقبة موارد النظام",
        "• إضافة إحصائيات مفصلة للعمليات",
        "• تطبيق الحدود الشفافة على العناصر الرئيسية",
        "• تحسين جودة عرض الشعار المخصص",
        "• إزالة رسائل debug من الإنتاج",
        "• تحسين الأداء والاستقرار العام",
        "• إزالة جميع الإيموجي لضمان أمان التصدير"
    ]
}

def get_version():
    """إرجاع رقم الإصدار الحالي"""
    return VERSION

def get_version_info():
    """إرجاع معلومات الإصدار كـ tuple"""
    return VERSION_INFO

def get_full_version_string():
    """إرجاع نص الإصدار الكامل"""
    try:
        from modules.settings import load_settings
        settings = load_settings()
        language = settings.get("language", "ar")
        author = APP_AUTHOR_AR if language == "ar" else APP_AUTHOR_EN
    except:
        author = APP_AUTHOR_AR
    
    return f"{APP_NAME} {VERSION} - {author}"

def get_about_text():
    """إرجاع نص حول التطبيق"""
    try:
        from modules.settings import load_settings
        settings = load_settings()
        language = settings.get("language", "ar")
    except:
        language = "ar"
    
    if language == "ar":
        # النص باللغة العربية
        return f"""
{APP_NAME} {VERSION}

{APP_DESCRIPTION_AR}

{APP_COPYRIGHT_AR}
تاريخ البناء: {BUILD_DATE}
نوع البناء: {BUILD_TYPE}

تم تطوير هذا التطبيق باستخدام:
• Python 3.13
• PySide6 للواجهة الرسومية  
• PyPDF2 & PyMuPDF لمعالجة ملفات PDF
• Pillow لمعالجة الصور
• psutil لمراقبة النظام

الميزات الجديدة في هذا الإصدار:
{chr(10).join('• ' + feature for feature in CHANGELOG[VERSION])}
"""
    else:
        # النص باللغة الإنجليزية
        return f"""
{APP_NAME} {VERSION}

{APP_DESCRIPTION_EN}

{APP_COPYRIGHT_EN}
Build Date: {BUILD_DATE}
Build Type: {BUILD_TYPE}

This application was developed using:
• Python 3.13
• PySide6 for the graphical interface
• PyPDF2 & PyMuPDF for PDF processing
• Pillow for image processing
• psutil for system monitoring

New features in this version:
{chr(10).join('• ' + feature for feature in CHANGELOG[VERSION])}
"""

if __name__ == "__main__":
    print("=" * 50)
    print(f"معلومات إصدار {APP_NAME}")
    print("=" * 50)
    print(f"الإصدار: {VERSION}")
    print(f"التطبيق: {APP_NAME}")
    print(f"الوصف: {APP_DESCRIPTION_AR}")
    print(f"المطور: {APP_AUTHOR_AR}")
    print(f"تاريخ البناء: {BUILD_DATE}")
    print(f"نوع البناء: {BUILD_TYPE}")
    print("=" * 50)
    print("\nالميزات الجديدة:")
    for feature in CHANGELOG[VERSION]:
        print(f"  {feature}")
    print("=" * 50)
