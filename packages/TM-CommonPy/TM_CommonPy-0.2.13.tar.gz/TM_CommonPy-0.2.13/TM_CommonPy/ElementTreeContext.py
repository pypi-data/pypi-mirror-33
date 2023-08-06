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
class ElementTreeContext:
    def __init__(self,sXMLFile,bSave=True):
        self.bSave = bSave
        self.sXMLFile = sXMLFile
    def __enter__(self):
        self.vTree = xml.etree.ElementTree.parse(self.sXMLFile)
        return self.vTree
    def __exit__(self,errtype,value,traceback):
        if self.bSave:
            #-Register namespaces, otherwise ElementTree will prepend all elements with the namespace.
            for sKey, vValue in TM.GetXMLNamespaces(self.sXMLFile).items():
                xml.etree.ElementTree.register_namespace(sKey, vValue)
            self.vTree.write(self.sXMLFile)
