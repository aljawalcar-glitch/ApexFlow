@echo off
setlocal enabledelayedexpansion
echo ========================================
echo          Running ApexFlow Build Script
echo ========================================
cd /d "%~dp0"

REM ============ STEP 1: Check Python Installation ============
echo [STEP 1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo To fix this issue:
    echo 1. Download Python from https://www.python.org/
    echo 2. Make sure to check "Add Python to PATH" during installation
    echo 3. Restart your command prompt after installation
    echo.
    echo [FATAL ERROR] Build process cannot continue without Python.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% found in PATH.

REM ============ STEP 2: Check PyInstaller ============
echo.
echo [STEP 2/5] Checking PyInstaller installation...
python -c "import PyInstaller; print(PyInstaller.__version__)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] PyInstaller not found. Installing...
    pip install --upgrade pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install PyInstaller.
        echo.
        echo To fix this issue:
        echo 1. Check your internet connection
        echo 2. Try running: pip install --upgrade pyinstaller manually
        echo 3. If that fails, try: pip install --user --upgrade pyinstaller
        echo.
        echo [FATAL ERROR] Build process cannot continue without PyInstaller.
        pause
        exit /b 1
    )
    for /f "tokens=*" %%i in ('python -c "import PyInstaller; print(PyInstaller.__version__)" 2^>^&1') do set PYINSTALLER_VERSION=%%i
    echo [SUCCESS] PyInstaller !PYINSTALLER_VERSION! installed successfully.
) else (
    for /f "tokens=*" %%i in ('python -c "import PyInstaller; print(PyInstaller.__version__)" 2^>^&1') do set PYINSTALLER_VERSION=%%i
    echo [SUCCESS] PyInstaller !PYINSTALLER_VERSION! found.
)

REM ============ STEP 3: Check NSIS Installation ============
echo.
echo [STEP 3/5] Checking NSIS installation...
reg query "HKLM\SOFTWARE\WOW6432Node\NSIS" /v "" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] NSIS is not installed or not found in the registry.
    echo.
    echo To fix this issue:
    echo 1. Download NSIS from https://nsis.sourceforge.io/Download
    echo 2. Install it using the default settings.
    echo.
    echo [FATAL ERROR] Build process cannot continue without NSIS.
    pause
    exit /b 1
)
echo [SUCCESS] NSIS installation found in registry.

REM ============ STEP 4: Check Required Python Modules ============
echo.
echo [STEP 4/5] Checking required Python modules...

REM Check each module individually
set MISSING_MODULES=

python -c "import PySide6" >nul 2>&1
if %errorlevel% neq 0 call :AddModule MISSING_MODULES PySide6

python -c "import pypdf" >nul 2>&1
if %errorlevel% neq 0 call :AddModule MISSING_MODULES pypdf

python -c "import fitz" >nul 2>&1
if %errorlevel% neq 0 call :AddModule MISSING_MODULES fitz

python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 call :AddModule MISSING_MODULES PIL

python -c "import arabic_reshaper" >nul 2>&1
if %errorlevel% neq 0 call :AddModule MISSING_MODULES arabic_reshaper

python -c "import bidi" >nul 2>&1
if %errorlevel% neq 0 call :AddModule MISSING_MODULES bidi

python -c "import psutil" >nul 2>&1
if %errorlevel% neq 0 call :AddModule MISSING_MODULES psutil

if not "%MISSING_MODULES%"=="" (
    echo [WARNING] The following required modules are missing:!MISSING_MODULES!
    echo [INFO] Attempting to install from requirements.txt...

    if exist "..\config\requirements.txt" (
        echo [INFO] Found requirements.txt, installing dependencies...
        pip install -r "..\config\requirements.txt"
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to install required modules.
            echo.
            echo To fix this issue:
            echo 1. Check your internet connection
            echo 2. Try installing manually: pip install -r ..\config\requirements.txt
            echo 3. If specific modules fail, try installing them individually
            echo.
            echo [FATAL ERROR] Build process cannot continue without required modules.
            pause
            exit /b 1
        )
        echo [SUCCESS] All required modules installed successfully.
    ) else (
        echo [ERROR] requirements.txt not found in config directory.
        echo.
        echo To fix this issue:
        echo 1. Make sure the config directory exists
        echo 2. Make sure requirements.txt is present in the config directory
        echo.
        echo [FATAL ERROR] Build process cannot continue without requirements.txt.
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] All required modules are installed.
)

REM ============ STEP 5: Run Build Process ============
echo.
echo [STEP 5/5] All dependencies verified. Starting build process...
echo ========================================
python build_master.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build process failed.
    echo.
    echo Common issues and solutions:
    echo 1. Make sure all required modules are properly installed
    echo 2. Check for conflicting Qt libraries (PyQt6 vs PySide6^)
    echo 3. Ensure all files referenced in the build script exist
    echo 4. Check the error messages above for more specific details
    echo.
    echo [FATAL ERROR] Build process failed. See error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo      BUILD PROCESS COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo You can find the generated installer in:
echo %cd%\ApexFlow_Setup_*.exe
echo.
pause
goto :eof

:AddModule
set "%1=%~1 %2"
goto :eof
