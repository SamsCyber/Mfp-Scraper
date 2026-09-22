@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python get_macros.py    
pause