# XML

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
from joints import *

def buildFromLocators():
    looseJoints()
    #~~
    s(["torso","torso_jnt"])
    py.pointConstraint()
    #~~
    s(["r_hip","torso_jnt"])
    py.aimConstraint()
    s(["r_knee","r_hip_jnt"])
    py.aimConstraint()
    s(["r_foot","r_knee_jnt"])
    py.aimConstraint()
    #~~
    s(["l_hip","torso_jnt"])
    py.aimConstraint()
    s(["l_knee","l_hip_jnt"])
    py.aimConstraint()
    s(["l_foot","l_knee_jnt"])
    py.aimConstraint()
    #~~
    s(["r_shoulder","torso_jnt"])
    py.aimConstraint()
    s(["r_elbow","r_shoulder_jnt"])
    py.aimConstraint()
    s(["r_hand","r_elbow_jnt"])
    py.aimConstraint()
    #~~
    s(["l_shoulder","torso_jnt"])
    py.aimConstraint()
    s(["l_elbow","l_shoulder_jnt"])
    py.aimConstraint()
    s(["l_hand","l_elbow_jnt"])
    py.aimConstraint()
    #~~
    s(["neck","torso_jnt"])
    py.aimConstraint()
    s(["head","neck_jnt"])
    py.aimConstraint()
    #~~
    s(["torso_jnt","r_shoulder_jnt","r_elbow_jnt","r_hand_jnt"])
    parentChain()
    s(["torso_jnt","l_shoulder_jnt","l_elbow_jnt","l_hand_jnt"])
    parentChain()
    s(["torso_jnt","r_hip_jnt","r_knee_jnt","r_foot_jnt"])
    parentChain()
    s(["torso_jnt","l_hip_jnt","l_knee_jnt","l_foot_jnt"])
    parentChain()
    s(["torso_jnt","neck_jnt","head_jnt"])
    parentChain()
    #~~
    t = s("torso_jnt")
    tt = listAll()
    for i in range(0,len(tt)):
        s(tt[i])
        bakeKeys(iT=inTime(), oT=outTime())
    for i in range(0,len(tt)):
        py.delete(cn=True)
        

# Warning--cut-and-paste from other stuff, not cleaned up yet.
# http://eat3d.com/free/maya_python

# build XML
def writeK2P():
    startTime = int(mc.playbackOptions(query=True, minTime=True))
    stopTime = int(mc.playbackOptions(query=True, maxTime=True))
    filePath = "/Users/nick/Desktop/"
    fileName = "doc.xml"

    openniNames = ["head", "neck", "torso", "l_shoulder", "l_elbow", "l_hand", "r_shoulder", "r_elbow", "r_hand", "l_hip", "l_knee", "l_foot", "r_hip", "r_knee", "r_foot"]
    cmuNames = ["Head", "Neck1", "Spine", "LeftArm", "LeftForeArm", "LeftFingerBase", "RightArm", "RightForeArm", "RightFingerBase", "LeftUpLeg", "LeftLeg", "LeftToeBase", "RightUpLeg", "RightLeg", "RightToeBase"]
    mobuNames = ["Head", "Neck", "Spine", "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"]

    doc = Document()

    root_node = doc.createElement("MotionCapture")
    doc.appendChild(root_node)
    root_node.setAttribute("width", "640")
    root_node.setAttribute("height", "480")
    root_node.setAttribute("depth", "200")
    root_node.setAttribute("dialogueFile", "none")
    root_node.setAttribute("fps", "24")
    root_node.setAttribute("numFrames", str(stopTime))

    for i in range(startTime, stopTime+1):
        print str(startTime) + " " + str(stopTime)
        mc.currentTime(i)
        frame_node = doc.createElement("MocapFrame")
        root_node.appendChild(frame_node)
        frame_node.setAttribute("index",str(i-1))

        skel_node = doc.createElement("Skeleton")
        frame_node.appendChild(skel_node)
        skel_node.setAttribute("id","0")

        joint_node = doc.createElement("Joints")
        skel_node.appendChild(joint_node)

        target = py.selected()
        print target

        joints = py.listRelatives(target[0], ad=True)
        joints.append(target[0])
        print "~~~~~     " + str(joints) + "     ~~~~~"

        for j in range(0,len(joints)):
            try:
                theJointName = str(joints[j])
                for k in range(0,len(openniNames)):
                    if(theJointName==cmuNames[k] or theJointName==mobuNames[k]):
                        theJointName=openniNames[k]

                k_node = doc.createElement(theJointName)
                joint_node.appendChild(k_node)

                p = py.xform(joints[j], q=True, t=True, ws=True)
                k_node.setAttribute("x", str(-1 * p[0]))
                k_node.setAttribute("y", str(-1 * p[1]))
                k_node.setAttribute("z", str(p[2]))
            except:
                print "Couldn't get joint position."

    xml_file = open(filePath + fileName, "w")
    xml_file.write(doc.toprettyxml())
    xml_file.close()

    print doc.toprettyxml()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import xml.dom.minidom as xd

def readK2P():
    mc.constructionHistory(toggle=False)
    mc.select(all=True)
    mc.delete()

    counterMin = 1;
    counter=counterMin;
    counterMax = 200;
    mc.playbackOptions(minTime=counterMin, maxTime=counterMax)

    skipCounterMin = 1;
    skipCounter=skipCounterMin;
    skipCounterMax = 6;


    path = "/Users/nick/Development/Maya/readxml"
    fileName = "mocapData1.xml"
    #trackPoint = ["l_foot","l_knee","l_hip","r_foot","r_knee","r_hip","l_hand","l_elbow","l_shoulder","r_hand","r_elbow","r_shoulder","torso","neck","head"]
    trackPoint = ["head"]
    scaler = 10
    grav = mc.gravity()

    xmlFile = xd.parse(path + "/" + fileName)
    print("loaded: " + fileName)

    for t in trackPoint:    
        joint = xmlFile.getElementsByTagName(t)
        jointCounter = 0;
        cubeName = t
        #mergeName = t + "Merge"

        for j in joint:
            counter=counterMin;
            x = scaler * float(j.getAttribute("x"))
            y = scaler * float(j.getAttribute("y"))
            z = scaler * float(j.getAttribute("z"))
            
            if(x!=0 and y!=0 and z!=0):
                mc.currentTime(counter)
                counter+=1
                if(skipCounter<skipCounterMax):
                    jointCounter+=1
                    mc.polyCube(name=cubeName+str(counter))
                    #polyCube(sx=2, sy=2, sz=2, name=cubeName+str(counter))
                    #polySmooth(dv=1)
                    mc.connectDynamic(f=grav) #adds gravity
                    mc.move(x, y, z)
                    mc.rotate(rnd.uniform(-1 * scaler, scaler),rnd.uniform(-1 * scaler, scaler),rnd.uniform(-1 * scaler, scaler))
                    skipCounter+=1
                else:
                    skipCounter=skipCounterMin

        print("cubes made: " + str(jointCounter))
        
        #select(all=True)
        #polyUnite(constructionHistory=False) #1=union, 2=difference, 3=intersection

    floor = mc.polyPlane(w=30,h=30)
    mc.rigidBody(passive=True)
    mc.move(0,0,0)

    print("...script complete.")


