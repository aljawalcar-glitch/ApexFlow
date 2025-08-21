# خطة إعادة هيكلة مشروع ApexFlow

## الهيكل الحالي
المشروع حالياً لديه بعض المشاكل في التنظيم:
- ملفات مبعثرة بين المجلد الجذر والمجلدات الفرعية
- استيرادات غير متسقة بين الوحدات
- بعض الوظائف مكررة في أماكن متعددة

## الهيكل الجديد المقترح

```
ApexFlow/
├── README.md
├── CONTRIBUTING.md
├── LICENSE.txt
├── requirements.txt
├── main.py                    # نقطة الدخول الرئيسية
├── config/                    # ملفات الإعدادات والتكوين
│   ├── __init__.py
│   ├── settings.py            # إعدادات التطبيق
│   ├── version.py             # معلومات الإصدار
│   └── requirements.txt       # المتطلبات
├── src/                       # الكود المصدري الرئيسي
│   ├── __init__.py
│   ├── core/                  # الوظائف الأساسية لمعالجة PDF
│   │   ├── __init__.py
│   │   ├── merge.py           # دمج ملفات PDF
│   │   ├── split.py           # تقسيم ملفات PDF
│   │   ├── compress.py        # ضغط ملفات PDF
│   │   ├── convert.py         # تحويل ملفات PDF
│   │   ├── rotate.py          # تدوير ملفات PDF
│   │   ├── security.py        # حماية ملفات PDF
│   │   └── stamp_processor.py # معالجة الختم على ملفات PDF
│   ├── managers/              # مديرات النظام
│   │   ├── __init__.py
│   │   ├── operations_manager.py # إدارة العمليات
│   │   ├── notification_system.py # نظام الإشعارات
│   │   ├── theme_manager.py   # إدارة السمات
│   │   └── overlay_manager.py # إدارة التراكبات
│   ├── ui/                    # واجهة المستخدم
│   │   ├── __init__.py
│   │   ├── main_window.py     # النافذة الرئيسية
│   │   ├── pages/             # صفحات التطبيق
│   │   │   ├── __init__.py
│   │   │   ├── welcome_page.py
│   │   │   ├── merge_page.py
│   │   │   ├── split_page.py
│   │   │   ├── compress_page.py
│   │   │   ├── convert_page.py
│   │   │   ├── rotate_page.py
│   │   │   ├── security_page.py
│   │   │   ├── settings_ui.py
│   │   │   └── help_page.py
│   │   └── widgets/           # عناصر واجهة المستخدم
│   │       ├── __init__.py
│   │       ├── base_page.py
│   │       ├── file_list_frame.py
│   │       ├── file_item_widget.py
│   │       ├── animated_stacked_widget.py
│   │       ├── smart_drop_overlay.py
│   │       ├── stamp_manager.py
│   │       ├── svg_icon_button.py
│   │       ├── theme_aware_widget.py
│   │       ├── notification_settings.py
│   │       ├── app_info_widget.py
│   │       ├── interactive_stamp.py
│   │       ├── file_logger.py
│   │       ├── global_styles.py
│   │       └── ui_helpers.py
│   └── utils/                  # الأدوات المساعدة
│       ├── __init__.py
│       ├── logger.py           # نظام تسجيل الأخطاء
│       ├── translator.py       # نظام الترجمة
│       ├── settings.py         # إدارة الإعدادات
│       ├── diagnostics.py      # التشخيصات
│       ├── update_checker.py   # فحص التحديثات
│       ├── coordinate_calibrator.py
│       └── page_settings.py
├── assets/                    # الموارد الثابتة
│   ├── icons/
│   │   ├── ApexFlow.ico
│   │   └── default/
│   ├── menu_icons/
│   ├── screenshots/
│   └── logo.png
├── data/                      # البيانات
│   ├── translations.json
│   ├── font_settings.json
│   ├── notifications.json
│   └── stamps/
├── build_scripts/             # سكربتات البناء
│   ├── build_master.py
│   ├── run_build.bat
│   ├── run_master.bat
│   └── build_nsis_only.bat
├── docs/                      # الوثائق
│   ├── USER_GUIDE.md
│   ├── DIAGNOSTICS_GUIDE.md
│   ├── README_AppInfo.md
│   └── LICENSE.txt
└── reports/                   # التقارير
    └── system_diagnostics_*.txt
```

## خطوات التنفيذ

1. **إنشاء الهيكل الجديد للمجلدات**
2. **نقل الملفات إلى أماكنها الجديدة**
3. **تحديث مسارات الاستيراد في جميع الملفات**
4. **إزالة الملفات المكررة وغير الضرورية**
5. **تحديث ملفات البناء والتكوين**
