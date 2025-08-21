"""
Core PDF Processing Module
الوحدة الأساسية لمعالجة ملفات PDF
"""

from .merge import merge_pdfs, merge_pdfs_with_bookmarks, merge_specific_pages, get_pdf_info
from .split import split_pdf, split_pdf_by_ranges, split_pdf_by_size, extract_pages
from .compress import compress_pdf, batch_compress
from .convert import pdf_to_images
from .rotate import rotate_pdf, rotate_specific_pages
from .security import encrypt_pdf, decrypt_pdf
from .pdf_worker import PDFLoadWorker

__all__ = [
    # Merge functions
    'merge_pdfs', 'merge_pdfs_with_bookmarks', 'merge_specific_pages', 'get_pdf_info',

    # Split functions
    'split_pdf', 'split_pdf_by_ranges', 'split_pdf_by_size', 'extract_pages',

    # Compress functions
    'compress_pdf', 'batch_compress',

    # Convert functions
    'pdf_to_images',

    # Rotate functions
    'rotate_pdf', 'rotate_specific_pages',

    # Security functions
    'encrypt_pdf', 'decrypt_pdf',

    # PDF Worker
    'PDFLoadWorker'
]
