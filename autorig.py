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
    appendCtl = "_ctl"
    appendCst = "_cst"
    appendGrp = "_grp"

    if(controlType=="circle"):
        circle(r=size, n=name + appendCtl)
        setAttr(selected()[0] + ".rotateX",90)
    elif(controlType=="sphere"):
        createNode("renderSphere")
        rename(selected(), name + appendCtl)
        setAttr(selected()[0]+".radius",size)
    elif(controlType=="cube"):
        curve(n=str(name) + str(appendCtl), d=1, p=((-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),-(size/2.0)),((size/2.0),(size/2.0),(size/2.0)),((size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),((size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),-(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),-(size/2.0)),(-(size/2.0),(size/2.0),(size/2.0)),(-(size/2.0),-(size/2.0),(size/2.0))), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19))
        
    else:
        print("Valid types are \"circle\", \"sphere\", and \"cube\".")

cc=createController