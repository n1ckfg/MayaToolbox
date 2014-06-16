# JOINTS

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
