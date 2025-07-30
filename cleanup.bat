@echo off
echo Deleting temporary and unused files...

REM Delete documentation folder
IF EXIST "docs" (
    echo Deleting docs directory...
    rmdir /s /q "docs"
)

REM Delete documentation file
IF EXIST "data\ANTIVIRUS_INFO.md" (
    echo Deleting ANTIVIRUS_INFO.md...
    del "data\ANTIVIRUS_INFO.md"
)

REM Delete development scripts
IF EXIST "debug_build.bat" (
    echo Deleting debug_build.bat...
    del "debug_build.bat"
)
IF EXIST "assets\icons\create_icon.py" (
    echo Deleting create_icon.py...
    del "assets\icons\create_icon.py"
)

echo Cleanup process initiated. This script will delete itself now.

REM Self-delete this script
del "%~f0"
