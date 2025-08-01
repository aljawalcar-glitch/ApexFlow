@echo off
setlocal

echo.
echo =================================================
echo  ApexFlow Quick Build Script
echo =================================================
echo This script will quickly compile the application only
echo (without installer) for testing purposes.
echo.

REM =================================================
REM QUICK BUILD FOR TESTING
REM =================================================
echo.
echo --- Quick Build for Testing ---
echo.

echo Installing/upgrading required packages...
python -m pip install --upgrade pyside6 pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages.
    pause
    goto :eof
)

echo.
echo Building with simple PyInstaller specification...
cd /d "%~dp0"
python -m PyInstaller ApexFlow_Simple.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller failed.
    pause
    goto :eof
)

echo.
echo =================================================
echo  SUCCESS! Quick build completed!
echo =================================================
echo.
echo Application compiled in: dist/ApexFlow/
echo You can run: dist/ApexFlow/ApexFlow.exe
echo.

:eof
pause
endlocal
