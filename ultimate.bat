@echo off
setlocal enabledelayedexpansion

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🚀 ULTIMATE CLI - UNIFIED INSTALLER & LAUNCHER
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 1. PRE-FLIGHT CHECKS
echo 🔍 Checking System Requirements...

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)
echo ✅ Python found.

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Node.js not found! Social data features (Aggregator) will be disabled.
    set NODE_AVAILABLE=0
) else (
    echo ✅ Node.js found.
    set NODE_AVAILABLE=1
)

echo.
echo 📦 INSTALLING DEPENDENCIES (For All Folders)...

REM 2. INSTALL PYTHON BACKEND
echo.
echo [1/2] Setting up Market Analysis (Python)...
if not exist "venv" (
    echo    Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo    Installing Python packages...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
   echo    ⚠️ Warning: Python install issues. Check logs if CLI fails.
) else (
   echo    ✅ Backend ready.
)

REM 3. INSTALL NODE.JS AGGREGATOR
if %NODE_AVAILABLE%==1 (
    echo.
    echo [2/2] Setting up Social Aggregator (Node.js)...
    if exist "..\aggregator" (
        cd ..\aggregator
        echo    Installing npm packages...
        call npm install --silent >nul 2>&1
        if %errorlevel% neq 0 (
             echo    ⚠️ Warning: npm install failed.
        ) else (
             echo    ✅ Aggregator ready.
        )
        cd ..\market_analysis
    ) else (
        echo    ⚠️ Aggregator folder not found relative to script. Skipping.
    )
)

echo.
echo 🚀 STARTING SERVICES...

REM 4. START SERVICES
REM Check Backend (Port 8000)
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo    Starting Backend API...
    start /min "Market Analysis Backend" cmd /k "venv\Scripts\python api_server_production.py"
    timeout /t 5 >nul
) else (
    echo    ✅ Backend is running.
)

REM Check Aggregator (Port 4001)
if %NODE_AVAILABLE%==1 (
    curl -s http://localhost:4001/health >nul 2>&1
    if %errorlevel% neq 0 (
        echo    Starting Aggregator...
        cd ..\aggregator
        start /min "Aggregator Service" cmd /k "npm run dev"
        cd ..\market_analysis
        timeout /t 5 >nul
    ) else (
        echo    ✅ Aggregator is running.
    )
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 👉 ENTER STOCK SYMBOL (e.g., TATASTEEL.NS)
echo    OR Press [ENTER] to view Top 10 Stocks Menu
echo.
set /p SYMBOL="Selection: "

if "%SYMBOL%"=="" (
    echo 🚀 Launching Interactive Menu...
    venv\Scripts\python ultimate_cli.py
) else (
    echo 🚀 Launching Analysis for %SYMBOL%...
    venv\Scripts\python ultimate_cli.py "%SYMBOL%"
)

echo.
echo ✅ Session Ended.
pause
