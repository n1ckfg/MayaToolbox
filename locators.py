# LOCATORS

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
#~~
from general import *
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
#~~

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


def duplicateSpecial():
    #1. make an array of all selected objects
    target = mc.ls(sl=1)

    #2. for each selected object...
    for i in range(0,len(target)):
        #3. ...select and duplicated with bones and keyframes
        mc.select(target[i])
        #call through mel because python has no rc option!
        mel.eval("duplicate -un -ic -rc")

