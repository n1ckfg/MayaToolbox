#AUTORIG

import pymel.core as py
import maya.cmds as mc
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os

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

def ikCreateController(controlType="cube", size=1.0, name="controller"):
    #1. Store current selection
    target = py.selected()
    finalGroup = py.group(em=True, name=name)

    appendCtl = "_control"
    appendCst = "_constraint"
    appendGrp = "_group"
    appendPole = "_pole"

    numReps = len(target)
    if(numReps<1):
        numReps=1
    for i in range(0,numReps):
        #2. Create IK handle
        py.select(target[i])
        joints = py.listRelatives(ad=True)
        joints.append(target[i])
        py.select(joints[len(joints)-1],joints[0])
        handle = py.ikHandle(solver="ikRPsolver")
        
        #3. Create controller
        ctl = controllerGeometry(controlType,size,name,appendCtl)
        ctl2 = controllerGeometry(controlType,size,name+appendPole,appendCtl)
        py.select(ctl,joints[0])
        snapToPos()
        #~~
        py.select(ctl)
        py.group(n=name + appendGrp)
        ctlGrp = py.selected()
        py.group(n=name + appendCst)
        ctlCst = py.selected()
        #~~
        py.parent(handle[0],ctlGrp[0])
        middleJoint = 0;
        jointCount = countChain(target[i])
        if(jointCount%2==0): #even joints
            middleJoint = int(jointCount/2)-1
        else: #odd joints
            middleJoint = int(jointCount/2)
        ikControllerConstraints(ctl,handle[0],ctl2,joints[middleJoint])      

        #4. Try to apply controller to original selection
        py.parent(ctlCst[0],name)
        py.parent(ctl2,name)
        
    return (name,ctlCst,ctlGrp,ctl,ctl2)

#~~

def ikControllerConstraints(constraint, target, constraint2, target2):
    #3b. select parent of target joint
    py.select(constraint, target)
    py.parentConstraint(mo=1)
    py.select(constraint2, target2)
    snapToPos()
    py.select(constraint2,target)
    py.poleVectorConstraint()
    #py.select(controller,handle)
    #cst1 = py.parentConstraint(mo=1)
    #py.select(constraint,handle)
    #cst2 = py.poleVectorConstraint()    

def countChain(target):
    returnCount = 0
    chain = py.listRelatives(target, ad=True)
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
    target = py.selected()
    finalGroup = py.group(em=True, name=name)

    appendCtl = "_control"
    appendCst = "_constraint"
    appendGrp = "_group"

    numReps = len(target)
    if(numReps<1):
        numReps=1
    for i in range(0,numReps):
        #2. Create controller
        ctl = controllerGeometry(controlType,size,name,appendCtl)

        py.group(n=name + appendGrp)
        ctlGrp = py.selected()
        py.group(n=name + appendCst)
        ctlCst = py.selected()

        #3. Try to apply controller to original selection
        try:
            py.parent(ctlCst[0],name)
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
    mom = py.listRelatives(target,parent=True)
    if(len(mom)<1):
        print "Selection should have a parent."
        return
    py.select(mom[0],constraint)
    cst1 = py.parentConstraint(mo=1)

    py.select(controller,target)
    cst2 = py.parentConstraint(mo=0)    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
def controllerGeometry(controlType,size,name,appendCtl):
    if(controlType=="circle"):
        ctl = py.circle(r=size/2.0, n=name + appendCtl)
        #setAttr(selected()[0] + ".rotateX",90)
    elif(controlType=="sphere"):
        ctl = py.curve(n=name + appendCtl, d=1, p=((0*(size/2.0),1*(size/2.0),0*(size/2.0)),(0*(size/2.0),0.809017*(size/2.0),-0.587785*(size/2.0)),(0*(size/2.0),0.309017*(size/2.0),-0.951057*(size/2.0)),(0*(size/2.0),-0.309017*(size/2.0),-0.951057*(size/2.0)),(0*(size/2.0),-0.809017*(size/2.0),-0.587785*(size/2.0)),(0*(size/2.0),-1*(size/2.0),5.96046e-08*(size/2.0)),(0*(size/2.0),-0.809017*(size/2.0),0.587785*(size/2.0)),(0*(size/2.0),-0.309017*(size/2.0),0.951057*(size/2.0)),(0*(size/2.0),0.309017*(size/2.0),0.951057*(size/2.0)),(0*(size/2.0),0.809017*(size/2.0),0.587785*(size/2.0)),(0*(size/2.0),1*(size/2.0),0*(size/2.0)),(0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(1*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),-0.587785*(size/2.0),0*(size/2.0)),(0.309017*(size/2.0),-0.951057*(size/2.0),0*(size/2.0)),(0*(size/2.0),-1*(size/2.0),5.96046e-08*(size/2.0)),(-0.309017*(size/2.0),-0.951057*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),-0.587785*(size/2.0),0*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(-0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(0*(size/2.0),1*(size/2.0),0*(size/2.0)),(-0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0*(size/2.0),-0.587785*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(0.809017*(size/2.0),0*(size/2.0),-0.587785*(size/2.0)),(1*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),0*(size/2.0),0.587785*(size/2.0)),(0.309017*(size/2.0),0*(size/2.0),0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),0.951057*(size/2.0)),(-0.809017*(size/2.0),0*(size/2.0),0.587785*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0)), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37))
    elif(controlType=="star"):
        ctl = py.curve(n=name + appendCtl, d=1, p=((-0.849836*(size/2.0),0*(size/2.0),-0.849836*(size/2.0)),(-0.79687*(size/2.0),0*(size/2.0),-0.330074*(size/2.0)),(-1.20185*(size/2.0),0*(size/2.0),0*(size/2.0)),(-0.79687*(size/2.0),0*(size/2.0),0.330074*(size/2.0)),(-0.849836*(size/2.0),0*(size/2.0),0.849836*(size/2.0)),(-0.330074*(size/2.0),0*(size/2.0),0.79687*(size/2.0)),(0*(size/2.0),0*(size/2.0),1.20185*(size/2.0)),(0.330074*(size/2.0),0*(size/2.0),0.79687*(size/2.0)),(0.849836*(size/2.0),0*(size/2.0),0.849836*(size/2.0)),(0.801233*(size/2.0),0*(size/2.0),0.326518*(size/2.0)),(1.20185*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.801233*(size/2.0),0*(size/2.0),-0.326518*(size/2.0)),(0.849836*(size/2.0),0*(size/2.0),-0.849836*(size/2.0)),(0.326518*(size/2.0),0*(size/2.0),-0.801233*(size/2.0)),(0*(size/2.0),0*(size/2.0),-1.20185*(size/2.0)),(-0.333798*(size/2.0),0*(size/2.0),-0.801604*(size/2.0)),(-0.857352*(size/2.0),0*(size/2.0),-0.865126*(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16))
    elif(controlType=="cube"):
        ctl = py.curve(n=name + appendCtl, d=1, p=((-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19))
    else:
        print 'Nothing created; valid types are "circle", "sphere", "star", and "cube".'
        return
    return ctl    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def snapToPos():
    s = py.selected()
    for i in range(0,len(s)-1):
        py.select(s[len(s)-1],s[i])
        cst0 = py.parentConstraint(mo=0)
        py.delete(cst0)    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


cc=fkCreateController
ccfk=fkCreateController
ccik=ikCreateController
