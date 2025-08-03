# -*- mode: python ; coding: utf-8 -*-
"""
ApexFlow Enhanced PyInstaller Specification

This file contains all the required settings to build ApexFlow
with all necessary files and libraries included
"""

import os
import sys
from pathlib import Path

# Add project path - use SPECPATH instead of __file__
spec_dir = os.path.dirname(SPECPATH)
project_root = os.path.dirname(spec_dir)  # Go up one level from build_scripts
config_path = os.path.join(project_root, 'config')

# Check if main.py exists
main_py_path = os.path.join(project_root, 'main.py')
if not os.path.exists(main_py_path):
    print(f"Error: main.py not found at {main_py_path}")
    print(f"SPECPATH: {SPECPATH}")
    print(f"spec_dir: {spec_dir}")
    print(f"project_root: {project_root}")
    raise FileNotFoundError(f"main.py not found at {main_py_path}")

sys.path.insert(0, project_root)
sys.path.insert(0, config_path)

# Import version information
VERSION = "5.3.0"
APP_NAME = "ApexFlow"
BUILD_INCLUDES = [
    "Translation files (Arabic/English)",
    "Font and theme settings",
    "All icons and assets",
    "Interactive stamp system",
    "Enhanced default settings",
    "Documentation and license files"
]

try:
    # Try to import version info if available
    exec(open(os.path.join(config_path, 'version.py')).read())
    print(f"Building {APP_NAME} {VERSION}")
    print("Included components:")
    for component in BUILD_INCLUDES:
        print(f"  • {component}")
except:
    print(f"Building {APP_NAME} {VERSION} (using default version info)")
    print("Using default build configuration")

# Define required files and folders
data_files = [
    # Assets and icons
    ('assets', 'assets'),

    # Data and translation files
    ('data', 'data'),

    # Default settings
    ('modules/default_settings.json', 'modules'),

    # Documentation and license
    ('docs', 'docs'),
]

# Required hidden imports
hidden_imports = [
    # PySide6 components
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.QtPrintSupport',
    'PySide6.QtSvg',
    
    # PDF processing
    'PyPDF2',
    'PyPDF2.pdf',
    'fitz',  # PyMuPDF
    'pymupdf',
    
    # Image processing
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'Pillow',
    
    # Arabic text support
    'arabic_reshaper',
    'bidi',
    'bidi.algorithm',
    
    # System monitoring
    'psutil',
    
    # Windows specific
    'win32api',
    'win32print',
    'win32gui',
    'pywintypes',
    
    # Encryption
    'Crypto',
    'Crypto.Cipher',
    'Crypto.Hash',
    
    # JSON and other utilities
    'json',
    'pathlib',
    'logging',
    'threading',
    'queue',
]

# Additional binary files
binaries = []

# Excluded modules (to reduce size)
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'jupyter',
    'IPython',
    'notebook',
    'tornado',
    'zmq',
]

# Analyze files
a = Analysis(
    [os.path.join(project_root, 'main.py')],
    pathex=[project_root],
    binaries=binaries,
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    optimize=0,
)

# Create PYZ file
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable file
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'assets', 'icons', 'ApexFlow.ico'),
    version_file=None,
)

# Collect all files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# Print build information
print("\n" + "="*60)
print(f"PyInstaller Configuration for {APP_NAME} {VERSION}")
print("="*60)
print(f"Data files included: {len(data_files)}")
print(f"Hidden imports: {len(hidden_imports)}")
print(f"Excluded modules: {len(excludes)}")
print(f"Icon: assets/icons/ApexFlow.ico")
print(f"Console mode: False (GUI)")
print(f"UPX compression: Enabled")
print("="*60)
