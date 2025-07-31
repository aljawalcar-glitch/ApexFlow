# -*- coding: utf-8 -*-
"""
صفحة تدوير ملفات PDF
"""

from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QLabel, QFileDialog, QMessageBox, QGraphicsOpacityEffect, QProgressBar)
from PySide6.QtGui import QPixmap, QImage, QTransform, QCursor, QBrush, QPainter
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
import fitz  # PyMuPDF
from .svg_icon_button import create_navigation_button, create_action_button
from .theme_aware_widget import make_theme_aware
from .notification_system import show_success, show_warning, show_error, show_info
from PySide6.QtWidgets import QWidget
from modules.translator import tr

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
            self.parent_page.placing_stamp and
            event.button() == Qt.LeftButton):

            scene_pos = self.mapToScene(event.pos())
            self.parent_page.place_stamp_at_position(scene_pos)
            return  # لا نستدعي المعالج الأصلي هنا

        # استدعاء المعالج الأصلي للسماح للعناصر التفاعلية بالعمل
        super().mousePressEvent(event)

class RotatePage(QWidget):
    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)
        self.theme_handler = make_theme_aware(self, "rotate_page")
        
        self.file_path = file_path
        self.current_page = 0
        self.page_rotations = {}  # قاموس لتخزين زاوية دوران كل صفحة
        self.pages = []  # List to store loaded pages as images

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

        # أقصى الشمال: التنقل
        buttons_layout.addWidget(self.prev_btn)         # ⬅️ السابق
        buttons_layout.addWidget(self.next_btn)         # ➡️ التالي

        # شمال: أزرار التدوير والختم
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
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

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
                show_error(self, tr("pdf_open_error"))
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
            self.page_rotations = {i: 0 for i in range(len(self.pages))}  # إعادة تعيين لكل صفحة
            self.stamps = {}  # إعادة تعيين الأختام
            self.show_page(use_transition=False)  # لا انتقال عند التحميل الأولي

            # تفعيل الأزرار بعد تحميل الملف
            self.prev_btn.setEnabled(len(self.pages) > 1)
            self.next_btn.setEnabled(len(self.pages) > 1)
            self.rotate_left_btn.setEnabled(True)
            self.rotate_right_btn.setEnabled(True)
            self.stamp_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

            # إشعار بالتحسينات الجديدة
            show_success(self, tr("pdf_load_success", count=len(self.pages)), duration=3000)

        except Exception as e:
            print(f"Error loading PDF: {e}")
            show_error(self, tr("pdf_load_error", error=str(e)))

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
            if use_transition and not self.is_transitioning:
                self.show_page_with_transition()
            else:
                self.show_page_direct()

    def show_page_with_transition(self):
        """عرض الصفحة بدون تأثيرات"""
        self.show_page_direct()



    def show_page_direct(self):
        """عرض الصفحة مباشرة بدون تأثيرات"""
        if 0 <= self.current_page < len(self.pages):
            pixmap = self.pages[self.current_page]

            # التحقق من نوع البيانات
            if pixmap is None:
                # إذا لم تكن الصفحة محملة، اطلب تحميلها
                cached_pixmap = global_page_loader.get_page(self.current_page, priority=True)
                if cached_pixmap:
                    pixmap = cached_pixmap
                    self.pages[self.current_page] = pixmap
                else:
                    # عرض placeholder أثناء التحميل
                    self.show_loading_placeholder()
                    return

            # التعامل مع QPixmap مباشرة (النظام الجديد)
            if isinstance(pixmap, QPixmap):
                qpixmap = pixmap
            else:
                # التعامل مع fitz.Pixmap (النظام القديم - للتوافق)
                qimage = QImage(
                    pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, QImage.Format_RGB888
                )
                qpixmap = QPixmap.fromImage(qimage)

            # تطبيق التدوير إذا كان مطلوباً
            rotation = self.page_rotations.get(self.current_page, 0)
            if rotation != 0:
                transform = QTransform().rotate(rotation)
                qpixmap = qpixmap.transformed(transform, Qt.SmoothTransformation)

            # مسح المشهد وإضافة الصورة الجديدة
            self.scene.clear()
            self.scene.addPixmap(qpixmap)

            # ضبط حجم المشهد ليطابق الصورة
            self.scene.setSceneRect(qpixmap.rect())

            # عرض الصورة بحجم أكبر مع الحفاظ على النسبة
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

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
            self.show_page(use_transition=True)

    def rotate_right(self):
        if not self.is_transitioning:
            rotation = self.page_rotations.get(self.current_page, 0)
            self.page_rotations[self.current_page] = (rotation + 90) % 360
            self.show_page(use_transition=True)

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
            show_warning(self, tr("no_file_to_save"))
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

            # فحص وجود أختام
            has_stamps = any(len(stamps) > 0 for stamps in self.stamps.values())

            if not rotations_to_apply and not has_stamps:
                show_info(self, tr("no_changes_to_save"))
                return

            # طباعة معلومات التصحيح
            print(f"حفظ الملف: {len(self.stamps)} صفحة تحتوي على أختام")
            for page_num, stamps in self.stamps.items():
                print(f"الصفحة {page_num + 1}: {len(stamps)} ختم")
                for i, stamp in enumerate(stamps):
                    stamp_data = stamp.get_stamp_data()
                    print(f"  الختم {i+1}: الموضع={stamp_data['position']}, المقياس={stamp_data['scale']}, الشفافية={stamp_data['opacity']}")

            # حساب عامل تحجيم العرض
            view_scale_factor = 1.0
            if hasattr(self, 'view') and hasattr(self.view, 'transform'):
                transform = self.view.transform()
                view_scale_factor = transform.m11()  # عامل التحجيم الأفقي

            print(f"عامل تحجيم العرض المحسوب: {view_scale_factor}")

            # حفظ الملف مع التدوير والأختام
            from modules.stamp_processor import save_pdf_with_stamps
            success = save_pdf_with_stamps(self.file_path, save_path, self.page_rotations, self.stamps, view_scale_factor)

            if success:
                # إظهار ملخص العملية
                from modules.stamp_processor import get_stamp_summary
                stamp_summary = get_stamp_summary(self.stamps)

                message = tr("save_success_summary", path=save_path, rotated_count=len(rotations_to_apply), stamp_count=stamp_summary['total_stamps'], page_count=stamp_summary['total_pages_with_stamps'])
                
                show_success(self, message, duration=5000)
            else:
                show_error(self, tr("save_failed"))

        except Exception as e:
            show_error(self, tr("save_error", error=str(e)))

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
            show_error(self, tr("stamp_manager_error", error=str(e)))

    def start_stamp_placement(self, stamp_path):
        """بدء وضع الختم التفاعلي"""
        if not self.pages:
            show_warning(self, tr("load_pdf_first"))
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
        show_info(self, tr("stamp_placement_guide"), duration=5000)



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



        # تفعيل أزرار التكبير والتصغير
        self.update_stamp_buttons_state()

    def zoom_selected_stamp_in(self):
        """تكبير الختم المحدد"""
        selected_stamp = self.get_selected_stamp()
        if selected_stamp:
            selected_stamp.zoom_in()

    def zoom_selected_stamp_out(self):
        """تصغير الختم المحدد"""
        selected_stamp = self.get_selected_stamp()
        if selected_stamp:
            selected_stamp.zoom_out()

    def get_selected_stamp(self):
        """الحصول على الختم المحدد حالياً"""
        if self.current_page in self.stamps:
            for stamp in self.stamps[self.current_page]:
                if stamp.isSelected():
                    return stamp
        return None

    def update_stamp_buttons_state(self):
        """تحديث حالة أزرار الختم حسب وجود ختم محدد"""
        has_selected_stamp = self.get_selected_stamp() is not None
        # إظهار/إخفاء الأزرار حسب وجود ختم محدد
        self.zoom_in_btn.setVisible(has_selected_stamp)
        self.zoom_out_btn.setVisible(has_selected_stamp)

        # إنهاء وضع الختم
        self.end_stamp_placement()



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
