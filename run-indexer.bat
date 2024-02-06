@echo off
echo Installing necessary Python modules...
call venv/Scripts/activate.bat
pip install -r requirements.txt
echo Running Python indexer script...
python indexer.py
pause