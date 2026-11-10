@echo off
setlocal
chcp 65001 >nul
title Institutional Intelligence - Auto Merger

set "PYTHON_EXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    where python >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=python"
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python 3.12 was not found. Please install Python 3.12.
    pause
    exit /b 1
)

echo =================================================================
echo   Institutional Intelligence Studio - Enterprise Video Merger
echo =================================================================
echo.
"%PYTHON_EXE%" "%~dp005_أدوات_والأكواد_والأتمتة\tools\merge_enterprise_video.py" --episode 1
if errorlevel 1 (
    echo.
    echo [X] Merge encountered an error!
    pause
    exit /b 1
)

echo.
pause

