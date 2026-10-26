@echo off
setlocal
REM BID OWL offline synthetic walkthrough. Uses only packaged fake data.
REM Does not touch customer SQLite files or require ReportLab/cloud access.
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 demo_local.py
) else (
    python demo_local.py
)
set "DEMO_EXIT=%ERRORLEVEL%"
if not "%DEMO_EXIT%"=="0" (
    echo.
    echo BID OWL synthetic demo failed with exit code %DEMO_EXIT%.
    echo Python 3.11+ must be installed.
    pause
)
exit /b %DEMO_EXIT%
