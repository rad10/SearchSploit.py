@echo off
set pythonscript = ""
:: put in the exact directory where youre storing your script. you can place this in a folder in path and youll be able to run it like on linux
python "%pythonscript%\searchsploit.py" --colour %*
