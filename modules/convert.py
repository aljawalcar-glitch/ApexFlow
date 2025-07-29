"""
PDF Conversion Module
وحدة تحويل ملفات PDF
This module provides functionality to convert PDF files to other formats and vice versa.
"""

import os
import io
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Optional, Dict, Any
import tempfile

def pdf_to_images(input_file: str, output_folder: str, 
                 image_format: str = "PNG", dpi: int = 150) -> bool:
    """
    Convert PDF pages to image files.
    تحويل صفحات PDF إلى ملفات صور
    
    Args:
        input_file (str): Path to the input PDF file
        output_folder (str): Folder where images will be saved
        image_format (str): Output image format (PNG, JPEG, TIFF)
        dpi (int): Resolution in DPI
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # التحقق من وجود الملف المدخل
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        if not input_file.lower().endswith('.pdf'):
            raise ValueError(f"الملف ليس PDF: {input_file}")
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # فتح ملف PDF
        pdf_document = fitz.open(input_file)
        total_pages = len(pdf_document)
        
        print(f"تحويل {total_pages} صفحة إلى صور {image_format}")
        print(f"الدقة: {dpi} DPI")
        
        # تحويل كل صفحة
        for page_num in range(total_pages):
            page = pdf_document[page_num]
            
            # تحديد معامل التكبير حسب DPI
            zoom = dpi / 72.0  # 72 DPI هو الافتراضي
            mat = fitz.Matrix(zoom, zoom)
            
            # تحويل الصفحة إلى صورة
            pix = page.get_pixmap(matrix=mat)
            
            # تحديد اسم الملف
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_filename = f"{base_name}_page_{page_num + 1:03d}.{image_format.lower()}"
            output_path = os.path.join(output_folder, output_filename)
            
            # حفظ الصورة
            if image_format.upper() == "PNG":
                pix.save(output_path)
            else:
                # تحويل إلى PIL للتنسيقات الأخرى
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                img.save(output_path, image_format.upper())
            
            if (page_num + 1) % 10 == 0:
                print(f"تم تحويل {page_num + 1}/{total_pages} صفحة")
        
        pdf_document.close()
        print(f"تم تحويل جميع الصفحات بنجاح إلى: {output_folder}")
        return True
        
    except Exception as e:
        print(f"خطأ في تحويل PDF إلى صور: {str(e)}")
        return False

def images_to_pdf(image_files: List[str], output_file: str, 
                 page_size: str = "A4") -> bool:
    """
    Convert image files to a single PDF.
    تحويل ملفات الصور إلى PDF واحد
    
    Args:
        image_files (List[str]): List of image file paths
        output_file (str): Path for the output PDF file
        page_size (str): Page size (A4, A3, Letter, etc.)
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        if not image_files:
            raise ValueError("لا توجد ملفات صور للتحويل")
        
        # التحقق من وجود ملفات الصور
        valid_images = []
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        
        for img_file in image_files:
            if os.path.exists(img_file):
                ext = os.path.splitext(img_file)[1].lower()
                if ext in supported_formats:
                    valid_images.append(img_file)
                else:
                    print(f"تحذير: تنسيق غير مدعوم: {img_file}")
            else:
                print(f"تحذير: ملف غير موجود: {img_file}")
        
        if not valid_images:
            raise ValueError("لا توجد ملفات صور صحيحة")
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # إنشاء مستند PDF جديد
        pdf_document = fitz.open()
        
        # تحديد أبعاد الصفحة
        page_sizes = {
            "A4": (595, 842),
            "A3": (842, 1191),
            "Letter": (612, 792),
            "Legal": (612, 1008)
        }
        
        page_width, page_height = page_sizes.get(page_size, page_sizes["A4"])
        
        print(f"تحويل {len(valid_images)} صورة إلى PDF")
        print(f"حجم الصفحة: {page_size}")
        
        # إضافة كل صورة كصفحة
        for i, img_file in enumerate(valid_images):
            try:
                # فتح الصورة
                img = Image.open(img_file)
                
                # تحويل إلى RGB إذا لزم الأمر
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # حساب أبعاد الصورة المناسبة للصفحة
                img_width, img_height = img.size
                scale_x = page_width / img_width
                scale_y = page_height / img_height
                scale = min(scale_x, scale_y)  # الحفاظ على النسبة
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                # تغيير حجم الصورة
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # حفظ الصورة مؤقتاً
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    img_resized.save(temp_file.name, 'PNG')
                    temp_path = temp_file.name
                
                # إنشاء صفحة جديدة
                page = pdf_document.new_page(width=page_width, height=page_height)
                
                # حساب موضع الصورة في المنتصف
                x = (page_width - new_width) / 2
                y = (page_height - new_height) / 2
                
                # إدراج الصورة
                page.insert_image(fitz.Rect(x, y, x + new_width, y + new_height), 
                                filename=temp_path)
                
                # حذف الملف المؤقت
                os.unlink(temp_path)
                
                if (i + 1) % 5 == 0:
                    print(f"تم معالجة {i + 1}/{len(valid_images)} صورة")
                    
            except Exception as e:
                print(f"خطأ في معالجة الصورة {img_file}: {str(e)}")
                continue
        
        # حفظ ملف PDF
        pdf_document.save(output_file)
        pdf_document.close()
        
        print(f"تم تحويل الصور بنجاح إلى: {output_file}")
        return True
        
    except Exception as e:
        print(f"خطأ في تحويل الصور إلى PDF: {str(e)}")
        return False

def pdf_to_text(input_file: str, output_file: str, 
               encoding: str = "utf-8") -> bool:
    """
    Extract text from PDF and save to text file.
    استخراج النص من PDF وحفظه في ملف نصي
    
    Args:
        input_file (str): Path to the input PDF file
        output_file (str): Path for the output text file
        encoding (str): Text encoding (utf-8, cp1256 for Arabic)
        
    Returns:
        bool: True if extraction was successful, False otherwise
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        # فتح ملف PDF
        pdf_document = fitz.open(input_file)
        total_pages = len(pdf_document)
        
        print(f"استخراج النص من {total_pages} صفحة")
        
        # استخراج النص من جميع الصفحات
        full_text = ""
        for page_num in range(total_pages):
            page = pdf_document[page_num]
            page_text = page.get_text()
            
            if page_text.strip():
                full_text += f"--- الصفحة {page_num + 1} ---\n"
                full_text += page_text + "\n\n"
            
            if (page_num + 1) % 10 == 0:
                print(f"تم معالجة {page_num + 1}/{total_pages} صفحة")
        
        pdf_document.close()
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # حفظ النص
        with open(output_file, 'w', encoding=encoding) as text_file:
            text_file.write(full_text)
        
        print(f"تم استخراج النص بنجاح إلى: {output_file}")
        return True
        
    except Exception as e:
        print(f"خطأ في استخراج النص: {str(e)}")
        return False

def text_to_pdf(input_file: str, output_file: str, 
               font_size: int = 12, encoding: str = "utf-8") -> bool:
    """
    Convert text file to PDF.
    تحويل ملف نصي إلى PDF
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path for the output PDF file
        font_size (int): Font size for the text
        encoding (str): Text encoding
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        # قراءة النص
        with open(input_file, 'r', encoding=encoding) as text_file:
            text_content = text_file.read()
        
        if not text_content.strip():
            raise ValueError("الملف النصي فارغ")
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # إنشاء مستند PDF جديد
        pdf_document = fitz.open()
        
        # إعدادات الصفحة
        page_width, page_height = 595, 842  # A4
        margin = 50
        line_height = font_size + 4
        
        # تقسيم النص إلى أسطر
        lines = text_content.split('\n')
        lines_per_page = int((page_height - 2 * margin) / line_height)
        
        print(f"تحويل النص إلى PDF ({len(lines)} سطر)")
        
        # إنشاء الصفحات
        current_line = 0
        page_num = 0
        
        while current_line < len(lines):
            # إنشاء صفحة جديدة
            page = pdf_document.new_page(width=page_width, height=page_height)
            page_num += 1
            
            # إضافة النص إلى الصفحة
            y_position = margin
            lines_in_page = 0
            
            while (current_line < len(lines) and 
                   lines_in_page < lines_per_page and 
                   y_position < page_height - margin):
                
                line_text = lines[current_line]
                
                # إدراج النص
                try:
                    page.insert_text((margin, y_position), line_text, 
                                   fontsize=font_size, color=(0, 0, 0))
                except:
                    # في حالة وجود أحرف غير مدعومة
                    safe_text = line_text.encode('ascii', 'ignore').decode('ascii')
                    page.insert_text((margin, y_position), safe_text, 
                                   fontsize=font_size, color=(0, 0, 0))
                
                y_position += line_height
                lines_in_page += 1
                current_line += 1
            
            if page_num % 10 == 0:
                print(f"تم إنشاء {page_num} صفحة")
        
        # حفظ ملف PDF
        pdf_document.save(output_file)
        pdf_document.close()
        
        print(f"تم تحويل النص بنجاح إلى: {output_file} ({page_num} صفحة)")
        return True
        
    except Exception as e:
        print(f"خطأ في تحويل النص إلى PDF: {str(e)}")
        return False

def get_conversion_info(input_file: str) -> Dict[str, Any]:
    """
    Get information about a file for conversion.
    الحصول على معلومات ملف للتحويل
    
    Args:
        input_file (str): Path to the input file
        
    Returns:
        Dictionary containing file information
    """
    try:
        if not os.path.exists(input_file):
            return {"error": "الملف غير موجود"}
        
        file_ext = os.path.splitext(input_file)[1].lower()
        file_size = os.path.getsize(input_file)
        
        info = {
            "filename": os.path.basename(input_file),
            "file_path": input_file,
            "file_extension": file_ext,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "supported_conversions": []
        }
        
        # تحديد التحويلات المدعومة حسب نوع الملف
        if file_ext == '.pdf':
            info["supported_conversions"] = [
                "PDF إلى صور (PNG, JPEG, TIFF)",
                "PDF إلى نص",
                "استخراج الصور من PDF"
            ]
            
            # معلومات إضافية للـ PDF
            try:
                pdf_doc = fitz.open(input_file)
                info["page_count"] = len(pdf_doc)
                info["has_text"] = any(page.get_text().strip() for page in pdf_doc)
                info["has_images"] = any(page.get_images() for page in pdf_doc)
                pdf_doc.close()
            except:
                pass
                
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            info["supported_conversions"] = [
                "صورة إلى PDF",
                "تغيير تنسيق الصورة"
            ]
            
            # معلومات إضافية للصور
            try:
                img = Image.open(input_file)
                info["image_size"] = img.size
                info["image_mode"] = img.mode
                img.close()
            except:
                pass
                
        elif file_ext == '.txt':
            info["supported_conversions"] = [
                "نص إلى PDF"
            ]
            
            # معلومات إضافية للنص
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    info["line_count"] = len(content.split('\n'))
                    info["char_count"] = len(content)
            except:
                pass
        
        return info
        
    except Exception as e:
        return {"error": f"خطأ في قراءة الملف: {str(e)}"}

# مثال على الاستخدام
if __name__ == "__main__":
    # أمثلة على الاستخدام
    
    # تحويل PDF إلى صور
    # pdf_to_images("document.pdf", "images_output", "PNG", 150)
    
    # تحويل صور إلى PDF
    # image_files = ["image1.jpg", "image2.png", "image3.jpg"]
    # images_to_pdf(image_files, "output.pdf", "A4")
    
    # استخراج النص من PDF
    # pdf_to_text("document.pdf", "extracted_text.txt")
    
    # تحويل نص إلى PDF
    # text_to_pdf("text_file.txt", "text_output.pdf", font_size=14)
    
    # معلومات التحويل
    # info = get_conversion_info("document.pdf")
    # print(info)
    
    print("وحدة التحويل تم تحميلها بنجاح")