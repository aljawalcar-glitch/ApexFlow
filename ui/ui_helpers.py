"""
وحدة الدوال المساعدة للواجهة
تحتوي على الدوال المساعدة للألوان والأنماط والتأثيرات البصرية
"""

from PySide6.QtWidgets import QPushButton, QLabel, QComboBox
from PySide6.QtCore import Qt
from .theme_manager import apply_theme_style

class FocusAwareComboBox(QComboBox):
    """
    QComboBox مخصص يتجاهل بكرة الماوس إلا إذا كانت القائمة مفتوحة.
    يحل مشكلة "سرقة" التمرير من الصفحات القابلة للتمرير.
    """
    def wheelEvent(self, event):
        if self.view().isVisible():
            # إذا كانت القائمة مفتوحة، اسمح بالتمرير
            super().wheelEvent(event)
        else:
            # إذا كانت القائمة مغلقة، تجاهل الحدث للسماح للصفحة بالتمرير
            event.ignore()

def create_button(text, on_click=None, is_default=False):
    """
    إنشاء زر بتصميم موحد.
    """
    button = QPushButton(text)
    # استخدام نظام السمات لتطبيق النمط
    apply_theme_style(button, "button", auto_register=True)
    if is_default:
        button.setDefault(True)
    if on_click:
        button.clicked.connect(on_click)
    return button

def create_title(text):
    """
    إنشاء عنوان صفحة بتصميم موحد.
    """
    title = QLabel(text)
    # استخدام نظام السمات لتطبيق النمط
    apply_theme_style(title, "title_text", auto_register=True)
    title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return title

def create_section_label(text):
    """
    Crea una QLabel para títulos de sección con un estilo específico.
    """
    label = QLabel(text)
    apply_theme_style(label, "section_label", auto_register=True)
    return label

def create_info_label(text):
    """
    Crea una QLabel para texto informativo con un estilo más suave.
    """
    label = QLabel(text)
    apply_theme_style(label, "info_label", auto_register=True)
    return label

# تم نقل darken_color إلى global_styles.py لتجنب التكرار

def hex_to_rgba(color, alpha=1.0):
    """تحويل لون hex إلى rgba"""
    # إزالة # إذا كانت موجودة
    color = color.lstrip('#')
    
    # تحويل إلى RGB
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    return f"rgba({r}, {g}, {b}, {alpha})"

def get_button_style(color, min_width=120):
    """إنشاء نمط زجاجي محسن للأزرار"""
    # تحويل اللون إلى rgba للشفافية
    rgba_color = hex_to_rgba(color, 0.4)
    rgba_hover = hex_to_rgba(color, 0.6)
    rgba_pressed = hex_to_rgba(color, 0.3)
    
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(180, 180, 180, 0.25),
                stop:0.5 rgba(180, 180, 180, 0.15),
                stop:1 {rgba_color});
            border: 1px solid rgba(180, 180, 180, 0.3);
            border-radius: 12px;
            color: white;
            font-size: 14px;
            font-weight: bold;
            min-width: {min_width}px;
            padding: 12px 24px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(180, 180, 180, 0.35),
                stop:0.5 rgba(180, 180, 180, 0.25),
                stop:1 {rgba_hover});
            border: 1px solid rgba(180, 180, 180, 0.5);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(180, 180, 180, 0.15),
                stop:0.5 rgba(180, 180, 180, 0.05),
                stop:1 {rgba_pressed});
            border: 1px solid rgba(180, 180, 180, 0.4);
        }}
    """

def get_combo_style():
    """تنسيق القوائم المنسدلة - محدث للتوحيد مع النمط الجديد"""
    return """
        QComboBox {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px 12px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            min-height: 20px;
            min-width: 150px;
        }
        QComboBox:hover {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 111, 0, 0.5);
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            background: rgba(255, 255, 255, 0.02);
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid rgba(255, 255, 255, 0.8);
            width: 0;
            height: 0;
        }
        QComboBox QAbstractItemView {
            background: rgba(26, 32, 44, 0.85);
            border: 1px solid rgba(255, 111, 0, 0.5);
            border-radius: 8px;
            color: rgba(255, 255, 255, 0.95);
            selection-background-color: rgba(255, 111, 0, 0.3);
            selection-color: white;
            padding: 4px;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            background: transparent;
            border: none;
            padding: 8px 12px;
            margin: 2px;
            border-radius: 4px;
            min-height: 20px;
        }
        QComboBox QAbstractItemView::item:hover {
            background: rgba(255, 111, 0, 0.2);
            color: white;
        }
        QComboBox QAbstractItemView::item:selected {
            background: rgba(255, 111, 0, 0.4);
            color: white;
        }
    """

def get_input_style():
    """تنسيق حقول الإدخال"""
    return """
        QLineEdit {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 6px;
            color: white;
            padding: 8px 12px;
            font-size: 13px;
            min-width: 150px;
        }
        QLineEdit:hover {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.25);
        }
    """

def adjust_color_brightness(color, factor):
    """تعديل سطوع اللون"""
    if color.startswith('#'):
        color = color[1:]
    
    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return color

def get_scroll_style():
    """تخصيص مظهر شريط التمرير"""
    return """
    QScrollBar:vertical {
        background: #2d3748;
        width: 10px;
        margin: 4px 0 4px 0;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #ff6f00;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    """

def get_menu_style():
    """تنسيق القائمة الجانبية"""
    return """
        QListWidget {
            background-color: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 8px;
            font-size: 16px;
            color: white;
            padding: 5px;
            text-align: right;
        }
        QListWidget::item {
            padding: 12px;
            margin: 2px;
            border-radius: 6px;
            text-align: right;
        }
        QListWidget::item:selected {
            background-color: #ff6f00;
            color: white;
        }
        QListWidget::item:hover {
            background-color: #4a5568;
        }
    """
