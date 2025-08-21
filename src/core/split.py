"""
PDF Split Module
وحدة تقسيم ملفات PDF
This module provides functionality to split PDF files into separate pages or ranges.
"""

import os
from pypdf import PdfReader, PdfWriter
from typing import List, Optional, Tuple
from src.utils.logger import info, warning, error

def split_pdf(input_file: str, output_folder: str, prefix: str = "page") -> bool:
    """
    Split a PDF file into individual pages.
    تقسيم ملف PDF إلى صفحات منفردة
    
    Args:
        input_file (str): Path to the input PDF file
        output_folder (str): Folder where split pages will be saved
        prefix (str): Prefix for output filenames (default: "page")
        
    Returns:
        bool: True if split was successful, False otherwise
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
        
        # قراءة ملف PDF
        pdf_reader = PdfReader(input_file)
        total_pages = len(pdf_reader.pages)
        
        info(f"تقسيم {total_pages} صفحة من الملف: {os.path.basename(input_file)}")
        
        # تقسيم كل صفحة إلى ملف منفصل
        for page_num in range(total_pages):
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[page_num])
            
            # تحديد اسم الملف المخرج
            output_filename = f"{prefix}_{page_num + 1:03d}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            # كتابة الصفحة إلى ملف منفصل
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
        
        info(f"تم تقسيم الملف بنجاح إلى {total_pages} صفحة في المجلد: {output_folder}")
        return True
        
    except Exception as e:
        error(f"خطأ في تقسيم PDF: {str(e)}")
        return False

def split_pdf_by_ranges(input_file: str, output_folder: str, 
                       page_ranges: List[Tuple[int, int]], 
                       filenames: Optional[List[str]] = None) -> bool:
    """
    Split a PDF file into multiple files based on page ranges.
    تقسيم ملف PDF إلى ملفات متعددة حسب نطاقات الصفحات
    
    Args:
        input_file (str): Path to the input PDF file
        output_folder (str): Folder where split files will be saved
        page_ranges (List[Tuple[int, int]]): List of (start_page, end_page) tuples (1-based)
        filenames (Optional[List[str]]): Custom filenames for each range
        
    Returns:
        bool: True if split was successful, False otherwise
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        pdf_reader = PdfReader(input_file)
        total_pages = len(pdf_reader.pages)
        
        # إنشاء أسماء ملفات افتراضية إذا لم تُحدد
        if filenames is None:
            filenames = [f"part_{i+1}.pdf" for i in range(len(page_ranges))]
        
        for i, (start_page, end_page) in enumerate(page_ranges):
            # تحويل إلى فهرسة تبدأ من 0
            start_idx = max(0, start_page - 1)
            end_idx = min(total_pages - 1, end_page - 1)
            
            if start_idx > end_idx or start_idx >= total_pages:
                warning(f"تحذير: نطاق صفحات غير صحيح: {start_page}-{end_page}")
                continue
            
            pdf_writer = PdfWriter()
            
            # إضافة الصفحات في النطاق المحدد
            for page_idx in range(start_idx, end_idx + 1):
                pdf_writer.add_page(pdf_reader.pages[page_idx])
            
            # تحديد اسم الملف المخرج
            if i < len(filenames):
                output_filename = filenames[i]
            else:
                output_filename = f"part_{i+1}.pdf"
            
            output_path = os.path.join(output_folder, output_filename)
            
            # كتابة النطاق إلى ملف
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            info(f"تم إنشاء: {output_filename} (صفحات {start_page}-{end_page})")
        
        info(f"تم تقسيم الملف بنجاح إلى {len(page_ranges)} جزء")
        return True
        
    except Exception as e:
        error(f"خطأ في تقسيم PDF بالنطاقات: {str(e)}")
        return False

def split_pdf_by_size(input_file: str, output_folder: str, 
                     pages_per_file: int, prefix: str = "part") -> bool:
    """
    Split a PDF file into multiple files with specified number of pages each.
    تقسيم ملف PDF إلى ملفات متعددة بعدد صفحات محدد لكل ملف
    
    Args:
        input_file (str): Path to the input PDF file
        output_folder (str): Folder where split files will be saved
        pages_per_file (int): Number of pages per output file
        prefix (str): Prefix for output filenames
        
    Returns:
        bool: True if split was successful, False otherwise
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        if pages_per_file <= 0:
            raise ValueError("عدد الصفحات لكل ملف يجب أن يكون أكبر من صفر")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        pdf_reader = PdfReader(input_file)
        total_pages = len(pdf_reader.pages)
        
        file_count = 0
        current_page = 0
        
        while current_page < total_pages:
            pdf_writer = PdfWriter()
            
            # إضافة الصفحات للملف الحالي
            pages_added = 0
            while pages_added < pages_per_file and current_page < total_pages:
                pdf_writer.add_page(pdf_reader.pages[current_page])
                current_page += 1
                pages_added += 1
            
            # حفظ الملف
            file_count += 1
            output_filename = f"{prefix}_{file_count:03d}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            info(f"تم إنشاء: {output_filename} ({pages_added} صفحة)")
        
        info(f"تم تقسيم الملف بنجاح إلى {file_count} ملف")
        return True
        
    except Exception as e:
        error(f"خطأ في تقسيم PDF بالحجم: {str(e)}")
        return False

def extract_pages(input_file: str, output_file: str, page_numbers: List[int]) -> bool:
    """
    Extract specific pages from a PDF file.
    استخراج صفحات محددة من ملف PDF
    
    Args:
        input_file (str): Path to the input PDF file
        output_file (str): Path for the output PDF file
        page_numbers (List[int]): List of page numbers to extract (1-based)
        
    Returns:
        bool: True if extraction was successful, False otherwise
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")
        
        pdf_reader = PdfReader(input_file)
        total_pages = len(pdf_reader.pages)
        pdf_writer = PdfWriter()
        
        # التحقق من صحة أرقام الصفحات واستخراجها
        extracted_count = 0
        for page_num in page_numbers:
            if 1 <= page_num <= total_pages:
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])  # تحويل إلى فهرسة تبدأ من 0
                extracted_count += 1
            else:
                warning(f"تحذير: رقم صفحة غير صحيح: {page_num}")
        
        if extracted_count == 0:
            warning("لم يتم استخراج أي صفحة")
            return False
        
        # إنشاء مجلد الحفظ إذا لم يكن موجوداً
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # حفظ الصفحات المستخرجة
        with open(output_file, 'wb') as output:
            pdf_writer.write(output)
        
        info(f"تم استخراج {extracted_count} صفحة إلى: {output_file}")
        return True
        
    except Exception as e:
        error(f"خطأ في استخراج الصفحات: {str(e)}")
        return False

def get_pdf_page_count(input_file: str) -> int:
    """
    Get the number of pages in a PDF file.
    الحصول على عدد الصفحات في ملف PDF
    
    Args:
        input_file (str): Path to the PDF file
        
    Returns:
        int: Number of pages, or -1 if error
    """
    try:
        if not os.path.exists(input_file):
            return -1
        
        pdf_reader = PdfReader(input_file)
        return len(pdf_reader.pages)
        
    except Exception as e:
        error(f"خطأ في قراءة عدد الصفحات: {str(e)}")
        return -1

# مثال على الاستخدام
if __name__ == "__main__":
    # أمثلة على الاستخدام
    input_pdf = "sample.pdf"
    output_dir = "split_output"
    
    # تقسيم إلى صفحات منفردة
    # split_pdf(input_pdf, output_dir)
    
    # تقسيم بنطاقات محددة
    # ranges = [(1, 5), (6, 10), (11, 15)]
    # split_pdf_by_ranges(input_pdf, output_dir, ranges)
    
    # تقسيم بحجم محدد (3 صفحات لكل ملف)
    # split_pdf_by_size(input_pdf, output_dir, 3)
    
    # استخراج صفحات محددة
    # extract_pages(input_pdf, "extracted.pdf", [1, 3, 5, 7])
    
    info("وحدة التقسيم تم تحميلها بنجاح")

def split_pdf_advanced(input_file: str, output_folder: str, prefix: str = "page",
                      pages_per_file: int = 1, create_subfolders: bool = False) -> bool:
    """
    تقسيم ملف PDF بخيارات متقدمة

    Args:
        input_file (str): مسار ملف PDF المراد تقسيمه
        output_folder (str): مجلد الحفظ
        prefix (str): بادئة أسماء الملفات
        pages_per_file (int): عدد الصفحات في كل ملف
        create_subfolders (bool): إنشاء مجلدات فرعية

    Returns:
        bool: True إذا نجح التقسيم، False في حالة الفشل
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"الملف غير موجود: {input_file}")

        pdf_reader = PdfReader(input_file)
        total_pages = len(pdf_reader.pages)

        if total_pages == 0:
            warning("الملف لا يحتوي على صفحات")
            return False

        # إنشاء مجلد الحفظ
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # تحديد مجلد الحفظ النهائي
        if create_subfolders:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            final_output_folder = os.path.join(output_folder, f"{base_name}_split")
            os.makedirs(final_output_folder, exist_ok=True)
        else:
            final_output_folder = output_folder

        # تقسيم الصفحات
        file_count = 0
        for start_page in range(0, total_pages, pages_per_file):
            end_page = min(start_page + pages_per_file, total_pages)

            # إنشاء كاتب PDF جديد
            pdf_writer = PdfWriter()

            # إضافة الصفحات للملف الحالي
            for page_num in range(start_page, end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            # تحديد اسم الملف
            if pages_per_file == 1:
                filename = f"{prefix}_{start_page + 1}.pdf"
            else:
                filename = f"{prefix}_{start_page + 1}_to_{end_page}.pdf"

            output_path = os.path.join(final_output_folder, filename)

            # حفظ الملف
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            file_count += 1
            info(f"تم إنشاء: {filename}")

        info(f"تم تقسيم الملف بنجاح إلى {file_count} ملف في: {final_output_folder}")
        return True

    except Exception as e:
        error(f"خطأ في تقسيم الملف: {str(e)}")
        return False
