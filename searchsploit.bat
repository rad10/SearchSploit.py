@echo off
set mycd = %cd%
set pythonscript = ""
cd %pythonscript%
python searchsploit.py %*
cd %mycd%