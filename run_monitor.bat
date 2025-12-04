@echo off
cd /d "%~dp0"
echo Starting Newspim Monitor...
just run
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)
