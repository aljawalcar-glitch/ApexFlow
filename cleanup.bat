@echo off
setlocal

echo.
echo =================================================
echo  ApexFlow Build Cleanup Script (Safe Version)
echo =================================================
echo This script will remove temporary files and folders
echo created by the build process (PyInstaller).
echo.
echo IMPORTANT: This will NOT delete the 'dist' folder,
echo which contains your compiled application.
echo.
echo The following will be removed:
echo - The 'build' folder
echo - The 'ApexFlow.spec' file
echo.

set /p "choice=Are you sure you want to continue? (y/N): "
if /i not "%choice%"=="y" (
    echo Cleanup cancelled.
    goto :eof
)

echo.
echo Deleting temporary build files...

if exist "build" (
    echo Removing 'build' directory...
    rmdir /s /q "build"
)

if exist "ApexFlow.spec" (
    echo Removing 'ApexFlow.spec' file...
    del "ApexFlow.spec"
)

echo.
echo =================================================
echo  Cleanup complete!
echo =================================================
echo The 'dist' folder has been kept.
echo.

:eof
pause
endlocal
