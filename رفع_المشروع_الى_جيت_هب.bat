@echo off
chcp 65001 > nul
echo ======================================================
echo    قناة الذكاء المؤسسي - رفع المشروع إلى GitHub
echo ======================================================
echo.
set /p REPO_URL="يرجى إدخال رابط مستودع GitHub الخاص بك (مثال: https://github.com/username/enterprise-intelligence-channel.git): "

if "%REPO_URL%"=="" (
    echo [خطأ] لم تقم بإدخال الرابط!
    pause
    exit /b
)

echo.
echo جاري ربط المستودع ورفع الملفات...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ======================================================
    echo   [نجاح] تم رفع كافة ملفات المشروع إلى GitHub بنجاح!
    echo ======================================================
) else (
    echo.
    echo [تنبيه] حدث خطأ أثناء الرفع، تأكد من صحة الرابط والصلاحيات.
)

pause

