@echo off
chcp 65001 >nul
cd /d "%~dp0frontend"
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)
echo Frontend: http://localhost:5173
call npm run dev
