@echo off
setlocal

echo.
echo =================================================
echo  ApexFlow - Run Built Application
echo =================================================
echo.

if exist "dist\ApexFlow\ApexFlow.exe" (
    echo Starting ApexFlow...
    echo.
    cd /d "%~dp0"
    start "" "dist\ApexFlow\ApexFlow.exe"
    echo ApexFlow started successfully!
) else (
    echo [ERROR] ApexFlow.exe not found!
    echo Please build the application first using:
    echo   build-quick.bat  (for quick build)
    echo   build.bat        (for full build)
    echo.
    pause
)

echo.
endlocal
