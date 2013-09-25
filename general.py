# GENERAL

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
import re
#~~

#select
def s(_t=None,d=False,all=False):
    if(d==True):
        py.select(d=True)
    elif(all==True):
        py.select(all=True)
    else:
        if not _t:
            try:
                py.select(py.ls(sl=1))
            except:
                print("Nothing selected.")
            return(py.ls(sl=1))
        else:
            py.select(_t)
            return _t
#time
def t(_t=None):
    try:
        mc.currentTime(_t)
    except:
        print "time: " + str(mc.currentTime(q=True))
    return mc.currentTime(q=True)

#delete
def d(_t=None, all=False):
    if _t:
        s(_t)
    if all:
        s(all=True)
    py.delete()

#delete all
def rm():
    d(all=True)

#move
def m(p, _t=None):
    if not _t:
        _t = mc.ls(sl=1)

    for i in range (0,len(_t)):
        mc.select(_t[i])
        mc.move(p[0],p[1],p[2])

#keyframe
def k(_t=None):
    if(_t):
        mc.select(_t)
    mc.setKeyframe()

#group
def g(_t=None):
    if not _t:
        _t = mc.ls(sl=1)
    obj = mc.group(_t)
    return obj

def listAll(target=None):
    allJoints = []
    if not target:
        target = s()
    if(len(target)==1):
        allJoints = mc.listRelatives(ad=1)
        allJoints.append(target[0])        
    else:
        for i in range(0,len(target)):
            joints = mc.listRelatives(ad=1)
            joints.append(target[i])
            allJoints.append(joints)
        
    print allJoints
    return allJoints

def posAll(target=None):
    pos = []
    
    if not target:
        target = s()
    
    obj = listAll()
    
    for i in range(0,len(obj)):
        p = getPos([obj[i]])
        pos.append(p[0])
        
    print pos
    return pos

#random 3d vector
def rnd3d(spread=5):
    return [rnd(-spread,spread),rnd(-spread,spread),rnd(-spread,spread)]

#move to random location
def rndMove(spread=5):
    val = rnd3d(spread)
    mc.move(val[0],val[1],val[2])

#get position
def getPos(target=None):
    returns = []
    if not target:
        target = s()
    
    for i in range(0,len(target)):
        p = py.xform(target[i], q=True, t=True, ws=True)
        returns.append(p)
    return returns

#move to last object
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

#toggle visibility
def showHide(target=None):
    if not target:
       target = mc.ls(sl=1)

    for i in range(0,len(target)):
        visible = mc.getAttr(target[i] + ".v")
        if(visible==False):
           mc.setAttr(target[i] + ".v",1)
        if(visible==True):
           mc.setAttr(target[i] + ".v",0) 

#toggle selectability
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

#reset transformations to 0
def freezeTransformations(target=None):
    if not target:
        target = mc.ls(sl=1)
    mc.select(target)
    mel.eval("makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;")
    return target
#~~

#parent to last selection
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


def duplicateSpecial(target = None, name = None):
    returns = []

    #1. make an array of all selected objects
    if not target:
        target = mc.ls(sl=1)

    #2. for each selected object...
    for i in range(0,len(target)):
        #3. ...select and duplicated with bones and keyframes
        mc.select(target[i])
        #call through mel because python has no rc option!
        if not name:
            val = mel.eval("duplicate -un -ic -rc")
        else:
            val = mel.eval("duplicate -un -ic -rc -name \"" + name + "\"")
        returns.append(val)

    return returns[0] #why is returns an array inside an array?

# by David Bokser davidbokser.com
def getUniqueName(name):
    # if the name is already unique, return it
    if not mc.ls(name):
        return name
    else:
        # find the trailing digit in the name
        trailingDigit = re.sub('.*?([0-9]*)$',r'\1',name)
        
        # create default variables for newDigit and shortname
        # in case there is no trailing digit (ie: "pSphere")
        newDigit = 1
        shortname = name
        
        if(trailingDigit):
            # increment the last digit and find the shortname using the length
            # of the trailing digit as a reference for how much to trim
            newDigit = int(trailingDigit)+1
            shortname = name[:-len(trailingDigit)]
        
        # create the new name
        newName = shortname+str(newDigit)

        # recursively run through the function until a unique name is reached and returned
        return getUniqueName(newName)

def lookAt(target=None):
    if not target:
        target = mc.ls(sl=1)

    angleBtwnNode = angleBetween(v1=(1, 0, 0), v2=(1, 0, 0), ch=True)

    mc.connectAttr( target[len(target)-1]+'.translateX', angleBtwnNode+'.vector2X' )
    mc.connectAttr( target[len(target)-1]+'.translateY', angleBtwnNode+'.vector2Y' )
    mc.connectAttr( target[len(target)-1]+'.translateZ', angleBtwnNode+'.vector2Z' )

    for i in range(0,len(target)-1):

        convertX = mc.createNode( 'unitConversion' )
        mc.connectAttr( angleBtwnNode+'.eulerX', convertX+'.input' )
        mc.connectAttr( convertX+'.output', target[i]+'.rotateX' )

        convertY = mc.createNode( 'unitConversion' )
        mc.connectAttr( angleBtwnNode+'.eulerY', convertY+'.input' )
        mc.connectAttr( convertY+'.output', target[i]+'.rotateY' )

        convertZ = mc.createNode( 'unitConversion' )
        mc.connectAttr( angleBtwnNode+'.eulerZ', convertZ+'.input' )
        mc.connectAttr( convertZ+'.output', target[i]+'.rotateZ' )


