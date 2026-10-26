@echo off
setlocal
REM BID OWL explicit offline CSV onboarding — customer inputs never sent online.
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 import_local.py
) else (
    python import_local.py
)
set "IMPORT_EXIT=%ERRORLEVEL%"
if not "%IMPORT_EXIT%"=="0" (
    echo.
    echo BID OWL local import could not complete (exit code %IMPORT_EXIT%).
    echo Python 3.11+ with Tkinter is needed for the graphical form.
    pause
)
exit /b %IMPORT_EXIT%
