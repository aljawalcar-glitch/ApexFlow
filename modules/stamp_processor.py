# -*- coding: utf-8 -*-
"""
معالج الأختام - دمج الأختام مع ملفات PDF
Stamp Processor - Merge stamps with PDF files
"""

import fitz  # PyMuPDF
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt
import tempfile
import os
from .coordinate_calibrator import CoordinateCalibrator, validate_coordinates

def save_pdf_with_stamps(input_path, output_path, page_rotations, page_stamps, view_scale_factor=1.0):
    """
    حفظ ملف PDF مع التدوير والأختام مع تحسينات دقة الحفظ

    Args:
        input_path (str): مسار الملف الأصلي
        output_path (str): مسار الملف المحفوظ
        page_rotations (dict): قاموس التدوير {page_num: angle}
        page_stamps (dict): قاموس الأختام {page_num: [stamp_objects]}
        view_scale_factor (float): عامل تحجيم العرض لتصحيح الإحداثيات

    Returns:
        bool: True إذا نجحت العملية
    """
    try:
        print(f"بدء حفظ PDF مع الأختام:")
        print(f"  - الملف المصدر: {input_path}")
        print(f"  - الملف الهدف: {output_path}")
        print(f"  - عامل تحجيم العرض: {view_scale_factor}")

        # فتح المستند الأصلي
        doc = fitz.open(input_path)

        # معالجة كل صفحة
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_rect = page.rect

            print(f"\nمعالجة الصفحة {page_num + 1}:")
            print(f"  - أبعاد الصفحة: {page_rect.width:.1f} x {page_rect.height:.1f}")

            # تطبيق التدوير إذا كان موجوداً
            if page_num in page_rotations and page_rotations[page_num] != 0:
                rotation_angle = page_rotations[page_num]
                page.set_rotation(rotation_angle)
                print(f"  - تم تطبيق التدوير: {rotation_angle} درجة")

            # إضافة الأختام إذا كانت موجودة
            if page_num in page_stamps and page_stamps[page_num]:
                stamps_count = len(page_stamps[page_num])
                print(f"  - عدد الأختام: {stamps_count}")
                add_stamps_to_page(page, page_stamps[page_num], view_scale_factor, input_path, page_num)
            else:
                print(f"  - لا توجد أختام")

        # حفظ المستند مع خيارات محسنة
        print(f"\nحفظ المستند...")
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

        print(f"تم حفظ الملف بنجاح: {output_path}")

        # التحقق من جودة الحفظ
        print(f"\nالتحقق من جودة الحفظ...")
        verification_result = verify_stamp_placement(output_path, page_stamps)

        if verification_result['success']:
            print(f"✓ تم التحقق من جودة الحفظ بنجاح")
        else:
            print(f"⚠ تحذير: تم العثور على مشاكل في الحفظ:")
            for issue in verification_result['issues']:
                print(f"  - {issue}")

        return True

    except Exception as e:
        print(f"خطأ في حفظ PDF مع الأختام: {e}")
        import traceback
        print(f"تفاصيل الخطأ: {traceback.format_exc()}")
        return False

def add_stamps_to_page(page, stamps, view_scale_factor=1.0, pdf_path=None, page_number=0):
    """
    إضافة الأختام إلى صفحة PDF مع تحويل دقيق للإحداثيات والمقاييس

    Args:
        page: صفحة PyMuPDF
        stamps: قائمة كائنات الأختام
        view_scale_factor: عامل تحجيم العرض (اختياري)
        pdf_path: مسار ملف PDF للمعايرة (اختياري)
        page_number: رقم الصفحة للمعايرة (اختياري)
    """
    try:
        # الحصول على أبعاد الصفحة
        page_rect = page.rect

        # إنشاء معايرة الإحداثيات إذا كانت المعلومات متوفرة
        calibrator = None
        if pdf_path:
            calibrator = CoordinateCalibrator(pdf_path, page_number)
            # تقدير أبعاد العرض بناءً على عامل التحجيم
            estimated_view_width = page_rect.width / view_scale_factor
            estimated_view_height = page_rect.height / view_scale_factor
            from PySide6.QtCore import QRectF
            calibrator.set_view_page_rect(QRectF(0, 0, estimated_view_width, estimated_view_height))

        for stamp in stamps:
            # الحصول على بيانات الختم
            stamp_data = stamp.get_stamp_data()
            image_path = stamp_data['image_path']
            position = stamp_data['position']
            scale = stamp_data['scale']
            opacity = stamp_data['opacity']

            # استخدام البيانات المحسنة إذا كانت متوفرة
            if 'current_width' in stamp_data and 'current_height' in stamp_data:
                display_width = stamp_data['current_width']
                display_height = stamp_data['current_height']
                final_scale = stamp_data.get('final_scale', scale)
            else:
                # الطريقة القديمة كاحتياطي
                current_pixmap = stamp.pixmap()
                display_width = current_pixmap.width()
                display_height = current_pixmap.height()
                final_scale = scale

            # حساب الحجم النهائي للختم في PDF
            final_width = display_width
            final_height = display_height

            # إصلاح تحويل الإحداثيات - تعديل لمعالجة الانزياح للأسفل
            pdf_x = position[0]
            # تعديل الإحداثي Y لمعالجة الانزياح للأسفل
            pdf_y = position[1] - 75  # زيادة التعديل لرفع الختم لأعلى بشكل أكبر
            scaled_width = final_width
            scaled_height = final_height

            print(f"إحداثيات مباشرة (بدون تحويل Y):")
            print(f"  - الموضع: ({pdf_x:.1f}, {pdf_y:.1f})")
            print(f"  - الحجم: ({scaled_width:.1f}x{scaled_height:.1f})")
            print(f"  - أبعاد الصفحة: ({page_rect.width:.1f}x{page_rect.height:.1f})")

            # طباعة معلومات التصحيح قبل التحقق
            print(f"قبل التحقق - الموضع: ({pdf_x:.1f}, {pdf_y:.1f}), الحجم: ({scaled_width:.1f}x{scaled_height:.1f})")
            print(f"أبعاد الصفحة: ({page_rect.width:.1f}x{page_rect.height:.1f})")

            # التحقق من الحدود وتصحيحها
            if pdf_x < 0 or pdf_y < 0 or pdf_x + scaled_width > page_rect.width or pdf_y + scaled_height > page_rect.height:
                print("⚠️ الختم خارج حدود الصفحة - سيتم تصحيحه")
                pdf_x = max(0, min(pdf_x, page_rect.width - scaled_width))
                pdf_y = max(0, min(pdf_y, page_rect.height - scaled_height))
                scaled_width = min(scaled_width, page_rect.width - pdf_x)
                scaled_height = min(scaled_height, page_rect.height - pdf_y)
                print(f"بعد التصحيح - الموضع: ({pdf_x:.1f}, {pdf_y:.1f}), الحجم: ({scaled_width:.1f}x{scaled_height:.1f})")
            else:
                print("✅ الختم داخل حدود الصفحة")

            # استخدام الأبعاد المصححة
            final_width = scaled_width
            final_height = scaled_height

            stamp_rect = fitz.Rect(
                pdf_x,
                pdf_y,
                pdf_x + final_width,
                pdf_y + final_height
            )

            # إدراج الصورة مع معلومات التصحيح محسنة وخيارات متقدمة
            print(f"إدراج ختم محسن:")
            print(f"  - المسار: {image_path}")
            print(f"  - الموضع الأصلي: ({position[0]:.1f}, {position[1]:.1f})")
            print(f"  - الموضع في PDF: ({pdf_x:.1f}, {pdf_y:.1f})")
            print(f"  - الحجم المعروض: ({display_width}x{display_height})")
            print(f"  - الحجم النهائي: ({final_width:.1f}x{final_height:.1f})")
            print(f"  - المقياس: {scale:.2f}, الشفافية: {opacity:.2f}")
            print(f"  - عامل تحجيم العرض: {view_scale_factor:.2f}")
            print(f"  - مستطيل الختم: ({stamp_rect.x0:.1f}, {stamp_rect.y0:.1f}, {stamp_rect.x1:.1f}, {stamp_rect.y1:.1f})")

            # التحقق من وجود ملف الصورة أولاً
            import os
            if not os.path.exists(image_path):
                print(f"❌ خطأ: ملف الصورة غير موجود: {image_path}")
                continue

            print(f"✅ ملف الصورة موجود: {image_path}")

            # إدراج الصورة مع معالجة الأخطاء
            try:
                # الطريقة البسيطة والمضمونة
                page.insert_image(stamp_rect, filename=image_path, alpha=int(opacity * 255))
                print(f"✅ تم إدراج الختم بنجاح في الموضع ({pdf_x:.1f}, {pdf_y:.1f})")

            except Exception as insert_error:
                print(f"❌ خطأ في إدراج الختم: {insert_error}")
                print(f"   - مسار الصورة: {image_path}")
                print(f"   - مستطيل الختم: {stamp_rect}")
                print(f"   - شفافية: {int(opacity * 255)}")
                continue

    except Exception as e:
        print(f"خطأ في إضافة الأختام للصفحة: {e}")
        import traceback
        print(f"تفاصيل الخطأ: {traceback.format_exc()}")

def create_preview_with_stamps(page_pixmap, stamps, page_rotation=0):
    """
    إنشاء معاينة للصفحة مع الأختام
    
    Args:
        page_pixmap: صورة الصفحة الأصلية
        stamps: قائمة الأختام
        page_rotation: زاوية دوران الصفحة
    
    Returns:
        QPixmap: صورة الصفحة مع الأختام
    """
    try:
        # إنشاء صورة جديدة بنفس حجم الصفحة
        result_pixmap = QPixmap(page_pixmap.size())
        result_pixmap.fill(Qt.white)
        
        # إنشاء رسام
        painter = QPainter(result_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # رسم الصفحة الأساسية
        if page_rotation != 0:
            # تطبيق التدوير
            painter.translate(result_pixmap.width()/2, result_pixmap.height()/2)
            painter.rotate(page_rotation)
            painter.translate(-page_pixmap.width()/2, -page_pixmap.height()/2)
        
        painter.drawPixmap(0, 0, page_pixmap)
        
        # رسم الأختام
        for stamp in stamps:
            stamp_data = stamp.get_stamp_data()
            position = stamp_data['position']
            scale = stamp_data['scale']
            opacity = stamp_data['opacity']
            
            # تحميل صورة الختم
            stamp_pixmap = QPixmap(stamp_data['image_path'])
            if not stamp_pixmap.isNull():
                # تطبيق التحجيم
                if scale != 1.0:
                    stamp_pixmap = stamp_pixmap.scaled(
                        int(stamp_pixmap.width() * scale),
                        int(stamp_pixmap.height() * scale),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                
                # تطبيق الشفافية
                painter.setOpacity(opacity)
                
                # رسم الختم
                painter.drawPixmap(int(position[0]), int(position[1]), stamp_pixmap)
                
                # إعادة تعيين الشفافية
                painter.setOpacity(1.0)
        
        painter.end()
        return result_pixmap
        
    except Exception as e:
        print(f"خطأ في إنشاء معاينة مع الأختام: {e}")
        return page_pixmap

def export_page_as_image(page_pixmap, stamps, output_path, page_rotation=0):
    """
    تصدير صفحة مع الأختام كصورة
    
    Args:
        page_pixmap: صورة الصفحة
        stamps: قائمة الأختام
        output_path: مسار الحفظ
        page_rotation: زاوية الدوران
    
    Returns:
        bool: True إذا نجحت العملية
    """
    try:
        # إنشاء الصورة مع الأختام
        result_pixmap = create_preview_with_stamps(page_pixmap, stamps, page_rotation)
        
        # حفظ الصورة
        return result_pixmap.save(output_path)
        
    except Exception as e:
        print(f"خطأ في تصدير الصفحة كصورة: {e}")
        return False

def get_stamp_summary(page_stamps):
    """
    الحصول على ملخص الأختام
    
    Args:
        page_stamps (dict): قاموس الأختام
    
    Returns:
        dict: ملخص الأختام
    """
    summary = {
        'total_pages_with_stamps': 0,
        'total_stamps': 0,
        'stamps_per_page': {}
    }
    
    for page_num, stamps in page_stamps.items():
        if stamps:
            summary['total_pages_with_stamps'] += 1
            summary['total_stamps'] += len(stamps)
            summary['stamps_per_page'][page_num] = len(stamps)
    
    return summary

def verify_stamp_placement(pdf_path, expected_stamps_info):
    """
    التحقق من صحة وضع الأختام في ملف PDF المحفوظ

    Args:
        pdf_path (str): مسار ملف PDF
        expected_stamps_info (dict): معلومات الأختام المتوقعة

    Returns:
        dict: تقرير التحقق
    """
    verification_report = {
        'success': True,
        'total_pages_checked': 0,
        'stamps_verified': 0,
        'issues': []
    }

    try:
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            verification_report['total_pages_checked'] += 1
            page = doc[page_num]

            # فحص وجود الصور في الصفحة
            image_list = page.get_images()

            if page_num in expected_stamps_info:
                expected_count = len(expected_stamps_info[page_num])
                actual_count = len(image_list)

                if actual_count >= expected_count:
                    verification_report['stamps_verified'] += expected_count
                    print(f"✓ الصفحة {page_num + 1}: تم العثور على {actual_count} صورة (متوقع {expected_count})")
                else:
                    issue = f"الصفحة {page_num + 1}: عدد الصور غير مطابق - موجود {actual_count}, متوقع {expected_count}"
                    verification_report['issues'].append(issue)
                    verification_report['success'] = False
                    print(f"⚠ {issue}")

        doc.close()

        if verification_report['success']:
            print(f"✓ تم التحقق بنجاح من {verification_report['stamps_verified']} ختم في {verification_report['total_pages_checked']} صفحة")
        else:
            print(f"⚠ تم العثور على {len(verification_report['issues'])} مشكلة أثناء التحقق")

    except Exception as e:
        verification_report['success'] = False
        verification_report['issues'].append(f"خطأ في فتح الملف: {e}")
        print(f"✗ خطأ في التحقق: {e}")

    return verification_report
