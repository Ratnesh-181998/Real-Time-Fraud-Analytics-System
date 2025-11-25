@echo off
echo ========================================
echo Real-Time Fraud Analytics System
echo ========================================
echo.
echo Starting the system...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo [2/3] Starting API Server...
echo API will be available at: http://localhost:8000
start "Fraud Analytics API" cmd /k "cd src && python api_server.py"

REM Wait a bit for API to start
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting Web Dashboard...
echo Dashboard will be available at: http://localhost:3000
start "Fraud Analytics Dashboard" cmd /k "cd web-ui && python -m http.server 3000"

REM Wait a bit for server to start
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo System is starting up!
echo ========================================
echo.
echo API Server:      http://localhost:8000
echo API Docs:        http://localhost:8000/docs
echo Web Dashboard:   http://localhost:3000
echo.
echo Opening dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo Press any key to stop all services...
pause >nul

REM Kill the servers
taskkill /FI "WindowTitle eq Fraud Analytics API*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Fraud Analytics Dashboard*" /T /F >nul 2>&1

echo.
echo All services stopped.
echo.
pause
