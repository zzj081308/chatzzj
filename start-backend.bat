@echo off
chcp 65001 >nul
cd /d "%~dp0backend"
call .venv\Scripts\activate.bat
echo Backend: http://127.0.0.1:8000  (API docs: /docs)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
