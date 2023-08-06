##region Settings
bDebug = False
sIndent = "-"
##endregion

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


##region Public
def Narrate(vVar,iRecursionThreshold=2,bMultiLine=True,bIncludeProtected=False,bIncludePrivate=False,cMembers=[],bStartFull=True,cCOMSearchMembers=None,bHideDuplications=False,bNarrateDuplications=False):
    return Narrator(iRecursionThreshold=iRecursionThreshold,bMultiLine=bMultiLine,bIncludeProtected=bIncludeProtected,bIncludePrivate=bIncludePrivate,cMembers=cMembers,bStartFull=bStartFull,cCOMSearchMembers=cCOMSearchMembers,bHideDuplications=bHideDuplications,bNarrateDuplications=bNarrateDuplications)(vVar)
##endregion


class RecursionContext:
    def __init__(self,iRecursionThreshold):
        self.iRecursionThreshold = iRecursionThreshold
        self.iRecursionLvl = 0
    def __enter__(self):
        self.iRecursionLvl += 1
    def __exit__(self, errtype, value, traceback):
        self.iRecursionLvl -= 1
    def IsThresholdMet(self,iShift=0):
        return (self.iRecursionLvl + iShift) > self.iRecursionThreshold

class DuplicationGuard:
    def __init__(self,bNarrateDuplications):
        self.bNarrateDuplications = bNarrateDuplications
        self.cDuplicationGuardSet = []
    def __call__(self,vVar):
        #If vVar is in cDuplicationGuardSet, maybe report it. If it isn't, maybe add it.
        if vVar in self.cDuplicationGuardSet:
            if not self.bNarrateDuplications:
                return True
        else:
            #Since it is difficult for python to group-type without duck-typing, this is what it is.
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
                self.cDuplicationGuardSet.append(vVar)
        return False
    def IsDuplication(self,vVar):
        return vVar in self.cDuplicationGuardSet

class Narrator:
    def __init__(self,iRecursionThreshold=2,bMultiLine=True,bIncludeProtected=False,bIncludePrivate=False,cMembers=[],bStartFull=True,cCOMSearchMembers=None,bHideDuplications=False,bNarrateDuplications=False):
        #---Params
        self.bMultiLine=bMultiLine
        self.bIncludeProtected=bIncludeProtected
        self.bIncludePrivate=bIncludePrivate
        self.cMembers=cMembers
        self.bStartFull=bStartFull
        self.cCOMSearchMembers=cCOMSearchMembers
        self.bHideDuplications=bHideDuplications
        self.vRecursionContext = RecursionContext(iRecursionThreshold)
        self.vDuplicationGuard = DuplicationGuard(bNarrateDuplications)
        #---
        self.cReturningStrings = []
    def __call__(self,vVar):
        sReturning = ""
        self.Narrate(vVar)
        for vItem in self.cReturningStrings:
            sReturning += vItem
        return sReturning
    def Narrate(self,vVar):
        ##region RecursionContext
        #Recursion should be checked before Narrate is re-called. This re-check is just a precaution.
        if self.vRecursionContext.IsThresholdMet():
            raise Exception("Narrate`Threshold is met. Threshold should be checked before Narrate is called.")
        ##endregion
        ##region DuplicationGuard
        if self.vDuplicationGuard(vVar):
            try:
                sName = vVar.Name
            except:
                self.cReturningStrings.append("<Duplication>")
            else:
                self.cReturningStrings.append("<Duplication of "+sName+">")
            return
        ##endregion
        with self.vRecursionContext:
            #-------Pass to another Narrate command depending on type
            #---COM
            if str(type(vVar)) == "<class 'win32com.client.CDispatch'>":
                self.Narrate_COM(vVar)
            #---If it's a simple variable, return it as a string.
            elif isinstance(vVar,(str,numbers.Number)):   #This also captures bools.
                self.cReturningStrings.append(str(vVar))
            #---None
            elif vVar is None:
                self.cReturningStrings.append("<None>")
            #---etree Element
            elif isinstance(vVar,xml.etree.ElementTree.Element):
                self.NarrateElem(vVar)
            #---Collection
            elif isinstance(vVar,(dict,list,tuple)):
                self.NarrateCollection(vVar)
            #---Everything else
            else:
                self.NarrateObject(vVar)
        return self.cReturningStrings

    #--------------------------------------------------------------------------------------
    def __Indent(self,iShift=0):
        global sIndent
        return sIndent * (self.vRecursionContext.iRecursionLvl + iShift)
    def __NL(self,iShift=0):
        return '\n' +self.__Indent(iShift)
    def Narrate_COM(self,vObj):
        if hasattr(vObj,"Count"):
            self.Narrate_COM_Collection(vObj)
        elif hasattr(vObj,"Name"):
            self.Narrate_COM_Object(vObj)
        else:
            try:
                self.Narrate_COM_Object(vObj)
            except:
                self.cReturningStrings.append("<failureToExtract>")

    #If you try to vObj.Value depreciated COM objects, an error is thrown.
    def GetValueOfPair_COMObject(self,vObj):
        try:
            if hasattr(vObj,"Value"): #This is known to throw an error for depreciated objects.
                return getattr(vObj,"Value")
            else:
                return "<None>"
        except:
            return "<ValueError>"

    #dir() does not work for all members of COM objects
    def GetMembers_COM(self,vObj):
        if self.cCOMSearchMembers is None:
            self.cCOMSearchMembers = ["Name"
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
        for vKey in self.cCOMSearchMembers:
            if hasattr(vObj,vKey):
                try:
                    vValue = getattr(vObj,vKey)
                    cMembers[vKey] = vValue
                except:
                    cMembers[vKey] = "<failureToExtract>"
        return cMembers.items()

    def Narrate_COM_Object(self,vObj):
        if hasattr(vObj,"Name"):
            self.cReturningStrings.append("(Object_COM)"+vObj.Name+"..")
        else:
            try:
                self.cReturningStrings.append("(Object_COM)"+str(vObj)+"..")
            except:
                self.cReturningStrings.append("Object_COM..")
        #---
        if self.vRecursionContext.IsThresholdMet():
            self.cReturningStrings.append("  <RecursionLvlReached>")
        else:
            for vKey,vValue in self.GetMembers_COM(vObj):
                ##region DuplicationGuardContext
                if self.vDuplicationGuard.IsDuplication(vValue) and self.bHideDuplications:
                    continue
                ##endregion
                self.cReturningStrings.append(self.__NL() + vKey + ":")
                self.Narrate(vValue)


    def Narrate_COM_Collection(self,cCollection):
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
        self.cReturningStrings.append("Collection_COM..    Count:"+str(cCollection.Count))
        if self.vRecursionContext.IsThresholdMet():
            self.cReturningStrings.append("  <RecursionLvlReached>")
        else:
            try:
                if bColHasKeys:
                    for i in range(cCollection.Count):
                        ##region DuplicationGuardContext
                        if DuplicationGuardContext.IsDuplication(GetValueOfPair_COMObject(cCollection[i])) and bHideDuplications:
                            continue
                        ##endregion
                        self.cReturningStrings.append(self.__NL() + str(cCollection[i].Name) + ":")
                        self.Narrate(GetValueOfPair_COMObject(cCollection[i]))
                else:
                    for i in range(cCollection.Count):
                        ##region DuplicationGuardContext
                        if DuplicationGuardContext.IsDuplication(cCollection[i]) and bHideDuplications:
                            continue
                        ##endregion
                        self.cReturningStrings.append(self.__NL() + str(i)+":")
                        self.Narrate(cCollection[i])
            except:
                self.cReturningStrings.append("  <ExceptionRaised>")



    #cMembers are exclusionary if they start full, inclusionary if they start empty.
    def NarrateObject(self,vObj):
        return self.NarrateObject_Options(vObj, self.bIncludeProtected, self.bIncludePrivate, self.cMembers, self.cMembers, self.cMembers, self.bStartFull, self.bStartFull, self.bStartFull)

    #cMethods, cProperties, cExtras are exclusionary if they start full, inclusionary if they start empty.
    def NarrateObject_Options(self,vObj,bIncludeProtected=False,bIncludePrivate=False, cMethods = [], cProperties = [], cExtras = [], bMethodsStartFull = True, bPropertiesStartFull = True, bExtrasStartFull = True):
        self.cReturningStrings.append("Object..")
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
            self.cReturningStrings.append("<EmptyObject>")
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
        if self.vRecursionContext.IsThresholdMet():
            self.cReturningStrings.append("  <RecursionLvlReached>")
        else:
            for vKey,vValue in cExtrasBeingNarrated.items():
                self.cReturningStrings.append(self.__NL() + vKey + ":" + vValue)
            for sProperty in cPropertiesBeingNarrated:
                self.cReturningStrings.append(self.__NL() + sProperty + ":")
                self.Narrate(getattr(vObj, sProperty))
            for sMethod in cMethodsBeingNarrated:
                self.cReturningStrings.append(self.__NL() + sMethod + ":" + "Method")

    #beta
    def NarrateElem(self,vElem):
        self.cReturningStrings.append("*Tag:   \t"+str(vElem.tag))
        if not (vElem.text is None or vElem.text.isspace()):
            self.cReturningStrings.append(self.__NL(-1)+"text:  \t"+str(vElem.text).replace("\n","\\n"))
        if not TMC.IsEmpty(vElem.attrib):
            self.cReturningStrings.append(self.__NL(-1)+"attrib:\t")
            self.NarrateCollection(vElem.attrib, bMultiLine=False)
        if len(list(vElem)) !=0:
            self.cReturningStrings.append(self.__NL(-1)+"children..")
            if self.vRecursionContext.IsThresholdMet():
                self.cReturningStrings.append("  <RecursionLvlReached>")
            else:
                for vChild in vElem:
                    self.cReturningStrings.append(self.__NL())
                    self.Narrate(vChild)

    #beta
    def NarrateCollection(self,cCollection,bMultiLine=None):
        if bMultiLine is None:
            bMultiLine = self.bMultiLine
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
                self.cReturningStrings.append("<Unknown>")
                return
        #---Empty
        if len(cCollection) ==0:
            self.cReturningStrings.append("<EmptyCollection>")
            return
        #------Narrate the collection.
        if bMultiLine:
            self.cReturningStrings.append("Collection..")
            if self.vRecursionContext.IsThresholdMet():
                self.cReturningStrings.append("  <RecursionLvlReached>")
            else:
                for vKey,vValue in cCollection:
                    self.cReturningStrings.append(self.__NL() + str(vKey) + ":")
                    self.Narrate(vValue)
        else:
            self.cReturningStrings.append("{")
            bDoOnce = False
            if self.vRecursionContext.IsThresholdMet():
                self.cReturningStrings.append("  <RecursionLvlReached>")
            else:
                for vKey,vValue in cCollection:
                    if not bDoOnce:
                        bDoOnce = True
                    else:
                        self.cReturningStrings.append(" , ")
                    self.cReturningStrings.append(str(vKey) + ":")
                    self.Narrate(vValue)
            self.cReturningStrings.append("}")
