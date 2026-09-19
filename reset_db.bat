@echo off
chcp 65001 >nul
echo ========================================
echo   Пересоздание базы данных
echo ========================================
echo.

if not exist venv (
    echo ❌ Виртуальное окружение не найдено!
    echo Сначала запустите install.bat
    pause
    exit /b 1
)

echo ⚠️  ВНИМАНИЕ! Все данные в базе будут удалены!
echo.
set /p confirm=Продолжить? (Y/N): 
if /i not "%confirm%"=="Y" (
    echo Отменено
    pause
    exit /b 0
)

echo.
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

echo.
echo 🔄 Пересоздание базы данных...
python recreate_db.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ База данных успешно пересоздана!
    echo ✅ Добавлены тестовые данные
) else (
    echo.
    echo ❌ Ошибка при пересоздании базы данных
)

echo.
pause
