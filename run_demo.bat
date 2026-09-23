@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0src"
python app.py
exit /b %errorlevel%
