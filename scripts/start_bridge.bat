@echo off
:: Chrome Bridge — Windows launcher
:: Double-click to start, or run from cmd: start_bridge.bat

echo ==========================================
echo   Chrome Bridge — Startup
echo ==========================================

:: Find Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)

:: Check websockets
python -c "import websockets" >nul 2>&1
if %errorlevel% neq 0 (
    echo [SETUP] Installing websockets...
    python -m pip install websockets -q
)

:: Check if already running
netstat -ano 2>nul | findstr ":19876" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [INFO] Server already running on port 19876
    goto :test
)

:: Create runtime dir
if not exist "%~dp0..\runtime" mkdir "%~dp0..\runtime"

:: Start in background
echo [START] Launching server in background...
start /B python -u "%~dp0..\bridge\server.py" > "%~dp0..\runtime\server.log" 2>&1

:: Wait for startup
timeout /t 2 /nobreak >nul

:test
echo [TEST] Sending ping...
python "%~dp0..\bridge\cli.py" ping

echo.
echo ==========================================
echo   Server running on:
echo     HTTP API:  http://127.0.0.1:19877/cmd
echo     WebSocket: ws://127.0.0.1:19876
echo ==========================================
echo.
echo   Now load the extension in Chrome:
echo     chrome://extensions -^> Dev mode -^> Load unpacked
echo   Select: %~dp0..\extension
echo.
pause
