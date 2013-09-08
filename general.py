# GENERAL

import pymel.core as py
import maya.cmds as mc
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
#~~

def t(_t):
	mc.currentTime(_t)

def d():
	mc.delete()

def k():
	mc.setKeyframe()

def rm():
    mc.select(all=True)
    mc.delete()

def getPos():
	target = mc.ls(sl=1)
	p = mc.xform(target[0], q=True, t=True, ws=True)
	return p

def moveTols(sl=1):
    #1. make an array of all selected objects
    target = mc.ls(sl=1)

    #2. get the position of the last selected object
    pos = mc.xform(target[len(target)-1], q=True, t=True, ws=True)

    #3. move the other objects to the last selected object
    for i in range(0,len(target)-1):
        mc.select(target[i])
        mc.move(pos[0],pos[1],pos[2])

def showHide():
	target = mc.ls(sl=1)

	for i in range(0,len(target)):
	    visible = mc.getAttr(target[i] + ".v")
	    if(visible==False):
	       mc.setAttr(target[i] + ".v",1)
	    if(visible==True):
	       mc.setAttr(target[i] + ".v",0) 

def toggleSelectable():
    target = mc.ls(sl=1)
    for i in range(0,len(target)):
        disabled = mc.getAttr(target[i] + ".overrideDisplayType")
        if(disabled==2):
            mc.setAttr(target[i] + ".overrideDisplayType",0)
        else:
            mc.setAttr(target[i] + ".overrideEnabled",1)
            mc.setAttr(target[i] + ".overrideDisplayType",2)
