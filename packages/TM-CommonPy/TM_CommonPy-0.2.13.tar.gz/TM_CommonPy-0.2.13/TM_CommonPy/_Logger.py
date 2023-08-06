##region Settings
import os
bWriteLog = True
sLogFile = os.path.join(__file__,'..','TMLog.log')
##endregion
##region LogInit
import logging
TMLog = logging.getLogger(__name__)
TMLog.setLevel(logging.DEBUG)
try:
    os.remove(sLogFile)
except (PermissionError,FileNotFoundError):
    pass
if bWriteLog:
    bLogFileIsOpen = False
    try:
        os.rename(sLogFile,sLogFile)
    except PermissionError:
        bLogFileIsOpen = True
    except FileNotFoundError:
        pass
    if not bLogFileIsOpen:
        TMLog.addHandler(logging.FileHandler(sLogFile))
##endregion
