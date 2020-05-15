@echo off
echo lunch kvThumb: Make gif from video files.
call conda.bat activate py376kv
python thumb.py
pause
rem # esto no funciona.
rem # cmd /k conda activate py38 | python thumb.py
rem # cmd /k python thumb.py

