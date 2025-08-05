# -*- coding: utf-8 -*-
"""
صفحة تدوير ملفات PDF
"""

from PySide6.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QLabel, QFileDialog, QMessageBox, QGraphicsOpacityEffect, QProgressBar, QGraphicsPixmapItem, QGraphicsSceneWheelEvent)
from PySide6.QtGui import QPixmap, QImage, QTransform, QCursor, QBrush, QPainter
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
import fitz  # PyMuPDF
from .interactive_stamp import InteractiveStamp
from .svg_icon_button import create_navigation_button, create_action_button
from .theme_aware_widget import make_theme_aware
from PySide6.QtWidgets import QWidget
from modules.translator import tr, register_language_change_callback

# استيراد الأنظمة الجديدة للأداء
from .lazy_loader import global_page_loader
from .smart_cache import pdf_cache
from .pdf_worker import global_worker_manager

class InteractiveGraphicsView(QGraphicsView):
    """QGraphicsView مخصص للتعامل مع الختم التفاعلي"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = None

    def set_parent_page(self, parent_page):
        """تعيين الصفحة الأب للوصول للمتغيرات"""
        self.parent_page = parent_page

    def mouseMoveEvent(self, event):
        """معالجة حركة الماوس مع إعطاء الأولوية للعناصر التفاعلية"""
        # إذا كنا في وضع إضافة ختم، تعامل مع المعاينة
        if (self.parent_page and
            hasattr(self.parent_page, 'placing_stamp') and
            self.parent_page.placing_stamp and
            hasattr(self.parent_page, 'stamp_preview') and
            self.parent_page.stamp_preview):

            scene_pos = self.mapToScene(event.pos())
            self.parent_page.stamp_preview.update_position(scene_pos)
            self.parent_page.stamp_preview.show_preview()

        # استدعاء المعالج الأصلي للسماح للعناصر التفاعلية بالعمل
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """معالجة الضغط على الماوس مع إعطاء الأولوية للعناصر التفاعلية"""
        # إذا كنا في وضع إضافة ختم
        if (self.parent_page and
            hasattr(self.parent_page, 'placing_stamp') and
            self.parent_page.placing_stamp):

            if event.button() == Qt.LeftButton:
                scene_pos = self.mapToScene(event.pos())
                self.parent_page.place_stamp_at_position(scene_pos)
                return  # لا نستدعي المعالج الأصلي هنا
            
            elif event.button() == Qt.RightButton:
                # إلغاء وضع الختم عند النقر بالزر الأيمن
                self.parent_page.end_stamp_placement()
                return

        # استدعاء المعالج الأصلي للسماح للعناصر التفاعلية بالعمل
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        """معالجة التكبير والتصغير مباشرة عند الضغط على Ctrl"""
        # التحقق من الضغط على مفتاح Ctrl
        if event.modifiers() == Qt.ControlModifier:
            # الحصول على العنصر الموجود تحت مؤشر الماوس
            item = self.itemAt(event.position().toPoint())
            
            # التحقق مما إذا كان العنصر هو ختم تفاعلي ومحدد
            if isinstance(item, InteractiveStamp) and item.isSelected():
                # تحديد اتجاه التكبير
                if event.angleDelta().y() > 0:
                    item.zoom_in()
                else:
                    item.zoom_out()
                
                # قبول الحدث لمنع أي معالجة إضافية (مثل التمرير)
                event.accept()
                return

        # إذا لم تتحقق الشروط، اسمح للسلوك الافتراضي
        super().wheelEvent(event)

class RotatePage(QWidget):
    def __init__(self, notification_manager, file_path=None, parent=None):
        super().__init__(parent)
        self.theme_handler = make_theme_aware(self, "rotate_page")
        
        self.notification_manager = notification_manager
        self.file_path = file_path
        self.current_page = 0
        self.page_rotations = {}  # قاموس لتخزين زاوية دوران كل صفحة
        self.pages = []  # List to store loaded pages as images
        self.has_unsaved_changes = False

        # متغيرات الختم
        self.stamps = {}  # قاموس لتخزين الأختام لكل صفحة {page_num: [stamps]}
        self.stamp_preview = None  # معاينة الختم
        self.placing_stamp = False  # حالة وضع الختم
        self.current_stamp_path = None  # مسار الختم الحالي

        # متغيرات الرسوم المتحركة
        self.is_transitioning = False
        self.opacity_effect = None
        self.fade_animation = None

        # Create UI components
        self.view = InteractiveGraphicsView()
        self.view.set_parent_page(self)  # ربط الصفحة بالعرض
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        # ربط تغيير التحديد بتحديث حالة الأزرار
        self.scene.selectionChanged.connect(self.update_stamp_buttons_state)

        # إعدادات العرض المحسنة
        self.setup_optimized_view()

        # تفعيل تتبع الماوس للختم التفاعلي
        self.view.setMouseTracking(True)

        # إعداد الرسوم المتحركة
        self.setup_page_transitions()

        self.page_label = QLabel()
        # تطبيق نمط الثيمة على تسمية الصفحة
        from .theme_manager import apply_theme_style
        apply_theme_style(self.page_label, "label", auto_register=True)
        self.update_page_label()

        # تحديد لون الأيقونات حسب السمة
        from .theme_manager import global_theme_manager
        if global_theme_manager.current_theme == "light":
            icon_color = "#333333"  # لون داكن للوضع الفاتح
        else:
            icon_color = "#ffffff"  # لون أبيض للوضع المظلم

        # أقصى الشمال: التنقل
        self.prev_btn = create_navigation_button("prev", 24, tr("previous_page"))
        self.prev_btn.set_icon_color(icon_color)
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.prev_page)

        self.next_btn = create_navigation_button("next", 24, tr("next_page"))
        self.next_btn.set_icon_color(icon_color)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.next_page)

        # أزرار التدوير (شمال) - أيقونات تدوير حقيقية
        self.rotate_left_btn = create_action_button("rotate-ccw", 24, tr("rotate_left"))
        self.rotate_left_btn.set_icon_color(icon_color)
        self.rotate_left_btn.setEnabled(False)
        self.rotate_left_btn.clicked.connect(self.rotate_left)

        self.rotate_right_btn = create_action_button("rotate-cw", 24, tr("rotate_right"))
        self.rotate_right_btn.set_icon_color(icon_color)
        self.rotate_right_btn.setEnabled(False)
        self.rotate_right_btn.clicked.connect(self.rotate_right)

        # زر الختم
        self.stamp_btn = create_action_button("stamp", 24, tr("add_stamp"))
        self.stamp_btn.set_icon_color(icon_color)
        self.stamp_btn.setEnabled(False)
        self.stamp_btn.clicked.connect(self.open_stamp_manager)

        # أزرار تكبير وتصغير الختم (مخفية في البداية)
        self.zoom_in_btn = create_action_button("stamp-zoom-in", 24, tr("zoom_in_stamp"))
        self.zoom_in_btn.set_icon_color(icon_color)
        self.zoom_in_btn.setVisible(False)  # مخفي في البداية
        self.zoom_in_btn.clicked.connect(self.zoom_selected_stamp_in)

        self.zoom_out_btn = create_action_button("stamp-zoom-out", 24, tr("zoom_out_stamp"))
        self.zoom_out_btn.set_icon_color(icon_color)
        self.zoom_out_btn.setVisible(False)  # مخفي في البداية
        self.zoom_out_btn.clicked.connect(self.zoom_selected_stamp_out)

        # اليمين: إدارة الملفات
        self.file_btn = create_action_button("folder", 24, tr("select_pdf_file"))
        self.file_btn.set_icon_color(icon_color)
        self.file_btn.clicked.connect(self.select_file)

        self.reset_btn = create_action_button("reset", 24, tr("reset_rotation"))
        self.reset_btn.set_icon_color(icon_color)
        self.reset_btn.setEnabled(False)
        self.reset_btn.clicked.connect(self.reset_rotation)

        self.save_btn = create_action_button("save", 24, tr("save_rotated_file"))
        self.save_btn.set_icon_color(icon_color)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_file)

        # تخطيط الأزرار أفقي
        buttons_layout = QHBoxLayout()

        # ترتيب أزرار التنقل والتدوير حسب اللغة
        from modules.translator import get_current_language
        current_lang = get_current_language()

        if current_lang == "ar":  # العربية RTL
            # أزرار التنقل: التالي ← السابق
            buttons_layout.addWidget(self.next_btn)         # ➡️ التالي
            buttons_layout.addWidget(self.prev_btn)         # ⬅️ السابق
            # أزرار التدوير: تدوير يمين ← تدوير يسار
            buttons_layout.addWidget(self.rotate_right_btn) # ↻ تدوير يمين
            buttons_layout.addWidget(self.rotate_left_btn)  # ↺ تدوير يسار
        else:  # الإنجليزية LTR
            # أزرار التنقل: السابق ← التالي
            buttons_layout.addWidget(self.prev_btn)         # ⬅️ السابق
            buttons_layout.addWidget(self.next_btn)         # ➡️ التالي
            # أزرار التدوير: تدوير يسار ← تدوير يمين
            buttons_layout.addWidget(self.rotate_left_btn)  # ↺ تدوير يسار
            buttons_layout.addWidget(self.rotate_right_btn) # ↻ تدوير يمين
        buttons_layout.addWidget(self.stamp_btn)        # 🏷️ إضافة ختم
        buttons_layout.addWidget(self.zoom_in_btn)      # 🔍+ تكبير ختم
        buttons_layout.addWidget(self.zoom_out_btn)     # 🔍- تصغير ختم

        buttons_layout.addStretch()  # مسافة مرنة في الوسط

        # يمين: إدارة الملفات (بالترتيب الجديد)
        buttons_layout.addWidget(self.save_btn)         # 💾 حفظ
        buttons_layout.addWidget(self.reset_btn)        # ↩️ إعادة تعيين
        buttons_layout.addWidget(self.file_btn)         # 📁 اختيار ملف

        # التخطيط الرئيسي للصفحة
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        main_layout.addWidget(self.view)
        main_layout.addWidget(self.page_label, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(buttons_layout)

        # حفظ مرجع للتخطيط لإعادة الترتيب لاحقاً
        self.buttons_layout = buttons_layout

        # تسجيل callback لتغيير اللغة
        register_language_change_callback(self.update_button_order_for_language)

    def _get_main_window(self):
        """الحصول على النافذة الرئيسية للتطبيق"""
        parent = self.parent()
        while parent:
            if parent.__class__.__name__ == 'ApexFlow':
                return parent
            parent = parent.parent()
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'ApexFlow':
                return widget
        return None

    def update_button_order_for_language(self):
        """إعادة ترتيب أزرار التنقل والتدوير عند تغيير اللغة"""
        from modules.translator import get_current_language
        current_lang = get_current_language()

        # إزالة أزرار التنقل والتدوير من التخطيط
        self.buttons_layout.removeWidget(self.prev_btn)
        self.buttons_layout.removeWidget(self.next_btn)
        self.buttons_layout.removeWidget(self.rotate_left_btn)
        self.buttons_layout.removeWidget(self.rotate_right_btn)

        # إعادة إدراجها بالترتيب الصحيح حسب اللغة
        if current_lang == "ar":  # العربية RTL
            # أزرار التنقل: التالي ← السابق
            self.buttons_layout.insertWidget(0, self.next_btn)
            self.buttons_layout.insertWidget(1, self.prev_btn)
            # أزرار التدوير: تدوير يمين ← تدوير يسار
            self.buttons_layout.insertWidget(2, self.rotate_right_btn)
            self.buttons_layout.insertWidget(3, self.rotate_left_btn)
        else:  # الإنجليزية LTR
            # أزرار التنقل: السابق ← التالي
            self.buttons_layout.insertWidget(0, self.prev_btn)
            self.buttons_layout.insertWidget(1, self.next_btn)
            # أزرار التدوير: تدوير يسار ← تدوير يمين
            self.buttons_layout.insertWidget(2, self.rotate_left_btn)
            self.buttons_layout.insertWidget(3, self.rotate_right_btn)



    def on_theme_changed(self, new_theme_color):
        """استدعاء هذه الدالة عند تغيير السمة"""
        # الأزرار بيضاء شفافة بالافتراض - لا حاجة لتغيير شيء
        pass

        # Load the initial file if provided
        if self.file_path:
            self.load_pdf(self.file_path)

    def setup_optimized_view(self):
        """إعداد عرض محسن للصورة مع إخفاء التمرير إلا عند الحاجة"""

        # إعدادات العرض المحسنة للدقة العالية
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.view.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        # إعداد DragMode - بدون تدخل في التحديد
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)

        # تفعيل التفاعل مع العناصر
        self.view.setInteractive(True)

        # إخفاء شريط التمرير إلا عند الحاجة الفعلية
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # السماح للعرض بالتمدد لملء المساحة المتاحة
        from PySide6.QtWidgets import QSizePolicy
        self.view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def setup_page_transitions(self):
        """إعداد الرسوم المتحركة للانتقال بين الصفحات"""
        # بدون تأثيرات - عرض مباشر
        pass

    @property
    def zoom_factor(self):
        """الحصول على عامل الزوم الحالي"""
        return self._zoom_factor

    @zoom_factor.setter
    def zoom_factor(self, value):
        """تعيين عامل الزوم الحالي"""
        self._zoom_factor = value
        self.apply_zoom()

    def apply_zoom(self):
        """تطبيق عامل الزوم على العرض"""
        transform = QTransform().scale(self._zoom_factor, self._zoom_factor)
        self.view.setTransform(transform)
        
        # جعل الخلفية شفافة مع شريط تمرير ذكي
        self.view.setStyleSheet("""
            QGraphicsView {
                background: transparent;
                border: none;
                outline: none;
            }
            QScrollBar:vertical {
                background: rgba(45, 55, 72, 0.3);
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.4);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.6);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
            QScrollBar:horizontal {
                background: rgba(45, 55, 72, 0.3);
                height: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: rgba(255, 255, 255, 0.4);
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(255, 255, 255, 0.6);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
                background: none;
            }
        """)

        # جعل المشهد شفاف
        self.scene.setBackgroundBrush(QBrush(Qt.GlobalColor.transparent))



    def load_pdf(self, file_path):
        """تحميل PDF باستخدام النظام الجديد المحسن"""
        try:
            self.file_path = file_path

            # إيقاف أي تحميل سابق
            global_worker_manager.stop_pdf_loading()

            # مسح البيانات السابقة
            self.pages = []
            self.current_page = 0
            self.scene.clear()

            # إعداد التحميل الكسول
            success = global_page_loader.set_pdf_file(file_path)
            if not success:
                self.notification_manager.show_notification(tr("pdf_open_error"), "error")
                return

            # إعداد شريط التقدم (إذا لم يكن موجوداً)
            if not hasattr(self, 'progress_bar'):
                self.progress_bar = QProgressBar()
                self.progress_bar.setVisible(False)
                # إضافة شريط التقدم للواجهة
                if hasattr(self, 'layout'):
                    self.layout().addWidget(self.progress_bar)

            # ربط إشارات التحميل الكسول
            global_page_loader.page_ready.connect(self.on_page_loaded)
            global_page_loader.loading_started.connect(self.on_page_loading_started)
            global_page_loader.error_occurred.connect(self.on_page_loading_error)

            # تحميل الصفحة الأولى فوراً
            self.total_pages = global_page_loader.total_pages
            self.pages = [None] * self.total_pages  # قائمة فارغة بالحجم الصحيح

            # تحميل الصفحة الأولى بأولوية عالية
            first_page = global_page_loader.get_page(0, priority=True)
            if first_page:
                self.on_page_loaded(0, first_page)

            # تحميل مسبق للصفحات القريبة
            nearby_pages = list(range(1, min(5, self.total_pages)))
            global_page_loader.preload_pages(nearby_pages)

            # المستند يُدار تلقائياً بواسطة LazyPageLoader
            # لا حاجة لإغلاق doc يدوياً

            self.current_page = 0
            self.page_rotations = {i: 0 for i in range(self.total_pages)}
            self.stamps = {}  # إعادة تعيين الأختام
            self.show_page(use_transition=False)  # لا انتقال عند التحميل الأولي

            # تفعيل الأزرار بعد تحميل الملف
            self.prev_btn.setEnabled(self.total_pages > 1)
            self.next_btn.setEnabled(self.total_pages > 1)
            self.rotate_left_btn.setEnabled(True)
            self.rotate_right_btn.setEnabled(True)
            self.stamp_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

        except Exception as e:
            print(f"Error loading PDF: {e}")
            self.notification_manager.show_notification(tr("pdf_load_error", error=str(e)), "error")
            return  # الخروج من الدالة في حالة حدوث خطأ

        # إظهار إشعار النجاح فقط إذا لم تحدث أخطاء
        self.notification_manager.show_notification(tr("pdf_load_success", count=self.total_pages), "success", duration=3000)

    def on_page_loaded(self, page_number: int, pixmap: QPixmap):
        """معالج تحميل الصفحة من النظام الكسول"""
        if page_number < len(self.pages):
            self.pages[page_number] = pixmap

            # إذا كانت هذه الصفحة الحالية، اعرضها
            if page_number == self.current_page:
                self.show_page(use_transition=False)

            # إخفاء شريط التقدم إذا كانت الصفحة الأولى
            if page_number == 0 and hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(False)

    def on_page_loading_started(self, page_number: int):
        """معالج بدء تحميل الصفحة"""
        if page_number == self.current_page and hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # شريط تقدم غير محدد

    def on_page_loading_error(self, page_number: int, error_msg: str):
        """معالج خطأ تحميل الصفحة"""
        print(f"Error loading page {page_number}: {error_msg}")
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)

    def show_page(self, use_transition=True):
        """عرض الصفحة مع انتقال سلس اختياري"""
        if 0 <= self.current_page < len(self.pages):
            # استخدام إعدادات الحركات
            from modules.settings import should_enable_animations
            enable_animations = should_enable_animations() and use_transition and not self.is_transitioning
            
            if enable_animations:
                self.show_page_with_transition()
            else:
                self.show_page_direct()

    def show_page_with_transition(self):
        """عرض الصفحة بدون تأثيرات"""
        self.show_page_direct()



    def show_page_direct(self):
        """عرض الصفحة مباشرة بدون تأثيرات، مع الحفاظ على الأختام التفاعلية."""
        if not (0 <= self.current_page < len(self.pages)):
            return

        base_pixmap = self.pages[self.current_page]

        if base_pixmap is None:
            cached_pixmap = global_page_loader.get_page(self.current_page, priority=True)
            if cached_pixmap:
                base_pixmap = cached_pixmap
                self.pages[self.current_page] = base_pixmap
            else:
                self.show_loading_placeholder()
                return

        # 1. تطبيق التدوير على الصورة الأساسية
        rotation = self.page_rotations.get(self.current_page, 0)
        if rotation != 0:
            transform = QTransform().rotate(rotation)
            rotated_pixmap = base_pixmap.transformed(transform, Qt.SmoothTransformation)
        else:
            rotated_pixmap = base_pixmap

        # 2. مسح صورة الخلفية القديمة فقط
        for item in self.scene.items():
            if isinstance(item, QGraphicsPixmapItem) and not isinstance(item, InteractiveStamp):
                self.scene.removeItem(item)

        # إضافة الصورة المدورة الجديدة كخلفية
        self.scene.addPixmap(rotated_pixmap)
        self.scene.setSceneRect(rotated_pixmap.rect())

        # 3. عرض الأختام التفاعلية فوق الصورة
        self.show_page_stamps()

        # 4. ضبط العرض وتحديث التسمية
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.update_page_label()

    def show_loading_placeholder(self):
        """عرض placeholder أثناء تحميل الصفحة"""
        # مسح المشهد
        self.scene.clear()

        # إنشاء placeholder بسيط
        placeholder = QPixmap(400, 600)
        placeholder.fill(Qt.lightGray)

        # إضافة نص "جاري التحميل..."
        painter = QPainter(placeholder)
        painter.setPen(Qt.black)
        painter.drawText(placeholder.rect(), Qt.AlignCenter, tr("loading_page", page_num=self.current_page + 1))
        painter.end()

        # إضافة للمشهد
        self.scene.addPixmap(placeholder)
        self.scene.setSceneRect(placeholder.rect())
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

        # تحديث تسمية الصفحة
        self.update_page_label()

        # عرض أختام الصفحة الحالية
        self.show_page_stamps()

    def next_page(self):
        """الانتقال للصفحة التالية مع التحميل الكسول"""
        if self.current_page < len(self.pages) - 1 and not self.is_transitioning:
            self.current_page += 1

            # تحميل الصفحة إذا لم تكن محملة
            if self.pages[self.current_page] is None:
                pixmap = global_page_loader.get_page(self.current_page, priority=True)
                if pixmap:
                    self.pages[self.current_page] = pixmap

            # تحميل مسبق للصفحات القريبة
            nearby_pages = [self.current_page + i for i in range(1, 4)
                          if self.current_page + i < len(self.pages)]
            global_page_loader.preload_pages(nearby_pages)

            self.show_page(use_transition=True)

    def prev_page(self):
        """الانتقال للصفحة السابقة مع التحميل الكسول"""
        if self.current_page > 0 and not self.is_transitioning:
            self.current_page -= 1

            # تحميل الصفحة إذا لم تكن محملة
            if self.pages[self.current_page] is None:
                pixmap = global_page_loader.get_page(self.current_page, priority=True)
                if pixmap:
                    self.pages[self.current_page] = pixmap

            # تحميل مسبق للصفحات القريبة
            nearby_pages = [self.current_page - i for i in range(1, 4)
                          if self.current_page - i >= 0]
            global_page_loader.preload_pages(nearby_pages)

            self.show_page(use_transition=True)

    def rotate_left(self):
        if not self.is_transitioning:
            rotation = self.page_rotations.get(self.current_page, 0)
            self.page_rotations[self.current_page] = (rotation - 90) % 360
            self.has_unsaved_changes = True
            self.show_page(use_transition=False) # تحديث فوري بدون انتقال

    def rotate_right(self):
        if not self.is_transitioning:
            rotation = self.page_rotations.get(self.current_page, 0)
            self.page_rotations[self.current_page] = (rotation + 90) % 360
            self.has_unsaved_changes = True
            self.show_page(use_transition=False) # تحديث فوري بدون انتقال

    def update_page_label(self):
        rotation = self.page_rotations.get(self.current_page, 0)
        rotation_text = ""
        if rotation != 0:
            actual_rotation = rotation % 360
            if actual_rotation < 0:
                actual_rotation += 360
            rotation_text = tr("rotated_label", angle=actual_rotation)

        self.page_label.setText(tr("page_label", current=self.current_page + 1, total=len(self.pages), rotation=rotation_text))

    def select_file(self):
        """اختيار ملف PDF"""
        self.reset_ui()
        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(main_window.get_page_index(self), True)
        import os
        # مجلد Documents كافتراضي
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")

        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("select_pdf_file_title"), default_dir, tr("pdf_files_filter_rotate")
        )
        if file_path:
            self.load_pdf(file_path)

    def reset_rotation(self):
        """إعادة تعيين التدوير والأختام"""
        if self.pages:
            # إعادة تعيين التدوير
            self.page_rotations[self.current_page] = 0

            # إزالة أختام الصفحة الحالية
            if self.current_page in self.stamps:
                for stamp in self.stamps[self.current_page]:
                    if stamp.scene():
                        self.scene.removeItem(stamp)
                del self.stamps[self.current_page]

            self.show_page(use_transition=False)  # لا انتقال عند إعادة التعيين

    def save_file(self):
        """حفظ الملف المُدوَّر"""
        if not self.file_path or not self.pages:
            self.notification_manager.show_notification(tr("no_file_to_save"), "warning")
            return

        # اختيار مكان الحفظ
        import os
        # مجلد Documents كافتراضي مع اسم الملف
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")
        filename = os.path.basename(self.file_path).replace('.pdf', '_rotated.pdf')
        default_path = os.path.join(default_dir, filename)

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("save_file_title"),
            default_path,
            tr("pdf_files_filter_rotate")
        )

        if not save_path:
            return

        try:
            # استخدام وحدة التدوير لحفظ الملف
            from modules.rotate import rotate_specific_pages

            # تجميع الصفحات التي تم تدويرها
            rotations_to_apply = [
                (i + 1, angle) for i, angle in self.page_rotations.items() if angle != 0
            ]

            if not self.has_unsaved_changes:
                self.notification_manager.show_notification(tr("no_changes_to_save"), "info")
                return

            # طباعة معلومات التصحيح
            print("--- DEBUG: بيانات الأختام قبل الحفظ ---")
            if not self.stamps:
                print("لا توجد أختام للحفظ.")
            else:
                for page_num, stamps_list in self.stamps.items():
                    print(f"  الصفحة {page_num}: {len(stamps_list)} ختم")
                    if not stamps_list:
                        print("    قائمة الأختام فارغة.")
                        continue
                    for i, stamp_item in enumerate(stamps_list):
                        try:
                            stamp_data = stamp_item.get_stamp_data()
                            print(f"    - الختم {i}: {stamp_data}")
                        except Exception as e:
                            print(f"    - خطأ في الحصول على بيانات الختم {i}: {e}")
            print("--- نهاية DEBUG ---")

            # --- بداية التعديل لإصلاح مشكلة الختم في الصفحات العرضية ---
            # الحصول على أبعاد العرض والمشهد لتمريرها للمعالج
            view_rect = self.view.viewport().rect()
            scene_rect = self.view.sceneRect()

            print(f"أبعاد العرض (Viewport): {view_rect.width()}x{view_rect.height()}")
            print(f"أبعاد المشهد (Scene): {scene_rect.width()}x{scene_rect.height()}")

            # حفظ الملف مع التدوير والأختام وتمرير الأبعاد الجديدة
            from modules.stamp_processor import save_pdf_with_stamps
            success = save_pdf_with_stamps(
                self.file_path, 
                save_path, 
                self.page_rotations, 
                self.stamps,
                view_rect=view_rect,
                scene_rect=scene_rect
            )
            # --- نهاية التعديل ---

            if success:
                # إظهار ملخص العملية
                from modules.stamp_processor import get_stamp_summary
                stamp_summary = get_stamp_summary(self.stamps)

                message = tr("save_success_summary", path=save_path, rotated_count=len(rotations_to_apply), stamp_count=stamp_summary['total_stamps'], page_count=stamp_summary['total_pages_with_stamps'])
                
                self.notification_manager.show_notification(message, "success", duration=5000)
                self.reset_ui()
            else:
                self.notification_manager.show_notification(tr("save_failed"), "error")

        except Exception as e:
            self.notification_manager.show_notification(tr("save_error", error=str(e)), "error")

    def open_stamp_manager(self):
        """فتح نافذة إدارة الأختام"""
        try:
            from .stamp_manager import StampManager
            
            stamp_manager = StampManager(self)
            stamp_manager.stamp_selected.connect(self.start_stamp_placement)
            stamp_manager.exec()

        except Exception as e:
            print(f"Error opening stamp manager: {e}")
            import traceback
            traceback.print_exc()
            self.notification_manager.show_notification(tr("stamp_manager_error", error=str(e)), "error")

    def start_stamp_placement(self, stamp_path):
        """بدء وضع الختم التفاعلي"""
        if not self.pages:
            self.notification_manager.show_notification(tr("load_pdf_first"), "warning")
            return

        self.current_stamp_path = stamp_path
        self.placing_stamp = True

        # إنشاء معاينة الختم
        from .interactive_stamp import StampPreview
        if self.stamp_preview:
            self.scene.removeItem(self.stamp_preview)

        self.stamp_preview = StampPreview(stamp_path)
        self.scene.addItem(self.stamp_preview)

        # تغيير مؤشر الماوس ووضع العرض
        self.view.setCursor(QCursor(Qt.CrossCursor))
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)  # تعطيل السحب أثناء وضع الختم

        # إظهار إشعار توجيهي
        self.notification_manager.show_notification(tr("stamp_placement_guide"), "info", duration=5000)



    def place_stamp_at_position(self, scene_pos):
        """وضع الختم في الموضع المحدد"""
        if not self.current_stamp_path:
            return

        # إنشاء ختم تفاعلي جديد
        from .interactive_stamp import InteractiveStamp
        stamp = InteractiveStamp(self.current_stamp_path)

        # وضع الختم في الموضع المحدد
        stamp_rect = stamp.pixmap().rect()
        stamp.setPos(scene_pos.x() - stamp_rect.width()/2,
                    scene_pos.y() - stamp_rect.height()/2)

        # إضافة الختم للمشهد
        self.scene.addItem(stamp)

        # تحديد الختم فوراً لإظهار المقابض
        stamp.setSelected(True)

        # التأكد من أن الختم قابل للتحديد والتحريك (استخدام الطريقة الصحيحة)
        from PySide6.QtWidgets import QGraphicsItem
        stamp.setFlag(QGraphicsItem.ItemIsSelectable, True)
        stamp.setFlag(QGraphicsItem.ItemIsMovable, True)

        # حفظ الختم في قائمة أختام الصفحة الحالية
        if self.current_page not in self.stamps:
            self.stamps[self.current_page] = []
        self.stamps[self.current_page].append(stamp)
        self.has_unsaved_changes = True

        # تفعيل أزرار التكبير والتصغير
        self.update_stamp_buttons_state()

        # إنهاء وضع الختم بعد وضعه مباشرة
        self.end_stamp_placement()
        
        # إعادة تعيين مؤشر الماوس إلى الوضع الطبيعي
        self.view.setCursor(Qt.ArrowCursor)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)

    def zoom_selected_stamp_in(self):
        """تكبير الختم المحدد"""
        selected_stamp = self.get_selected_stamp()
        if selected_stamp:
            selected_stamp.zoom_in()
            self.has_unsaved_changes = True

    def zoom_selected_stamp_out(self):
        """تصغير الختم المحدد"""
        selected_stamp = self.get_selected_stamp()
        if selected_stamp:
            selected_stamp.zoom_out()
            self.has_unsaved_changes = True

    def get_selected_stamp(self):
        """الحصول على الختم المحدد حالياً"""
        if self.current_page in self.stamps:
            stamps_to_remove = []
            for stamp in self.stamps[self.current_page]:
                try:
                    if stamp.isSelected():
                        return stamp
                except RuntimeError:
                    # الكائن محذوف، نضيفه للقائمة المؤقتة
                    stamps_to_remove.append(stamp)
            
            # إزالة الأختام المحذوفة
            for stamp in stamps_to_remove:
                self.stamps[self.current_page].remove(stamp)
                
            # إذا لم تعد الصفحة تحتوي على أختام، نزيلها من القاموس
            if not self.stamps[self.current_page]:
                del self.stamps[self.current_page]
                
        return None

    def update_stamp_buttons_state(self):
        """تحديث حالة أزرار الختم حسب وجود ختم محدد"""
        has_selected_stamp = self.get_selected_stamp() is not None
        # إظهار/إخفاء الأزرار حسب وجود ختم محدد
        self.zoom_in_btn.setVisible(has_selected_stamp)
        self.zoom_out_btn.setVisible(has_selected_stamp)



    def end_stamp_placement(self):
        """إنهاء وضع الختم"""
        self.placing_stamp = False
        self.current_stamp_path = None

        # إزالة معاينة الختم
        if self.stamp_preview:
            self.scene.removeItem(self.stamp_preview)
            self.stamp_preview = None

        # إعادة مؤشر الماوس ووضع العرض العادي
        self.view.setCursor(Qt.ArrowCursor)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)  # الحفاظ على عدم التدخل

    def show_page_stamps(self):
        """عرض أختام الصفحة الحالية"""
        # تنظيف الأختام المحذوفة أولاً
        self.cleanup_deleted_stamps()

        # إزالة جميع الأختام من المشهد أولاً
        for page_stamps in self.stamps.values():
            for stamp in page_stamps[:]:  # نسخة من القائمة لتجنب التعديل أثناء التكرار
                try:
                    if stamp.scene():
                        self.scene.removeItem(stamp)
                except RuntimeError:
                    # الكائن محذوف، نزيله من القائمة
                    page_stamps.remove(stamp)

        # إضافة أختام الصفحة الحالية
        if self.current_page in self.stamps:
            for stamp in self.stamps[self.current_page][:]:  # نسخة من القائمة
                try:
                    self.scene.addItem(stamp)
                except RuntimeError:
                    # الكائن محذوف، نزيله من القائمة
                    self.stamps[self.current_page].remove(stamp)

    def cleanup_deleted_stamps(self):
        """تنظيف الأختام المحذوفة من جميع الصفحات"""
        for page_num in list(self.stamps.keys()):
            stamps_to_remove = []
            for stamp in self.stamps[page_num]:
                try:
                    # محاولة الوصول لخاصية من الكائن للتأكد من صحته
                    _ = stamp.pos()
                except RuntimeError:
                    # الكائن محذوف
                    stamps_to_remove.append(stamp)

            # إزالة الأختام المحذوفة
            for stamp in stamps_to_remove:
                self.stamps[page_num].remove(stamp)

            # إزالة الصفحة إذا لم تعد تحتوي على أختام
            if not self.stamps[page_num]:
                del self.stamps[page_num]

    def resizeEvent(self, event):
        """معالجة تغيير حجم النافذة للحفاظ على ملاءمة الصفحة."""
        super().resizeEvent(event)
        # استخدام مؤقت يضمن استقرار التخطيط قبل إعادة الملاءمة
        QTimer.singleShot(0, self.fit_page_in_view)

    def fit_page_in_view(self):
        """ملاءمة محتوى المشهد الحالي في العرض."""
        if self.scene and self.scene.items():
            # ملاءمة الصفحة في العرض مع الحفاظ على نسبة الأبعاد
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def reset_ui(self):
        """إعادة تعيين الواجهة إلى حالتها الأولية."""
        self.file_path = None
        self.pages = []
        self.scene.clear()
        self.page_rotations = {}
        self.stamps = {}
        self.has_unsaved_changes = False
        self.current_page = 0
        self.update_page_label()

        # تعطيل الأزرار
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.rotate_left_btn.setEnabled(False)
        self.rotate_right_btn.setEnabled(False)
        self.stamp_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.zoom_in_btn.setVisible(False)
        self.zoom_out_btn.setVisible(False)

        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(main_window.get_page_index(self), False)
