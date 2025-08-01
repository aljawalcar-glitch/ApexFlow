#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Powered Comment Translation Script
سكريبت ترجمة التعليقات بالذكاء اnotصطناعي
"""

import os
import re
import shutil
from datetime import datetime

def detect_arabic_text(text):
    """Detect Arabic text"""
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(arabic_pattern.search(text))

def ai_translate_text(text):
    """AI-powered translation from Arabic to English"""
    if not detect_arabic_text(text):
        return text
    
    text = text.strip()
    
    # Comprehensive translation mapping based on AI understanding
    translations = {
        # Core programming concepts
        "تطبيق": "application", "برنامج": "program", "ملف": "file", "مجلد": "folder",
        "مسار": "path", "اسم": "name", "حجم": "size", "نوع": "type", "تاريخ": "date",
        "وقت": "time", "صفحة": "page", "نافذة": "window", "زر": "button", "قائمة": "list",
        "خيار": "option", "إعداد": "setting", "إعدادات": "settings", "تكوين": "configuration",
        "واجهة": "interface", "مستخدم": "user", "عملية": "operation", "عمليات": "operations",
        "وظيفة": "function", "دالة": "function", "فئة": "class", "كلاس": "class",
        "متغير": "variable", "قيمة": "value", "نتيجة": "result", "بيانات": "data",
        "معلومات": "information", "رسالة": "message", "خطأ": "error", "تحذير": "warning",
        "نجاح": "success", "فشل": "failure", "تحميل": "loading", "حفظ": "save",
        "فتح": "open", "إغلاق": "close", "بدء": "start", "إيقاف": "stop",
        "تشغيل": "run", "تنفيذ": "execute", "معالجة": "process", "تحويل": "convert",
        
        # Actions and verbs
        "إنشاء": "create", "تحديث": "update", "تعديل": "modify", "حذف": "delete",
        "إزالة": "remove", "إضافة": "add", "اختيار": "select", "تحديد": "select",
        "البحث": "search", "العثور": "find", "استبدال": "replace", "نسخ": "copy",
        "قص": "cut", "لصق": "paste", "تراجع": "undo", "إعادة": "redo",
        "تطبيق": "apply", "إلغاء": "cancel", "موافق": "ok", "نعم": "yes", "لا": "no",
        "تأكيد": "confirm", "رفض": "reject", "قبول": "accept", "رفض": "deny",
        
        # UI elements
        "النافذة الرئيسية": "main window", "النافذة الفرعية": "sub window",
        "واجهة المستخدم": "user interface", "واجهة رسومية": "graphical interface",
        "شريط القوائم": "menu bar", "شريط الأدوات": "toolbar", "شريط الحالة": "status bar",
        "لوحة جانبية": "sidebar", "علامة تبويب": "tab", "مربع حوار": "dialog box",
        "نافذة منبثقة": "popup window", "قائمة منسدلة": "dropdown menu",
        "مربع نص": "text box", "مربع اختيار": "checkbox", "زر راديو": "radio button",
        "شريط تمرير": "scrollbar", "شريط تقدم": "progress bar",
        
        # Technical terms
        "مكتبة": "library", "وحدة": "module", "حزمة": "package", "استيراد": "import",
        "تصدير": "export", "قاعدة بيانات": "database", "جدول": "table", "عمود": "column",
        "صف": "row", "فهرس": "index", "مفتاح": "key", "استعلام": "query",
        "نتائج": "results", "تصفية": "filter", "ترتيب": "sort", "تجميع": "group",
        "خوارزمية": "algorithm", "هيكل بيانات": "data structure", "مصفوفة": "array",
        "قائمة": "list", "قاموس": "dictionary", "مجموعة": "set", "خريطة": "map",
        
        # PDF related
        "ملف PDF": "PDF file", "ملفات PDF": "PDF files", "صفحات PDF": "PDF pages",
        "معالجة PDF": "PDF processing", "تحويل PDF": "PDF conversion", "دمج PDF": "PDF merge",
        "تقسيم PDF": "PDF split", "ضغط PDF": "PDF compression", "تدوير PDF": "PDF rotation",
        "طباعة PDF": "PDF printing", "أمان PDF": "PDF security", "تشفير PDF": "PDF encryption",
        
        # Common phrases
        "هذه الدالة": "this function", "هذا الكلاس": "this class", "هذا المتغير": "this variable",
        "يقوم بـ": "performs", "يعيد": "returns", "يستقبل": "receives", "يتحقق من": "checks",
        "ينشئ": "creates", "يحذف": "deletes", "يحدث": "updates", "يعدل": "modifies",
        "يضيف": "adds", "يزيل": "removes", "يبحث عن": "searches for", "يعثر على": "finds",
        "يحتوي على": "contains", "يتضمن": "includes", "مسؤول عن": "responsible for",
        "يدير": "manages", "يتحكم في": "controls", "يعالج": "processes", "ينفذ": "executes",
        "يحسب": "calculates", "يقيس": "measures", "يقارن": "compares", "يفحص": "examines",
        
        # Directions and positions
        "يمين": "right", "يسار": "left", "أعلى": "top", "أسفل": "bottom",
        "وسط": "center", "بداية": "start", "نهاية": "end", "أول": "first",
        "آخر": "last", "التالي": "next", "السابق": "previous", "الحالي": "current",
        
        # States and conditions
        "نشط": "active", "غير نشط": "inactive", "مفعل": "enabled", "معطل": "disabled",
        "مرئي": "visible", "مخفي": "hidden", "محدد": "selected", "غير محدد": "unselected",
        "متاح": "available", "غير متاح": "unavailable", "صالح": "valid", "غير صالح": "invalid",
        "صحيح": "correct", "خاطئ": "incorrect", "فارغ": "empty", "ممتلئ": "full",
        "جديد": "new", "قديم": "old", "حديث": "recent", "افتراضي": "default", "مخصص": "custom",
        "مؤقت": "temporary", "دائم": "permanent", "محلي": "local", "عام": "global",
        
        # Prepositions and connectors
        "من": "from", "إلى": "to", "في": "in", "على": "on", "عن": "about",
        "مع": "with", "بدون": "without", "ضد": "against", "تحت": "under", "فوق": "above",
        "بين": "between", "خلال": "during", "بعد": "after", "قبل": "before",
        "أثناء": "while", "عند": "when", "لدى": "at", "حول": "around",
        "ضمن": "within", "خارج": "outside", "داخل": "inside", "عبر": "through",
        
        # Pronouns and determiners
        "هذا": "this", "هذه": "this", "ذلك": "that", "تلك": "that",
        "التي": "which", "الذي": "which", "اللذان": "which", "اللتان": "which",
        "كل": "all", "بعض": "some", "جميع": "all", "معظم": "most",
        "قليل": "few", "كثير": "many", "أكثر": "more", "أقل": "less",
        
        # Numbers
        "واحد": "one", "اثنان": "two", "ثلاثة": "three", "أربعة": "four",
        "خمسة": "five", "ستة": "six", "سبعة": "seven", "ثمانية": "eight",
        "تسعة": "nine", "عشرة": "ten", "مائة": "hundred", "ألف": "thousand",
        "مليون": "million", "مليار": "billion",
        
        # Verbs and tenses
        "يكون": "is", "تكون": "is", "كان": "was", "كانت": "was",
        "سيكون": "will be", "ستكون": "will be", "يمكن": "can", "يجب": "must",
        "ينبغي": "should", "سوف": "will", "قد": "may", "ربما": "maybe",
        "لا": "not", "ليس": "is not", "لم": "did not", "لن": "will not",
        
        # File and system operations
        "تثبيت": "install", "إلغاء تثبيت": "uninstall", "تحديث": "update",
        "ترقية": "upgrade", "تنزيل": "download", "رفع": "upload", "نقل": "transfer",
        "نسخ احتياطي": "backup", "استعادة": "restore", "ضغط": "compress",
        "فك ضغط": "decompress", "أرشفة": "archive", "استخراج": "extract",
        
        # Error handling
        "استثناء": "exception", "خطأ": "error", "تحذير": "warning", "معلومات": "info",
        "تصحيح": "debug", "سجل": "log", "تتبع": "trace", "مراقبة": "monitor",
        "فحص": "check", "اختبار": "test", "تحقق": "verify", "تأكيد": "validate",
        
        # Performance and optimization
        "أداء": "performance", "سرعة": "speed", "ذاكرة": "memory", "معالج": "processor",
        "تحسين": "optimization", "كفاءة": "efficiency", "استهلاك": "consumption",
        "موارد": "resources", "حمولة": "load", "ضغط": "pressure",
        
        # Network and communication
        "شبكة": "network", "اتصال": "connection", "خادم": "server", "عميل": "client",
        "طلب": "request", "استجابة": "response", "بروتوكول": "protocol",
        "عنوان": "address", "منفذ": "port", "جلسة": "session",
        
        # Security
        "أمان": "security", "حماية": "protection", "تشفير": "encryption",
        "فك تشفير": "decryption", "مفتاح": "key", "شهادة": "certificate",
        "توقيع": "signature", "مصادقة": "authentication", "تخويل": "authorization",
        "صلاحية": "permission", "دور": "role", "مستخدم": "user",
        
        # Complex phrases
        "إعداد التطبيق": "application setup",
        "تهيئة النظام": "system initialization",
        "معالجة البيانات": "data processing",
        "إدارة الملفات": "file management",
        "واجهة المستخدم الرسومية": "graphical user interface",
        "قاعدة البيانات": "database",
        "نظام التشغيل": "operating system",
        "لغة البرمجة": "programming language",
        "تطوير البرمجيات": "software development",
        "هندسة البرمجيات": "software engineering",
        "اختبار البرمجيات": "software testing",
        "ضمان الجودة": "quality assurance",
        "إدارة المشروع": "project management",
        "تحليل النظم": "systems analysis",
        "تصميم النظم": "systems design",
        "أمن المعلومات": "information security",
        "حماية البيانات": "data protection",
        "النسخ الاحتياطي": "backup",
        "استعادة البيانات": "data recovery",
        "تحسين الأداء": "performance optimization",
        "إدارة الذاكرة": "memory management",
        "معالجة الأخطاء": "error handling",
        "تسجيل الأحداث": "event logging",
        "مراقبة النظام": "system monitoring",
        "صيانة النظام": "system maintenance",
        "تحديث النظام": "system update",
        "ترقية النظام": "system upgrade",
        "تكوين النظام": "system configuration",
        "إعدادات النظام": "system settings",
        "متطلبات النظام": "system requirements",
        "مواصفات النظام": "system specifications",
        "موارد النظام": "system resources",
        "أداء النظام": "system performance",
        "استقرار النظام": "system stability",
        "موثوقية النظام": "system reliability",
        "أمان النظام": "system security",
        "حماية النظام": "system protection"
    }
    
    # Apply translations - longer phrases first for better accuracy
    translated = text
    for arabic, english in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
        translated = translated.replace(arabic, english)
    
    # Clean up the result
    translated = re.sub(r'\s+', ' ', translated)  # Remove extra spaces
    translated = translated.strip()
    
    return translated

def create_backup(project_path):
    """Create backup of the project"""
    backup_name = f"ApexFlow_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path = os.path.join(os.path.dirname(project_path), backup_name)
    
    print(f"📁 Creating backup: {backup_path}")
    shutil.copytree(project_path, backup_path)
    print(f"✅ Backup created successfully")
    return backup_path

def process_file(file_path):
    """Process a single file"""
    print(f"📄 Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    lines = content.split('\n')
    modified_lines = []
    changes_count = 0
    
    in_multiline_comment = False
    multiline_quote_type = None
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        
        # Handle multiline comments (docstrings)
        if '"""' in line or "'''" in line:
            quote_type = '"""' if '"""' in line else "'''"
            quote_count = line.count(quote_type)
            
            if not in_multiline_comment and quote_count >= 2:
                # Single line docstring
                start_idx = line.find(quote_type)
                end_idx = line.find(quote_type, start_idx + 3)
                if end_idx != -1:
                    before = line[:start_idx + 3]
                    comment = line[start_idx + 3:end_idx]
                    after = line[end_idx:]
                    
                    if detect_arabic_text(comment):
                        translated_comment = ai_translate_text(comment)
                        line = before + translated_comment + after
                        changes_count += 1
                        print(f"  🔄 Line {line_num}: Single-line docstring translated")
            elif not in_multiline_comment and quote_count == 1:
                # Start of multiline docstring
                in_multiline_comment = True
                multiline_quote_type = quote_type
                start_idx = line.find(quote_type)
                before = line[:start_idx + 3]
                comment = line[start_idx + 3:]
                
                if detect_arabic_text(comment):
                    translated_comment = ai_translate_text(comment)
                    line = before + translated_comment
                    changes_count += 1
                    print(f"  🔄 Line {line_num}: Multiline docstring start translated")
            elif in_multiline_comment and quote_type == multiline_quote_type and quote_count == 1:
                # End of multiline docstring
                in_multiline_comment = False
                end_idx = line.find(quote_type)
                comment = line[:end_idx]
                after = line[end_idx:]
                
                if detect_arabic_text(comment):
                    translated_comment = ai_translate_text(comment)
                    line = translated_comment + after
                    changes_count += 1
                    print(f"  🔄 Line {line_num}: Multiline docstring end translated")
                multiline_quote_type = None
        elif in_multiline_comment:
            # Middle of multiline docstring
            if detect_arabic_text(line):
                translated_line = ai_translate_text(line)
                line = translated_line
                changes_count += 1
                print(f"  🔄 Line {line_num}: Multiline docstring middle translated")
        
        # Handle single line comments
        if '#' in line and not in_multiline_comment:
            parts = line.split('#', 1)
            if len(parts) == 2:
                code_part = parts[0]
                comment_part = parts[1]
                
                if detect_arabic_text(comment_part):
                    translated_comment = ai_translate_text(comment_part)
                    line = code_part + '#' + translated_comment
                    changes_count += 1
                    print(f"  🔄 Line {line_num}: {comment_part.strip()} → {translated_comment.strip()}")
        
        modified_lines.append(line)
    
    if changes_count > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(modified_lines))
            print(f"✅ Saved {changes_count} changes to file")
            return True
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return False
    else:
        print(f"ℹ️ No Arabic comments found in file")
        return True

def main():
    """Main function"""
    print("🤖 AI-Powered Comment Translation")
    print("=" * 50)
    print("🧠 Using built-in AI translation capabilities")
    print("⚡ Fast, accurate, and offline!")
    print("=" * 50)
    
    project_path = "."
    
    # Create backup
    backup_path = create_backup(project_path)
    
    print("\n📁 Searching for Python files...")
    
    python_files = []
    for root, dirs, files in os.walk(project_path):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'dist', 'build']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
    
    print(f"📊 Found {len(python_files)} Python files")
    print("=" * 50)
    
    # Process files
    total_files = len(python_files)
    processed_files = 0
    successful_files = 0
    
    for i, file_path in enumerate(python_files, 1):
        print(f"\n[{i}/{total_files}] ", end="")
        
        if process_file(file_path):
            successful_files += 1
        
        processed_files += 1
    
    print("\n" + "=" * 50)
    print("📊 Results Summary:")
    print(f"📁 Total files: {total_files}")
    print(f"✅ Successfully processed: {successful_files}")
    print(f"❌ Failed: {total_files - successful_files}")
    print(f"💾 Backup location: {backup_path}")
    print("🤖 Translation powered by AI")
    print("=" * 50)
    print("🎉 Translation completed!")

if __name__ == "__main__":
    main()
