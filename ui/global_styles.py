from PySide6.QtWidgets import QWidget

def get_font_settings():
    """الحصول على إعدادات الخطوط من الملف"""
    try:
        from modules import settings
        settings_data = settings.load_settings()
        ui_settings = settings_data.get("ui_settings", {})

        font_size = ui_settings.get("font_size", 14)
        font_family = ui_settings.get("font_family", "النظام الافتراضي")
        font_weight = ui_settings.get("font_weight", "عادي")

        # تحويل نوع الخط
        if font_family == "النظام الافتراضي":
            font_family_css = "'Segoe UI', 'Tahoma', 'Arial Unicode MS', 'Cairo', sans-serif"
        else:
            font_family_css = f"'{font_family}', 'Segoe UI', sans-serif"

        # تحويل وزن الخط
        weight_map = {
            "عادي": "normal",
            "سميك": "bold",
            "سميك جداً": "900"
        }
        font_weight_css = weight_map.get(font_weight, "normal")

        return {
            "size": font_size,
            "family": font_family_css,
            "weight": font_weight_css
        }
    except:
        # القيم الافتراضية في حالة الخطأ
        return {
            "size": 14,
            "family": "'Segoe UI', 'Tahoma', 'Arial Unicode MS', 'Cairo', sans-serif",
            "weight": "normal"
        }

def get_widget_style(widget_type, colors, accent_color):
    """مولد الأنماط الموحد لجميع العناصر"""

    # الحصول على إعدادات الخطوط
    font_settings = get_font_settings()

    if widget_type == "main_window":
        return f"""
            QMainWindow {{
                background-color: {colors["bg"]};
                color: {colors["text_body"]};
            }}
            QLabel {{
                color: {colors["text_body"]};
                background: transparent;
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "dialog" or widget_type == "settings_window":
        return f"""
            QDialog, QWidget {{
                background-color: {colors["bg"]};
                color: {colors["text_body"]};
                font-family: 'Microsoft Sans Serif', 'Segoe UI', 'Tahoma', Arial, sans-serif;
            }}
            QFrame {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
            }}
            QLabel {{
                color: {colors["text_body"]};
                background: transparent;
                border: none;
                outline: none;
            }}
            QFormLayout QLabel {{
                color: {colors["text_body"]};
                background: transparent;
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "button":
        return f"""
            QPushButton {{
                background-color: {accent_color};
                color: {colors["text_body"]};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {darken_color(accent_color)};
            }}
        """

    elif widget_type == "frame":
        return f"""
            QFrame {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
            }}
        """

    elif widget_type == "label":
        return f"""
            QLabel {{
                color: {colors["text_body"]};
                background: transparent;
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "title_text":
        return f"""
            QLabel {{
                color: {colors["text_title"]};
                background: transparent;
                font-size: {int(font_settings["size"] * 1.7)}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "body_text":
        return f"""
            QLabel {{
                color: {colors["text_body"]};
                background: transparent;
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "secondary_text":
        return f"""
            QLabel {{
                color: {colors["text_secondary"]};
                background: transparent;
                font-size: {int(font_settings["size"] * 0.9)}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "muted_text":
        return f"""
            QLabel {{
                color: {colors["text_muted"]};
                background: transparent;
                font-size: {int(font_settings["size"] * 0.8)}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "accent_text":
        return f"""
            QLabel {{
                color: {colors["text_accent"]};
                background: transparent;
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "section_label":
        return f"""
            QLabel {{
                color: {colors["text_title"]};
                background: transparent;
                font-size: {int(font_settings["size"] * 1.3)}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
                border: none;
                outline: none;
                margin-bottom: 10px;
            }}
        """

    elif widget_type == "info_label":
        return f"""
            QLabel {{
                color: {colors["text_secondary"]};
                background: transparent;
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
                border: none;
                outline: none;
            }}
        """

    # تم حذف mixed_text و mixed_title - الحلول المعقدة غير مجدية

    elif widget_type == "input":
        return f"""
            QLineEdit {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 6px;
                color: {colors["text_body"]};
                padding: 8px 12px;
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
            }}
            QLineEdit:focus {{
                border: 1px solid {accent_color};
            }}
        """

    elif widget_type == "combo":
        return f"""
            QComboBox {{
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: {colors['text_body']};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
                min-height: 20px;
                selection-background-color: rgba(255, 111, 0, 0.3);
            }}

            QComboBox:hover {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid {accent_color}80;
            }}

            QComboBox:focus {{
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid {accent_color}CC;
                outline: none;
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid rgba(255, 255, 255, 0.1);
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background: rgba(255, 255, 255, 0.02);
            }}

            QComboBox::drop-down:hover {{
                background: {accent_color}33;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid rgba(255, 255, 255, 0.8);
                width: 0;
                height: 0;
            }}

            QComboBox::down-arrow:hover {{
                border-top: 6px solid {accent_color};
            }}

            QComboBox QAbstractItemView {{
                background: rgba(26, 32, 44, 0.85);
                border: 1px solid {accent_color}80;
                border-radius: 8px;
                color: rgba(255, 255, 255, 0.95);
                selection-background-color: {accent_color}4D;
                selection-color: white;
                padding: 4px;
                outline: none;
            }}

            QComboBox QAbstractItemView::item {{
                background: transparent;
                border: none;
                padding: 8px 12px;
                margin: 2px;
                border-radius: 4px;
                min-height: 20px;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background: {accent_color}33;
                color: white;
            }}

            QComboBox QAbstractItemView::item:selected {{
                background: {accent_color}66;
                color: white;
            }}
        """

    elif widget_type == "combobox":
        # نفس نمط "combo" للتوحيد
        return f"""
            QComboBox {{
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: {colors['text_body']};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
                min-height: 20px;
                selection-background-color: rgba(255, 111, 0, 0.3);
            }}

            QComboBox:hover {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid {accent_color}80;
            }}

            QComboBox:focus {{
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid {accent_color}CC;
                outline: none;
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid rgba(255, 255, 255, 0.1);
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background: rgba(255, 255, 255, 0.02);
            }}

            QComboBox::drop-down:hover {{
                background: {accent_color}33;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid rgba(255, 255, 255, 0.8);
                width: 0;
                height: 0;
            }}

            QComboBox::down-arrow:hover {{
                border-top: 6px solid {accent_color};
            }}

            QComboBox QAbstractItemView {{
                background: rgba(26, 32, 44, 0.85);
                border: 1px solid {accent_color}80;
                border-radius: 8px;
                color: rgba(255, 255, 255, 0.95);
                selection-background-color: {accent_color}4D;
                selection-color: white;
                padding: 4px;
                outline: none;
            }}

            QComboBox QAbstractItemView::item {{
                background: transparent;
                border: none;
                padding: 8px 12px;
                margin: 2px;
                border-radius: 4px;
                min-height: 20px;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background: {accent_color}33;
                color: white;
            }}

            QComboBox QAbstractItemView::item:selected {{
                background: {accent_color}66;
                color: white;
            }}
        """

    elif widget_type == "menu":
        return f"""
            QListWidget {{
                background-color: {colors["surface"]};
                color: {colors["text_body"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                outline: none;
                selection-background-color: transparent;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 12px 15px;
                margin: 2px;
                border-radius: 6px;
                outline: none;
                border: none;
                font-size: 14px;
                font-weight: 500;
            }}
            QListWidget::item:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border-left: 3px solid {accent_color};
                padding-left: 12px;
                border-radius: 6px;
            }}
            QListWidget::item:selected {{
                background-color: {accent_color};
                color: white;
                font-weight: bold;
                border-left: 4px solid {darken_color(accent_color)};
                padding-left: 11px;
                border-radius: 6px;
            }}
            QListWidget::item:selected:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
            }}
            QListWidget::item:focus {{
                outline: none;
                border: none;
            }}
            QListWidget:focus {{
                outline: none;
                border: 1px solid {colors["border"]};
            }}
        """

    elif widget_type == "scroll":
        return f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 12px;
                margin: 0;
                border-radius: 6px;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {accent_color},
                    stop:1 {darken_color(accent_color)});
                min-height: 20px;
                border-radius: 5px;
                margin: 1px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {darken_color(accent_color)},
                    stop:1 {accent_color});
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 12px;
                margin: 0;
                border-radius: 6px;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {accent_color},
                    stop:1 {darken_color(accent_color)});
                min-width: 20px;
                border-radius: 5px;
                margin: 1px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {darken_color(accent_color)},
                    stop:1 {accent_color});
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: transparent;
            }}
        """
    
    elif widget_type == "group_box":
        return f"""
            QGroupBox {{
                font-size: {int(font_settings["size"] * 1.1)}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
                color: {colors.get("text_title", "white")};
                border: 1px solid {colors.get("border", "#4a5568")};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {colors.get("text_secondary", "#a0aec0")};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
            }}
        """

    elif widget_type == "slider":
        return f"""
            QSlider::groove:horizontal {{
                background: {colors['border']};
                height: 8px;
                border-radius: 4px;
                border: 1px solid {colors['surface']};
            }}
            QSlider::handle:horizontal {{
                background: {accent_color};
                border: 2px solid {colors['text_body']};
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background: {darken_color(accent_color, -0.2)};
                border: 2px solid {colors['text_accent']};
                transform: scale(1.1);
            }}
            QSlider::handle:horizontal:pressed {{
                background: {darken_color(accent_color, 0.2)};
                border: 2px solid {colors['text_accent']};
            }}
        """

    elif widget_type == "checkbox":
        return f"""
            QCheckBox {{
                color: {colors['text_body']};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background: {colors['surface']};
            }}
            QCheckBox::indicator:hover {{
                background: {colors['bg']};
                border: 1px solid {accent_color};
            }}
            QCheckBox::indicator:checked {{
                background: {accent_color};
                border: 1px solid {darken_color(accent_color)};
            }}
        """

    elif widget_type == "transparent_button":
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 180, 180, 0.25),
                    stop:0.5 rgba(180, 180, 180, 0.15),
                    stop:1 rgba(180, 180, 180, 0.08));
                border: 1px solid rgba(180, 180, 180, 0.3);
                border-radius: 12px;
                color: {colors["text_body"]};
                font-size: 13px;
                font-weight: bold;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 180, 180, 0.35),
                    stop:0.5 rgba(180, 180, 180, 0.25),
                    stop:1 rgba(180, 180, 180, 0.15));
                border: 1px solid rgba(180, 180, 180, 0.5);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 180, 180, 0.15),
                    stop:0.5 rgba(180, 180, 180, 0.05),
                    stop:1 rgba(180, 180, 180, 0.03));
                border: 1px solid rgba(180, 180, 180, 0.4);
            }}
            QPushButton:disabled {{
                background: rgba(180, 180, 180, 0.03);
                border: 1px solid rgba(180, 180, 180, 0.05);
                color: rgba(180, 180, 180, 0.3);
            }}
        """

    elif widget_type == "save_button":
        return f"""
            QPushButton {{
                background: rgba(40, 167, 69, 0.2);
                border: 1px solid rgba(40, 167, 69, 0.4);
                border-radius: 8px;
                color: {colors["text_body"]};
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background: rgba(40, 167, 69, 0.3);
                border: 1px solid rgba(40, 167, 69, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba(40, 167, 69, 0.1);
            }}
        """

    elif widget_type == "cancel_button":
        return f"""
            QPushButton {{
                background: rgba(220, 53, 69, 0.2);
                border: 1px solid rgba(220, 53, 69, 0.4);
                border-radius: 8px;
                color: {colors["text_body"]};
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background: rgba(220, 53, 69, 0.3);
                border: 1px solid rgba(220, 53, 69, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba(220, 53, 69, 0.1);
            }}
        """

    elif widget_type == "progress":
        return f"""
            QProgressBar {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 6px;
                text-align: center;
                color: {colors["text_body"]};
                font-size: 12px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {accent_color},
                    stop:1 {darken_color(accent_color, 0.2)});
                border-radius: 5px;
                margin: 1px;
            }}
        """



    else:  # default
        return f"""
            QWidget {{
                background-color: {colors["bg"]};
                color: {colors["text_body"]};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
            }}
        """

def darken_color(color, factor=0.2):
    """تغميق اللون"""
    from PySide6.QtGui import QColor
    color = QColor(color)
    h, s, l, a = color.getHsl()
    l = max(0, int(l * (1 - factor)))
    color.setHsl(h, s, l, a)
    return color.name()

# تم حذف get_mixed_text_style - الحلول المعقدة غير مجدية

# تم نقل format_mixed_text إلى text_utils.py لتجنب التكرار

def apply_global_style(widget: QWidget):
    """
    تطبّق هذه الدالة تنسيقًا موحدًا على جميع عناصر الواجهة.
    
    يجب تمرير العنصر الجذر (مثل QMainWindow أو QWidget) إليها.

    ✨ المكونات التي يتم تنسيقها:
    - QFrame
    - QLabel
    - QPushButton
    - QLineEdit
    - QScrollBar
    - QComboBox
    - QCheckBox
    - QRadioButton
    - QTabWidget

    ملاحظات:
    - التنسيقات آمنة ومتوافقة مع PyQt6 / PySide6.
    - يتم تطبيق التنسيق مباشرة على العنصر الجذر دون التأثير على الأداء.
    """

    widget.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #e2e8f0;
            font-family: 'Segoe UI', 'Tahoma', 'Arial Unicode MS', 'Cairo', sans-serif;
            font-size: 13px;
        }

        QLabel {
            color: #e2e8f0;
            background: transparent;
            border: none;
            outline: none;
        }

        QLabel:hover {
            background: transparent;
            border: none;
            outline: none;
        }

        QFrame {
            background-color: #1a202c;
            border: 1px solid #2d3748;
            border-radius: 10px;
        }

        QFrame:hover {
            border-color: #ff6f00;
            background-color: #2d3748;
        }

        QPushButton {
            background-color: #2d3748;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
        }
    """)

# الدوال القديمة للتوافق مع الكود الموجود
def get_button_style(color):
    """دالة توافق للأزرار"""
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {darken_color(color)};
        }}
    """

def get_menu_style():
    """دالة توافق للقوائم مع تأثيرات محسنة"""
    return """
        QListWidget {
            background-color: #2d3748;
            color: #e2e8f0;
            border: 1px solid #4a5568;
            border-radius: 8px;
            outline: none;
            selection-background-color: transparent;
            padding: 5px;
        }
        QListWidget::item {
            padding: 12px 15px;
            margin: 2px;
            border-radius: 6px;
            outline: none;
            border: none;
            font-size: 14px;
            font-weight: 500;
        }
        QListWidget::item:hover {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border-left: 3px solid #ff6f00;
            padding-left: 12px;
            border-radius: 6px;
        }
        QListWidget::item:selected {
            background-color: #ff6f00;
            color: white;
            font-weight: bold;
            border-left: 4px solid #e65100;
            padding-left: 11px;
            border-radius: 6px;
        }
        QListWidget::item:selected:hover {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
        }
        QListWidget::item:focus {
            outline: none;
            border: none;
        }
        QListWidget:focus {
            outline: none;
            border: 1px solid #4a5568;
        }
    """

def get_scroll_style():
    """دالة توافق للتمرير مع تأثيرات محسنة"""
    return """
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollBar:vertical {
            background: #2d3748;
            width: 12px;
            margin: 0;
            border-radius: 6px;
            border: 1px solid #4a5568;
        }
        QScrollBar::handle:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ff6f00,
                stop:1 #e65100);
            min-height: 20px;
            border-radius: 5px;
            margin: 1px;
        }
        QScrollBar::handle:vertical:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #e65100,
                stop:1 #ff6f00);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
            background: none;
            border: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }
        QScrollBar:horizontal {
            background: #2d3748;
            height: 12px;
            margin: 0;
            border-radius: 6px;
            border: 1px solid #4a5568;
        }
        QScrollBar::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff6f00,
                stop:1 #e65100);
            min-width: 20px;
            border-radius: 5px;
            margin: 1px;
        }
        QScrollBar::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e65100,
                stop:1 #ff6f00);
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0;
            background: none;
            border: none;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: transparent;
        }
    """
