__version__ = '0.10.0'
#__all__ = ["CommandSet"]
##region ImportThisModule
from TM_CommonPy.Misc import *
del TMLog #TMLog is in Misc, but shouldn't be exposed
from TM_CommonPy.CommandSet import CommandSet
from TM_CommonPy.CopyContext import CopyContext
from TM_CommonPy.WorkspaceContext import WorkspaceContext
from TM_CommonPy.ElementTreeContext import ElementTreeContext
import TM_CommonPy.Narrator
##endregion
