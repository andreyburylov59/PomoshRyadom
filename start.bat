@echo off
chcp 65001 >nul
echo ========================================
echo   Запуск "Помощь Рядом"
echo ========================================
echo.

if not exist venv (
    echo ❌ Виртуальное окружение не найдено!
    echo Сначала запустите install.bat
    pause
    exit /b 1
)

echo Активация виртуального окружения...
call venv\Scripts\activate.bat

echo.
echo 🚀 Запуск приложения...
echo.
echo 📍 Откройте в браузере: http://127.0.0.1:5000
echo.
echo Для остановки нажмите Ctrl+C
echo.

python app.py

pause
