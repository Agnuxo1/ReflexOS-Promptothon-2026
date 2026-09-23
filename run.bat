@echo off
setlocal
cd /d "%~dp0"
python run_reflexos.py %*
exit /b %errorlevel%
