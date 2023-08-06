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
import pickle
import dill
from enum import Enum
from types import ModuleType

#I can't put this into CommandSet or it becomes unpickleable.
#CommandSet_QueType = Enum("CommandSet_QueType","Function Script")
class CommandSet_QueType(Enum):
    Function = 1
    Script = 2
#beta
class CommandSet:
    def __init__(self):
        self.PreviousCommandSet = []
        self.CommandSet = []
    def Que(self,cDoUndoPair,cArgs):
        #---Filter
        if len(cDoUndoPair) != 2:
            raise ValueError(self.__class__.__name__+"::"+TM.FnName()+"`first arg must be a container of 2 methods: Do and Undo")
        if not TM.IsCollection(cArgs):
            cArgs = [cArgs]
        #---
        self.CommandSet.append([CommandSet_QueType.Function,cDoUndoPair,cArgs])
    def QueScript(self,sFilePath,cArgs):
        #---Filter
        if not os.path.isfile(sFilePath):
            raise FileNotFoundError("sFilePath is not a file:"+sFilePath)
        #---Determine sScript
        sScript = open(sFilePath).read()
        #---Make sure Script has Do and Undo
        vModule = ModuleType("CommandSetQuedScript", "This module represents a qued script")
        exec(sScript, vModule.__dict__)
        if not (hasattr(vModule,"Do") and hasattr(vModule,"Undo")):
            raise Exception("QueScript`Script must have Do and Undo functions.")
        #---
        self.CommandSet.append([CommandSet_QueType.Script,sScript,cArgs])
    def Execute(self,bRedo=False):
        TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Open")
        if bRedo:
            #---Undo what is in PreviousCommandSet
            for vItem in self.PreviousCommandSet:
                TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Reundo:"+str(vItem[0]))
                self._Undo(*vItem)
        else:
            #---Undo what is in PreviousCommandSet but not CommandSet
            for vItem in [x for x in self.PreviousCommandSet if x not in self.CommandSet]:
                TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Undo:"+str(vItem[0]))
                self._Undo(*vItem)
        if bRedo:
            #---Do what is in CommandSet
            for vItem in self.CommandSet:
                TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Redo:"+str(vItem[0]))
                self._Do(*vItem)
        else:
            #---Do what is in CommandSet but not PreviousCommandSet
            for vItem in [x for x in self.CommandSet if x not in self.PreviousCommandSet]:
                TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Do:"+str(vItem[0]))
                self._Do(*vItem)
        #---
        self.PreviousCommandSet = self.CommandSet
        self.CommandSet = []
    def Save(self):
        with open('CommandSet.pickle', 'wb') as handle:
            dill.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)
    def _Do(self,eQueType,vAction,cArgs):
        if eQueType == CommandSet_QueType.Function:
            vAction[0](*cArgs)
        elif eQueType == CommandSet_QueType.Script:
            vModule = ModuleType("CommandSetQuedScript", "This module represents a qued script")
            exec(vAction, vModule.__dict__)
            vModule.Do(*cArgs)
    def _Undo(self,eQueType,vAction,cArgs):
        if eQueType == CommandSet_QueType.Function:
            vAction[1](*cArgs)
        elif eQueType == CommandSet_QueType.Script:
            vModule = ModuleType("CommandSetQuedScript", "This module represents a qued script")
            exec(vAction, vModule.__dict__)
            vModule.Undo(*cArgs)
    @staticmethod
    def TryLoad():
        try:
            with open('CommandSet.pickle', 'rb') as handle:
                return dill.load(handle)
        except FileNotFoundError:
            return TM.CommandSet()
