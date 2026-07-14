@echo off
echo ============================================
echo   HoloOrb Frontend - Development Server
echo ============================================
echo.

echo [1/2] Installing dependencies...
call npm install

echo.
echo [2/2] Starting dev server on http://localhost:5173 ...
call npm run dev

pause
