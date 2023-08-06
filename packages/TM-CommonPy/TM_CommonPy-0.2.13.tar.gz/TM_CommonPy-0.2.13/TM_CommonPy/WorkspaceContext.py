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
class WorkspaceContext:
    def __init__(self,sPath,sSource=None,bPostDelete=True,bCDInto=True,bPreDelete=False):
        self.bCDInto = bCDInto
        self.bPostDelete = bPostDelete
        self.sPath = sPath
        self.sSource = sSource
        self.bPreDelete = bPreDelete
    def __enter__(self):
        if self.bPreDelete:
            TM.Delete(sPath)
        if self.sSource is None:
            TM.TryMkdir(self.sPath)
        else:
            TM.Copy(self.sSource,self.sPath)
        if self.bCDInto:
            self.OldCWD = os.getcwd()
            os.chdir(self.sPath)
    def __exit__(self,errtype,value,traceback):
        if self.bCDInto:
            os.chdir(self.OldCWD)
        if self.bPostDelete:
            TM.Delete(self.sPath)
