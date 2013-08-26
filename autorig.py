from pymel.core import *
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
        target = selected()
    except:
        print "Nothing selected; only creating controller."

    #2. Create controller
    appendCtl = "_control"
    appendCst = "_constraint"
    appendGrp = "_group"

    if(controlType=="circle"):
        ctl = circle(r=size, n=name + appendCtl)
        #setAttr(selected()[0] + ".rotateX",90)
    elif(controlType=="sphere"):
        ctl = curve(n=name + appendCtl, d=1, p=((0*size,1*size,0*size),(0*size,0.809017*size,-0.587785*size),(0*size,0.309017*size,-0.951057*size),(0*size,-0.309017*size,-0.951057*size),(0*size,-0.809017*size,-0.587785*size),(0*size,-1*size,5.96046e-08*size),(0*size,-0.809017*size,0.587785*size),(0*size,-0.309017*size,0.951057*size),(0*size,0.309017*size,0.951057*size),(0*size,0.809017*size,0.587785*size),(0*size,1*size,0*size),(0.309017*size,0.951057*size,0*size),(0.809017*size,0.587785*size,0*size),(1*size,0*size,0*size),(0.809017*size,-0.587785*size,0*size),(0.309017*size,-0.951057*size,0*size),(0*size,-1*size,5.96046e-08*size),(-0.309017*size,-0.951057*size,0*size),(-0.809017*size,-0.587785*size,0*size),(-1*size,-5.96046e-08*size,0*size),(-0.809017*size,0.587785*size,0*size),(-0.309017*size,0.951057*size,0*size),(0*size,1*size,0*size),(-0.309017*size,0.951057*size,0*size),(-0.809017*size,0.587785*size,0*size),(-1*size,-5.96046e-08*size,0*size),(-0.809017*size,0*size,-0.587785*size),(-0.309017*size,0*size,-0.951057*size),(-0.309017*size,0*size,-0.951057*size),(-0.309017*size,0*size,-0.951057*size),(0.309017*size,0*size,-0.951057*size),(0.809017*size,0*size,-0.587785*size),(1*size,0*size,0*size),(0.809017*size,0*size,0.587785*size),(0.309017*size,0*size,0.951057*size),(-0.309017*size,0*size,0.951057*size),(-0.809017*size,0*size,0.587785*size),(-1*size,-5.96046e-08*size,0)), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37))
    elif(controlType=="cube"):
        ctl = curve(n=name + appendCtl, d=1, p=((-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19))
    else:
        print("Valid types are \"circle\", \"sphere\", and \"cube\".")

    group(n=name + appendGrp)
    group(n=name + appendCst)
    ctlCst = selected()

    #3. Try to apply controller to original selection
    try:
        select(target[0],ctlCst[0])
        #3a. snap controller to target joint location
        cst0 = parentConstraint(mo=0)
        delete(cst0)
        #3b. select parent of target joint
        mom = listRelatives(target[0],parent=True)
        select(mom[0],ctlCst[0])
        cst1 = parentConstraint(mo=1)

        select(ctl,target[0])
        cst2 = parentConstraint(mo=0)

    except:
        print "Couldn't apply controller to selection."

cc=createController