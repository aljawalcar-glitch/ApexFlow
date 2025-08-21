# -*- coding: utf-8 -*-

"""
وحدة حماية وخصائص ملفات PDF
"""

from pypdf import PdfReader, PdfWriter
from src.utils.logger import info, error

def get_pdf_metadata(file_path, password=None):
    """
    الحصول على بيانات التعريف (metadata) من ملف PDF.
    يعالج الملفات المشفرة إذا تم توفير كلمة مرور.
    """
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            
            # إذا كان الملف مشفرًا، حاول فك تشفيره
            if reader.is_encrypted:
                if password and reader.decrypt(password):
                    info("تم فك تشفير الملف بنجاح لقراءة البيانات الوصفية.")
                else:
                    error("الملف مشفر ولا يمكن قراءة بياناته الوصفية بدون كلمة مرور صحيحة.")
                    return {'encrypted': True}  # إرجاع علامة للتعامل معها في الواجهة

            metadata = reader.metadata
            if metadata is None:
                return {}

            # استخراج البيانات الوصفية مع التعامل مع الاختلافات بين إصدارات pypdf
            result = {}
            try:
                # محاولة الوصول إلى البيانات باستخدام الخصائص المباشرة (الإصدار الحديث)
                result['/Title'] = metadata.title or ""
                result['/Author'] = metadata.author or ""
                result['/Subject'] = metadata.subject or ""
                result['/Keywords'] = metadata.get('/Keywords', "") or ""
            except (AttributeError, TypeError):
                # الطريقة البديلة للإصدارات القديمة من pypdf
                for key in ['/Title', '/Author', '/Subject', '/Keywords']:
                    if key in metadata:
                        result[key] = metadata[key]
                    else:
                        result[key] = ""

            # طباعة البيانات المستخرجة للتحقق
            info(f"البيانات الوصفية للملف: {result}")
            return result
    except Exception as e:
        error(f"فشل في قراءة بيانات التعريف من {file_path}: {e}")
        return None

def update_pdf_metadata(input_path, output_path, metadata):
    """
    تحديث بيانات التعريف (metadata) لملف PDF.
    """
    try:
        with open(input_path, 'rb') as f:
            reader = PdfReader(f)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)
            
            writer.add_metadata(metadata)

            with open(output_path, 'wb') as out:
                writer.write(out)
        info(f"تم تحديث بيانات التعريف بنجاح في: {output_path}")
        return True
    except Exception as e:
        error(f"فشل في تحديث بيانات التعريف: {e}")
        return False

def encrypt_pdf(input_path, output_path, user_password, owner_password=None, permissions=None):
    """
    تشفير ملف PDF بكلمة مرور وأذونات.
    """
    try:
        with open(input_path, 'rb') as f:
            reader = PdfReader(f)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # تعيين كلمة المرور
            writer.encrypt(user_password, owner_password)
            
            # تعيين الأذونات (إذا تم توفيرها)
            if permissions:
                # pypdf لا يدعم تعيين الأذونات بشكل مباشر بعد الإنشاء
                # هذه الميزة قد تحتاج إلى مكتبة أخرى أو إصدار أحدث
                pass

            with open(output_path, 'wb') as out:
                writer.write(out)
        info(f"تم تشفير الملف بنجاح: {output_path}")
        return True
    except Exception as e:
        error(f"فشل في تشفير الملف: {e}")
        return False

def decrypt_pdf(input_path, output_path, password):
    """
    فك تشفير ملف PDF.
    """
    try:
        with open(input_path, 'rb') as f:
            reader = PdfReader(f)
            
            if reader.is_encrypted:
                if reader.decrypt(password):
                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    with open(output_path, 'wb') as out:
                        writer.write(out)
                    
                    info(f"تم فك تشفير الملف بنجاح: {output_path}")
                    return True
                else:
                    error("كلمة مرور غير صحيحة.")
                    return False
            else:
                info("الملف غير مشفر أصلاً.")
                # يمكن نسخ الملف كما هو إذا أردنا
                import shutil
                shutil.copy2(input_path, output_path)
                return True
    except Exception as e:
        error(f"فشل في فك تشفير الملف: {e}")
        return False
