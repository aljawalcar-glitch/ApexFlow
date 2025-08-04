@echo off
=================================================
Running ApexFlow NSIS Installer Build Script
=================================================
cd /d "%~dp0\build_scripts"
"C:\Program Files (x86)\NSIS\makensis.exe" "build_installer.nsi"
=================================================
NSIS Installer build process finished.
=================================================
pause
