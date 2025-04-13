@echo off
echo Installing required Python packages...

REM Upgrade pip
python -m pip install --upgrade pip

REM Install discord.py (use the latest fork that supports slash commands)
pip install -U discord.py

REM Install Tornado
pip install tornado

REM Install mysql.connector
pip install mysql.connector

REM Install requests
pip install requests

echo All packages installed successfully!
pause