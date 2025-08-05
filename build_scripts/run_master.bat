@echo off
echo ========================================
echo      Running ApexFlow Master Build
echo ========================================
cd /d "%~dp0"
python build_master.py
echo.
echo ========================================
echo      Build process finished.
echo ========================================
pause
