@echo off
setlocal

REM Windows launcher for ControllerBotti
REM Usage: double-click or run from cmd

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" main.py %*
  goto :eof
)

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 main.py %*
  goto :eof
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python main.py %*
  goto :eof
)

echo Python not found. Install Python 3 or create a .venv in this folder.
pause

endlocal
