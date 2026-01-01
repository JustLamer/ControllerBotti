@echo off
setlocal

REM Windows launcher for ControllerBotti
REM Usage: double-click or run from cmd

set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe main.py %*
) else (
  python main.py %*
)

endlocal
