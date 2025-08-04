from PySide6.QtWidgets import QWidget

def get_font_settings():
    """الحصول على إعدادات الخطوط من الملف مع دعم الأحجام المنفصلة"""
    try:
        from modules import settings
        settings_data = settings.load_settings()
        ui_settings = settings_data.get("ui_settings", {})

        # أحجام الخطوط المنفصلة
        font_size = ui_settings.get("font_size", 12)
        title_font_size = ui_settings.get("title_font_size", 18)
        menu_font_size = ui_settings.get("menu_font_size", 12)

        font_family = ui_settings.get("font_family", "النظام الافتراضي")
        font_weight = ui_settings.get("font_weight", "عادي")

        if font_family == "النظام الافتراضي":
            font_family_css = "'Segoe UI', 'Tahoma', 'Arial Unicode MS', 'Cairo', sans-serif"
        else:
            font_family_css = f"'{font_family}', 'Segoe UI', sans-serif"

        weight_map = {"عادي": "normal", "سميك": "bold", "سميك جداً": "900"}
        font_weight_css = weight_map.get(font_weight, "normal")

        return {
            "size": font_size,
            "title_size": title_font_size,
            "menu_size": menu_font_size,
            "family": font_family_css,
            "weight": font_weight_css
        }
    except:
        return {
            "size": 12,
            "title_size": 18,
            "menu_size": 12,
            "family": "'Segoe UI', 'Tahoma', 'Arial Unicode MS', 'Cairo', sans-serif",
            "weight": "normal"
        }

def get_widget_style(widget_type, colors, accent_color):
    """مولد الأنماط الموحد لجميع العناصر"""
    font_settings = get_font_settings()
    
    # --- Start of widget styles ---

    if widget_type == "main_window":
        return f"""
            QMainWindow {{ background-color: {colors["bg"]}; color: {colors["text_body"]}; }}
            QLabel {{ color: {colors["text_body"]}; background: transparent; border: none; outline: none; }}
        """

    elif widget_type in ["dialog", "settings_window", "widget"]:
        return f"""
            QDialog, QWidget {{
                background-color: {colors["bg"]};
                color: {colors["text_body"]};
                font-family: {font_settings['family']};
            }}
            QFrame {{ background-color: {colors["surface"]}; border: 1px solid {colors["border"]}; border-radius: 8px; }}
            QLabel {{ color: {colors["text_body"]}; background: transparent; border: none; outline: none; }}
            QFormLayout QLabel {{ color: {colors["text_body"]}; background: transparent; border: none; outline: none; }}
        """

    elif widget_type == "dialog_about":
        return f"""
            QDialog {{
                background-color: {darken_color(colors["bg"], 0.1)};
                border: 1px solid {colors["border"]};
                border-radius: 10px;
            }}
            QLabel {{
                color: {colors["text_body"]};
                background: transparent;
            }}
            QLabel#about_app_name {{
                font-size: {font_settings["title_size"]}px;
                font-weight: bold;
                color: {accent_color};
            }}
            QLabel#about_version {{
                font-size: {font_settings["size"]}px;
                color: {colors["text_secondary"]};
            }}
            QLabel#about_author {{
                font-size: {int(font_settings["size"] * 0.85)}px;
                color: {colors["text_muted"]};
            }}
            QFrame#about_separator {{
                background-color: {colors["border"]};
                border: none;
                height: 1px;
            }}
            QTextEdit {{
                background: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 6px;
                color: {colors["text_body"]};
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {int(font_settings["size"] * 0.8)}px;
            }}
            QTextEdit QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QTextEdit QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QTextEdit QScrollBar::handle:vertical:hover {{
                background: {darken_color(accent_color)};
            }}
            QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QTextEdit QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QTextEdit QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 4px;
                min-width: 20px;
            }}
            QTextEdit QScrollBar::handle:horizontal:hover {{
                background: {darken_color(accent_color)};
            }}
            QTextEdit QScrollBar::add-line:horizontal, QTextEdit QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
            QPushButton#about_close_button {{
                background: {accent_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton#about_close_button:hover {{
                background: {lighten_color(accent_color, 0.1)};
            }}
        """
    
    elif widget_type == "menu":
        return f"""
            QMenu, QListWidget {{
                background-color: {colors["surface"]};
                color: {colors["text_body"]};
                font-family: {font_settings['family']};
                font-size: {font_settings['menu_size']}px;
                border: 1px solid {colors["border"]};
                border-radius: 8px;
            }}
            QMenu::item, QListWidget::item {{
                color: {colors['text_body']};
                background-color: transparent;
                padding: 12px 20px;
            }}
            QMenu::item:selected, QListWidget::item:selected {{
                background-color: {accent_color};
                color: white;
                font-weight: bold;
            }}
            QMenu::item:hover, QListWidget::item:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            QMenu::item:selected:hover, QListWidget::item:selected:hover {{
                background-color: {darken_color(accent_color, 0.2)};
                color: white;
                font-weight: bold;
            }}
        """

    elif widget_type == "button":
        return f"""
            QPushButton {{
                background-color: {accent_color};
                color: {colors["text_body"]};
                border: none; border-radius: 6px; padding: 8px 16px;
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]}; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {lighten_color(accent_color, 0.2)}; }}
        """

    elif widget_type == "icon_button":
        return f"""
            QPushButton {{ background: transparent; border: none; border-radius: 4px; padding: 4px; }}
            QPushButton:hover {{ background-color: {accent_color}33; }}
            QPushButton:pressed {{ background-color: {accent_color}66; }}
        """

    elif widget_type == "frame":
        return f"""
            QFrame {{ background-color: {colors["surface"]}; border: none; border-radius: 8px; }}
        """

    elif widget_type == "slider_indicator":
        return f"""
            QFrame {{ background-color: {accent_color}; border: none; border-radius: 3px; }}
        """

    elif widget_type == "tab_button":
        return f"""
            QPushButton {{
                background: transparent;
                border: none;
                outline: none;
                font-size: {font_settings["size"]}px;
                font-weight: normal;
                padding: 15px 25px;
                color: {colors["text_body"]};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: {colors["surface"]};
            }}
            QPushButton:checked {{
                background: {colors["surface"]};
            }}
        """

    elif widget_type == "theme_separator":
        # استخراج قيم RGB من لون السمة
        if accent_color.startswith('#'):
            hex_color = accent_color[1:]
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            r, g, b = 255, 111, 0  # fallback

        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba({r}, {g}, {b}, 0.0),
                    stop:0.5 rgba({r}, {g}, {b}, 0.4),
                    stop:1 rgba({r}, {g}, {b}, 0.0));
                border: none;
            }}
        """

    elif widget_type == "separator":
         return f"""
            QFrame {{
                background-color: {colors["border"]};
                border: none;
                height: 1px;
            }}
        """

    elif widget_type == "company_name":
        return f"""
            QLabel {{
                color: {accent_color};
                font-size: {int(font_settings["size"] * 0.9)}px;
                font-weight: bold;
                background: transparent;
                border: none;
                outline: none;
            }}
        """

    elif widget_type == "label":
        return f"""
            QLabel {{
                color: {colors["text_body"]}; background: transparent;
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]}; font-weight: {font_settings["weight"]};
                border: none; outline: none;
            }}
        """

    elif widget_type == "title_text":
        return f"""
            QLabel {{
                color: {colors["text_title"]}; background: transparent;
                font-size: {font_settings["title_size"]}px; font-family: {font_settings["family"]}; font-weight: bold;
                border: none; outline: none;
            }}
        """

    elif widget_type == "text_edit":
        return f"""
            QTextEdit {{
                background-color: {colors["surface"]};
                color: {colors["text_body"]};
                border: 1px solid {colors["border"]};
                border-radius: 6px;
                padding: 8px;
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
            }}
            QTextEdit:focus {{ border: 1px solid {accent_color}; }}
        """
        
    elif widget_type == "list_widget":
        return f"""
            QListWidget {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                outline: none;
            }}
            QListWidget::item {{
                background-color: {colors["bg"]};
                border: 1px solid {colors["border"]};
                border-radius: 6px;
                padding: 10px; margin: 4px;
                color: {colors["text_body"]};
            }}
            QListWidget::item:hover {{
                background-color: {colors["surface"]};
                border: 1px solid {accent_color};
            }}
            QListWidget::item:selected {{
                background-color: {accent_color};
                border: 1px solid {darken_color(accent_color)};
                color: white; font-weight: bold;
            }}
            QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """

    elif widget_type == "compression_slider":
        return f"""
            QSlider::groove:horizontal {{
                border: 1px solid {colors['border']};
                height: 14px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00C851, stop:0.3 #00C851, stop:0.5 #ffbb33, stop:0.7 #ffbb33, stop:1 #ff4444);
                border-radius: 7px;
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #e0e0e0);
                border: 2px solid #333333;
                width: 22px; margin: -6px 0; border-radius: 11px;
            }}
            QSlider::handle:horizontal:hover {{ border: 2px solid {accent_color}; }}
            QSlider::sub-page:horizontal {{ background: transparent; border: none; }}
        """

    elif widget_type == "graphics_view":
        return f"""
            QGraphicsView, QScrollArea {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QGraphicsView > QWidget, QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """

    elif widget_type == "scrollbar":
        return f"""
            QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """

    # --- Other widget styles from original file... ---
    
    elif widget_type == "group_box":
        return f"""
            QGroupBox {{
                font-size: {font_settings["menu_size"]}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
                color: {colors.get("text_title", "white")};
                border: 1px solid {colors.get("border", "#4a5568")};
                border-radius: 8px;
                margin-top: 15px; padding-top: 15px;
                background: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 15px; padding: 0 8px;
                color: {colors.get("text_secondary", "#a0aec0")};
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]};
            }}
        """

    elif widget_type == "slider":
        return f"""
            QSlider::groove:horizontal {{ background: {colors['border']}; height: 8px; border-radius: 4px; border: 1px solid {colors['surface']}; }}
            QSlider::handle:horizontal {{ background: {accent_color}; border: 2px solid {colors['text_body']}; width: 18px; height: 18px; border-radius: 9px; margin: -6px 0; }}
            QSlider::handle:horizontal:hover {{ background: {darken_color(accent_color, -0.2)}; border: 2px solid {colors['text_accent']}; }}
            QSlider::handle:horizontal:pressed {{ background: {darken_color(accent_color, 0.2)}; border: 2px solid {colors['text_accent']}; }}
        """

    elif widget_type == "checkbox":
        return f"""
            QCheckBox {{ color: {colors['text_body']}; font-size: {font_settings["size"]}px; font-family: {font_settings["family"]}; font-weight: {font_settings["weight"]}; spacing: 8px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {colors['border']}; border-radius: 3px; background: {colors['surface']}; }}
            QCheckBox::indicator:hover {{ border: 1px solid {accent_color}; }}
            QCheckBox::indicator:checked {{ background: {accent_color}; border: 1px solid {darken_color(accent_color)}; }}
        """

    elif widget_type == "combo":
        return f"""
            QComboBox {{
                background-color: {colors['surface']}; border: 1px solid {colors['border']}; border-radius: 6px; padding: 8px; color: {colors['text_body']};
                font-size: {font_settings['size']}px; font-family: {font_settings['family']};
            }}
            QComboBox:focus, QComboBox:hover {{ border: 1px solid {accent_color}; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {colors['bg']}; border: 1px solid {colors['border']}; color: {colors['text_body']};
                selection-background-color: {accent_color};
            }}
        """

    elif widget_type == "card_colors_only":
        return f"""
            QFrame {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
            }}
            QFrame:hover {{
                border-color: {accent_color};
                background-color: {darken_color(colors["surface"], 0.1)};
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

def lighten_color(color, factor=0.2):
    """تفتيح اللون"""
    from PySide6.QtGui import QColor
    color = QColor(color)
    h, s, l, a = color.getHsl()
    l = min(255, int(l * (1 + factor)))
    color.setHsl(h, s, l, a)
    return color.name()

def apply_dynamic_font_style(widget, style_type="base"):
    """تطبيق أنماط الخطوط الديناميكية على العناصر"""
    font_settings = get_font_settings()

    style_map = {
        "base": f"font-size: {font_settings['size']}px; font-family: {font_settings['family']}; font-weight: {font_settings['weight']};",
        "title": f"font-size: {font_settings['title_size']}px; font-family: {font_settings['family']}; font-weight: bold;",
        "menu": f"font-size: {font_settings['menu_size']}px; font-family: {font_settings['family']}; font-weight: {font_settings['weight']};",
        "small": f"font-size: {int(font_settings['size'] * 0.85)}px; font-family: {font_settings['family']}; font-weight: {font_settings['weight']};",
        "large": f"font-size: {int(font_settings['size'] * 1.2)}px; font-family: {font_settings['family']}; font-weight: {font_settings['weight']};"
    }

    style = style_map.get(style_type, style_map["base"])
    current_style = widget.styleSheet()

    # إزالة أي أنماط خطوط موجودة وإضافة الجديدة
    import re
    current_style = re.sub(r'font-size:\s*[^;]+;', '', current_style)
    current_style = re.sub(r'font-family:\s*[^;]+;', '', current_style)
    current_style = re.sub(r'font-weight:\s*[^;]+;', '', current_style)

    widget.setStyleSheet(f"{current_style} {style}")
    return widget

# Keep compatibility functions if they are used elsewhere
def get_button_style(colors, accent_color):
    return get_widget_style("button", colors, accent_color)



def get_rtl_aware_scroll_style(colors, accent_color):
    """دالة للحصول على ستايل scrollbar مع دعم RTL/LTR"""
    try:
        from modules import settings
        settings_data = settings.load_settings()
        ui_settings = settings_data.get("ui_settings", {})
        language = ui_settings.get("language", "العربية")

        # نفس الستايل للآن، لكن يمكن تخصيصه لاحقاً
        return f"""
            QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """
    except:
        # في حالة حدوث خطأ، استخدم الستايل الافتراضي
        return f"""
            QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 8px;
                border-radius: 4px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {darken_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """


def get_file_list_title_style(colors, accent_color):
    """نمط عنوان قائمة الملفات"""
    font_settings = get_font_settings()
    return f"""
        QLabel#fileListTitle {{
            color: {colors["text_title"]};
            font-size: {int(font_settings["size"] * 1.2)}px;
            font-weight: bold;
            padding: 5px;
            border-bottom: 1px solid {accent_color}66;
            margin-bottom: 5px;
        }}
    """

def get_scroll_style(colors, accent_color):
    return get_widget_style("graphics_view", colors, accent_color)
