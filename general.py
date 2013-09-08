# GENERAL

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
#~~

def s(_t=None):
    if not _t:
        try:
            mc.select(mc.ls(sl=1))
        except:
            print("Nothing selected.")
        return(mc.ls(sl=1))
    else:
        py.select(_t)
        return _t

def t(_t=None):
    try:
        mc.currentTime(_t)
    except:
        print "time: " + str(mc.currentTime(q=True))
    return mc.currentTime(q=True)

def d(_t=None, all=False):
    if _t:
        mc.select(_t)
    if all:
        mc.select(all=True)
    mc.delete()

def rm():
    d(all=True)

def ds():
    mc.select(d=True)

def m(p, _t=None):
    if not _t:
        _t = mc.ls(sl=1)

    for i in range (0,len(_t)):
        mc.select(_t[i])
        mc.move(p[0],p[1],p[2])

def k(_t=None):
    if(_t):
        mc.select(_t)
    mc.setKeyframe()

def cubes(num=100,spread=5):
    val = []
    for i in range(0, num):
        obj = mc.polyCube()
        val.append(obj)
        rndMove(spread)
    return val

def rnd3d(spread=5):
    return rnd(-spread,spread),rnd(-spread,spread),rnd(-spread,spread)

def rndMove(spread=5):
    val = rnd3d(spread)
    mc.move(val[0],val[1],val[2])

def getPos(target=None):
    if not target:
        target = mc.ls(sl=1)
    p = mc.xform(target[0], q=True, t=True, ws=True)
    return p

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

def showHide(target=None):
    if not target:
       target = mc.ls(sl=1)

    for i in range(0,len(target)):
        visible = mc.getAttr(target[i] + ".v")
        if(visible==False):
           mc.setAttr(target[i] + ".v",1)
        if(visible==True):
           mc.setAttr(target[i] + ".v",0) 

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
