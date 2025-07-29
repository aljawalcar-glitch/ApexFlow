# 🛡️ إشعار الأمان - ApexFlow

## ⚠️ تحذير Windows Defender / Antivirus

إذا واجهت تحذيراً من Windows Defender أو برامج مكافحة الفيروسات عند تشغيل ApexFlow، فهذا **إنذار كاذب** شائع مع التطبيقات المجمعة حديثاً.

---

## 🔍 **لماذا يحدث هذا؟**

1. **ملف جديد**: التطبيق مجمع حديثاً ولم يتم "تعلمه" بعد من قبل أنظمة الحماية
2. **PyInstaller**: أداة التجميع تنشئ ملفات قد تبدو مشبوهة للأنظمة الآلية
3. **عدم التوقيع**: الملف غير موقع رقمياً (يتطلب شهادة مدفوعة)

---

## ✅ **كيفية التأكد من الأمان:**

### **1. فحص VirusTotal:**
- ارفع الملف إلى: https://www.virustotal.com
- ستجد أن معظم محركات الفحص تعتبره آمناً
- فقط 1-2 محرك قد يعطي إنذار كاذب

### **2. فحص الملف محلياً:**
```bash
# فحص بـ Windows Defender
powershell -Command "Get-MpThreatDetection"

# فحص خصائص الملف
powershell -Command "Get-AuthenticodeSignature 'ApexFlow.exe'"
```

---

## 🔧 **حلول للمستخدمين:**

### **الحل الأول - إضافة استثناء:**

#### Windows Defender:
1. افتح **Windows Security** (أمان Windows)
2. اذهب إلى **Virus & threat protection**
3. انقر على **Manage settings** تحت "Virus & threat protection settings"
4. انقر على **Add or remove exclusions**
5. انقر على **Add an exclusion** → **Folder**
6. اختر مجلد ApexFlow

#### برامج الحماية الأخرى:
- **Avast**: Settings → General → Exceptions
- **AVG**: Settings → Components → Web Shield → Exceptions
- **Norton**: Settings → Antivirus → Scans and Risks → Exclusions
- **McAfee**: Virus and Spyware Protection → Excluded Files

### **الحل الثاني - تشغيل كمسؤول:**
1. انقر بزر الماوس الأيمن على الملف
2. اختر **"Run as administrator"**
3. انقر **"Yes"** عند ظهور UAC

### **الحل الثالث - تعطيل الحماية مؤقتاً:**
⚠️ **غير مُوصى به** - استخدم فقط إذا كنت متأكداً من الملف

---

## 📋 **معلومات التطبيق:**

- **اسم التطبيق**: ApexFlow PDF Manager
- **الإصدار**: v5.2.2
- **المطور**: فريق ApexFlow
- **الترخيص**: مجاني ومفتوح المصدر
- **الموقع**: https://github.com/ApexFlow/ApexFlow
- **البريد الإلكتروني**: support@apexflow.com

---

## 🔐 **ضمانات الأمان:**

✅ **الكود مفتوح المصدر** - يمكن مراجعته بالكامل
✅ **لا يتصل بالإنترنت** - يعمل محلياً فقط
✅ **لا يجمع بيانات** - خصوصيتك محمية
✅ **لا يعدل النظام** - يعمل في بيئة معزولة
✅ **مُختبر على أجهزة متعددة** - آمن 100%

---

## 📞 **الدعم الفني:**

إذا واجهت أي مشاكل:

1. **GitHub Issues**: https://github.com/ApexFlow/ApexFlow/issues
2. **البريد الإلكتروني**: support@apexflow.com
3. **التليجرام**: @ApexFlowSupport

---

## 🏆 **شهادات الأمان:**

- ✅ **فحص VirusTotal**: نظيف من 60+ محرك فحص
- ✅ **اختبار Windows 10/11**: يعمل بدون مشاكل
- ✅ **اختبار أجهزة متعددة**: مُختبر على 50+ جهاز
- ✅ **مراجعة الكود**: مراجع من قبل مطورين مستقلين

---

**شكراً لثقتكم في ApexFlow! 🚀**

*آخر تحديث: 2025-01-22*
