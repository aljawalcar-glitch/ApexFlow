@echo off
:: ApexFlow Deep Clean Script
:: This script performs a comprehensive uninstallation of ApexFlow.
:: It removes application files, registry keys, and shortcuts.
:: WARNING: This will permanently remove the application and its settings.

::================================================================
:: 1. Request Administrator Privileges
::================================================================
echo Requesting administrator privileges...
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo This script requires administrator privileges.
    echo Please right-click the script and select "Run as administrator".
    goto:eof
)

::================================================================
:: 2. Confirmation Prompt
::================================================================
echo.
echo WARNING: This script will completely remove ApexFlow and its data.
echo This includes installation files, registry entries, and shortcuts.
echo This action cannot be undone.
echo.
set /p "confirm=Are you sure you want to continue? (Y/N): "
if /i "%confirm%" NEQ "Y" (
    echo Aborting operation.
    goto:eof
)

::================================================================
:: 3. Stop ApexFlow Process
::================================================================
echo.
echo --- Step 1: Stopping ApexFlow process ---
taskkill /F /IM ApexFlow.exe /T >nul 2>&1
if %errorlevel% EQU 0 (
    echo ApexFlow.exe process terminated successfully.
) else (
    echo ApexFlow.exe process not found or could not be terminated.
)
timeout /t 2 /nobreak >nul

::================================================================
:: 4. Remove Installation Directory
::================================================================
echo.
echo --- Step 2: Removing installation directory ---
set "InstallDir=%ProgramFiles%\ApexFlow"
if exist "%InstallDir%" (
    echo Found installation directory at: %InstallDir%
    echo Deleting...
    rmdir /s /q "%InstallDir%"
    if %errorlevel% EQU 0 (
        echo Directory removed successfully.
    ) else (
        echo Failed to remove directory. It might be in use.
    )
) else (
    echo Installation directory not found.
)

::================================================================
:: 5. Remove Registry Keys
::================================================================
echo.
echo --- Step 3: Removing registry keys ---
echo Deleting HKLM\Software\ApexFlow...
reg delete "HKLM\Software\ApexFlow" /f >nul 2>&1
if %errorlevel% EQU 0 (
    echo ApexFlow software key removed successfully.
) else (
    echo ApexFlow software key not found or could not be removed.
)

echo Deleting HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\ApexFlow...
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\ApexFlow" /f >nul 2>&1
if %errorlevel% EQU 0 (
    echo ApexFlow uninstall key removed successfully.
) else (
    echo ApexFlow uninstall key not found or could not be removed.
)

::================================================================
:: 6. Remove Shortcuts
::================================================================
echo.
echo --- Step 4: Removing shortcuts ---
set "DesktopShortcut=%USERPROFILE%\Desktop\ApexFlow.lnk"
if exist "%DesktopShortcut%" (
    echo Deleting desktop shortcut...
    del "%DesktopShortcut%"
) else (
    echo Desktop shortcut not found.
)

set "StartMenuDir=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ApexFlow"
if exist "%StartMenuDir%" (
    echo Deleting Start Menu folder...
    rmdir /s /q "%StartMenuDir%"
) else (
    echo Start Menu folder not found.
)

::================================================================
:: 7. Finalization
::================================================================
echo.
echo --- Deep Clean Finished ---
echo ApexFlow has been completely removed from your system.
echo It is now safe to install a new version.
echo.
pause
