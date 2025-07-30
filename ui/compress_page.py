# -*- coding: utf-8 -*-
"""
صفحة ضغط ملفات PDF
"""

from .base_page import BasePageWidget
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QSlider, QLabel, QCheckBox,
    QGroupBox, QFormLayout, QPushButton, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt
from .theme_manager import apply_theme_style
from .svg_icon_button import create_action_button
import os

class CompressPage(BasePageWidget):
    """
    واجهة المستخدم الخاصة بوظيفة ضغط ملفات PDF.
    """
    def __init__(self, file_manager, operations_manager, parent=None):
        """
        :param file_manager: مدير الملفات لاختيار الملفات.
        :param operations_manager: مدير العمليات لتنفيذ الضغط.
        """
        super().__init__(page_title="ضغط ملفات PDF", theme_key="compress_page", parent=parent)

        self.file_manager = file_manager
        self.operations_manager = operations_manager

        # متغيرات لحفظ معلومات الملف
        self.current_file_size = 0
        self.current_file_path = ""
        self.selected_files = []

        # إضافة زر اختيار الملفات
        self.select_button = self.add_top_button(
            text="اختر ملف PDF لتقليل الحجم",
            on_click=self.select_files_for_compression
        )

        # إضافة checkbox للتبديل بين الأوضاع
        self.batch_mode_checkbox = QCheckBox("ضغط مجموعة ملفات")
        apply_theme_style(self.batch_mode_checkbox, "checkbox", auto_register=True)
        self.batch_mode_checkbox.stateChanged.connect(self.on_mode_changed)
        self.main_layout.addWidget(self.batch_mode_checkbox)

        # إنشاء الفريمات المختلفة
        self.create_save_location_frame()
        self.create_compression_slider()
        self.create_compression_info_frame()
        self.create_batch_options()

        # إضافة زر تنفيذ الضغط
        self.compress_button = self.add_action_button(
            text="ضغط الملفات",
            on_click=self.execute_compress,
            is_default=True
        )

        # إخفاء جميع الفريمات في البداية
        self.hide_all_frames()

    def create_save_location_frame(self):
        """إنشاء تخطيط أفقي لمجلد الحفظ وزر الضغط"""
        # تخطيط أفقي للفريم وزر الضغط
        self.save_and_compress_layout = QHBoxLayout()

        # فريم مجلد الحفظ
        self.save_location_frame = QGroupBox("مجلد الحفظ")
        apply_theme_style(self.save_location_frame, "group_box", auto_register=True)
        save_layout = QVBoxLayout(self.save_location_frame)

        # تخطيط أفقي للمسار والزر
        path_layout = QHBoxLayout()

        # عرض المسار الكامل
        self.save_location_label = QLabel("المسار: لم يتم اختيار ملف بعد")
        apply_theme_style(self.save_location_label, "label", auto_register=True)
        self.save_location_label.setWordWrap(True)  # للسماح بالتفاف النص

        self.browse_save_btn = create_action_button("folder-open", 24, "تغيير المجلد")
        self.browse_save_btn.set_icon_color("#ffffff")
        self.browse_save_btn.clicked.connect(self.select_save_location)

        path_layout.addWidget(self.save_location_label, 1)  # يأخذ معظم المساحة
        path_layout.addWidget(self.browse_save_btn)

        save_layout.addLayout(path_layout)

        # فريم زر الضغط
        self.single_compress_frame = QGroupBox("تنفيذ")
        apply_theme_style(self.single_compress_frame, "group_box", auto_register=True)
        compress_layout = QVBoxLayout(self.single_compress_frame)

        self.single_compress_button = create_action_button("play", 24, "تنفيذ الضغط")
        self.single_compress_button.set_icon_color("#ffffff")
        self.single_compress_button.clicked.connect(self.execute_compress)

        compress_layout.addWidget(self.single_compress_button)
        compress_layout.addStretch()

        # إضافة الفريمين للتخطيط الأفقي
        self.save_and_compress_layout.addWidget(self.save_location_frame, 2)  # يأخذ مساحة أكبر
        self.save_and_compress_layout.addWidget(self.single_compress_frame, 0)  # مساحة صغيرة

        self.main_layout.addLayout(self.save_and_compress_layout)

    def create_compression_slider(self):
        """إنشاء الشريط المئوي الجذاب بدون فريم"""
        # تخطيط للشريط والنسبة
        slider_layout = QVBoxLayout()

        # عنوان الشريط
        self.slider_title = QLabel("نسبة الضغط:")
        apply_theme_style(self.slider_title, "label", auto_register=True)
        slider_layout.addWidget(self.slider_title)

        # تخطيط أفقي للشريط والنسبة
        slider_row = QHBoxLayout()

        # الشريط المئوي
        self.compression_slider = QSlider(Qt.Horizontal)
        self.compression_slider.setMinimum(5)
        self.compression_slider.setMaximum(100)
        self.compression_slider.setValue(10)
        self.compression_slider.setTickPosition(QSlider.TicksBelow)
        self.compression_slider.setTickInterval(10)
        self.compression_slider.valueChanged.connect(self.update_compression_info)

        # تطبيق نمط متدرج الألوان للشريط (أخضر → أصفر → أحمر)
        self.compression_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #4a5568;
                height: 14px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00C851, stop:0.3 #00C851,
                    stop:0.5 #ffbb33, stop:0.7 #ffbb33,
                    stop:1 #ff4444);
                border-radius: 7px;
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #e0e0e0);
                border: 2px solid #333333;
                width: 22px;
                margin: -6px 0;
                border-radius: 11px;
            }}
            QSlider::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0f0f0, stop:1 #d0d0d0);
                border: 2px solid #555555;
            }}
            QSlider::handle:horizontal:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0e0e0, stop:1 #c0c0c0);
            }}
            QSlider::sub-page:horizontal {{
                background: transparent;
                border: none;
            }}
        """)

        # عرض النسبة
        self.compression_percentage = QLabel("10%")
        apply_theme_style(self.compression_percentage, "label", auto_register=True)
        self.compression_percentage.setMinimumWidth(50)
        self.compression_percentage.setAlignment(Qt.AlignCenter)

        slider_row.addWidget(self.compression_slider, 1)
        slider_row.addWidget(self.compression_percentage)

        slider_layout.addLayout(slider_row)
        self.main_layout.addLayout(slider_layout)

    def create_compression_info_frame(self):
        """إنشاء فريم المعلومات الثلاث في تخطيط أفقي"""
        self.info_frame = QGroupBox("معلومات الضغط")
        apply_theme_style(self.info_frame, "group_box", auto_register=True)

        # تخطيط أفقي للمعلومات الثلاث
        info_layout = QHBoxLayout(self.info_frame)

        # القسم الأول: نسبة الضغط
        compression_section = QVBoxLayout()
        compression_title = QLabel("نسبة الضغط")
        compression_title.setAlignment(Qt.AlignCenter)
        apply_theme_style(compression_title, "label", auto_register=True)
        compression_title.setStyleSheet(compression_title.styleSheet() + "font-weight: bold; background: transparent;")

        self.compression_level_label = QLabel("ضغط خفيف جداً")
        self.compression_level_label.setAlignment(Qt.AlignCenter)
        apply_theme_style(self.compression_level_label, "label", auto_register=True)

        self.compression_percent_label = QLabel("(10%)")
        self.compression_percent_label.setAlignment(Qt.AlignCenter)
        apply_theme_style(self.compression_percent_label, "label", auto_register=True)

        compression_section.addWidget(compression_title)
        compression_section.addWidget(self.compression_level_label)
        compression_section.addWidget(self.compression_percent_label)
        compression_section.addStretch()

        # القسم الثاني: الحجم المتوقع
        size_section = QVBoxLayout()
        size_title = QLabel("الحجم المتوقع")
        size_title.setAlignment(Qt.AlignCenter)
        apply_theme_style(size_title, "label", auto_register=True)
        size_title.setStyleSheet(size_title.styleSheet() + "font-weight: bold; background: transparent;")

        self.original_size_label = QLabel("الأصلي: غير معروف")
        self.original_size_label.setAlignment(Qt.AlignCenter)
        apply_theme_style(self.original_size_label, "label", auto_register=True)

        self.expected_size_label = QLabel("المتوقع: غير معروف")
        self.expected_size_label.setAlignment(Qt.AlignCenter)
        apply_theme_style(self.expected_size_label, "label", auto_register=True)

        self.savings_label = QLabel("توفير: غير معروف")
        self.savings_label.setAlignment(Qt.AlignCenter)
        apply_theme_style(self.savings_label, "label")

        size_section.addWidget(size_title)
        size_section.addWidget(self.original_size_label)
        size_section.addWidget(self.expected_size_label)
        size_section.addWidget(self.savings_label)

        # القسم الثالث: جودة الملف
        quality_section = QVBoxLayout()
        quality_title = QLabel("جودة الملف")
        quality_title.setAlignment(Qt.AlignCenter)
        apply_theme_style(quality_title, "label")
        quality_title.setStyleSheet(quality_title.styleSheet() + "font-weight: bold; background: transparent;")

        self.quality_status_label = QLabel("ممتاز ✅")
        self.quality_status_label.setAlignment(Qt.AlignCenter)
        apply_theme_style(self.quality_status_label, "label")

        self.quality_desc_label = QLabel("مناسب للضغط العالي")
        self.quality_desc_label.setAlignment(Qt.AlignCenter)
        apply_theme_style(self.quality_desc_label, "label")

        quality_section.addWidget(quality_title)
        quality_section.addWidget(self.quality_status_label)
        quality_section.addWidget(self.quality_desc_label)
        quality_section.addStretch()

        # إضافة الأقسام الثلاثة للتخطيط الأفقي
        info_layout.addLayout(compression_section, 1)
        info_layout.addLayout(size_section, 1)
        info_layout.addLayout(quality_section, 1)

        self.main_layout.addWidget(self.info_frame)

    def create_batch_options(self):
        """إنشاء خيارات الضغط المجمع"""
        # إنشاء تخطيط أفقي للفريمات الثلاثة
        self.batch_horizontal_layout = QHBoxLayout()

        # فريم مجلد الحفظ للمجموعة
        self.batch_save_frame = QGroupBox("مجلد الحفظ")
        apply_theme_style(self.batch_save_frame, "group_box")
        batch_save_layout = QVBoxLayout(self.batch_save_frame)

        self.batch_save_label = QLabel("سيتم إنشاء مجلد جديد")
        apply_theme_style(self.batch_save_label, "label")
        self.batch_save_label.setWordWrap(True)

        self.batch_browse_btn = create_action_button("folder-open", 24, "تغيير المجلد")
        self.batch_browse_btn.set_icon_color("#ffffff")
        self.batch_browse_btn.clicked.connect(self.select_batch_save_location)

        batch_save_layout.addWidget(self.batch_save_label)
        batch_save_layout.addWidget(self.batch_browse_btn)

        # فريم خيارات الضغط
        self.batch_options_frame = QGroupBox("خيارات الضغط")
        apply_theme_style(self.batch_options_frame, "group_box")
        batch_layout = QFormLayout(self.batch_options_frame)

        # مستوى ضغط ثابت
        self.batch_compression_combo = QComboBox()
        self.batch_compression_combo.addItems(["ضغط خفيف", "ضغط متوسط", "ضغط عالي", "ضغط أقصى"])
        self.batch_compression_combo.setCurrentIndex(1)  # متوسط
        apply_theme_style(self.batch_compression_combo, "combo")

        # إنشاء label مع خلفية شفافة
        compression_label = QLabel("مستوى الضغط:")
        compression_label.setStyleSheet("background: transparent; color: white;")
        batch_layout.addRow(compression_label, self.batch_compression_combo)

        # فريم زر الضغط المصغر
        self.batch_button_frame = QGroupBox("تنفيذ")
        apply_theme_style(self.batch_button_frame, "group_box")
        button_layout = QVBoxLayout(self.batch_button_frame)

        self.batch_compress_button = create_action_button("play", 24, "تنفيذ الضغط")
        self.batch_compress_button.set_icon_color("#ffffff")
        self.batch_compress_button.clicked.connect(self.execute_compress)

        button_layout.addWidget(self.batch_compress_button)
        button_layout.addStretch()

        # إضافة الفريمات الثلاثة للتخطيط الأفقي
        self.batch_horizontal_layout.addWidget(self.batch_save_frame, 2)  # يأخذ مساحة أكبر
        self.batch_horizontal_layout.addWidget(self.batch_options_frame, 1)
        self.batch_horizontal_layout.addWidget(self.batch_button_frame, 0)  # أصغر مساحة

        self.main_layout.addLayout(self.batch_horizontal_layout)

    def hide_all_frames(self):
        """إخفاء جميع الفريمات"""
        self.save_location_frame.hide()
        self.single_compress_frame.hide()
        self.slider_title.hide()
        self.compression_slider.hide()
        self.compression_percentage.hide()
        self.info_frame.hide()
        # إخفاء فريمات الضغط المجمع
        self.batch_save_frame.hide()
        self.batch_options_frame.hide()
        self.batch_button_frame.hide()
        # إخفاء زر الضغط الأصلي
        self.compress_button.hide()

    def show_single_file_mode(self):
        """إظهار خيارات الملف الواحد"""
        self.save_location_frame.show()
        self.single_compress_frame.show()
        self.slider_title.show()
        self.compression_slider.show()
        self.compression_percentage.show()
        self.info_frame.show()
        # إخفاء فريمات الضغط المجمع
        self.batch_save_frame.hide()
        self.batch_options_frame.hide()
        self.batch_button_frame.hide()
        # إخفاء فريم الملفات في وضع الملف الواحد
        self.file_list_frame.hide()
        # إخفاء زر الضغط الأصلي
        self.compress_button.hide()

    def show_batch_mode(self):
        """إظهار خيارات الضغط المجمع"""
        # إخفاء فريمات الملف الواحد
        self.save_location_frame.hide()
        self.single_compress_frame.hide()
        self.slider_title.hide()
        self.compression_slider.hide()
        self.compression_percentage.hide()
        self.info_frame.hide()

        # إظهار فريمات الضغط المجمع
        self.batch_save_frame.show()
        self.batch_options_frame.show()
        self.batch_button_frame.show()

        # إظهار فريم الملفات في وضع المجموعة
        self.file_list_frame.show()

        # إخفاء زر الضغط الأصلي
        self.compress_button.hide()

    def on_mode_changed(self):
        """التعامل مع تغيير وضع الضغط"""
        # مسح الملفات المختارة
        self.clear_files()

        # إخفاء جميع الفريمات
        self.hide_all_frames()

        # تحديث نص زر اختيار الملفات
        if self.batch_mode_checkbox.isChecked():
            self.top_buttons_layout.itemAt(0).widget().setText("اختر ملفات PDF للضغط المجمع")
        else:
            self.top_buttons_layout.itemAt(0).widget().setText("اختر ملف PDF لتقليل الحجم")

    def select_files_for_compression(self):
        """فتح حوار لاختيار ملفات PDF وتحديث القائمة"""
        if self.batch_mode_checkbox.isChecked():
            # وضع المجموعة - ملفات متعددة
            files = self.file_manager.select_pdf_files(title="اختر ملفات PDF للضغط المجمع", multiple=True)
            if files:
                self.selected_files = files
                self.file_list_frame.add_files(files)
                # إنشاء مجلد جديد بناءً على مسار أول ملف
                base_directory = os.path.dirname(files[0])
                new_folder = self.create_unique_folder(base_directory, "compressed_files")
                self.batch_save_label.setText(f"المسار: {new_folder}")
                # إظهار الفريمات والخيارات
                self.on_files_changed(files)
        else:
            # وضع الملف الواحد
            file_path = self.file_manager.select_pdf_files(title="اختر ملف PDF للضغط", multiple=False)
            if file_path and os.path.exists(file_path):
                self.selected_files = [file_path]
                self.current_file_path = file_path
                self.current_file_size = os.path.getsize(file_path)
                self.update_save_path(file_path)
                # إظهار الفريمات والخيارات
                self.on_files_changed([file_path])
            elif file_path:
                print(f"خطأ: الملف غير موجود: {file_path}")

    def update_save_path(self, file_path):
        """تحديث مسار الحفظ بناءً على مسار الملف المختار"""
        if file_path:
            directory = os.path.dirname(file_path)
            if self.batch_mode_checkbox.isChecked():
                # في وضع المجموعة، إنشاء مجلد جديد
                new_folder = self.create_unique_folder(directory, "compressed_files")
                self.batch_save_label.setText(f"المسار: {new_folder}")
            else:
                # في وضع الملف الواحد، نفس المجلد
                self.save_location_label.setText(f"المسار: {directory}")

    def create_unique_folder(self, base_path, folder_name):
        """إنشاء مجلد جديد بأسم فريد لتجنب الاستبدال"""
        counter = 1
        original_name = folder_name

        while True:
            if counter == 1:
                new_folder_path = os.path.join(base_path, original_name)
            else:
                new_folder_path = os.path.join(base_path, f"{original_name}_{counter}")

            if not os.path.exists(new_folder_path):
                try:
                    os.makedirs(new_folder_path, exist_ok=True)
                    return new_folder_path
                except Exception as e:
                    print(f"خطأ في إنشاء المجلد: {e}")
                    return base_path

            counter += 1
            # تجنب الحلقة اللانهائية
            if counter > 100:
                return base_path

    def select_save_location(self):
        """اختيار مجلد الحفظ للملف الواحد"""
        directory = self.select_directory_with_home_default("اختيار مجلد الحفظ")
        if directory:
            self.save_location_label.setText(f"المسار: {directory}")

    def select_batch_save_location(self):
        """اختيار مجلد الحفظ للمجموعة"""
        directory = self.select_directory_with_home_default("اختيار مجلد الحفظ للمجموعة")
        if directory:
            # إنشاء مجلد فرعي جديد
            new_folder = self.create_unique_folder(directory, "compressed_files")
            self.batch_save_label.setText(f"المسار: {new_folder}")

    def select_directory_with_home_default(self, title):
        """اختيار مجلد مع فتح مجلد Documents كافتراضي"""
        from PySide6.QtWidgets import QFileDialog
        import os

        # الحصول على مجلد Documents
        documents_directory = os.path.join(os.path.expanduser("~"), "Documents")

        full_title = f"ApexFlow - {title}"

        directory = QFileDialog.getExistingDirectory(
            self,
            full_title,
            documents_directory  # فتح مجلد Documents كافتراضي
        )
        return directory

    def update_compression_info(self):
        """تحديث معلومات الضغط الثلاث"""
        value = self.compression_slider.value()

        # تحديث النسبة المئوية
        self.compression_percentage.setText(f"{value}%")

        # تحديث مستوى الضغط
        compression_level = self.get_compression_level(value)
        self.compression_level_label.setText(compression_level)
        self.compression_percent_label.setText(f"({value}%)")

        # تحديث معلومات الحجم
        self.update_size_info(value)

        # تحديث جودة الملف
        self.update_quality_info(value)

    def get_compression_level(self, value):
        """تحديد مستوى الضغط بناءً على النسبة مع أوصاف واقعية"""
        if value <= 15:
            return "ضغط خفيف جداً (5-10% توفير)"
        elif value <= 30:
            return "ضغط خفيف (10-20% توفير)"
        elif value <= 50:
            return "ضغط متوسط (15-35% توفير)"
        elif value <= 70:
            return "ضغط عالي (25-50% توفير)"
        elif value <= 85:
            return "ضغط قوي (35-65% توفير)"
        else:
            return "ضغط أقصى (45-75% توفير)"

    def update_size_info(self, compression_value):
        """تحديث معلومات الحجم بحسابات واقعية"""
        if self.current_file_size > 0:
            # حساب الحجم المتوقع بناءً على نوع المحتوى وحجم الملف
            file_size_mb = self.current_file_size / (1024 * 1024)

            # تقدير واقعي للضغط حسب حجم الملف ومستوى الضغط
            compression_level = self.get_compression_level_number(compression_value)

            # نسب ضغط واقعية حسب المستوى وحجم الملف
            if file_size_mb < 1:  # ملفات صغيرة
                compression_ratios = {1: 0.05, 2: 0.10, 3: 0.15, 4: 0.25, 5: 0.35}
            elif file_size_mb < 5:  # ملفات متوسطة
                compression_ratios = {1: 0.10, 2: 0.20, 3: 0.30, 4: 0.45, 5: 0.60}
            else:  # ملفات كبيرة
                compression_ratios = {1: 0.15, 2: 0.25, 3: 0.40, 4: 0.55, 5: 0.70}

            actual_compression_ratio = compression_ratios.get(compression_level, 0.30)
            expected_size = self.current_file_size * (1 - actual_compression_ratio)
            savings = self.current_file_size - expected_size

            # تحويل إلى وحدات مناسبة
            original_text = self.format_file_size(self.current_file_size)
            expected_text = self.format_file_size(expected_size)
            savings_text = self.format_file_size(savings)
            savings_percent = (savings / self.current_file_size) * 100

            self.original_size_label.setText(f"الأصلي: {original_text}")
            self.expected_size_label.setText(f"المتوقع: {expected_text}")

            # إضافة ملاحظة للتوقعات
            if compression_level >= 4:
                self.savings_label.setText(f"توفير: {savings_text} ({savings_percent:.0f}%) *تقديري")
            else:
                self.savings_label.setText(f"توفير: {savings_text} ({savings_percent:.0f}%)")
        else:
            self.original_size_label.setText("الأصلي: غير معروف")
            self.expected_size_label.setText("المتوقع: غير معروف")
            self.savings_label.setText("توفير: غير معروف")

    def update_quality_info(self, compression_value):
        """تحديث معلومات جودة الملف بناءً على مستوى الضغط الفعلي مع ألوان"""
        if self.current_file_size == 0:
            self.quality_status_label.setText("غير معروف")
            self.quality_desc_label.setText("اختر ملف أولاً")
            return

        # تحليل ذكي لجودة الملف حسب مستوى الضغط الفعلي
        file_size_mb = self.current_file_size / (1024 * 1024)

        # تحديد الجودة والألوان حسب النسبة
        if compression_value <= 15:  # أخضر - آمن
            quality = "ممتاز 🟢"
            desc = "جودة عالية، ضغط آمن"
            color = "#00C851"
        elif compression_value <= 30:  # أخضر فاتح
            quality = "جيد جداً 🟢"
            desc = "توازن ممتاز، جودة محفوظة"
            color = "#00C851"
        elif compression_value <= 50:  # أصفر - متوسط
            quality = "جيد 🟡"
            desc = "توازن جيد بين الحجم والجودة"
            color = "#ffbb33"
        elif compression_value <= 70:  # أصفر برتقالي
            quality = "مقبول 🟠"
            desc = "قد تتأثر الجودة قليلاً"
            color = "#ff8800"
        elif compression_value <= 85:  # أحمر فاتح
            quality = "منخفض 🔴"
            desc = "ضغط قوي، فقدان في الجودة"
            color = "#ff4444"
        else:  # أحمر - خطر
            quality = "سيء ⛔"
            desc = "ضغط أقصى، فقدان كبير في الجودة"
            color = "#cc0000"

        # تطبيق اللون على النص
        self.quality_status_label.setText(quality)
        self.quality_status_label.setStyleSheet(f"color: {color}; font-weight: bold; background: transparent;")
        self.quality_desc_label.setText(desc)

    def format_file_size(self, size_bytes):
        """تحويل حجم الملف إلى وحدة مناسبة"""
        if size_bytes < 1024:
            return f"{size_bytes:.0f} بايت"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} كيلوبايت"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} ميجابايت"

    def update_expected_size(self):
        """تحديث الحجم المتوقع بناءً على نسبة الضغط"""
        if self.file_list_frame.files:
            total_size = sum(os.path.getsize(file) for file in self.file_list_frame.files)
            compression_ratio = self.compression_slider.value() / 100
            expected_size = total_size * compression_ratio

            # تحويل إلى وحدات مناسبة
            if expected_size < 1024:
                size_text = f"{expected_size:.0f} بايت"
            elif expected_size < 1024 * 1024:
                size_text = f"{expected_size / 1024:.1f} كيلوبايت"
            else:
                size_text = f"{expected_size / (1024 * 1024):.1f} ميجابايت"

            self.expected_size_label.setText(f"الحجم المتوقع بعد الضغط: {size_text}")
        else:
            self.expected_size_label.setText("الحجم المتوقع بعد الضغط: غير معروف")

    def on_quality_changed(self, quality):
        """التعامل مع تغيير الجودة"""
        # تحديث الشريط المئوي بناءً على الجودة
        quality_values = {
            "عالية جداً": 90,
            "عالية": 75,
            "متوسطة": 50,
            "منخفضة": 30,
            "منخفضة جداً": 15
        }
        if quality in quality_values:
            self.compression_slider.setValue(quality_values[quality])

    def execute_compress(self):
        """تنفيذ عملية الضغط باستخدام مدير العمليات"""
        try:
            if self.batch_mode_checkbox.isChecked():
                # وضع الملفات المتعددة
                self.execute_batch_compress()
            else:
                # وضع الملف الواحد
                self.execute_single_compress()
        except Exception as e:
            self.operations_manager.message_manager.show_error(f"خطأ في تنفيذ الضغط: {str(e)}")

    def execute_single_compress(self):
        """تنفيذ ضغط ملف واحد"""
        if not self.selected_files:
            self.operations_manager.message_manager.show_error("يجب اختيار ملف للضغط")
            return False

        file_path = self.selected_files[0]
        if not os.path.exists(file_path):
            self.operations_manager.message_manager.show_error("الملف المختار غير موجود")
            return False

        # الحصول على مسار الحفظ
        save_directory = self.save_location_label.text().replace("المسار: ", "")
        if not save_directory or save_directory == "لم يتم اختيار ملف بعد":
            save_directory = os.path.dirname(file_path)

        # إنشاء اسم الملف المضغوط
        file_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(file_name)[0]
        output_path = os.path.join(save_directory, f"{name_without_ext}_compressed.pdf")

        # تجنب الاستبدال
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(save_directory, f"{name_without_ext}_compressed_{counter}.pdf")
            counter += 1

        # تنفيذ الضغط
        compression_value = self.compression_slider.value()
        compression_level = self.get_compression_level_number(compression_value)

        success = self.operations_manager.compress_module.compress_pdf(file_path, output_path, compression_level)

        if success:
            self.operations_manager.message_manager.show_success(f"تم ضغط الملف بنجاح!\nحُفظ في: {output_path}")
            # مسح الملف المختار
            self.selected_files = []
            self.current_file_path = ""
            self.current_file_size = 0
            self.hide_all_frames()
            # إلغاء تحديد الـ checkbox والعودة للوضع الافتراضي
            self.batch_mode_checkbox.setChecked(False)
            return True
        else:
            self.operations_manager.message_manager.show_error("فشل في ضغط الملف")
            return False

    def execute_batch_compress(self):
        """تنفيذ ضغط مجموعة ملفات"""
        if not self.selected_files:
            self.operations_manager.message_manager.show_error("يجب اختيار ملفات للضغط")
            return False

        # الحصول على مجلد الحفظ
        save_directory = self.batch_save_label.text().replace("المسار: ", "")
        if not save_directory or save_directory == "سيتم إنشاء مجلد جديد":
            # إنشاء مجلد جديد
            base_directory = os.path.dirname(self.selected_files[0])
            save_directory = self.create_unique_folder(base_directory, "compressed_files")

        # التأكد من وجود المجلد
        if not os.path.exists(save_directory):
            try:
                os.makedirs(save_directory, exist_ok=True)
            except Exception as e:
                self.operations_manager.message_manager.show_error(f"فشل في إنشاء مجلد الحفظ: {str(e)}")
                return False

        # الحصول على مستوى الضغط
        compression_text = self.batch_compression_combo.currentText()
        compression_level = self.get_batch_compression_level(compression_text)

        # ضغط كل ملف
        successful_files = 0
        failed_files = 0

        for file_path in self.selected_files:
            if not os.path.exists(file_path):
                failed_files += 1
                continue

            # إنشاء اسم الملف المضغوط
            file_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(file_name)[0]
            output_path = os.path.join(save_directory, f"{name_without_ext}_compressed.pdf")

            # تجنب الاستبدال
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(save_directory, f"{name_without_ext}_compressed_{counter}.pdf")
                counter += 1

            # تنفيذ الضغط
            success = self.operations_manager.compress_module.compress_pdf(file_path, output_path, compression_level)

            if success:
                successful_files += 1
            else:
                failed_files += 1

        # عرض النتائج
        if successful_files > 0:
            message = f"تم ضغط {successful_files} ملف بنجاح!"
            if failed_files > 0:
                message += f"\nفشل في ضغط {failed_files} ملف."
            message += f"\nحُفظت الملفات في: {save_directory}"
            self.operations_manager.message_manager.show_success(message)

            # مسح الملفات المختارة
            self.selected_files = []
            self.file_list_frame.clear_all_files()
            self.hide_all_frames()
            # إلغاء تحديد الـ checkbox والعودة للوضع الافتراضي
            self.batch_mode_checkbox.setChecked(False)
            return True
        else:
            self.operations_manager.message_manager.show_error("فشل في ضغط جميع الملفات")
            return False

    def get_compression_level_number(self, percentage):
        """تحويل النسبة المئوية إلى مستوى ضغط رقمي"""
        if percentage <= 15:
            return 1  # ضغط خفيف جداً
        elif percentage <= 30:
            return 2  # ضغط خفيف
        elif percentage <= 50:
            return 3  # ضغط متوسط
        elif percentage <= 70:
            return 4  # ضغط عالي
        elif percentage <= 85:
            return 5  # ضغط قوي
        else:
            return 5  # ضغط أقصى (نفس المستوى 5)

    def get_batch_compression_level(self, compression_text):
        """تحويل نص مستوى الضغط إلى رقم"""
        levels = {
            "ضغط خفيف": 2,
            "ضغط متوسط": 3,
            "ضغط عالي": 4,
            "ضغط أقصى": 5
        }
        return levels.get(compression_text, 3)

    def on_files_changed(self, files):
        """إظهار أو إخفاء الخيارات بناءً على عدد الملفات"""
        if len(files) == 0:
            # لا ملفات = لا خيارات
            self.hide_all_frames()
            # إعادة تعيين المتغيرات
            self.current_file_size = 0
            self.current_file_path = ""
            self.selected_files = []
        elif len(files) >= 1:
            # ملفات موجودة = إظهار الخيارات المناسبة للوضع
            self.selected_files = files
            if self.batch_mode_checkbox.isChecked():
                self.show_batch_mode()
            else:
                self.show_single_file_mode()
                # تحديث معلومات الملف الواحد
                file_path = files[0] if files else None
                if file_path and os.path.exists(file_path):
                    self.current_file_path = file_path
                    self.current_file_size = os.path.getsize(file_path)
                    self.update_compression_info()
