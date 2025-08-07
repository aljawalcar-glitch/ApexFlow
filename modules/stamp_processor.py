# -*- coding: utf-8 -*-
"""
معالج الأختام - دمج الأختام مع ملفات PDF
Stamp Processor - Merge stamps with PDF files
"""

import fitz  # PyMuPDF
from PySide6.QtGui import QPixmap, QPainter, QImage, QTransform
from PySide6.QtCore import Qt, QRectF, QObject, Signal
import tempfile
import os
from .coordinate_calibrator import CoordinateCalibrator, validate_coordinates

class StampWorker(QObject):
    """
    عامل لمعالجة وحفظ PDF في خيط منفصل لتجنب تجميد الواجهة.
    """
    progress = Signal(int, int)  # (current_page, total_pages)
    finished = Signal(bool, str, dict)  # (success, output_path, summary)
    error = Signal(str)

    def __init__(self, input_path, output_path, page_rotations, page_stamps, view_rect, scene_rect):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.page_rotations = page_rotations
        self.page_stamps = page_stamps
        self.view_rect = view_rect
        self.scene_rect = scene_rect
        self.is_cancelled = False

    def cancel(self):
        """إلغاء العملية"""
        self.is_cancelled = True

    def run(self):
        """
        تشغيل عملية حفظ PDF مع الأختام.
        """
        try:
            print(f"بدء الحفظ في خيط منفصل: {self.input_path} -> {self.output_path}")
            
            input_doc = fitz.open(self.input_path)
            output_doc = fitz.open()
            temp_files = []
            total_pages = len(input_doc)

            for page_num in range(total_pages):
                if self.is_cancelled:
                    print(f"تم إلغاء العملية عند الصفحة {page_num + 1}")
                    self.finished.emit(False, "", {})
                    return

                print(f"\n--- معالجة الصفحة {page_num + 1}/{total_pages} ---")
                self.progress.emit(page_num, total_pages)

                page = input_doc[page_num]
                rotation = self.page_rotations.get(page_num, 0)
                stamps = self.page_stamps.get(page_num, [])

                zoom_matrix = fitz.Matrix(3, 3)
                page_pixmap_fitz = page.get_pixmap(matrix=zoom_matrix)
                
                image_format = QImage.Format_RGBA8888 if page_pixmap_fitz.alpha else QImage.Format_RGB888
                qimage = QImage(page_pixmap_fitz.samples, page_pixmap_fitz.width, page_pixmap_fitz.height, page_pixmap_fitz.stride, image_format)
                page_pixmap = QPixmap.fromImage(qimage)

                if rotation != 0:
                    transform = QTransform().rotate(rotation)
                    page_pixmap = page_pixmap.transformed(transform, Qt.SmoothTransformation)

                if stamps:
                    final_pixmap = create_stamped_image(page_pixmap, stamps, self.scene_rect)
                else:
                    final_pixmap = page_pixmap

                temp_image_path = os.path.join(tempfile.gettempdir(), f"stamped_page_{page_num}.png")
                if not final_pixmap.save(temp_image_path, "PNG"):
                    raise Exception(f"فشل حفظ الصورة المؤقتة: {temp_image_path}")
                temp_files.append(temp_image_path)

                img_doc = fitz.open(temp_image_path)
                pdf_bytes = img_doc.convert_to_pdf()
                img_pdf_doc = fitz.open("pdf", pdf_bytes)
                output_doc.insert_pdf(img_pdf_doc)
                img_doc.close()
                img_pdf_doc.close()

            if self.is_cancelled:
                self.finished.emit(False, "", {})
                return

            self.progress.emit(total_pages, total_pages)

            if len(output_doc) > 0:
                output_doc.save(self.output_path, garbage=4, deflate=True, clean=True)
                summary = get_stamp_summary(self.page_stamps)
                self.finished.emit(True, self.output_path, summary)
            else:
                self.finished.emit(False, "", {})

        except Exception as e:
            error_msg = f"خطأ فادح في حفظ PDF: {e}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"تفاصيل الخطأ: {traceback.format_exc()}")
            self.error.emit(error_msg)
        finally:
            if 'output_doc' in locals() and output_doc:
                output_doc.close()
            if 'input_doc' in locals() and input_doc:
                input_doc.close()
            
            for f in temp_files:
                try:
                    os.remove(f)
                except OSError:
                    pass

def save_pdf_with_stamps(input_path, output_path, page_rotations, page_stamps, view_rect=None, scene_rect=None):
    """
    حفظ ملف PDF مع الأختام عن طريق تحويل الصفحات إلى صور ودمجها.
    هذه الطريقة تضمن تطابق "ما تراه هو ما تحصل عليه" على حساب قابلية تحرير النص.

    Args:
        input_path (str): مسار الملف الأصلي
        output_path (str): مسار الملف المحفوظ
        page_rotations (dict): قاموس التدوير {page_num: angle}
        page_stamps (dict): قاموس الأختام {page_num: [stamp_objects]}
        view_rect (QRect): أبعاد منطقة العرض (viewport) - غير مستخدم حالياً
        scene_rect (QRectF): أبعاد المشهد (scene) - مهم لحساب مواضع الأختام

    Returns:
        bool: True إذا نجحت العملية
    """
    try:
        print(f"بدء الحفظ بطريقة الصورة: {input_path} -> {output_path}")
        
        input_doc = fitz.open(input_path)
        output_doc = fitz.open()  # إنشاء مستند PDF جديد فارغ
        
        temp_files = []

        # معالجة كل صفحة
        for page_num in range(len(input_doc)):
            print(f"\n--- معالجة الصفحة {page_num + 1}/{len(input_doc)} ---")
            
            # 1. الحصول على بيانات الصفحة
            page = input_doc[page_num]
            rotation = page_rotations.get(page_num, 0)
            stamps = page_stamps.get(page_num, [])
            
            # 2. تحويل صفحة PDF إلى صورة عالية الجودة (QPixmap)
            #    - نستخدم مصفوفة تكبير (zoom matrix) للحصول على دقة أعلى (e.g., 3x for better quality)
            zoom_matrix = fitz.Matrix(3, 3)
            page_pixmap_fitz = page.get_pixmap(matrix=zoom_matrix)
            
            # تحويل من fitz.Pixmap إلى QPixmap
            image_format = QImage.Format_RGB888
            if page_pixmap_fitz.alpha:
                image_format = QImage.Format_RGBA8888
            
            qimage = QImage(page_pixmap_fitz.samples, page_pixmap_fitz.width, page_pixmap_fitz.height, page_pixmap_fitz.stride, image_format)
            page_pixmap = QPixmap.fromImage(qimage)

            # تطبيق التدوير يدويًا إذا لزم الأمر
            if rotation != 0:
                transform = QTransform().rotate(rotation)
                page_pixmap = page_pixmap.transformed(transform, Qt.SmoothTransformation)

            print(f"  - تم تحويل الصفحة إلى صورة بحجم: {page_pixmap.width()}x{page_pixmap.height()}")

            # 3. رسم الأختام على الصورة
            image_format = QImage.Format_RGB888
            if page_pixmap_fitz.alpha:
                image_format = QImage.Format_RGBA8888
            
            # 3. رسم الأختام على الصورة
            if stamps:
                print(f"  - سيتم إضافة {len(stamps)} ختم")
                # نستخدم أبعاد الصورة كمشهد مرجعي جديد للختم
                final_pixmap = create_stamped_image(page_pixmap, stamps, scene_rect)
            else:
                final_pixmap = page_pixmap
                print("  - لا توجد أختام لهذه الصفحة.")

            # 4. حفظ الصورة النهائية مؤقتاً
            temp_image_path = os.path.join(tempfile.gettempdir(), f"stamped_page_{page_num}.png")
            if not final_pixmap.save(temp_image_path, "PNG"):
                 raise Exception(f"فشل حفظ الصورة المؤقتة: {temp_image_path}")
            temp_files.append(temp_image_path)
            print(f"  - تم حفظ الصورة المختومة مؤقتاً في: {temp_image_path}")

            # 5. إضافة الصورة كصفحة جديدة في ملف PDF الناتج
            img_doc = fitz.open(temp_image_path)
            pdf_bytes = img_doc.convert_to_pdf()
            img_pdf_doc = fitz.open("pdf", pdf_bytes)
            output_doc.insert_pdf(img_pdf_doc)
            img_doc.close()
            img_pdf_doc.close()
            print(f"  - تم إضافة الصورة كصفحة جديدة في الملف الناتج.")

        # 6. حفظ المستند النهائي
        if len(output_doc) > 0:
            print("\nحفظ المستند النهائي...")
            output_doc.save(output_path, garbage=4, deflate=True, clean=True)
            print(f"✓ تم حفظ الملف بنجاح: {output_path}")
        else:
            print("⚠ تحذير: لم يتم إنشاء أي صفحات في الملف الناتج.")

        return True

    except Exception as e:
        print(f"❌ خطأ فادح في حفظ PDF بطريقة الصورة: {e}")
        import traceback
        print(f"تفاصيل الخطأ: {traceback.format_exc()}")
        return False
    finally:
        # 7. تنظيف الملفات المؤقتة
        if 'output_doc' in locals() and output_doc:
            output_doc.close()
        if 'input_doc' in locals() and input_doc:
            input_doc.close()
            
        print("\nتنظيف الملفات المؤقتة...")
        for f in temp_files:
            try:
                os.remove(f)
                print(f"  - تم حذف: {f}")
            except OSError as e:
                print(f"  - فشل حذف {f}: {e}")

def create_stamped_image(base_pixmap, stamps, scene_rect):
    """
    يرسم الأختام على صورة (QPixmap) موجودة.
    هذه هي النسخة المستخدمة في الحفظ النهائي والمعاينة.

    Args:
        base_pixmap (QPixmap): الصورة الأساسية للصفحة (قد تكون مدورة).
        stamps (list): قائمة كائنات الأختام.
        scene_rect (QRectF): أبعاد المشهد الأصلي الذي تم وضع الأختام فيه (مهم للتحويل).

    Returns:
        QPixmap: صورة جديدة مع الأختام مرسومة عليها.
    """
    try:
        result_pixmap = base_pixmap.copy()
        painter = QPainter(result_pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        target_rect = result_pixmap.rect()
        if not scene_rect or scene_rect.width() == 0 or scene_rect.height() == 0:
            print("تحذير: أبعاد المشهد المصدر غير صالحة. لا يمكن رسم الأختام بدقة.")
            return base_pixmap

        for stamp in stamps:
            stamp_data = stamp.get_stamp_data()
            stamp_pixmap = QPixmap(stamp_data['image_path'])
            if stamp_pixmap.isNull():
                print(f"تحذير: لا يمكن تحميل صورة الختم: {stamp_data['image_path']}")
                continue

            original_pos = stamp_data['position']
            original_width = stamp_data['current_width']
            original_height = stamp_data['current_height']

            x_ratio = original_pos[0] / scene_rect.width()
            y_ratio = original_pos[1] / scene_rect.height()
            width_ratio = original_width / scene_rect.width()
            height_ratio = original_height / scene_rect.height()

            target_x = x_ratio * target_rect.width()
            target_y = y_ratio * target_rect.height()
            target_width = width_ratio * target_rect.width()
            target_height = height_ratio * target_rect.height()
            
            painter.setOpacity(stamp_data['opacity'])
            target_draw_rect = QRectF(target_x, target_y, target_width, target_height)
            painter.drawPixmap(target_draw_rect, stamp_pixmap, stamp_pixmap.rect())
            painter.setOpacity(1.0)

        painter.end()
        return result_pixmap
        
    except Exception as e:
        print(f"خطأ في إنشاء صورة مختومة: {e}")
        import traceback
        print(f"تفاصيل الخطأ: {traceback.format_exc()}")
        return base_pixmap

def create_preview_with_stamps(page_pixmap, stamps, scene_rect, page_rotation=0):
    """
    إنشاء معاينة للصفحة مع الأختام (للعرض في الواجهة).
    هذه الدالة تقوم بتطبيق التدوير قبل استدعاء دالة الرسم الأساسية.

    Args:
        page_pixmap (QPixmap): صورة الصفحة الأصلية (غير مدورة).
        stamps (list): قائمة الأختام.
        scene_rect (QRectF): أبعاد المشهد الذي تم وضع الأختام فيه.
        page_rotation (int): زاوية دوران الصفحة.

    Returns:
        QPixmap: صورة الصفحة النهائية مع التدوير والأختام.
    """
    try:
        # 1. إنشاء QTransform لتطبيق التدوير
        transform = QTransform()
        transform.translate(page_pixmap.width() / 2, page_pixmap.height() / 2)
        transform.rotate(page_rotation)
        transform.translate(-page_pixmap.width() / 2, -page_pixmap.height() / 2)

        # 2. تطبيق التدوير على صورة الصفحة الأساسية
        rotated_pixmap = page_pixmap.transformed(transform, Qt.SmoothTransformation)

        # 3. استدعاء الدالة الأساسية لرسم الأختام على الصورة المدورة
        return create_stamped_image(rotated_pixmap, stamps, scene_rect)

    except Exception as e:
        print(f"خطأ في إنشاء معاينة مع الأختام: {e}")
        import traceback
        print(f"تفاصيل الخطأ: {traceback.format_exc()}")
        return page_pixmap # إرجاع الصورة الأصلية في حالة الخطأ

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
