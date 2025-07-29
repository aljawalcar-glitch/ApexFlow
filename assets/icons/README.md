# 🎨 نظام الأيقونات SVG - ApexFlow

## 📁 هيكل المجلدات

```
assets/icons/
├── default/          # السمة الافتراضية
│   ├── chevron-right.svg    # التالي
│   ├── chevron-left.svg     # السابق
│   ├── rotate-ccw.svg       # تدوير يسار
│   ├── rotate-cw.svg        # تدوير يمين
│   ├── folder-open.svg      # اختر ملف
│   ├── save.svg             # حفظ
│   ├── refresh-cw.svg       # إعادة تعيين
│   ├── trash-2.svg          # حذف
│   ├── merge.svg            # دمج
│   ├── scissors.svg         # تقسيم
│   ├── archive.svg          # ضغط
│   ├── settings.svg         # إعدادات
│   ├── image.svg            # صورة
│   ├── file-text.svg        # نص
│   └── plus.svg             # إضافة
├── outline/          # سمة خطوط خارجية (مستقبلي)
├── filled/           # سمة ممتلئة (مستقبلي)
└── minimal/          # سمة بسيطة (مستقبلي)
```

## 🎯 المواصفات التقنية

- **التنسيق**: SVG (Vector Graphics)
- **الحجم**: 24x24px (قابل للتكبير)
- **سماكة الخطوط**: 2px
- **النمط**: Outline مع currentColor
- **التوافق**: جميع أحجام الشاشات

## 🚀 كيفية الاستخدام

### 1. استيراد النظام
```python
from ui.svg_icon_button import SVGIconButton, create_navigation_button, create_rotation_button, create_action_button
```

### 2. إنشاء أزرار بأيقونات

#### أزرار التنقل
```python
next_btn = create_navigation_button("next", 20, "الصفحة التالية")
prev_btn = create_navigation_button("prev", 20, "الصفحة السابقة")
```

#### أزرار التدوير
```python
rotate_right_btn = create_rotation_button("right", 20, "تدوير يمين")
rotate_left_btn = create_rotation_button("left", 20, "تدوير يسار")
```

#### أزرار الإجراءات
```python
save_btn = create_action_button("save", 20, "حفظ الملف")
delete_btn = create_action_button("delete", 16, "حذف")
folder_btn = create_action_button("folder", 20, "اختر ملف")
```

### 3. نظام الألوان التلقائي
```python
# الأزرار تطبق لون السمة تلقائياً
button = create_action_button("save", 20, "حفظ")  # سيستخدم لون السمة

# أزرار الحذف تستخدم الأحمر تلقائياً
delete_btn = create_action_button("delete", 16, "حذف")  # أحمر تلقائياً
```

### 4. تحديث السمة
```python
# تحديث جميع الأزرار عند تغيير السمة
from ui.svg_icon_button import update_all_theme_buttons
update_all_theme_buttons(parent_widget, "#3b82f6")  # أزرق جديد
```

## 🎨 نظام الألوان الذكي

### الألوان التلقائية:
- **الأزرار العادية**: لون السمة الحالي مع شفافية 90%
- **الخلفية العادية**: شفاف تماماً
- **الخلفية Hover**: لون السمة مع شفافية 8%
- **الخلفية Pressed**: لون السمة مع شفافية 15%
- **الحدود Hover**: لون السمة مع شفافية 25%
- **أزرار الحذف**: أحمر ثابت `#dc3545`
- **الأزرار المعطلة**: رمادي `#666666`

### السمات المدعومة:
- **Dark**: `#ff6f00` (برتقالي)
- **Light**: `#2563eb` (أزرق)
- **Blue**: `#3b82f6` (أزرق فاتح)
- **Green**: `#10b981` (أخضر)
- **Purple**: `#8b5cf6` (بنفسجي)

## 📋 قائمة الأيقونات المتاحة

| الملف | الاستخدام |
|-------|----------|
| chevron-right.svg | التالي |
| chevron-left.svg | السابق |
| rotate-ccw.svg | تدوير يسار |
| rotate-cw.svg | تدوير يمين |
| folder-open.svg | اختر ملف |
| save.svg | حفظ |
| refresh-cw.svg | إعادة تعيين |
| trash-2.svg | حذف |
| merge.svg | دمج |
| scissors.svg | تقسيم |
| archive.svg | ضغط |
| settings.svg | إعدادات |
| image.svg | صورة |
| file-text.svg | نص |
| plus.svg | إضافة |

## 🔧 إضافة أيقونات جديدة

1. إنشاء ملف SVG جديد في `default/`
2. استخدام `currentColor` للون
3. حجم 24x24px وسماكة خط 2px
4. إضافة الأيقونة لقاموس `action_icons` في `svg_icon_button.py`

## 💡 نصائح

- استخدم `currentColor` في SVG للتحكم في اللون
- احتفظ بنفس سماكة الخطوط للتناسق
- اختبر الأيقونات على خلفيات مختلفة
- استخدم أحجام مناسبة (16px للأزرار الصغيرة، 20-24px للعادية)
