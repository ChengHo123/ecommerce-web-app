@echo off
cd /d "%~dp0"

echo [1/4] Starting Docker (postgres + redis)...
docker-compose up -d postgres redis

@REM echo Waiting for database to be ready...
@REM timeout /t 5 /nobreak > nul

wt -w 0 ^
  -d "%~dp0backend" cmd /k "call conda activate web-backend && uvicorn app.main:app --reload" ; ^
  new-tab -d "%~dp0frontend" cmd /k "npm run dev" ; ^
  new-tab -d "%~dp0admin" cmd /k "npm run dev"

echo.
echo All services started!
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo   Frontend : http://localhost:5173
echo   Admin    : http://localhost:5174
echo.
pause
