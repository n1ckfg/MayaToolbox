# MODELING

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
import re
#~~
from general import *

def booleanLoop():
    #1. Make an array of all selections
    target = mc.ls(sl=1)

    #2. Boolean union each item in the array to the next
    for i in range(0,len(target)-1,2):
        mc.polyBoolOp(target[i],target[i+1])
        
        #3. Delete construction history
        mc.delete(ch=True)

        #4. Recenter the pivot
        mc.xform(cp=True)

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