@echo off
echo Installing necessary Python modules...
call venv/Scripts/activate.bat
pip install -r requirements.txt
echo Running Python WebApp script...
python run.py
pause