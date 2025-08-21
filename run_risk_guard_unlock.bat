@echo off
setlocal
cd /d "%~dp0"

if not exist logs mkdir logs

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

".venv\Scripts\python.exe" "risk_guard.py" --unlock >> "logs\risk_guard.log" 2>&1
