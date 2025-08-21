# نغمات الإشعارات / Notification Sounds

هذا المجلد يحتوي على ملفات النغمات الخفيفة للإشعارات في ApexFlow.

## الملفات المتوفرة / Available Files

- `notification_success.wav` - نغمة النجاح (نغمة صاعدة لطيفة)
- `notification_warning.wav` - نغمة التحذير (نغمة متوسطة)
- `notification_error.wav` - نغمة الخطأ (نغمة هابطة)
- `notification_info.wav` - نغمة المعلومات (نغمة بسيطة)

## إعادة إنشاء النغمات / Regenerating Sounds

يمكنك إعادة إنشاء النغمات باستخدام:
```bash
python create_sounds.py
```

## الخصائص التقنية / Technical Specifications

- **التردد**: 22050 Hz
- **البت**: 16-bit Mono
- **المدة**: 0.15-0.3 ثانية
- **الحجم**: خفيف (30% من الحد الأقصى)
- **التأثيرات**: Fade in/out للنعومة

## الاستخدام / Usage

يتم تشغيل النغمات تلقائياً عند ظهور الإشعارات، ويمكن التحكم فيها من إعدادات الإشعارات.