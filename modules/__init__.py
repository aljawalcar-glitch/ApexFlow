"""
PDF Tool Modules Package
حزمة وحدات أداة PDF
This package contains various PDF processing modules for the PDF Tool application.

تم تحسين هذا الملف لاستخدام التحميل الكسول (Lazy Loading) لتسريع بدء التطبيق.
الوحدات الثقيلة مثل PyMuPDF لن يتم تحميلها إلا عند الحاجة الفعلية.
"""

# لا نستورد أي وحدات ثقيلة هنا لضمان بدء تشغيل سريع
# سيتم تحميل الوحدات عند الحاجة من خلال OperationsManager

def __getattr__(name):
    """
    تحميل كسول للوحدات والدوال عند الطلب
    هذا يضمن عدم تحميل PyMuPDF والمكتبات الثقيلة إلا عند الحاجة
    """
    # وحدة الدمج
    if name in ['merge_pdfs', 'merge_pdfs_with_bookmarks', 'merge_specific_pages', 'get_pdf_info']:
        try:
            from .merge import merge_pdfs, merge_pdfs_with_bookmarks, merge_specific_pages, get_pdf_info
            globals().update({
                'merge_pdfs': merge_pdfs,
                'merge_pdfs_with_bookmarks': merge_pdfs_with_bookmarks,
                'merge_specific_pages': merge_specific_pages,
                'get_pdf_info': get_pdf_info
            })
            return globals()[name]
        except ImportError:
            pass

    # وحدة التقسيم
    elif name in ['split_pdf', 'split_pdf_by_ranges', 'split_pdf_by_size', 'extract_pages']:
        try:
            from .split import split_pdf, split_pdf_by_ranges, split_pdf_by_size, extract_pages
            globals().update({
                'split_pdf': split_pdf,
                'split_pdf_by_ranges': split_pdf_by_ranges,
                'split_pdf_by_size': split_pdf_by_size,
                'extract_pages': extract_pages
            })
            return globals()[name]
        except ImportError:
            pass

    # وحدة الضغط
    elif name in ['compress_pdf', 'batch_compress', 'get_compression_info']:
        try:
            from .compress import compress_pdf, batch_compress, get_compression_info
            globals().update({
                'compress_pdf': compress_pdf,
                'batch_compress': batch_compress,
                'get_compression_info': get_compression_info
            })
            return globals()[name]
        except ImportError:
            pass

    # وحدة التدوير
    elif name in ['rotate_pdf', 'rotate_specific_pages', 'auto_rotate_pages', 'get_page_orientations']:
        try:
            from .rotate import rotate_pdf, rotate_specific_pages, auto_rotate_pages, get_page_orientations
            globals().update({
                'rotate_pdf': rotate_pdf,
                'rotate_specific_pages': rotate_specific_pages,
                'auto_rotate_pages': auto_rotate_pages,
                'get_page_orientations': get_page_orientations
            })
            return globals()[name]
        except ImportError:
            pass

    # وحدة التحويل
    elif name in ['pdf_to_images', 'images_to_pdf', 'pdf_to_text', 'text_to_pdf', 'get_conversion_info']:
        try:
            from .convert import pdf_to_images, images_to_pdf, pdf_to_text, text_to_pdf, get_conversion_info
            globals().update({
                'pdf_to_images': pdf_to_images,
                'images_to_pdf': images_to_pdf,
                'pdf_to_text': pdf_to_text,
                'text_to_pdf': text_to_pdf,
                'get_conversion_info': get_conversion_info
            })
            return globals()[name]
        except ImportError:
            pass

    # وحدة الإعدادات (خفيفة، يمكن تحميلها مباشرة)
    elif name in ['load_settings', 'save_settings', 'get_setting', 'set_setting',
                  'add_recent_file', 'get_recent_files', 'reset_settings']:
        try:
            from .settings import (load_settings, save_settings, get_setting, set_setting,
                                  add_recent_file, get_recent_files, reset_settings)
            globals().update({
                'load_settings': load_settings,
                'save_settings': save_settings,
                'get_setting': get_setting,
                'set_setting': set_setting,
                'add_recent_file': add_recent_file,
                'get_recent_files': get_recent_files,
                'reset_settings': reset_settings
            })
            return globals()[name]
        except ImportError:
            pass

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__version__ = "v5.3.0"
__author__ = "ApexFlow Team"
__description__ = "PDF processing modules for ApexFlow application"

# قائمة بجميع الوحدات المتاحة
__all__ = [
    # Merge functions
    'merge_pdfs', 'merge_pdfs_with_bookmarks', 'merge_specific_pages', 'get_pdf_info',

    # Split functions
    'split_pdf', 'split_pdf_by_ranges', 'split_pdf_by_size', 'extract_pages',

    # Compress functions
    'compress_pdf', 'batch_compress', 'get_compression_info',

    # Rotate functions
    'rotate_pdf', 'rotate_specific_pages', 'auto_rotate_pages', 'get_page_orientations',

    # Convert functions
    'pdf_to_images', 'images_to_pdf', 'pdf_to_text', 'text_to_pdf', 'get_conversion_info',

    # Settings functions
    'load_settings', 'save_settings', 'get_setting', 'set_setting',
    'add_recent_file', 'get_recent_files', 'reset_settings'
]
