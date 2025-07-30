@echo off
setlocal enabledelayedexpansion

:: Define progress display function
set "progressBar=####################"
set /a totalSteps=3
set /a currentStep=0

call :show_progress "Start..."

echo.
echo =================================================
echo     ApexFlow Final Build Script
echo =================================================
echo This script will compile the application and build the installer.
echo.
pause

:: STEP 1: Install dependencies
set /a currentStep+=1
call :show_progress "Installing dependencies..."
python -m pip install --upgrade pyside6 pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages.
    pause
    goto :eof
)

:: STEP 2: Compile application with PyInstaller
set /a currentStep+=1
call :show_progress "Compiling the application..."
python -m PyInstaller main.py ^
    --name ApexFlow ^
    --windowed ^
    --onedir ^
    --icon="assets/icons/ApexFlow.ico" ^
    --add-data="assets;assets" ^
    --add-data="modules/default_settings.json;modules" ^
    --clean
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller failed.
    pause
    goto :eof
)

:: STEP 3: Build NSIS installer
set /a currentStep+=1
call :show_progress "Building the installer..."
"C:\Program Files (x86)\NSIS\makensis.exe" "build_installer.nsi"
if %errorlevel% neq 0 (
    echo [ERROR] NSIS compilation failed.
    pause
    goto :eof
)

:: Done
echo.
echo =================================================
echo    ✅ SUCCESS! Installer built successfully!
echo =================================================
echo.
echo Output: ApexFlow_Setup_5.2.2.exe
echo.
goto :eof

:: ====== Progress bar function ======
:show_progress
cls
set /a percent=(currentStep*100)/totalSteps
set /a bars=(currentStep*20)/totalSteps
set "bar="
for /L %%i in (1,1,!bars!) do set "bar=!bar!#"
for /L %%i in (!bars!,1,20) do set "bar=!bar!."
echo [!bar!] !percent!%% - %~1
echo.
exit /b
