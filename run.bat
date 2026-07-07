@echo off
setlocal

cd /d "%~dp0"
set PYTHONPATH=%~dp0Admin_api

echo [1/2] Running Alembic migrations...
python -m alembic upgrade head

echo [2/2] Starting Uvicorn server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
