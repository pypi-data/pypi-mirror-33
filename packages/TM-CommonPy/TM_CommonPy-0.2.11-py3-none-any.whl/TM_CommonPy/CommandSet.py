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
from TM_CommonPy import TMLog
import pickle
import dill

##region Private
def _GetDependencyRoots(sConanBuildInfoTxtFile):
    bRootIsNext = False
    with open(sConanBuildInfoTxtFile,'r') as vFile:
        cReturning = []
        for sLine in vFile:
            if "[rootpath_" in sLine:
                bRootIsNext = True
                continue
            if bRootIsNext:
                bRootIsNext = False
                cReturning.append(sLine.strip())
    TMLog.debug("_GetDependencyRoots`cReturning:"+TM.Narrator.Narrate(cReturning))
    return cReturning

def GetRecommendedIntegrationFilePaths(sConanBuildInfoTxtFile):
    cReturning = []
    for sRoot in _GetDependencyRoots(sConanBuildInfoTxtFile):
        sRecommendedIntegrationFile = os.path.join(sRoot,"RecommendedIntegration.py")
        if os.path.isfile(sRecommendedIntegrationFile):
            cReturning.append(sRecommendedIntegrationFile)
    TMLog.debug("GetRecommendedIntegrationFilePaths`cReturning:"+TM.Narrator.Narrate(cReturning))
    return cReturning



def _GetRecommendedIntegrationsPair(sRoot):
    sRecommendedIntegrationFile = os.path.join(sRoot,"RecommendedIntegration.py")
    if os.path.isfile(sRecommendedIntegrationFile):
        TMLog.debug(__name__+"::_GetRecommendedIntegrationsPairsRecommendedIntegrationFile is file:"+sRecommendedIntegrationFile)
        RecommendedIntegration = TM.ImportFromDir(sRecommendedIntegrationFile)
        # sys.path.insert(0,sRoot)
        # import RecommendedIntegration
        if not hasattr(RecommendedIntegration,"Main"):
            raise AttributeError("RecommendedIntegration.Main")
        if not hasattr(RecommendedIntegration,"Main_Undo"):
            raise AttributeError("RecommendedIntegration.Main_Undo")
        return (TM.CopyFunction(RecommendedIntegration.Main),TM.CopyFunction(RecommendedIntegration.Main_Undo))
    else:
        TMLog.debug(__name__+"::_GetRecommendedIntegrationsPair`sRecommendedIntegrationFile is NOT file:"+sRecommendedIntegrationFile)
##endregion



#beta
class CommandSet:
    def __init__(self):
        self.PreviousCommandSet = []
        self.CommandSet = []
    def Que(self,cDoUndoPair,cArgs):
        if len(cDoUndoPair) != 2:
            raise ValueError(self.__class__.__name__+"::"+TM.FnName()+"`first arg must be a container of 2 methods: Do and Undo")
        if not TM.IsCollection(cArgs):
            cArgs = [cArgs]
        self.CommandSet.append([cDoUndoPair,cArgs])
    def QueImport(self,sFilePath):
        sFileBytes = open(sFilePath, "rb").read()
        sFileName = os.path.split(sFilePath)[1]
        self.Exec2(sFileBytes,sFileName)
        #sFileString = open(sFilePath, "r").read()
        #TMLog.debug(TM.FnName()+"`sFileString:"+sFileString)
        #Main()
        self.CommandSet.append([(self.DoNothing,self.Exec2),(sFileBytes,sFileName)])
    def Execute(self,bRedo=False):
        TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Open")
        if bRedo:
            #---Undo what is in PreviousCommandSet
            for vItem in self.PreviousCommandSet:
                TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Reundo:"+str(vItem[0]))
                self._Undo(vItem[0],vItem[1])
        else:
            #---Undo what is in PreviousCommandSet but not CommandSet
            for vItem in [x for x in self.PreviousCommandSet if x not in self.CommandSet]:
                TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Undo:"+str(vItem[0]))
                self._Undo(vItem[0],vItem[1])
        if bRedo:
            #---Do what is in CommandSet
            for vItem in self.CommandSet:
                TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Redo:"+str(vItem[0]))
                self._Do(vItem[0],vItem[1])
        else:
            #---Do what is in CommandSet but not PreviousCommandSet
            for vItem in [x for x in self.CommandSet if x not in self.PreviousCommandSet]:
                TMLog.debug(self.__class__.__name__+"::"+TM.FnName()+"`Do:"+str(vItem[0]))
                self._Do(vItem[0],vItem[1])
        #---
        self.PreviousCommandSet = self.CommandSet
        self.CommandSet = []
    def Save(self):
        with open('CommandSet.pickle', 'wb') as handle:
            dill.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)
    @staticmethod
    def _Do(cDoUndoPair,cArgs):
        cDoUndoPair[0](*cArgs)
    @staticmethod
    def _Undo(cDoUndoPair,cArgs):
        cDoUndoPair[1](*cArgs)
    @staticmethod
    def DoNothing(a,b):
        pass
    @staticmethod
    def TryLoad():
        try:
            with open('CommandSet.pickle', 'rb') as handle:
                return dill.load(handle)
        except FileNotFoundError:
            return TM.CommandSet()
    @staticmethod
    def Exec2(sFileBytes,sFileName):
        exec(compile(sFileBytes, sFileName, 'exec'),globals())
    @staticmethod
    def ExecFileInfo(cFileInfo):
        exec(compile(cFileInfo["sFileBytes"], cFileInfo["sFileName"], 'exec'))


    def QueConanPackageRecommendedIntegrations(self,sProj,sConanBuildInfoTxtFile):
        for sRoot in _GetDependencyRoots(sConanBuildInfoTxtFile):
            vDoUndoPair = _GetRecommendedIntegrationsPair(sRoot)
            if not vDoUndoPair is None:
                self.Que(vDoUndoPair,[sProj,sRoot])
