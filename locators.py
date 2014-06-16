# LOCATORS

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
from shaders import *

def addLocator(alsoParent=False):
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
                    locName = k + "_loc"
                    locPos = mc.xform(k, q=True, t=True, ws=True)
                    loc = mc.spaceLocator(n=locName)
                    mc.move(locPos[0],locPos[1],locPos[2])
                    if(alsoParent==True):
                        mc.parent(k,loc)
                        #parentConstraint(loc,k)
            except:
                print "No child joints."

            #5. get the original selection's name
            locName = target[i] + "_loc"
        
            #6. get its position
            locPos = mc.xform(target[i], q=True, t=True, ws=True)
        
            #7. create a new locator with that name at that position
            loc = mc.spaceLocator(n=locName)
            mc.move(locPos[0],locPos[1],locPos[2])
            if(alsoParent==True):
                mc.parent(target[i],loc)
                #parentConstraint(loc,target[i])
