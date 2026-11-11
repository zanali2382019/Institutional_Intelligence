@echo off
setlocal
chcp 65001 >nul
title NEXORA Studio - Master Long-Form Merger (Episode 01)

set "PYTHON_EXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    where python >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=python"
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python was not found. Please install Python.
    pause
    exit /b 1
)

echo =================================================================
echo   NEXORA STUDIO — دمج وإنتاج الحلقة الأولى الوثائقية الكاملة
echo   كارثة المستخلصات: كيف ابتلع بند خرسانة واحد 12 مليون دولار؟
echo =================================================================
echo.
"%PYTHON_EXE%" "%~dp005_أدوات_والأكواد_والأتمتة\tools\merge_longform_episode01.py"
if errorlevel 1 (
    echo.
    echo [X] حدث خطأ أثناء الدمج، تأكد من وجود ملفات الفيديو في مجلد الإنتاج.
    pause
    exit /b 1
)

echo.
echo =================================================================
echo   [تم بنجاح] مبروك! تم تصدير الحلقة الأولى بالكامل بجودة 1080p
echo =================================================================
pause

