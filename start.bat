@echo off
cd /d "%~dp0"

echo [1/4] Starting Docker (postgres + redis)...
docker-compose up -d postgres redis

echo Waiting for database to be ready...
timeout /t 5 /nobreak > nul

echo [2/4] Starting Backend...
start "Backend" cmd /k "cd /d "%~dp0backend" && uvicorn app.main:app --reload"

echo [3/4] Starting Frontend...
start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo [4/4] Starting Admin...
start "Admin" cmd /k "cd /d "%~dp0admin" && npm run dev"

echo.
echo All services started!
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo   Frontend : http://localhost:5173
echo   Admin    : http://localhost:5174
echo.
pause
