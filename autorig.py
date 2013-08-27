import pymel.core as py
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Function to create a controller.
# Takes in controlType (string) that is either "circle", "sphere", or "cube"
# Takes in unit size
# creates the control curve and groups it and names the objects <name>_constraint, <name>_grp, <name>_control
# returns the names of the objects it's created  

# Ah, so this is how you specify default settings for a function! Neat!
def createController(controlType="cube", size=1.0, name="controller"):
    #1. Store current selection
    try:
        target = py.selected()
        finalGroup = py.group(em=True, name=name)
    except:
        print "Nothing selected; only creating controller."

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
            controllerConstraints(target[i],ctlCst[0],ctl)      
        except:
            print "Couldn't apply controller to a selection."

    return name

#~~

def controllerConstraints(target,constraint,controller):
    py.select(target,constraint)
    #3a. snap controller to target joint location
    cst0 = py.parentConstraint(mo=0)
    py.delete(cst0)
    #3b. select parent of target joint
    mom = py.listRelatives(target,parent=True)
    if(len(mom)<1):
        print "Selection should have a parent."
        return
    py.select(mom[0],constraint)
    cst1 = py.parentConstraint(mo=1)

    py.select(controller,target)
    cst2 = py.parentConstraint(mo=0)    

#~~
    
def controllerGeometry(controlType,size,name,appendCtl):
    if(controlType=="circle"):
        ctl = py.circle(r=size/2.0, n=name + appendCtl)
        #setAttr(selected()[0] + ".rotateX",90)
    elif(controlType=="sphere"):
        ctl = py.curve(n=name + appendCtl, d=1, p=((0*(size/2.0),1*(size/2.0),0*(size/2.0)),(0*(size/2.0),0.809017*(size/2.0),-0.587785*(size/2.0)),(0*(size/2.0),0.309017*(size/2.0),-0.951057*(size/2.0)),(0*(size/2.0),-0.309017*(size/2.0),-0.951057*(size/2.0)),(0*(size/2.0),-0.809017*(size/2.0),-0.587785*(size/2.0)),(0*(size/2.0),-1*(size/2.0),5.96046e-08*(size/2.0)),(0*(size/2.0),-0.809017*(size/2.0),0.587785*(size/2.0)),(0*(size/2.0),-0.309017*(size/2.0),0.951057*(size/2.0)),(0*(size/2.0),0.309017*(size/2.0),0.951057*(size/2.0)),(0*(size/2.0),0.809017*(size/2.0),0.587785*(size/2.0)),(0*(size/2.0),1*(size/2.0),0*(size/2.0)),(0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(1*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),-0.587785*(size/2.0),0*(size/2.0)),(0.309017*(size/2.0),-0.951057*(size/2.0),0*(size/2.0)),(0*(size/2.0),-1*(size/2.0),5.96046e-08*(size/2.0)),(-0.309017*(size/2.0),-0.951057*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),-0.587785*(size/2.0),0*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(-0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(0*(size/2.0),1*(size/2.0),0*(size/2.0)),(-0.309017*(size/2.0),0.951057*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0.587785*(size/2.0),0*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0*(size/2.0)),(-0.809017*(size/2.0),0*(size/2.0),-0.587785*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(0.309017*(size/2.0),0*(size/2.0),-0.951057*(size/2.0)),(0.809017*(size/2.0),0*(size/2.0),-0.587785*(size/2.0)),(1*(size/2.0),0*(size/2.0),0*(size/2.0)),(0.809017*(size/2.0),0*(size/2.0),0.587785*(size/2.0)),(0.309017*(size/2.0),0*(size/2.0),0.951057*(size/2.0)),(-0.309017*(size/2.0),0*(size/2.0),0.951057*(size/2.0)),(-0.809017*(size/2.0),0*(size/2.0),0.587785*(size/2.0)),(-1*(size/2.0),-5.96046e-08*(size/2.0),0)), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37))
    elif(controlType=="cube"):
        ctl = py.curve(n=name + appendCtl, d=1, p=((-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19))
    else:
        print 'Nothing created; valid types are "circle", "sphere", and "cube".'
        return
    return ctl    

#~~

cc=createController