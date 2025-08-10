# -*- coding: utf-8 -*-
"""
الطبقة الذكية للسحب والإفلات داخل النافذة الرئيسية، بتصميم عصري ومتكامل مع السمات.
يدعم أنواع مختلفة من الملفات والمجلدات مع وضعيات (modes) ديناميكية.
"""
import os
import mimetypes
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QPushButton, QGraphicsDropShadowEffect,
                               QScrollArea, QGraphicsBlurEffect, QGridLayout)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QRect, QSize
from PySide6.QtGui import QColor, QPixmap, QDragEnterEvent, QDropEvent, QIcon

from .svg_icon_button import load_svg_icon
from modules.translator import tr
from .theme_manager import global_theme_manager
from .pdf_worker import global_worker_manager
from modules.page_settings import page_settings
from modules import settings

class FileThumbnailCard(QWidget):
    """بطاقة مصغرة لعرض ملف مع صورته واسمه وزر حذف، مع تأثيرات حركية."""
    file_deleted = Signal(str)

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setFixedSize(90, 120)
        self.setContentsMargins(0, 0, 0, 0)

        # الرسوم المتحركة
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.OutCubic)

        # الهيكل الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # حاوية الصورة المصغرة (للسماح بتراكب زر الحذف)
        self.thumbnail_container = QFrame()
        self.thumbnail_container.setObjectName("thumbnailContainer")
        self.thumbnail_container.setFixedSize(80, 80)
        container_layout = QVBoxLayout(self.thumbnail_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setObjectName("thumbnailLabel")
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.thumbnail_label)

        # زر الحذف مع أيقونة
        self.delete_button = QPushButton()
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.setFixedSize(22, 22)
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(self.delete_file)
        self.delete_button.setParent(self.thumbnail_container)
        self.delete_button.hide()  # إخفاء مبدئي

        # العنوان
        self.name_label = QLabel(os.path.basename(file_path))
        self.name_label.setObjectName("thumbnailNameLabel")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)

        # إضافة المكونات إلى الهيكل
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.thumbnail_container)
        h_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.name_label)
        
        self.animate_in()

    def update_delete_button_icon(self, color):
        """تحديث أيقونة زر الحذف."""
        icon = load_svg_icon("assets/icons/default/trash-2.svg", 16, color)
        if icon:
            self.delete_button.setIcon(icon)
            self.delete_button.setIconSize(QSize(16, 16))

    def enterEvent(self, event):
        """حدث عند دخول الفأرة."""
        self.delete_button.show()
        
        # لا نستخدم الحركة حاليا لتجنب التعارض مع ال layout
        # start_rect = self.geometry()
        # end_rect = QRect(start_rect.x() - 2, start_rect.y() - 2, start_rect.width() + 4, start_rect.height() + 4)
        
        # self.scale_animation.setStartValue(start_rect)
        # self.scale_animation.setEndValue(end_rect)
        # self.scale_animation.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        """حدث عند خروج الفأرة."""
        self.delete_button.hide()
        
        # لا نستخدم الحركة حاليا لتجنب التعارض مع ال layout
        # start_rect = self.geometry()
        # end_rect = QRect(start_rect.x() + 2, start_rect.y() + 2, start_rect.width() - 4, start_rect.height() - 4)
        
        # self.scale_animation.setStartValue(start_rect)
        # self.scale_animation.setEndValue(end_rect)
        # self.scale_animation.start()
        
        super().leaveEvent(event)

    def resizeEvent(self, event):
        """تحديث موقع زر الحذف عند تغيير الحجم."""
        super().resizeEvent(event)
        # وضع الزر في الزاوية العلوية اليمنى
        self.delete_button.move(self.thumbnail_container.width() - self.delete_button.width() - 2, 2)

    def animate_in(self):
        """تأثير الدخول للبطاقة."""
        self.setWindowOpacity(0.0)
        self.anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.anim_in.setDuration(250)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.OutCubic)
        self.anim_in.start()

    def delete_file(self):
        """بدء تأثير الخروج ثم إرسال إشارة الحذف عند الانتهاء."""
        if not hasattr(self, 'anim_out'):
            self.anim_out = QPropertyAnimation(self, b"windowOpacity")
            self.anim_out.setDuration(250)
            self.anim_out.setEasingCurve(QEasingCurve.InCubic)
            self.anim_out.finished.connect(self._on_animation_finished)
        
        self.delete_button.setEnabled(False)
        self.anim_out.setStartValue(self.windowOpacity())
        self.anim_out.setEndValue(0.0)
        self.anim_out.start()

    def _on_animation_finished(self):
        """عندما تنتهي حركة الاختفاء، يتم إرسال الإشارة."""
        self.file_deleted.emit(self.file_path)

    def set_thumbnail(self, pixmap):
        self.thumbnail_label.setPixmap(pixmap)

    def set_placeholder_style(self, colors):
        delete_button_style = f"""
            QPushButton#deleteButton {{
                background-color: rgba(239, 68, 68, 0.85);
                border-radius: 11px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            QPushButton#deleteButton:hover {{
                background-color: rgba(239, 68, 68, 1);
            }}
        """
        self.delete_button.setStyleSheet(delete_button_style)
        self.update_delete_button_icon("white")

        self.thumbnail_container.setStyleSheet(f"""
            #thumbnailContainer {{
                background-color: {colors.get("bg", "#1a202c")};
                border: 1px dashed {colors.get("border", "#4a5568")};
                border-radius: 8px;
            }}
        """)
        self.thumbnail_label.setStyleSheet(f"""
            QLabel#thumbnailLabel {{
                color: {colors.get("text_muted", "#718096")};
                border: none;
                background: transparent;
            }}
        """)
        self.name_label.setStyleSheet(f"""
            QLabel#thumbnailNameLabel {{
                color: {colors.get("text_secondary", "#a0aec0")};
                font-size: 9px;
            }}
        """)
        self.thumbnail_label.setText(tr("loading_placeholder"))


class SmartDropOverlay(QWidget):
    """طبقة ذكية للسحب والإفلات بتصميم عصري ومتكامل مع السمات.
    
    يدعم الوضعيات المختلفة:
    - 'folder': يقبل فقط المجلدات
    - 'image': يقبل فقط الصور
    - 'pdf_or_txt': يقبل ملفات PDF أو TXT فقط
    - 'single_file': يقبل ملفًا واحدًا فقط
    - 'conditional_folder': يقبل مجلدات فقط إن كان شرط معين محققًا
    - 'multiple_files': يقبل عدد محدد من الملفات
    """

    action_selected = Signal(str, list)
    cancelled = Signal()

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setParent(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()

        self.setAcceptDrops(True)
        
        self.files = []
        self.current_context = 'welcome'
        self.page_title = tr("menu_home")
        self.is_valid_drop = False
        self.thumbnail_widgets = {}

        # متغيرات للتأثيرات الانتقالية
        self.fade_animation = None
        self.scale_animation = None

        self.setup_ui()
        global_theme_manager.theme_changed.connect(self.update_styles)
        self.update_styles()

    def setup_ui(self):
        """إنشاء واجهة المستخدم بالهيكل الجديد مع طبقة بلور صحيحة."""
        # تعيين الطبقة الرئيسية لتغطي النافذة بالكامل
        self.setStyleSheet("background: transparent;")

        # استخدام QGridLayout للسماح بتداخل الطبقات
        full_layout = QGridLayout(self)
        full_layout.setContentsMargins(0, 0, 0, 0)
        full_layout.setSpacing(0)

        # طبقة الخلفية الضبابية التي تغطي النافذة بالكامل
        self.blur_background = QWidget()
        self.blur_background.setObjectName("blurBackground")
        self.blur_background.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        full_layout.addWidget(self.blur_background, 0, 0)

        # طبقة المحتوى (البطاقة) فوق الطبقة الضبابية
        content_widget = QWidget()
        content_widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addStretch()

        self.main_card = QFrame()
        self.main_card.setObjectName("smartDropCard")
        self.main_card.setMinimumSize(500, 450)
        self.main_card.setMaximumSize(600, 550)

        # تطبيق تأثير الظل على البطاقة
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        self.main_card.setGraphicsEffect(shadow)

        card_h_layout = QHBoxLayout()
        card_h_layout.addStretch()
        card_h_layout.addWidget(self.main_card)
        card_h_layout.addStretch()

        content_layout.addLayout(card_h_layout)
        content_layout.addStretch()

        full_layout.addWidget(content_widget, 0, 0)

        # إعداد محتويات البطاقة
        self.setup_card_content()

    def setup_card_content(self):
        """إعداد محتويات البطاقة الرئيسية."""
        card_layout = QVBoxLayout(self.main_card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)

        # أيقونة كبيرة في الأعلى
        self.icon_label = QLabel()
        self.icon_label.setObjectName("smartDropIcon")
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setAlignment(Qt.AlignCenter)
        
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(self.icon_label)
        icon_layout.addStretch()
        card_layout.addLayout(icon_layout)

        # العنوان
        self.title_label = QLabel()
        self.title_label.setObjectName("smartDropTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        card_layout.addWidget(self.title_label)

        # الوصف
        self.description_label = QLabel()
        self.description_label.setObjectName("smartDropDescription")
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setWordWrap(True)
        card_layout.addWidget(self.description_label)

        # أيقونة الإسقاط الكبيرة
        self.drop_icon_label = QLabel()
        self.drop_icon_label.setObjectName("smartDropLargeIcon")
        self.drop_icon_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.drop_icon_label)

        # حاوية الخيارات
        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(10)
        card_layout.addLayout(self.options_layout)
        card_layout.addStretch(1)

        # منطقة عرض الصور المصغرة
        self.thumbnails_scroll_area = QScrollArea()
        self.thumbnails_scroll_area.setObjectName("thumbnailsScrollArea")
        self.thumbnails_scroll_area.setWidgetResizable(True)
        self.thumbnails_scroll_area.setFixedHeight(140)
        
        self.thumbnails_widget = QWidget()
        self.thumbnails_layout = QHBoxLayout(self.thumbnails_widget)
        self.thumbnails_layout.setAlignment(Qt.AlignLeft)
        self.thumbnails_scroll_area.setWidget(self.thumbnails_widget)
        
        card_layout.addWidget(self.thumbnails_scroll_area)
        card_layout.addStretch(1)

        # زر الإلغاء
        self.cancel_button = QPushButton(tr("cancel_button"))
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.cancel)
        card_layout.addWidget(self.cancel_button)

    def update_styles(self):
        """تحديث الأنماط بناءً على السمة الحالية."""
        colors = global_theme_manager.get_current_colors()
        accent = global_theme_manager.current_accent
        
        from .global_styles import get_font_settings, lighten_color, darken_color
        font_settings = get_font_settings()

        is_dark = QColor(colors.get("bg", "#000000")).lightness() < 128
        cancel_bg = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.05)"
        cancel_hover_bg = "rgba(255, 255, 255, 0.15)" if is_dark else "rgba(0, 0, 0, 0.1)"

        stylesheet = f"""
            QWidget#blurBackground {{
                background-color: rgba(0, 0, 0, 0.6);
                border: none;
            }}
            QFrame#smartDropCard {{
                background-color: {colors.get("surface", "#2d3748")};
                border: 2px dashed {accent if self.is_valid_drop else "rgba(255, 80, 80, 0.8)"};
                border-radius: 16px;
            }}
            QLabel#smartDropTitle {{
                color: {colors.get("text_title", "white")};
                font-family: {font_settings['family']};
                font-size: {font_settings['title_size']}px;
                font-weight: bold;
            }}
            QLabel#smartDropDescription {{
                color: {colors.get("text_secondary", "#a0aec0")};
                font-family: {font_settings['family']};
                font-size: {font_settings['size']}px;
            }}
            QPushButton.optionButton {{
                background-color: {accent};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-family: {font_settings['family']};
                font-size: {font_settings['size']}px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton.optionButton:hover {{
                background-color: {lighten_color(accent, 0.15)};
            }}
            QPushButton#cancelButton {{
                background-color: {cancel_bg};
                color: {colors.get("text_body", "white")};
                border: 1px solid {colors.get("border", "#4a5568")};
                border-radius: 8px;
                padding: 10px;
                font-family: {font_settings['family']};
                font-size: {font_settings['size']}px;
                font-weight: normal;
            }}
            QPushButton#cancelButton:hover {{
                background-color: {cancel_hover_bg};
                border-color: {colors.get("text_secondary", "#a0aec0")};
            }}
            QScrollArea#thumbnailsScrollArea {{
                background-color: transparent;
                border: 1px solid {colors.get("border", "#4a5568")};
                border-radius: 8px;
            }}
            QScrollBar:horizontal {{
                background: {colors.get("surface", "#2d3748")};
                height: 10px;
                margin: 0px 15px 0 15px;
                border: 1px solid {colors.get("border", "#4a5568")};
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: {accent};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
            }}
        """
        self.setStyleSheet(stylesheet)
        self.update_icon_color()
        # تحديث نمط البطاقات الموجودة
        for card in self.thumbnail_widgets.values():
            card.set_placeholder_style(colors)

    def update_icon_color(self):
        """تحديث لون الأيقونة بناءً على السياق والسمة."""
        colors = global_theme_manager.get_current_colors()
        icon_color = colors.get("text_accent", "#056a51")
        
        icon_name = "file-text"
        context_map = {
            'welcome': 'logo', 'merge': 'merge', 'split': 'scissors',
            'compress': 'archive', 'rotate': 'rotate-cw', 'convert': 'file-text',
            'security': 'settings', 'help': 'info', 'settings': 'settings'
        }
        icon_name = context_map.get(self.current_context, "file-text")
            
        icon = load_svg_icon(f"assets/icons/default/{icon_name}.svg", 64, icon_color)
        if icon:
            self.icon_label.setPixmap(icon)

    def update_context(self, context, title):
        """تحديث السياق والعنوان بناءً على الصفحة الحالية."""
        # تحديث السياق
        self.current_context = context
        self.page_title = title
        self.update_ui_for_context()
        
    def update_page_settings(self, settings):
        """تحديث إعدادات الصفحة الحالية في واجهة الإسقاط"""
        # تحديث إعدادات الصفحة
        self.current_page_settings = settings
        # يمكن إضافة المزيد من المنطق هنا حسب الحاجة
        
    def animate_show(self):
        """Show the overlay with a smooth transition effect."""
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        # Fade in the overlay
        fade_in = QPropertyAnimation(self, b"windowOpacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.OutCubic)

        # Scale up the card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        self.main_card.setGraphicsEffect(shadow)
        
        end_size = self.main_card.size()
        start_size = QSize(0, 0)
        
        scale_up = QPropertyAnimation(self.main_card, b"size")
        scale_up.setDuration(300)
        scale_up.setStartValue(start_size)
        scale_up.setEndValue(end_size)
        scale_up.setEasingCurve(QEasingCurve.OutQuad)

        self.animation_group = QParallelAnimationGroup(self)
        self.animation_group.addAnimation(fade_in)
        self.animation_group.addAnimation(scale_up)
        self.animation_group.start()

    def animate_hide(self):
        """Hide the overlay with a smooth transition effect."""
        # Fade out the overlay
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(200)
        fade_out.setStartValue(self.windowOpacity())
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InCubic)

        # Scale down the card
        start_size = self.main_card.size()
        end_size = QSize(0, 0)
        
        scale_down = QPropertyAnimation(self.main_card, b"size")
        scale_down.setDuration(200)
        scale_down.setStartValue(start_size)
        scale_down.setEndValue(end_size)
        scale_down.setEasingCurve(QEasingCurve.InQuad)

        self.animation_group = QParallelAnimationGroup(self)
        self.animation_group.addAnimation(fade_out)
        self.animation_group.addAnimation(scale_down)
        self.animation_group.finished.connect(self.hide)
        self.animation_group.start()

    def hide_overlay(self):
        """إخفاء الطبقة وتنظيف تأثير البلور."""
        global_worker_manager.stop_thumbnail_generation()

        # تنظيف الطبقة الضبابية
        if hasattr(self, 'blur_background'):
            # إزالة جميع العناصر الفرعية من الطبقة الضبابية
            for child in self.blur_background.findChildren(QLabel):
                child.deleteLater()

        # استخدام التأثير الانتقالي للإخفاء
        self.animate_hide()

    def cancel(self):
        # إلغاء واجهة الإسقاط
        self.cancelled.emit()

        # إشعار النافذة الرئيسية بتحديث حالة العمل
        if hasattr(self.main_window, 'update_work_status_after_file_removal'):
            self.main_window.update_work_status_after_file_removal()

        self.hide_overlay()

    def update_ui_for_context(self):
        """تحديث واجهة المستخدم بناءً على السياق."""
        self.clear_options()
        self.title_label.setText(self.page_title)
        self.description_label.setText(tr("drop_files_prompt"))
        self.update_icon_color()
        
        # إظهار أيقونة الإسقاط الكبيرة
        self.drop_icon_label.show()
        icon = load_svg_icon("assets/icons/default/plus.svg", 128, "#555")
        self.drop_icon_label.setPixmap(icon)

        # إخفاء المصغرات والأزرار عند بدء السحب
        self.thumbnails_scroll_area.hide()
        self.cancel_button.hide()

    def add_option_button(self, text, callback):
        """إضافة زر خيار بتصميم موحد."""
        button = QPushButton(text)
        button.setObjectName("optionButton")
        button.setProperty("class", "optionButton") # For styling
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(callback)
        self.options_layout.addWidget(button)

    def clear_options(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def populate_thumbnails(self):
        """إنشاء بطاقات مصغرة للملفات وبدء العامل لجلب الصور."""
        # مسح البطاقات القديمة
        while self.thumbnails_layout.count():
            child = self.thumbnails_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.thumbnail_widgets.clear()

        colors = global_theme_manager.get_current_colors()
        pdf_files = [f for f in self.files if f.lower().endswith('.pdf')]

        if not pdf_files:
            self.thumbnails_scroll_area.hide()
            return
            
        self.thumbnails_scroll_area.show()

        for file_path in pdf_files:
            card = FileThumbnailCard(file_path)
            card.set_placeholder_style(colors)
            self.thumbnails_layout.addWidget(card)
            self.thumbnail_widgets[file_path] = card

        # بدء العامل لجلب الصور
        worker = global_worker_manager.start_thumbnail_generation(pdf_files)
        worker.thumbnail_ready.connect(self.update_thumbnail)

    def update_thumbnail(self, file_path, pixmap):
        """تحديث الصورة المصغرة عند جهوزيتها من العامل."""
        if file_path in self.thumbnail_widgets:
            self.thumbnail_widgets[file_path].set_thumbnail(pixmap)

    def emit_action(self, action_type):
        # التحقق من صحة الإجراء قبل الإرسال
        if not action_type or action_type == "False":
            action_type = "add_to_list"
            
        self.action_selected.emit(action_type, self.files)
        self.hide_overlay()
        
        # إعادة تفعيل النافذة الرئيسية لضمان ظهور الملفات المضافة
        if self.main_window:
            self.main_window.setEnabled(True)
            self.main_window.activateWindow()
            self.main_window.raise_()

    def _setup_options_for_context(self):
        """إعداد الخيارات بعد إفلات الملفات بنجاح."""
        self.clear_options()
        self.description_label.setText(tr("smart_drop_welcome_description", count=len(self.files)))

        context_action_map = {
            'welcome': [
                (tr("smart_drop_merge_files"), "merge") if len(self.files) > 1 else (tr("smart_drop_compress_file"), "compress"),
                (tr("smart_drop_compress_files"), "compress") if len(self.files) > 1 else (tr("smart_drop_rotate_file"), "rotate")
            ],
            'merge': [(tr("smart_drop_add_to_merge_list"), "add_to_list")],
            'split': [(tr("smart_drop_add_to_split_list"), "add_to_list")],
            'compress': [(tr("smart_drop_add_to_compress_list"), "add_to_list")],
            'rotate': [(tr("smart_drop_add_to_rotate_list"), "add_to_list")],
            'convert': [(tr("smart_drop_add_to_convert_list"), "add_to_list")],
            'security': [(tr("smart_drop_add_to_security_list"), "add_to_list")],
        }

        actions = context_action_map.get(self.current_context, [])
        for text, action in actions:
            self.add_option_button(text, lambda act=action: self.emit_action(act))

    def resizeEvent(self, event):
        """تحديث الحجم عند تغيير حجم النافذة الأصلية."""
        super().resizeEvent(event)
        if self.parent():
            self.setFixedSize(self.parent().size())

        # تحديث حجم الطبقة الضبابية
        if hasattr(self, 'blur_background'):
            self.blur_background.resize(self.size())
            # تحديث حجم العناصر الفرعية في الطبقة الضبابية
            for child in self.blur_background.findChildren(QLabel):
                child.resize(self.blur_background.size())
            
    def reset_mode(self):
        """إعادة تعيين الوضع إلى الوضع الافتراضي"""
        self.current_context = 'welcome'
        self.page_title = tr("menu_home")
        self.is_valid_drop = False
        
    def remove_file(self, file_path):
        """إزالة ملف من القائمة مع تأثير حركي."""
        if file_path in self.thumbnail_widgets:
            widget = self.thumbnail_widgets[file_path]
            # بدء حركة الحذف في البطاقة نفسها
            widget.delete_file()
        else:
            # إذا لم يكن الويدجت موجودًا لسبب ما، قم بإزالته مباشرة
            self._handle_file_removal(file_path)

    def _handle_file_removal(self, file_path):
        """يتم استدعاؤها بعد انتهاء حركة حذف البطاقة."""
        if file_path in self.files:
            self.files.remove(file_path)
        
        if file_path in self.thumbnail_widgets:
            widget = self.thumbnail_widgets.pop(file_path)
            # إزالة الويدجت من الـ layout قبل حذفه
            self.thumbnails_layout.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()

        # إذا لم يتبق ملفات، أغلق النافذة
        if not self.files:
            self.cancel()
        else:
            # تحديث الوصف ليعكس العدد الجديد للملفات
            self.description_label.setText(tr("smart_drop_welcome_description", count=len(self.files)))

            # إشعار النافذة الرئيسية بتحديث حالة العمل
            if hasattr(self.main_window, 'update_work_status_after_file_removal'):
                self.main_window.update_work_status_after_file_removal()


    def enhanced_populate_thumbnails(self):
        """نسخة محسنة من دالة populate_thumbnails لدعم أنواع مختلفة من الملفات"""
        # مسح البطاقات القديمة
        while self.thumbnails_layout.count():
            child = self.thumbnails_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.thumbnail_widgets.clear()

        colors = global_theme_manager.get_current_colors()
        
        # تصنيف الملفات حسب النوع
        pdf_files = [f for f in self.files if f.lower().endswith('.pdf')]
        image_files = [f for f in self.files if self._is_image_file(f)]
        text_files = [f for f in self.files if f.lower().endswith('.txt')]
        folder_files = [f for f in self.files if os.path.isdir(f)]
        other_files = [f for f in self.files if f not in pdf_files + image_files + text_files and os.path.isfile(f)]
        
        # إذا لم يكن هناك ملفات معروضة، إخفاء منطقة المصغرات
        if not (pdf_files or image_files or text_files or folder_files or other_files):
            self.thumbnails_scroll_area.hide()
            return

        self.thumbnails_scroll_area.show()

        # إنشاء بطاقات لكل نوع من الملفات
        for file_path in pdf_files:
            card = FileThumbnailCard(file_path)
            card.file_deleted.connect(self._handle_file_removal)
            card.set_placeholder_style(colors)
            self.thumbnails_layout.addWidget(card)
            self.thumbnail_widgets[file_path] = card
            
        for file_path in image_files:
            card = FileThumbnailCard(file_path)
            card.file_deleted.connect(self._handle_file_removal)
            card.set_placeholder_style(colors)
            self.thumbnails_layout.addWidget(card)
            self.thumbnail_widgets[file_path] = card
            # تحميل الصورة مباشرة
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(80, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                card.set_thumbnail(scaled_pixmap)
                
        for file_path in text_files:
            card = FileThumbnailCard(file_path)
            card.file_deleted.connect(self._handle_file_removal)
            card.set_placeholder_style(colors)
            self.thumbnails_layout.addWidget(card)
            self.thumbnail_widgets[file_path] = card
            # استخدام أيقونة نصية
            icon = load_svg_icon("assets/icons/default/file-text.svg", 64, colors.get("text_accent", "#056a51"))
            if icon:
                card.set_thumbnail(icon)
                
        for file_path in folder_files:
            card = FileThumbnailCard(file_path)
            card.file_deleted.connect(self._handle_file_removal)
            card.set_placeholder_style(colors)
            self.thumbnails_layout.addWidget(card)
            self.thumbnail_widgets[file_path] = card
            # استخدام أيقونة مجلد
            icon = load_svg_icon("assets/icons/default/folder-open.svg", 64, colors.get("text_accent", "#056a51"))
            if icon:
                card.set_thumbnail(icon)
                
        for file_path in other_files:
            card = FileThumbnailCard(file_path)
            card.file_deleted.connect(self._handle_file_removal)
            card.set_placeholder_style(colors)
            self.thumbnails_layout.addWidget(card)
            self.thumbnail_widgets[file_path] = card
            # استخدام أيقونة عامة
            icon = load_svg_icon("assets/icons/default/file-text.svg", 64, colors.get("text_accent", "#056a51"))
            if icon:
                card.set_thumbnail(icon)

        # بدء العامل لجلب الصور فقط لملفات PDF
        if pdf_files:
            worker = global_worker_manager.start_thumbnail_generation(pdf_files)
            worker.thumbnail_ready.connect(self.update_thumbnail)

    def capture_background_blur(self):
        """التقاط لقطة من الخلفية وتطبيق تأثير البلور عليها."""
        if self.parent() and self.main_window:
            try:
                # تنظيف الطبقة الضبابية أولاً
                for child in self.blur_background.findChildren(QLabel):
                    child.deleteLater()

                # تم تعطيل لقطة الشاشة واستبدالها بخلفية بسيطة لتوفير الموارد
                self.blur_background.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")

            except Exception as e:
                # في حالة فشل التقاط الصورة، استخدم خلفية بسيطة
                self.blur_background.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")

    def handle_drag_enter(self, event: QDragEnterEvent):
        """معالجة دخول السحب إلى النافذة الرئيسية."""
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        urls = event.mimeData().urls()
        self.files = [url.toLocalFile() for url in urls if url.isLocalFile()]
        self.is_valid_drop = self._validate_files_for_context(self.files)

        if self.parent():
            self.setFixedSize(self.parent().size())
            self.move(0, 0)

        self.capture_background_blur()
        self.update_styles()
        self.update_ui_for_context()
        self.animate_show()
        event.acceptProposedAction()

    def handle_drag_leave(self, event):
        """معالجة مغادرة السحب للنافذة."""
        # معالجة مغادرة السحب في واجهة الإسقاط
        self.cancel()
        event.accept()

    def handle_drop(self, event: QDropEvent):
        """معالجة إفلات الملفات مع دعم توسيع المجلدات."""
        # الملفات تم التحقق منها مسبقًا في handle_drag_enter
        # التحقق من صحة الملفات قبل المتابعة
        if not self.is_valid_drop:
            self.cancel()
            event.ignore()
            return

        self.drop_icon_label.hide()
        self.enhanced_populate_thumbnails()
        self._setup_options_for_context()
        self.thumbnails_scroll_area.show()
        self.cancel_button.show()
        event.acceptProposedAction()

    def _validate_files_for_context(self, file_paths):
        """التحقق من صحة الملفات بناءً على السياق الحالي وإعدادات الصفحة."""
        if not file_paths:
            return False

        if self.current_context in ['help', 'settings', 'welcome']:
            return False

        settings = getattr(self, 'current_page_settings', None)
        if not settings:
            from modules.page_settings import page_settings
            page_key_map = {
                'merge': 'merge_print', 'split': 'split', 'compress': 'compress',
                'rotate': 'stamp_rotate', 'convert': 'convert', 'security': 'protect_properties'
            }
            page_key = page_key_map.get(self.current_context)
            if not page_key or page_key not in page_settings:
                return False
            settings = page_settings[page_key]

        accepted_types = settings.get("accepted_file_types", [])
        if not accepted_types:
            return False

        for path in file_paths:
            if not os.path.isdir(path):
                file_ext = os.path.splitext(path)[1].lower()
                if file_ext not in accepted_types:
                    return False
        
        return True

    def _is_image_file(self, file_path):
        """التحقق مما إذا كان الملف صورة"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('image/'):
            return True
            
        # التحقق من الامتدادات الشائعة للصور
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        return any(file_path.lower().endswith(ext) for ext in image_extensions)
        
    def _show_rejection_message(self):
        """(DEPRECATED) عرض رسالة رفض للملفات"""
        # هذا لم يعد مستخدماً، حيث يتم التوضيح بصرياً عبر لون الإطار
        pass
