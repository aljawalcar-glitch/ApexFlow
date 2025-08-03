@echo off
cls
echo =================================================
echo  Running ApexFlow Master Build Script
echo =================================================
echo.

REM Execute the master Python build script
python build_scripts/build_master.py

echo.
echo =================================================
echo  Build process finished.
echo =================================================
echo.
pause
