# PAINT EFFECTS

import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
import xml.etree.ElementTree as etree
from random import uniform as rnd
import os
import re
#~~
from mayatoolbox import *
from modeling import *

def lightningStar(target=None):
    if not target:
        target = mc.ls(sl=1)
    
    for i in range(0,len(target)-1):
        mc.select(target[i],target[len(target)-1])
        mel.eval("lightning \"\" 0 1 20 0.1 1 0 1 0.3;")
        

def paintSurface(target=None, brush="fire"):
    returns = []
    if not target:
        target = s()

    for i in range(0,len(target)):
        s([target[i]])
        curveSurface()
        paintAssign(brush=brush)
        d([target[i]])

#~~

def paintAssign(target=None, brush="fire"):
    returns = []
    if not target:
        target = s()

    if(brush=="fire"):
        paintBrushFire()

    for i in range(0,len(target)):
        s(target[i])
        mel.eval("assignNewPfxToon;")
        mel.eval("assignBrushToPfxToon;")

def paintBrushFire():
    mel.eval("brushPresetSetup();bPset \"time\" 1; bPset \"globalScale\" 0.7656982396; bPset \"depth\" 1; bPset \"modifyDepth\" 1; bPset \"modifyColor\" 1; bPset \"modifyAlpha\" 1; bPset \"illuminated\" 0; bPset \"castShadows\" 0; bPset \"branches\" 0; bPset \"twigs\" 0; bPset \"buds\" 0; bPset \"leaves\" 0; bPset \"flowers\" 0; bPset \"brushType\" 0; bPset \"brushWidth\" 0.04252389795; bPset \"screenspaceWidth\" 0; bPset \"stampDensity\" 3; bPset \"softness\" 0.17886; bPset \"edgeAntialias\" 1; bPset \"blurIntensity\" 4; bPset \"color1R\" 0.3098039329; bPset \"color1G\" 0.2235294133; bPset \"color1B\" 0.03921568766; bPset \"color2R\" 0.1372549087; bPset \"color2G\" 0; bPset \"color2B\" 0; bPset \"transparency1R\" 0.8666666746; bPset \"transparency1G\" 0.8666666746; bPset \"transparency1B\" 0.8666666746; bPset \"transparency2R\" 1; bPset \"transparency2G\" 1; bPset \"transparency2B\" 1; bPset \"incandescence1R\" 0.2039215714; bPset \"incandescence1G\" 0.1529411823; bPset \"incandescence1B\" 0.01568627357; bPset \"incandescence2R\" 0.1529411823; bPset \"incandescence2G\" 0.01176470611; bPset \"incandescence2B\" 0; bPset \"specularColorR\" 0; bPset \"specularColorG\" 0; bPset \"specularColorB\" 0; bPset \"specular\" 0; bPset \"specularPower\" 10; bPset \"translucence\" 0.2; bPset \"glow\" 0; bPset \"glowColorR\" 1; bPset \"glowColorG\" 0.8601613641; bPset \"glowColorB\" 0.595744729; bPset \"glowSpread\" 3.561; bPset \"shaderGlow\" 0; bPset \"hueRand\" 0.09756; bPset \"satRand\" 0.17074; bPset \"valRand\" 0.88618; bPset \"rootFade\" 0.22764; bPset \"tipFade\" 0.55284; bPset \"fakeShadow\" 0; bPset \"shadowOffset\" 0.5; bPset \"shadowDiffusion\" 0.1; bPset \"shadowTransparency\" 0.8; bPset \"backShadow\" 0; bPset \"brightnessRand\" 0; bPset \"centerShadow\" 0; bPset \"depthShadowType\" 0; bPset \"depthShadow\" 0; bPset \"depthShadowDepth\" 0; bPset \"realLights\" 0; bPset \"lightDirectionX\" 0.5; bPset \"lightDirectionY\" 0.5; bPset \"lightDirectionZ\" -0.5; bPset \"gapSize\" 0; bPset \"gapSpacing\" 1; bPset \"gapRand\" 1; bPset \"flowSpeed\" 0; bPset \"timeClip\" 0; bPset \"strokeTime\" 0; bPset \"startTime\" 0; bPset \"endTime\" 1000; bPset \"tubes\" 1; bPset \"tubeCompletion\" 1; bPset \"tubesPerStep\" 5.4369; bPset \"tubeRand\" 1; bPset \"startTubes\" 0; bPset \"lengthMax\" 0.1626; bPset \"lengthMin\" 0.1626; bPset \"segments\" 18; bPset \"tubeWidth1\" 0.027642; bPset \"tubeWidth2\" 0.007318; bPset \"widthRand\" 0.73984; bPset \"widthBias\" -0.49592; bPset \"lengthFlex\" 0.61788; bPset \"segmentLengthBias\" 0.08944; bPset \"segmentWidthBias\" 0; bPset \"tubeDirection\" 0; bPset \"elevationMin\" 0.1493599524; bPset \"elevationMax\" 0.72816; bPset \"azimuthMin\" -0.72816; bPset \"azimuthMax\" 0.96116; bPset \"flatness1\" 0; bPset \"flatness2\" 0; bPset \"twist\" 0; bPset \"twistRate\" 0; bPset \"twistRand\" 1; bPset \"spiralMin\" 0; bPset \"spiralMax\" 0; bPset \"spiralDecay\" 0; bPset \"displacementDelay\" 0.2; bPset \"wiggle\" 0; bPset \"wiggleFrequency\" 5; bPset \"wiggleOffset\" 0; bPset \"curl\" 0; bPset \"curlFrequency\" 1; bPset \"curlOffset\" 0; bPset \"noise\" 0; bPset \"noiseFrequency\" 0.2; bPset \"noiseOffset\" 0; bPset \"splitMaxDepth\" 2; bPset \"splitRand\" 0.187; bPset \"splitAngle\" 27.804; bPset \"splitSizeDecay\" 0.7; bPset \"splitBias\" 0; bPset \"splitTwist\" 0.5; bPset \"startBranches\" 0; bPset \"numBranches\" 3; bPset \"branchDropout\" 0.6504; bPset \"middleBranch\" 0; bPset \"minSize\" 0.0001; bPset \"pathFollow\" 0; bPset \"pathAttract\" 0; bPset \"curveFollow\" 0; bPset \"curveAttract\" 0; bPset \"curveMaxDist\" 0; bPset \"uniformForceX\" 0; bPset \"uniformForceY\" 0; bPset \"uniformForceZ\" 0; bPset \"turbulenceType\" 5; bPset \"turbulenceInterpolation\" 2; bPset \"turbulence\" 1; bPset \"turbulenceFrequency\" 9.1524; bPset \"turbulenceSpeed\" 0.25242; bPset \"turbulenceOffsetX\" 0; bPset \"turbulenceOffsetY\" 0; bPset \"turbulenceOffsetZ\" 0; bPset \"random\" 0; bPset \"gravity\" -0.45166; bPset \"momentum\" 0.29268; bPset \"deflection\" 0; bPset \"deflectionMin\" 0; bPset \"deflectionMax\" 0.3; bPset \"twigsInCluster\" 1; bPset \"twigDropout\" 0; bPset \"twigAngle1\" 90; bPset \"twigAngle2\" 80; bPset \"twigTwist\" 0; bPset \"twigLength\" 0.5; bPset \"twigStart\" 0.5; bPset \"numTwigClusters\" 4; bPset \"twigBaseWidth\" 0.4; bPset \"twigTipWidth\" 0.2; bPset \"leavesInCluster\" 1; bPset \"leafDropout\" 0; bPset \"leafAngle1\" 75; bPset \"leafAngle2\" 25; bPset \"leafTwist\" 0; bPset \"leafSegments\" 5; bPset \"leafStart\" 0.5; bPset \"numLeafClusters\" 3; bPset \"leafFlatness\" 1; bPset \"leafLength\" 0.3; bPset \"leafBaseWidth\" 0.15; bPset \"leafTipWidth\" 0.05; bPset \"leafSizeDecay\" 0.7; bPset \"leafTranslucence\" 0.7; bPset \"terminalLeaf\" 0; bPset \"leafColor1R\" 0.200000003; bPset \"leafColor1G\" 0.6000000238; bPset \"leafColor1B\" 0.3000000119; bPset \"leafColor2R\" 0.400000006; bPset \"leafColor2G\" 0.6000000238; bPset \"leafColor2B\" 0.3000000119; bPset \"leafHueRand\" 0; bPset \"leafSatRand\" 0; bPset \"leafValRand\" 0; bPset \"leafUseBranchTex\" 1; bPset \"budSize\" 0.03; bPset \"budColorR\" 0.400000006; bPset \"budColorG\" 0.8000000119; bPset \"budColorB\" 0.200000003; bPset \"petalsInFlower\" 1; bPset \"petalDropout\" 0; bPset \"flowerAngle1\" 75; bPset \"flowerAngle2\" 25; bPset \"flowerTwist\" 0.23; bPset \"petalSegments\" 5; bPset \"flowerStart\" 1; bPset \"numFlowers\" 10; bPset \"petalFlatness\" 1; bPset \"petalLength\" 0.2; bPset \"petalBaseWidth\" 0.05; bPset \"petalTipWidth\" 0.1; bPset \"flowerSizeDecay\" 0.7; bPset \"flowerTranslucence\" 0.7; bPset \"petalColor1R\" 0.8000000119; bPset \"petalColor1G\" 0.200000003; bPset \"petalColor1B\" 0.1000000015; bPset \"petalColor2R\" 1; bPset \"petalColor2G\" 1; bPset \"petalColor2B\" 1; bPset \"flowerHueRand\" 0; bPset \"flowerSatRand\" 0; bPset \"flowerValRand\" 0; bPset \"flowerUseBranchTex\" 1; bPset \"simplifyMethod\" 0; bPset \"colorLengthMap\" 0; bPset \"transpLengthMap\" 0; bPset \"incandLengthMap\" 0; bPset \"widthLengthMap\" 0; bPset \"splitLengthMap\" 0; bPset \"mapColor\" 0; bPset \"mapOpacity\" 0; bPset \"textureType\" 0; bPset \"mapMethod\" 2; bPset \"texColorScale\" 1; bPset \"texColorOffset\" 0; bPset \"texOpacityScale\" 1; bPset \"texOpacityOffset\" 0; bPset \"texColor1R\" 1; bPset \"texColor1G\" 1; bPset \"texColor1B\" 1; bPset \"texColor2R\" 0; bPset \"texColor2G\" 0; bPset \"texColor2B\" 0; bPset \"texAlpha1\" 0; bPset \"texAlpha2\" 1; bPset \"texUniformity\" 0.5; bPset \"fringeRemoval\" 0; bPset \"repeatU\" 1; bPset \"repeatV\" 1; bPset \"offsetU\" 0; bPset \"offsetV\" 0; bPset \"blurMult\" 1; bPset \"smear\" 0.1; bPset \"smearU\" 0; bPset \"smearV\" 0; bPset \"useFrameExtension\" 0; bPset \"frameExtension\" 1; bPset \"fractalRatio\" 0.7; bPset \"fractalAmplitude\" 1; bPset \"fractalThreshold\" 0; ")
    mel.eval("bPsetName \"imageName\" \"\";")
    mel.eval("bPsetName \"leafImage\" \"\";")
    mel.eval("bPsetName \"flowerImage\" \"\";")
    mel.eval("bPsetName \"creationScript\" \"\";")
    mel.eval("bPsetName \"runtimeScript\" \"\";")
    mel.eval("brushPresetApply();")
    mel.eval("presetSetPressure 1 8 0.1057000011 0.9430999756;")
    mel.eval("presetSetPressure 2 7 0.5 2.5;")
    mel.eval("presetSetPressure 3 5 0.1463000029 1;")
    mel.eval("rename (getDefaultBrush()) flameCurly;")
    print "// Result: flameCurly //"

def gmlToPaintEffects(brush="fire"):
    inputDir="/Users/nick/Desktop/output_r_hand.gml"
    paintCurves = []
    tree = etree.parse(inputDir)
    root = tree.getroot()
    '''
    if (root.tag.lower() != "gml"):
        print("Not a GML file.")
        return
    '''
    #~
    tag = root.find("tag")
    header = tag.find("header")
    drawing = tag.find("drawing")
    environment = header.find("environment")
    if not environment:
        environment = tag.find("environment")
    screenBounds = environment.find("screenBounds")
    globalScale = (0.01,0.01,0.01)
    dim = (float(screenBounds.find("x").text) * globalScale[0], float(screenBounds.find("y").text) * globalScale[1], float(screenBounds.find("z").text) * globalScale[2])
    #~
    strokes = drawing.findall("stroke")
    for stroke in strokes:
        points = []
        pointsEl = stroke.findall("pt")
        for pointEl in pointsEl:
            x = float(pointEl.find("x").text) * dim[0] 
            y = float(pointEl.find("y").text) * dim[1]
            z = float(pointEl.find("z").text) * dim[2]
            point = (x, y, z)
            points.append(point)
        crv = drawPoints(points)
        paintCurves.append(crv)
    s(d=True)
    target = s(paintCurves)
    paintSurface(target, brush)
