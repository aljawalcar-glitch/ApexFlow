@echo off
setlocal

:: =================================================================
:: سكريبت تنظيف ملفات البناء - ApexFlow Build Cleanup Script
:: =================================================================

echo.
echo =================================================
echo     ApexFlow Build Cleanup Script
echo     سكريبت تنظيف ملفات البناء
echo =================================================
echo.

echo جاري تنظيف ملفات البناء القديمة...
echo Cleaning old build files...
echo.

:: تنظيف مجلد dist
if exist "dist" (
    echo جاري حذف مجلد dist...
    echo Removing dist folder...
    rmdir /s /q "dist"
    if %errorlevel% equ 0 (
        echo ✅ تم حذف مجلد dist بنجاح
        echo ✅ dist folder removed successfully
    ) else (
        echo ❌ فشل في حذف مجلد dist
        echo ❌ Failed to remove dist folder
    )
) else (
    echo ℹ️  مجلد dist غير موجود
    echo ℹ️  dist folder does not exist
)

echo.

:: تنظيف مجلد build
if exist "build" (
    echo جاري حذف مجلد build...
    echo Removing build folder...
    rmdir /s /q "build"
    if %errorlevel% equ 0 (
        echo ✅ تم حذف مجلد build بنجاح
        echo ✅ build folder removed successfully
    ) else (
        echo ❌ فشل في حذف مجلد build
        echo ❌ Failed to remove build folder
    )
) else (
    echo ℹ️  مجلد build غير موجود
    echo ℹ️  build folder does not exist
)

echo.

:: تنظيف ملف spec
if exist "ApexFlow.spec" (
    echo جاري حذف ملف ApexFlow.spec...
    echo Removing ApexFlow.spec file...
    del "ApexFlow.spec"
    if %errorlevel% equ 0 (
        echo ✅ تم حذف ملف spec بنجاح
        echo ✅ spec file removed successfully
    ) else (
        echo ❌ فشل في حذف ملف spec
        echo ❌ Failed to remove spec file
    )
) else (
    echo ℹ️  ملف ApexFlow.spec غير موجود
    echo ℹ️  ApexFlow.spec file does not exist
)

echo.

:: تنظيف ملفات المثبت القديمة
echo جاري البحث عن ملفات المثبت القديمة...
echo Looking for old installer files...

for %%f in (ApexFlow_Setup_*.exe) do (
    echo جاري حذف ملف المثبت القديم: %%f
    echo Removing old installer file: %%f
    del "%%f"
    if %errorlevel% equ 0 (
        echo ✅ تم حذف %%f بنجاح
        echo ✅ %%f removed successfully
    ) else (
        echo ❌ فشل في حذف %%f
        echo ❌ Failed to remove %%f
    )
)

echo.

:: تنظيف ملفات Python المؤقتة
echo جاري تنظيف ملفات Python المؤقتة...
echo Cleaning Python temporary files...

:: حذف ملفات __pycache__
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo جاري حذف: %%d
        echo Removing: %%d
        rmdir /s /q "%%d"
    )
)

:: حذف ملفات .pyc
for /r . %%f in (*.pyc) do (
    if exist "%%f" (
        echo جاري حذف: %%f
        echo Removing: %%f
        del "%%f"
    )
)

:: حذف ملفات .pyo
for /r . %%f in (*.pyo) do (
    if exist "%%f" (
        echo جاري حذف: %%f
        echo Removing: %%f
        del "%%f"
    )
)

echo.

:: تنظيف ملفات السجلات المؤقتة
if exist "*.log" (
    echo جاري حذف ملفات السجلات...
    echo Removing log files...
    del "*.log"
)

if exist "*.tmp" (
    echo جاري حذف الملفات المؤقتة...
    echo Removing temporary files...
    del "*.tmp"
)

echo.
echo =================================================
echo    ✅ تم التنظيف بنجاح! / CLEANUP COMPLETED! ✅
echo =================================================
echo.

echo تم تنظيف:
echo Cleaned:
echo • مجلد dist / dist folder
echo • مجلد build / build folder  
echo • ملف ApexFlow.spec / ApexFlow.spec file
echo • ملفات المثبت القديمة / Old installer files
echo • ملفات Python المؤقتة / Python temporary files
echo • ملفات السجلات / Log files
echo.

echo يمكنك الآن تشغيل سكريبت البناء:
echo You can now run the build script:
echo • build.bat
echo • build-progressBar.bat  
echo • build-enhanced.bat
echo.

pause
endlocal
