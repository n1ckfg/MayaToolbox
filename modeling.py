# MODELING

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

def getVerts(target=None):
    if not target:
        target = s()[0]
    return mc.getAttr(target + ".vrts", multiIndices=True)

def selectVerts(target=None):
    if not target:
        target = s()[0]
    py.select(target.vtx)

def fixAlembicColors(filePath=None):
    if not filePath:
        filePath = openFileDialog("abc")
    mel.eval("AbcImport -mode import -rcs 3fc \"" + filePath + "\";")

def fixNormals(target=None):
    if not target:
        target = s()

    for i in range(0,len(target)):
        s(target[i])
        py.polySetToFaceNormal()
        py.polySoftEdge()

def eroder(repeat=1, iter=1):
    for i in range(0,repeat):
        mc.polyAverageVertex(i=iter)
        ch()

def onVerts(target=None, normals=True, type="vector"):
    #1. make an array of all selected objects
    if not target:
        target = mc.ls(sl=1)

    #2. get the first selected object so it can be copied...
    foo = target[0]

    #3. then get the vertices of each other object and copy the first one there.
    for i in range(1,len(target)):

        v = getVertPos(target[i])
            
        for j in range(0,len(v)):
            s(foo)
            foo2 = py.duplicate()
            mc.move(v[j][0],v[j][1],v[j][2])

            if(normals==True):
                py.mel.eval("select -r " + target[i] + ".vtx[" + str(j) +"] " + foo2[0] + ";")
                py.normalConstraint(worldUpType=type)

            '''
            else:
            s(foo)
            py.mel.eval("duplicate -un -ic -rc")
            mc.move(v[j][0],v[j][1],v[j][2])
            '''
            
def getVertPos( shapeNode ) :
    vtxWorldPosition = []    # will contain positions in space of all object vertices
    vtxIndexList = mc.getAttr( shapeNode+".vrts", multiIndices=True )
 
    for i in vtxIndexList :
        curPointPosition = mc.xform( str(shapeNode)+".pnts["+str(i)+"]", query=True, translation=True, worldSpace=True )    # [1.1269192869360154, 4.5408735275268555, 1.3387055339628269]
        vtxWorldPosition.append( curPointPosition )
 
    return vtxWorldPosition

#from Sam Lavigne
def moveVerts(target=None, spread=1, time=1):
    if not target:
        target = s()

    for i in range(0,len(target)):
        # iterate through every vertex in the sphere           
        index = 1
        for v in target[i].vtx:
            # set initial position
            if(time > 1):
                py.setKeyframe(v, t=1)
            original = v.getPosition()

            # make a new position
            new_pos = [p + rnd(-spread, spread) for p in original]
            v.setPosition(new_pos)
            
            if(time > 1):
                py.setKeyframe(v, t=index)
            
            if(time > 1):
                v.setPosition(original)
                py.setKeyframe(v, t=index+time)
            
            index += 1


def text(t = "foo", font="Droid Sans", hipoly = False, cleanup = True):
    #note: hipoly mode seems to generate a couple weird extra vertices in the final output.
    obj1 = mc.textCurves( f=font,t=t)
    obj2 = mc.planarSrf(obj1)
    if hipoly:
        obj3 = nurbsToPoly()
    else:
        obj3 = mel.eval("nurbsToPoly -mnd 1  -ch 1 -f 1 -pt 1 -pc 500 -chr 0.9 -ft 0.7787 -mel 1 -d 0.196 -ut 1 -un 3 -vt 1 -vn 3 -uch 0 -ucr 0 -cht 0.01 -es 0 -ntr 0 -mrt 0 -uss 1 \"" + obj2[0] + "\";")
    if cleanup:
        d([obj1,obj2])
        mc.xform(obj3[0], cp=True)
    return obj3

def puppetMesh(target=None):
    returns = []
    
    if not target:
        target = mc.ls(sl=1)
    
    for i in range(0,len(target)):    
        obj = mel.eval("planarSrf -ch 1 -d 3 -ko 0 -tol 0 -rn 0 -po 1 \""+target[i]+"\";")
        #delete history, recenter the pivot
        mc.delete(ch=True)
        mc.xform(cp=True)
 
        returns.append(obj)
        
    return returns

def iteratePolyToSubdiv(target=None,polys=1000,reps=1000,delete=False):
    
    counter = 0
    initPolyCount = polys
    currentPolyCount = initPolyCount
    finished = False
    
    if not target:
        target = mc.ls(sl=1)

    for i in range(0,len(target)):
            while(finished==False and counter < reps):
                try:
                    finished=True
                    mc.polyToSubdiv(target[i], maxPolyCount=currentPolyCount)

                except:
                    finished=False
                    counter+=1
                    currentPolyCount += initPolyCount
                    print "Failed using " + str(currentPolyCount - initPolyCount) + " polys; trying " + str(currentPolyCount) + " polys."
            if(finished==True):
                if(delete==True):
                    mc.delete(constructionHistory=True) # prevents deletion of polys from wrecking subdivs
                    mc.delete(target[i])
                print "Successfully converted " + str(target[i]) + " using < " + str(currentPolyCount) + " polys in " + str(counter+1) + " tries."
            else:
                print "Failed to convert " + str(target[i]) + " using < " + str(currentPolyCount) + " polys in " + str(counter+1) + " tries."


def booleanLoop(legacy=False):
    #1. Make an array of all selections
    target = mc.ls(sl=1)

    if (legacy):
        #2. Boolean union each item in the array to the next
        for i in range(0,len(target)-1,2):
            mc.polyBoolOp(target[i],target[i+1])
            
            #3. Delete construction history
            mc.delete(ch=True)

            #4. Recenter the pivot
            mc.xform(cp=True)
    else:
        mc.polyCBoolOp()
        mc.delete(ch=True)

def cubes(num=100,spread=5):
    val = []
    for i in range(0, num):
        obj = mc.polyCube()
        val.append(obj)
        k()
        t(48)
        rndMove(spread)
        k()
        t(0)
    return val

def curveAB(target=None, type="line", fill=False):
    returns = []
    if not target:
        target = s()

    p = getPos(target)

    for i in range(0,len(target)):
        if(type=="line"):
            if(i<len(target)-1):
                ctl = makeLine(p[i],p[i+1])
        elif(type=="star"):
            if(i<len(target)-1):
                ctl = makeLine(p[i],p[len(target)-1])
        elif(type=="circle"):
            if(i<len(target)-1):
                ctl = makeLine(p[i],p[i+1])
            else:
                ctl = makeLine(p[i],p[0])
        if(fill==True):
            ctl2 = curveSurface()
            d(ctl)
            returns.append(ctl2)
        else:
            returns.append(ctl)

    return returns

def curveSurface():
    returns = []
    target = s()
    
    for i in range(0,len(target)):
        ctl = py.revolve(target[i], ch=1, po=1, rn=1, ssw=0, esw=3, ut=1, tol=0, degree=3, s=8, ulp=1, ax=(1,0,0))
        returns.append(ctl)

    return returns

def makeLine(p1=[-2,0,0], p2=[2,0,0], name="curve"):
    name = getUniqueName(name)
    ctl = mc.curve(n=name, d=1, p=(p1,p2), k=(0,1))
    return ctl

def drawPoints(points=None, name="curve", uniqueName=True):
    if (uniqueName==True):
        name = getUniqueName(name)
    crv = mc.curve(n=name, d=1, p=points)
    return crv
    
def smoothMesh(target=None):
    if not target:
        target = s()
    
    polysOnly = py.filterExpand(target, sm=12)
    py.select(polysOnly, r=True)

    for i in range(0,len(target)):
        try:
            py.mel.eval("polySmooth -mth 0 -dv 1 -bnr 2 -c 1 -kb 1 -ksb 1 -khe 0 -kt 1 -kmb 1 -suv 0 -peh 0 -sl 1 -dpe 1 -ps 0.1 -ro 1 -ch 1 " + target[i] + ";")    
            py.mel.eval("BakeAllNonDefHistory;")
            py.mel.eval("bakePartialHistory -all;")
        except:
            print "Smooth failed; " + target[i] + " probably isn't a polygonal mesh."