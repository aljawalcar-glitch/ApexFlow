# -*- coding: utf-8 -*-
"""
PyInstaller runtime hook for PySide6
يضمن هذا الملف تضمين جميع مكونات PySide6 المطلوبة في الملف التنفيذي
"""

import os
import sys

# تأكد من تضمين جميع مكونات PySide6
if hasattr(sys, '_MEIPASS'):
    # مسار مجلد الموارد في الملف التنفيذي
    resources_path = os.path.join(sys._MEIPASS, 'PySide6')

    # أضف المسار إلى sys.path إذا كان موجودًا
    if os.path.exists(resources_path):
        sys.path.insert(0, resources_path)

    # تأكد من تضمين الإضافات
    plugins_path = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')
    if os.path.exists(plugins_path):
        os.environ['QT_PLUGIN_PATH'] = plugins_path
