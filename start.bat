@echo off
REM Windows batch startup script for AttentionLens
REM Double-click this file to start both servers

echo Starting AttentionLens...
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Error: Virtual environment not found. Please run:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -e .
    pause
    exit /b 1
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo Starting FastAPI backend on port 8000...
start "AttentionLens Backend" cmd /k ".venv\Scripts\activate && uvicorn api.main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

echo Starting React frontend on port 5173...
start "AttentionLens Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ✓ AttentionLens is running!
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Close this window to stop (servers will keep running in their own windows)
pause
