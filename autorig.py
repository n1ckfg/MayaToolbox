#AUTORIG

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
#~~
from general import *

# Write a function that will automatically create an IK setup, given a list of joints
# 
# 1. Assume joints are oriented correctly
# 2. Function should return base IK joint, control curves
# 3. Process:
#   3.1. Create ikHandle from base joint to end joint
#   3.2. Create cube control curve
#   3.3. snap controller_constraint to end joint
#   3.4. parent ikHandle to control curve
#   3.5. create pole vector controller (see constrain menu)
#   3.6. snap pole vector controller to middle joint *
#   3.7. create pole vector constraint to ikHandle
#   3.8. clean up all created objects into separate group
# 4. def createIKControls(startJoint, endJoint)
# 5. return [group, IK Controller, Pole Vector, IK Chain Base]
# 
# * Make the middle snap to the middle joint in any number of arbitrary joints. If there is an even number, 
# just pick the lowest of the 2 half joints. (ie: 3 joints, pole on 2nd, 4 joints - pole vector on 2nd. 
# 5 joints - pole vector on 3rd, 6 joints - pole on 3rd, etc.)

def ikCreateController(startJoint=None, endJoint=None, controlType="cube", size=1.0, name="controller"):
    #1. Store current selection
    target = mc.ls(sl=1)
    finalGroup = mc.group(em=True, name=name)

    appendCtl = "_control"
    appendCst = "_constraint"
    appendGrp = "_group"
    appendPole = "_pole"

    numReps = len(target)
    if(numReps<1):
        numReps=1
    for i in range(0,numReps):
        joints = []
        #2. Create IK handle
        if not startJoint or not endJoint:
            mc.select(target[i])
            joints = mc.listRelatives(ad=True)
            joints.append(target[i])
            mc.select(joints[len(joints)-1],joints[0])
        else:
            mc.select(startJoint)
            joints = mc.listRelatives(ad=True)
            joints.append(startJoint)
            mc.select(startJoint,endJoint)

        handle = mc.ikHandle(solver="ikRPsolver")
        
        #3. Create controller
        ctl = controllerGeometry(controlType,size,name,appendCtl)
        ctl2 = controllerGeometry("sphere",size,name+appendPole,appendCtl)
        
        if not startJoint or not endJoint:
            mc.select(ctl,joints[0])
        else:
            mc.select(ctl,endJoint)

        snapToPos()
        #~~
        mc.select(ctl)
        mc.group(n=name + appendGrp)
        ctlGrp = mc.ls(sl=1)
        mc.group(n=name + appendCst)
        ctlCst = mc.ls(sl=1)
        #~~
        mc.parent(handle[0],ctlGrp[0])
        middleJoint = 0;
        if not startJoint or not endJoint:
            jointCount = countChain(target[i])
        else:
            jointCount = countChain(startJoint) - countChain(endJoint)
        if(jointCount%2==0): #even joints
            middleJoint = int(jointCount/2)-1
        else: #odd joints
            middleJoint = int(jointCount/2)
        
        if not startJoint or not endJoint:
            ikControllerConstraints(ctl,handle[0],ctl2,joints[middleJoint])      
        else:
            ikControllerConstraints(ctl,handle[0],ctl2,joints[middleJoint-countChain(endJoint)])      

        #4. Try to apply controller to original selection
        mc.parent(ctlCst[0],name)
        mc.parent(ctl2,name)
        
    return (name,ctlCst,ctlGrp,ctl,ctl2)

#~~

def ikControllerConstraints(constraint, target, constraint2, target2):
    #3b. select parent of target joint
    mc.select(constraint, target)
    mc.parentConstraint(mo=1)
    mc.select(constraint2, target2)
    snapToPos()
    mc.select(constraint2,target)
    mc.poleVectorConstraint()
    #mc.select(controller,handle)
    #cst1 = mc.parentConstraint(mo=1)
    #mc.select(constraint,handle)
    #cst2 = mc.poleVectorConstraint()    

def countChain(target):
    returnCount = 0
    chain = mc.listRelatives(target, ad=True)
    returnCount = len(chain)
    print returnCount
    return(returnCount)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Function to create an fk controller.
# Takes in controlType (string) that is either "circle", "sphere", or "cube"
# Takes in unit size
# creates the control curve and groups it and names the objects <name>_constraint, <name>_grp, <name>_control
# returns the names of the objects it's created  

def fkCreateController(controlType="cube", size=1.0, name="controller"):
    #1. Store current selection
    target = mc.ls(sl=1)
    finalGroup = mc.group(em=True, name=name)

    appendCtl = "_control"
    appendCst = "_constraint"
    appendGrp = "_group"

    numReps = len(target)
    if(numReps<1):
        numReps=1
    for i in range(0,numReps):
        #2. Create controller
        ctl = controllerGeometry(controlType,size,name,appendCtl)

        mc.group(n=name + appendGrp)
        ctlGrp = mc.ls(sl=1)
        mc.group(n=name + appendCst)
        ctlCst = mc.ls(sl=1)

        #3. Try to apply controller to original selection
        try:
            mc.parent(ctlCst[0],name)
            fkControllerConstraints(target[i],ctlCst[0],ctl)      
        except:
            print "Couldn't apply controller to a selection."

    return (name,ctlCst,ctlGrp,ctl)

#~~

def fkControllerConstraints(target,constraint,controller):
    #3a. snap controller to target joint location
    select(constraint,target)
    snapToPos()
    #3b. select parent of target joint
    mom = mc.listRelatives(target,parent=True)
    if(len(mom)<1):
        print "Selection should have a parent."
        return
    mc.select(mom[0],constraint)
    cst1 = mc.parentConstraint(mo=1)

    mc.select(controller,target)
    cst2 = mc.parentConstraint(mo=0)    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
def controllerGeometry(controlType,size,name,appendCtl):
    if(controlType=="circle"):
        ctl = mc.circle(r=size/2.0, n=name + appendCtl)
        #setAttr(ls(sl=1)[0] + ".rotateX",90)
    elif(controlType=="sphere"):
        ctl = mc.curve(n=name + appendCtl, d=1, p=((0*(size/2.0),1*(size/2.0),0*(size/2.0)),(0*(size/2.0),0.809017*(size/2.0),-0.587785*(size/2.0)),(0*(size/2.0),0.309017*(size/2.0),-0.951057*(size/2.0)),(0*(size/2.0),-0.309017*(size/2.0),-0.951057*(size/2.0)),(0*(size/2.0),-0.809017*(size/2.0),-0.587785*(size/2.0)),(0*(size/2.0),-1*(size/2.0),5.96046e-08*(size/2.0)),(0*(size/2.0),-0.809017*(size/2.0),0.587785*(size/2.0)),(0*(size/2.0),-0.309017*(size/2.0),0.951057*(size/2.0)),(0*(size/2.0),0.309017*(size/2.0),0.951057*(size/2.0)),(0*(size/2.0),0.809017*(size/2.0),0.587785*(size/2.0)),(0*(size/2.0),1*(size/2.0),0*(size/2.0)),(0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(1*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),-0.587785*(size/2.0),0*(size/2.0)),(0.309017*(size/2.0),-0.951057*(size/2.0),0*(size/2.0)),(0*(size/2.0),-1*(size/2.0),5.96046e-08*(size/2.0)),(-0.309017*(size/2.0),-0.951057*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),-0.587785*(size/2.0),0*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(-0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(0*(size/2.0),1*(size/2.0),0*(size/2.0)),(-0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0*(size/2.0),-0.587785*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(0.809017*(size/2.0),0*(size/2.0),-0.587785*(size/2.0)),(1*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),0*(size/2.0),0.587785*(size/2.0)),(0.309017*(size/2.0),0*(size/2.0),0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),0.951057*(size/2.0)),(-0.809017*(size/2.0),0*(size/2.0),0.587785*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0)), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37))
    elif(controlType=="star"):
        ctl = mc.curve(n=name + appendCtl, d=1, p=((-0.849836*(size/2.0),0*(size/2.0),-0.849836*(size/2.0)),(-0.79687*(size/2.0),0*(size/2.0),-0.330074*(size/2.0)),(-1.20185*(size/2.0),0*(size/2.0),0*(size/2.0)),(-0.79687*(size/2.0),0*(size/2.0),0.330074*(size/2.0)),(-0.849836*(size/2.0),0*(size/2.0),0.849836*(size/2.0)),(-0.330074*(size/2.0),0*(size/2.0),0.79687*(size/2.0)),(0*(size/2.0),0*(size/2.0),1.20185*(size/2.0)),(0.330074*(size/2.0),0*(size/2.0),0.79687*(size/2.0)),(0.849836*(size/2.0),0*(size/2.0),0.849836*(size/2.0)),(0.801233*(size/2.0),0*(size/2.0),0.326518*(size/2.0)),(1.20185*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.801233*(size/2.0),0*(size/2.0),-0.326518*(size/2.0)),(0.849836*(size/2.0),0*(size/2.0),-0.849836*(size/2.0)),(0.326518*(size/2.0),0*(size/2.0),-0.801233*(size/2.0)),(0*(size/2.0),0*(size/2.0),-1.20185*(size/2.0)),(-0.333798*(size/2.0),0*(size/2.0),-0.801604*(size/2.0)),(-0.857352*(size/2.0),0*(size/2.0),-0.865126*(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16))
    elif(controlType=="cube"):
        ctl = mc.curve(n=name + appendCtl, d=1, p=((-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19))
    else:
        print 'Nothing created; valid types are "circle", "sphere", "star", and "cube".'
        return
    return ctl    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def snapToPos():
    s = mc.ls(sl=1)
    for i in range(0,len(s)-1):
        mc.select(s[len(s)-1],s[i])
        cst0 = mc.parentConstraint(mo=0)
        mc.delete(cst0)    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ccfk=fkCreateController
ccik=ikCreateController
