@echo off
setlocal

echo.
echo =================================================
echo  ApexFlow Final Build Script
echo =================================================
echo This script will compile the application and then build the installer.
echo.
pause

REM =================================================
REM PART 1: COMPILE THE PYTHON APPLICATION
REM =================================================
echo.
echo --- PART 1: Compiling the Python Application ---
echo.

python -m pip install --upgrade pyside6 pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages.
    pause
    goto :eof
)

python -m PyInstaller main.py ^
    --name ApexFlow ^
    --windowed ^
    --onedir ^
    --icon="assets/icons/ApexFlow.ico" ^
    --add-data="assets;assets" ^
    --add-data="modules/default_settings.json;modules" ^
    --clean

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller failed.
    pause
    goto :eof
)

echo.
echo --- PART 1 COMPLETED ---
echo.
pause

REM =================================================
REM PART 2: BUILD THE NSIS INSTALLER
REM =================================================
echo.
echo --- PART 2: Building the NSIS Installer ---
echo.

"C:\Program Files (x86)\NSIS\makensis.exe" "build_installer.nsi"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] NSIS compilation failed.
    pause
    goto :eof
)

echo.
echo =================================================
echo  SUCCESS! Installer built successfully!
echo =================================================
echo.
echo You can find 'ApexFlow_Setup_5.2.2.exe' in this directory.
echo.

:eof
pause
endlocal
