# 🛡️ ApexFlow Security Information

## 🔒 Security Assurance / ضمان الأمان

**ApexFlow is a legitimate PDF processing application. Any antivirus detection is a false positive.**

**ApexFlow هو تطبيق شرعي لمعالجة ملفات PDF. أي اكتشاف من برامج مكافحة الفيروسات هو إنذار كاذب.**

---

## 🚨 False Positive Alert / تنبيه الإنذار الكاذب

### Why might antivirus software flag ApexFlow? / لماذا قد تعتبر برامج مكافحة الفيروسات ApexFlow مشبوهاً؟

1. **PyInstaller Packaging** / تغليف PyInstaller
   - ApexFlow is packaged using PyInstaller
   - This is a common cause of false positives
   - Many legitimate applications face this issue

2. **File Operations** / عمليات الملفات
   - The app reads and writes PDF files
   - Creates temporary files during processing
   - These operations can trigger heuristic detection

3. **No Digital Signature** / عدم وجود توقيع رقمي
   - The application is not commercially signed
   - This increases false positive likelihood

---

## ✅ How to Verify ApexFlow is Safe / كيفية التحقق من أمان ApexFlow

### 1. **Source Code Review** / مراجعة الكود المصدري
- Complete source code is available
- No obfuscated or hidden code
- Transparent build process

### 2. **Hash Verification** / التحقق من Hash
- File hashes are provided with each release
- Compare with official hashes to verify integrity
- Use the included `file_hashes.txt`

### 3. **Behavioral Analysis** / تحليل السلوك
- Application works completely offline
- No network connections
- No data transmission to external servers
- Only accesses user-selected files

---

## 🛠️ How to Whitelist ApexFlow / كيفية إضافة ApexFlow للقائمة البيضاء

### Windows Defender:
1. Open Windows Security
2. Go to "Virus & threat protection"
3. Click "Manage settings" under "Virus & threat protection settings"
4. Scroll down to "Exclusions"
5. Click "Add or remove exclusions"
6. Add these paths:
   - `C:\Program Files\ApexFlow\`
   - `C:\Program Files\ApexFlow\ApexFlow.exe`

### Other Antivirus Software:
- Add the installation directory to exclusions
- Add the executable file to trusted applications
- Consult your antivirus documentation for specific steps

---

## 📋 Technical Details / التفاصيل التقنية

### Application Information:
- **Name:** ApexFlow PDF Manager
- **Version:** v5.2.2
- **Developer:** ApexFlow Team
- **Programming Language:** Python 3.13
- **GUI Framework:** PySide6 (Qt)
- **Build Tool:** PyInstaller

### Libraries Used:
- **PyPDF2:** PDF processing
- **PyMuPDF (fitz):** Advanced PDF operations
- **Pillow (PIL):** Image processing
- **psutil:** System monitoring
- **PySide6:** User interface

### Security Features:
- ✅ No network activity
- ✅ No data collection
- ✅ No unauthorized file access
- ✅ No system modifications
- ✅ No hidden processes
- ✅ Clean, readable code

---

## 🔍 Verification Files / ملفات التحقق

The following files are included for security verification:

1. **`ANTIVIRUS_INFO.md`** - Detailed antivirus information
2. **`SECURITY_VERIFICATION.txt`** - Security checklist
3. **`file_hashes.txt`** - File integrity hashes
4. **`security_report.json`** - Comprehensive security report

---

## 📞 Contact for Security Concerns / الاتصال لمخاوف الأمان

If you have security concerns or need additional verification:

- **GitHub Issues:** Report false positives
- **Documentation:** Complete technical documentation available
- **Source Code:** Available for security review

---

## ⚖️ Legal Disclaimer / إخلاء المسؤولية القانونية

This application is provided "as is" without warranty. The developers are not responsible for any false positive detections by antivirus software. Users should make their own security assessments based on the provided information and verification methods.

---

## 🏆 Trust Indicators / مؤشرات الثقة

- ✅ **Open Source Components:** Uses well-known, trusted libraries
- ✅ **Transparent Build:** Build process is documented and reproducible
- ✅ **No Obfuscation:** Code is clear and readable
- ✅ **Predictable Behavior:** Application behavior is documented
- ✅ **Community Verified:** Available for community security review

---

**Remember: Always verify software from official sources and use the provided hash verification methods.**

**تذكر: تحقق دائماً من البرامج من المصادر الرسمية واستخدم طرق التحقق من Hash المقدمة.**
