"""
Script to create a simple PDF icon
سكريبت لإنشاء أيقونة PDF بسيطة
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_pdf_icon(size=64, output_path="pdf_icon.png"):
    """
    Create a simple PDF icon
    إنشاء أيقونة PDF بسيطة
    """
    try:
        # إنشاء صورة جديدة بخلفية شفافة
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # ألوان
        bg_color = (220, 53, 69)  # أحمر
        text_color = (255, 255, 255)  # أبيض
        border_color = (180, 43, 59)  # أحمر داكن
        
        # رسم الخلفية المستطيلة
        margin = 4
        draw.rounded_rectangle(
            [margin, margin, size-margin, size-margin],
            radius=8,
            fill=bg_color,
            outline=border_color,
            width=2
        )
        
        # محاولة استخدام خط مناسب
        try:
            font_size = max(12, size // 4)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # رسم النص "PDF"
        text = "PDF"
        if font:
            # حساب موضع النص في المنتصف
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, fill=text_color, font=font)
        else:
            # رسم النص بدون خط محدد
            x = size // 4
            y = size // 3
            draw.text((x, y), text, fill=text_color)
        
        # حفظ الأيقونة
        img.save(output_path, "PNG")
        print(f"تم إنشاء الأيقونة: {output_path}")
        return True
        
    except Exception as e:
        print(f"خطأ في إنشاء الأيقونة: {str(e)}")
        return False

if __name__ == "__main__":
    # إنشاء الأيقونة
    create_pdf_icon(64, "pdf_icon.png")
