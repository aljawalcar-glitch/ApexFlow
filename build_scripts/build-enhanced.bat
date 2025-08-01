@echo off
setlocal enabledelayedexpansion

:: =================================================================
:: ApexFlow Enhanced Build Script - سكريبت البناء المحسن
:: =================================================================

echo.
echo =================================================
echo     ApexFlow Enhanced Build Script
echo     سكريبت البناء المحسن لـ ApexFlow
echo =================================================
echo.

:: التحقق من وجود الملفات المطلوبة
echo جاري التحقق من الملفات المطلوبة...
echo Checking required files...
echo.

set "missing_files="

:: فحص الملفات الأساسية
if not exist "main.py" (
    set "missing_files=!missing_files! main.py"
)

if not exist "assets\icons\ApexFlow.ico" (
    set "missing_files=!missing_files! assets\icons\ApexFlow.ico"
)

if not exist "data\translations.json" (
    set "missing_files=!missing_files! data\translations.json"
)

if not exist "modules\default_settings.json" (
    set "missing_files=!missing_files! modules\default_settings.json"
)

if not exist "build_installer.nsi" (
    set "missing_files=!missing_files! build_installer.nsi"
)

:: التحقق من وجود ملفات مفقودة
if not "!missing_files!"=="" (
    echo.
    echo [خطأ] الملفات التالية مفقودة:
    echo [ERROR] The following files are missing:
    for %%f in (!missing_files!) do (
        echo   - %%f
    )
    echo.
    pause
    goto :eof
)

echo ✅ جميع الملفات المطلوبة موجودة
echo ✅ All required files found
echo.
pause

:: =================================================================
:: الخطوة 1: تثبيت المتطلبات
:: =================================================================
echo.
echo --- الخطوة 1: تثبيت المتطلبات ---
echo --- Step 1: Installing Requirements ---
echo.

echo جاري تحديث pip...
echo Updating pip...
python -m pip install --upgrade pip

echo.
echo جاري تثبيت المتطلبات من requirements.txt...
echo Installing requirements from requirements.txt...
python -m pip install -r requirements.txt

echo.
echo جاري تثبيت PyInstaller...
echo Installing PyInstaller...
python -m pip install --upgrade pyinstaller

if %errorlevel% neq 0 (
    echo.
    echo [خطأ] فشل في تثبيت المتطلبات
    echo [ERROR] Failed to install requirements
    pause
    goto :eof
)

echo.
echo ✅ تم تثبيت جميع المتطلبات بنجاح
echo ✅ All requirements installed successfully
echo.
pause

:: =================================================================
:: الخطوة 2: تنظيف الملفات القديمة
:: =================================================================
echo.
echo --- الخطوة 2: تنظيف الملفات القديمة ---
echo --- Step 2: Cleaning Old Files ---
echo.

if exist "dist" (
    echo جاري حذف مجلد dist القديم...
    echo Removing old dist folder...
    rmdir /s /q "dist"
)

if exist "build" (
    echo جاري حذف مجلد build القديم...
    echo Removing old build folder...
    rmdir /s /q "build"
)

if exist "ApexFlow.spec" (
    echo جاري حذف ملف spec القديم...
    echo Removing old spec file...
    del "ApexFlow.spec"
)

echo ✅ تم تنظيف الملفات القديمة
echo ✅ Old files cleaned
echo.

:: =================================================================
:: الخطوة 3: بناء التطبيق باستخدام PyInstaller
:: =================================================================
echo.
echo --- الخطوة 3: بناء التطبيق ---
echo --- Step 3: Building Application ---
echo.

echo جاري بناء التطبيق مع جميع الملفات المطلوبة...
echo Building application with all required files...
echo.

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
    --clean ^
    --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo [خطأ] فشل في بناء التطبيق
    echo [ERROR] Failed to build application
    pause
    goto :eof
)

echo.
echo ✅ تم بناء التطبيق بنجاح
echo ✅ Application built successfully
echo.

:: التحقق من وجود الملفات المبنية
if not exist "dist\ApexFlow\ApexFlow.exe" (
    echo [خطأ] لم يتم العثور على الملف التنفيذي المبني
    echo [ERROR] Built executable not found
    pause
    goto :eof
)

echo جاري التحقق من الملفات المضمنة...
echo Checking included files...

set "check_files=assets data docs modules"
for %%d in (%check_files%) do (
    if exist "dist\ApexFlow\%%d" (
        echo ✅ مجلد %%d موجود
        echo ✅ Folder %%d exists
    ) else (
        echo ❌ مجلد %%d مفقود
        echo ❌ Folder %%d missing
    )
)

echo.
pause

:: =================================================================
:: الخطوة 4: بناء المثبت
:: =================================================================
echo.
echo --- الخطوة 4: بناء المثبت ---
echo --- Step 4: Building Installer ---
echo.

:: التحقق من وجود NSIS
if not exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo [تحذير] لم يتم العثور على NSIS في المسار الافتراضي
    echo [WARNING] NSIS not found in default path
    echo يرجى التأكد من تثبيت NSIS أو تحديث المسار في السكريبت
    echo Please ensure NSIS is installed or update the path in the script
    echo.
    pause
    goto :skip_installer
)

echo جاري بناء المثبت...
echo Building installer...

"C:\Program Files (x86)\NSIS\makensis.exe" "build_installer.nsi"

if %errorlevel% neq 0 (
    echo.
    echo [خطأ] فشل في بناء المثبت
    echo [ERROR] Failed to build installer
    pause
    goto :eof
)

echo.
echo ✅ تم بناء المثبت بنجاح
echo ✅ Installer built successfully
goto :success

:skip_installer
echo تم تخطي بناء المثبت
echo Installer build skipped

:success
echo.
echo =================================================
echo    🎉 تم البناء بنجاح! / BUILD SUCCESSFUL! 🎉
echo =================================================
echo.

if exist "ApexFlow_Setup_5.2.2.exe" (
    echo 📦 ملف المثبت: ApexFlow_Setup_5.2.2.exe
    echo 📦 Installer file: ApexFlow_Setup_5.2.2.exe
)

echo 📁 ملفات التطبيق: dist\ApexFlow\
echo 📁 Application files: dist\ApexFlow\
echo.
echo يمكنك الآن تشغيل التطبيق من: dist\ApexFlow\ApexFlow.exe
echo You can now run the application from: dist\ApexFlow\ApexFlow.exe
echo.

:eof
pause
endlocal
