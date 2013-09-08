# JOINTS

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
#~~
from general import *

def testJoints(numChains = 2, numJoints = 5):
    rm()
    makeChains(numChains,numJoints)    

def makeChains(numChains = 2, numJoints = 5):
    mc.select(d=True)
    for i in range(0,numChains):
        joints = makeJoints(numJoints)
        mc.select(joints[0])
        mc.move(numJoints*i,0,0)
        mc.select(d=True)

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

def keyAllChildren(jointsOnly=False):
    target=mc.ls(sl=1)

    for i in range(0,len(target)):
       mc.select(target[i])
       mc.setKeyframe()

       try:
          if(jointsOnly==True):
             kids = mc.listRelatives(target[i], children=True, type="joint", allDescendents=True)
          else:
             kids = mc.listRelatives(target[i], children=True, allDescendents=True)
          for k in kids:
             mc.select(k)
             mc.setKeyframe()
       except:
          print "Joint " + str(target[i]) + "has no child joints."

    mc.select(target)

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
        mc.select(target[i])
        lockHandler(False,False,False) #root joint is unlocked
        
        try:
            if(jointsOnly==True):
                kids = mc.listRelatives(ls(selection=True), children=True, type="joint", allDescendents=True)
            else:
                kids = mc.listRelatives(ls(selection=True), children=True, allDescendents=True)
            for k in kids:
                mc.select(k)
                lockHandler(True,True,True) #lock all...
                mc.setAttr(k + ".rotateX",lock=True) 
                mc.setAttr(k + ".rotateZ",lock=True) 
                mc.setAttr(k + ".rotateY",lock=False) #...except Y rotation.
        except:
            print "No child joints."   
            
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

#broken
def parentConstraintAll():
    target = mc.ls(sl=1)
    for i in range(0,len(target)):
        if(i<len(target)-1):
            mc.select(target[len(target)-1],target[i])
            mc.parentConstraint()
    mc.select(target)
