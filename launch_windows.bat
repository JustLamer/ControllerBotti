@echo off
setlocal

REM Windows launcher for ControllerBotti
REM Usage: double-click or run from cmd

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist "logs" mkdir logs
set LOG_FILE=logs\launcher_windows.log

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" main.py %* > "%LOG_FILE%" 2>&1
  if %ERRORLEVEL%==0 goto :eof
  goto :error
)

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 main.py %* > "%LOG_FILE%" 2>&1
  if %ERRORLEVEL%==0 goto :eof
  goto :error
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python main.py %* > "%LOG_FILE%" 2>&1
  if %ERRORLEVEL%==0 goto :eof
  goto :error
)

echo Python not found. Install Python 3 or create a .venv in this folder.
pause
goto :eof

:error
echo The app closed with an error. See "%LOG_FILE%" for details.
pause

endlocal
