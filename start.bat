@echo off
cd /d "%~dp0"
title VOX//PROTOCOL - Neural Voice Studio

echo =======================================================================
echo   VOX//PROTOCOL - NEURAL VOICE STUDIO
echo   Enterprise Text-to-Speech and Voice AI SaaS Platform
echo =======================================================================
echo.
echo Launching VOX//PROTOCOL server...
echo Dashboard will automatically open in your browser at:
echo http://localhost:8000
echo.
echo Press Ctrl+C to stop the server.
echo =======================================================================
echo.

python run_server.py

if errorlevel 1 (
    echo.
    echo [ERROR] Server encountered an error.
    pause
)
