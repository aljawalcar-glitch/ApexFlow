# ApexFlow <img src="assets/logo.png" alt="ApexFlow Logo" width="40" height="40">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.6+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](docs/LICENSE.txt)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://github.com/yourusername/ApexFlow)
[![Version](https://img.shields.io/badge/Version-v6.1.1-brightgreen.svg)](docs/RELEASE_NOTES_V6.1.1.md)
[![Performance](https://img.shields.io/badge/Performance-Optimized-orange.svg)](#whats-new-in-v611)
[![Security](https://img.shields.io/badge/Security-Enhanced-red.svg)](#whats-new-in-v611)

[🇸🇦 اقرأ هذا الملف باللغة العربية](README_AR.md)

**ApexFlow v6.1.1** is a comprehensive, high-performance desktop application for managing and processing PDF files, built with Python and PySide6. This latest version features significant performance optimizations, enhanced security, and improved stability with an intuitive Arabic-first user interface.

## ✨ Key Features

### 📄 PDF Operations
- **🔗 Merge:** Combine multiple PDF files into a single document with custom ordering
- **✂️ Split:** Extract specific pages or split PDFs into multiple files
- **🗜️ Compress:** Reduce file size while maintaining document quality
- **🔄 Rotate:** Correct page orientation (90°, 180°, 270°)
- **🔒 Security:** Add/remove password protection and encryption
- **🖼️ Stamping:** Apply custom text or image watermarks and stamps

### 🎨 User Experience
- **📂 Drag & Drop:** Easily add files by dragging and dropping them into the application
- **🎨 Modern UI:** Clean, intuitive Arabic-first interface with enhanced responsiveness
- **🎨 Theming:** Multiple themes (Dark, Light) with customizable accent colors
- **📱 Responsive:** Adaptive layout that works on different screen sizes
- **🚀 Performance:** Optimized processing with background workers and improved memory management
- **📊 Progress Tracking:** Real-time progress indicators for all operations
- **🔔 Notifications:** Enhanced notification system with better error handling

### 🛠️ Advanced Features
- **🖨️ Print Integration:** Direct printing with Windows printer support
- **📁 Batch Processing:** Handle multiple files simultaneously with improved efficiency
- **💾 Smart Caching:** Intelligent preview caching for better performance
- **🔧 Settings Management:** Comprehensive settings with reset/cancel functionality
- **📝 Logging:** Enhanced logging system with security improvements
- **🔍 System Diagnostics:** Comprehensive system diagnostics with better error reporting
- **🖼️ Interactive Stamps:** Apply watermarks and stamps with precise positioning
- **🔄 Lazy Loading:** Efficient page loading system with memory optimization
- **🎨 Theme Management:** Advanced theme system with improved validation
- **📊 Performance Monitoring:** Real-time performance monitoring with enhanced stability

### 🆕 New in v6.1.1
- **⚡ Performance Boost:** 15-20% improvement in memory usage and startup speed
- **🛡️ Enhanced Security:** Fixed 25+ security vulnerabilities and improved input validation
- **🔧 Better Error Handling:** Improved exception handling and error recovery
- **🎯 Functional Completeness:** Implemented missing settings functions (reset/cancel)
- **🧹 Code Quality:** Cleaner, more maintainable codebase with reduced complexity

## 📸 Screenshots

### Main Interface
![Main Interface with Dark Theme](assets/screenshots/main-interface.png)

### PDF Merge and Print Interface
![PDF Merge and Print Interface](assets/screenshots/Merge-Page.png)

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download Python](https://python.org/downloads/)
- **Windows 10/11** - Primary supported platform
- **4GB RAM** - Recommended for optimal performance (2GB minimum)
- **500MB Storage** - For application and temporary files

### 📦 Installation

#### Option 1: Download Executable (Recommended)
1. Go to [Releases](https://github.com/yourusername/ApexFlow/releases)
2. Download the latest `ApexFlow-Setup.exe`
3. Run the installer and follow the setup wizard

#### Option 2: Run from Source
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ApexFlow.git
   cd ApexFlow
   ```

2. **Install dependencies:**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   # or simply double-click run.bat
   ```

## 💡 Usage Examples

### Basic PDF Operations

```python
# Merge multiple PDFs
python main.py
# 1. Select "Merge & Print" from the sidebar
# 2. Click "Select Files" and choose your PDFs
# 3. Arrange files in desired order
# 4. Click "Merge Files"
```

### Advanced Features

- **Batch Processing:** Select multiple files for simultaneous operations
- **Custom Stamps:** Create and manage your own watermark library
- **Print Integration:** Direct printing to any Windows-compatible printer
- **Theme Customization:** Switch between themes and customize accent colors

## 🏗️ Project Architecture

```
ApexFlow/
├── 📄 main.py                    # Application entry point
├── 🚀 run.bat                   # Quick launch script
├── 📁 modules/                  # Core business logic
│   ├── app_utils.py            # Application utilities & managers
│   ├── merge.py                # PDF merging operations
│   ├── split.py                # PDF splitting operations
│   ├── compress.py             # PDF compression
│   ├── security.py             # Encryption & password protection
│   └── ...                     # Other processing modules
├── 📁 ui/                       # User interface components
│   ├── theme_manager.py        # Theme & styling system
│   ├── merge_page.py           # Merge interface
│   ├── notification_system.py  # Toast notifications
│   └── ...                     # Other UI components
├── 📁 assets/                   # Static resources
├── 📁 data/                     # User data & settings
├── 📁 config/                   # Configuration files
└── 📁 build_scripts/            # Build & deployment scripts
```

## 🛠️ Development

### Setting up Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/ApexFlow.git
   cd ApexFlow
   ```
3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
4. **Install development dependencies:**
   ```bash
   pip install -r config/requirements.txt
   ```

### Building Executable

```bash
cd build_scripts
build.bat  # Creates executable in dist/ folder
```

### Code Style

- Follow PEP 8 guidelines
- Use Arabic comments for Arabic-specific features
- Maintain consistent naming conventions
- Add docstrings for all public methods

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
- Use the [issue tracker](https://github.com/yourusername/ApexFlow/issues)
- Include system information and steps to reproduce
- Attach sample files if relevant

### 💡 Feature Requests
- Check existing issues first
- Describe the use case and expected behavior
- Consider implementation complexity

### 🔧 Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 System Requirements

| Component | Minimum | Recommended | v6.1.1 Optimized |
|-----------|---------|-------------|-------------------|
| OS | Windows 10 | Windows 11 | Windows 11 |
| Python | 3.8 | 3.11+ | 3.11+ |
| RAM | 2GB | 4GB+ | 4GB+ (15% less usage) |
| Storage | 100MB | 500MB+ | 500MB+ |
| Display | 1024x768 | 1920x1080+ | 1920x1080+ |
| Startup Time | ~10s | ~5s | ~4s (20% faster) |

## 🆘 Support

- 📖 **Documentation:** Check the [Wiki](https://github.com/yourusername/ApexFlow/wiki)
- 🐛 **Bug Reports:** [Issues](https://github.com/yourusername/ApexFlow/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourusername/ApexFlow/discussions)
- 📧 **Email:** support@apexflow.com
- 📋 **Release Notes:** [v6.1.1 Changes](docs/RELEASE_NOTES_V6.1.1.md)

## 🔄 What's New in v6.1.1

### Performance Improvements
- **Memory Optimization:** Reduced memory usage by ~15% through better resource management
- **Startup Speed:** 20% faster application startup with optimized initialization
- **Code Efficiency:** Improved algorithms and data structures for better performance

### Security Enhancements
- **Input Validation:** Enhanced validation for all user inputs and settings
- **Log Security:** Fixed log injection vulnerabilities (CWE-117)
- **Exception Handling:** Improved security in error handling and exception management
- **Data Protection:** Better protection against malformed data and edge cases

### Stability Improvements
- **Error Recovery:** Better error handling and recovery mechanisms
- **Memory Management:** Improved memory cleanup and resource management
- **Exception Safety:** More robust exception handling throughout the application
- **Settings Management:** Complete implementation of settings reset and cancel functions

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](docs/LICENSE.txt) file for details.

## 🙏 Acknowledgments

- **PySide6** - For the excellent Qt bindings
- **PyMuPDF** - For powerful PDF processing capabilities
- **PyInstaller** - For executable packaging
- **Security Researchers** - For identifying vulnerabilities and suggesting improvements
- **Performance Testers** - For helping optimize the application
- **Contributors** - Thank you to all who have contributed to this project

---

<div align="center">
  <p>Made with ❤️ for the Arabic-speaking community</p>
  <p>⭐ Star this repository if you find it helpful!</p>
</div>