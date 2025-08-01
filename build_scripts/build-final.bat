@echo off
setlocal enabledelayedexpansion

:: =================================================================
:: ApexFlow Final Build Script - سكريبت البناء النهائي المحسن
:: =================================================================

title ApexFlow Build System

echo.
echo =================================================
echo     ApexFlow Final Build System v2.0
echo     نظام البناء النهائي المحسن
echo =================================================
echo.

:: عرض معلومات النظام
echo معلومات النظام / System Information:
echo • التاريخ / Date: %DATE%
echo • الوقت / Time: %TIME%
echo • المستخدم / User: %USERNAME%
echo • المجلد / Directory: %CD%
echo.

:: =================================================================
:: الخطوة 0: فحص المتطلبات المسبقة
:: =================================================================
echo.
echo --- الخطوة 0: فحص المتطلبات المسبقة ---
echo --- Step 0: Prerequisites Check ---
echo.

:: فحص Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python غير مثبت أو غير متاح في PATH
    echo ❌ Python is not installed or not available in PATH
    pause
    goto :eof
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% متاح
echo ✅ Python %PYTHON_VERSION% available

:: فحص pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip غير متاح
    echo ❌ pip is not available
    pause
    goto :eof
)

echo ✅ pip متاح
echo ✅ pip available

:: تشغيل فحص المتطلبات التفصيلي
if exist "check_build_requirements.py" (
    echo.
    echo جاري تشغيل فحص المتطلبات التفصيلي...
    echo Running detailed requirements check...
    echo.
    python check_build_requirements.py
    
    echo.
    echo هل تريد المتابعة مع البناء؟ (y/n)
    echo Do you want to continue with the build? (y/n)
    set /p continue_build=
    
    if /i not "!continue_build!"=="y" (
        echo تم إلغاء البناء
        echo Build cancelled
        pause
        goto :eof
    )
) else (
    echo تحذير: ملف فحص المتطلبات غير موجود
    echo Warning: Requirements check file not found
)

echo.
pause

:: =================================================================
:: الخطوة 1: تحديث وتثبيت المتطلبات
:: =================================================================
echo.
echo --- الخطوة 1: تحديث وتثبيت المتطلبات ---
echo --- Step 1: Update and Install Requirements ---
echo.

echo جاري تحديث pip إلى أحدث إصدار...
echo Updating pip to latest version...
python -m pip install --upgrade pip

echo.
echo جاري تثبيت wheel و setuptools...
echo Installing wheel and setuptools...
python -m pip install --upgrade wheel setuptools

echo.
echo جاري تثبيت المتطلبات من requirements.txt...
echo Installing requirements from requirements.txt...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ❌ فشل في تثبيت المتطلبات
    echo ❌ Failed to install requirements
    echo.
    echo هل تريد المحاولة مرة أخرى؟ (y/n)
    echo Do you want to try again? (y/n)
    set /p retry_install=
    
    if /i "!retry_install!"=="y" (
        echo جاري إعادة المحاولة...
        echo Retrying...
        python -m pip install -r requirements.txt --force-reinstall
    )
    
    if %errorlevel% neq 0 (
        echo ❌ فشل نهائي في تثبيت المتطلبات
        echo ❌ Final failure to install requirements
        pause
        goto :eof
    )
)

echo.
echo ✅ تم تثبيت جميع المتطلبات بنجاح
echo ✅ All requirements installed successfully
echo.
pause

:: =================================================================
:: الخطوة 2: تنظيف شامل
:: =================================================================
echo.
echo --- الخطوة 2: تنظيف شامل ---
echo --- Step 2: Comprehensive Cleanup ---
echo.

if exist "clean_build.bat" (
    echo جاري تشغيل سكريبت التنظيف...
    echo Running cleanup script...
    call clean_build.bat
) else (
    echo تنظيف يدوي...
    echo Manual cleanup...
    
    if exist "dist" rmdir /s /q "dist"
    if exist "build" rmdir /s /q "build"
    if exist "ApexFlow.spec" del "ApexFlow.spec"
    
    for %%f in (ApexFlow_Setup_*.exe) do del "%%f"
)

echo.
echo ✅ تم التنظيف بنجاح
echo ✅ Cleanup completed successfully
echo.

:: =================================================================
:: الخطوة 3: البناء باستخدام الملف المحسن
:: =================================================================
echo.
echo --- الخطوة 3: البناء المحسن ---
echo --- Step 3: Enhanced Building ---
echo.

echo جاري البناء باستخدام التكوين المحسن...
echo Building using enhanced configuration...
echo.

if exist "ApexFlow_Enhanced.spec" (
    echo استخدام ملف التكوين المحسن...
    echo Using enhanced configuration file...
    python -m PyInstaller ApexFlow_Enhanced.spec --clean --noconfirm
) else (
    echo استخدام التكوين الافتراضي المحسن...
    echo Using default enhanced configuration...
    python -m PyInstaller main.py ^
        --name ApexFlow ^
        --windowed ^
        --onedir ^
        --icon="assets/icons/ApexFlow.ico" ^
        --add-data="assets;assets" ^
        --add-data="data;data" ^
        --add-data="modules/default_settings.json;modules" ^
        --add-data="docs;docs" ^
        --hidden-import="PySide6.QtCore" ^
        --hidden-import="PySide6.QtGui" ^
        --hidden-import="PySide6.QtWidgets" ^
        --hidden-import="PyPDF2" ^
        --hidden-import="fitz" ^
        --hidden-import="PIL" ^
        --hidden-import="arabic_reshaper" ^
        --hidden-import="bidi" ^
        --hidden-import="psutil" ^
        --hidden-import="win32api" ^
        --exclude-module="tkinter" ^
        --exclude-module="matplotlib" ^
        --clean ^
        --noconfirm
)

if %errorlevel% neq 0 (
    echo.
    echo ❌ فشل في بناء التطبيق
    echo ❌ Failed to build application
    echo.
    echo فحص الأخطاء:
    echo Error checking:
    echo • تأكد من وجود جميع الملفات المطلوبة
    echo • Check that all required files exist
    echo • تأكد من تثبيت جميع المكتبات
    echo • Ensure all libraries are installed
    echo • راجع رسائل الخطأ أعلاه
    echo • Review error messages above
    pause
    goto :eof
)

echo.
echo ✅ تم بناء التطبيق بنجاح
echo ✅ Application built successfully
echo.

:: =================================================================
:: الخطوة 4: فحص الملفات المبنية
:: =================================================================
echo.
echo --- الخطوة 4: فحص الملفات المبنية ---
echo --- Step 4: Verify Built Files ---
echo.

if not exist "dist\ApexFlow\ApexFlow.exe" (
    echo ❌ الملف التنفيذي غير موجود
    echo ❌ Executable file not found
    pause
    goto :eof
)

echo ✅ الملف التنفيذي موجود
echo ✅ Executable file exists

:: فحص المجلدات المطلوبة
set "required_folders=assets data docs modules"
for %%d in (%required_folders%) do (
    if exist "dist\ApexFlow\%%d" (
        echo ✅ مجلد %%d موجود
        echo ✅ Folder %%d exists
    ) else (
        echo ❌ مجلد %%d مفقود
        echo ❌ Folder %%d missing
    )
)

:: حساب حجم التطبيق
for /f %%i in ('dir "dist\ApexFlow" /s /-c ^| find "bytes"') do set app_size=%%i
echo.
echo حجم التطبيق المبني / Built application size: %app_size%
echo.

:: =================================================================
:: الخطوة 5: بناء المثبت
:: =================================================================
echo.
echo --- الخطوة 5: بناء المثبت ---
echo --- Step 5: Build Installer ---
echo.

if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo جاري بناء المثبت باستخدام NSIS...
    echo Building installer using NSIS...
    
    "C:\Program Files (x86)\NSIS\makensis.exe" "build_installer.nsi"
    
    if %errorlevel% equ 0 (
        echo ✅ تم بناء المثبت بنجاح
        echo ✅ Installer built successfully
        
        if exist "ApexFlow_Setup_5.2.2.exe" (
            for %%i in (ApexFlow_Setup_5.2.2.exe) do set installer_size=%%~zi
            echo حجم المثبت / Installer size: !installer_size! bytes
        )
    ) else (
        echo ❌ فشل في بناء المثبت
        echo ❌ Failed to build installer
    )
) else (
    echo ⚠️  NSIS غير مثبت - تم تخطي بناء المثبت
    echo ⚠️  NSIS not installed - Installer build skipped
)

:: =================================================================
:: النتيجة النهائية
:: =================================================================
echo.
echo =================================================
echo    🎉 اكتمل البناء بنجاح! / BUILD COMPLETED! 🎉
echo =================================================
echo.

echo الملفات المُنتجة / Generated Files:
echo.

if exist "dist\ApexFlow\ApexFlow.exe" (
    echo 📁 التطبيق المبني / Built Application:
    echo    dist\ApexFlow\ApexFlow.exe
    echo.
)

if exist "ApexFlow_Setup_5.2.2.exe" (
    echo 📦 ملف المثبت / Installer File:
    echo    ApexFlow_Setup_5.2.2.exe
    echo.
)

echo الخطوات التالية / Next Steps:
echo • اختبار التطبيق: dist\ApexFlow\ApexFlow.exe
echo • Test application: dist\ApexFlow\ApexFlow.exe
echo • تثبيت باستخدام المثبت (إذا كان متاحاً)
echo • Install using installer (if available)
echo • توزيع الملفات حسب الحاجة
echo • Distribute files as needed
echo.

echo تم البناء في: %DATE% %TIME%
echo Build completed at: %DATE% %TIME%
echo.

:eof
pause
endlocal
