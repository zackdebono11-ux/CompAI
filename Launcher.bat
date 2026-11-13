@echo off
setlocal
cd /d "%~dp0"
title CompAI v0.15.0
if exist "%~dp0startup_voice.ps1" (
    start "" powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0startup_voice.ps1"
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 "%~dp0CompAI_GUI.py"
) else (
    python "%~dp0CompAI_GUI.py"
)
if errorlevel 1 (
    echo.
    echo CompAI could not start. Check that Python and Tkinter are installed.
    pause
)
endlocal
