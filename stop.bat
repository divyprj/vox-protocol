@echo off
cd /d "%~dp0"
title Stopping VOX//PROTOCOL Server

echo =======================================================================
echo   VOX//PROTOCOL - STOPPING SERVER
echo =======================================================================
echo.

set FOUND=0
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo Found server process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    set FOUND=1
)

if "%FOUND%"=="1" (
    echo.
    echo [SUCCESS] VOX//PROTOCOL application stopped completely.
) else (
    echo [INFO] VOX//PROTOCOL is not currently running on port 8000.
)

echo =======================================================================
echo.
ping 127.0.0.1 -n 3 >nul
