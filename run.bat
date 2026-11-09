@echo off
setlocal

set PYTHON_BIN=C:\Users\Asus\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PYTHON_BIN%" (
    where python >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_BIN=python
    ) else (
        where py >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            set PYTHON_BIN=py
        ) else (
            echo Python interpreter not found.
            exit /b 1
        )
    )
)

if "%~1"=="" (
    "%PYTHON_BIN%" -m src.main --config config.json
) else if "%~1"=="test" (
    "%PYTHON_BIN%" -m unittest discover -s tests -p "test_*.py" -v
) else (
    "%PYTHON_BIN%" %*
)
