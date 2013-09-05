# GENERAL

import pymel.core as py
import maya.cmds as mc
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
#~~

def t(_t):
	py.currentTime(_t)

def d():
	py.delete()

def k():
	py.setKeyframe()

def rm():
    py.select(all=True)
    py.delete()

def getPos():
	target = py.ls(sl=1)
	p = py.xform(target[0], q=True, t=True, ws=True)
	return p

def moveToSelected():
    #1. make an array of all selected objects
    target = py.ls(sl=True)

    #2. get the position of the last selected object
    pos = py.xform(target[len(target)-1], q=True, t=True, ws=True)

    #3. move the other objects to the last selected object
    for i in range(0,len(target)-1):
        py.select(target[i])
        py.move(pos[0],pos[1],pos[2])

def showHide():
	target = py.ls(sl=1)

	for i in range(0,len(target)):
	    visible = py.getAttr(target[i] + ".v")
	    if(visible==False):
	       py.setAttr(target[i] + ".v",1)
	    if(visible==True):
	       py.setAttr(target[i] + ".v",0) 

def toggleSelectable():
    target = py.selected()
    for i in range(0,len(target)):
        disabled = py.getAttr(target[i] + ".overrideDisplayType")
        if(disabled==2):
            py.setAttr(target[i] + ".overrideDisplayType",0)
        else:
            py.setAttr(target[i] + ".overrideEnabled",1)
            py.setAttr(target[i] + ".overrideDisplayType",2)
