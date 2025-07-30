#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل لتكامل إعدادات الخط في جميع التبويبات
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                               QHBoxLayout, QPushButton, QSlider, QLabel, QComboBox,
                               QTabWidget)
from PySide6.QtCore import Qt
from ui.theme_manager import global_theme_manager, refresh_all_fonts
from modules.settings import load_settings, save_settings

# استيراد جميع التبويبات
from ui.merge_page import MergePage
from ui.split_page import SplitPage
from ui.compress_page import CompressPage
from ui.rotate_page import RotatePage
from ui.convert_page import ConvertPage
from ui.security_page import SecurityPage
from ui.settings_ui import SettingsUI

class AllTabsTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار تكامل الخط - جميع التبويبات")
        self.setGeometry(100, 100, 1400, 900)
        
        # تحميل السمة من الإعدادات
        global_theme_manager.load_theme_from_settings()
        
        # إنشاء الواجهة الرئيسية
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # إنشاء أدوات التحكم في الخط
        controls_layout = QHBoxLayout()
        
        # شريط تمرير حجم الخط
        font_size_label = QLabel("حجم الخط:")
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(10, 24)
        self.font_size_slider.setValue(14)
        self.font_size_value_label = QLabel("14")
        self.font_size_slider.valueChanged.connect(self.update_font_size)
        
        # قائمة نوع الخط
        font_family_label = QLabel("نوع الخط:")
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "النظام الافتراضي",
            "Arial",
            "Tahoma",
            "Segoe UI",
            "Cairo"
        ])
        self.font_family_combo.currentTextChanged.connect(self.update_font_family)
        
        # قائمة وزن الخط
        font_weight_label = QLabel("وزن الخط:")
        self.font_weight_combo = QComboBox()
        self.font_weight_combo.addItems([
            "عادي",
            "سميك",
            "سميك جداً"
        ])
        self.font_weight_combo.currentTextChanged.connect(self.update_font_weight)
        
        # إضافة أدوات التحكم
        controls_layout.addWidget(font_size_label)
        controls_layout.addWidget(self.font_size_slider)
        controls_layout.addWidget(self.font_size_value_label)
        controls_layout.addWidget(font_family_label)
        controls_layout.addWidget(self.font_family_combo)
        controls_layout.addWidget(font_weight_label)
        controls_layout.addWidget(self.font_weight_combo)
        controls_layout.addStretch()
        
        main_layout.addLayout(controls_layout)
        
        # إنشاء التبويبات
        self.tab_widget = QTabWidget()
        
        # إنشاء مدراء وهميين للاختبار
        class DummyManager:
            def __getattr__(self, name):
                return lambda *args, **kwargs: print(f"تم استدعاء {name} مع {args}, {kwargs}")
        
        file_manager = DummyManager()
        operations_manager = DummyManager()
        
        # إضافة التبويبات
        try:
            merge_page = MergePage(file_manager, operations_manager)
            self.tab_widget.addTab(merge_page, "دمج وطباعة")
        except Exception as e:
            print(f"خطأ في تحميل تبويب الدمج: {e}")
        
        try:
            split_page = SplitPage(file_manager, operations_manager)
            self.tab_widget.addTab(split_page, "تقسيم")
        except Exception as e:
            print(f"خطأ في تحميل تبويب التقسيم: {e}")
        
        try:
            compress_page = CompressPage(file_manager, operations_manager)
            self.tab_widget.addTab(compress_page, "ضغط")
        except Exception as e:
            print(f"خطأ في تحميل تبويب الضغط: {e}")
        
        try:
            rotate_page = RotatePage()
            self.tab_widget.addTab(rotate_page, "تدوير")
        except Exception as e:
            print(f"خطأ في تحميل تبويب التدوير: {e}")
        
        try:
            convert_page = ConvertPage(operations_manager)
            self.tab_widget.addTab(convert_page, "تحويل")
        except Exception as e:
            print(f"خطأ في تحميل تبويب التحويل: {e}")
        
        try:
            security_page = SecurityPage(file_manager, operations_manager)
            self.tab_widget.addTab(security_page, "حماية وخصائص")
        except Exception as e:
            print(f"خطأ في تحميل تبويب الحماية: {e}")
        
        main_layout.addWidget(self.tab_widget)
        
        self.setCentralWidget(main_widget)
        
        # تطبيق السمة على النافذة الرئيسية
        from ui.theme_manager import apply_theme_style
        apply_theme_style(self, "main_window", auto_register=True)
        
        # تطبيق السمة على أدوات التحكم
        apply_theme_style(font_size_label, "label", auto_register=True)
        apply_theme_style(self.font_size_value_label, "label", auto_register=True)
        apply_theme_style(font_family_label, "label", auto_register=True)
        apply_theme_style(font_weight_label, "label", auto_register=True)
        apply_theme_style(self.font_family_combo, "combo", auto_register=True)
        apply_theme_style(self.font_weight_combo, "combo", auto_register=True)
        apply_theme_style(self.font_size_slider, "slider", auto_register=True)
        apply_theme_style(self.tab_widget, "frame", auto_register=True)
        
    def update_font_size(self, value):
        """تحديث حجم الخط"""
        self.font_size_value_label.setText(str(value))
        self.apply_font_changes()
        
    def update_font_family(self, family):
        """تحديث نوع الخط"""
        self.apply_font_changes()
        
    def update_font_weight(self, weight):
        """تحديث وزن الخط"""
        self.apply_font_changes()
        
    def apply_font_changes(self):
        """تطبيق تغييرات الخط"""
        # تحديث الإعدادات
        settings_data = load_settings()
        ui_settings = settings_data.get("ui_settings", {})
        
        ui_settings["font_size"] = self.font_size_slider.value()
        ui_settings["font_family"] = self.font_family_combo.currentText()
        ui_settings["font_weight"] = self.font_weight_combo.currentText()
        
        settings_data["ui_settings"] = ui_settings
        save_settings(settings_data)
        
        # إعادة تطبيق الخطوط على جميع العناصر
        refresh_all_fonts()
        
        print(f"تم تحديث الخط: حجم={ui_settings['font_size']}, نوع={ui_settings['font_family']}, وزن={ui_settings['font_weight']}")

def test_all_tabs_font_integration():
    """اختبار تكامل الخط في جميع التبويبات"""
    app = QApplication(sys.argv)
    
    print("اختبار تكامل الخط في جميع التبويبات")
    print("=" * 50)
    print("استخدم أدوات التحكم في الأعلى لتغيير إعدادات الخط")
    print("تنقل بين التبويبات لمشاهدة التأثير على جميع العناصر")
    print("=" * 50)
    
    # إنشاء النافذة
    window = AllTabsTestWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    test_all_tabs_font_integration()
