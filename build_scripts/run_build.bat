@echo off
echo ========================================
echo Running ApexFlow Build Script
echo ========================================
cd /d "%~dp0"
python build_master.py
echo.
echo Build process completed
pause
