# MODELING

import pymel.core as py
import maya.cmds as mc
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
#~~
from general import *

def booleanLoop():
    #1. Make an array of all selections
    target = mc.ls(sl=1)

    #2. Boolean union each item in the array to the next
    for i in range(0,len(target)-1,2):
        mc.polyBoolOp(target[i],target[i+1])
        
        #3. Delete construction history
        mc.delete(ch=True)

        #4. Recenter the pivot
        mc.xform(cp=True)
