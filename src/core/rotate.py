"""
PDF Rotation Module
وحدة تدوير ملفات PDF
This module provides functionality to rotate PDF pages.
"""

import os
from pypdf import PdfReader, PdfWriter
from typing import List, Optional, Union
from src.utils.logger import info, warning, error

def rotate_pdf(input_file: str, output_file: str, rotation_angle: int = 90) -> bool:
    """
    Rotate all pages of a PDF file.
    تدوير جميع صفحات ملف PDF
    
    Args:
        input_file (str): Path to the input PDF file
        output_file (str): Path for the rotated output PDF file
        rotation_angle (int): Rotation angle in degrees (90, 180, 270, or -90, -180, -270)
        
    Returns:
        bool: True if rotation was successful, False otherwise
    """
    try:
        # التحقق من وجود الملف المدخل
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        if not input_file.lower().endswith('.pdf'):
            raise ValueError(f"الملف ليس PDF: {input_file}")
        
        # التحقق من زاوية التدوير
        valid_angles = [90, 180, 270, -90, -180, -270]
        if rotation_angle not in valid_angles:
            warning(f"تحذير: زاوية تدوير غير صحيحة {rotation_angle}. سيتم استخدام 90 درجة.")
            rotation_angle = 90
        
        # قراءة ملف PDF
        pdf_reader = PdfReader(input_file)
        pdf_writer = PdfWriter()
        
        total_pages = len(pdf_reader.pages)
        info(f"تدوير {total_pages} صفحة بزاوية {rotation_angle} درجة")
        
        # تدوير كل صفحة
        for page_num, page in enumerate(pdf_reader.pages):
            rotated_page = page.rotate(rotation_angle)
            pdf_writer.add_page(rotated_page)
            
            if (page_num + 1) % 10 == 0:
                info(f"تم تدوير {page_num + 1}/{total_pages} صفحة")
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # حفظ الملف المدور
        with open(output_file, 'wb') as output:
            pdf_writer.write(output)
        
        info(f"تم تدوير الملف بنجاح: {os.path.basename(output_file)}")
        return True
        
    except Exception as e:
        error(f"خطأ في تدوير PDF: {str(e)}")
        return False

def rotate_specific_pages(input_file: str, output_file: str, 
                         page_rotations: List[tuple]) -> bool:
    """
    Rotate specific pages with different angles.
    تدوير صفحات محددة بزوايا مختلفة
    
    Args:
        input_file (str): Path to the input PDF file
        output_file (str): Path for the output PDF file
        page_rotations (List[tuple]): List of (page_number, rotation_angle) tuples (1-based)
        
    Returns:
        bool: True if rotation was successful, False otherwise
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        pdf_reader = PdfReader(input_file)
        pdf_writer = PdfWriter()
        total_pages = len(pdf_reader.pages)
        
        # إنشاء قاموس للتدويرات
        rotation_dict = {}
        for page_num, angle in page_rotations:
            if 1 <= page_num <= total_pages:
                rotation_dict[page_num - 1] = angle  # تحويل إلى فهرسة تبدأ من 0
            else:
                warning(f"تحذير: رقم صفحة غير صحيح: {page_num}")
        
        info(f"تدوير صفحات محددة من أصل {total_pages} صفحة")
        
        # معالجة كل صفحة
        for page_num, page in enumerate(pdf_reader.pages):
            if page_num in rotation_dict:
                angle = rotation_dict[page_num]
                rotated_page = page.rotate(angle)
                pdf_writer.add_page(rotated_page)
                info(f"تم تدوير الصفحة {page_num + 1} بزاوية {angle} درجة")
            else:
                # إضافة الصفحة بدون تدوير
                pdf_writer.add_page(page)
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # حفظ الملف
        with open(output_file, 'wb') as output:
            pdf_writer.write(output)
        
        info(f"تم تدوير الصفحات المحددة بنجاح: {os.path.basename(output_file)}")
        return True
        
    except Exception as e:
        error(f"خطأ في تدوير الصفحات المحددة: {str(e)}")
        return False

def rotate_page_range(input_file: str, output_file: str, 
                     start_page: int, end_page: int, rotation_angle: int = 90) -> bool:
    """
    Rotate a range of pages in a PDF file.
    تدوير نطاق من الصفحات في ملف PDF
    
    Args:
        input_file (str): Path to the input PDF file
        output_file (str): Path for the output PDF file
        start_page (int): Starting page number (1-based)
        end_page (int): Ending page number (1-based)
        rotation_angle (int): Rotation angle in degrees
        
    Returns:
        bool: True if rotation was successful, False otherwise
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        pdf_reader = PdfReader(input_file)
        pdf_writer = PdfWriter()
        total_pages = len(pdf_reader.pages)
        
        # التحقق من صحة النطاق
        start_idx = max(0, start_page - 1)  # تحويل إلى فهرسة تبدأ من 0
        end_idx = min(total_pages - 1, end_page - 1)
        
        if start_idx > end_idx:
            raise ValueError(f"نطاق صفحات غير صحيح: {start_page}-{end_page}")
        
        info(f"تدوير الصفحات {start_page}-{end_page} بزاوية {rotation_angle} درجة")
        
        # معالجة كل صفحة
        for page_num, page in enumerate(pdf_reader.pages):
            if start_idx <= page_num <= end_idx:
                # تدوير الصفحات في النطاق المحدد
                rotated_page = page.rotate(rotation_angle)
                pdf_writer.add_page(rotated_page)
            else:
                # إضافة الصفحات الأخرى بدون تدوير
                pdf_writer.add_page(page)
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # حفظ الملف
        with open(output_file, 'wb') as output:
            pdf_writer.write(output)
        
        pages_rotated = end_idx - start_idx + 1
        info(f"تم تدوير {pages_rotated} صفحة بنجاح: {os.path.basename(output_file)}")
        return True
        
    except Exception as e:
        error(f"خطأ في تدوير نطاق الصفحات: {str(e)}")
        return False

def auto_rotate_pages(input_file: str, output_file: str) -> bool:
    """
    Automatically rotate pages to portrait orientation.
    تدوير الصفحات تلقائياً إلى الوضع العمودي
    
    Args:
        input_file (str): Path to the input PDF file
        output_file (str): Path for the output PDF file
        
    Returns:
        bool: True if rotation was successful, False otherwise
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        pdf_reader = PdfReader(input_file)
        pdf_writer = PdfWriter()
        
        rotated_count = 0
        total_pages = len(pdf_reader.pages)
        
        info(f"فحص وتدوير الصفحات تلقائياً لـ {total_pages} صفحة")
        
        for page_num, page in enumerate(pdf_reader.pages):
            # الحصول على أبعاد الصفحة
            media_box = page.mediabox
            width = float(media_box.width)
            height = float(media_box.height)
            
            # تحديد ما إذا كانت الصفحة في وضع أفقي
            if width > height:
                # تدوير الصفحة 90 درجة لجعلها عمودية
                rotated_page = page.rotate(90)
                pdf_writer.add_page(rotated_page)
                rotated_count += 1
                info(f"تم تدوير الصفحة {page_num + 1} (أفقية → عمودية)")
            else:
                # الصفحة عمودية بالفعل
                pdf_writer.add_page(page)
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # حفظ الملف
        with open(output_file, 'wb') as output:
            pdf_writer.write(output)
        
        info(f"تم التدوير التلقائي بنجاح: {rotated_count} صفحة من أصل {total_pages}")
        return True
        
    except Exception as e:
        error(f"خطأ في التدوير التلقائي: {str(e)}")
        return False

def get_page_orientations(input_file: str) -> List[dict]:
    """
    Get orientation information for all pages.
    الحصول على معلومات اتجاه جميع الصفحات
    
    Args:
        input_file (str): Path to the PDF file
        
    Returns:
        List of dictionaries containing page orientation info
    """
    try:
        if not os.path.exists(input_file):
            return []
        
        pdf_reader = PdfReader(input_file)
        orientations = []
        
        for page_num, page in enumerate(pdf_reader.pages):
            media_box = page.mediabox
            width = float(media_box.width)
            height = float(media_box.height)
            
            orientation = "عمودي" if height >= width else "أفقي"
            rotation = page.get('/Rotate', 0)
            
            page_info = {
                'page_number': page_num + 1,
                'width': width,
                'height': height,
                'orientation': orientation,
                'current_rotation': rotation,
                'aspect_ratio': width / height if height > 0 else 0
            }
            orientations.append(page_info)
        
        return orientations
        
    except Exception as e:
        error(f"خطأ في قراءة اتجاهات الصفحات: {str(e)}")
        return []

def batch_rotate(input_folder: str, output_folder: str, rotation_angle: int = 90) -> dict:
    """
    Rotate multiple PDF files in a folder.
    تدوير عدة ملفات PDF في مجلد
    
    Args:
        input_folder (str): Path to folder containing PDF files
        output_folder (str): Path to folder for rotated files
        rotation_angle (int): Rotation angle in degrees
        
    Returns:
        Dictionary containing rotation results
    """
    results = {
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'files': []
    }
    
    try:
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"المجلد غير موجود: {input_folder}")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # البحث عن ملفات PDF
        pdf_files = [f for f in os.listdir(input_folder) 
                    if f.lower().endswith('.pdf')]
        
        info(f"تدوير {len(pdf_files)} ملف PDF بزاوية {rotation_angle} درجة")
        
        for filename in pdf_files:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"rotated_{filename}")
            
            results['processed'] += 1
            info(f"معالجة: {filename}")
            
            if rotate_pdf(input_path, output_path, rotation_angle):
                results['successful'] += 1
                results['files'].append({
                    'filename': filename,
                    'status': 'نجح',
                    'rotation_angle': rotation_angle
                })
            else:
                results['failed'] += 1
                results['files'].append({
                    'filename': filename,
                    'status': 'فشل',
                    'rotation_angle': rotation_angle
                })
        
        info(f"\nالنتائج: {results['successful']} نجح، {results['failed']} فشل")
        return results
        
    except Exception as e:
        error(f"خطأ في التدوير المجمع: {str(e)}")
        return results

# مثال على الاستخدام
if __name__ == "__main__":
    # أمثلة على الاستخدام
    input_pdf = "sample.pdf"
    output_pdf = "rotated_sample.pdf"
    
    # تدوير جميع الصفحات
    # rotate_pdf(input_pdf, output_pdf, rotation_angle=90)
    
    # تدوير صفحات محددة
    # page_rotations = [(1, 90), (3, 180), (5, 270)]
    # rotate_specific_pages(input_pdf, output_pdf, page_rotations)
    
    # تدوير نطاق من الصفحات
    # rotate_page_range(input_pdf, output_pdf, start_page=1, end_page=5, rotation_angle=90)
    
    # التدوير التلقائي
    # auto_rotate_pages(input_pdf, output_pdf)
    
    # معلومات اتجاه الصفحات
    # orientations = get_page_orientations(input_pdf)
    # for info in orientations:
    #     info(f"الصفحة {info['page_number']}: {info['orientation']}")
    
    info("وحدة التدوير تم تحميلها بنجاح")
