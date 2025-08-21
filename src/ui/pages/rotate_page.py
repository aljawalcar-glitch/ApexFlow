# -*- coding: utf-8 -*-
"""
صفحة تدوير ملفات PDF
"""

from PySide6.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QLabel, QFileDialog, QMessageBox, QGraphicsOpacityEffect, QProgressBar, QGraphicsPixmapItem, QGraphicsSceneWheelEvent)
from PySide6.QtGui import QPixmap, QImage, QTransform, QCursor, QBrush, QPainter
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QThread, QSize
import fitz  # PyMuPDF
from src.ui.widgets.interactive_stamp import InteractiveStamp
from src.ui.widgets.svg_icon_button import create_navigation_button, create_action_button
from src.ui.widgets.icon_utils import create_colored_icon_button
from src.ui.widgets.theme_aware_widget import make_theme_aware
from PySide6.QtWidgets import QWidget
from src.utils.i18n import tr
from managers.language_manager import language_manager

# استيراد الأنظمة الجديدة للأداء
from src.utils.lazy_loader import global_page_loader
from src.utils.smart_cache import pdf_cache
from src.core.pdf_worker import global_worker_manager
from src.core.stamp_processor import StampWorker

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
        make_theme_aware(self, "rotate_page")

        # تفعيل السحب والإفلات
        self.setAcceptDrops(True)
        
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

        # متغيرات شريط التقدم
        self.progress_bar = None  # شريط التقدم العائم
        self.progress_timer = None  # مؤقت تحديث التقدم

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
        make_theme_aware(self.page_label, "label")
        self.update_page_label()


        # أقصى الشمال: التنقل
        self.prev_btn = create_colored_icon_button("chevron-left", 24, "", tr("previous_page"))
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.prev_page)
        # التأكد من ظهور الأيقونة
        self.prev_btn.setIconSize(QSize(20, 20))

        self.next_btn = create_colored_icon_button("chevron-right", 24, "", tr("next_page"))
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.next_page)
        # التأكد من ظهور الأيقونة
        self.next_btn.setIconSize(QSize(20, 20))

        # أزرار التدوير (شمال) - أيقونات تدوير حقيقية
        self.rotate_left_btn = create_colored_icon_button("rotate-ccw", 24, "", tr("rotate_left_tooltip"))
        self.rotate_left_btn.setEnabled(False)
        self.rotate_left_btn.clicked.connect(self.rotate_left)
        # التأكد من ظهور الأيقونة
        self.rotate_left_btn.setIconSize(QSize(20, 20))

        self.rotate_right_btn = create_colored_icon_button("rotate-cw", 24, "", tr("rotate_right_tooltip"))
        self.rotate_right_btn.setEnabled(False)
        self.rotate_right_btn.clicked.connect(self.rotate_right)
        # التأكد من ظهور الأيقونة
        self.rotate_right_btn.setIconSize(QSize(20, 20))

        # زر الختم
        self.stamp_btn = create_colored_icon_button("stamp", 24, "", tr("add_stamp_tooltip"))
        self.stamp_btn.setEnabled(False)
        self.stamp_btn.clicked.connect(self.open_stamp_manager)
        # التأكد من ظهور الأيقونة
        self.stamp_btn.setIconSize(QSize(20, 20))

        # أزرار تكبير وتصغير الختم (مخفية في البداية)
        self.zoom_in_btn = create_colored_icon_button("stamp-zoom-in", 24, "", tr("zoom_in_tooltip"))
        self.zoom_in_btn.setVisible(False)  # مخفي في البداية
        self.zoom_in_btn.clicked.connect(self.zoom_selected_stamp_in)
        # التأكد من ظهور الأيقونة
        self.zoom_in_btn.setIconSize(QSize(20, 20))

        self.zoom_out_btn = create_colored_icon_button("stamp-zoom-out", 24, "", tr("zoom_out_tooltip"))
        self.zoom_out_btn.setVisible(False)  # مخفي في البداية
        self.zoom_out_btn.clicked.connect(self.zoom_selected_stamp_out)
        # التأكد من ظهور الأيقونة
        self.zoom_out_btn.setIconSize(QSize(20, 20))

        # اليمين: إدارة الملفات
        self.file_btn = create_colored_icon_button("folder-open", 24, "", tr("select_pdf_file_tooltip"))
        self.file_btn.clicked.connect(self.select_file)
        # التأكد من ظهور الأيقونة
        self.file_btn.setIconSize(QSize(20, 20))

        self.reset_btn = create_colored_icon_button("refresh-cw", 24, "", tr("reset_rotation_tooltip"))
        self.reset_btn.setEnabled(False)
        self.reset_btn.clicked.connect(self.reset_rotation)
        # التأكد من ظهور الأيقونة
        self.reset_btn.setIconSize(QSize(20, 20))

        self.save_btn = create_colored_icon_button("save", 24, "", tr("save_rotated_file_tooltip"))
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_file)
        # التأكد من ظهور الأيقونة
        self.save_btn.setIconSize(QSize(20, 20))

        # تخطيط الأزرار أفقي
        buttons_layout = QHBoxLayout()

        # ترتيب أزرار التنقل والتدوير حسب اللغة
        if language_manager.get_direction() == Qt.RightToLeft:  # العربية RTL
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

        # ربط إشارة تغيير اللغة بتحديث ترتيب الأزرار
        language_manager.language_changed.connect(self.update_button_order_for_language)

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

    def update_button_order_for_language(self, lang_code=None, direction=None):
        """إعادة ترتيب أزرار التنقل والتدوير عند تغيير اللغة"""
        # مسح التخطيط القديم بالكامل
        while self.buttons_layout.count():
            item = self.buttons_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # إعادة بناء التخطيط بالترتيب الصحيح
        if language_manager.get_direction() == Qt.RightToLeft:  # العربية RTL
            self.buttons_layout.addWidget(self.next_btn)
            self.buttons_layout.addWidget(self.prev_btn)
            self.buttons_layout.addWidget(self.rotate_right_btn)
            self.buttons_layout.addWidget(self.rotate_left_btn)
        else:  # الإنجليزية LTR
            self.buttons_layout.addWidget(self.prev_btn)
            self.buttons_layout.addWidget(self.next_btn)
            self.buttons_layout.addWidget(self.rotate_left_btn)
            self.buttons_layout.addWidget(self.rotate_right_btn)
            
        self.buttons_layout.addWidget(self.stamp_btn)
        self.buttons_layout.addWidget(self.zoom_in_btn)
        self.buttons_layout.addWidget(self.zoom_out_btn)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.save_btn)
        self.buttons_layout.addWidget(self.reset_btn)
        self.buttons_layout.addWidget(self.file_btn)



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
        make_theme_aware(self.view, "rotate_page_view")

        # جعل المشهد شفاف
        self.scene.setBackgroundBrush(QBrush(Qt.GlobalColor.transparent))



    def load_pdf(self, file_path):
        """تحميل PDF باستخدام النظام الجديد المحسن"""
        try:
            self.file_path = file_path

            # إيقاف أي تحميل سابق
            global_worker_manager.stop_worker(self.file_path)

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
            # أزرار التكبير والتصغير مخفية في البداية وتظهر فقط عند تحديد ختم
            self.zoom_in_btn.setVisible(False)
            self.zoom_out_btn.setVisible(False)

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
            if page_number == 0 and hasattr(self, 'progress_bar') and self.progress_bar is not None:
                self.progress_bar.setVisible(False)

    def on_page_loading_started(self, page_number: int):
        """معالج بدء تحميل الصفحة"""
        if page_number == self.current_page and hasattr(self, 'progress_bar') and self.progress_bar is not None:
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
            from src.utils.settings import should_enable_animations
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
        """حفظ الملف المُدوَّر باستخدام خيط منفصل."""
        if not self.file_path or not self.pages:
            self.notification_manager.show_notification(tr("no_file_to_save"), "warning")
            return

        if not self.has_unsaved_changes:
            self.notification_manager.show_notification(tr("no_changes_to_save"), "info")
            return

        import os
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")
        filename = os.path.basename(self.file_path).replace('.pdf', '_rotated.pdf')
        default_path = os.path.join(default_dir, filename)

        save_path, _ = QFileDialog.getSaveFileName(
            self, tr("save_file_title"), default_path, tr("pdf_files_filter_rotate")
        )

        if not save_path:
            return

        # إعداد شريط التقدم
        if not self.progress_bar:
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setTextVisible(True)
            # إضافة شريط التقدم إلى التخطيط السفلي
            self.buttons_layout.insertWidget(self.buttons_layout.count() - 1, self.progress_bar, 1)
        
        self.progress_bar.setVisible(True)
        self.set_buttons_enabled(False)

        # إنشاء وتشغيل العامل
        self.thread = QThread()
        self.worker = StampWorker(
            self.file_path,
            save_path,
            self.page_rotations,
            self.stamps,
            self.view.viewport().rect(),
            self.view.sceneRect()
        )
        self.worker.moveToThread(self.thread)

        # ربط الإشارات
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_save_finished)
        self.worker.error.connect(self.on_save_error)
        self.worker.progress.connect(self.on_save_progress)
        
        # تنظيف عند الانتهاء
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def set_buttons_enabled(self, enabled):
        """تفعيل أو تعطيل أزرار التحكم أثناء الحفظ."""
        self.prev_btn.setEnabled(enabled)
        self.next_btn.setEnabled(enabled)
        self.rotate_left_btn.setEnabled(enabled)
        self.rotate_right_btn.setEnabled(enabled)
        self.stamp_btn.setEnabled(enabled)
        self.reset_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        self.file_btn.setEnabled(enabled)

    def on_save_progress(self, current_page, total_pages):
        """تحديث شريط التقدم."""
        if total_pages > 0:
            progress_value = int((current_page / total_pages) * 100)
            self.progress_bar.setValue(progress_value)
            self.progress_bar.setFormat(f"{tr('saving_progress')} {progress_value}%")

    def on_save_finished(self, success, output_path, summary):
        """معالجة انتهاء عملية الحفظ."""
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)

        if success:
            rotations_to_apply = [
                (i + 1, angle) for i, angle in self.page_rotations.items() if angle != 0
            ]
            message = tr("save_success_summary", path=output_path, rotated_count=len(rotations_to_apply), stamp_count=summary['total_stamps'], page_count=summary['total_pages_with_stamps'])
            self.notification_manager.show_notification(message, "success", duration=5000)
            self.reset_ui()
        else:
            # قد يكون الإلغاء هو السبب، لا نظهر رسالة خطأ
            if not (hasattr(self.worker, 'is_cancelled') and self.worker.is_cancelled):
                 self.notification_manager.show_notification(tr("save_failed"), "error")

    def on_save_error(self, error_message):
        """معالجة خطأ أثناء الحفظ."""
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        self.notification_manager.show_notification(tr("save_error", error=error_message), "error")

    def open_stamp_manager(self):
        """فتح نافذة إدارة الأختام"""
        try:
            from src.ui.widgets.stamp_manager import StampManager
            
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
        from src.ui.widgets.interactive_stamp import StampPreview
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
        from src.ui.widgets.interactive_stamp import InteractiveStamp
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

    def zoom_in(self):
        """تكبير عرض الصفحة (محفوظة للتوافق)"""
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        """تصغير عرض الصفحة (محفوظة للتوافق)"""
        self.view.scale(1 / 1.2, 1 / 1.2)

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
        # أزرار التكبير والتصغير تظهر فقط عند تحديد ختم
        self.zoom_in_btn.setVisible(has_selected_stamp)
        self.zoom_out_btn.setVisible(has_selected_stamp)
        self.zoom_in_btn.setEnabled(has_selected_stamp)
        self.zoom_out_btn.setEnabled(has_selected_stamp)



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
        # تأكد من وجود العرض والمشهد
        if not hasattr(self, "view") or self.view is None:
            self.view = InteractiveGraphicsView()
            self.view.set_parent_page(self)
            
        if not hasattr(self, "scene") or self.scene is None:
            self.scene = QGraphicsScene()
            self.view.setScene(self.scene)
            
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
        self.zoom_in_btn.setEnabled(False)
        self.zoom_out_btn.setEnabled(False)

        main_window = self._get_main_window()
        if main_window:
            main_window.set_page_has_work(main_window.get_page_index(self), False)

    def dragEnterEvent(self, event):
        """عند دخول ملفات مسحوبة إلى منطقة الصفحة"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """عند إفلات الملفات في منطقة الصفحة"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            files = [url.toLocalFile() for url in urls if url.isLocalFile()]
            
            if files:
                main_window = self._get_main_window()
                if main_window and hasattr(main_window, 'smart_drop_overlay'):
                    # تحديث وضع الطبقة الذكية بناءً على الصفحة الحالية
                    main_window._update_smart_drop_mode_for_page(main_window.stack.currentIndex())
                    
                    # تعيين الملفات والتحقق من صحتها
                    main_window.smart_drop_overlay.files = files
                    main_window.smart_drop_overlay.is_valid_drop = main_window.smart_drop_overlay._validate_files_for_context(files)
                    
                    # تعطيل النافذة الرئيسية بالكامل عند تفعيل واجهة الافلات
                    main_window.setEnabled(False)
                    
                    # التقاط وتطبيق تأثير البلور على الخلفية
                    main_window.smart_drop_overlay.capture_background_blur()
                    main_window.smart_drop_overlay.update_styles()
                    main_window.smart_drop_overlay.update_ui_for_context()
                    
                    # إظهار الطبقة مع تأثير انتقالي سلس
                    main_window.smart_drop_overlay.animate_show()
                    
                    # معالجة الإفلات
                    main_window.smart_drop_overlay.handle_drop(event)
                    event.acceptProposedAction()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    def add_files(self, files):
        """إضافة ملفات مباشرة إلى القائمة (للسحب والإفلات)"""
        if files:
            # صفحة التدوير تقبل ملف واحد فقط
            self.load_pdf(files[0])

    def handle_smart_drop_action(self, action_type, files):
        """معالجة الإجراء المحدد من الطبقة الذكية"""
        if action_type == "add_to_list":
            self.add_files(files)
