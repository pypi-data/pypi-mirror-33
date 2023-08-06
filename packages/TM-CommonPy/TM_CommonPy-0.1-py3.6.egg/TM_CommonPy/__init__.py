import os, sys
import importlib
import pip
import xml.etree.ElementTree
import shutil

#Maybe use __file__ instead?
def GetScriptRoot():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def GetFileContent(sFile):
    vFile = open(sFile,'r')
    sContent = vFile.read()
    vFile.close()
    return sContent

#Works fine for non-BOM XML files.. but runs into trouble otherwise.
def GetXMLNamespaces(sXMLFile):
    cNamespaces = dict([
        node for _, node in xml.etree.ElementTree.iterparse(
            sXMLFile, events=['start-ns']
        )
    ])
    return cNamespaces

def Copy(src,root_dst_dir):
    if os.path.isdir(src):
        for src_dir, dirs, files in os.walk(src):
            dst_dir = src_dir.replace(src, root_dst_dir, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_dir)
    elif os.path.isfile(src):
        dst_dir = src_dir.replace(src, root_dst_dir, 1)
        shutil.copy(src, dst_dir)
    else:
        print("Copy|Error|src "+src+" is not a valid file or directory")

def GetDictCount(cDict):
    return len(cDict.values())

#not tested
def TryMakeDirs(sDir):
    if not os.path.exists(sDir):
        os.makedirs(sDir)

#not tested
def InstallAndImport(package):
    try:
        importlib.import_module(package)
    except ImportError:
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)
