@echo off
cd /d "%~dp0"
echo Setting up Newspim Monitor...
just setup
if %errorlevel% neq 0 (
    echo.
    echo Setup failed. Press any key to exit.
    pause >nul
)
echo.
echo Setup finished.
pause
