@echo off
REM Explicit local CSV/company onboarding. No network or writable HTTP endpoints.
call "%~dp0backend\START_IMPORT.cmd"
exit /b %ERRORLEVEL%
