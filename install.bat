@echo off
chcp 65001 >nul
echo ========================================
echo   Установка "Помощь Рядом"
echo ========================================
echo.

echo Шаг 1: Создание виртуального окружения...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Ошибка создания виртуального окружения
    echo Убедитесь, что Python установлен и добавлен в PATH
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение создано

echo.
echo Шаг 2: Активация виртуального окружения...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Ошибка активации виртуального окружения
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение активировано

echo.
echo Шаг 3: Обновление pip...
python -m pip install --upgrade pip
echo ✅ pip обновлен

echo.
echo Шаг 4: Установка зависимостей...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)
echo ✅ Все зависимости установлены

echo.
echo Шаг 5: Инициализация базы данных...
python recreate_db.py
if %errorlevel% neq 0 (
    echo ⚠️  Ошибка инициализации базы данных
    echo База данных будет создана автоматически при первом запуске
)
echo ✅ База данных инициализирована

echo.
echo ========================================
echo   ✅ УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Для запуска приложения используйте: start.bat
echo Для просмотра презентации: presentation.bat
echo.
pause
