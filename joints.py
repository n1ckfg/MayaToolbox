# JOINTS

import pymel.core as py
import maya.cmds as mc
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
    py.select(d=True)
    for i in range(0,numChains):
        joints = makeJoints(numJoints)
        py.select(joints[0])
        py.move(numJoints*i,0,0)
        py.select(d=True)

def makeJoints(reps=3):
    joints = []
    offset = 0
    offsetDelta = 2
    middleJoint=0
    startPos = [0,0,0]
    target = py.selected()
    if(len(target)>=1):
        startPos = py.xform(target[0], q=True, t=True, ws=True)
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
            
        newJoint = py.joint(position=[startPos[0] + offset,startPos[1],startPos[2] + (i*4)])
        joints.append(newJoint)
    return joints

def keyAllChildren(jointsOnly):
    target=py.ls(sl=1)

    for i in range(0,len(target)):
       py.select(target[i])
       py.setKeyframe()

       try:
          if(jointsOnly==True):
             kids = py.istRelatives(ls(selection=True), children=True, type="joint", allDescendents=True)
          else:
             kids = py.listRelatives(ls(selection=True), children=True, allDescendents=True)
          for k in kids:
             py.select(k)
             py.setKeyframe()
       except:
          print "No child joints."

    py.select(target)

def lockTranslate(target, doLock):
    py.setAttr(target + ".translateX",lock=doLock)
    py.setAttr(target + ".translateY",lock=doLock)
    py.setAttr(target + ".translateZ",lock=doLock)

def lockRotate(target, doLock):
    py.setAttr(target + ".rotateX",lock=doLock)
    py.setAttr(target + ".rotateY",lock=doLock)
    py.setAttr(target + ".rotateZ",lock=doLock)

def lockScale(target, doLock):
    py.setAttr(target + ".scaleX",lock=doLock)
    py.setAttr(target + ".scaleY",lock=doLock)
    py.setAttr(target + ".scaleZ",lock=doLock)

def lockHandler(t, r, s): #bool, bool, bool
    target = py.selected()
    for i in range(0,len(target)):
        lockTranslate(target[i],t)
        lockRotate(target[i],r)
        lockScale(target[i],s)

def lockChildren(jointsOnly, t, r, s):
    target=py.ls(sl=1)

    for i in range(0,len(target)):
       py.select(target[i])
       lockHandler(t,r,s)

       try:
          if(jointsOnly==True):
             kids = py.listRelatives(ls(selection=True), children=True, type="joint", allDescendents=True)
          else:
             kids = py.listRelatives(ls(selection=True), children=True, allDescendents=True)
          for k in kids:
             py.select(k)
             lockHandler(t,r,s)
       except:
          print "No child joints."

    py.select(target)

def lockPuppet(jointsOnly=False):
    target=py.ls(sl=1)
    
    for i in range(0,len(target)):
        py.select(target[i])
        lockHandler(False,False,False) #root joint is unlocked
        
        try:
            if(jointsOnly==True):
                kids = py.listRelatives(ls(selection=True), children=True, type="joint", allDescendents=True)
            else:
                kids = py.listRelatives(ls(selection=True), children=True, allDescendents=True)
            for k in kids:
                py.select(k)
                lockHandler(True,True,True) #lock all...
                py.setAttr(k + ".rotateX",lock=True) 
                py.setAttr(k + ".rotateZ",lock=True) 
                py.setAttr(k + ".rotateY",lock=False) #...except Y rotation.
        except:
            print "No child joints."   
            
    py.select(target) 

def lockAll():
    lockChildren(False,True,True,True)

def lockNone():
    lockChildren(False,False,False,False)

def eyeRig(scaler): #try 4
    target = py.selected()
    py.delete(e=True)
    for i in range(0,len(target)):
        if(i<len(target)-1):
            py.expression(s=target[i]+".rotateX = " + target[len(target)-1] + ".translateY * -1 * " + str(scaler))
            py.expression(s=target[i]+".rotateY = " + target[len(target)-1] + ".translateX * " + str(scaler))

#broken
def parentConstraintAll():
    target = py.selected()
    for i in range(0,len(target)):
        if(i<len(target)-1):
            py.select(target[len(target)-1],target[i])
            py.parentConstraint()
    py.select(target)
