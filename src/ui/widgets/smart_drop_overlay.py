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

from src.ui.widgets.svg_icon_button import load_svg_icon
from src.utils.translator import tr
from src.managers.theme_manager import make_theme_aware, global_theme_manager
from src.core.pdf_worker import global_worker_manager
from src.utils.page_settings import page_settings
from src.utils import settings
from managers.language_manager import language_manager

class ThemedTransparentButton(QPushButton):
    """زر شفاف بلون السمة مع تأثيرات المرور"""
    
    def __init__(self, text, is_cancel=False, parent=None):
        super().__init__(text, parent)
        self.is_cancel = is_cancel
        self.setup_style()
        
    def setup_style(self):
        if self.is_cancel:
            # زر الإلغاء بلون أحمر خفيف
            base_color = "#e74c3c"
            bg_color = "#e74c3c30"  # خلفية حمراء شفافة خفيفة
            hover_color = "#c0392b"
        else:
            # زر الإضافة بلون أخضر خفيف
            base_color = "#27ae60"
            bg_color = "#27ae6030"  # خلفية خضراء شفافة خفيفة
            hover_color = "#229954"
            
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: 2px solid {base_color};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_color}50;
                border-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {base_color}70;
            }}
        """)
    


class FileThumbnailCard(QWidget):
    """بطاقة مصغرة لعرض ملف مع صورته واسمه وزر حذف، مع تأثيرات حركية."""
    file_deleted = Signal(str)

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setFixedSize(110, 140)  # حجم أكبر لتجنب الاقتصاص
        self.setContentsMargins(0, 0, 0, 0)

        # الرسوم المتحركة
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.OutCubic)

        # الهيكل الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # حاوية الصورة المصغرة مع حجم أكبر (للسماح بتراكب زر الحذف)
        self.thumbnail_container = QFrame()
        self.thumbnail_container.setObjectName("thumbnailContainer")
        self.thumbnail_container.setFixedSize(100, 100)  # حجم أكبر
        container_layout = QVBoxLayout(self.thumbnail_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setObjectName("thumbnailLabel")
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setScaledContents(True)  # تمكين التحجيم التلقائي
        container_layout.addWidget(self.thumbnail_label)

        # زر الحذف مع أيقونة وحجم أكبر
        self.delete_button = QPushButton()
        make_theme_aware(self.delete_button, "delete_button")
        self.delete_button.setFixedSize(26, 26)  # حجم أكبر للزر
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(self.delete_file)
        self.delete_button.setParent(self.thumbnail_container)
        self.delete_button.hide()  # إخفاء مبدئي

        # العنوان
        self.name_label = QLabel(os.path.basename(file_path))
        make_theme_aware(self.name_label, "thumbnail_name_label")
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
        """تحديث أيقونة زر الحذف بجودة عالية."""
        icon = load_svg_icon("assets/icons/default/trash-2.svg", 20, color)  # حجم أكبر
        if icon:
            self.delete_button.setIcon(icon)
            self.delete_button.setIconSize(QSize(20, 20))  # حجم أيقونة أكبر

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
        # وضع الزر في الزاوية العلوية اليمنى مع موقع محسن
        self.delete_button.move(self.thumbnail_container.width() - self.delete_button.width() - 3, 3)

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
        """تعيين الصورة المصغرة مع تحسين الجودة"""
        if pixmap:
            # تطبيق تحجيم عالي الجودة
            scaled_pixmap = pixmap.scaled(
                95, 95,  # حجم مناسب للحاوية الجديدة
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            self.thumbnail_label.setPixmap(pixmap)

    def set_placeholder_style(self):
        make_theme_aware(self.delete_button, "delete_button")
        self.update_delete_button_icon("white")

        make_theme_aware(self.thumbnail_container, "thumbnail_container")
        make_theme_aware(self.thumbnail_label, "thumbnail_label")
        # Text color for name_label is handled automatically by ThemeAwareFilter


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
        self._is_processing = False  # منع السباق
        self._is_showing = False  # منع الاستدعاء المتكرر

        # متغيرات للتأثيرات الانتقالية
        self.fade_animation = None
        self.scale_animation = None

        self.setup_ui()
        
        # ربط تحديث السمات
        global_theme_manager.theme_changed.connect(self.update_theme)
        global_theme_manager.theme_changed.connect(self.update_button_styles)

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
        make_theme_aware(self.blur_background, "blur_background")
        self.blur_background.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        full_layout.addWidget(self.blur_background, 0, 0)

        # طبقة المحتوى (البطاقة) فوق الطبقة الضبابية
        content_widget = QWidget()
        content_widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addStretch()

        self.main_card = QFrame()
        make_theme_aware(self.main_card, "smart_drop_card")
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

        # أيقونة كبيرة في الأعلى مع جودة عالية
        self.icon_label = QLabel()
        self.icon_label.setObjectName("smartDropIcon")
        self.icon_label.setFixedSize(120, 120)  # حجم أكبر للأيقونة الرئيسية
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setScaledContents(True)
        
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(self.icon_label)
        icon_layout.addStretch()
        card_layout.addLayout(icon_layout)

        # العنوان
        self.title_label = QLabel()
        make_theme_aware(self.title_label, "smart_drop_title")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        card_layout.addWidget(self.title_label)

        # الوصف
        self.description_label = QLabel()
        make_theme_aware(self.description_label, "smart_drop_description")
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

        # فريم الأيقونات المصغرة مع ارتفاع أكبر
        self.thumbnails_frame = QFrame()
        make_theme_aware(self.thumbnails_frame, "thumbnails_frame")
        self.thumbnails_frame.setFixedHeight(130)  # ارتفاع أكبر ليتناسب مع الأيقونات الجديدة
        self.thumbnails_layout = QHBoxLayout(self.thumbnails_frame)
        self.thumbnails_layout.setAlignment(Qt.AlignCenter)
        self.thumbnails_layout.setSpacing(15)  # مسافة أكبر بين الأيقونات
        
        card_layout.addWidget(self.thumbnails_frame)
        card_layout.addStretch(1)

        # حاوية الأزرار (الإضافة والإلغاء)
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(10)
        
        # زر الإلغاء
        self.cancel_button = ThemedTransparentButton(tr("cancel_button"), is_cancel=True)
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.cancel)
        
        card_layout.addLayout(self.buttons_layout)

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
        """Show the overlay with a simple fade in."""
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        # Simple fade in only
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(200)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in.start()

    def animate_hide(self):
        """Hide the overlay with a simple fade out."""
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(150)
        self.fade_out.setStartValue(self.windowOpacity())
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self.hide)
        self.fade_out.start()

    def hide_overlay(self):
        """إخفاء الطبقة وتنظيف تأثير البلور."""
        self._is_showing = False
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
        
        icon_color = global_theme_manager.get_color("text_accent")
        
        icon_name = "file-text"
        context_map = {
            'welcome': 'logo', 'merge': 'merge', 'split': 'scissors',
            'compress': 'archive', 'rotate': 'rotate-cw', 'convert': 'file-text',
            'security': 'settings', 'help': 'info', 'settings': 'settings'
        }
        icon_name = context_map.get(self.current_context, "file-text")
            
        # تحميل الأيقونة بحجم أكبر وجودة عالية
        icon = load_svg_icon(f"assets/icons/default/{icon_name}.svg", 256, icon_color)
        if icon:
            # تطبيق تحجيم عالي الجودة
            scaled_pixmap = icon.scaled(
                120, 120,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.icon_label.setPixmap(scaled_pixmap)
        
        # إظهار أيقونة الإسقاط الكبيرة
        self.drop_icon_label.show()
        icon = load_svg_icon("assets/icons/default/plus.svg", 128, "#555")
        self.drop_icon_label.setPixmap(icon)

        # إخفاء المصغرات والأزرار عند بدء السحب
        self.thumbnails_frame.hide()
        # إخفاء حاوية الأزرار بالكامل
        for i in range(self.buttons_layout.count()):
            item = self.buttons_layout.itemAt(i)
            if item and item.widget():
                item.widget().hide()

    def add_option_button(self, text, callback):
        """إضافة زر خيار بتصميم موحد."""
        button = ThemedTransparentButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(40)
        button.clicked.connect(callback)
        self.buttons_layout.addWidget(button)

    def clear_options(self):
        if self._is_processing:
            return
        self._is_processing = True
        
        try:
            # حذف جميع العناصر
            while self.buttons_layout.count():
                try:
                    item = self.buttons_layout.takeAt(0)
                    if item and item.widget():
                        item.widget().deleteLater()
                except RuntimeError:
                    break
            
            # إعادة إنشاء زر الإلغاء
            self.cancel_button = ThemedTransparentButton(tr("cancel_button"), is_cancel=True)
            self.cancel_button.setMinimumHeight(40)
            self.cancel_button.setCursor(Qt.PointingHandCursor)
            self.cancel_button.clicked.connect(self.cancel)
        except Exception:
            pass
        finally:
            self._is_processing = False

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
        
        # إضافة زر الإلغاء في النهاية
        self.buttons_layout.addWidget(self.cancel_button)

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
    
    def update_theme(self):
        if self._is_processing:
            return
            
        """تحديث السمة لجميع عناصر نافذة الإسقاط"""
        try:
            icon_color = global_theme_manager.get_color("text_accent")
            
            # تحديث أيقونة السياق بجودة عالية
            if hasattr(self, 'icon_label') and self.icon_label:
                try:
                    icon_name = "file-text"
                    context_map = {
                        'welcome': 'logo', 'merge': 'merge', 'split': 'scissors',
                        'compress': 'archive', 'rotate': 'rotate-cw', 'convert': 'file-text',
                        'security': 'settings', 'help': 'info', 'settings': 'settings'
                    }
                    icon_name = context_map.get(self.current_context, "file-text")
                    icon = load_svg_icon(f"assets/icons/default/{icon_name}.svg", 256, icon_color)
                    if icon:
                        scaled_pixmap = icon.scaled(
                            120, 120,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.icon_label.setPixmap(scaled_pixmap)
                except (RuntimeError, AttributeError):
                    pass
            
            # تحديث أيقونة الإسقاط
            if hasattr(self, 'drop_icon_label') and self.drop_icon_label:
                try:
                    icon = load_svg_icon("assets/icons/default/plus.svg", 128, "#555")
                    if icon:
                        self.drop_icon_label.setPixmap(icon)
                except (RuntimeError, AttributeError):
                    pass
            
            # تحديث أيقونات أزرار الحذف في البطاقات المصغرة
            if hasattr(self, 'thumbnail_widgets') and self.thumbnail_widgets:
                for widget in list(self.thumbnail_widgets.values()):
                    try:
                        if widget and hasattr(widget, 'update_delete_button_icon'):
                            widget.update_delete_button_icon("white")
                    except (RuntimeError, AttributeError):
                        continue
        except Exception:
            pass
    
    def update_button_styles(self):
        """تحديث أنماط الأزرار عند تغيير السمة"""
        # تحديث جميع الأزرار في الحاوية الأفقية
        for i in range(self.buttons_layout.count()):
            item = self.buttons_layout.itemAt(i)
            if item and isinstance(item.widget(), ThemedTransparentButton):
                item.widget().setup_style()
    
    def update_styles(self):
        """تحديث جميع الأنماط (دالة مطلوبة من merge_page)"""
        self.update_theme()
        self.update_button_styles()
    
    def _add_buttons_with_fade(self):
        if self._is_processing:
            return
        
        """إضافة الأزرار بتأثير fade in"""
        self._setup_options_for_context()
        
        # إظهار الأزرار بتأثير fade in
        for i in range(self.buttons_layout.count()):
            try:
                item = self.buttons_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    widget.setWindowOpacity(0.0)
                    widget.show()
                    
                    # أنيميشن fade in للزر
                    fade_in = QPropertyAnimation(widget, b"windowOpacity")
                    fade_in.setDuration(200)
                    fade_in.setStartValue(0.0)
                    fade_in.setEndValue(1.0)
                    fade_in.setEasingCurve(QEasingCurve.OutCubic)
                    fade_in.start()
            except RuntimeError:
                continue


    def enhanced_populate_thumbnails(self):
        if self._is_processing:
            return
            
        """نسخة محسنة من دالة populate_thumbnails لدعم أنواع مختلفة من الملفات مع أيقونات عالية الجودة"""
        try:
            # مسح البطاقات القديمة
            while self.thumbnails_layout.count():
                try:
                    child = self.thumbnails_layout.takeAt(0)
                    if child and child.widget():
                        child.widget().deleteLater()
                except RuntimeError:
                    break
            self.thumbnail_widgets.clear()

            icon_color = global_theme_manager.get_color("text_accent")
            
            # إذا لم يكن هناك ملفات، إخفاء فريم المصغرات
            if not self.files:
                if hasattr(self, 'thumbnails_frame') and self.thumbnails_frame:
                    self.thumbnails_frame.hide()
                return

            if hasattr(self, 'thumbnails_frame') and self.thumbnails_frame:
                self.thumbnails_frame.show()

            # إنشاء أيقونة مع زر حذف لكل ملف
            for file_path in self.files:
                try:
                    # تحديد الأيقونة حسب نوع الملف
                    if os.path.isdir(file_path):
                        icon_name = "folder-open"
                    elif file_path.lower().endswith('.pdf'):
                        icon_name = "file-text"
                    elif self._is_image_file(file_path):
                        icon_name = "image"
                    else:
                        icon_name = "file-text"
                    
                    # إنشاء حاوية للأيقونة وزر الحذف
                    icon_container = QWidget()
                    icon_container.setFixedSize(100, 100)
                    
                    # الأيقونة
                    icon_label = QLabel(icon_container)
                    icon_label.setFixedSize(90, 90)
                    icon_label.move(5, 5)
                    icon_label.setAlignment(Qt.AlignCenter)
                    icon_label.setScaledContents(True)
                    
                    # تحميل الأيقونة
                    icon = load_svg_icon(f"assets/icons/default/{icon_name}.svg", 128, icon_color)
                    if icon:
                        scaled_pixmap = icon.scaled(
                            90, 90,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        icon_label.setPixmap(scaled_pixmap)
                    else:
                        file_ext = os.path.splitext(file_path)[1].upper() or "FILE"
                        icon_label.setText(file_ext)
                        icon_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {icon_color};")
                    
                    # زر الحذف
                    delete_btn = QPushButton(icon_container)
                    delete_btn.setFixedSize(26, 26)
                    delete_btn.move(74, 2)
                    delete_btn.hide()
                    delete_btn.setCursor(Qt.PointingHandCursor)
                    
                    delete_icon = load_svg_icon("assets/icons/default/trash-2.svg", 20, "white")
                    if delete_icon:
                        delete_btn.setIcon(delete_icon)
                        delete_btn.setIconSize(QSize(20, 20))
                    else:
                        delete_btn.setText("🗑")
                        delete_btn.setStyleSheet("font-size: 16px;")
                    
                    make_theme_aware(delete_btn, "delete_button")
                    delete_btn.clicked.connect(lambda checked, fp=file_path: self._handle_file_removal(fp))
                    
                    # أحداث المرور
                    def enter_event(event, btn=delete_btn):
                        if btn:
                            btn.show()
                    def leave_event(event, btn=delete_btn):
                        if btn:
                            btn.hide()
                            
                    icon_container.enterEvent = enter_event
                    icon_container.leaveEvent = leave_event
                    
                    self.thumbnails_layout.addWidget(icon_container)
                    self.thumbnail_widgets[file_path] = icon_container
                except (RuntimeError, AttributeError, OSError):
                    continue
        except Exception:
            pass

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
        if self._is_showing or not event.mimeData().hasUrls():
            event.ignore()
            return

        self._is_showing = True
        urls = event.mimeData().urls()
        self.files = [url.toLocalFile() for url in urls if url.isLocalFile()]
        
        # إظهار النافذة أولاً
        if self.parent():
            self.setFixedSize(self.parent().size())
            self.move(0, 0)

        self.capture_background_blur()
        self.update_ui_for_context()
        self.animate_show()
        
        # التحقق من صحة الملفات بعد إظهار النافذة
        self.is_valid_drop = self._validate_files_for_context(self.files)
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
            event.ignore()
            return

        self.drop_icon_label.hide()
        self.enhanced_populate_thumbnails()
        self.thumbnails_frame.show()
        
        # تأخير إضافة الأزرار حتى انتهاء الأنيميشن
        QTimer.singleShot(250, self._add_buttons_with_fade)
        event.acceptProposedAction()

    def _validate_files_for_context(self, file_paths):
        """التحقق من صحة الملفات بناءً على السياق الحالي وإعدادات الصفحة."""
        print(f"DEBUG: Validating files: {file_paths}")
        print(f"DEBUG: Current context: {self.current_context}")
        
        if not file_paths:
            return False

        if self.current_context in ['help', 'settings', 'welcome']:
            print("DEBUG: Unsupported context")
            self._show_unsupported_context_message()
            return False

        settings = getattr(self, 'current_page_settings', None)
        if not settings:
            from src.utils.page_settings import page_settings
            page_key_map = {
                'merge': 'merge_print', 'split': 'split', 'compress': 'compress',
                'rotate': 'stamp_rotate', 'convert': 'convert', 'security': 'protect_properties'
            }
            page_key = page_key_map.get(self.current_context)
            print(f"DEBUG: Page key: {page_key}")
            if not page_key or page_key not in page_settings:
                print("DEBUG: No page settings found")
                self._show_unsupported_context_message()
                return False
            settings = page_settings[page_key]

        accepted_types = settings.get("accepted_file_types", [])
        print(f"DEBUG: Accepted types: {accepted_types}")
        if not accepted_types:
            print("DEBUG: No accepted types")
            self._show_unsupported_context_message()
            return False

        unsupported_files = []
        for path in file_paths:
            if not os.path.isdir(path):
                file_ext = os.path.splitext(path)[1].lower()
                print(f"DEBUG: File {path} has extension {file_ext}")
                if file_ext not in accepted_types:
                    unsupported_files.append(os.path.basename(path))
        
        print(f"DEBUG: Unsupported files: {unsupported_files}")
        if unsupported_files:
            print("DEBUG: Showing unsupported files message")
            self._show_unsupported_files_message(unsupported_files, accepted_types)
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
    
    def _show_unsupported_context_message(self):
        """عرض رسالة عند محاولة إسقاط ملفات في سياق غير مدعوم"""
        self.title_label.setText("لا يمكن إسقاط الملفات هنا")
        self.description_label.setText("انتقل إلى صفحة معالجة PDF لإضافة الملفات")
        self.drop_icon_label.hide()
        QTimer.singleShot(3000, self._reset_to_files_view)
    
    def _show_unsupported_files_message(self, unsupported_files, accepted_types):
        """عرض رسالة تفصيلية عن الملفات غير المدعومة"""
        # فلترة الملفات المدعومة فقط
        supported_files = []
        for path in self.files:
            if not os.path.isdir(path):
                file_ext = os.path.splitext(path)[1].lower()
                if file_ext in accepted_types:
                    supported_files.append(path)
            else:
                supported_files.append(path)
        
        self.files = supported_files
        
        files_text = ", ".join(unsupported_files[:3])
        if len(unsupported_files) > 3:
            files_text += f" و{len(unsupported_files) - 3} ملفات أخرى"
        
        # عرض رسالة بنفس تنسيق العنوان الأصلي
        message = f"تم تجاهل الملفات غير المدعومة: {files_text}"
        self.title_label.setText("ملفات غير مدعومة")
        self.description_label.setText(message)
        
        # إخفاء أيقونة الإسقاط
        self.drop_icon_label.hide()
        
        QTimer.singleShot(3000, self._reset_to_files_view)
    
    def _reset_to_files_view(self):
        """العودة إلى عرض الملفات بدلاً من إغلاق النافذة"""
        if self.files:
            self.is_valid_drop = True
            # إعادة تعيين العنوان والوصف مع اللون الأصلي
            self.title_label.setText(self.page_title)
            self.title_label.setStyleSheet("")
            make_theme_aware(self.title_label, "smart_drop_title")
            self.description_label.setText(tr("smart_drop_welcome_description", count=len(self.files)))
            self.description_label.setStyleSheet("")
            make_theme_aware(self.description_label, "smart_drop_description")
            
            self.drop_icon_label.hide()
            self.enhanced_populate_thumbnails()
            self.thumbnails_frame.show()
            QTimer.singleShot(250, self._add_buttons_with_fade)
        elif self._has_files_in_current_page():
            # إذا كانت هناك ملفات في الصفحة الحالية، عد إلى عرضها
            self.cancel()
        else:
            self.cancel()
        
    def _has_files_in_current_page(self):
        """التحقق من وجود ملفات في الصفحة الحالية"""
        if not self.main_window:
            return False
        
        current_page_index = self.main_window.stack.currentIndex()
        if current_page_index > 0 and self.main_window.pages_loaded[current_page_index]:
            current_page = self.main_window.stack.widget(current_page_index)
            if hasattr(current_page, 'widget'):
                current_page = current_page.widget()
            
            if hasattr(current_page, 'has_files'):
                return current_page.has_files()
            elif hasattr(current_page, 'file_list_frame') and hasattr(current_page.file_list_frame, 'has_files'):
                return current_page.file_list_frame.has_files()
        
        return False
    
    def _reset_ui_to_normal(self):
        """إعادة تعيين واجهة المستخدم للوضع الطبيعي"""
        self.title_label.setText(self.page_title)
        self.title_label.setStyleSheet("")
        make_theme_aware(self.title_label, "smart_drop_title")
        self.description_label.setText(tr("drop_files_prompt"))
        self.description_label.setStyleSheet("")
        make_theme_aware(self.description_label, "smart_drop_description")
