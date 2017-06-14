# MOCAP

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
from animation import *

def buildFromLocators():
    looseJoints()
    #~~
    s(["r_hip","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["r_knee","r_hip_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["r_foot","r_knee_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["l_hip","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["l_knee","l_hip_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["l_foot","l_knee_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["r_shoulder","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["r_elbow","r_shoulder_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["r_hand","r_elbow_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["l_shoulder","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["l_elbow","l_shoulder_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["l_hand","l_elbow_jnt"])
    py.aimConstraint(wut="none", mo=True)
    #~~
    s(["neck","torso_jnt"])
    py.aimConstraint(wut="none", mo=True)
    s(["head","neck_jnt"])
    py.aimConstraint(wut="none", mo=True)
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
    s(["torso","torso_jnt"])
    py.parentConstraint()
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
    fileName = openFileDialog("xml")
    joints = ["l_foot","l_knee","l_hip","r_foot","r_knee","r_hip","l_hand","l_elbow","l_shoulder","r_hand","r_elbow","r_shoulder","torso","neck","head"]
    globalScale = (10, -10, 10)

    xmlFile = xd.parse(fileName)
    print("loaded: " + fileName)

    for joint in joints:    
        s(d=True)
        frames = xmlFile.getElementsByTagName(joint)
        loc = addLocator()
        mc.rename(loc, joint)

        for i, frame in enumerate(frames):
            x = float(frame.getAttribute("x")) * globalScale[0]
            y = float(frame.getAttribute("y")) * globalScale[1]
            z = float(frame.getAttribute("z")) * globalScale[2]
            
            mc.currentTime(i)
            mc.move(x, y, z)
            k()

    s(joints)
    buildFromLocators()


