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
import types
from TM_CommonPy._Logger import TMLog
import TM_CommonPy as TM

##region Conan CommandSet
def GetDependencyRoots(sConanBuildInfoTxtFile):
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
    TMLog.debug("GetDependencyRoots`cReturning:"+TM.Narrator.Narrate(cReturning))
    return cReturning
##endregion

#dev
def GetGitTitleFromURL(sURL):
    return sURL[sURL.rfind("/")+1:sURL.rfind(".git")]

#dev
def GitPullOrClone(sURL,bCDIntoFolder=False):
    #---Open
    sCWD = os.getcwd()
    sName = GetGitTitleFromURL(sURL)
    #---
    #-Try to find .git
    sPathToGit = ""
    if os.path.exists(".git"):
        sPathToGit = "."
    elif os.path.exists(os.path.join(sName,".git")):
        sPathToGit = sName
    #-Pull or clone
    if sPathToGit != "":
        os.chdir(sPathToGit)
        Run("git pull "+sURL)
        if bCDIntoFolder:
            sCWD = "."
    else:
        Run("git clone "+sURL+" --no-checkout")
        if bCDIntoFolder:
            sCWD = sName
    #---Close
    os.chdir(sCWD)

#beta
def TryMkdir(sPath):
    try:
        os.mkdir(sPath)
    except FileExistsError:
        pass

#dev
def GitFullClean(bStash = False):
    if bStash:
        Run("git stash -u")
    else:
        Run("git clean -f")
        Run("git reset --hard")

#dev
def GitAbsoluteCheckout(sURL,sBranch=""):
    #---Open
    sCWD = os.getcwd()
    sName = GetGitNameFromURL(sURL)
    #---Get .git
    GitPullOrClone(sURL,bCDIntoFolder=True)
    #---Clean
    GitFullClean()
    #---Checkout
    Run("git checkout "+sBranch)
    #---Close
    os.chdir(sCWD)

#beta
#Maybe use __file__ instead?
def GetScriptRoot():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def GetFileContent(sFilePath):
    vFile = open(sFilePath,'r')
    sContent = vFile.read()
    vFile.close()
    return sContent

def GetXMLNamespaces(sXMLFile):
    cNamespaces = dict([
        node for _, node in xml.etree.ElementTree.iterparse(
            sXMLFile, events=['start-ns']
        )
    ])
    return cNamespaces

def GetRelFileNames(sDir):
    cFileNames = []
    for root, dirs, files in os.walk(sDir):
        sRelPath = root.replace(sDir, '')
        for f in files:
            cFileNames.append(os.path.join(sRelPath,f))
    return cFileNames

def GetFullFileNames(sDir):
    cFileNames = []
    for root, dirs, files in os.walk(sDir):
        for f in files:
            cFileNames.append(os.path.abspath(f))
    return cFileNames


def Copy(sSrc,sDstDir,bPreDelete=False,sExclude=""):
    #---PreDelete
    if bPreDelete:
        Delete(sDstDir)
    #---Dir
    if os.path.isdir(sSrc):
        for sRoot, cDirs, cFiles in os.walk(sSrc):
            dst_dir = sRoot.replace(sSrc, sDstDir, 1)
            if not os.path.exists(dst_dir):
                if not (sExclude != "" and sExclude in dst_dir):
                    os.makedirs(dst_dir)
            for file_ in cFiles:
                src_file = os.path.join(sRoot, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                if not (sExclude != "" and sExclude in src_file):
                    shutil.copy(src_file, dst_dir)
    #---File
    elif os.path.isfile(sSrc):
        if not (sExclude != "" and sExclude in sSrc):
            shutil.copy(sSrc, sDstDir)
    else:
        raise OSError("sSrc:"+sSrc+" is not a valid file or directory")

def GetDictCount(cDict):
    return len(cDict.values())

#alpha
def IsEmpty(cCollection):
    #---None
    if cCollection is None:
        return True
    #---Dict
    if isinstance(cCollection,dict):
        cCollection = cCollection.items()
    #---NotACollection
    try:
        for vKey,vValue in cCollection:
            pass
    except:
        return True
    #---Empty
    if len(cCollection) ==0:
        return True


#beta
def FindElem(vElemToFind,vTreeToSearch):
    for vElem in vTreeToSearch.iter():
        bFound = True
        #-tag or text differences?
        if not (vElemToFind.tag in vElem.tag and ((vElemToFind.text == vElem.text) or (vElemToFind.text is None))):
            bFound = False
            continue
        #-attrib differences?
        for vKey,vValue in vElemToFind.attrib.items():
            if not ((vKey in vElem.attrib) and (vElem.attrib[vKey] == vValue)):
                bFound = False
                break
        if not bFound:
            continue
        #-child differences?
        for vElemToFindChild in vElemToFind:
            if FindElem(vElemToFindChild,vElem) is None:
                bFound = False
                break
        #-If there are still no differences, we found it. Return the element
        if bFound:
            return vElem
    #-Couldn't find
    return

#dev
def AppendElemIfAbsent(vElemToAppend,vElemToAppendTo):
    if FindElem(vElemToAppend,vElemToAppendTo) is None:
        vElemToAppendTo.append(vElemToAppend)

#dev
def RemoveElem(vElemToRemoveTemplate,vElemToRemoveFrom):
    vElemToRemove = FindElem(vElemToRemoveTemplate,vElemToRemoveFrom)
    if not vElemToRemove is None:
        vElemToRemoveFrom.remove(vElemToRemove)

#dev
def IsCollection(vVar):
    try:
        iter(vVar)
        bCanIter = True
    except:
        bCanIter = False
    return bCanIter and not isinstance(vVar,str)

#dev
def RunPowerShellScript(sScriptFile):
    vProcess = subprocess.Popen(["powershell.exe","-executionpolicy ","bypass","-file",sScriptFile], shell=True)
    vProcess.communicate()
    return vProcess

#dev
#Currently, passing a string to subprocess.run will fail on linux (if shell=false) because lunix believes the first item is a param.
#To get around this, this function uses shlex to split the string  and pass it as a collection instead.
#More info here:https://codecalamity.com/run-subprocess-run/#arguments-as-string-or-list
def Run(sToRun):
    subprocess.run(shlex.split(sToRun,posix=False))

#dev
def Delete(sFilePathOrDir):
    if os.path.isdir(sFilePathOrDir):
        #-Change mode of all files to Write
        for root, dirs, files in os.walk(sFilePathOrDir):
            for sFilePath in files:
                os.chmod(os.path.join(root,sFilePath), stat.S_IWRITE)
        #-
        shutil.rmtree(sFilePathOrDir)
    elif os.path.exists(sFilePathOrDir):
        os.remove(sFilePathOrDir)

#dev
def MakeDir(sDir, bCDInto=False):
    if not os.path.exists(sDir):
        os.makedirs(sDir)
    os.chdir(sDir)

def ListFiles(sDir):
    sReturning = ""
    for root, dirs, files in os.walk(sDir):
        level = root.replace(sDir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        sReturning += "\n"+ '{}{}/'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            sReturning += "\n"+ '{}{}'.format(subindent, f)
    return sReturning

#dev
class fragile(object):
    class Break(Exception):
      """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error
#dev
#This function allows you to import a file witout poluting sys.path
def ImportFromDir(sFilePath):
    #---Determine sModuleName
    sModuleName = os.path.split(sFilePath)[1]
    if sModuleName[-3:] == ".py":
        sModuleName = sModuleName[:-3]
    #---Get vModule
    vSpec = importlib.util.spec_from_file_location(sModuleName, sFilePath)
    if vSpec is None:
        raise ValueError("ImportFromDir`Could not retrieve spec. \nsModuleName:"+sModuleName+"\nsFilePath:"+sFilePath+"\nCurrentWorkingDir:"+os.getcwd())
    vModule = importlib.util.module_from_spec(vSpec)
    #---Execute vModule
    vSpec.loader.exec_module(vModule)
    #---
    return vModule

#dev
def InstallAndImport(package):
    try:
        importlib.import_module(package)
    except ImportError:
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)

#dev
def TryGetCollectionAttrib(vObject,sAttribName):
    if hasattr(vObject,sAttribName):
        return getattr(vObject,sAttribName)
    else:
        return []

#dev
def MsgBox(sMsg):
    ctypes.windll.user32.MessageBoxW(0, sMsg, FnName(1), 1)

#beta
def FnName(iShift=0):
   return inspect.stack()[1+iShift][3]

#dev
def IsTextInFile(sText,sFilePath):
    try:
        with open(sFilePath, 'r') as vFile:
            return sText in vFile.read()
    except UnicodeDecodeError:
        with open(sFilePath, 'rb') as vFile:
            return sText in "".join(map(chr, vFile.read()))

#dev
def ImportSubmodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(ImportSubmodules(full_name))
    return results

#beta
def CopyFunction(vFunction):
    return types.FunctionType(vFunction.__code__, vFunction.__globals__, vFunction.__name__, vFunction.__defaults__, vFunction.__closure__)
