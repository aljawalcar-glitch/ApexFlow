"""
PDF Merge Module
This module provides functionality to merge multiple PDF files into a single PDF file.
"""

import os
from typing import List, Optional

from modules.logger import error, info, warning

# تحميل كسول للمكتبات الثقيلة
_pdf_reader = None
_pdf_writer = None

def _get_pdf_classes():
    """تحميل كسول لمكتبات pypdf مع معالجة أفضل للأخطاء"""
    global _pdf_reader, _pdf_writer
    if _pdf_reader is None or _pdf_writer is None:
        try:
            from pypdf import PdfReader, PdfWriter
            _pdf_reader = PdfReader
            _pdf_writer = PdfWriter
            info("تم تحميل مكتبة pypdf بنجاح")
        except ImportError as e:
            error_msg = f"مكتبة pypdf غير مثبتة. يرجى تثبيتها باستخدام الأمر: pip install pypdf==5.0.0"
            error(error_msg)
            raise ImportError(error_msg) from e
        except Exception as e:
            error_msg = f"حدث خطأ أثناء تحميل مكتبة pypdf: {str(e)}"
            error(error_msg)
            raise ImportError(error_msg) from e
    return _pdf_reader, _pdf_writer

def merge_pdfs(input_files: List[str], output_path: str) -> bool:
    """
    Merge multiple PDF files into a single PDF file.
    
    Args:
        input_files (List[str]): List of paths to PDF files to be merged
        output_path (str): Path where the merged PDF will be saved
        
    Returns:
        bool: True if merge was successful, False otherwise
        
    Raises:
        FileNotFoundError: If any input file doesn't exist
        Exception: For other PDF processing errors
    """
    try:
        # Validate input files
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"لم يتم العثور على الملف: {file_path}")
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"الملف ليس من نوع PDF: {file_path}")
        
        # تحميل كسول للمكتبات
        PdfReader, PdfWriter = _get_pdf_classes()
        
        # Create PDF writer object
        pdf_writer = PdfWriter()

        # Process each input file
        for file_path in input_files:
            try:
                pdf_reader = PdfReader(file_path)
                
                # Add all pages from current PDF to the writer
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)
                    
            except Exception as e:
                warning(f"خطأ في معالجة الملف {file_path}: {str(e)}")
                continue
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Check if any pages were added before writing
        if len(pdf_writer.pages) == 0:
            error("خطأ: لم تتم إضافة أي صفحات إلى الملف المدمج. قد تكون جميع ملفات الإدخال غير صالحة.")
            return False

        # Write merged PDF to output file
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        info(f"تم دمج {len(input_files)} ملف بنجاح في {output_path}")
        return True
        
    except Exception as e:
        error(f"خطأ في دمج ملفات PDF: {str(e)}")
        return False

def merge_pdfs_with_bookmarks(input_files: List[str], output_path: str, 
                             bookmark_names: Optional[List[str]] = None) -> bool:
    """
    Merge multiple PDF files with bookmarks for each original file.
    
    Args:
        input_files (List[str]): List of paths to PDF files to be merged
        output_path (str): Path where the merged PDF will be saved
        bookmark_names (Optional[List[str]]): Custom names for bookmarks. 
                                            If None, uses filenames.
        
    Returns:
        bool: True if merge was successful, False otherwise
    """
    try:
        # Validate input files
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"لم يتم العثور على الملف: {file_path}")
        
        PdfReader, PdfWriter = _get_pdf_classes()
        
        # Create PDF writer object
        pdf_writer = PdfWriter()
        
        # Generate bookmark names if not provided
        if bookmark_names is None:
            bookmark_names = [os.path.splitext(os.path.basename(f))[0] 
                            for f in input_files]
        
        # Process each input file
        current_page = 0
        for i, file_path in enumerate(input_files):
            try:
                pdf_reader = PdfReader(file_path)
                
                # Add bookmark for this file
                if i < len(bookmark_names):
                    pdf_writer.add_outline_item(bookmark_names[i], current_page)
                
                # Add all pages from current PDF to the writer
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)
                    current_page += 1
                    
            except Exception as e:
                warning(f"خطأ في معالجة الملف {file_path}: {str(e)}")
                continue
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Write merged PDF to output file
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        info(f"تم دمج {len(input_files)} ملفات مع الإشارات المرجعية بنجاح في {output_path}")
        return True
        
    except Exception as e:
        error(f"خطأ في دمج ملفات PDF مع الإشارات المرجعية: {str(e)}")
        return False

def merge_specific_pages(file_page_ranges: List[tuple], output_path: str) -> bool:
    """
    Merge specific pages from multiple PDF files.
    
    Args:
        file_page_ranges (List[tuple]): List of tuples containing 
                                       (file_path, start_page, end_page)
                                       Page numbers are 0-based
        output_path (str): Path where the merged PDF will be saved
        
    Returns:
        bool: True if merge was successful, False otherwise
    """
    try:
        PdfReader, PdfWriter = _get_pdf_classes()
        pdf_writer = PdfWriter()
        
        for file_path, start_page, end_page in file_page_ranges:
            if not os.path.exists(file_path):
                warning(f"تحذير: لم يتم العثور على الملف: {file_path}")
                continue
                
            try:
                pdf_reader = PdfReader(file_path)
                total_pages = len(pdf_reader.pages)
                
                # Validate page ranges
                start_page = max(0, min(start_page, total_pages - 1))
                end_page = max(start_page, min(end_page, total_pages - 1))
                
                # Add specified pages
                for page_num in range(start_page, end_page + 1):
                    if page_num < total_pages:
                        page = pdf_reader.pages[page_num]
                        pdf_writer.add_page(page)
                        
            except Exception as e:
                warning(f"خطأ في معالجة الملف {file_path}: {str(e)}")
                continue
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Write merged PDF to output file
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        info(f"تم دمج صفحات محددة بنجاح في {output_path}")
        return True
        
    except Exception as e:
        error(f"خطأ في دمج صفحات محددة: {str(e)}")
        return False

def get_pdf_info(file_path: str) -> dict:
    """
    Get basic information about a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing PDF information
    """
    try:
        if not os.path.exists(file_path):
            return {"error": "لم يتم العثور على الملف"}
        
        PdfReader, _ = _get_pdf_classes()
        pdf_reader = PdfReader(file_path)
        
        info = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "page_count": len(pdf_reader.pages),
            "encrypted": pdf_reader.is_encrypted,
        }
        
        # Try to get metadata
        if pdf_reader.metadata:
            info["title"] = pdf_reader.metadata.get("/Title", "")
            info["author"] = pdf_reader.metadata.get("/Author", "")
            info["subject"] = pdf_reader.metadata.get("/Subject", "")
            info["creator"] = pdf_reader.metadata.get("/Creator", "")
        
        return info
        
    except Exception as e:
        return {"error": f"خطأ في قراءة ملف PDF: {str(e)}"}

# Example usage and testing functions
if __name__ == "__main__":
    # Example usage
    sample_files = ["file1.pdf", "file2.pdf", "file3.pdf"]
    output_file = "merged_output.pdf"
    
    # Basic merge
    # result = merge_pdfs(sample_files, output_file)
    
    # Merge with bookmarks
    # result = merge_pdfs_with_bookmarks(sample_files, output_file, 
    #                                   ["Chapter 1", "Chapter 2", "Chapter 3"])
    
    # Merge specific pages
    # page_ranges = [("file1.pdf", 0, 2), ("file2.pdf", 1, 3), ("file3.pdf", 0, 1)]
    # result = merge_specific_pages(page_ranges, output_file)
    
    info("تم تحميل وحدة الدمج بنجاح")
