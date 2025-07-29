# ApexFlow - Antivirus Information
## معلومات مكافحة الفيروسات - ApexFlow

### Application Information / معلومات التطبيق
- **Name / الاسم:** ApexFlow PDF Manager
- **Version / الإصدار:** v5.2.2
- **Developer / المطور:** ApexFlow Team
- **Purpose / الغرض:** PDF Processing and Management Tool
- **Language / لغة البرمجة:** Python 3.13 with PySide6

### Digital Signature Status / حالة التوقيع الرقمي
- **Status / الحالة:** Self-signed (غير موقع تجارياً)
- **Reason / السبب:** Independent developer project
- **Security / الأمان:** Source code available for review

### False Positive Information / معلومات الإنذار الكاذب
This application may trigger false positives in antivirus software due to:
قد يؤدي هذا التطبيق إلى إنذارات كاذبة في برامج مكافحة الفيروسات بسبب:

1. **PyInstaller Packaging / تغليف PyInstaller:**
   - Uses PyInstaller to create executable
   - Common cause of false positives
   - سبب شائع للإنذارات الكاذبة

2. **File Operations / عمليات الملفات:**
   - Reads and writes PDF files
   - Creates temporary files during processing
   - ينشئ ملفات مؤقتة أثناء المعالجة

3. **System Integration / تكامل النظام:**
   - Accesses system fonts and resources
   - Uses Windows printing services
   - يستخدم خدمات الطباعة في Windows

### Whitelist Recommendations / توصيات القائمة البيضاء
To avoid false positives, please whitelist:
لتجنب الإنذارات الكاذبة، يرجى إضافة للقائمة البيضاء:

- **Executable Path / مسار الملف التنفيذي:** `C:\Program Files\ApexFlow\ApexFlow.exe`
- **Installation Directory / مجلد التثبيت:** `C:\Program Files\ApexFlow\`
- **Temp Directory / المجلد المؤقت:** `%TEMP%\ApexFlow\`

### Virus Total Information / معلومات Virus Total
- **Hash Type:** SHA256
- **Scan Results:** Available upon request
- **Last Scan:** Updated with each release

### Contact Information / معلومات الاتصال
- **Support / الدعم:** Available through GitHub issues
- **Source Code / الكود المصدري:** Available for security review
- **License / الترخيص:** Open source components

### Technical Details / التفاصيل التقنية
- **Framework:** PySide6 (Qt for Python)
- **PDF Libraries:** PyPDF2, PyMuPDF
- **Image Processing:** Pillow (PIL)
- **System Monitoring:** psutil
- **Build Tool:** PyInstaller 5.13+

### Security Measures / إجراءات الأمان
1. **No Network Activity / لا توجد أنشطة شبكة:**
   - Application works offline only
   - No data transmission to external servers

2. **File Access / الوصول للملفات:**
   - Only accesses user-selected files
   - No unauthorized file system access

3. **Registry Access / الوصول للسجل:**
   - Minimal registry access for settings only
   - No system-critical modifications

### For Antivirus Vendors / لمطوري برامج مكافحة الفيروسات
If you need additional information for whitelisting:
إذا كنت بحاجة لمعلومات إضافية للقائمة البيضاء:

- Source code review available
- Build process documentation provided
- Test samples available upon request
- Developer verification possible

---
**Note / ملاحظة:** This is a legitimate PDF processing application. Any detection as malware is a false positive.
هذا تطبيق شرعي لمعالجة ملفات PDF. أي اكتشاف كبرمجية خبيثة هو إنذار كاذب.
