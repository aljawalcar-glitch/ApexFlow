# -*- coding: utf-8 -*-
"""
العناصر الذكية التي تستمع لتغييرات السمة
Theme-Aware Widgets that automatically respond to theme changes
"""

from src.managers.theme_manager import global_theme_manager

def make_theme_aware(widget, widget_type="default"):
    """
    تحويل أي عنصر موجود إلى عنصر ذكي.
    يسجل العنصر لدى مدير السمات ويطبق السمة الحالية.
    """
    global_theme_manager.register_widget(widget, widget_type)
    return widget
