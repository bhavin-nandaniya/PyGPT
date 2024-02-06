@echo off
echo Installing necessary Python modules...
call venv/Scripts/activate.bat
pip install -r requirements.txt
echo Running Python script...
python indexer.py
python run.py
pause