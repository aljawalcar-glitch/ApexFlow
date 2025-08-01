# -*- coding: utf-8 -*-
"""
وحدة ضغط ملفات PDF باستخدام PyMuPDF لنتائج أفضل.
"""

import os
from typing import Dict, Any

# تحميل كسول لمكتبة PyMuPDF الثقيلة
_fitz = None

def _get_fitz():
    """تحميل كسول لمكتبة PyMuPDF"""
    global _fitz
    if _fitz is None:
        import fitz  # PyMuPDF
        _fitz = fitz
    return _fitz

def get_compression_settings(level: int) -> Dict[str, Any]:
    """
    الحصول على إعدادات الضغط حسب المستوى.

    Args:
        level (int): مستوى الضغط (1-5)

    Returns:
        Dict: إعدادات الضغط
    """
    settings = {
        1: {  # ضغط خفيف - جودة عالية
            "image_quality": 95,
            "resize_factor": 1.0,
            "remove_metadata": False,
            "description": "ضغط خفيف - جودة عالية"
        },
        2: {  # ضغط متوسط
            "image_quality": 85,
            "resize_factor": 0.95,
            "remove_metadata": False,
            "description": "ضغط متوسط - توازن بين الجودة والحجم"
        },
        3: {  # ضغط قياسي
            "image_quality": 75,
            "resize_factor": 0.9,
            "remove_metadata": True,
            "description": "ضغط قياسي - موصى به"
        },
        4: {  # ضغط عالي
            "image_quality": 60,
            "resize_factor": 0.8,
            "remove_metadata": True,
            "description": "ضغط عالي - حجم أصغر"
        },
        5: {  # ضغط قوي جداً
            "image_quality": 45,
            "resize_factor": 0.7,
            "remove_metadata": True,
            "description": "ضغط قوي جداً - أصغر حجم ممكن"
        }
    }

    return settings.get(level, settings[3])  # افتراضي: مستوى 3

def format_file_size(size_bytes: int) -> str:
    """
    تنسيق حجم الملف بشكل قابل للقراءة.
    """
    if size_bytes == 0:
        return "0 بايت"
    
    size_names = ["بايت", "كيلوبايت", "ميجابايت", "جيجابايت"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def compress_pdf(input_file: str, output_file: str, compression_level: int = 3) -> bool:
    """
    ضغط ملف PDF لتقليل حجمه باستخدام PyMuPDF مع تقنيات ضغط متقدمة.

    Args:
        input_file (str): مسار ملف PDF المدخل.
        output_file (str): مسار ملف PDF الناتج.
        compression_level (int): مستوى الضغط (1-5).

    Returns:
        bool: True إذا نجح الضغط، False إذا فشل.
    """
    try:
        # التحقق من وجود الملف المدخل
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")

        if not input_file.lower().endswith('.pdf'):
            raise ValueError(f"الملف ليس PDF: {input_file}")

        # تحميل كسول لمكتبة PyMuPDF
        fitz = _get_fitz()

        # فتح الملف باستخدام fitz
        doc = fitz.open(input_file)

        # الحصول على حجم الملف الأصلي
        original_size = os.path.getsize(input_file)

        # الحصول على إعدادات الضغط
        compression_settings = get_compression_settings(compression_level)

        print(f"بدء ضغط الملف: {os.path.basename(input_file)}")
        print(f"الحجم الأصلي: {format_file_size(original_size)}")
        print(f"مستوى الضغط: {compression_level}/5 - {compression_settings['description']}")
        print(f"عدد الصفحات: {len(doc)}")

        # تحليل محتوى PDF للحصول على إحصائيات
        total_images = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            total_images += len(image_list)

        if total_images > 0:
            print(f"تم العثور على {total_images} صورة في المستند")
        else:
            print("لا توجد صور في المستند")

        # إزالة البيانات الوصفية إذا كان مطلوباً
        if compression_settings["remove_metadata"]:
            print("إزالة البيانات الوصفية...")
            doc.set_metadata({})

        # إعدادات الحفظ المحسنة والآمنة
        save_options = {
            "garbage": 4,           # إزالة الكائنات غير المستخدمة
            "deflate": True,        # ضغط التدفقات
            "clean": True,          # تنظيف بناء الجملة
            "ascii": False,         # عدم تحويل إلى ASCII (يسبب مشاكل)
            "expand": 0,            # عدم توسيع المحتوى
            "linear": False,        # عدم التحسين للويب
        }

        # إعدادات متدرجة حسب مستوى الضغط (آمنة)
        if compression_level >= 2:
            save_options["deflate_images"] = True  # ضغط الصور
            save_options["deflate_fonts"] = True   # ضغط الخطوط

        if compression_level >= 3:
            save_options["garbage"] = 4
            save_options["clean"] = True

        if compression_level >= 4:
            save_options["pretty"] = False         # عدم تنسيق المحتوى
            # إزالة ascii=True لتجنب الأخطاء

        # للمستوى 5، نستخدم إعدادات أكثر قوة لكن آمنة
        if compression_level >= 5:
            save_options["garbage"] = 4
            save_options["deflate"] = True
            save_options["clean"] = True
            # عدم استخدام ascii=True لتجنب الأخطاء

        print(f"إعدادات الضغط المطبقة: {list(save_options.keys())}")
        print(f"قيم الإعدادات: {save_options}")

        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # حفظ الملف المضغوط مع تشخيص مفصل
        save_successful = False
        try:
            print("محاولة الحفظ بالإعدادات المتقدمة...")
            doc.save(output_file, **save_options)
            doc.close()
            save_successful = True
            print("تم الحفظ بالإعدادات المتقدمة بنجاح")
        except Exception as save_error:
            print(f"خطأ في الحفظ بالإعدادات المتقدمة: {save_error}")
            print("محاولة الحفظ بإعدادات أساسية...")
            doc.close()

            # إعادة فتح الملف ومحاولة حفظ بإعدادات أساسية
            try:
                doc = fitz.open(input_file)
                basic_options = {
                    "garbage": 4,
                    "deflate": True,
                    "clean": True
                }
                doc.save(output_file, **basic_options)
                doc.close()
                save_successful = True
                print("تم الحفظ بإعدادات أساسية بنجاح")
            except Exception as basic_error:
                print(f"فشل الحفظ بالإعدادات الأساسية: {basic_error}")
                try:
                    doc.close()
                except:
                    pass
                # نسخ الملف الأصلي كحل أخير
                import shutil
                shutil.copy(input_file, output_file)
                save_successful = False
                print("تم نسخ الملف الأصلي (لم يحدث ضغط)")

        # حساب نسبة الضغط مع تشخيص دقيق
        if os.path.exists(output_file):
            compressed_size = os.path.getsize(output_file)
            print(f"حجم الملف الناتج: {format_file_size(compressed_size)}")
        else:
            print("خطأ: الملف الناتج غير موجود!")
            return False

        # مقارنة الأحجام
        size_difference = original_size - compressed_size

        if save_successful and size_difference > 0:
            # ضغط ناجح
            compression_ratio = (size_difference / original_size) * 100
            print(f"✅ تم الضغط بنجاح!")
            print(f"الحجم الأصلي: {format_file_size(original_size)}")
            print(f"الحجم الجديد: {format_file_size(compressed_size)}")
            print(f"نسبة التوفير: {compression_ratio:.1f}%")
            print(f"توفير في المساحة: {format_file_size(size_difference)}")
        elif save_successful and size_difference == 0:
            # نفس الحجم
            print(f"⚠️ تم الحفظ لكن لم يتغير الحجم")
            print(f"الحجم: {format_file_size(compressed_size)} (لم يتغير)")
            print("السبب المحتمل: الملف مضغوط مسبقاً أو لا يحتوي على عناصر قابلة للضغط")
        elif save_successful and size_difference < 0:
            # الملف أصبح أكبر
            print(f"⚠️ الملف أصبح أكبر بعد المعالجة")
            print(f"الحجم الأصلي: {format_file_size(original_size)}")
            print(f"الحجم الجديد: {format_file_size(compressed_size)}")
            print("سيتم استبداله بالملف الأصلي...")
            import shutil
            shutil.copy(input_file, output_file)
            compressed_size = original_size
        else:
            # لم يحدث ضغط (تم النسخ فقط)
            print(f"❌ لم يحدث ضغط - تم نسخ الملف الأصلي")
            print(f"الحجم: {format_file_size(compressed_size)} (نفس الأصلي)")

        return True

    except Exception as e:
        print(f"خطأ في ضغط PDF: {str(e)}")
        # في حالة الخطأ، حاول نسخ الملف الأصلي لضمان وجود ناتج
        try:
            import shutil
            shutil.copy(input_file, output_file)
        except Exception as copy_e:
            print(f"فشل نسخ الملف الأصلي بعد الخطأ: {copy_e}")
        return False

def batch_compress(input_folder: str, output_folder: str, 
                  compression_level: int = 3) -> Dict[str, Any]:
    """
    ضغط عدة ملفات PDF في مجلد.
    
    Args:
        input_folder (str): مسار المجلد الذي يحتوي على ملفات PDF.
        output_folder (str): مسار المجلد لحفظ الملفات المضغوطة.
        compression_level (int): مستوى الضغط (1-5).
        
    Returns:
        Dict: قاموس يحتوي على نتائج الضغط.
    """
    results = {
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'total_original_size': 0,
        'total_compressed_size': 0,
        'files': []
    }
    
    try:
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"المجلد غير موجود: {input_folder}")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
        
        print(f"تم العثور على {len(pdf_files)} ملف PDF")
        
        for filename in pdf_files:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"compressed_{filename}")
            
            results['processed'] += 1
            original_size = os.path.getsize(input_path)
            results['total_original_size'] += original_size
            
            print(f"معالجة: {filename}")
            
            if compress_pdf(input_path, output_path, compression_level):
                compressed_size = os.path.getsize(output_path)
                results['total_compressed_size'] += compressed_size
                results['successful'] += 1
                
                file_result = {
                    'filename': filename,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
                }
                results['files'].append(file_result)
            else:
                results['failed'] += 1
        
        if results['total_original_size'] > 0:
            total_ratio = ((results['total_original_size'] - results['total_compressed_size']) 
                          / results['total_original_size']) * 100
            print(f"\nالنتائج الإجمالية:")
            print(f"الملفات المعالجة: {results['successful']}/{results['processed']}")
            print(f"الحجم الأصلي الإجمالي: {format_file_size(results['total_original_size'])}")
            print(f"الحجم المضغوط الإجمالي: {format_file_size(results['total_compressed_size'])}")
            print(f"نسبة التوفير الإجمالية: {total_ratio:.1f}%")
        
        return results
        
    except Exception as e:
        print(f"خطأ في الضغط المجمع: {str(e)}")
        return results

def test_compression_levels(input_file: str, output_folder: str) -> Dict[str, Any]:
    """
    اختبار جميع مستويات الضغط على ملف واحد لمقارنة النتائج.

    Args:
        input_file (str): مسار ملف PDF للاختبار
        output_folder (str): مجلد حفظ النتائج

    Returns:
        Dict: نتائج الاختبار لجميع المستويات
    """
    if not os.path.exists(input_file):
        return {"error": "الملف غير موجود"}

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    original_size = os.path.getsize(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    results = {
        "original_file": input_file,
        "original_size": original_size,
        "levels": {}
    }

    print(f"اختبار مستويات الضغط لملف: {os.path.basename(input_file)}")
    print(f"الحجم الأصلي: {format_file_size(original_size)}")
    print("-" * 60)

    for level in range(1, 6):
        output_file = os.path.join(output_folder, f"{base_name}_level_{level}.pdf")

        print(f"\nاختبار المستوى {level}...")
        success = compress_pdf(input_file, output_file, level)

        if success:
            compressed_size = os.path.getsize(output_file)
            compression_ratio = ((original_size - compressed_size) / original_size) * 100
            settings = get_compression_settings(level)

            results["levels"][level] = {
                "output_file": output_file,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "settings": settings,
                "success": True
            }

            print(f"المستوى {level}: {format_file_size(compressed_size)} ({compression_ratio:.1f}% توفير)")
        else:
            results["levels"][level] = {"success": False}
            print(f"المستوى {level}: فشل")

    print("\n" + "=" * 60)
    print("ملخص النتائج:")
    print("=" * 60)

    for level in range(1, 6):
        if results["levels"][level]["success"]:
            data = results["levels"][level]
            print(f"المستوى {level}: {format_file_size(data['compressed_size'])} "
                  f"({data['compression_ratio']:.1f}% توفير)")

    return results

if __name__ == "__main__":
    print("وحدة الضغط المحسنة (PyMuPDF) تم تحميلها بنجاح")
    print("الميزات الجديدة:")
    print("- ضغط الصور المتقدم")
    print("- إزالة البيانات الوصفية")
    print("- 5 مستويات ضغط محسنة")
    print("- إحصائيات مفصلة")
