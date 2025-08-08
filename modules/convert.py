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
import arabic_reshaper
from bidi.algorithm import get_display
from modules.logger import info, warning, error

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
        
        info(f"تحويل {total_pages} صفحة إلى صور {image_format}")
        info(f"الدقة: {dpi} DPI")
        
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
                info(f"تم تحويل {page_num + 1}/{total_pages} صفحة")
        
        pdf_document.close()
        info(f"تم تحويل جميع الصفحات بنجاح إلى: {output_folder}")
        return True
        
    except Exception as e:
        error(f"خطأ في تحويل PDF إلى صور: {str(e)}")
        return False

def images_to_pdf(image_files: List[str], output_file: str) -> bool:
    """
    Convert image files to a single PDF without reducing quality.
    تحويل ملفات الصور إلى PDF واحد بدون تقليل الجودة
    
    Args:
        image_files (List[str]): List of image file paths
        output_file (str): Path for the output PDF file
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        if not image_files:
            raise ValueError("لا توجد ملفات صور للتحويل")
        
        valid_images = [f for f in image_files if os.path.exists(f)]
        if not valid_images:
            raise ValueError("لا توجد ملفات صور صحيحة")
        
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        pdf_document = fitz.open()
        
        info(f"تحويل {len(valid_images)} صورة إلى PDF بالجودة الكاملة")
        
        for i, img_file in enumerate(valid_images):
            try:
                img_data = open(img_file, "rb").read()
                img = fitz.open("png", img_data) # Use fitz to handle images
                
                page_width = img[0].rect.width
                page_height = img[0].rect.height
                
                page = pdf_document.new_page(width=page_width, height=page_height)
                page.insert_image(page.rect, stream=img_data)
                
                img.close()
                
                if (i + 1) % 5 == 0:
                    info(f"تم معالجة {i + 1}/{len(valid_images)} صورة")
                    
            except Exception as e:
                warning(f"خطأ في معالجة الصورة {img_file}: {str(e)}")
                continue
        
        pdf_document.save(output_file)
        pdf_document.close()
        
        info(f"تم تحويل الصور بنجاح إلى: {output_file}")
        return True
        
    except Exception as e:
        error(f"خطأ في تحويل الصور إلى PDF: {str(e)}")
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
        
        pdf_document = fitz.open(input_file)
        total_pages = len(pdf_document)
        
        info(f"استخراج النص من {total_pages} صفحة")
        
        full_text = ""
        for page_num in range(total_pages):
            page = pdf_document[page_num]
            page_text = page.get_text("text")
            
            if page_text.strip():
                full_text += f"--- الصفحة {page_num + 1} ---\n"
                full_text += page_text + "\n\n"
            
            if (page_num + 1) % 10 == 0:
                info(f"تم معالجة {page_num + 1}/{total_pages} صفحة")
        
        pdf_document.close()
        
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_file, 'w', encoding=encoding) as text_file:
            text_file.write(full_text)
        
        info(f"تم استخراج النص بنجاح إلى: {output_file}")
        return True
        
    except Exception as e:
        error(f"خطأ في استخراج النص: {str(e)}")
        return False

def find_system_font(name: str) -> Optional[str]:
    """Find a font file on the system."""
    # For Windows
    if os.name == 'nt':
        font_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts")
        font_path = os.path.join(font_dir, name)
        if os.path.exists(font_path):
            return font_path
    # Add paths for other OS if needed
    return None

def text_to_pdf(input_file: str, output_file: str, 
               font_size: int = 12, encoding: str = "utf-8") -> bool:
    """
    Convert text file to PDF with full Arabic support.
    تحويل ملف نصي إلى PDF مع دعم كامل للغة العربية
    
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
        
        with open(input_file, 'r', encoding=encoding) as text_file:
            text_content = text_file.read()
        
        if not text_content.strip():
            raise ValueError("الملف النصي فارغ")
        
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        pdf_document = fitz.open()
        
        # Find a suitable Arabic font
        font_path = find_system_font("arial.ttf")
        if not font_path:
            warning("تحذير: لم يتم العثور على خط Arial. قد لا يتم عرض النص العربي بشكل صحيح.")
            font_name = "helv" # Fallback
        else:
            # Embed the font
            try:
                font_name = "Arial"
                pdf_document.insert_font(fontname=font_name, fontfile=font_path)
            except Exception as e:
                warning(f"خطأ في تضمين الخط: {e}. استخدام الخط الافتراضي.")
                font_name = "helv"

        page_width, page_height = 595, 842  # A4
        margin = 40
        line_height = font_size + 6
        
        lines = text_content.split('\n')
        info(f"تحويل النص إلى PDF ({len(lines)} سطر)")
        
        y_position = margin
        page = pdf_document.new_page(width=page_width, height=page_height)

        for line_text in lines:
            if y_position > page_height - margin:
                page = pdf_document.new_page(width=page_width, height=page_height)
                y_position = margin

            # Reshape and apply BiDi for Arabic text
            reshaped_text = arabic_reshaper.reshape(line_text)
            bidi_text = get_display(reshaped_text)
            
            # Calculate text width to handle alignment
            text_width = fitz.get_text_length(bidi_text, fontname=font_name, fontsize=font_size)
            
            # Position for RTL text
            x_position = page_width - margin - text_width
            
            page.insert_text((x_position, y_position), bidi_text, 
                           fontsize=font_size, fontname=font_name, color=(0, 0, 0))
            
            y_position += line_height
        
        pdf_document.save(output_file)
        pdf_document.close()
        
        info(f"تم تحويل النص بنجاح إلى: {output_file}")
        return True
        
    except Exception as e:
        error(f"خطأ في تحويل النص إلى PDF: {str(e)}")
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
        
        if file_ext == '.pdf':
            info["supported_conversions"] = [
                "PDF إلى صور (PNG, JPEG, TIFF)",
                "PDF إلى نص",
                "استخراج الصور من PDF"
            ]
            try:
                pdf_doc = fitz.open(input_file)
                info["page_count"] = len(pdf_doc)
                info["has_text"] = any(page.get_text().strip() for page in pdf_doc)
                info["has_images"] = any(page.get_images() for page in pdf_doc)
                pdf_doc.close()
            except: pass
                
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            info["supported_conversions"] = ["صورة إلى PDF", "تغيير تنسيق الصورة"]
            try:
                img = Image.open(input_file)
                info["image_size"] = img.size
                info["image_mode"] = img.mode
                img.close()
            except: pass
                
        elif file_ext == '.txt':
            info["supported_conversions"] = ["نص إلى PDF"]
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    info["line_count"] = len(content.split('\n'))
                    info["char_count"] = len(content)
            except: pass
        
        return info
        
    except Exception as e:
        return {"error": f"خطأ في قراءة الملف: {str(e)}"}

if __name__ == "__main__":
    info("وحدة التحويل تم تحميلها بنجاح")
