##region Settings
bWriteLog=True
##endregion

__version__ = '0.10.0'
#__all__ = ["CommandSet"]
##region LogInit
import logging, os
sLogFile = os.path.join(__file__,'..','TMLog.log')
TMLog = logging.getLogger(__name__)
TMLog.setLevel(logging.DEBUG)
try:
    os.remove(sLogFile)
except (PermissionError,FileNotFoundError):
    pass
if bWriteLog:
    TMLog.addHandler(logging.FileHandler(sLogFile))
##endregion
##region ImportThisModule
from TM_CommonPy.Misc import *
from TM_CommonPy.CommandSet import CommandSet
from TM_CommonPy.CommandSet import GetRecommendedIntegrationFilePaths
from TM_CommonPy.CopyContext import CopyContext
from TM_CommonPy.ElementTreeContext import ElementTreeContext
import TM_CommonPy.Narrator
##endregion
