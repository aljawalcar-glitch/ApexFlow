@echo off
setlocal

echo --- SCRIPT DEBUG MODE ---
echo.
echo Step 1: Install packages. Press any key to continue...
pause
pip install --upgrade pyside6 pyinstaller
echo Command finished. Check for errors above.
pause

echo.
echo Step 2: Run PyInstaller. Press any key to continue...
pause
python -m PyInstaller main.py --name ApexFlow --windowed --onedir --icon="assets/icons/ApexFlow.ico" --add-data="assets;assets" --add-data="modules/default_settings.json;modules" --clean
echo Command finished. Check for errors above.
pause

echo.
echo Step 3: Run NSIS. Press any key to continue...
pause
"C:\Program Files (x86)\NSIS\makensis.exe" "build_installer.nsi"
echo Command finished. Check for errors above.
pause

echo.
echo --- SCRIPT FINISHED ---
pause
endlocal
