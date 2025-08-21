# -*- coding: utf-8 -*-
"""
أدوات مساعدة للتعامل مع الأيقونات الملونة في التطبيق
Icon utilities for handling colored icons throughout the application
"""

from PySide6.QtWidgets import QPushButton, QListWidgetItem
from PySide6.QtGui import QIcon
from .svg_icon_button import create_colored_icon

def create_colored_icon_button(icon_name, size=18, text="", tooltip=""):
    """
    إنشاء زر مع أيقونة ملونة باستخدام لون التمييز الحالي

    Args:
        icon_name: اسم الأيقونة (بدون امتداد)
        size: حجم الأيقونة بالبكسل
        text: نص الزر (اختياري)
        tooltip: تلميح الزر (اختياري)

    Returns:
        QPushButton: زر مع أيقونة ملونة
    """
    from src.managers.theme_manager import make_theme_aware

    # إنشاء الزر بأيقونة فقط (بدون نص ظاهر)
    button = QPushButton()
    button.setText("")  # التأكد من عدم وجود نص

    # تعيين التلميح إذا تم توفيره
    if tooltip:
        from src.utils.settings import should_show_tooltips
        if should_show_tooltips():
            button.setToolTip(tooltip)

    # تعيين حجم الأيقونة
    from PySide6.QtCore import QSize
    button.setIconSize(QSize(size, size))

    # إنشاء الأيقونة الملونة وتعيينها للزر
    colored_icon = create_colored_icon(icon_name, size)
    if colored_icon:
        button.setIcon(colored_icon)
    
    # تخزين اسم الأيقونة وحجمها كخصائص مخصصة للزر
    button.setProperty("icon_name", icon_name)
    button.setProperty("icon_size", size)

    # تطبيق السمة الشفافة على الزر
    make_theme_aware(button, "transparent_button")

    return button

def create_colored_list_item(icon_name, text, size=18):
    """
    إنشاء عنصر قائمة مع أيقونة ملونة باستخدام لون التمييز الحالي

    Args:
        icon_name: اسم الأيقونة (بدون امتداد)
        text: نص العنصر
        size: حجم الأيقونة بالبكسل

    Returns:
        QListWidgetItem: عنصر قائمة مع أيقونة ملونة
    """
    # إنشاء الأيقونة الملونة
    colored_icon = create_colored_icon(icon_name, size)

    if colored_icon:
        # إنشاء عنصر القائمة مع الأيقونة الملونة
        item = QListWidgetItem(colored_icon, text)
    else:
        # الرجوع إلى الأيقونة الأصلية في حالة الفشل
        from .ui_helpers import get_icon_path
        icon_path = get_icon_path(icon_name)
        item = QListWidgetItem(QIcon(icon_path), text)

    return item

def update_widget_icon(widget, icon_name, size=18):
    """
    تحديث أيقونة ودجت موجود باستخدام أيقونة ملونة

    Args:
        widget: الودجت المراد تحديث أيقونته
        icon_name: اسم الأيقونة الجديدة (بدون امتداد)
        size: حجم الأيقونة بالبكسل
    """
    # إنشاء الأيقونة الملونة
    colored_icon = create_colored_icon(icon_name, size)

    if colored_icon:
        # تعيين الأيقونة الملونة للودجت
        widget.setIcon(colored_icon)
