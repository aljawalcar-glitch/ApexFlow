from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor
import re

def darken_color(color, factor=0.2):
    """تغميق اللون"""
    try:
        q_color = QColor(color)
        h, s, l, a = q_color.getHsl()
        l = max(0, int(l * (1 - factor)))
        q_color.setHsl(h, s, l, a)
        return q_color.name()
    except:
        return color

def lighten_color(color, factor=0.2):
    """تفتيح اللون"""
    try:
        q_color = QColor(color)
        h, s, l, a = q_color.getHsl()
        l = min(255, int(l * (1 + factor)))
        q_color.setHsl(h, s, l, a)
        return q_color.name()
    except:
        return color

def hex_to_rgb(hex_color):
    """تحويل لون HEX إلى سلسلة RGB"""
    try:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}"
        elif len(hex_color) == 3:
            return f"{int(hex_color[0]*2, 16)}, {int(hex_color[1]*2, 16)}, {int(hex_color[2]*2, 16)}"
    except:
        pass
    return "0, 0, 0"

def get_font_settings():
    """الحصول على إعدادات الخطوط من الملف مع دعم الأحجام المنفصلة"""
    try:
        from src.utils import settings
        settings_data = settings.load_settings(force_reload=True)
        ui_settings = settings_data.get("ui_settings", {})

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
    except Exception:
        return {
            "size": 12,
            "title_size": 18,
            "menu_size": 12,
            "family": "'Segoe UI', 'Tahoma', 'Arial Unicode MS', 'Cairo', sans-serif",
            "weight": "normal"
        }

def get_widget_style(widget_type, colors, accent_color):
    """مولد الأنماط الموحد لجميع العناصر مع تأثيرات مرور متناسقة"""
    font_settings = get_font_settings()
    
    try:
        is_dark_theme = QColor(colors.get("bg", "#000000")).lightness() < 128
    except Exception:
        is_dark_theme = True
        
    hover_bg_color = "rgba(255, 255, 255, 0.08)" if is_dark_theme else "rgba(0, 0, 0, 0.04)"
    
    if widget_type == "main_window":
        return f"""
            QMainWindow {{ background-color: {colors["bg"]}; }}
            QLabel {{ background-color: transparent; border: none; outline: none; }}
            QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 10px;
                border-radius: 5px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 5px;
                min-height: 25px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {lighten_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 10px;
                border-radius: 5px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 5px;
                min-width: 25px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {lighten_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """

    elif widget_type in ["dialog", "settings_window", "widget"]:
        return f"""
            QDialog, QWidget {{
                background-color: {colors["surface"]};
                font-family: {font_settings['family']};
            }}
            QFrame {{ background-color: {colors["surface"]}; border: 1px solid {colors["border"]}; border-radius: 8px; }}
            QFormLayout QLabel {{ background: transparent; border: none; outline: none; }}
        """

    elif widget_type == "dialog_about":
        return f"""
            QDialog {{
                background-color: {darken_color(colors["bg"], 0.1)};
                border: 1px solid {colors["border"]};
                border-radius: 10px;
            }}
            QLabel {{ background: transparent; }}
            QLabel#about_app_name {{ font-size: {font_settings["title_size"]}px; font-weight: bold; color: {accent_color}; background: transparent; }}
            QLabel#about_version {{ font-size: {font_settings["size"]}px; color: {colors["text_secondary"]}; background: transparent; }}
            QLabel#about_author {{ font-size: {int(font_settings["size"] * 0.85)}px; color: {colors["text_muted"]}; background: transparent; }}
            QLabel#about_logo_label {{ 
                background: transparent; 
                border: 1px solid {colors["border"]}; 
                border-radius: 8px; 
                padding: 5px;
            }}
            QFrame#about_separator {{ background-color: rgba({hex_to_rgb(colors["border"])}, 0.5); border: none; height: 1px; }}
            QTextEdit#about_text {{
                background: {colors["surface"]}; 
                border: 1px solid {colors["border"]}; 
                border-radius: 6px;
                padding: 10px; 
                font-family: 'Consolas', 'Monaco', monospace;
                color: {colors["text_body"]};
            }}
            QTextEdit#about_text QScrollBar::handle:vertical {{ background: rgba({hex_to_rgb(accent_color)}, 0.8); border-radius: 4px; min-height: 20px; }}
            QTextEdit#about_text QScrollBar::handle:vertical:hover {{ background: rgba({hex_to_rgb(lighten_color(accent_color))}, 0.9); }}
            QTextEdit#about_text QScrollBar::add-line:vertical, QTextEdit#about_text QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
            QTextEdit#about_text QScrollBar:horizontal {{
                background: rgba({hex_to_rgb(colors["surface"])}, 0.5); height: 8px; border-radius: 4px;
                margin: 0; border: 1px solid rgba({hex_to_rgb(colors["border"])}, 0.4);
            }}
            QTextEdit#about_text QScrollBar::handle:horizontal {{ background: rgba({hex_to_rgb(accent_color)}, 0.8); border-radius: 4px; min-width: 20px; }}
            QTextEdit#about_text QScrollBar::handle:horizontal:hover {{ background: rgba({hex_to_rgb(lighten_color(accent_color))}, 0.9); }}
            QTextEdit#about_text QScrollBar::add-line:horizontal, QTextEdit#about_text QScrollBar::sub-line:horizontal {{ width: 0; background: none; }}
            QPushButton#about_update_button {{
                background: transparent; color: rgba({hex_to_rgb(accent_color)}, 0.9); border: 1px solid rgba({hex_to_rgb(accent_color)}, 0.7); border-radius: 6px;
                padding: 8px 16px; font-weight: bold;
            }}
            QPushButton#about_update_button:hover {{ background: rgba({hex_to_rgb(hover_bg_color)}, 0.7); }}
            QPushButton#about_update_button:disabled {{ background: rgba({hex_to_rgb(colors["surface"])}, 0.5); color: rgba({hex_to_rgb(colors["text_muted"])}, 0.7); border-color: rgba({hex_to_rgb(colors["border"])}, 0.5); }}
            QPushButton#about_close_button {{
                background: rgba({hex_to_rgb(accent_color)}, 0.9); color: rgba(255, 255, 255, 0.95); border: none; border-radius: 6px;
                padding: 8px 16px; font-weight: bold;
            }}
            QPushButton#about_close_button:hover {{ background: rgba({hex_to_rgb(lighten_color(accent_color, 0.1))}, 0.95); }}
        """
    
    elif widget_type == "menu":
        return f"""
            QMenu, QListWidget {{
                background-color: {colors["surface"]}; color: {colors["text_body"]};
                font-family: {font_settings['family']}; font-size: {font_settings['menu_size']}px;
                border: 1px solid {colors["border"]}; border-radius: 8px;
            }}
            QMenu::item, QListWidget::item {{
                color: {colors['text_body']}; background-color: transparent; padding: 12px 20px;
            }}
            QMenu::item:selected, QListWidget::item:selected {{
                background-color: {accent_color}; color: white; font-weight: bold;
            }}
            QMenu::item:hover, QListWidget::item:hover {{
                background-color: {hover_bg_color}; border-left: 3px solid {accent_color};
            }}
            QMenu::item:selected:hover, QListWidget::item:selected:hover {{
                background-color: {lighten_color(accent_color, 0.1)}; color: white; font-weight: bold;
            }}
        """

    elif widget_type == "button":
        button_text_color = "#ffffff" if not is_dark_theme else colors["text_body"]
        return f"""
            QPushButton {{
                background-color: {accent_color}; color: {button_text_color};
                border: none; border-radius: 6px; padding: 8px 16px;
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]}; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {lighten_color(accent_color, 0.2)}; }}
            QPushButton:pressed {{ background-color: {darken_color(accent_color, 0.1)}; }}
        """

    elif widget_type in ["quick_start_button_split", "quick_start_button_compress"]:
        return f"""
            QPushButton {{
                background-color: transparent; color: {accent_color};
                border: 1px solid {accent_color}; border-radius: 6px; padding: 8px 16px;
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]}; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {hover_bg_color}; }}
            QPushButton:pressed {{ background-color: {accent_color}66; }}
        """

    elif widget_type == "icon_button":
        return f"""
            QPushButton {{ background: transparent; border: none; border-radius: 4px; padding: 4px; }}
            QPushButton:hover {{ background-color: {hover_bg_color}; }}
            QPushButton:pressed {{ background-color: {accent_color}66; }}
            QPushButton[update_available="true"] {{
                border: 1px solid #4CAF50;
            }}
            QPushButton[update_available="true"]:hover {{
                background: rgba(76, 175, 80, 0.2);
            }}
        """
    
    elif widget_type == "about_info_button":
        return f"""
            QPushButton {{ 
                background: transparent; 
                border: 1px solid {colors["border"]}; 
                border-radius: 4px; 
                padding: 4px;
                color: {colors["text_secondary"]};
            }}
            QPushButton:hover {{ 
                background-color: {hover_bg_color}; 
                border-color: {accent_color};
                color: {accent_color};
            }}
            QPushButton:pressed {{ 
                background-color: {accent_color}33; 
                border-color: {accent_color};
            }}
        """

    elif widget_type == "app_info_widget":
        if accent_color.startswith('#'):
            hex_color = accent_color[1:]
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        else:
            r, g, b = 255, 111, 0
        return f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({r}, {g}, {b}, 0.02),
                    stop:1 rgba({r}, {g}, {b}, 0.05));
                border: none;
                border-radius: 8px;
                margin: 2px;
            }}
        """

    elif widget_type == "frame":
        return f"""
            QFrame {{ background-color: {colors["surface"]}; border: 1px solid {colors["border"]}; border-radius: 8px; }}
            QFrame:hover {{ border: 1px solid {accent_color}; }}
        """

    elif widget_type == "features_frame":
        return f"""
            QFrame {{
                background-color: {colors["surface"]};
                border: none;
                border-radius: 12px;
            }}
        """
    elif widget_type == "step_indicator":
        return f"""
            QWidget {{
                background-color: transparent;
                border-bottom: 1px solid {colors["border"]};
            }}
        """
    elif widget_type == "notification_bar":
        bg_color_q = QColor(colors.get("surface", "#2D3748"))
        bg_color_q.setAlpha(220)
        return f"""
            QFrame#NotificationBar {{
                background-color: {bg_color_q.name(QColor.NameFormat.HexArgb)};
                border-radius: 8px;
                margin: 0 5px 5px 5px;
                border: 1px solid {colors["border"]};
            }}
        """
    elif widget_type == "notification_text":
        return f"""
            QLabel {{
                color: {colors["text_body"]};
                background-color: transparent;
                border: none;
            }}
        """
    elif widget_type == "notification_close_button":
        return f"""
            QPushButton {{
                color: {colors["text_secondary"]};
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_bg_color};
                color: {colors["text_body"]};
            }}
        """

    elif widget_type == "slider_indicator":
        return f"""
            QFrame {{ background-color: {accent_color}; border: none; border-radius: 3px; }}
        """

    elif widget_type == "tab_button":
        return f"""
            QPushButton {{
                background: transparent; border: none; outline: none;
                font-size: {font_settings["size"]}px; font-weight: normal;
                padding: 15px 25px; color: {colors["text_body"]}; border-radius: 8px;
            }}
            QPushButton:hover {{ background: {lighten_color(accent_color, 0.8)}; }}
            QPushButton:checked {{ background: {accent_color}; color: white; }}
        """

    elif widget_type == "theme_separator":
        if accent_color.startswith('#'):
            hex_color = accent_color[1:]
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        else:
            r, g, b = 255, 111, 0
        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba({r}, {g}, {b}, 0.0), stop:0.5 rgba({r}, {g}, {b}, 0.4), stop:1 rgba({r}, {g}, {b}, 0.0));
                border: none;
            }}
        """

    elif widget_type == "separator":
         return f"""
            QFrame {{ background-color: {colors["border"]}; border: none; height: 1px; }}
        """

    elif widget_type == "company_name":
        return f"""
            QLabel {{
                color: {accent_color}; font-size: {int(font_settings["size"] * 0.9)}px; font-weight: bold;
                background: transparent; border: none; outline: none;
            }}
        """

    elif widget_type == "version_label":
        return f"""
            QLabel {{
                color: {colors["text_muted"]};
                font-size: 10px;
                background: transparent;
            }}
        """

    elif widget_type == "author_label":
        return f"""
            QLabel {{
                color: {darken_color(colors["text_muted"])};
                font-size: 9px;
                background: transparent;
            }}
        """

    elif widget_type == "label":
        return f"""
            QLabel {{
                color: {colors["text_body"]}; background: transparent;
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]}; font-weight: {font_settings["weight"]};
                border: none;
                outline: none;
                padding: 0px;
                margin: 0px;
            }}
            QLabel.section_label:hover, QLabel.title_label:hover {{ color: {accent_color}; }}
        """

    elif widget_type == "error_label":
        return f"""
            QLabel {{ color: #ff6b6b; padding: 20px; background: transparent; }}
        """

    elif widget_type == "section_label":
        return f"""
            QLabel {{
                color: {colors["text_title"]};
                background-color: transparent;
                font-size: {int(font_settings["size"] * 1.2)}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
                border: none;
                outline: none;
                margin-top: 10px;
                margin-bottom: 5px;
            }}
        """

    elif widget_type == "title_text":
        return f"""
            QLabel {{
                color: {colors["text_title"]}; 
                background-color: transparent;
                font-size: {font_settings["title_size"]}px; 
                font-family: {font_settings["family"]}; 
                font-weight: bold;
                border: none; 
                outline: none;
            }}
        """

    elif widget_type == "text_edit":
        return f"""
            QTextEdit, QLineEdit {{
                background-color: transparent; color: {colors["text_body"]};
                border: none; border-radius: 6px; padding: 8px;
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]};
                selection-background-color: {accent_color}; selection-color: white;
            }}
            QTextEdit:focus, QTextEdit:hover, QLineEdit:focus, QLineEdit:hover {{ border: none; }}
        """

    elif widget_type == "text_edit_with_frame":
        return f"""
            QLineEdit, QTextEdit {{
                background-color: {colors["surface"]}; color: {colors["text_body"]};
                border: 1px solid {colors["border"]}; border-radius: 6px; padding: 8px;
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]};
                selection-background-color: {accent_color}; selection-color: white;
            }}
            QLineEdit:focus, QTextEdit:focus, QLineEdit:hover, QTextEdit:hover {{
                border: 1px solid {accent_color};
            }}
        """

    elif widget_type == "text_browser":
        return f"""
            QTextBrowser {{
                background-color: transparent; color: {colors["text_body"]}; border: none;
                border-radius: 0px; padding: 0px; font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                selection-background-color: {accent_color}; selection-color: white;
            }}
            QTextBrowser:focus {{ border: none; }}
        """
        
    elif widget_type == "list_widget":
        return f"""
            QListWidget {{
                background-color: {colors["surface"]}; border: 1px solid {colors["border"]};
                border-radius: 8px; outline: none;
            }}
            QListWidget::item {{
                background-color: {colors["bg"]}; border: 1px solid {colors["border"]};
                border-radius: 6px; padding: 10px; margin: 4px; color: {colors["text_body"]};
            }}
            QListWidget::item:hover {{
                background-color: {hover_bg_color}; border: 1px solid {accent_color};
            }}
            QListWidget::item:selected {{
                background-color: {accent_color}; border: 1px solid {darken_color(accent_color)};
                color: white; font-weight: bold;
            }}
        """

    elif widget_type == "compression_slider":
        return f"""
            QSlider::groove:horizontal {{
                border: 1px solid {colors['border']}; height: 14px; border-radius: 7px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00C851, stop:0.5 #ffbb33, stop:1 #ff4444);
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #e0e0e0);
                border: 2px solid #333333; width: 22px; margin: -6px 0; border-radius: 11px;
            }}
            QSlider::handle:horizontal:hover {{ border: 2px solid {accent_color}; }}
            QSlider::sub-page:horizontal {{ background: transparent; border: none; }}
        """

    elif widget_type in ["graphics_view", "scroll_area", "scrollbar"]:
        return f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollArea > QWidget {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: {colors["surface"]};
                width: 10px;
                border-radius: 5px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 5px;
                min-height: 25px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {lighten_color(accent_color)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {colors["surface"]};
                height: 10px;
                border-radius: 5px;
                margin: 0;
                border: 1px solid {colors["border"]};
            }}
            QScrollBar::handle:horizontal {{
                background: {accent_color};
                border-radius: 5px;
                min-width: 25px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {lighten_color(accent_color)};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """

    elif widget_type == "rotate_page_view":
        return f"""
            QGraphicsView {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QScrollBar:vertical {{
                background: rgba(45, 55, 72, 0.3);
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.4);
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(255, 255, 255, 0.6);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: rgba(45, 55, 72, 0.3);
                height: 8px;
                border-radius: 4px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: rgba(255, 255, 255, 0.4);
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: rgba(255, 255, 255, 0.6);
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                background: none;
            }}
        """

    elif widget_type == "hlayout":
        return f"""
            QWidget {{
                background: transparent;
                color: {colors["text_body"]};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
            }}
            QLabel {{
                background: transparent;
                color: {colors["text_body"]};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
            }}
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {lighten_color(accent_color, 0.2)}; }}
            QPushButton:pressed {{ background-color: {darken_color(accent_color, 0.1)}; }}
        """

    elif widget_type == "group_box":
        return f"""
            QGroupBox {{
                font-size: {font_settings["menu_size"]}px; font-family: {font_settings["family"]}; font-weight: bold;
                color: {colors.get("text_title", "white")};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: {colors["surface"]};
            }}
            QGroupBox:hover {{
                border: 1px solid {accent_color};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: {colors.get("text_secondary", "#a0aec0")};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
            }}
            QGroupBox QSlider {{
                border: none;
                outline: none;
                background: transparent;
            }}
        """

    elif widget_type == "slider":
        return f"""
            QSlider {{
                border: none !important;
                outline: none !important;
                background: transparent !important;
            }}
            QSlider::groove:horizontal {{
                background: {colors['border']} !important;
                height: 8px !important;
                border-radius: 4px !important;
                border: none !important;
                outline: none !important;
            }}
            QSlider::handle:horizontal {{
                background: {accent_color} !important;
                border: none !important;
                outline: none !important;
                width: 18px !important;
                height: 18px !important;
                border-radius: 9px !important;
                margin: -6px 0 !important;
            }}
            QSlider::handle:horizontal:hover {{
                background: {lighten_color(accent_color, 0.2)} !important;
                border: none !important;
                outline: none !important;
            }}
            QSlider::handle:horizontal:pressed {{
                background: {darken_color(accent_color, 0.2)} !important;
                border: none !important;
                outline: none !important;
            }}
            QSlider::sub-page:horizontal {{
                background: transparent !important;
                border: none !important;
                outline: none !important;
            }}
            QSlider::add-page:horizontal {{
                background: transparent !important;
                border: none !important;
                outline: none !important;
            }}
        """

    elif widget_type == "checkbox":
        return f"""

        """

    elif widget_type == "spin_box":
        return f"""
            QSpinBox {{
                background-color: {colors['surface']}; border: 1px solid {colors['border']}; border-radius: 6px; 
                padding: 6px 8px; color: {colors['text_body']}; font-size: {font_settings['size']}px; 
                font-family: {font_settings['family']}; min-width: 60px;
            }}
            QSpinBox:focus, QSpinBox:hover {{ border: 1px solid {accent_color}; }}
            QSpinBox::up-button, QSpinBox::down-button {{ border: none; width: 16px; background: transparent; }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {hover_bg_color}; }}
            QSpinBox::up-arrow {{ image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 4px solid {colors['text_body']}; width: 0; height: 0; }}
            QSpinBox::down-arrow {{ image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 4px solid {colors['text_body']}; width: 0; height: 0; }}
            QSpinBox::up-arrow:hover, QSpinBox::down-arrow:hover {{ border-bottom-color: {accent_color}; border-top-color: {accent_color}; }}
        """

    elif widget_type == "combo":
        return f"""
            QComboBox {{
                background-color: {colors['surface']}; border: 1px solid {colors['border']}; border-radius: 6px; 
                padding: 8px; color: {colors['text_body']}; font-size: {font_settings['size']}px; font-family: {font_settings['family']};
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
            QFrame {{ background-color: {colors["surface"]}; border: 1px solid {colors["border"]}; }}
            QFrame:hover {{ border-color: {accent_color}; background-color: {hover_bg_color}; }}
        """

    elif widget_type == "feature_card":
        return f"""
            QFrame {{
                background-color: {colors["surface"]};
                border-radius: 12px;
                padding: 16px;
                border: 2px solid {colors["border"]};
                border-style: solid;
            }}
            QFrame:hover {{
                border: 2px solid {accent_color};
                background-color: {lighten_color(colors["surface"], 0.05)};
                border-style: solid;
            }}
        """

    elif widget_type == "feature_card_title":
        return f"""
            QLabel {{
                background: transparent;
                color: {colors["text_title"]};
                font-weight: bold;
                font-size: {font_settings["size"]}px;
            }}
        """

    elif widget_type == "feature_card_desc":
        return f"""
            QLabel {{
                background: transparent;
                color: {colors["text_secondary"]};
                font-size: {int(font_settings['size'] * 0.9)}px;
            }}
        """

    elif widget_type == "tab_widget":
        return f"""
            QTabWidget::pane {{ border: none; background: {colors["surface"]}; border-radius: 6px; }}
            QTabBar::tab {{
                background: {colors["surface"]}; color: {colors["text_body"]}; border: none;
                border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px;
                padding: 8px 16px; margin-right: 2px;
            }}
            QTabBar::tab:selected {{ background: {accent_color}; color: white; border-color: {darken_color(accent_color)}; }}
            QTabBar::tab:hover:!selected {{ background: {hover_bg_color}; color: {colors.get("text_accent", accent_color)}; border-bottom: 2px solid {accent_color}; }}
        """
    
    elif widget_type == "tree_widget":
        return f"""
            QTreeWidget {{
                background-color: {colors["surface"]}; alternate-background-color: {colors["surface"]};
                border: 1px solid {colors["border"]}; border-radius: 6px; color: {colors["text_body"]};
            }}
            QTreeWidget::item {{ border-bottom: 1px solid {colors["border"]}; padding: 4px; }}
            QTreeWidget::item:selected {{ background-color: {accent_color}; color: white; }}
            QTreeWidget::item:hover {{ background-color: {hover_bg_color}; border-left: 3px solid {accent_color}; }}
        """

    elif widget_type in ["transparent_widget", "transparent_container"]:
        return "background: transparent; border: none; margin: 0px; padding: 0px;"

    elif widget_type == "transparent_button":
        return f"""
            QPushButton {{
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg_color};
            }}
            QPushButton:pressed {{
                background-color: {accent_color}66;
            }}
        """

    elif widget_type == "warning_button":
        return get_special_button_style("255, 193, 7")

    elif widget_type == "success_button":
        return get_special_button_style("40, 167, 69")

    elif widget_type == "danger_button":
        return get_special_button_style("220, 53, 69")

    elif widget_type in ["quick_start_button_compress", "quick_start_button_split", "quick_start_button_merge"]:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {accent_color};
                border: 1px solid {accent_color};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_bg_color};
            }}
            QPushButton:pressed {{
                background-color: {accent_color}66;
            }}
        """

    elif widget_type == "changes_report_label":
        text_color_q = QColor(colors.get('text', '#ffffff'))
        return f"""
            QLabel {{
                font-size: {int(font_settings['size'] * 0.9)}px;
                line-height: 1.6;
                padding: 15px;
                background: rgba({text_color_q.red()}, {text_color_q.green()}, {text_color_q.blue()}, 0.05);
                border: none;
                border-radius: 6px;
                color: {colors.get('text_body', '#ffffff')};
            }}
        """
    
    elif widget_type == "value_label":
        return f"""
            QLabel {{
                color: {colors["text_body"]}; 
                background: transparent;
                font-size: {font_settings["size"]}px; 
                font-family: {font_settings["family"]}; 
                font-weight: {font_settings["weight"]};
                border: none;
                outline: none;
                padding: 0px;
                margin: 0px;
                min-width: 30px;
                text-align: center;
            }}
        """
    
    elif widget_type == "preview_label":
        return f"""
            QLabel {{
                color: {colors["text_body"]}; 
                background: transparent;
                font-size: {font_settings["size"]}px; 
                font-family: {font_settings["family"]}; 
                font-weight: {font_settings["weight"]};
                border: none !important;
                outline: none !important;
                padding: 15px;
                margin: 0px;
                text-align: center;
            }}
        """
    
    elif widget_type == "blur_background":
        return f"""
            QWidget {{
                background-color: rgba(0, 0, 0, 0.7);
            }}
        """
    
    elif widget_type == "smart_drop_card":
        return f"""
            QFrame {{
                background-color: {colors["surface"]};
                border: 2px solid {colors["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """
    
    elif widget_type == "smart_drop_title":
        return f"""
            QLabel {{
                color: {colors["text_title"]};
                font-size: {int(font_settings["title_size"] * 1.2)}px;
                font-family: {font_settings["family"]};
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """
    
    elif widget_type == "smart_drop_description":
        return f"""
            QLabel {{
                color: {colors["text_secondary"]};
                font-size: {font_settings["size"]}px;
                font-family: {font_settings["family"]};
                background: transparent;
                border: none;
            }}
        """
    
    elif widget_type == "thumbnails_frame":
        return f"""
            QFrame {{
                background: transparent;
                border: none;
            }}
        """
    
    elif widget_type == "thumbnail_container":
        return f"""
            QFrame {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
            }}
        """
    
    elif widget_type == "thumbnail_label":
        return f"""
            QLabel {{
                background: transparent;
                color: {colors["text_body"]};
                border: none;
            }}
        """
    
    elif widget_type == "thumbnail_name_label":
        return f"""
            QLabel {{
                color: {colors["text_body"]};
                font-size: {int(font_settings["size"] * 0.8)}px;
                background: transparent;
                border: none;
            }}
        """
    
    elif widget_type == "delete_button":
        return f"""
            QPushButton {{
                background-color: rgba(255, 0, 0, 0.8);
                border: none;
                border-radius: 11px;
                color: white;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 0, 0, 1.0);
            }}
        """
    
    elif widget_type == "cancel_button":
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {colors["text_secondary"]};
                border: 1px solid {colors["border"]};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: {font_settings["size"]}px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg_color};
                border-color: {accent_color};
                color: {colors["text_body"]};
            }}
        """
        
    else:
        return f"""
            QWidget {{
                background-color: {colors["bg"]}; color: {colors["text_body"]};
                font-size: {font_settings["size"]}px; font-family: {font_settings["family"]};
                font-weight: {font_settings["weight"]};
            }}
        """

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
    
    current_style = re.sub(r'font-size:\s*[^;]+;', '', current_style)
    current_style = re.sub(r'font-family:\s*[^;]+;', '', current_style)
    current_style = re.sub(r'font-weight:\s*[^;]+;', '', current_style)
    
    widget.setStyleSheet(f"{current_style} {style}")
    return widget

def get_button_style(colors, accent_color):
    return get_widget_style("button", colors, accent_color)

def get_rtl_aware_scroll_style(colors, accent_color):
    """دالة للحصول على ستايل scrollbar مع دعم RTL/LTR"""
    return get_widget_style("scrollbar", colors, accent_color)

def get_file_list_title_style(colors, accent_color):
    """نمط عنوان قائمة الملفات"""
    font_settings = get_font_settings()
    return f"""
        QLabel#fileListTitle {{
            color: {colors["text_title"]};
            font-size: {int(font_settings["size"] * 1.2)}px;
            font-weight: bold;
            padding: 5px;
            background: transparent;
            border: none;
            margin-bottom: 5px;
        }}
    """

def get_scroll_style(colors, accent_color):
    return get_widget_style("scroll_area", colors, accent_color)

def get_special_button_style(rgb_color="40, 167, 69"):
    """Helper function to create styles for special buttons."""
    return f"""
        QPushButton {{
            background-color: rgba({rgb_color}, 0.8);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: rgba({rgb_color}, 1.0);
        }}
        QPushButton:pressed {{
            background-color: rgba({rgb_color}, 0.7);
        }}
    """
