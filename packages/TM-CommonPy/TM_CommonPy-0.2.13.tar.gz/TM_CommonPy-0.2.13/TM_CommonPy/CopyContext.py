import os, sys
import importlib
import pip
import xml.etree.ElementTree
import shutil
import subprocess
import shlex
import stat
import importlib
import pkgutil
import inspect
import importlib.util
import TM_CommonPy.Narrator
import ctypes
import TM_CommonPy as TM
from TM_CommonPy._Logger import TMLog

#beta
#depreciated by WorkspaceContext
class CopyContext:
    def __init__(self,sSource,sDestination,bPostDelete=False,bCDInto=True,bPreDelete=True):
        self.bCDInto = bCDInto
        self.bPostDelete = bPostDelete
        self.sDestination = sDestination
        self.sSource = sSource
        self.bPreDelete = bPreDelete
    def __enter__(self):
        TM.Copy(self.sSource,self.sDestination,bPreDelete=self.bPreDelete)
        if self.bCDInto:
            self.OldCWD = os.getcwd()
            os.chdir(self.sDestination)
    def __exit__(self,errtype,value,traceback):
        if self.bCDInto:
            os.chdir(self.OldCWD)
        if self.bPostDelete:
            TM.Delete(self.sDestination)
