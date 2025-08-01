# ApexFlow Build Scripts Guide

## 📁 Available Build Files

### 🚀 Build Scripts
- **`build.bat`** - Complete build (application + installer)
- **`build-quick.bat`** - Quick build (application only for testing)
- **`build-enhanced.bat`** - Enhanced build with advanced options
- **`build-final.bat`** - Final build for production

### ⚙️ Configuration Files
- **`ApexFlow_Simple.spec`** - Simple and reliable PyInstaller file ✅
- **`ApexFlow_Enhanced.spec`** - Enhanced PyInstaller file (under development)
- **`build_installer.nsi`** - NSIS script for installer

### 🧹 Cleanup Tools
- **`clean_build.bat`** - Clean build files
- **`run_app.bat`** - Run application directly

## 🔧 How to Use

### For quick build (testing):
```bash
build-quick.bat
```

### For complete build (production):
```bash
build.bat
```

### For cleanup:
```bash
clean_build.bat
```

## 📋 Build Requirements

### Required Programs:
- Python 3.11+ with pip
- PyInstaller
- NSIS (for installer)

### Required Libraries:
- PySide6
- PyPDF2
- PyMuPDF
- Pillow
- psutil
- arabic_reshaper
- python-bidi

## 📂 Output Structure

```
build_scripts/
├── dist/
│   └── ApexFlow/
│       ├── ApexFlow.exe
│       ├── assets/
│       ├── data/
│       ├── docs/
│       └── [other libraries]
└── ApexFlow_Setup_5.2.2.exe (installer)
```

## ⚠️ Important Notes

1. Make sure all files are in their correct location
2. Run the script from the build_scripts folder
3. Check Python version and libraries
4. For installer, make sure NSIS is installed

## 🐛 Common Issues Solutions

### Library import error:
```bash
pip install --upgrade -r ../config/requirements.txt
```

### File path error:
Make sure to run the script from the build_scripts folder

### Installer creation failure:
Check that NSIS is installed in the default path
