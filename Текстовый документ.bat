@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ========================================
echo    Запуск Python проекта с venv
echo ========================================

REM Функция для поиска папки venv
set VENV_FOUND=0
set VENV_PATH=

echo Поиск виртуального окружения...
for /d /r . %%d in (.venv) do (
    if exist "%%d\Scripts\activate.bat" (
        set "VENV_PATH=%%d"
        set "VENV_FOUND=1"
        echo Найдено виртуальное окружение: %%d
        goto :venv_found
    )
)

:venv_found
if %VENV_FOUND%==0 (
    echo Ошибка: Виртуальное окружение не найдено!
    echo Ищу папку с именем 'venv' в текущей и подпапках...
    echo Если venv в другом месте, укажите путь вручную.
    echo.
    set /p VENV_PATH="Введите полный путь к папке venv: "
    
    if not exist "!VENV_PATH!\Scripts\activate.bat" (
        echo Ошибка: В указанной папке нет виртуального окружения
        pause
        exit /b 1
    )
)

REM Запрос пути к Python скрипту
echo.
set SCRIPT_PATH="D:\Python\AlfaServis\Constructor\projects\specification\spec_app.py"

REM Проверка существования скрипта
if not exist "!SCRIPT_PATH!" (
    echo Ошибка: Файл не существует - !SCRIPT_PATH!
    pause
    exit /b 1
)

REM Проверка расширения файла
echo "!SCRIPT_PATH!" | findstr /i "\.py$" > nul
if errorlevel 1 (
    echo Внимание: Файл не имеет расширения .py
    set /p CONFIRM="Вы уверены, что хотите запустить этот файл? (y/n): "
    if /i not "!CONFIRM!"=="y" (
        echo Отмена запуска
        pause
        exit /b 0
    )
)

echo.
echo ========================================
echo Запуск проекта:
echo Виртуальное окружение: !VENV_PATH!
echo Python скрипт: !SCRIPT_PATH!
echo ========================================
echo.

REM Активация виртуального окружения
echo Активация виртуального окружения...
call "!VENV_PATH!\Scripts\activate.bat"

if errorlevel 1 (
    echo Ошибка при активации виртуального окружения
    pause
    exit /b 1
)

echo Виртуальное окружение активировано
echo.

REM Запуск Python скрипта
echo Запуск Python скрипта...
python "!SCRIPT_PATH!"

set EXIT_CODE=%errorlevel%

echo.
echo ========================================
if %EXIT_CODE%==0 (
    echo Скрипт выполнен успешно
) else (
    echo Скрипт завершился с кодом ошибки: %EXIT_CODE%
)
echo ========================================
echo.

REM Деактивация venv (опционально)
call "!VENV_PATH!\Scripts\deactivate.bat" > nul 2>&1

pause
exit /b %EXIT_CODE%