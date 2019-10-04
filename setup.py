from tkinter import Tk
from tkinter.filedialog import askdirectory
import os

rcr = open(".searchsploit_rc", "r").read().splitlines()
print(rcr)

if input("Do you want to connect to the exploit database exploits? [Y/n]: ") == "Y":
    print("Please select the location of the exploit database")
    Tk().withdraw()
    edbexploits = askdirectory()
    print(edbexploits)
    if os.path.exists(edbexploits):
        rcr[6] = 'path_array+=("' + edbexploits + '")'
        rcr[14] = 'path_array+=("' + edbexploits + '")'

if input("Do you want to connect to the exploit database papers? [Y/n]: ") == "Y":
    print("Please select the location of the exploit database papers")
    Tk().withdraw()
    temp = askdirectory()
    print(temp)
    if os.path.exists(temp):
        rcr[22] = 'path_array+=("' + temp + '")'

# installing settings files in locations
rc = "\n".join(rcr)
if os.sys.platform == "win32":
    open(os.getenv("userprofile").replace(
        "\\", "/") + "/.searchsploit_rc", "w").write(rc)
    batch = open("searchsploit.bat", "r").readlines()
    batch[1] = 'set pythonscript="' + os.getcwd() + '"'
    batch = "\n".join(batch)
    open("searchsploit.bat", "w").write(batch)
else:
    try:
        open("/etc/.searchsploit_rc", "w").write(rc)
    except:
        open(os.path.expanduser("~").replace("\\", "/") +
             "/.searchsploit_rc", "w").write(rc)

print("Install complete. you may now use searchsploit freely")
if os.sys.platform == "win32":
    print("Take your batch script and move it to some place that youll use it.")
print("This script may need to be ran again if the contents in this folder move or if any databases move from their origional spots.")
