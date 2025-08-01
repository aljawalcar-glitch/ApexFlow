@echo off
setlocal

echo.
echo =================================================
echo  ApexFlow Enhanced Build Script v2.0
echo =================================================
echo This script will compile the application using the enhanced spec file
echo and then build the installer.
echo.
pause

REM =================================================
REM PART 1: COMPILE THE PYTHON APPLICATION
REM =================================================
echo.
echo --- PART 1: Compiling the Python Application ---
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
echo --- PART 1 COMPLETED ---
echo Application compiled successfully in 'build_scripts/dist/ApexFlow' folder
echo.
pause

REM =================================================
REM PART 2: BUILD THE NSIS INSTALLER
REM =================================================
echo.
echo --- PART 2: Building the NSIS Installer ---
echo.

cd /d "%~dp0"
"C:\Program Files (x86)\NSIS\makensis.exe" "build_installer.nsi"

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] NSIS compilation failed or NSIS not found.
    echo You can manually run the installer script later.
    echo The compiled application is available in the 'dist' folder.
    pause
    goto :eof
)

echo.
echo =================================================
echo  SUCCESS! Build completed successfully!
echo =================================================
echo.
echo Files created:
echo   • Compiled app: build_scripts/dist/ApexFlow/
echo   • Installer: build_scripts/ApexFlow_Setup_5.2.2.exe
echo.
echo The application is ready for distribution!
echo.

:eof
pause
endlocal
