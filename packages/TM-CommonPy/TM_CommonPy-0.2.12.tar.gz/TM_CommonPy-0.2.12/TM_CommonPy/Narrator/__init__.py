#-------Settings
bDebug = False
sIndent = "-"
#-------

#In python, this file is already considered a class
import os, sys
import importlib
import pip
import xml.etree.ElementTree
import shutil
import TM_CommonPy as TMC
import collections
import numbers
from pprint import pprint

_self = sys.modules[__name__]
iIndent = 0
iRecursionLvl = 0
iRecursionThreshold = 2
bSentRecursionMsg = False
cDuplicationGuardSet = None
bHideDuplications = False
bNarrateDuplications = False

def __Indent(iShift=0):
    return _self.sIndent * (_self.iRecursionLvl + iShift)
def __NL(iShift=0):
    return "\n" +__Indent(iShift)
class DuplicationGuardContext:
    def __init__(self,vVar):
        self.bCleanupDuplicationGuardSet = False
        global cDuplicationGuardSet
        if cDuplicationGuardSet is None:
            self.bCleanupDuplicationGuardSet = True
            cDuplicationGuardSet = []
        if vVar in cDuplicationGuardSet:
            self.bPass = False
        else:
            #Since python currently can't group-type without without duck-typing, this is what it is.
            if str(type(vVar)) == "<class 'win32com.client.CDispatch'>":
                bAdd = True
            elif isinstance(vVar,(str,numbers.Number)):   #This also captures bools.
                bAdd = False
            elif vVar is None:
                bAdd = False
            elif isinstance(vVar,xml.etree.ElementTree.Element):
                bAdd = False
            elif isinstance(vVar,(dict,list,tuple)):
                bAdd = True
            else:
                bAdd = True
            if bAdd:
                cDuplicationGuardSet.append(vVar)
            self.bPass = True
    def __enter__(self):
        return self.bPass
    def __exit__(self, errtype, value, traceback):
        global cDuplicationGuardSet
        if self.bCleanupDuplicationGuardSet:
            cDuplicationGuardSet = None
    def IsDuplication(vVar):
        return ((not cDuplicationGuardSet is None) and (vVar in cDuplicationGuardSet)) and not bNarrateDuplications
class RecursionContext:
    def __enter__(self):
        global iRecursionLvl
        iRecursionLvl += 1
    def __exit__(self, errtype, value, traceback):
        global iRecursionLvl
        iRecursionLvl -= 1
    def IsThresholdMet(iShift=0):
        return (_self.iRecursionLvl + iShift) > _self.iRecursionThreshold

def Narrate_COM(vObj,cCOMSearchMembers=[]):
    s = ""
    #-
    if hasattr(vObj,"Count"):
        s += Narrate_COM_Collection(vObj,cCOMSearchMembers=cCOMSearchMembers)
    elif hasattr(vObj,"Name"):
        s += Narrate_COM_Object(vObj,cCOMSearchMembers=cCOMSearchMembers)
    else:
        #try:
        s += Narrate_COM_Object(vObj,cCOMSearchMembers=cCOMSearchMembers)
        #except:
        #    s += "<failureToExtract>"
    return s

#If you try to vObj.Value depreciated COM objects, an error is thrown.
def GetValueOfPair_COMObject(vObj):
    try:
        if hasattr(vObj,"Value"): #This is known to throw an error for depreciated objects.
            return getattr(vObj,"Value")
        else:
            return "<None>"
    except:
        return "<ValueError>"

#dir() does not work for all members of COM objects
def GetMembers_COM(vObj,cCOMSearchMembers=[]):
    if not cCOMSearchMembers:
        cCOMSearchMembers = ["Name"
            ,"Object"
            ,"Collection"
            ,"ProjectItems"
            ,"Properties"
            ,"Files"
            ,"Filters"
            ,"ConfigurationManager"
            ,"Application"
            ,"SuppressUI"
            ,"Events"
            ,"Process"#guess
            ,"ProcessID"
            ,"ID"#guess
            ,"CurrentProcess"
            ,"LocalProcesses"
            ,"Programs"
            #,"DTE"
            ,"DebuggedProcesses"
            ]
    cMembers = {}
    for vKey in cCOMSearchMembers:
        if hasattr(vObj,vKey):
            try:
                vValue = getattr(vObj,vKey)
                cMembers[vKey] = vValue
            except:
                cMembers[vKey] = "<failureToExtract>"
    return cMembers.items()

def Narrate_COM_Object(vObj,cCOMSearchMembers=[]):
    if hasattr(vObj,"Name"):
        s = "(Object_COM)"+vObj.Name+".."
    else:
        try:
            s = "(Object_COM)"+str(vObj)+".."
        except:
            s = "Object_COM.."
    #---
    if RecursionContext.IsThresholdMet():
        s += "  <RecursionLvlReached>"
    else:
        for vKey,vValue in GetMembers_COM(vObj,cCOMSearchMembers):
            ##region DuplicationGuardContext
            if DuplicationGuardContext.IsDuplication(vValue) and bHideDuplications:
                continue
            ##endregion
            s += __NL() + vKey + ":" + _Narrate2(vValue,cCOMSearchMembers=cCOMSearchMembers)
    return s


def Narrate_COM_Collection(cCollection,cCOMSearchMembers=[]):
    ##region Determine bColHasKeys
    #Checking for Value is tricky because hasattr will throw an error for depreciated objects
    bColHasKeys = False
    for i in range(cCollection.Count):
        try:
            if not hasattr(cCollection[i],"Value"):
                break
        except:
            pass
    else: #If for loop never hit break.
        bColHasKeys = True
    ##endregion
    s = "Collection_COM..    Count:"+str(cCollection.Count)
    if RecursionContext.IsThresholdMet():
        s += "  <RecursionLvlReached>"
    else:
        try:
            if bColHasKeys:
                for i in range(cCollection.Count):
                    ##region DuplicationGuardContext
                    if DuplicationGuardContext.IsDuplication(GetValueOfPair_COMObject(cCollection[i])) and bHideDuplications:
                        continue
                    ##endregion
                    s += __NL() + str(cCollection[i].Name) + ":" + _Narrate2(GetValueOfPair_COMObject(cCollection[i]),cCOMSearchMembers=cCOMSearchMembers)
            else:
                for i in range(cCollection.Count):
                    ##region DuplicationGuardContext
                    if DuplicationGuardContext.IsDuplication(cCollection[i]) and bHideDuplications:
                        continue
                    ##endregion
                    s += __NL() + str(i)+":"+_Narrate2(cCollection[i],cCOMSearchMembers=cCOMSearchMembers)
        except:
            s += "  <ExceptionRaised>"
    return s



#cMembers are exclusionary if they start full, inclusionary if they start empty.
def NarrateObject(vObj,bIncludeProtected=False,bIncludePrivate=False, cMembers=[], bStartFull=True):
    return NarrateObject_Options(vObj, bIncludeProtected, bIncludePrivate, cMembers, cMembers, cMembers, bStartFull, bStartFull, bStartFull)

#cMethods, cProperties, cExtras are exclusionary if they start full, inclusionary if they start empty.
def NarrateObject_Options(vObj,bIncludeProtected=False,bIncludePrivate=False, cMethods = [], cProperties = [], cExtras = [], bMethodsStartFull = True, bPropertiesStartFull = True, bExtrasStartFull = True):
    sReturning = ""
    #------Reflection
    #---Reflect the object's members
    if not bIncludeProtected:
        cMembers = [x for x in dir(vObj) if not x.startswith("_")]
    elif not bIncludePrivate:
        cMembers = [x for x in dir(vObj) if not x.startswith("__")]
    else:
        cMembers = dir(vObj)
    #---Seperate cMethodsBeingNarrated and cPropertiesBeingNarrated from cMembers. Define cExtrasBeingNarrated.
    cExtrasBeingNarrated = {"Type":str(type(vObj))}
    cPropertiesBeingNarrated = [a for a in cMembers if not callable(getattr(vObj, a))]
    cMethodsBeingNarrated = [a for a in cMembers if callable(getattr(vObj, a))]
    #---Empty
    if len(cPropertiesBeingNarrated) ==0 and len(cMethodsBeingNarrated) ==0:
        sReturning += "<EmptyObject>"
    #------Exclusion/Inclusion
    if bExtrasStartFull:
        cExtrasBeingNarrated = { k : cExtrasBeingNarrated[k] for k in set(cExtrasBeingNarrated) - set(cExtras) }
    else:
        cExtrasBeingNarrated = { k : cExtrasBeingNarrated[k] for k in set(cExtrasBeingNarrated) & set(cExtras) }
    if bPropertiesStartFull:
        cPropertiesBeingNarrated = [a for a in cPropertiesBeingNarrated if a not in cProperties]
    else:
        cPropertiesBeingNarrated = [a for a in cPropertiesBeingNarrated if a in cProperties]
    if bMethodsStartFull:
        cMethodsBeingNarrated = [a for a in cMethodsBeingNarrated if a not in cMethods]
    else:
        cMethodsBeingNarrated = [a for a in cMethodsBeingNarrated if a in cMethods]
    #------Narration
    if RecursionContext.IsThresholdMet():
        sReturning += "  <RecursionLvlReached>"
    else:
        for vKey,vValue in cExtrasBeingNarrated.items():
            sReturning += __NL() + vKey + ":" + vValue
        for sProperty in cPropertiesBeingNarrated:
            sReturning += __NL() + sProperty + ":" + _Narrate2(getattr(vObj, sProperty))
        for sMethod in cMethodsBeingNarrated:
            sReturning += __NL() + sMethod + ":" + "Method"
    #---small fixes
    if sReturning == "":
        sReturning += "<Object>"
    else:
        sReturning = "Object.." + sReturning
    return sReturning

#beta
def NarrateElem(vElem):
    sReturning = "*Tag:   \t"+str(vElem.tag)
    if not (vElem.text is None or vElem.text.isspace()):
        sReturning += __NL()+"text:  \t"+str(vElem.text).replace("\n","\\n")
    if not TMC.IsEmpty(vElem.attrib):
        sReturning += __NL()+"attrib:\t"+NarrateCollection(vElem.attrib, bMultiLine=False)
    if len(list(vElem)) !=0:
        sReturning += __NL()+"children.."
        if RecursionContext.IsThresholdMet():
            s += "  <RecursionLvlReached>"
        else:
            for vChild in vElem:
                sReturning += __NL() + NarrateElem(vChild)
    return sReturning

#beta
def NarrateCollection(cCollection,bMultiLine = True):
    #------Convert to 2xiter collection
    #---Dict
    if isinstance(cCollection,dict):
        cCollection = cCollection.items()
    #---
    try:
        for vKey,vValue in cCollection:
            pass
    except:
        try:
            cTemp = {}
            i=0
            for vValue in cCollection:
                cTemp[str(i)] = vValue
                i += 1
            cCollection = cTemp.items()
        except:
            return "<Unknown>"
    #---Empty
    if len(cCollection) ==0:
        return "<EmptyCollection>"
    #------Narrate the collection.
    if bMultiLine:
        sReturning = "Collection.."
        if RecursionContext.IsThresholdMet():
            sReturning += "  <RecursionLvlReached>"
        else:
            for vKey,vValue in cCollection:
                sReturning += __NL() + str(vKey) + ":" + _Narrate2(vValue)
        return sReturning
    else:
        sReturning = "{"
        bDoOnce = False
        if RecursionContext.IsThresholdMet():
            s += "  <RecursionLvlReached>"
        else:
            for vKey,vValue in cCollection:
                if not bDoOnce:
                    bDoOnce = True
                else:
                    sReturning += " , "
                sReturning += str(vKey) + ":" + _Narrate2(vValue)
        sReturning += "}"
        return sReturning


#In-house defaults
def _Narrate2(vVar,iRecursionThreshold=12345,bMultiLine=True,bIncludeProtected=False,bIncludePrivate=False,cMembers=[],bStartFull=True,cCOMSearchMembers=[],bHideDuplications=False,bNarrateDuplications=False):
    iRecursionThreshold=_self.iRecursionThreshold   #_self.iRecursionThreshold cannot be used as default value
    bHideDuplications=_self.bHideDuplications
    bNarrateDuplications=_self.bNarrateDuplications
    return Narrate(vVar,iRecursionThreshold=iRecursionThreshold,bMultiLine=bMultiLine,bIncludeProtected=bIncludeProtected,bIncludePrivate=bIncludePrivate,cMembers=cMembers,bStartFull=bStartFull,cCOMSearchMembers=cCOMSearchMembers,bHideDuplications=bHideDuplications,bNarrateDuplications=bNarrateDuplications)


#------Public
#release
def Print(vVar,iRecursionThreshold=2,bMultiLine=True,bIncludeProtected=False,bIncludePrivate=False,cMembers=[],bStartFull=True,cCOMSearchMembers=[],bHideDuplications=False,bNarrateDuplications=False):
    print(Narrate(vVar,iRecursionThreshold=iRecursionThreshold,bMultiLine=bMultiLine,bIncludeProtected=bIncludeProtected,bIncludePrivate=bIncludePrivate,cMembers=cMembers,bStartFull=bStartFull,cCOMSearchMembers=cCOMSearchMembers,bHideDuplications=bHideDuplications,bNarrateDuplications=bNarrateDuplications))

#beta
def Narrate(vVar,iRecursionThreshold=2,bMultiLine=True,bIncludeProtected=False,bIncludePrivate=False,cMembers=[],bStartFull=True,cCOMSearchMembers=[],bHideDuplications=False,bNarrateDuplications=False):
    _self.bHideDuplications = bHideDuplications
    _self.bNarrateDuplications = bNarrateDuplications
    ##region RecursionContext
    _self.iRecursionThreshold = iRecursionThreshold
    #Recursion should be checked before Narrate is re-called. This re-check is just a precaution.
    if RecursionContext.IsThresholdMet():
        if not _self.bSentRecursionMsg:
            _self.bSentRecursionMsg = True
            return "<ReachedRecursionThreshold 2>"
        else:
            return ""
    _self.bSentRecursionMsg = False
    ##endregion
    ##region DuplicationGuardContext
    if DuplicationGuardContext.IsDuplication(vVar):
        try:
            sName = vVar.Name
        except:
            return "<Duplication>"
        else:
            return "<Duplication of "+sName+">"
    ##endregion
    with RecursionContext(), DuplicationGuardContext(vVar):
        #-------Pass to another Narrate command depending on type
        #---COM
        if str(type(vVar)) == "<class 'win32com.client.CDispatch'>":
            sReturning = Narrate_COM(vVar,cCOMSearchMembers)
        #---If it's a simple variable, return it as a string.
        elif isinstance(vVar,(str,numbers.Number)):   #This also captures bools.
            sReturning = str(vVar)
        #---None
        elif vVar is None:
            sReturning = "<None>"
        #---etree Element
        elif isinstance(vVar,xml.etree.ElementTree.Element):
            sReturning = NarrateElem(vVar)
        #---Collection
        elif isinstance(vVar,(dict,list,tuple)):
            sReturning = NarrateCollection(vVar,bMultiLine)
        #---Everything else
        else:
            sReturning = NarrateObject(vVar,bIncludeProtected,bIncludePrivate,cMembers,bStartFull)
        return sReturning
