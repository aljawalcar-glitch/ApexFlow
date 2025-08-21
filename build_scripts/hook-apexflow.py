# -*- coding: utf-8 -*-
"""
PyInstaller hook for ApexFlow
Ensures all resources are properly included
"""

from PyInstaller.utils.hooks import collect_data_files, collect_all
import os

# Collect all data files from assets directory
datas = []

# Add all icon files
icon_patterns = [
    ('assets/icons', 'assets/icons'),
    ('assets/icons/default', 'assets/icons/default'),
    ('assets/menu_icons', 'assets/menu_icons'),
]

for src, dst in icon_patterns:
    if os.path.exists(src):
        datas += collect_data_files('assets', include_py_files=False)

# Add other asset files
asset_files = [
    ('assets/logo.png', 'assets'),
    ('assets/wordmark.svg', 'assets'),
    ('assets/sounds', 'assets/sounds'),
    ('assets/screenshots', 'assets/screenshots'),
]

for src, dst in asset_files:
    if os.path.exists(src):
        if os.path.isfile(src):
            datas.append((src, dst))
        else:
            datas += collect_data_files(src, include_py_files=False)

# Collect PySide6 resources
pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all('PySide6')
datas += pyside6_datas
binaries = pyside6_binaries
hiddenimports = pyside6_hiddenimports