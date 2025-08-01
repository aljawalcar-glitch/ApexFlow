@echo off
chcp 65001 > nul
title ApexFlow - PDF Processing Tool

echo.
echo ========================================
echo    ApexFlow - أداة معالجة ملفات PDF
echo ========================================
echo.

python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo خطأ في تشغيل التطبيق!
    echo تأكد من تثبيت Python والمتطلبات
    echo.
    pause
)
