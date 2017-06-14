# ANIMATION--JOINTS, CONSTRAINTS, KEYFRAMES, ETC.

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
import re
#~~
from mayatoolbox import *

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

