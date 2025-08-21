# -*- coding: utf-8 -*-
"""
وحدة ضغط ملفات PDF باستخدام PyMuPDF + Pillow لضغط فعلي للصور.
"""

import os
import io
from typing import Dict, Any
from PIL import Image
from utils.logger import info, warning, error

_fitz = None

def _get_fitz():
    global _fitz
    if _fitz is None:
        import fitz  # PyMuPDF
        _fitz = fitz
    return _fitz

def get_compression_settings(level: int) -> Dict[str, Any]:
    settings = {
        1: {"image_quality": 95, "resize_factor": 1.0, "remove_metadata": False, "description": "ضغط خفيف - جودة عالية"},
        2: {"image_quality": 85, "resize_factor": 0.95, "remove_metadata": False, "description": "ضغط متوسط - توازن"},
        3: {"image_quality": 75, "resize_factor": 0.9, "remove_metadata": True, "description": "ضغط قياسي - موصى به"},
        4: {"image_quality": 60, "resize_factor": 0.8, "remove_metadata": True, "description": "ضغط عالي - حجم أقل"},
        5: {"image_quality": 40, "resize_factor": 0.7, "remove_metadata": True, "description": "ضغط قوي جداً - أصغر حجم"}
    }
    return settings.get(level, settings[3])

def format_file_size(size_bytes: int) -> str:
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
    ضغط PDF فعلي مع إعادة ترميز الصور وتقليل دقتها.
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        if not input_file.lower().endswith('.pdf'):
            raise ValueError(f"الملف ليس PDF: {input_file}")

        fitz = _get_fitz()
        doc = fitz.open(input_file)
        original_size = os.path.getsize(input_file)
        settings = get_compression_settings(compression_level)

        info(f"📄 بدء ضغط {os.path.basename(input_file)}")
        info(f"المستوى {compression_level} - {settings['description']}")
        info(f"الحجم الأصلي: {format_file_size(original_size)}")

        for page_index in range(len(doc)):
            page = doc[page_index]
            images = page.get_images(full=True)
            for img_index, img_info in enumerate(images):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]

                try:
                    image = Image.open(io.BytesIO(image_data))
                    new_width = int(image.width * settings["resize_factor"])
                    new_height = int(image.height * settings["resize_factor"])
                    image = image.resize((new_width, new_height), Image.LANCZOS)

                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format="JPEG", quality=settings["image_quality"])
                    img_byte_arr = img_byte_arr.getvalue()

                    doc.update_image(xref, img_byte_arr)
                except Exception as img_err:
                    warning(f"تعذر ضغط صورة في الصفحة {page_index+1}: {img_err}")

        if settings["remove_metadata"]:
            doc.set_metadata({})

        save_options = {"garbage": 4, "deflate": True, "clean": True}
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        doc.save(output_file, **save_options)
        doc.close()

        compressed_size = os.path.getsize(output_file)
        ratio = (original_size - compressed_size) / original_size * 100
        info(f"✅ تم الضغط: {format_file_size(original_size)} → {format_file_size(compressed_size)} ({ratio:.1f}% توفير)")

        return True

    except Exception as e:
        error(f"فشل الضغط: {e}")
        return False

def batch_compress(input_folder: str, output_folder: str, compression_level: int = 3) -> Dict[str, Any]:
    results = {'processed': 0, 'successful': 0, 'failed': 0, 'total_original_size': 0, 'total_compressed_size': 0, 'files': []}
    try:
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"المجلد غير موجود: {input_folder}")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
        info(f"تم العثور على {len(pdf_files)} ملف PDF")

        for filename in pdf_files:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"compressed_{filename}")

            results['processed'] += 1
            original_size = os.path.getsize(input_path)
            results['total_original_size'] += original_size

            if compress_pdf(input_path, output_path, compression_level):
                compressed_size = os.path.getsize(output_path)
                results['total_compressed_size'] += compressed_size
                results['successful'] += 1
                results['files'].append({
                    'filename': filename,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
                })
            else:
                results['failed'] += 1

        return results
    except Exception as e:
        error(f"خطأ في الضغط المجمع: {str(e)}")
        return results

def test_compression_levels(input_file: str, output_folder: str) -> Dict[str, Any]:
    if not os.path.exists(input_file):
        return {"error": "الملف غير موجود"}
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    original_size = os.path.getsize(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    results = {"original_file": input_file, "original_size": original_size, "levels": {}}
    info(f"اختبار مستويات الضغط لملف: {os.path.basename(input_file)}")
    info(f"الحجم الأصلي: {format_file_size(original_size)}")
    info("-" * 60)

    for level in range(1, 6):
        output_file = os.path.join(output_folder, f"{base_name}_level_{level}.pdf")
        success = compress_pdf(input_file, output_file, level)
        if success:
            compressed_size = os.path.getsize(output_file)
            compression_ratio = ((original_size - compressed_size) / original_size) * 100
            results["levels"][level] = {
                "output_file": output_file,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "settings": get_compression_settings(level),
                "success": True
            }
            info(f"المستوى {level}: {format_file_size(compressed_size)} ({compression_ratio:.1f}% توفير)")
        else:
            results["levels"][level] = {"success": False}
            warning(f"المستوى {level}: فشل")
    return results

if __name__ == "__main__":
    info("وحدة الضغط المحسنة (PyMuPDF + Pillow) تم تحميلها بنجاح")
    info("الميزات:")
    info("- ضغط الصور الفعلي")
    info("- إزالة البيانات الوصفية")
    info("- 5 مستويات ضغط")
    info("- إحصائيات مفصلة")
