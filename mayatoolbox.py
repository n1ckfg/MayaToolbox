'''
MayaToolbox was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center

Copyright (c) 2018 Nick Fox-Gieg
http://fox-gieg.com
'''

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
import xml.etree.ElementTree as etree
from random import uniform as rnd
import os
import sys
import sys as sys
import re
import json
from operator import itemgetter

# GENERAL UTILITIES

#delete history
def ch(target=None):
    if not target:
        target = s()
    for i in range(0,len(target)):
        s(target[i])
        mc.delete(ch=True)

#select
def s(_t=None, d=False, all=False):
    if(d==True):
        py.select(d=True)
    elif(all==True):
        py.select(all=True)
    else:
        if not _t:
            try:
                py.select(py.ls(sl=1))
            except:
                print("Nothing selected.")
            return(py.ls(sl=1))
        else:
            py.select(_t)
            return _t

def ss(_t=None, d=False, all=False):
    return s(_t, d, all)[0]

#time
def t(_t=None):
    try:
        mc.currentTime(_t)
    except:
        print "time: " + str(mc.currentTime(q=True))
    return mc.currentTime(q=True)

#delete
def d(_t=None, all=False):
    if _t:
        s(_t)
    if all:
        s(all=True)
    py.delete()

#delete all
def rm():
    d(all=True)

#move
def m(p, _t=None):
    if not _t:
        _t = mc.ls(sl=1)

    for i in range (0,len(_t)):
        mc.select(_t[i])
        mc.move(p[0],p[1],p[2])

#keyframe
def k(_t=None):
    if(_t):
        mc.select(_t)
    mc.setKeyframe()

#group
def g(_t=None):
    if not _t:
        _t = mc.ls(sl=1)
    obj = mc.group(_t)
    return obj

#center pivot
def cp(_t=None):
    if not _t:
        _t = s()
    py.xform(_t, cp=True)

def listAll(target=None):
    allJoints = []
    if not target:
        target = s()
    if(len(target)==1):
        allJoints = mc.listRelatives(ad=1)
        allJoints.append(target[0])        
    else:
        for i in range(0,len(target)):
            joints = mc.listRelatives(ad=1)
            joints.append(target[i])
            allJoints.append(joints)
        
    print allJoints
    return allJoints

def listAllCurves():
    return mc.ls(type="nurbsCurve", long=True, allPaths=True)

def getCurveCvs(target=None):
    points = []
    if not target:
        target = ss()
    cvs = mc.getAttr(target + ".cp",s=1)
    try:
        if(len(cvs) > 1):
            cvs = int(cvs[0])
    except:
        pass
    print(cvs)
    for i in range(0, cvs):
        point = py.getAttr(target + ".cv[" + str(i) + "]")
        points.append(point)
    return points

def getAllCurveCvs():
    strokes = []
    curves = listAllCurves()
    for curve in curves:
        try:
            points = getCurveCvs(curve)
            strokes.append(points)
        except:
            pass
    return strokes

def posAll(target=None):
    pos = []
    
    if not target:
        target = s()
    
    obj = listAll()
    
    for i in range(0,len(obj)):
        p = getPos([obj[i]])
        pos.append(p[0])
        
    print pos
    return pos

#random 3d vector
def rnd3d(spread=5):
    return [rnd(-spread,spread),rnd(-spread,spread),rnd(-spread,spread)]

#move to random location
def rndMove(spread=5):
    val = rnd3d(spread)
    mc.move(val[0],val[1],val[2])

#get position
def getPos(target=None):
    returns = []
    if not target:
        target = s()
    
    for i in range(0,len(target)):
        p = py.xform(target[i], q=True, t=True, ws=True)
        returns.append(p)
    return returns

#move to last object
def moveTo(target=None):
    #1. make an array of all selected objects
    if not target:
        target = mc.ls(sl=1)
    
    #2. get the position of the last selected object
    pos = mc.xform(target[len(target)-1], q=True, t=True, ws=True)
    
    #3. move the other objects to the last selected object
    for i in range(0,len(target)-1):
        mc.select(target[i])
        mc.move(pos[0],pos[1],pos[2])

#toggle visibility
def showHide(target=None):
    if not target:
       target = s()

    for i in range(0,len(target)):
        visible = mc.getAttr(target[i] + ".v")
        if(visible==False):
           mc.setAttr(target[i] + ".v", 1)
        if(visible==True):
           mc.setAttr(target[i] + ".v", 0)

'''
def show(target=None):
    if not target:
        target = s()
    for i in range(0, len(target)):
        mc.setAttr(target[i] + ".v", 1)

def hide(target=None):
    if not target:
        target = s()
    for i in range(0, len(target)):
        mc.setAttr(target[i] + ".v", 0)
'''

#toggle selectability
def toggleSelectable(target=None):
    if not target:
        target = mc.ls(sl=1)
    for i in range(0,len(target)):
        disabled = mc.getAttr(target[i] + ".overrideDisplayType")
        if(disabled==2):
            mc.setAttr(target[i] + ".overrideDisplayType",0)
        else:
            mc.setAttr(target[i] + ".overrideEnabled",1)
            mc.setAttr(target[i] + ".overrideDisplayType",2)

def getAllObjects():
    s(all=True)
    target = s()
    s(d=True)
    return target

def getNewObjects(oldObjects):
    newObjects = getAllObjects()
    finalList = newObjects
    for i, newObj in enumerate(newObjects):
        for oldObj in oldObjects:
            if (newObj == oldObj):
                finalList = [x for x in finalList if x != oldObj]
    return finalList
    
#reset transformations to 0
def freezeTransformations(target=None):
    if not target:
        target = mc.ls(sl=1)
    mc.select(target)
    mel.eval("makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;")
    return target
#~~

#parent to last selection
def parentLast():
    #1. make an array of all selected objects
    target = mc.ls(sl=1)

    #2. parent each selected object to the last object
    for i in range(0,len(target)-1):
        mc.select(target[i])
        mc.parent(target[i],target[len(target)-1])


    #3. select last object
    mc.select(target[len(target)-1])
    
#~~

#parent each selection to the next
def parentChain():
    #1. make an array of all selected objects
    target = mc.ls(sl=1)

    #2. parent each selected object to the last object
    for i in range(0,len(target)):
        if(i>0):
            mc.select(target[i])
            mc.parent(target[i],target[i-1])


    #3. select first object
    mc.select(target[0])
    
#~~

def instanceFirst(doShaders=False):
    #1. make an array of all selected objects
    target = mc.ls(sl=1)

    #2. if only one selection, just make a new instance at the same coordinates...
    if(len(target)==1):
        mc.instance()

    else:
        #3. ...otherwise, for each selected object...
        for i in range(1,len(target)):

            #4. ...get current selection's position and copy keyframes and shader
            mc.select(target[i])
            pos = mc.xform(target[i], q=True, t=True, ws=True)
            try:
                shader = getShader()
            except:
                print "Couldn't get shader."
            try:
                mc.copyKey()
            except:
                print "Couldn't copy keys."

            #5. instance the first selection
            mc.select(target[0])
            mc.instance()
        
            #6. move first selection to position and paste keyframes and shader
            mc.move(pos[0],pos[1],pos[2])
            if(doShaders==True):
                setShader(shader)
            try:
                mc.pasteKey()
            except:
                print "Couldn't paste keys."
           
            #7. delete selection
            mc.delete(target[i])

#~~

# http://download.autodesk.com/us/maya/2009help/CommandsPython/fileDialog.html
# http://download.autodesk.com/us/maya/2011help/CommandsPython/fileDialog2.html

def openFileDialog(fileFilter="*"):
    returns = py.fileDialog2(fileFilter="*." + fileFilter, dialogStyle=1, fileMode=1)
    return str(returns[0])

def saveFileDialog(fileFilter="*"):
    returns = py.fileDialog2(fileFilter="*." + fileFilter, dialogStyle=1, fileMode=0)
    return str(returns[0])

def duplicateFirst(doShaders=False):
    #1. make an array of all selected objects
    target = mc.ls(sl=1)

    #2. if only one selection, just make a new duplicate at the same coordinates...
    if(len(target)==1):
        #call through mel because python has no rc option!
        mel.eval("duplicate -un -ic -rc")

    else:
        try:
            #3. check if the first selection is skinned.
            mc.select(target[0])
            mc.skinCluster(q=True)
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            print "Select the root joint for this to work properly."
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        except:
            #4. ...otherwise, for each selected object...
            for i in range(1,len(target)):

                #5. ...get current selection's position and copy keyframes and shader
                mc.select(target[i])
                pos = mc.xform(target[i], q=True, t=True, ws=True)
                try:
                    shader = getShader()
                except:
                    print "Couldn't get shader."
                try:
                    mc.copyKey()
                except:
                    print "Couldn't copy keys."

                #6. duplicate the first selection
                mc.select(target[0])
                #call through mel because python has no rc option!
                mel.eval("duplicate -un -ic -rc")
            
                #7. move first selection to position and paste keyframes and shader
                mc.move(pos[0],pos[1],pos[2])
                if(doShaders==True):
                    setShader(shader)
                try:
                    mc.pasteKey()
                except:
                    print "Couldn't paste keys."
               
                #8. delete selection
                mc.delete(target[i])
                
#~~


def duplicateSpecial(target = None, name = None):
    returns = []

    #1. make an array of all selected objects
    if not target:
        target = mc.ls(sl=1)

    #2. for each selected object...
    for i in range(0,len(target)):
        #3. ...select and duplicated with bones and keyframes
        mc.select(target[i])
        #call through mel because python has no rc option!
        if not name:
            val = mel.eval("duplicate -un -ic -rc")
        else:
            val = mel.eval("duplicate -un -ic -rc -name \"" + name + "\"")
        returns.append(val)

    return returns[0] #why is returns an array inside an array?

# by David Bokser davidbokser.com
def getUniqueName(name):
    # if the name is already unique, return it
    if not mc.ls(name):
        return name
    else:
        # find the trailing digit in the name
        trailingDigit = re.sub('.*?([0-9]*)$',r'\1',name)
        
        # create default variables for newDigit and shortname
        # in case there is no trailing digit (ie: "pSphere")
        newDigit = 1
        shortname = name
        
        if(trailingDigit):
            # increment the last digit and find the shortname using the length
            # of the trailing digit as a reference for how much to trim
            newDigit = int(trailingDigit)+1
            shortname = name[:-len(trailingDigit)]
        
        # create the new name
        newName = shortname+str(newDigit)

        # recursively run through the function until a unique name is reached and returned
        return getUniqueName(newName)

#~~

def lookAt(target=None):
    if not target:
        target = mc.ls(sl=1)

    angleBtwnNode = angleBetween(v1=(1, 0, 0), v2=(1, 0, 0), ch=True)

    mc.connectAttr( target[len(target)-1]+'.translateX', angleBtwnNode+'.vector2X' )
    mc.connectAttr( target[len(target)-1]+'.translateY', angleBtwnNode+'.vector2Y' )
    mc.connectAttr( target[len(target)-1]+'.translateZ', angleBtwnNode+'.vector2Z' )

    for i in range(0,len(target)-1):

        convertX = mc.createNode( 'unitConversion' )
        mc.connectAttr( angleBtwnNode+'.eulerX', convertX+'.input' )
        mc.connectAttr( convertX+'.output', target[i]+'.rotateX' )

        convertY = mc.createNode( 'unitConversion' )
        mc.connectAttr( angleBtwnNode+'.eulerY', convertY+'.input' )
        mc.connectAttr( convertY+'.output', target[i]+'.rotateY' )

        convertZ = mc.createNode( 'unitConversion' )
        mc.connectAttr( angleBtwnNode+'.eulerZ', convertZ+'.input' )
        mc.connectAttr( convertZ+'.output', target[i]+'.rotateZ' )

#unfinished
def tryGetAngle():
    s(["camera1"])
    resetRotation()

    target = s(["head","neck","camera2"])

    scaler = 10

    for i in range(inTime(),outTime()):
        t(i)
        v1 = xform(target[0], q=True, t=True, ws=True)
        v2 = xform(target[1], q=True, t=True, ws=True)

        r = angleBetween(vector1=v1,vector2=v2,euler=True)
        print r
        s(target[2])
        rotate(r[0]*scaler,r[1]*scaler,r[2]*scaler, rotateXYZ=True)
        k()

#~~

def inTime(newTime=None):
    if newTime != None and newTime != 0:
        mc.playbackOptions(minTime=newTime, animationStartTime=newTime)
    elif newTime != None and newTime ==0:
        mc.playbackOptions(minTime=newTime, animationStartTime=newTime)
    return int(mc.playbackOptions(q=True, animationStartTime=True))

def outTime(newTime=None):
    if newTime != None and newTime != 0:
        mc.playbackOptions(maxTime=newTime, animationEndTime=newTime)
    elif newTime != None and newTime ==0:
        mc.playbackOptions(maxTime=newTime, animationEndTime=newTime)
    #return int(mc.playbackOptions(q=True, animationEndTime=True)) + 2
    return int(mc.playbackOptions(q=True, animationEndTime=True))

def getStartEnd():
    #return inTime(), outTime()
    return inTime(), outTime() + 1

def checkStartEnd():
    start, end = getStartEnd()
    for i in range(start, end):
        print(str(i))

def bakeKeys(target=None, iT=inTime(), oT=outTime()):
    if not target:
        target=s()

    for i in range(0,len(target)): 
        py.mel.eval("bakeResults -simulation true -t \"" + str(iT) + ":" + str(oT) + "\" -sampleBy 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {\"" + str(target[i]) + "\"};")

bakeAnimation = bakeKeys

def resetAll(target=None, iT=inTime(), oT=outTime()):
    resetPosition(target, iT, oT)
    resetRotation(target, iT, oT)
    resetScale(target, iT, oT)

def normalizeAll(target=None, iT=inTime(), oT=outTime()):
    normalizePosition(target)
    normalizeRotation(target)
    normalizeScale(target)

def resetPosition(target=None, iT=inTime(), oT=outTime()):
    if not target:
        target = s()

    for i in range(0,len(target)):

        for m in range(iT,oT):
            try:
                py.keyframe(target[i]+'.translateX',edit=True,time=[m],valueChange=0)
                py.keyframe(target[i]+'.translateY',edit=True,time=[m],valueChange=0)
                py.keyframe(target[i]+'.translateZ',edit=True,time=[m],valueChange=0)
            except:
                print "Couldn't set keyframe " + str(m) + "."

def resetRotation(target=None, iT=inTime(), oT=outTime()):
    if not target:
        target = s()

    for i in range(0,len(target)):

        for m in range(iT,oT):
            try:
                py.keyframe(target[i]+'.rotateX',edit=True,time=[m],valueChange=0)
                py.keyframe(target[i]+'.rotateY',edit=True,time=[m],valueChange=0)
                py.keyframe(target[i]+'.rotateZ',edit=True,time=[m],valueChange=0)
            except:
                print "Couldn't set keyframe " + str(m) + "."  

def resetScale(target=None, iT=inTime(), oT=outTime()):
    if not target:
        target = s()

    for i in range(0,len(target)):

        for m in range(iT,oT):
            try:
                py.keyframe(target[i]+'.scaleX',edit=True,time=[m],valueChange=1)
                py.keyframe(target[i]+'.scaleY',edit=True,time=[m],valueChange=1)
                py.keyframe(target[i]+'.scaleZ',edit=True,time=[m],valueChange=1)
            except:
                print "Couldn't set keyframe " + str(m) + "."  

def normalizePosition(target=None, iT=inTime(), oT=outTime()):
    x = 0
    y = 0
    z = 0

    p = []

    if not target:
        target = s()

    for i in range(0,len(target)):

        for j in range(iT,oT):
            t(j)
            pp = py.xform(target[i], q=True, t=True, ws=True)
            p.append(pp)

            pOrig = p[0]

            for m in range(iT,oT):
                try:
                    x = p[m][0]-pOrig[0]
                    y = p[m][1]-pOrig[1]
                    z = p[m][2]-pOrig[2]

                    py.keyframe(target[i]+'.translateX',edit=True,time=[m],valueChange=x)
                    py.keyframe(target[i]+'.translateY',edit=True,time=[m],valueChange=y)
                    py.keyframe(target[i]+'.translateZ',edit=True,time=[m],valueChange=z)
                except:
                    print "Couldn't set keyframe " + str(m) + "."

def normalizeRotation(target=None, iT=inTime(), oT=outTime()):
    x = 0
    y = 0
    z = 0

    p = []

    if not target:
        target = s()

    for i in range(0,len(target)):

        for j in range(iT,oT):
            t(j)
            pp = py.xform(target[i], q=True, rotation=True, ws=True)
            p.append(pp)

            pOrig = p[0]

            for m in range(iT,oT):
                try:
                    x = p[m][0]-pOrig[0]
                    y = p[m][1]-pOrig[1]
                    z = p[m][2]-pOrig[2]
                    
                    py.keyframe(target[i]+'.rotateX',edit=True,time=[m],valueChange=x)
                    py.keyframe(target[i]+'.rotateY',edit=True,time=[m],valueChange=y)
                    py.keyframe(target[i]+'.rotateZ',edit=True,time=[m],valueChange=z)
                except:
                    print "Couldn't set keyframe " + str(m) + "."

def normalizeScale(target=None, iT=inTime(), oT=outTime()):
    x = 0
    y = 0
    z = 0

    p = []

    if not target:
        target = s()

    for i in range(0,len(target)):

        for j in range(iT,oT):
            t(j)
            pp = mc.py.xform(target[i], q=True, scale=True, ws=True)
            p.append(pp)

            pOrig = p[0]

            for m in range(iT,oT):
                try:
                    x = p[m][0]/pOrig[0]
                    y = p[m][1]/pOrig[1]
                    z = p[m][2]/pOrig[2]
                    
                    py.keyframe(target[i]+'.scaleX',edit=True,time=[m],valueChange=x)
                    py.keyframe(target[i]+'.scaleY',edit=True,time=[m],valueChange=y)
                    py.keyframe(target[i]+'.scaleZ',edit=True,time=[m],valueChange=z)
                except:
                    print "Couldn't set keyframe " + str(m) + "."

def renamer(source="", dest="", target=None):
    if not target:
        target = s()
        target = mc.listRelatives( target, ad=True ) + target

    for i in range(0,len(target)):
        s(target[i])
        nameText = str(target[i])
        nameText = nameText.replace(source,dest)
        print nameText
        mc.rename(target[i], nameText)
        
def pcount():
    returns = mc.polyEvaluate(f=True)
    return returns

def unparent(target = None):
    if not target:
        target = s()
    py.parent(target, world=True)

def roundVal(a, b):
    formatter = "{0:." + str(b) + "f}"
    return formatter.format(a)

def roundValInt(a):
    formatter = "{0:." + str(0) + "f}"
    return int(formatter.format(a))
# ANIMATION--JOINTS, CONSTRAINTS, KEYFRAMES, ETC.

def timeSequence(target=None):
    if not target:
        target = s()
    for i in range(start, end-1):
        for j in range(0, len(target)):
            if (i==j+1):
                mc.setAttr(target[j] + ".v", 1, keyable=True)
            else:
                mc.setAttr(target[j] + ".v", 0, keyable=True)
            mc.setKeyframe(time=i)

def looseJoints(target=None):
    if not target:
        target = s()
        
    for i in range(0,len(target)):
        s(target[i])
        jnt = py.joint(name=getUniqueName(target[i]+"_jnt"))
        unparent(jnt)

def createConstraint(target=None, type="parent"):
    if not target:
        target = s()

    #point, orient, and parent constraints work similarly
    if(type=="orient"):
        mel.eval("orientConstraint -mo -weight 1;")
    if(type=="parent"):
        mel.eval("parentConstraint -mo -weight 1;")
    if(type=="point"):
        mel.eval("pointConstraint -mo -weight 1;")

    return target

# legacy   
def orientConstraint(target=None):
    if not target:
        target = s()

    mel.eval("orientConstraint -mo -weight 1;")

    return target
    
def testJoints(numChains = 2, numJoints = 5, selectLast=True):
    rm()
    obj = makeChains(numChains,numJoints)
    if(selectLast==True):
        mc.select(obj[len(obj)-1][0])    
    return obj

def makeChains(numChains = 2, numJoints = 5):
    returns = []
    mc.select(d=True)
    for i in range(0,numChains):
        joints = makeJoints(numJoints)
        mc.select(joints[0])
        mc.move(numJoints*i,0,0)
        mc.select(d=True)
        returns.append(joints)
    return returns

def cleanJoints(target=None):
    if not target:
        target = s()
    
    for i in range(0,len(target)):
        s(target[i])
        mel.eval("makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;")
        mel.eval("joint -e  -oj none -ch -zso;")

def makeJoints(reps=3):
    joints = []
    offset = 0
    offsetDelta = 2
    middleJoint=0
    startPos = [0,0,0]
    target = mc.ls(sl=1)
    if(len(target)>=1):
        startPos = mc.xform(target[0], q=True, t=True, ws=True)
        startPos[0] += offsetDelta
        startPos[2] += offsetDelta
    
    if(reps%2==0): #even joints
        middleJoint = int(reps/2)-1
    else: #odd joints
        middleJoint = int(reps/2)
        
    for i in range(0,reps):
        if(i<=middleJoint):
            offset += offsetDelta
        else:
            offset -= offsetDelta
            
        newJoint = mc.joint(position=[startPos[0] + offset,startPos[1],startPos[2] + (i*4)])
        joints.append(newJoint)
    return joints

def keyAllChildren(op="set", jointsOnly=False): #set, cut, copy, paste
   selectedObjects = mc.ls(sl=True)
   targetObjects = mc.listRelatives( selectedObjects, ad=True ) + selectedObjects
   if(jointsOnly):
      targetObjects = mc.ls(targetObjects, type='joint')
   if(op=="set"):
      py.setKeyframe( targetObjects )
   elif(op=="cut"):
      py.cutKey( targetObjects )
   elif(op=="copy"):
      py.copyKey( targetObjects )
   elif(op=="paste"):
      py.pasteKey( targetObjects )   
   elif(op=="bake"):
      inTime=mc.playbackOptions(q=1,ast=1)
      outTime=mc.playbackOptions(q=1,aet=1)
      mc.bakeResults(targetObjects,simulation=1,sampleBy=1,time=(inTime,outTime))

def lockTranslate(target, doLock):
    mc.setAttr(target + ".translateX",lock=doLock)
    mc.setAttr(target + ".translateY",lock=doLock)
    mc.setAttr(target + ".translateZ",lock=doLock)

def lockRotate(target, doLock):
    mc.setAttr(target + ".rotateX",lock=doLock)
    mc.setAttr(target + ".rotateY",lock=doLock)
    mc.setAttr(target + ".rotateZ",lock=doLock)

def lockScale(target, doLock):
    mc.setAttr(target + ".scaleX",lock=doLock)
    mc.setAttr(target + ".scaleY",lock=doLock)
    mc.setAttr(target + ".scaleZ",lock=doLock)

def lockHandler(t, r, s): #bool, bool, bool
    target = mc.ls(sl=1)
    for i in range(0,len(target)):
        lockTranslate(target[i],t)
        lockRotate(target[i],r)
        lockScale(target[i],s)

def lockChildren(jointsOnly, t, r, s):
    target=mc.ls(sl=1)

    for i in range(0,len(target)):
       mc.select(target[i])
       lockHandler(t,r,s)

       try:
          if(jointsOnly==True):
             kids = mc.listRelatives(ls(selection=True), children=True, type="joint", allDescendents=True)
          else:
             kids = mc.listRelatives(ls(selection=True), children=True, allDescendents=True)
          for k in kids:
             mc.select(k)
             lockHandler(t,r,s)
       except:
          print "No child joints."

    mc.select(target)

def lockPuppet(jointsOnly=False):
    target=mc.ls(sl=1)
    
    for i in range(0,len(target)):
        try: #works, but generates a strange error
            py.select(target[i])
            lockHandler(False,False,False) #root joint is unlocked
            
            try:
                if(jointsOnly==True):
                    kids = mc.listRelatives(ls(selection=True), children=True, type="joint", allDescendents=True)
                else:
                    kids = mc.listRelatives(ls(selection=True), children=True, allDescendents=True)
                for k in kids:
                    py.select(k)
                    lockHandler(True,True,True) #lock all...
                    mc.setAttr(k + ".rotateX",lock=True) 
                    mc.setAttr(k + ".rotateZ",lock=False) 
                    mc.setAttr(k + ".rotateY",lock=True) #...except Z rotation.
                    mc.setAttr(k + ".translateX",lock=False) 
                    mc.setAttr(k + ".translateZ",lock=True) 
                    mc.setAttr(k + ".translateY",lock=False)
            except:
                print "No child joints."   
        except:
            print "Error."
            
    mc.select(target) 

def lockAll():
    lockChildren(False,True,True,True)

def lockNone():
    lockChildren(False,False,False,False)

def eyeRig(scaler): #try 4
    target = mc.ls(sl=1)
    mc.delete(e=True)
    for i in range(0,len(target)):
        if(i<len(target)-1):
            mc.expression(s=target[i]+".rotateX = " + target[len(target)-1] + ".translateY * -1 * " + str(scaler))
            mc.expression(s=target[i]+".rotateY = " + target[len(target)-1] + ".translateX * " + str(scaler))

def parentConstraintAll(target=None):
    if not target:
        target = mc.ls(sl=1)
    
    for i in range(0,len(target)):
        if(i<len(target)-1):
            mc.parentConstraint(target[len(target)-1],target[i],mo=1)
    mc.select(target)

def addLocator(alsoParent=False, name=None):
    #1. make an array of all selected objects
    target = mc.ls(sl=1)

    #2. if no selection, just make a locator at 0,0,0...
    if(len(target)==0):
        mc.spaceLocator()

    else:
        #3. otherwise, for each selected object...
        for i in range(0,len(target)):
        
            #4. ...if there are child joints, give them locators too
            try:
                kids = mc.listRelatives(target[i], children=True, type="joint", allDescendents=True)
                for k in kids:
                    if not name:
                        name = k + "_loc"
                    locPos = mc.xform(k, q=True, t=True, ws=True)
                    loc = mc.spaceLocator(n=name)
                    mc.move(locPos[0],locPos[1],locPos[2])
                    if(alsoParent==True):
                        mc.parent(k,loc)
                        #parentConstraint(loc,k)
            except:
                print "No child joints."

            #5. get the original selection's name
            if not name:
                name = target[i] + "_loc"
        
            #6. get its position
            locPos = mc.xform(target[i], q=True, t=True, ws=True)
        
            #7. create a new locator with that name at that position
            loc = mc.spaceLocator(n=name)
            mc.move(locPos[0],locPos[1],locPos[2])
            if(alsoParent==True):
                mc.parent(target[i],loc)
                #parentConstraint(loc,target[i])

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# DYNAMICS

def quickDyn(spread=5, num=10, joints=False, bake=False):
    target = []
    g = py.gravity()

    for i in range(0,num):
        c = py.polyCube()
        target.append(c)
        x = rnd(-spread,spread)
        y = rnd(-spread,spread) + 10
        z = rnd(-spread,spread)
        py.move(x,y,z)
        py.rotate(x,y,z)

    s(target)
    py.rigidBody()

    for i in range(0,len(target)):
        py.connectDynamic(target[i],f=g)

    if(joints==False and bake==True):
        bakeAnimation(target)
        
    if(joints==True):
        target2 = []

        for i in range(0,len(target)):
            s(target[i])
            jnt = py.joint()
            target2.append(jnt)
            
        if(bake==True):
            bakeAnimation(target2)

        for i in range(0,len(target2)):
            unparent(target2[i])

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# MOCAP

def buildFromLocators():
    looseJoints()
    #~~
    s(["r_hip","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["r_knee","r_hip_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["r_foot","r_knee_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["l_hip","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["l_knee","l_hip_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["l_foot","l_knee_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["r_shoulder","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["r_elbow","r_shoulder_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["r_hand","r_elbow_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["l_shoulder","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["l_elbow","l_shoulder_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["l_hand","l_elbow_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["neck","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["head","neck_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["torso_jnt","r_shoulder_jnt","r_elbow_jnt","r_hand_jnt"])
    parentChain()
    s(["torso_jnt","l_shoulder_jnt","l_elbow_jnt","l_hand_jnt"])
    parentChain()
    s(["torso_jnt","r_hip_jnt","r_knee_jnt","r_foot_jnt"])
    parentChain()
    s(["torso_jnt","l_hip_jnt","l_knee_jnt","l_foot_jnt"])
    parentChain()
    s(["torso_jnt","neck_jnt","head_jnt"])
    parentChain()
    #~~
    s(["torso","torso_jnt"])
    py.parentConstraint()
    #~~
    t = s("torso_jnt")
    tt = listAll()
    for i in range(0,len(tt)):
        s(tt[i])
        bakeKeys(iT=inTime(), oT=outTime())
    for i in range(0,len(tt)):
        py.delete(cn=True)
        

# Warning--cut-and-paste from other stuff, not cleaned up yet.
# http://eat3d.com/free/maya_python

# build XML
def writeK2P():
    startTime = int(mc.playbackOptions(query=True, minTime=True))
    stopTime = int(mc.playbackOptions(query=True, maxTime=True))
    filePath = "/Users/nick/Desktop/"
    fileName = "doc.xml"

    openniNames = ["head", "neck", "torso", "l_shoulder", "l_elbow", "l_hand", "r_shoulder", "r_elbow", "r_hand", "l_hip", "l_knee", "l_foot", "r_hip", "r_knee", "r_foot"]
    cmuNames = ["Head", "Neck1", "Spine", "LeftArm", "LeftForeArm", "LeftFingerBase", "RightArm", "RightForeArm", "RightFingerBase", "LeftUpLeg", "LeftLeg", "LeftToeBase", "RightUpLeg", "RightLeg", "RightToeBase"]
    mobuNames = ["Head", "Neck", "Spine", "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"]

    doc = Document()

    root_node = doc.createElement("MotionCapture")
    doc.appendChild(root_node)
    root_node.setAttribute("width", "640")
    root_node.setAttribute("height", "480")
    root_node.setAttribute("depth", "200")
    root_node.setAttribute("dialogueFile", "none")
    root_node.setAttribute("fps", "24")
    root_node.setAttribute("numFrames", str(stopTime))

    for i in range(startTime, stopTime+1):
        print str(startTime) + " " + str(stopTime)
        mc.currentTime(i)
        frame_node = doc.createElement("MocapFrame")
        root_node.appendChild(frame_node)
        frame_node.setAttribute("index",str(i-1))

        skel_node = doc.createElement("Skeleton")
        frame_node.appendChild(skel_node)
        skel_node.setAttribute("id","0")

        joint_node = doc.createElement("Joints")
        skel_node.appendChild(joint_node)

        target = py.selected()
        print target

        joints = py.listRelatives(target[0], ad=True)
        joints.append(target[0])
        print "~~~~~     " + str(joints) + "     ~~~~~"

        for j in range(0,len(joints)):
            try:
                theJointName = str(joints[j])
                for k in range(0,len(openniNames)):
                    if(theJointName==cmuNames[k] or theJointName==mobuNames[k]):
                        theJointName=openniNames[k]

                k_node = doc.createElement(theJointName)
                joint_node.appendChild(k_node)

                p = py.xform(joints[j], q=True, t=True, ws=True)
                k_node.setAttribute("x", str(-1 * p[0]))
                k_node.setAttribute("y", str(-1 * p[1]))
                k_node.setAttribute("z", str(p[2]))
            except:
                print "Couldn't get joint position."

    xml_file = open(filePath + fileName, "w")
    xml_file.write(doc.toprettyxml())
    xml_file.close()

    print doc.toprettyxml()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import xml.dom.minidom as xd

def readK2P():
    fileName = openFileDialog("xml")
    joints = ["l_foot","l_knee","l_hip","r_foot","r_knee","r_hip","l_hand","l_elbow","l_shoulder","r_hand","r_elbow","r_shoulder","torso","neck","head"]
    globalScale = (10, -10, 10)

    xmlFile = xd.parse(fileName)
    print("loaded: " + fileName)

    for joint in joints:    
        s(d=True)
        frames = xmlFile.getElementsByTagName(joint)
        loc = addLocator()
        mc.rename(loc, joint)

        for i, frame in enumerate(frames):
            x = float(frame.getAttribute("x")) * globalScale[0]
            y = float(frame.getAttribute("y")) * globalScale[1]
            z = float(frame.getAttribute("z")) * globalScale[2]
            
            mc.currentTime(i)
            mc.move(x, y, z)
            k()

    s(joints)
    buildFromLocators()

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

# MODELING

def getVerts(target=None):
    if not target:
        target = s()[0]
    return mc.getAttr(target + ".vrts", multiIndices=True)

def selectVerts(target=None):
    if not target:
        target = s()[0]
    py.select(target.vtx)

def fixAlembicColors(filePath=None):
    if not filePath:
        filePath = openFileDialog("abc")
    mel.eval("AbcImport -mode import -rcs 3fc \"" + filePath + "\";")

def fixNormals(target=None):
    if not target:
        target = s()

    for i in range(0,len(target)):
        s(target[i])
        py.polySetToFaceNormal()
        py.polySoftEdge()

def eroder(repeat=1, iter=1):
    for i in range(0,repeat):
        mc.polyAverageVertex(i=iter)
        ch()

def onVerts(target=None, normals=True, type="vector"):
    #1. make an array of all selected objects
    if not target:
        target = mc.ls(sl=1)

    #2. get the first selected object so it can be copied...
    foo = target[0]

    #3. then get the vertices of each other object and copy the first one there.
    for i in range(1,len(target)):

        v = getVertPos(target[i])
            
        for j in range(0,len(v)):
            s(foo)
            foo2 = py.duplicate()
            mc.move(v[j][0],v[j][1],v[j][2])

            if(normals==True):
                py.mel.eval("select -r " + target[i] + ".vtx[" + str(j) +"] " + foo2[0] + ";")
                py.normalConstraint(worldUpType=type)

            '''
            else:
            s(foo)
            py.mel.eval("duplicate -un -ic -rc")
            mc.move(v[j][0],v[j][1],v[j][2])
            '''
            
def getVertPos( shapeNode ) :
    vtxWorldPosition = []    # will contain positions in space of all object vertices
    vtxIndexList = mc.getAttr( shapeNode+".vrts", multiIndices=True )
 
    for i in vtxIndexList :
        curPointPosition = mc.xform( str(shapeNode)+".pnts["+str(i)+"]", query=True, translation=True, worldSpace=True )    # [1.1269192869360154, 4.5408735275268555, 1.3387055339628269]
        vtxWorldPosition.append( curPointPosition )
 
    return vtxWorldPosition

#from Sam Lavigne
def moveVerts(target=None, spread=1, time=1):
    if not target:
        target = s()

    for i in range(0,len(target)):
        # iterate through every vertex in the sphere           
        index = 1
        for v in target[i].vtx:
            # set initial position
            if(time > 1):
                py.setKeyframe(v, t=1)
            original = v.getPosition()

            # make a new position
            new_pos = [p + rnd(-spread, spread) for p in original]
            v.setPosition(new_pos)
            
            if(time > 1):
                py.setKeyframe(v, t=index)
            
            if(time > 1):
                v.setPosition(original)
                py.setKeyframe(v, t=index+time)
            
            index += 1


def text(t = "foo", font="Droid Sans", hipoly = False, cleanup = True):
    #note: hipoly mode seems to generate a couple weird extra vertices in the final output.
    obj1 = mc.textCurves( f=font,t=t)
    obj2 = mc.planarSrf(obj1)
    if hipoly:
        obj3 = nurbsToPoly()
    else:
        obj3 = mel.eval("nurbsToPoly -mnd 1  -ch 1 -f 1 -pt 1 -pc 500 -chr 0.9 -ft 0.7787 -mel 1 -d 0.196 -ut 1 -un 3 -vt 1 -vn 3 -uch 0 -ucr 0 -cht 0.01 -es 0 -ntr 0 -mrt 0 -uss 1 \"" + obj2[0] + "\";")
    if cleanup:
        d([obj1,obj2])
        mc.xform(obj3[0], cp=True)
    return obj3

def puppetMesh(target=None):
    returns = []
    
    if not target:
        target = mc.ls(sl=1)
    
    for i in range(0,len(target)):    
        obj = mel.eval("planarSrf -ch 1 -d 3 -ko 0 -tol 0 -rn 0 -po 1 \""+target[i]+"\";")
        #delete history, recenter the pivot
        mc.delete(ch=True)
        mc.xform(cp=True)
 
        returns.append(obj)
        
    return returns

def iteratePolyToSubdiv(target=None,polys=1000,reps=1000,delete=False):
    
    counter = 0
    initPolyCount = polys
    currentPolyCount = initPolyCount
    finished = False
    
    if not target:
        target = mc.ls(sl=1)

    for i in range(0,len(target)):
            while(finished==False and counter < reps):
                try:
                    finished=True
                    mc.polyToSubdiv(target[i], maxPolyCount=currentPolyCount)

                except:
                    finished=False
                    counter+=1
                    currentPolyCount += initPolyCount
                    print "Failed using " + str(currentPolyCount - initPolyCount) + " polys; trying " + str(currentPolyCount) + " polys."
            if(finished==True):
                if(delete==True):
                    mc.delete(constructionHistory=True) # prevents deletion of polys from wrecking subdivs
                    mc.delete(target[i])
                print "Successfully converted " + str(target[i]) + " using < " + str(currentPolyCount) + " polys in " + str(counter+1) + " tries."
            else:
                print "Failed to convert " + str(target[i]) + " using < " + str(currentPolyCount) + " polys in " + str(counter+1) + " tries."


def booleanLoop(legacy=False):
    #1. Make an array of all selections
    target = mc.ls(sl=1)

    if (legacy):
        #2. Boolean union each item in the array to the next
        for i in range(0,len(target)-1,2):
            mc.polyBoolOp(target[i],target[i+1])
            
            #3. Delete construction history
            mc.delete(ch=True)

            #4. Recenter the pivot
            mc.xform(cp=True)
    else:
        mc.polyCBoolOp()
        mc.delete(ch=True)

def cubes(num=100,spread=5):
    val = []
    for i in range(0, num):
        obj = mc.polyCube()
        val.append(obj)
        k()
        t(48)
        rndMove(spread)
        k()
        t(0)
    return val

def curveAB(target=None, type="line", fill=False):
    returns = []
    if not target:
        target = s()

    p = getPos(target)

    for i in range(0,len(target)):
        if(type=="line"):
            if(i<len(target)-1):
                ctl = makeLine(p[i],p[i+1])
        elif(type=="star"):
            if(i<len(target)-1):
                ctl = makeLine(p[i],p[len(target)-1])
        elif(type=="circle"):
            if(i<len(target)-1):
                ctl = makeLine(p[i],p[i+1])
            else:
                ctl = makeLine(p[i],p[0])
        if(fill==True):
            ctl2 = curveSurface()
            d(ctl)
            returns.append(ctl2)
        else:
            returns.append(ctl)

    return returns

def curveSurface():
    returns = []
    target = s()
    
    for i in range(0,len(target)):
        ctl = py.revolve(target[i], ch=1, po=1, rn=1, ssw=0, esw=3, ut=1, tol=0, degree=3, s=8, ulp=1, ax=(1,0,0))
        returns.append(ctl)

    return returns

def makeLine(p1=[-2,0,0], p2=[2,0,0], name="curve"):
    name = getUniqueName(name)
    ctl = mc.curve(n=name, d=1, p=(p1,p2), k=(0,1))
    return ctl

def drawPoints(points=None, name="curve", uniqueName=True):
    if (uniqueName==True):
        name = getUniqueName(name)
    crv = mc.curve(n=name, d=1, p=points)
    return crv
    
def smoothMesh(target=None):
    if not target:
        target = s()
    
    polysOnly = py.filterExpand(target, sm=12)
    py.select(polysOnly, r=True)

    for i in range(0,len(target)):
        try:
            py.mel.eval("polySmooth -mth 0 -dv 1 -bnr 2 -c 1 -kb 1 -ksb 1 -khe 0 -kt 1 -kmb 1 -suv 0 -peh 0 -sl 1 -dpe 1 -ps 0.1 -ro 1 -ch 1 " + target[i] + ";")    
            py.mel.eval("BakeAllNonDefHistory;")
            py.mel.eval("bakePartialHistory -all;")
        except:
            print "Smooth failed; " + target[i] + " probably isn't a polygonal mesh."

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# PAINT EFFECTS

# test
def lightningStar(target=None):
    if not target:
        target = mc.ls(sl=1)
    
    for i in range(0,len(target)-1):
        mc.select(target[i],target[len(target)-1])
        mel.eval("lightning \"\" 0 1 20 0.1 1 0 1 0.3;")        

def paintCurve(target=None, brush=None, bake=True, reducePolys=0.1, maxPolys=0):
    returns = []
    if not target:
        target = s()

    paintBrushSelector(brush)

    for i in range(0,len(target)):
        oldObjects = getAllObjects()
        s(target[i])
        mel.eval("AttachBrushToCurves;")
        crv = getNewObjects(oldObjects)[1]
        #crv.setAttr("sampleDensity", reducePolys)
        if (bake==True):
            oldObjects = getAllObjects()
            s(crv)
            mel.eval("doPaintEffectsToPoly(1,1,1,1," + str(maxPolys) + ");")
            newObjects = getNewObjects(oldObjects)
            obj = newObjects[len(newObjects)-1]
            s(obj)
            ch()
            d(crv)
            #ch()
            #ch()
            #mc.polyReduce(percentage=10)
            #ch()
            returns.append(obj)
        else:
            returns.append(crv)
        d(target[i])

    print("Created " + str(returns))
    return returns

def paintSurface(target=None, brush=None, bake=True, reducePolys=0.1, maxPolys=0):
    returns = []
    deleteCurves = []
    if not target:
        target = s()

    for i in range(0,len(target)):
        s([target[i]])
        crv=curveSurface()
        returns.append(paintAssign(brush=brush))
        deleteCurves.append(crv[0][0])
        d([target[i]])

    if (bake==True):
        s(returns)
        bakePaintEffects(reducePolys=reducePolys, maxPolys=maxPolys)
        d(deleteCurves)

    return returns

def paintAssign(target=None, brush=None):
    returns = []
    if not target:
        target = s()

    paintBrushSelector(brush)

    for i in range(0,len(target)):
        oldObjects = getAllObjects()
        s(target[i])
        mel.eval("assignNewPfxToon;")
        mel.eval("assignBrushToPfxToon;")
        
        returns.append(getNewObjects(oldObjects)[1])
        
    return returns

def bakePaintEffects(target=None, reducePolys=0.1, maxPolys=0):
    if not target:
        target = s()
    mel.eval("doPaintEffectsToPoly(1,1,1,1," + str(maxPolys) + ");")
    ch()
    if (reducePolys < 1.0):
        for obj in target:
            #obj.setAttr("sampleDensity", reducePolys)
            ch()
        #mc.polyReduce(percentage=10)
        #ch()
    mc.polyQuad()
    ch()

# ~ ~ ~ ~ ~ ~

def latkToPaintEffects(inputDir=None, brush=None, bake=True, reducePolys=0.5, maxPolys=0, animateFrames=True):
    globalScale = (10,10,10)
    if not inputDir:
        inputDir=openFileDialog("json")
    with open(inputDir) as data_file:    
        data = json.load(data_file)
    #~
    for h in range(0, len(data["grease_pencil"][0]["layers"])):
        inTime(0)
        outTime(len(data["grease_pencil"][0]["layers"][h]["frames"]))
        start, end = getStartEnd()
        #~
        for i in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"])):
            strokes = []
            frameList = []
            for j in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"])):
                points = []
                for l in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"])):
                    x = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][0] * globalScale[0]
                    y = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][1] * globalScale[1]
                    z = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][2] * globalScale[2]
                    points.append((x,y,z))
                strokes.append(points)
            for stroke in strokes:
                if (len(stroke) > 1):
                    drawPoints(stroke, uniqueName=False)
                    paintStroke = paintCurve(brush=brush, bake=bake, reducePolys=reducePolys, maxPolys=maxPolys)
                    frameList.append(paintStroke)

            # TODO Fix for variable length frames, needs JSON to have frame_number field per frame.
            # TODO Add transform animation.
            if (animateFrames==True):
                if (len(frameList) > 0):
                    print("\nframeList for frame " + str(i) + " has " + str(len(frameList)) + " strokes.")
                    
                    s(frameList)
                    frameListObj = frameList[0]
                    try:
                        frameListObj = mc.polyUnite(ch=False, object=True) #name=getUniqueName("stroke"))
                    except:
                        pass
                    print(frameListObj)
                    ch()
                    for m in range(start, end):
                        if (i==m):
                            mc.setAttr(frameListObj[0] + ".v", 1, keyable=True)
                        else:
                            mc.setAttr(frameListObj[0] + ".v", 0, keyable=True)
                        mc.setKeyframe(frameListObj, time=m)

            # Old mesh show/hide method from Blender
            '''
            for i in range(0, len(frameList)):
                totalCounter += 1
                print(frameList[i].name + " | " + str(totalCounter) + " of " + totalStrokes + " total")
                if (_animateFrames==True):
                    hideFrame(frameList[i], 0, True)
                    for j in range(start, end):
                        if (j == layer.frames[c].frame_number):
                            hideFrame(frameList[i], j, False)
                            keyTransform(frameList[i], j)
                        elif (c < len(layer.frames)-1 and j > layer.frames[c].frame_number and j < layer.frames[c+1].frame_number):
                            hideFrame(frameList[i], j, False)
                        elif (c != len(layer.frames)-1):
                            hideFrame(frameList[i], j, True)
            '''
    print("*** FINISHED ***")

def latk():
    rm()
    latkToPaintEffects(inputDir="C:/Users/nick/Documents/GitHub/LightningArtist/latkUnreal/Content/Latk/layer_test.json", brush="neon")

def getQuillParentColor(target=None):
    if not target:
        target = ss()
    try:
        targetParent = None
        try:
            targetParent = py.listRelatives(parent=True)[0]
        except:
            targetParent = py.listRelatives(parent=True)
        rgba = py.getAttr(targetParent + ".rgba")
        color = (rgba[0], rgba[1], rgba[2], rgba[3])
        return color
    except:
        return (0,0,0,1)
    
def getAllQuillParentColors():
    colors = []
    curves = listAllCurves()
    for curve in curves:
        ss(curve)
        color = getQuillParentColor(curve)
        colors.append(color)
    return colors

def latkFromQuill():
    url = saveFileDialog("json")#filepath # compatibility with gui keywords

    #curves = listAllCurves()
    strokes = getAllCurveCvs()
    colors = getAllQuillParentColors()

    #if (len(curves) == len(strokes) == len(colors)):
    if (len(strokes) == len(colors)):
        pass
    else:
        print("Warning: color information doesn't match stroke information.")

    writeFilePath = "/Users/nick/Projects/LightningArtist/LightningArtistJS/animations/"
    writeFileName = "new_test.json"
    #~
    #if(bake == True):
        #bakeFrames()
    #gp = bpy.context.scene.grease_pencil
    globalScale = (-0.1, 0.1, 0.1)
    globalOffset = (0, 0, 0)
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    #palette = getActivePalette()
    #~
    sg = "{" + "\n"
    sg += "    \"creator\": \"maya\"," + "\n"
    sg += "    \"grease_pencil\": [" + "\n"
    sg += "        {" + "\n"
    sg += "            \"layers\": [" + "\n"
    sl = ""
    for f in range(0, 1):#len(gp.layers)):
        sb = ""
        #layer = gp.layers[f]
        for h in range(0, 1):#len(layer.frames)):
            #currentFrame = h
            #goToFrame(h)
            sb += "                        {" + "\n" # one frame
            sb += "                            \"strokes\": [" + "\n"
            if (len(strokes) > 0):#layer.frames[currentFrame].strokes) > 0):
                sb += "                                {" + "\n" # one stroke
                for i in range(0, len(strokes)):#layer.frames[currentFrame].strokes)):
                    color = (0,0,0)
                    try:
                        color = colors[i]#palette.colors[layer.frames[currentFrame].strokes[i].colorname].color
                    except:
                        pass
                    sb += "                                    \"color\": [" + str(color[0]) + ", " + str(color[1]) + ", " + str(color[2])+ "]," + "\n"
                    sb += "                                    \"points\": [" + "\n"
                    for j in range(0, len(strokes[i])):#layer.frames[currentFrame].strokes[i].points)):
                        x = 0.0
                        y = 0.0
                        z = 0.0
                        pressure = 1.0
                        strength = 1.0
                        #.
                        print(strokes[i][j])
                        point = strokes[i][j]#layer.frames[currentFrame].strokes[i].points[j].co
                        #pressure = layer.frames[currentFrame].strokes[i].points[j].pressure
                        #strength = layer.frames[currentFrame].strokes[i].points[j].strength
                        if useScaleAndOffset == True:
                            x = (point[0] * globalScale[0]) + globalOffset[0]
                            y = (point[1] * globalScale[1]) + globalOffset[1]
                            z = (point[2] * globalScale[2]) + globalOffset[2]
                        else:
                            x = point[0]
                            y = point[1]
                            z = point[2]
                        #~
                        if roundValues == True:
                            sb += "                                        {\"co\": [" + roundVal(x, numPlaces) + ", " + roundVal(y, numPlaces) + ", " + roundVal(z, numPlaces) + "], \"pressure\": " + roundVal(pressure, numPlaces) + ", \"strength\": " + roundVal(strength, numPlaces)
                        else:
                            sb += "                                        {\"co\": [" + str(x) + ", " + str(y) + ", " + str(z) + "], \"pressure\": " + pressure + ", \"strength\": " + strength                  
                        #~
                        if (j == len(strokes[i])-1):#layer.frames[currentFrame].strokes[i].points) - 1:
                            sb += "}" + "\n"
                            sb += "                                    ]" + "\n"
                            if (i == len(strokes) - 1):
                                sb += "                                }" + "\n" # last stroke for this frame
                            else:
                                sb += "                                }," + "\n" # end stroke
                                sb += "                                {" + "\n" # begin stroke
                        else:
                            sb += "}," + "\n"
                    if i == len(strokes) - 1:
                        sb += "                            ]" + "\n"
            else:
                sb += "                            ]" + "\n"
            if (h == 0):
                sb += "                        }" + "\n"
            else:
                sb += "                        }," + "\n"
        #~
        sf = "                {" + "\n" 
        sf += "                    \"name\": \"" + "maya_layer1" + "\"," + "\n"
        sf += "                    \"frames\": [" + "\n" + sb + "                    ]" + "\n"
        if (f == 0):
            sf += "                }" + "\n"
        else:
            sf += "                }," + "\n"
        sl += sf
        #~
    sg += sl
    sg += "            ]" + "\n"
    sg += "        }"+ "\n"
    sg += "    ]"+ "\n"
    sg += "}"+ "\n"
    if (url==None):
        url = writeFilePath + writeFileName
    #~
    with open(url, "w") as f:
        f.write(sg)
        f.closed
    print("Wrote " + url)

def hideFrame(target=None, _frame=0, _hide=True):
    if not target:
        target = s()
    for i in range (0, len(target)):
        if (_hide==True):
            mc.setAttr(target[i][0] + ".v", 0)
        else:
            mc.setAttr(target[i][0] + ".v", 1)
        try:
            k()
        except:
            pass
    try:
        k()
    except:
        pass

def gmlToPaintEffects(inputDir=None, brush=None, bake=True, reducePolys=0.1, maxPolys=0):
    if not inputDir:
        inputDir=openFileDialog("gml")
    paintCurves = []
    tree = etree.parse(inputDir)
    root = tree.getroot()
    '''
    if (root.tag.lower() != "gml"):
        print("Not a GML file.")
        return
    '''
    #~
    tag = root.find("tag")
    header = tag.find("header")
    drawing = tag.find("drawing")
    environment = header.find("environment")
    if not environment:
        environment = tag.find("environment")
    screenBounds = environment.find("screenBounds")
    globalScale = (0.01,0.01,0.01)
    dim = (float(screenBounds.find("x").text) * globalScale[0], float(screenBounds.find("y").text) * globalScale[1], float(screenBounds.find("z").text) * globalScale[2])
    #~
    strokes = drawing.findall("stroke")
    for stroke in strokes:
        points = []
        pointsEl = stroke.findall("pt")
        for pointEl in pointsEl:
            x = float(pointEl.find("x").text) * dim[0] 
            y = float(pointEl.find("y").text) * dim[1]
            z = float(pointEl.find("z").text) * dim[2]
            point = (x, y, z)
            points.append(point)
        crv = drawPoints(points)
        paintCurves.append(crv)
    s(d=True)
    newCurves = paintCurve(paintCurves, brush, bake, reducePolys, maxPolys)

# ~ ~ ~ BRUSHES ~ ~ ~

def paintBrushSelector(brush=None):
    if (brush=="fire"):
        brushFlameCurly()
    elif (brush=="oil"):
        brushThickOilRed()
    elif (brush=="neon"):
        brushNeonBlue()
    else:
        brushDefault()

def brushDefault():
    mel.eval("brushPresetSetup();bPset \"time\" 1; bPset \"globalScale\" 1; bPset \"depth\" 0; bPset \"modifyDepth\" 1; bPset \"modifyColor\" 1; bPset \"modifyAlpha\" 1; bPset \"illuminated\" 0; bPset \"castShadows\" 0; bPset \"branches\" 0; bPset \"twigs\" 0; bPset \"buds\" 0; bPset \"leaves\" 0; bPset \"flowers\" 0; bPset \"brushType\" 0; bPset \"brushWidth\" 0.05000000075; bPset \"screenspaceWidth\" 0; bPset \"stampDensity\" 8; bPset \"softness\" 0.5; bPset \"edgeAntialias\" 1; bPset \"blurIntensity\" 4; bPset \"color1R\" 0; bPset \"color1G\" 0; bPset \"color1B\" 0; bPset \"color2R\" 1; bPset \"color2G\" 1; bPset \"color2B\" 1; bPset \"transparency1R\" 0; bPset \"transparency1G\" 0; bPset \"transparency1B\" 0; bPset \"transparency2R\" 0; bPset \"transparency2G\" 0; bPset \"transparency2B\" 0; bPset \"incandescence1R\" 0; bPset \"incandescence1G\" 0; bPset \"incandescence1B\" 0; bPset \"incandescence2R\" 0; bPset \"incandescence2G\" 0; bPset \"incandescence2B\" 0; bPset \"specularColorR\" 1; bPset \"specularColorG\" 1; bPset \"specularColorB\" 1; bPset \"specular\" 0; bPset \"specularPower\" 10; bPset \"translucence\" 0.2; bPset \"glow\" 0; bPset \"glowColorR\" 0.5; bPset \"glowColorG\" 0.5; bPset \"glowColorB\" 0.5; bPset \"glowSpread\" 3; bPset \"shaderGlow\" 0; bPset \"hueRand\" 0; bPset \"satRand\" 0; bPset \"valRand\" 0; bPset \"rootFade\" 0; bPset \"tipFade\" 0; bPset \"fakeShadow\" 0; bPset \"shadowOffset\" 0.5; bPset \"shadowDiffusion\" 0.1; bPset \"shadowTransparency\" 0.8; bPset \"backShadow\" 0; bPset \"brightnessRand\" 0; bPset \"centerShadow\" 0; bPset \"depthShadowType\" 0; bPset \"depthShadow\" 0; bPset \"depthShadowDepth\" 0; bPset \"realLights\" 0; bPset \"lightDirectionX\" 0.5; bPset \"lightDirectionY\" 0.5; bPset \"lightDirectionZ\" -0.5; bPset \"gapSize\" 0; bPset \"gapSpacing\" 1; bPset \"gapRand\" 0; bPset \"flowSpeed\" 0; bPset \"timeClip\" 0; bPset \"strokeTime\" 0; bPset \"startTime\" 0; bPset \"endTime\" 1000; bPset \"tubes\" 0; bPset \"tubeCompletion\" 1; bPset \"tubesPerStep\" 0.5; bPset \"tubeRand\" 1; bPset \"startTubes\" 0; bPset \"lengthMax\" 1; bPset \"lengthMin\" 0; bPset \"segments\" 10; bPset \"tubeWidth1\" 0.01; bPset \"tubeWidth2\" 0.01; bPset \"widthRand\" 0; bPset \"widthBias\" 0; bPset \"lengthFlex\" 0; bPset \"segmentLengthBias\" 0; bPset \"segmentWidthBias\" 0; bPset \"tubeDirection\" 0; bPset \"elevationMin\" 0.2; bPset \"elevationMax\" 0.5; bPset \"azimuthMin\" -0.1; bPset \"azimuthMax\" 0.1; bPset \"flatness1\" 0; bPset \"flatness2\" 0; bPset \"twist\" 0; bPset \"twistRate\" 0; bPset \"twistRand\" 1; bPset \"spiralMin\" 0; bPset \"spiralMax\" 0; bPset \"spiralDecay\" 0; bPset \"displacementDelay\" 0.2; bPset \"wiggle\" 0; bPset \"wiggleFrequency\" 3; bPset \"wiggleOffset\" 0; bPset \"curl\" 0; bPset \"curlFrequency\" 1; bPset \"curlOffset\" 0; bPset \"noise\" 0; bPset \"noiseFrequency\" 0.2; bPset \"noiseOffset\" 0; bPset \"splitMaxDepth\" 2; bPset \"splitRand\" 0; bPset \"splitAngle\" 30; bPset \"splitSizeDecay\" 0.7; bPset \"splitBias\" 0; bPset \"splitTwist\" 0.5; bPset \"startBranches\" 0; bPset \"numBranches\" 2; bPset \"branchDropout\" 0; bPset \"middleBranch\" 0; bPset \"minSize\" 0.0001; bPset \"pathFollow\" 0; bPset \"pathAttract\" 0; bPset \"curveFollow\" 0; bPset \"curveAttract\" 0; bPset \"curveMaxDist\" 0; bPset \"uniformForceX\" 0; bPset \"uniformForceY\" 0; bPset \"uniformForceZ\" 0; bPset \"turbulenceType\" 0; bPset \"turbulenceInterpolation\" 0; bPset \"turbulence\" 0.2; bPset \"turbulenceFrequency\" 0.2; bPset \"turbulenceSpeed\" 0.5; bPset \"turbulenceOffsetX\" 0; bPset \"turbulenceOffsetY\" 0; bPset \"turbulenceOffsetZ\" 0; bPset \"random\" 0; bPset \"gravity\" 0; bPset \"momentum\" 1; bPset \"deflection\" 0; bPset \"deflectionMin\" 0; bPset \"deflectionMax\" 0.3; bPset \"twigsInCluster\" 1; bPset \"twigDropout\" 0; bPset \"twigAngle1\" 90; bPset \"twigAngle2\" 80; bPset \"twigTwist\" 0; bPset \"twigLength\" 0.5; bPset \"twigStart\" 0.5; bPset \"numTwigClusters\" 4; bPset \"twigBaseWidth\" 0.4; bPset \"twigTipWidth\" 0.2; bPset \"leavesInCluster\" 1; bPset \"leafDropout\" 0; bPset \"leafAngle1\" 75; bPset \"leafAngle2\" 25; bPset \"leafTwist\" 0; bPset \"leafSegments\" 5; bPset \"leafStart\" 0.5; bPset \"numLeafClusters\" 3; bPset \"leafFlatness\" 1; bPset \"leafLength\" 0.3; bPset \"leafBaseWidth\" 0.15; bPset \"leafTipWidth\" 0.05; bPset \"leafSizeDecay\" 0.7; bPset \"leafTranslucence\" 0.7; bPset \"terminalLeaf\" 0; bPset \"leafColor1R\" 0.200000003; bPset \"leafColor1G\" 0.6000000238; bPset \"leafColor1B\" 0.3000000119; bPset \"leafColor2R\" 0.400000006; bPset \"leafColor2G\" 0.6000000238; bPset \"leafColor2B\" 0.3000000119; bPset \"leafHueRand\" 0; bPset \"leafSatRand\" 0; bPset \"leafValRand\" 0; bPset \"leafUseBranchTex\" 1; bPset \"budSize\" 0.03; bPset \"budColorR\" 0.400000006; bPset \"budColorG\" 0.8000000119; bPset \"budColorB\" 0.200000003; bPset \"petalsInFlower\" 1; bPset \"petalDropout\" 0; bPset \"flowerAngle1\" 75; bPset \"flowerAngle2\" 25; bPset \"flowerTwist\" 0.23; bPset \"petalSegments\" 5; bPset \"flowerStart\" 1; bPset \"numFlowers\" 10; bPset \"petalFlatness\" 1; bPset \"petalLength\" 0.2; bPset \"petalBaseWidth\" 0.05; bPset \"petalTipWidth\" 0.1; bPset \"flowerSizeDecay\" 0.7; bPset \"flowerTranslucence\" 0.7; bPset \"petalColor1R\" 0.8000000119; bPset \"petalColor1G\" 0.200000003; bPset \"petalColor1B\" 0.1000000015; bPset \"petalColor2R\" 1; bPset \"petalColor2G\" 1; bPset \"petalColor2B\" 1; bPset \"flowerHueRand\" 0; bPset \"flowerSatRand\" 0; bPset \"flowerValRand\" 0; bPset \"flowerUseBranchTex\" 1; bPset \"simplifyMethod\" 2; bPset \"colorLengthMap\" 0; bPset \"transpLengthMap\" 0; bPset \"incandLengthMap\" 0; bPset \"widthLengthMap\" 0; bPset \"splitLengthMap\" 0; bPset \"mapColor\" 0; bPset \"mapOpacity\" 0; bPset \"textureType\" 0; bPset \"mapMethod\" 2; bPset \"texColorScale\" 1; bPset \"texColorOffset\" 0; bPset \"texOpacityScale\" 1; bPset \"texOpacityOffset\" 0; bPset \"texColor1R\" 1; bPset \"texColor1G\" 1; bPset \"texColor1B\" 1; bPset \"texColor2R\" 0; bPset \"texColor2G\" 0; bPset \"texColor2B\" 0; bPset \"texAlpha1\" 1; bPset \"texAlpha2\" 0; bPset \"texUniformity\" 0.5; bPset \"fringeRemoval\" 1; bPset \"repeatU\" 1; bPset \"repeatV\" 1; bPset \"offsetU\" 0; bPset \"offsetV\" 0; bPset \"blurMult\" 1; bPset \"smear\" 0.1; bPset \"smearU\" 0; bPset \"smearV\" 0; bPset \"useFrameExtension\" 0; bPset \"frameExtension\" 1; bPset \"fractalRatio\" 0.7; bPset \"fractalAmplitude\" 1; bPset \"fractalThreshold\" 0; ")
    mel.eval("bPsetName \"imageName\" \"\";")
    mel.eval("bPsetName \"leafImage\" \"\";")
    mel.eval("bPsetName \"flowerImage\" \"\";")
    mel.eval("bPsetName \"creationScript\" \"\";")
    mel.eval("bPsetName \"runtimeScript\" \"\";")
    mel.eval("brushPresetApply();")
    mel.eval("presetSetPressure 1 5 0 1;")
    mel.eval("presetSetPressure 2 0 0 1;")
    mel.eval("presetSetPressure 3 0 0 1;")
    mel.eval("rename (getDefaultBrush()) defaultPaint;")

def brushFlameCurly():
    mel.eval("brushPresetSetup();bPset \"time\" 1; bPset \"globalScale\" 0.7656982396; bPset \"depth\" 1; bPset \"modifyDepth\" 1; bPset \"modifyColor\" 1; bPset \"modifyAlpha\" 1; bPset \"illuminated\" 0; bPset \"castShadows\" 0; bPset \"branches\" 0; bPset \"twigs\" 0; bPset \"buds\" 0; bPset \"leaves\" 0; bPset \"flowers\" 0; bPset \"brushType\" 0; bPset \"brushWidth\" 0.04252389795; bPset \"screenspaceWidth\" 0; bPset \"stampDensity\" 3; bPset \"softness\" 0.17886; bPset \"edgeAntialias\" 1; bPset \"blurIntensity\" 4; bPset \"color1R\" 0.3098039329; bPset \"color1G\" 0.2235294133; bPset \"color1B\" 0.03921568766; bPset \"color2R\" 0.1372549087; bPset \"color2G\" 0; bPset \"color2B\" 0; bPset \"transparency1R\" 0.8666666746; bPset \"transparency1G\" 0.8666666746; bPset \"transparency1B\" 0.8666666746; bPset \"transparency2R\" 1; bPset \"transparency2G\" 1; bPset \"transparency2B\" 1; bPset \"incandescence1R\" 0.2039215714; bPset \"incandescence1G\" 0.1529411823; bPset \"incandescence1B\" 0.01568627357; bPset \"incandescence2R\" 0.1529411823; bPset \"incandescence2G\" 0.01176470611; bPset \"incandescence2B\" 0; bPset \"specularColorR\" 0; bPset \"specularColorG\" 0; bPset \"specularColorB\" 0; bPset \"specular\" 0; bPset \"specularPower\" 10; bPset \"translucence\" 0.2; bPset \"glow\" 0; bPset \"glowColorR\" 1; bPset \"glowColorG\" 0.8601613641; bPset \"glowColorB\" 0.595744729; bPset \"glowSpread\" 3.561; bPset \"shaderGlow\" 0; bPset \"hueRand\" 0.09756; bPset \"satRand\" 0.17074; bPset \"valRand\" 0.88618; bPset \"rootFade\" 0.22764; bPset \"tipFade\" 0.55284; bPset \"fakeShadow\" 0; bPset \"shadowOffset\" 0.5; bPset \"shadowDiffusion\" 0.1; bPset \"shadowTransparency\" 0.8; bPset \"backShadow\" 0; bPset \"brightnessRand\" 0; bPset \"centerShadow\" 0; bPset \"depthShadowType\" 0; bPset \"depthShadow\" 0; bPset \"depthShadowDepth\" 0; bPset \"realLights\" 0; bPset \"lightDirectionX\" 0.5; bPset \"lightDirectionY\" 0.5; bPset \"lightDirectionZ\" -0.5; bPset \"gapSize\" 0; bPset \"gapSpacing\" 1; bPset \"gapRand\" 1; bPset \"flowSpeed\" 0; bPset \"timeClip\" 0; bPset \"strokeTime\" 0; bPset \"startTime\" 0; bPset \"endTime\" 1000; bPset \"tubes\" 1; bPset \"tubeCompletion\" 1; bPset \"tubesPerStep\" 5.4369; bPset \"tubeRand\" 1; bPset \"startTubes\" 0; bPset \"lengthMax\" 0.1626; bPset \"lengthMin\" 0.1626; bPset \"segments\" 18; bPset \"tubeWidth1\" 0.027642; bPset \"tubeWidth2\" 0.007318; bPset \"widthRand\" 0.73984; bPset \"widthBias\" -0.49592; bPset \"lengthFlex\" 0.61788; bPset \"segmentLengthBias\" 0.08944; bPset \"segmentWidthBias\" 0; bPset \"tubeDirection\" 0; bPset \"elevationMin\" 0.1493599524; bPset \"elevationMax\" 0.72816; bPset \"azimuthMin\" -0.72816; bPset \"azimuthMax\" 0.96116; bPset \"flatness1\" 0; bPset \"flatness2\" 0; bPset \"twist\" 0; bPset \"twistRate\" 0; bPset \"twistRand\" 1; bPset \"spiralMin\" 0; bPset \"spiralMax\" 0; bPset \"spiralDecay\" 0; bPset \"displacementDelay\" 0.2; bPset \"wiggle\" 0; bPset \"wiggleFrequency\" 5; bPset \"wiggleOffset\" 0; bPset \"curl\" 0; bPset \"curlFrequency\" 1; bPset \"curlOffset\" 0; bPset \"noise\" 0; bPset \"noiseFrequency\" 0.2; bPset \"noiseOffset\" 0; bPset \"splitMaxDepth\" 2; bPset \"splitRand\" 0.187; bPset \"splitAngle\" 27.804; bPset \"splitSizeDecay\" 0.7; bPset \"splitBias\" 0; bPset \"splitTwist\" 0.5; bPset \"startBranches\" 0; bPset \"numBranches\" 3; bPset \"branchDropout\" 0.6504; bPset \"middleBranch\" 0; bPset \"minSize\" 0.0001; bPset \"pathFollow\" 0; bPset \"pathAttract\" 0; bPset \"curveFollow\" 0; bPset \"curveAttract\" 0; bPset \"curveMaxDist\" 0; bPset \"uniformForceX\" 0; bPset \"uniformForceY\" 0; bPset \"uniformForceZ\" 0; bPset \"turbulenceType\" 5; bPset \"turbulenceInterpolation\" 2; bPset \"turbulence\" 1; bPset \"turbulenceFrequency\" 9.1524; bPset \"turbulenceSpeed\" 0.25242; bPset \"turbulenceOffsetX\" 0; bPset \"turbulenceOffsetY\" 0; bPset \"turbulenceOffsetZ\" 0; bPset \"random\" 0; bPset \"gravity\" -0.45166; bPset \"momentum\" 0.29268; bPset \"deflection\" 0; bPset \"deflectionMin\" 0; bPset \"deflectionMax\" 0.3; bPset \"twigsInCluster\" 1; bPset \"twigDropout\" 0; bPset \"twigAngle1\" 90; bPset \"twigAngle2\" 80; bPset \"twigTwist\" 0; bPset \"twigLength\" 0.5; bPset \"twigStart\" 0.5; bPset \"numTwigClusters\" 4; bPset \"twigBaseWidth\" 0.4; bPset \"twigTipWidth\" 0.2; bPset \"leavesInCluster\" 1; bPset \"leafDropout\" 0; bPset \"leafAngle1\" 75; bPset \"leafAngle2\" 25; bPset \"leafTwist\" 0; bPset \"leafSegments\" 5; bPset \"leafStart\" 0.5; bPset \"numLeafClusters\" 3; bPset \"leafFlatness\" 1; bPset \"leafLength\" 0.3; bPset \"leafBaseWidth\" 0.15; bPset \"leafTipWidth\" 0.05; bPset \"leafSizeDecay\" 0.7; bPset \"leafTranslucence\" 0.7; bPset \"terminalLeaf\" 0; bPset \"leafColor1R\" 0.200000003; bPset \"leafColor1G\" 0.6000000238; bPset \"leafColor1B\" 0.3000000119; bPset \"leafColor2R\" 0.400000006; bPset \"leafColor2G\" 0.6000000238; bPset \"leafColor2B\" 0.3000000119; bPset \"leafHueRand\" 0; bPset \"leafSatRand\" 0; bPset \"leafValRand\" 0; bPset \"leafUseBranchTex\" 1; bPset \"budSize\" 0.03; bPset \"budColorR\" 0.400000006; bPset \"budColorG\" 0.8000000119; bPset \"budColorB\" 0.200000003; bPset \"petalsInFlower\" 1; bPset \"petalDropout\" 0; bPset \"flowerAngle1\" 75; bPset \"flowerAngle2\" 25; bPset \"flowerTwist\" 0.23; bPset \"petalSegments\" 5; bPset \"flowerStart\" 1; bPset \"numFlowers\" 10; bPset \"petalFlatness\" 1; bPset \"petalLength\" 0.2; bPset \"petalBaseWidth\" 0.05; bPset \"petalTipWidth\" 0.1; bPset \"flowerSizeDecay\" 0.7; bPset \"flowerTranslucence\" 0.7; bPset \"petalColor1R\" 0.8000000119; bPset \"petalColor1G\" 0.200000003; bPset \"petalColor1B\" 0.1000000015; bPset \"petalColor2R\" 1; bPset \"petalColor2G\" 1; bPset \"petalColor2B\" 1; bPset \"flowerHueRand\" 0; bPset \"flowerSatRand\" 0; bPset \"flowerValRand\" 0; bPset \"flowerUseBranchTex\" 1; bPset \"simplifyMethod\" 0; bPset \"colorLengthMap\" 0; bPset \"transpLengthMap\" 0; bPset \"incandLengthMap\" 0; bPset \"widthLengthMap\" 0; bPset \"splitLengthMap\" 0; bPset \"mapColor\" 0; bPset \"mapOpacity\" 0; bPset \"textureType\" 0; bPset \"mapMethod\" 2; bPset \"texColorScale\" 1; bPset \"texColorOffset\" 0; bPset \"texOpacityScale\" 1; bPset \"texOpacityOffset\" 0; bPset \"texColor1R\" 1; bPset \"texColor1G\" 1; bPset \"texColor1B\" 1; bPset \"texColor2R\" 0; bPset \"texColor2G\" 0; bPset \"texColor2B\" 0; bPset \"texAlpha1\" 0; bPset \"texAlpha2\" 1; bPset \"texUniformity\" 0.5; bPset \"fringeRemoval\" 0; bPset \"repeatU\" 1; bPset \"repeatV\" 1; bPset \"offsetU\" 0; bPset \"offsetV\" 0; bPset \"blurMult\" 1; bPset \"smear\" 0.1; bPset \"smearU\" 0; bPset \"smearV\" 0; bPset \"useFrameExtension\" 0; bPset \"frameExtension\" 1; bPset \"fractalRatio\" 0.7; bPset \"fractalAmplitude\" 1; bPset \"fractalThreshold\" 0; ")
    mel.eval("bPsetName \"imageName\" \"\";")
    mel.eval("bPsetName \"leafImage\" \"\";")
    mel.eval("bPsetName \"flowerImage\" \"\";")
    mel.eval("bPsetName \"creationScript\" \"\";")
    mel.eval("bPsetName \"runtimeScript\" \"\";")
    mel.eval("brushPresetApply();")
    mel.eval("presetSetPressure 1 8 0.1057000011 0.9430999756;")
    mel.eval("presetSetPressure 2 7 0.5 2.5;")
    mel.eval("presetSetPressure 3 5 0.1463000029 1;")
    mel.eval("rename (getDefaultBrush()) flameCurly;")

def brushThickOilRed():
    mel.eval("brushPresetSetup();bPset \"time\" 1; bPset \"globalScale\" 1; bPset \"depth\" 0; bPset \"modifyDepth\" 1; bPset \"modifyColor\" 1; bPset \"modifyAlpha\" 1; bPset \"illuminated\" 1; bPset \"castShadows\" 0; bPset \"branches\" 0; bPset \"twigs\" 0; bPset \"buds\" 0; bPset \"leaves\" 0; bPset \"flowers\" 0; bPset \"brushType\" 0; bPset \"brushWidth\" 0.016264; bPset \"screenspaceWidth\" 0; bPset \"stampDensity\" 3; bPset \"softness\" 0.21138; bPset \"edgeAntialias\" 1; bPset \"blurIntensity\" 4; bPset \"color1R\" 1; bPset \"color1G\" 0; bPset \"color1B\" 0; bPset \"color2R\" 1; bPset \"color2G\" 0; bPset \"color2B\" 0; bPset \"transparency1R\" 0.6235294342; bPset \"transparency1G\" 0.5529412031; bPset \"transparency1B\" 0.5529412031; bPset \"transparency2R\" 0; bPset \"transparency2G\" 0; bPset \"transparency2B\" 0; bPset \"incandescence1R\" 0; bPset \"incandescence1G\" 0; bPset \"incandescence1B\" 0; bPset \"incandescence2R\" 0; bPset \"incandescence2G\" 0; bPset \"incandescence2B\" 0; bPset \"specularColorR\" 0.9764705896; bPset \"specularColorG\" 0.9764705896; bPset \"specularColorB\" 0.9764705896; bPset \"specular\" 0; bPset \"specularPower\" 18.8616; bPset \"translucence\" 0.5122; bPset \"glow\" 0; bPset \"glowColorR\" 1; bPset \"glowColorG\" 1; bPset \"glowColorB\" 1; bPset \"glowSpread\" 1; bPset \"shaderGlow\" 0; bPset \"hueRand\" 0.01626; bPset \"satRand\" 0.05692; bPset \"valRand\" 0.03252; bPset \"rootFade\" 0.20326; bPset \"tipFade\" 0.14634; bPset \"fakeShadow\" 0; bPset \"shadowOffset\" 0.5; bPset \"shadowDiffusion\" 0.1; bPset \"shadowTransparency\" 0.8; bPset \"backShadow\" 0; bPset \"brightnessRand\" 0.0244; bPset \"centerShadow\" 0; bPset \"depthShadowType\" 0; bPset \"depthShadow\" 0; bPset \"depthShadowDepth\" 0; bPset \"realLights\" 0; bPset \"lightDirectionX\" 0.400000006; bPset \"lightDirectionY\" -0.200000003; bPset \"lightDirectionZ\" -0.6000000238; bPset \"gapSize\" 0; bPset \"gapSpacing\" 1; bPset \"gapRand\" 1; bPset \"flowSpeed\" 0; bPset \"timeClip\" 0; bPset \"strokeTime\" 0; bPset \"startTime\" 0; bPset \"endTime\" 1000; bPset \"tubes\" 1; bPset \"tubeCompletion\" 0; bPset \"tubesPerStep\" 6.2602; bPset \"tubeRand\" 0; bPset \"startTubes\" 0; bPset \"lengthMax\" 0.1199999973; bPset \"lengthMin\" 0.009999999776; bPset \"segments\" 23; bPset \"tubeWidth1\" 0.004066; bPset \"tubeWidth2\" 0.005692; bPset \"widthRand\" 0.43902; bPset \"widthBias\" -0.38212; bPset \"lengthFlex\" 1; bPset \"segmentLengthBias\" 0; bPset \"segmentWidthBias\" 0; bPset \"tubeDirection\" 0; bPset \"elevationMin\" 0.2; bPset \"elevationMax\" 0.5; bPset \"azimuthMin\" -0.1; bPset \"azimuthMax\" 0.1; bPset \"flatness1\" 0; bPset \"flatness2\" 0; bPset \"twist\" 0; bPset \"twistRate\" 0; bPset \"twistRand\" 1; bPset \"spiralMin\" 0; bPset \"spiralMax\" 0; bPset \"spiralDecay\" 0; bPset \"displacementDelay\" 0.2; bPset \"wiggle\" 0; bPset \"wiggleFrequency\" 5; bPset \"wiggleOffset\" 0; bPset \"curl\" 0; bPset \"curlFrequency\" 1; bPset \"curlOffset\" 0; bPset \"noise\" 0; bPset \"noiseFrequency\" 0.2; bPset \"noiseOffset\" 0; bPset \"splitMaxDepth\" 2; bPset \"splitRand\" 0; bPset \"splitAngle\" 30; bPset \"splitSizeDecay\" 0.7; bPset \"splitBias\" 0; bPset \"splitTwist\" 0.5; bPset \"startBranches\" 0; bPset \"numBranches\" 2; bPset \"branchDropout\" 0; bPset \"middleBranch\" 0; bPset \"minSize\" 0.0001; bPset \"pathFollow\" 1; bPset \"pathAttract\" 0; bPset \"curveFollow\" 0; bPset \"curveAttract\" 0; bPset \"curveMaxDist\" 0; bPset \"uniformForceX\" 0; bPset \"uniformForceY\" 0; bPset \"uniformForceZ\" 0; bPset \"turbulenceType\" 0; bPset \"turbulenceInterpolation\" 0; bPset \"turbulence\" 0.2; bPset \"turbulenceFrequency\" 0.2; bPset \"turbulenceSpeed\" 0.5; bPset \"turbulenceOffsetX\" 0; bPset \"turbulenceOffsetY\" 0; bPset \"turbulenceOffsetZ\" 0; bPset \"random\" 0; bPset \"gravity\" 0; bPset \"momentum\" 0.03252; bPset \"deflection\" 0; bPset \"deflectionMin\" 0; bPset \"deflectionMax\" 0.3; bPset \"twigsInCluster\" 1; bPset \"twigDropout\" 0; bPset \"twigAngle1\" 90; bPset \"twigAngle2\" 80; bPset \"twigTwist\" 0; bPset \"twigLength\" 0.5; bPset \"twigStart\" 0.5; bPset \"numTwigClusters\" 4; bPset \"twigBaseWidth\" 0.4; bPset \"twigTipWidth\" 0.2; bPset \"leavesInCluster\" 1; bPset \"leafDropout\" 0; bPset \"leafAngle1\" 75; bPset \"leafAngle2\" 25; bPset \"leafTwist\" 0; bPset \"leafSegments\" 5; bPset \"leafStart\" 0.5; bPset \"numLeafClusters\" 3; bPset \"leafFlatness\" 1; bPset \"leafLength\" 0.3; bPset \"leafBaseWidth\" 0.15; bPset \"leafTipWidth\" 0.05; bPset \"leafSizeDecay\" 0.7; bPset \"leafTranslucence\" 0.3; bPset \"terminalLeaf\" 0; bPset \"leafColor1R\" 0.200000003; bPset \"leafColor1G\" 0.6000000238; bPset \"leafColor1B\" 0.3000000119; bPset \"leafColor2R\" 0.400000006; bPset \"leafColor2G\" 0.6000000238; bPset \"leafColor2B\" 0.3000000119; bPset \"leafHueRand\" 0; bPset \"leafSatRand\" 0; bPset \"leafValRand\" 0; bPset \"leafUseBranchTex\" 1; bPset \"budSize\" 0.03; bPset \"budColorR\" 0.400000006; bPset \"budColorG\" 0.8000000119; bPset \"budColorB\" 0.200000003; bPset \"petalsInFlower\" 1; bPset \"petalDropout\" 0; bPset \"flowerAngle1\" 75; bPset \"flowerAngle2\" 25; bPset \"flowerTwist\" 0.23; bPset \"petalSegments\" 5; bPset \"flowerStart\" 1; bPset \"numFlowers\" 10; bPset \"petalFlatness\" 1; bPset \"petalLength\" 0.2; bPset \"petalBaseWidth\" 0.05; bPset \"petalTipWidth\" 0.1; bPset \"flowerSizeDecay\" 0.7; bPset \"flowerTranslucence\" 0.3; bPset \"petalColor1R\" 0.8000000119; bPset \"petalColor1G\" 0.200000003; bPset \"petalColor1B\" 0.1000000015; bPset \"petalColor2R\" 1; bPset \"petalColor2G\" 1; bPset \"petalColor2B\" 1; bPset \"flowerHueRand\" 0; bPset \"flowerSatRand\" 0; bPset \"flowerValRand\" 0; bPset \"flowerUseBranchTex\" 1; bPset \"simplifyMethod\" 2; bPset \"colorLengthMap\" 0; bPset \"transpLengthMap\" 0; bPset \"incandLengthMap\" 0; bPset \"widthLengthMap\" 0; bPset \"splitLengthMap\" 0; bPset \"mapColor\" 0; bPset \"mapOpacity\" 0; bPset \"textureType\" 3; bPset \"mapMethod\" 2; bPset \"texColorScale\" 1; bPset \"texColorOffset\" 0; bPset \"texOpacityScale\" 1; bPset \"texOpacityOffset\" 0; bPset \"texColor1R\" 1; bPset \"texColor1G\" 0.991538465; bPset \"texColor1B\" 0.8821457028; bPset \"texColor2R\" 0.8823529482; bPset \"texColor2G\" 0.8666666746; bPset \"texColor2B\" 1; bPset \"texAlpha1\" 1; bPset \"texAlpha2\" 0; bPset \"texUniformity\" 1; bPset \"fringeRemoval\" 0; bPset \"repeatU\" 0.02999999933; bPset \"repeatV\" 0.3000000119; bPset \"offsetU\" 0; bPset \"offsetV\" 0; bPset \"blurMult\" 0.39024; bPset \"smear\" 0.82114; bPset \"smearU\" 0; bPset \"smearV\" 0; bPset \"useFrameExtension\" 0; bPset \"frameExtension\" 1; bPset \"fractalRatio\" 0.8374; bPset \"fractalAmplitude\" 0.9187; bPset \"fractalThreshold\" 0.21952;") 
    mel.eval("bPsetName \"imageName\" \"\";")
    mel.eval("bPsetName \"leafImage\" \"leaftex\";")
    mel.eval("bPsetName \"flowerImage\" \"\";")
    mel.eval("bPsetName \"creationScript\" \"\";")
    mel.eval("bPsetName \"runtimeScript\" \"\";")
    mel.eval("brushPresetApply();")
    mel.eval("presetSetPressure 1 1 0.7073000073 1.5;") 
    mel.eval("presetSetPressure 2 5 0 1;")
    mel.eval("presetSetPressure 3 3 0 1;")
    mel.eval("rename (getDefaultBrush()) thickOilRed;")

def brushNeonBlue():
    mel.eval("brushPresetSetup();bPset \"time\" 1; bPset \"globalScale\" 0.4447684171; bPset \"depth\" 1; bPset \"modifyDepth\" 1; bPset \"modifyColor\" 1; bPset \"modifyAlpha\" 1; bPset \"illuminated\" 0; bPset \"castShadows\" 0; bPset \"branches\" 0; bPset \"twigs\" 0; bPset \"buds\" 0; bPset \"leaves\" 0; bPset \"flowers\" 0; bPset \"brushType\" 0; bPset \"brushWidth\" 0.03500000015; bPset \"screenspaceWidth\" 0; bPset \"stampDensity\" 5.8256; bPset \"softness\" -0.16504; bPset \"edgeAntialias\" 1; bPset \"blurIntensity\" 4; bPset \"color1R\" 0.1450980455; bPset \"color1G\" 0.07843137532; bPset \"color1B\" 0.04705882445; bPset \"color2R\" 1; bPset \"color2G\" 1; bPset \"color2B\" 1; bPset \"transparency1R\" 0.9450980425; bPset \"transparency1G\" 0.9450980425; bPset \"transparency1B\" 0.9450980425; bPset \"transparency2R\" 0.9450980425; bPset \"transparency2G\" 0.9450980425; bPset \"transparency2B\" 0.9450980425; bPset \"incandescence1R\" 0.01568627357; bPset \"incandescence1G\" 0.1411764771; bPset \"incandescence1B\" 0.3764705956; bPset \"incandescence2R\" 0.01196968555; bPset \"incandescence2G\" 0.1077273041; bPset \"incandescence2B\" 0.2872727215; bPset \"specularColorR\" 0; bPset \"specularColorG\" 0; bPset \"specularColorB\" 0; bPset \"specular\" 0; bPset \"specularPower\" 10; bPset \"translucence\" 0.2; bPset \"glow\" 0.60976; bPset \"glowColorR\" 1; bPset \"glowColorG\" 0; bPset \"glowColorB\" 0.6735985875; bPset \"glowSpread\" 6; bPset \"shaderGlow\" 0; bPset \"hueRand\" 0; bPset \"satRand\" 0; bPset \"valRand\" 0; bPset \"rootFade\" 0; bPset \"tipFade\" 0; bPset \"fakeShadow\" 1; bPset \"shadowOffset\" 0.36586; bPset \"shadowDiffusion\" 0.47572; bPset \"shadowTransparency\" 0.13592; bPset \"backShadow\" 0; bPset \"brightnessRand\" 0; bPset \"centerShadow\" 0; bPset \"depthShadowType\" 0; bPset \"depthShadow\" 0; bPset \"depthShadowDepth\" 0; bPset \"realLights\" 0; bPset \"lightDirectionX\" 0.5; bPset \"lightDirectionY\" 0.5; bPset \"lightDirectionZ\" -0.5; bPset \"gapSize\" 0; bPset \"gapSpacing\" 1; bPset \"gapRand\" 1; bPset \"flowSpeed\" 0; bPset \"timeClip\" 0; bPset \"strokeTime\" 0; bPset \"startTime\" 0; bPset \"endTime\" 1000; bPset \"tubes\" 0; bPset \"tubeCompletion\" 0; bPset \"tubesPerStep\" 0.5; bPset \"tubeRand\" 0; bPset \"startTubes\" 0; bPset \"lengthMax\" 0.1; bPset \"lengthMin\" 0.1; bPset \"segments\" 2; bPset \"tubeWidth1\" 0.02233; bPset \"tubeWidth2\" 0.024272; bPset \"widthRand\" 0; bPset \"widthBias\" 0; bPset \"lengthFlex\" 0; bPset \"segmentLengthBias\" 0; bPset \"segmentWidthBias\" 0; bPset \"tubeDirection\" 0; bPset \"elevationMin\" 0; bPset \"elevationMax\" 0; bPset \"azimuthMin\" -0.3; bPset \"azimuthMax\" -0.3; bPset \"flatness1\" 0; bPset \"flatness2\" 0; bPset \"twist\" 0; bPset \"twistRate\" 0; bPset \"twistRand\" 1; bPset \"spiralMin\" 0; bPset \"spiralMax\" 0; bPset \"spiralDecay\" 0; bPset \"displacementDelay\" 0.2; bPset \"wiggle\" 0; bPset \"wiggleFrequency\" 5; bPset \"wiggleOffset\" 0; bPset \"curl\" 0; bPset \"curlFrequency\" 1; bPset \"curlOffset\" 0; bPset \"noise\" 0; bPset \"noiseFrequency\" 0.2; bPset \"noiseOffset\" 0; bPset \"splitMaxDepth\" 2; bPset \"splitRand\" 0; bPset \"splitAngle\" 30; bPset \"splitSizeDecay\" 0.7; bPset \"splitBias\" 0; bPset \"splitTwist\" 0.5; bPset \"startBranches\" 0; bPset \"numBranches\" 2; bPset \"branchDropout\" 0; bPset \"middleBranch\" 0; bPset \"minSize\" 0.0001; bPset \"pathFollow\" 0; bPset \"pathAttract\" 0; bPset \"curveFollow\" 0; bPset \"curveAttract\" 0; bPset \"curveMaxDist\" 0; bPset \"uniformForceX\" 0; bPset \"uniformForceY\" 0; bPset \"uniformForceZ\" 0; bPset \"turbulenceType\" 0; bPset \"turbulenceInterpolation\" 0; bPset \"turbulence\" 0.2; bPset \"turbulenceFrequency\" 0.2; bPset \"turbulenceSpeed\" 0.5; bPset \"turbulenceOffsetX\" 0; bPset \"turbulenceOffsetY\" 0; bPset \"turbulenceOffsetZ\" 0; bPset \"random\" 0; bPset \"gravity\" 0; bPset \"momentum\" 1; bPset \"deflection\" 0; bPset \"deflectionMin\" 0; bPset \"deflectionMax\" 0.3; bPset \"twigsInCluster\" 1; bPset \"twigDropout\" 0; bPset \"twigAngle1\" 90; bPset \"twigAngle2\" 80; bPset \"twigTwist\" 0; bPset \"twigLength\" 0.5; bPset \"twigStart\" 0.5; bPset \"numTwigClusters\" 4; bPset \"twigBaseWidth\" 0.4; bPset \"twigTipWidth\" 0.2; bPset \"leavesInCluster\" 1; bPset \"leafDropout\" 0; bPset \"leafAngle1\" 75; bPset \"leafAngle2\" 25; bPset \"leafTwist\" 0; bPset \"leafSegments\" 5; bPset \"leafStart\" 0.5; bPset \"numLeafClusters\" 3; bPset \"leafFlatness\" 1; bPset \"leafLength\" 0.3; bPset \"leafBaseWidth\" 0.15; bPset \"leafTipWidth\" 0.05; bPset \"leafSizeDecay\" 0.7; bPset \"leafTranslucence\" 0.3; bPset \"terminalLeaf\" 0; bPset \"leafColor1R\" 0.200000003; bPset \"leafColor1G\" 0.6000000238; bPset \"leafColor1B\" 0.3000000119; bPset \"leafColor2R\" 0.400000006; bPset \"leafColor2G\" 0.6000000238; bPset \"leafColor2B\" 0.3000000119; bPset \"leafHueRand\" 0; bPset \"leafSatRand\" 0; bPset \"leafValRand\" 0; bPset \"leafUseBranchTex\" 1; bPset \"budSize\" 0.03; bPset \"budColorR\" 0.400000006; bPset \"budColorG\" 0.8000000119; bPset \"budColorB\" 0.200000003; bPset \"petalsInFlower\" 1; bPset \"petalDropout\" 0; bPset \"flowerAngle1\" 75; bPset \"flowerAngle2\" 25; bPset \"flowerTwist\" 0.23; bPset \"petalSegments\" 5; bPset \"flowerStart\" 1; bPset \"numFlowers\" 10; bPset \"petalFlatness\" 1; bPset \"petalLength\" 0.2; bPset \"petalBaseWidth\" 0.05; bPset \"petalTipWidth\" 0.1; bPset \"flowerSizeDecay\" 0.7; bPset \"flowerTranslucence\" 0.3; bPset \"petalColor1R\" 0.8000000119; bPset \"petalColor1G\" 0.200000003; bPset \"petalColor1B\" 0.1000000015; bPset \"petalColor2R\" 1; bPset \"petalColor2G\" 1; bPset \"petalColor2B\" 1; bPset \"flowerHueRand\" 0; bPset \"flowerSatRand\" 0; bPset \"flowerValRand\" 0; bPset \"flowerUseBranchTex\" 1; bPset \"simplifyMethod\" 2; bPset \"colorLengthMap\" 0; bPset \"transpLengthMap\" 0; bPset \"incandLengthMap\" 0; bPset \"widthLengthMap\" 0; bPset \"splitLengthMap\" 0; bPset \"mapColor\" 0; bPset \"mapOpacity\" 0; bPset \"textureType\" 2; bPset \"mapMethod\" 2; bPset \"texColorScale\" 1; bPset \"texColorOffset\" 0; bPset \"texOpacityScale\" 1; bPset \"texOpacityOffset\" 0; bPset \"texColor1R\" 1; bPset \"texColor1G\" 1; bPset \"texColor1B\" 1; bPset \"texColor2R\" 0.2196078449; bPset \"texColor2G\" 0.2196078449; bPset \"texColor2B\" 0.2196078449; bPset \"texAlpha1\" 0; bPset \"texAlpha2\" 1; bPset \"texUniformity\" 0.5; bPset \"fringeRemoval\" 1; bPset \"repeatU\" 2.35776; bPset \"repeatV\" 1.86992; bPset \"offsetU\" 0; bPset \"offsetV\" 0.57724; bPset \"blurMult\" 2.5; bPset \"smear\" 0.07318; bPset \"smearU\" 0; bPset \"smearV\" 0; bPset \"useFrameExtension\" 0; bPset \"frameExtension\" 1; bPset \"fractalRatio\" 0.7; bPset \"fractalAmplitude\" 1; bPset \"fractalThreshold\" 0; ")
    mel.eval("bPsetName \"imageName\" \"\";")
    mel.eval("bPsetName \"leafImage\" \"leaftex\";")
    mel.eval("bPsetName \"flowerImage\" \"\";")
    mel.eval("bPsetName \"creationScript\" \"\";")
    mel.eval("bPsetName \"runtimeScript\" \"\";")
    mel.eval("brushPresetApply();")
    mel.eval("presetSetPressure 1 8 0 1;")
    mel.eval("presetSetPressure 2 0 0 1;")
    mel.eval("presetSetPressure 3 9 0.3007999957 1;")
    mel.eval("rename (getDefaultBrush()) neonBlue;")

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# RIGGING

# function to create a default bipedal skeleton
def createBipedSkeleton(prefix="", size=1.0, hands=False):
    joints = []

    if len(prefix) > 0:
        prefix += ("_")

    rootJnt = mc.joint(name=prefix+"root_jnt", p=(0.0*size,15.161*size,0.0*size))

    # make other joints
    #1. root to head2
    spine1Jnt = mc.joint(prefix+"root_jnt", name=prefix+"spine1_jnt", p=(0.0*size,18.161*size,-0.313*size))
    spine2Jnt = mc.joint(prefix+"spine1_jnt", name=prefix+"spine2_jnt", p=(0.0*size,21.370*size,-0.104*size))
    neckJnt = mc.joint(prefix+"spine2_jnt", name=prefix+"neck_jnt", p=(0.0*size,24.37*size,0.104*size))
    head1Jnt = mc.joint(prefix+"neck_jnt", name=prefix+"head1_jnt", p=(0.0*size,26.362*size,0.28*size))
    head2Jnt = mc.joint(prefix+"head1_jnt", name=prefix+"head2_jnt", p=(0.0*size,30.362*size,0.279*size))

    #2. root to toe_l
    hipLJnt = mc.joint(prefix+"root_jnt", name=prefix+"hip_l_jnt", p=(2.385*size,15.022*size,0.016*size))
    kneeLJnt = mc.joint(prefix+"hip_l_jnt", name=prefix+"knee_l_jnt", p=(2.385*size,8.2*size,1.561*size))
    ankleLJnt = mc.joint(prefix+"knee_l_jnt", name=prefix+"ankle_l_jnt", p=(2.385*size,1.253*size,0.0*size))
    ballLJnt = mc.joint(prefix+"ankle_l_jnt", name=prefix+"ball_l_jnt", p=(2.385*size,0.253*size,2.0*size))
    toeLJnt = mc.joint(prefix+"ball_l_jnt", name=prefix+"toe_l_jnt", p=(2.385*size,0.253*size,4.0*size))

    #3. spine2 to wrist_l
    clavicleLJnt = mc.joint(prefix+"spine2_jnt", name=prefix+"clavicle_l_jnt", p=(0.897*size,23.147*size,0.582*size))
    shoulderLJnt = mc.joint(prefix+"clavicle_l_jnt", name=prefix+"shoulder_l_jnt", p=(3.217*size,23.716*size,0.045*size))
    elbowLJnt = mc.joint(prefix+"shoulder_l_jnt", name=prefix+"elbow_l_jnt", p=(7.131*size,23.716*size,-1.239*size))
    wristLJnt = mc.joint(prefix+"elbow_l_jnt", name=prefix+"wrist_l_jnt", p=(11.204*size,23.716*size,-0.658*size))

    if (hands==True):
        #4a. wrist_l to thumb4_l
        thumb1LJnt = mc.joint(prefix+"wrist_l_jnt", name=prefix+"thumb1_l_jnt", p=(11.909*size, 23.716*size, 0.026*size))
        thumb2LJnt = mc.joint(prefix+"thumb1_l_jnt", name=prefix+"thumb2_l_jnt", p=(12.129*size, 23.402*size, 0.656*size))
        thumb3LJnt = mc.joint(prefix+"thumb2_l_jnt", name=prefix+"thumb3_l_jnt", p=(12.610*size, 23.063*size, 1.2118*size))
        thumb4LJnt = mc.joint(prefix+"thumb3_l_jnt", name=prefix+"thumb4_l_jnt", p=(13.303*size, 22.8*size, 1.477*size))

        #4b. wrist_l to index4_l
        index1LJnt = mc.joint(prefix+"wrist_l_jnt", name=prefix+"index1_l_jnt", p=(13.0421*size, 23.716*size, 0.104*size))
        index2LJnt = mc.joint(prefix+"index1_l_jnt", name=prefix+"index2_l_jnt", p=(13.957*size, 23.716*size, 0.261*size))
        index3LJnt = mc.joint(prefix+"index2_l_jnt", name=prefix+"index3_l_jnt", p=(14.915*size, 23.48*size, 0.426*size))
        index4LJnt = mc.joint(prefix+"index3_l_jnt", name=prefix+"index4_l_jnt", p=(15.79*size, 23.021*size, 0.576*size))

        #4c. wrist_l to middle4_l
        middle1LJnt = mc.joint(prefix+"wrist_l_jnt", name=prefix+"middle1_l_jnt", p=(13.052*size, 23.716*size, -0.597*size))
        middle2LJnt = mc.joint(prefix+"middle1_l_jnt", name=prefix+"middle2_l_jnt", p=(14.046*size, 23.716*size, -0.541*size))
        middle3LJnt = mc.joint(prefix+"middle2_l_jnt", name=prefix+"middle3_l_jnt", p=(15.081*size, 23.464*size, -0.484*size))
        middle4LJnt = mc.joint(prefix+"middle3_l_jnt", name=prefix+"middle4_l_jnt", p=(16.028*size, 22.974*size, -0.431*size))

        #4d. wrist_l to ring4_l
        ring1LJnt = mc.joint(prefix+"wrist_l_jnt", name=prefix+"ring1_l_jnt", p=(13.053*size, 23.716*size, -1.223*size))
        ring2LJnt = mc.joint(prefix+"ring1_l_jnt", name=prefix+"ring2_l_jnt", p=(13.995*size, 23.716*size, -1.243*size))
        ring3LJnt = mc.joint(prefix+"ring2_l_jnt", name=prefix+"ring3_l_jnt", p=(14.979*size, 23.477*size, -1.265*size))
        ring4LJnt = mc.joint(prefix+"ring3_l_jnt", name=prefix+"ring4_l_jnt", p=(15.879*size, 23.0127*size, -1.284*size))

        #4e. wrist_l to pinky4_l
        pinky1LJnt = mc.joint(prefix+"wrist_l_jnt", name=prefix+"pinky1_l_jnt", p=(13.045*size, 23.716*size, -1.886*size))
        pinky2LJnt = mc.joint(prefix+"pinky1_l_jnt", name=prefix+"pinky2_l_jnt", p=(13.891*size, 23.716*size, -2.013*size))
        pinky3LJnt = mc.joint(prefix+"pinky2_l_jnt", name=prefix+"pinky3_l_jnt", p=(14.781*size, 23.497*size, -2.147*size))
        pinky4LJnt = mc.joint(prefix+"pinky3_l_jnt", name=prefix+"pinky4_l_jnt", p=(15.595*size, 23.072*size, -2.269*size))

    #5. root to toe_r
    hipRJnt = mc.joint(prefix+"root_jnt", name=prefix+"hip_r_jnt", p=(-2.385*size,15.022*size,0.016*size))
    kneeRJnt = mc.joint(prefix+"hip_r_jnt", name=prefix+"knee_r_jnt", p=(-2.385*size,8.2*size,1.561*size))
    ankleRJnt = mc.joint(prefix+"knee_r_jnt", name=prefix+"ankle_r_jnt", p=(-2.385*size,1.253*size,0.0*size))
    ballRJnt = mc.joint(prefix+"ankle_r_jnt", name=prefix+"ball_r_jnt", p=(-2.385*size,0.253*size,2.0*size))
    toeRJnt = mc.joint(prefix+"ball_r_jnt", name=prefix+"toe_r_jnt", p=(-2.385*size,0.253*size,4.0*size))

    #6. spine2 to wrist_r
    clavicleRJnt = mc.joint(prefix+"spine2_jnt", name=prefix+"clavicle_r_jnt", p=(-0.897*size,23.147*size,0.582*size))
    shoulderRJnt = mc.joint(prefix+"clavicle_r_jnt", name=prefix+"shoulder_r_jnt", p=(-3.217*size,23.716*size,0.045*size))
    elbowRJnt = mc.joint(prefix+"shoulder_r_jnt", name=prefix+"elbow_r_jnt", p=(-7.131*size,23.716*size,-1.239*size))
    wristRJnt = mc.joint(prefix+"elbow_r_jnt", name=prefix+"wrist_r_jnt", p=(-11.204*size,23.716*size,-0.658*size))
    
    if (hands==True):
        #7a. wrist_r to thumb4_r
        thumb1RJnt = mc.joint(prefix+"wrist_r_jnt", name=prefix+"thumb1_r_jnt", p=(-11.909*size, 23.716*size, 0.026*size))
        thumb2RJnt = mc.joint(prefix+"thumb1_r_jnt", name=prefix+"thumb2_r_jnt", p=(-12.129*size, 23.402*size, 0.656*size))
        thumb3RJnt = mc.joint(prefix+"thumb2_r_jnt", name=prefix+"thumb3_r_jnt", p=(-12.610*size, 23.063*size, 1.2118*size))
        thumb4RJnt = mc.joint(prefix+"thumb3_r_jnt", name=prefix+"thumb4_r_jnt", p=(-13.303*size, 22.8*size, 1.477*size))

        #7b. wrist_r to index4_r
        index1RJnt = mc.joint(prefix+"wrist_r_jnt", name=prefix+"index1_r_jnt", p=(-13.0421*size, 23.716*size, 0.104*size))
        index2RJnt = mc.joint(prefix+"index1_r_jnt", name=prefix+"index2_r_jnt", p=(-13.957*size, 23.716*size, 0.261*size))
        index3RJnt = mc.joint(prefix+"index2_r_jnt", name=prefix+"index3_r_jnt", p=(-14.915*size, 23.48*size, 0.426*size))
        index4RJnt = mc.joint(prefix+"index3_r_jnt", name=prefix+"index4_r_jnt", p=(-15.79*size, 23.021*size, 0.576*size))

        #7c. wrist_r to middle4_r
        middle1RJnt = mc.joint(prefix+"wrist_r_jnt", name=prefix+"middle1_r_jnt", p=(-13.052*size, 23.716*size, -0.597*size))
        middle2RJnt = mc.joint(prefix+"middle1_r_jnt", name=prefix+"middle2_r_jnt", p=(-14.046*size, 23.716*size, -0.541*size))
        middle3RJnt = mc.joint(prefix+"middle2_r_jnt", name=prefix+"middle3_r_jnt", p=(-15.081*size, 23.464*size, -0.484*size))
        middle4RJnt = mc.joint(prefix+"middle3_r_jnt", name=prefix+"middle4_r_jnt", p=(-16.028*size, 22.974*size, -0.431*size))

        #7d. wrist_r to ring4_r
        ring1RJnt = mc.joint(prefix+"wrist_r_jnt", name=prefix+"ring1_r_jnt", p=(-13.053*size, 23.716*size, -1.223*size))
        ring2RJnt = mc.joint(prefix+"ring1_r_jnt", name=prefix+"ring2_r_jnt", p=(-13.995*size, 23.716*size, -1.243*size))
        ring3RJnt = mc.joint(prefix+"ring2_r_jnt", name=prefix+"ring3_r_jnt", p=(-14.979*size, 23.477*size, -1.265*size))
        ring4RJnt = mc.joint(prefix+"ring3_r_jnt", name=prefix+"ring4_r_jnt", p=(-15.879*size, 23.0127*size, -1.284*size))

        #7e. wrist_r to pinky4_r
        pinky1RJnt = mc.joint(prefix+"wrist_r_jnt", name=prefix+"pinky1_r_jnt", p=(-13.045*size, 23.716*size, -1.886*size))
        pinky2RJnt = mc.joint(prefix+"pinky1_r_jnt", name=prefix+"pinky2_r_jnt", p=(-13.891*size, 23.716*size, -2.013*size))
        pinky3RJnt = mc.joint(prefix+"pinky2_r_jnt", name=prefix+"pinky3_r_jnt", p=(-14.781*size, 23.497*size, -2.147*size))
        pinky4RJnt = mc.joint(prefix+"pinky3_r_jnt", name=prefix+"pinky4_r_jnt", p=(-15.595*size, 23.072*size, -2.269*size))

    # orient skeleton
    orientBipedSkeleton(rootJnt)

    mc.select(rootJnt)
    return rootJnt
 
# function to reorient the skeleton joints to "factory settings" so that the autorig maintains consistent orientations no matter the joint positions.
def orientBipedSkeleton(rootJnt = None):
    if not rootJnt:
        return False

    target = mc.listRelatives(rootJnt, ad=1)
    target.append(rootJnt)

    # orient rootJnt
    # find and orient the rest of the joints
    for i in range(0,len(target)):
        mc.joint(target[i], e=True, oj='xzy', secondaryAxisOrient='zup', zso=True)

    return True 

def cbs():
    rm()
    createBipedSkeleton()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Write a function that will build an IK/FK rig programmatically, given 3 joints as the input
# 1. Function should assume joints are oriented correctly
# 2. Process:
#   2.1. Duplicates the given joint heirarchy
#   2.2. Renames duplicate to have "_IK" suffix
#   2.3. Runs chain through IK setup function as written previously
#   2.4. Duplicates original chain
#   2.5. Renames duplicate to have "_FK" suffix
#   2.6. Runs chain through FK setup function as written previously
#   2.7. Create "Settings" curve and constrains it to the last skin joint
#   2.8. Add attribute to Settings curve for FK/IK switch
#   2.9. Constrains original joints to the FK/IK joints using parentConstraints
#   2.10. Link constraints up to FK/IK attribute on Settings controller
#   2.11. Cleans up nodes into a single grouped hierarchy, leaving the original chain intact.
# 3. return group

def fkikCreateController(startJoint=None, endJoint=None, name="controller"):
    name = getUniqueName(name)
    target = []

    print "startJoint: " + str(startJoint) + "   endJoint: " + str(endJoint)

    if not startJoint or not endJoint:
        target = s()
    else:
        firstList = mc.listRelatives([startJoint], ad=1)
        secondList = mc.listRelatives([endJoint], ad=1)
        target = []
        for i in range(0,len(firstList) - len(secondList)):
            target.append(firstList[i])
        target.append(startJoint)
        print "Specified start and end joints."
        print "Listing: " + target
    
    for i in range(0,len(target)):
        tempTarget = mc.listRelatives([target[i]], ad=1)
        tempTarget.append(target[i])
        print "0. tempTarget: " + str(tempTarget)
        origTarget = []
        for h in range(0,len(tempTarget)):
            origTarget.append(tempTarget[(len(tempTarget)-1)-h])
        print "1. origTarget: " + str(origTarget)

        name1 = getUniqueName(target[i]+"_IK")
        ikTarget = duplicateSpecial(name=name1)
        print "2. ikTarget: " + str(ikTarget)

        name2 = getUniqueName(target[i]+"_FK")
        fkTarget = duplicateSpecial(name=name2)
        print "3. fkTarget: " + str(fkTarget)

        name3 = getUniqueName(name)
        if not startJoint or not endJoint:
            startJoint = ikTarget[0]
            endJoint = ikTarget[len(target)-2]
        ikCreateControllerAlt(startJoint=startJoint, endJoint=endJoint, name=name3)
        
        name4 = getUniqueName(name)
        fkCreateController(fkTarget, name=name4)

        settings = controllerGeometry(controlType="star",size=2,name="settings")
        # ...if you want to rotate the star controller
        #mc.setAttr(settings + ".rotateX",90)
        #freezeTransformations(settings)
        pos = getPos([target[i]])
        mc.move(pos[0][0],pos[0][1],pos[0][2])
        # do later!
        #py.parentConstraint(settings,target[i],mo=1)
        fkikName = "FKIK_switch"
        fkik = addAttrFloatSlider([settings],name=fkikName)
        fkikVal = mc.getAttr(settings + "." + fkikName)
        print fkikVal

        for j in range(0,countChain(target[i])+1):
            pcfk = py.parentConstraint(fkTarget[j],origTarget[j])
            expr1 = "expressionEditor EE \""+pcfk+"\" \""+fkTarget[j]+"W0\";"
            print "expr1: " + expr1
            #expr2 = "expression -s \""+str(pcfk)+"."+str(fkTarget[j])+"W0 = "+str(settings)+"."+str(fkikName)+"\"  -o "+str(settings)+" -ae 1 -uc all ;"
            expr2 = "expression -s \""+pcfk+"."+fkTarget[j]+"W0 = abs(1-"+settings+"."+fkikName+")\"  -o "+settings+" -ae 1 -uc all ;"
            print "expr2: " + expr2
            mel.eval(expr1)
            mel.eval(expr2)
            #~~
            pcik = py.parentConstraint(ikTarget[j],origTarget[j])
            expr3 = "expressionEditor EE \""+pcik+"\" \""+ikTarget[j]+"W1\";"
            print "expr1: " + expr3
            expr4 = "expression -s \""+pcik+"."+ikTarget[j]+"W1 = "+settings+"."+fkikName+"\"  -o "+settings+" -ae 1 -uc all ;"
            print "expr2: " + expr4
            mel.eval(expr3)
            mel.eval(expr4)

        py.parentConstraint(settings,target[i],mo=1)
        name5 = getUniqueName(name)
        mc.group(settings,name1,name2,name3,name4,name=name5)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Write a function that will automatically create an IK setup, given a list of joints
# 
# 1. Assume joints are oriented correctly
# 2. Function should return base IK joint, control curves
# 3. Process:
#   3.1. Create ikHandle from base joint to end joint
#   3.2. Create cube control curve
#   3.3. snap controller_constraint to end joint
#   3.4. parent ikHandle to control curve
#   3.5. create pole vector controller (see constrain menu)
#   3.6. snap pole vector controller to middle joint *
#   3.7. create pole vector constraint to ikHandle
#   3.8. clean up all created objects into separate group
# 4. def createIKControls(startJoint, endJoint)
# 5. return [group, IK Controller, Pole Vector, IK Chain Base]
# 
# * Make the middle snap to the middle joint in any number of arbitrary joints. If there is an even number, 
# just pick the lowest of the 2 half joints. (ie: 3 joints, pole on 2nd, 4 joints - pole vector on 2nd. 
# 5 joints - pole vector on 3rd, 6 joints - pole on 3rd, etc.)

def ikCreateController(startJoint=None, endJoint=None, controlType="cube", size=1.0, name="controller"):
    name = getUniqueName(name)

    #getting rid of multiple targets
    if not startJoint:
        startJoint = mc.ls(sl=True)[0]

    joints = mc.listRelatives( startJoint, ad=True )
    
    # let's find our end joint
    if not endJoint:
        endJoint = joints[0]


    finalGroup = mc.group(em=True, name=name)

    appendCtl = "_control"
    appendCst = "_constraint"
    appendGrp = "_group"
    appendPole = "_pole"

    returns = []

    # getting rid of loop, since the only time this loop will run
    # is if you want to select multiple start joints and have multiple
    # ik controls being made with a single command. It's better to keep
    # the scope of this function limited at this point and if you want
    # to create multiple ik controllers, create another function that
    # will call this one based off multiple selection

    #for i in range(0,len(target)):

    '''
    #2. Create IK handle
    if not startJoint or not endJoint:
        mc.select(target[i])
        joints = mc.listRelatives(ad=True)
        joints.append(target[i])
        mc.select(joints[len(joints)-1],joints[0])
    else:
        mc.select(startJoint)
        joints = mc.listRelatives(ad=True)
        joints.append(startJoint)
        mc.select(startJoint,endJoint)
    '''

    # directly inputting the start joint and end effector
    print startJoint[0]
    print endJoint
    handle = py.ikHandle(sj=startJoint[0], ee=endJoint, solver="ikRPsolver")
    
    #3. Create controller
    ctl = controllerGeometry(controlType,size, getUniqueName(name), appendCtl) # getting unique name now
    ctl2 = controllerGeometry("sphere",size, getUniqueName(name+appendPole), appendCtl) # getting unique name now
    
    # got rid of conditional
    '''
    if not startJoint or not endJoint:
        snapToPos([ctl,joints[0]])
    else:
    '''
    snapToPos([ctl,endJoint[0]])
    
    #~~
    # got rid of selection, directly inputting what to group
    ctlGrp = [mc.group(ctl, n= getUniqueName(name + appendGrp))]
    ctlCst = [mc.group(ctlGrp, n= getUniqueName(name + appendCst))]

    #~~
    mc.parent(handle[0],ctlGrp[0])
    middleJoint = 0;
    
    # at this point startJoint and endJoint are definitely going to be there.
    # we don't want to create too many similar conditionals and reuse code.
    # It's better to just create a function that tries to fill in the information,
    # for instance in this case, the function needs a start joint and an end joint,
    # so you should use selection in the beginning to get your start and end joint
    # instead of creating a number of conditionals to do different things at different
    # times. These branches could lead to bugs.
    '''
    if not startJoint or not endJoint:
        jointCount = countChain(target[i])
    else:
    '''
    jointCount = countChain(startJoint) - countChain(endJoint)
    
    '''
    if(jointCount%2==0): #even joints
        middleJoint = int(jointCount/2) #-1
    else: #odd joints
        middleJoint = int(jointCount/2)
    '''

    # in order to find the middle joint, we need a list
    # of all of the joints between the start joint and the end joint
    # One way to do this is to get the long name of the end joint,
    # since we assume we're dealing with the same chain, the start
    # joint will be in the long name so we split the string by the short
    # name. This will give us a string that looks like this:
    # "joint2|joint3|joint4" We then split that again by "|" and now
    # have an array that looks like this: ["joint2", "joint3", "joint4"]
    # and we could now just find the halfway point within that array
    # and get our mid point.
    # As a warning, though, this method will break if the start, end or
    # middle joint don't have a unique name
    activeJoints = mc.ls(endJoint, l=True)[0].split(startJoint)[-1].split('|')

    middleJoint = activeJoints[int(floor(jointCount/2.0))]

    # at this point startJoint and endJoint are definitely going to be there.
    '''
    if not startJoint or not endJoint:
        ikControllerConstraints(ctl,handle[0],ctl2,joints[middleJoint])
    else:
    '''
    ikControllerConstraints(ctl,handle[0],ctl2,middleJoint)     

    #4. Try to apply controller to original selection
    mc.parent(ctlCst[0],name)
    mc.parent(ctl2,name)
    returns.append([ctlCst,ctlGrp,ctl,ctl2])

    return (name,returns)

#~~

def ikControllerConstraints(constraint, target, constraint2, target2):
    #3b. select parent of target joint

    # got rid of selection
    #mc.select(constraint, target)
    mc.parentConstraint(constraint, target, mo=1)
    #mc.select(constraint2, target2)
    snapToPos([constraint2, target2])
    #mc.select(constraint2,target)
    mc.poleVectorConstraint(constraint2, target)
    #mc.select(controller,handle)
    #cst1 = mc.parentConstraint(mo=1)
    #mc.select(constraint,handle)
    #cst2 = mc.poleVectorConstraint()

def countChain(target=None):
    if not target:
        try:
            target = s()
        except:
            print "Nothing selected or specified."
            return

    try:
        chain = py.listRelatives(target, ad=True)
        returnCount = len(chain)
    except:
        returnCount = 0
    print returnCount
    return(returnCount)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IK Controller Alt Version (without David's improvements)
# Generally less reliable but can succeed when used as shelf button, where normal function breaks.

def ikCreateControllerAlt(startJoint=None, endJoint=None, controlType="cube", size=1.0, name="controller"):
    name = getUniqueName(name)
    #1. Store current selection
    if(startJoint):
        target = [startJoint]
    else:
        target = mc.ls(sl=True)

    finalGroup = mc.group(em=True, name=name)

    appendCtl = "_control"
    appendCst = "_constraint"
    appendGrp = "_group"
    appendPole = "_pole"

    returns = []

    for i in range(0,len(target)):
        joints = []
        #2. Create IK handle
        if not startJoint or not endJoint:
            mc.select(target[i])
            joints = mc.listRelatives(ad=True)
            joints.append(target[i])
            mc.select(joints[len(joints)-1],joints[0])
        else:
            mc.select(startJoint)
            joints = mc.listRelatives(ad=True)
            joints.append(startJoint)
            mc.select(startJoint,endJoint)

        handle = mc.ikHandle(solver="ikRPsolver")
        
        #3. Create controller
        ctl = controllerGeometry(controlType,size,name + str(i+1),appendCtl)
        ctl2 = controllerGeometry("sphere",size,name+appendPole + str(i+1),appendCtl)
        
        if not startJoint or not endJoint:
            mc.select(ctl,joints[0])
        else:
            mc.select(ctl,endJoint)

        snapToPos()
        #~~
        mc.select(ctl)
        mc.group(n=name + appendGrp + str(i+1))
        ctlGrp = mc.ls(sl=1)
        mc.group(n=name + appendCst + str(i+1))
        ctlCst = mc.ls(sl=1)
        #~~
        mc.parent(handle[0],ctlGrp[0])
        middleJoint = 0;
        if not startJoint or not endJoint:
            jointCount = countChainAlt(target[i])
        else:
            jointCount = countChainAlt(startJoint) - countChainAlt(endJoint)
        if(jointCount%2==0): #even joints
            middleJoint = int(jointCount/2) #-1
        else: #odd joints
            middleJoint = int(jointCount/2)
        
        if not startJoint or not endJoint:
            ikControllerConstraintsAlt(ctl,handle[0],ctl2,joints[middleJoint])      
        else:
            ikControllerConstraintsAlt(ctl,handle[0],ctl2,joints[middleJoint-countChainAlt(endJoint)])      

        #4. Try to apply controller to original selection
        mc.parent(ctlCst[0],name)
        mc.parent(ctl2,name)
        returns.append([ctlCst,ctlGrp,ctl,ctl2])

    return (name,returns)

#~~

def ikControllerConstraintsAlt(constraint, target, constraint2, target2):
    #3b. select parent of target joint
    mc.select(constraint, target)
    mc.parentConstraint(mo=1)
    mc.select(constraint2, target2)
    snapToPos()
    mc.select(constraint2,target)
    mc.poleVectorConstraint()
    #mc.select(controller,handle)
    #cst1 = mc.parentConstraint(mo=1)
    #mc.select(constraint,handle)
    #cst2 = mc.poleVectorConstraint()    

def countChainAlt(target=None):
    if not target:
        try:
            target = s()
        except:
            print "Nothing selected or specified."
            return

    try:
        chain = py.listRelatives(target, ad=True)
        returnCount = len(chain)
    except:
        returnCount = 0
    print returnCount
    return(returnCount)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Function to create an fk controller.
# Takes in controlType (string) that is either "circle", "sphere", or "cube"
# Takes in unit size
# creates the control curve and groups it and names the objects <name>_constraint, <name>_grp, <name>_control
# returns the names of the objects it's created  

def fkCreateController(targets=None, controlType="cube", size=1.0, name="controller"):
    name = getUniqueName(name)

    #1. Store current selection
    if not targets:
        targets = mc.ls(sl=1) # changed the name of this variable because we're expecting an array
    finalGroup = mc.group(em=True, name=name)

    appendCtl = "_control"
    appendCst = "_constraint"
    appendGrp = "_group"


    # shortened this a little and got rid of clamping the numReps to 1
    # it shouldn't run if there are no targets

    #numReps = len(target)
    #if(numReps<1):
    #    numReps=1
    
    # creating a return array
    returns = []

    for i in range( 0, len(targets) ):
        #2. Create controller

        # I'm appending the i to the controller name to create unique
        # names for the multiple fk controls. Otherwise it will try
        # to create something with the same name and fail.
        ctl = controllerGeometry(controlType,size,name+str(i+1),appendCtl)

        ctlGrp = mc.group(ctl, n=name + appendGrp + str(i+1)) # putting the grp right into a variable
        # also explicitly specifying what should be grouped, just in case we don't know
        # what's selected at that moment

        #ctlGrp = mc.ls(sl=1)
        
        ctlCst = mc.group(ctlGrp, n=name + appendCst + str(i+1)) # putting the grp right into a variable
        #ctlCst = mc.ls(sl=1)

        #3. Try to apply controller to original selection
        # let's get rid of the try, except so we know where the error is
        mc.parent(ctlCst,name) # ctlCst isn't an array since the grp command returns a string
        fkControllerConstraints(targets[i],ctlCst,ctl)

        returns.append([ctlCst,ctlGrp,ctl])

    return (name, returns)

#~~

def fkControllerConstraints(target,constraint,controller):
    #3a. snap controller to target joint location
    # was missing a .py here
    py.select(constraint,target)
    snapToPos()

    #3b. select parent of target joint
    mom = mc.listRelatives(target,parent=True)

    # changed this chunk of code so that it will apply the constraint to the fk controller
    # if there is a parent, but if not it will just continue on and apply the constraint
    # for the joint. Otherwise it will create the controller
    # but not do anything with it.
    if mom: #changed this to not look at mom's length, but just to check if mom has anything in it.
        # removed selection as you could apply constraint directly
        cst1 = mc.parentConstraint(mom[0],constraint, mo=1)
    else:
        print "No parent detected, not parentConstraining FK controller."

    # removed selection as you could apply constraint directly
    cst2 = mc.parentConstraint(controller,target, mo=0)    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
def controllerGeometry(controlType="cube",size=1,name="controller",appendCtl="_ctl"):
    if(controlType=="circle"):
        ctl = mc.circle(r=size/2.0, n=name + appendCtl)
        #setAttr(ls(sl=1)[0] + ".rotateX",90)
    elif(controlType=="sphere"):
        ctl = mc.curve(n=name + appendCtl, d=1, p=((0*(size/2.0),1*(size/2.0),0*(size/2.0)),(0*(size/2.0),0.809017*(size/2.0),-0.587785*(size/2.0)),(0*(size/2.0),0.309017*(size/2.0),-0.951057*(size/2.0)),(0*(size/2.0),-0.309017*(size/2.0),-0.951057*(size/2.0)),(0*(size/2.0),-0.809017*(size/2.0),-0.587785*(size/2.0)),(0*(size/2.0),-1*(size/2.0),5.96046e-08*(size/2.0)),(0*(size/2.0),-0.809017*(size/2.0),0.587785*(size/2.0)),(0*(size/2.0),-0.309017*(size/2.0),0.951057*(size/2.0)),(0*(size/2.0),0.309017*(size/2.0),0.951057*(size/2.0)),(0*(size/2.0),0.809017*(size/2.0),0.587785*(size/2.0)),(0*(size/2.0),1*(size/2.0),0*(size/2.0)),(0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(1*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),-0.587785*(size/2.0),0*(size/2.0)),(0.309017*(size/2.0),-0.951057*(size/2.0),0*(size/2.0)),(0*(size/2.0),-1*(size/2.0),5.96046e-08*(size/2.0)),(-0.309017*(size/2.0),-0.951057*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),-0.587785*(size/2.0),0*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(-0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(0*(size/2.0),1*(size/2.0),0*(size/2.0)),(-0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0*(size/2.0),-0.587785*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(0.809017*(size/2.0),0*(size/2.0),-0.587785*(size/2.0)),(1*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),0*(size/2.0),0.587785*(size/2.0)),(0.309017*(size/2.0),0*(size/2.0),0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),0.951057*(size/2.0)),(-0.809017*(size/2.0),0*(size/2.0),0.587785*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0)), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37))
    elif(controlType=="star"):
        ctl = mc.curve(n=name + appendCtl, d=1, p=((-0.849836*(size/2.0),0*(size/2.0),-0.849836*(size/2.0)),(-0.79687*(size/2.0),0*(size/2.0),-0.330074*(size/2.0)),(-1.20185*(size/2.0),0*(size/2.0),0*(size/2.0)),(-0.79687*(size/2.0),0*(size/2.0),0.330074*(size/2.0)),(-0.849836*(size/2.0),0*(size/2.0),0.849836*(size/2.0)),(-0.330074*(size/2.0),0*(size/2.0),0.79687*(size/2.0)),(0*(size/2.0),0*(size/2.0),1.20185*(size/2.0)),(0.330074*(size/2.0),0*(size/2.0),0.79687*(size/2.0)),(0.849836*(size/2.0),0*(size/2.0),0.849836*(size/2.0)),(0.801233*(size/2.0),0*(size/2.0),0.326518*(size/2.0)),(1.20185*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.801233*(size/2.0),0*(size/2.0),-0.326518*(size/2.0)),(0.849836*(size/2.0),0*(size/2.0),-0.849836*(size/2.0)),(0.326518*(size/2.0),0*(size/2.0),-0.801233*(size/2.0)),(0*(size/2.0),0*(size/2.0),-1.20185*(size/2.0)),(-0.333798*(size/2.0),0*(size/2.0),-0.801604*(size/2.0)),(-0.857352*(size/2.0),0*(size/2.0),-0.865126*(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16))
    elif(controlType=="cube"):
        ctl = mc.curve(n=name + appendCtl, d=1, p=((-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19))
    else:
        print 'Nothing created; valid types are "circle", "sphere", "star", and "cube".'
        return
    return ctl    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def snapToPos(s=None):
    if not s:
        s = mc.ls(sl=1)
    for i in range(0,len(s)-1):
        cst0 = mc.parentConstraint(s[len(s)-1],s[i],mo=0)
        mc.delete(cst0)    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def addAttrVector(target=None, name="tempVector"):
    if not target:
        target = mc.ls(sl=1)
    for i in range(0,len(target)):
        mel.eval("addAttr -ln \"" + name + "\"  -at double3  "+target[i]+";")
        mel.eval("addAttr -ln \""+name+"X\"  -at double -p "+name+"  "+target[i]+";")
        mel.eval("addAttr -ln \""+name+"Y\"  -at double -p "+name+"  "+target[i]+";")
        mel.eval("addAttr -ln \""+name+"Z\"  -at double -p "+name+"  "+target[i]+";")
        mel.eval("setAttr -e-keyable true "+target[i]+"." + name + ";")
        mel.eval("setAttr -e-keyable true "+target[i]+"." + name + "X;")
        mel.eval("setAttr -e-keyable true "+target[i]+"." + name + "Y;")
        mel.eval("setAttr -e-keyable true "+target[i]+"." + name + "Z;")

def addAttrFloat(target=None, name="tempFloat"):
    if not target:
        target = mc.ls(sl=1)
    for i in range(0,len(target)):
        mel.eval("addAttr -ln \"" + name + "\"  -at double  "+target[i]+";")
        mel.eval("setAttr -e-keyable true "+target[i]+"." + name + ";")

def addAttrFloatSlider(target=None, name="tempFloat",minVal=0,maxVal=1,defaultVal=0):
    if not target:
        target = mc.ls(sl=1)
    for i in range(0,len(target)):
        mel.eval("addAttr -ln \"" + name + "\"  -at double  -min "+str(minVal)+" -max "+str(maxVal)+" -dv "+str(defaultVal)+"  "+target[i]+";")
        mel.eval("setAttr -e-keyable true "+target[i]+"." + name + ";")

def addAttrString(target=None, name="tempString"):
    if not target:
        target = mc.ls(sl=1)
    for i in range(0,len(target)):
        mel.eval("addAttr -ln \"" + name + "\"  -dt \"string\"  "+target[i]+";")
        #mel.eval("setAttr -e-keyable true "+target[i]+"." + name + ";")

def addAttrBoolean(target=None, name="tempBoolean"):
    returns = []
    if not target:
        target = mc.ls(sl=1)
    for i in range(0,len(target)):
        mel.eval("addAttr -ln \"" + name + "\"  -at bool  "+target[i]+";")
        mel.eval("setAttr -e-keyable true "+target[i]+"." + name + ";")
        val = target[i] + "." + name
        returns.append(val)
    return returns

def createBlendshapes():
    sel = mc.ls(sl=1,fl=1)
    
    time = mc.currentTime(q=1)
    min = int(mc.playbackOptions(q=1, min=1))
    max = int(mc.playbackOptions(q=1, max=1)+1)
    
    timeStep = (float(min) / float(max))
    
    for i in sel:
        bsLs = []
        for t in range(min, max):
            mc.setAttr("time1.outTime", t)
            bsShape=mc.duplicate(i, n="%s_fr_%02d"%(i,t))[0]
            bsLs.append(bsShape)
        
        if i.endswith("_Geo") == 1:
            newNm="%s_outputMesh"%i.split("_")[0]
        else:
            newNm="%s_outputMesh"%i
            
        tar = mc.rename(bsLs.pop(0), newNm)
    
        grpNm = mc.group(bsLs, n="%s_BS_Grp"%i)
        
        bsLs.append(tar)
    
        bs = mc.blendShape(bsLs, ib=1, n=i.replace("_Geo","_BS"))
        
        mc.delete(grpNm)
        
        mc.setKeyframe(bs, v=0, at=bsShape, t=min, ott="linear")
        mc.setKeyframe(bs, v=1, at=bsShape, t=max-1, itt="linear")
    
    mc.currentTime(time, u=1)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

fk=fkCreateController
ik=ikCreateController
fkik = fkikCreateController

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# SHADERS, CAMERAS, ETC.

def setVertexColor(r=1, g=0, b=0):
	c = (r,g,b)
	py.polyColorPerVertex(colorRGB=c)
	return c

def getVertexColor():
    return py.polyColorPerVertex(query=True, colorRGB=True)

def sCameraCubeCam(p = [0,0,0], r = [0,0,0], fov=90, name="camera"):
    name = getUniqueName(name)
    target = py.camera(n=str(name), horizontalFieldOfView=fov)
    py.move(p[0],p[1],p[2])
    py.rotate(r[0],r[1],r[2])
    return target


def sCameraCube(ipd = 0.064, fov = 90, stereo=False):
    target = []
    ipd /= 2.0
    
    if (stereo==True):
        target += sCameraCubeCam([-ipd,0,0], [0,0,0], fov, "CameraNorthL") #northL
        target += sCameraCubeCam([ipd,0,0], [0,0,0], fov, "CameraNorthR") #northR
        target += sCameraCubeCam([-ipd,0,0], [0,0,180], fov, "CameraSouthL") #southL
        target += sCameraCubeCam([ipd,0,0], [0,0,180], fov, "CameraSouthR") #southR
        target += sCameraCubeCam([-ipd,0,0], [0,90,0], fov, "CameraUpL") #upL
        target += sCameraCubeCam([ipd,0,0], [0,90,0], fov, "CameraUpR") #upR
        target += sCameraCubeCam([-ipd,0,0], [0,-90,0], fov, "CameraDownL") #downL
        target += sCameraCubeCam([ipd,0,0], [0,-90,0], fov, "CameraDownR") #downR
        #~~
        '''
        target += sCameraCubeCam([0,0,-ipd], [0,0,-90], fov, "CameraEastL") #eastL
        target += sCameraCubeCam([0,0,ipd], [0,0,-90], fov, "CameraEastR") #eastR
        target += sCameraCubeCam([0,0,-ipd], [0,0,90], fov, "CameraWestL") #westL
        target += sCameraCubeCam([0,0,ipd], [0,0,90], fov, "CameraWestR") #westR
        '''
        target += sCameraCubeCam([-ipd,0,0], [0,0,-90], fov, "CameraEastL") #eastL
        target += sCameraCubeCam([ipd,0,0], [0,0,-90], fov, "CameraEastR") #eastR
        target += sCameraCubeCam([-ipd,0,0], [0,0,90], fov, "CameraWestL") #westL
        target += sCameraCubeCam([ipd,0,0], [0,0,90], fov, "CameraWestR") #westR
    else:
        target += sCameraCubeCam([0,0,0], [0,0,0], fov, "CameraNorth") #north
        target += sCameraCubeCam([0,0,0], [0,0,180], fov, "CameraSouth") #south
        target += sCameraCubeCam([0,0,0], [0,90,0], fov, "CameraUp") #up
        target += sCameraCubeCam([0,0,0], [0,-90,0], fov, "CameraDown") #down
        target += sCameraCubeCam([0,0,0], [0,0,-90], fov, "CameraEast") #east
        target += sCameraCubeCam([0,0,0], [0,0,90], fov, "CameraWest") #west
        
    sl = py.spaceLocator(name="cameraRoot")

    for i in range(0,len(target)):
        try:
            py.parent(target[i],sl)
        except:
            print "Error parenting camera to locator."

    s(sl)


def revealYaxis():
    target = py.ls(sl=1)

    for i in range(0,len(target)):
        py.select(target[i])
        p = getPos()
        a = getAlpha()
        
        t(0)
        keyAlpha(0)
        
        delay = 10 * p[1]
        t(delay)
        keyAlpha(0)
        
        t(delay+10)
        keyAlpha(a)

def createShader(shaderType="lambert",shaderColor=[127,127,127,255],useTexture=False):
    #1. get selection
    target = py.ls(sl=1)
    #2. initialize shader
    shader=py.shadingNode(shaderType,asShader=True)
    #3. create a file texture node
    if(useTexture==True):
        file_node=py.shadingNode("file",asTexture=True)
    #4. create a shading group
    shading_group= py.sets(renderable=True,noSurfaceShader=True,empty=True)
    #5. set the color
    setRGBA(shader,shaderColor)
    #6. connect shader to sg surface shader
    py.connectAttr('%s.outColor' %shader ,'%s.surfaceShader' %shading_group)
    #7. connect file texture node to shader's color
    if(useTexture==True):
        py.connectAttr('%s.outColor' %file_node, '%s.color' %shader)
    #9. restore selection
    py.select(target)
    #10. return the completed shader
    return shader

def setShader(shader):
    py.hyperShade(a=shader)

def getShader():
    # get shapes of selection:
    shapesInSel = py.ls(dag=1,o=1,s=1,sl=1)
    # get shading groups from shapes:
    shadingGrps = py.listConnections(shapesInSel,type='shadingEngine')
    # get the shaders:
    shader = py.ls(py.listConnections(shadingGrps),materials=1)
    return shader[0] 

def quickShader(shaderColor=[255,0,0]):
    if(len(shaderColor)==3):
        shaderColor.append(255)
    shader = createShader("lambert",shaderColor,False)
    setShader(shader)
    return shader
    
#~~

#set RGBA, RGB, A at shader level
def setRGBA(s,c):
    r = float(c[0]) / 255.0
    g = float(c[1]) / 255.0
    b = float(c[2]) / 255.0
    a = abs(1-(float(c[3]) / 255.0))
    py.setAttr(s + ".color", (r,g,b))
    py.setAttr(s + ".transparency", (a,a,a))

def setRGB(s,c):
    r = float(c[0]) / 255.0
    g = float(c[1]) / 255.0
    b = float(c[2]) / 255.0
    py.setAttr(s + ".color", (r,g,b))

def setA(s,c):
    a = abs(1-(float(c) / 255.0))
    py.setAttr(s + ".transparency", (a,a,a))   

#~~

# set RGB color 0-255, any number of selections
def setColor(c):
    target = py.ls(sl=1)
    for i in range(0,len(target)):
        py.select(target[i])
        s = getShader()
        r = float(c[0]) / 255.0
        g = float(c[1]) / 255.0
        b = float(c[2]) / 255.0
        py.setAttr(s + ".color", (r,g,b))      

# returns RGB color 0-255 of first selection
def getColor():
    target = py.ls(sl=1)
    py.select(target[0])
    s = getShader()
    c = py.getAttr(s + ".color")   
    r = float(c[0]) / 255.0
    g = float(c[1]) / 255.0
    b = float(c[2]) / 255.0
    return (r,g,b)
#~~

# set transparency 0-255, any number of selections
def setAlpha(c):
    target = py.ls(sl=1)
    for i in range(0,len(target)):
        py.select(target[i])
        s = getShader()
        a = abs(1-(float(c) / 255.0))
        py.setAttr(s + ".transparency", (a,a,a))   

# returns transparency 0-255 from first selection
def getAlpha():
    target = py.ls(sl=1)
    py.select(target[0])
    s = getShader()
    aa = py.getAttr(s + ".transparency")
    a = 255 * abs(1-aa[0])
    return a

# keyframe transparency 0-255, any number of selections
def keyAlpha(c):
    target = py.ls(sl=1)
    for i in range(0,len(target)):
        py.select(target[i])
        s = getShader()
        setA(s,c)
        py.mel.eval("setKeyframe { \"" + s + ".it\" };")

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
