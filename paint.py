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
import json
#~~
from mayatoolbox import *
from modeling import *

# test
def lightningStar(target=None):
    if not target:
        target = mc.ls(sl=1)
    
    for i in range(0,len(target)-1):
        mc.select(target[i],target[len(target)-1])
        mel.eval("lightning \"\" 0 1 20 0.1 1 0 1 0.3;")        

def paintCurve(target=None, brush=None, bake=True, reducePolys=0.1, maxPolys=0):
    returns = []
    if not target:
        target = s()

    paintBrushSelector(brush)

    for i in range(0,len(target)):
        oldObjects = getAllObjects()
        s(target[i])
        mel.eval("AttachBrushToCurves;")
        crv = getNewObjects(oldObjects)[1]
        crv.setAttr("sampleDensity", reducePolys)
        if (bake==True):
            oldObjects = getAllObjects()
            s(crv)
            mel.eval("doPaintEffectsToPoly(1,1,1,1," + str(maxPolys) + ");")
            newObjects = getNewObjects(oldObjects)
            obj = newObjects[len(newObjects)-1]
            s(obj)
            ch()
            d(crv)
            #ch()
            #ch()
            #mc.polyReduce(percentage=10)
            #ch()
            returns.append(obj)
        else:
            returns.append(crv)
        d(target[i])

    print("Created " + str(returns))
    return returns

def paintSurface(target=None, brush=None, bake=True, reducePolys=0.1, maxPolys=0):
    returns = []
    deleteCurves = []
    if not target:
        target = s()

    for i in range(0,len(target)):
        s([target[i]])
        crv=curveSurface()
        returns.append(paintAssign(brush=brush))
        deleteCurves.append(crv[0][0])
        d([target[i]])

    if (bake==True):
        s(returns)
        bakePaintEffects(reducePolys=reducePolys, maxPolys=maxPolys)
        d(deleteCurves)

    return returns

def paintAssign(target=None, brush=None):
    returns = []
    if not target:
        target = s()

    paintBrushSelector(brush)

    for i in range(0,len(target)):
        oldObjects = getAllObjects()
        s(target[i])
        mel.eval("assignNewPfxToon;")
        mel.eval("assignBrushToPfxToon;")
        
        returns.append(getNewObjects(oldObjects)[1])
        
    return returns

def bakePaintEffects(target=None, reducePolys=0.1, maxPolys=0):
    if not target:
        target = s()
    mel.eval("doPaintEffectsToPoly(1,1,1,1," + str(maxPolys) + ");")
    ch()
    if (reducePolys < 1.0):
        for obj in target:
            obj.setAttr("sampleDensity", reducePolys)
            ch()
        #mc.polyReduce(percentage=10)
        #ch()
    mc.polyQuad()
    ch()

# ~ ~ ~ ~ ~ ~

def latkToPaintEffects(inputDir=None, brush=None, bake=True, reducePolys=0.5, maxPolys=0, animateFrames=True):
    globalScale = (10,10,10)
    if not inputDir:
        inputDir=openFileDialog("json")
    with open(inputDir) as data_file:    
        data = json.load(data_file)
    #~
    for h in range(0, len(data["grease_pencil"][0]["layers"])):
        inTime(0)
        outTime(len(data["grease_pencil"][0]["layers"][h]["frames"]))
        start, end = getStartEnd()
        #~
        for i in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"])):
            strokes = []
            frameList = []
            for j in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"])):
                points = []
                for l in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"])):
                    x = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][0] * globalScale[0]
                    y = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][1] * globalScale[1]
                    z = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][2] * globalScale[2]
                    points.append((x,y,z))
                strokes.append(points)
            for stroke in strokes:
                if (len(stroke) > 1):
                    drawPoints(stroke, uniqueName=False)
                    paintStroke = paintCurve(brush=brush, bake=bake, reducePolys=reducePolys, maxPolys=maxPolys)
                    frameList.append(paintStroke)

            # TODO Fix for variable length frames, needs JSON to have frame_number field per frame.
            # TODO Add transform animation.
            if (animateFrames==True):
                if (len(frameList) > 0):
                    print("\nframeList for frame " + str(i) + " has " + str(len(frameList)) + " strokes.")
                    
                    s(frameList)
                    frameListObj = frameList[0]
                    try:
                        frameListObj = mc.polyUnite(ch=False, object=True) #name=getUniqueName("stroke"))
                    except:
                        pass
                    print(frameListObj)
                    ch()
                    for m in range(start, end):
                        if (i==m):
                            mc.setAttr(frameListObj[0] + ".v", 1, keyable=True)
                        else:
                            mc.setAttr(frameListObj[0] + ".v", 0, keyable=True)
                        mc.setKeyframe(frameListObj, time=m)

            # Old mesh show/hide method from Blender
            '''
            for i in range(0, len(frameList)):
                totalCounter += 1
                print(frameList[i].name + " | " + str(totalCounter) + " of " + totalStrokes + " total")
                if (_animateFrames==True):
                    hideFrame(frameList[i], 0, True)
                    for j in range(start, end):
                        if (j == layer.frames[c].frame_number):
                            hideFrame(frameList[i], j, False)
                            keyTransform(frameList[i], j)
                        elif (c < len(layer.frames)-1 and j > layer.frames[c].frame_number and j < layer.frames[c+1].frame_number):
                            hideFrame(frameList[i], j, False)
                        elif (c != len(layer.frames)-1):
                            hideFrame(frameList[i], j, True)
            '''
    print("*** FINISHED ***")

def latk():
    rm()
    latkToPaintEffects(inputDir="C:/Users/nick/Documents/GitHub/LightningArtist/latkUnreal/Content/Latk/layer_test.json", brush="neon")

def getQuillParentColor(target=None):
    if not target:
        target = ss()
    try:
        targetParent = None
        try:
            targetParent = py.listRelatives(parent=True)[0]
        except:
            targetParent = py.listRelatives(parent=True)
        rgba = py.getAttr(targetParent + ".rgba")
        color = (rgba[0], rgba[1], rgba[2], rgba[3])
        return color
    except:
        return (0,0,0,1)
    
def getAllQuillParentColors():
    colors = []
    curves = listAllCurves()
    for curve in curves:
        ss(curve)
        color = getQuillParentColor(curve)
        colors.append(color)
    return colors

def latkFromQuill():
    url = saveFileDialog("json")#filepath # compatibility with gui keywords

    #curves = listAllCurves()
    strokes = getAllCurveCvs()
    colors = getAllQuillParentColors()

    #if (len(curves) == len(strokes) == len(colors)):
    if (len(strokes) == len(colors)):
        pass
    else:
        print("Warning: color information doesn't match stroke information.")

    writeFilePath = "/Users/nick/Projects/LightningArtist/LightningArtistJS/animations/"
    writeFileName = "new_test.json"
    #~
    #if(bake == True):
        #bakeFrames()
    #gp = bpy.context.scene.grease_pencil
    globalScale = (-0.1, 0.1, 0.1)
    globalOffset = (0, 0, 0)
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    #palette = getActivePalette()
    #~
    sg = "{" + "\n"
    sg += "    \"creator\": \"maya\"," + "\n"
    sg += "    \"grease_pencil\": [" + "\n"
    sg += "        {" + "\n"
    sg += "            \"layers\": [" + "\n"
    sl = ""
    for f in range(0, 1):#len(gp.layers)):
        sb = ""
        #layer = gp.layers[f]
        for h in range(0, 1):#len(layer.frames)):
            #currentFrame = h
            #goToFrame(h)
            sb += "                        {" + "\n" # one frame
            sb += "                            \"strokes\": [" + "\n"
            if (len(strokes) > 0):#layer.frames[currentFrame].strokes) > 0):
                sb += "                                {" + "\n" # one stroke
                for i in range(0, len(strokes)):#layer.frames[currentFrame].strokes)):
                    color = (0,0,0)
                    try:
                        color = colors[i]#palette.colors[layer.frames[currentFrame].strokes[i].colorname].color
                    except:
                        pass
                    sb += "                                    \"color\": [" + str(color[0]) + ", " + str(color[1]) + ", " + str(color[2])+ "]," + "\n"
                    sb += "                                    \"points\": [" + "\n"
                    for j in range(0, len(strokes[i])):#layer.frames[currentFrame].strokes[i].points)):
                        x = 0.0
                        y = 0.0
                        z = 0.0
                        pressure = 1.0
                        strength = 1.0
                        #.
                        print(strokes[i][j])
                        point = strokes[i][j]#layer.frames[currentFrame].strokes[i].points[j].co
                        #pressure = layer.frames[currentFrame].strokes[i].points[j].pressure
                        #strength = layer.frames[currentFrame].strokes[i].points[j].strength
                        if useScaleAndOffset == True:
                            x = (point[0] * globalScale[0]) + globalOffset[0]
                            y = (point[1] * globalScale[1]) + globalOffset[1]
                            z = (point[2] * globalScale[2]) + globalOffset[2]
                        else:
                            x = point[0]
                            y = point[1]
                            z = point[2]
                        #~
                        if roundValues == True:
                            sb += "                                        {\"co\": [" + roundVal(x, numPlaces) + ", " + roundVal(y, numPlaces) + ", " + roundVal(z, numPlaces) + "], \"pressure\": " + roundVal(pressure, numPlaces) + ", \"strength\": " + roundVal(strength, numPlaces)
                        else:
                            sb += "                                        {\"co\": [" + str(x) + ", " + str(y) + ", " + str(z) + "], \"pressure\": " + pressure + ", \"strength\": " + strength                  
                        #~
                        if (j == len(strokes[i])-1):#layer.frames[currentFrame].strokes[i].points) - 1:
                            sb += "}" + "\n"
                            sb += "                                    ]" + "\n"
                            if (i == len(strokes) - 1):
                                sb += "                                }" + "\n" # last stroke for this frame
                            else:
                                sb += "                                }," + "\n" # end stroke
                                sb += "                                {" + "\n" # begin stroke
                        else:
                            sb += "}," + "\n"
                    if i == len(strokes) - 1:
                        sb += "                            ]" + "\n"
            else:
                sb += "                            ]" + "\n"
            if (h == 0):
                sb += "                        }" + "\n"
            else:
                sb += "                        }," + "\n"
        #~
        sf = "                {" + "\n" 
        sf += "                    \"name\": \"" + "maya_layer1" + "\"," + "\n"
        sf += "                    \"frames\": [" + "\n" + sb + "                    ]" + "\n"
        if (f == 0):
            sf += "                }" + "\n"
        else:
            sf += "                }," + "\n"
        sl += sf
        #~
    sg += sl
    sg += "            ]" + "\n"
    sg += "        }"+ "\n"
    sg += "    ]"+ "\n"
    sg += "}"+ "\n"
    if (url==None):
        url = writeFilePath + writeFileName
    #~
    with open(url, "w") as f:
        f.write(sg)
        f.closed
    print("Wrote " + url)

def hideFrame(target=None, _frame=0, _hide=True):
    if not target:
        target = s()
    for i in range (0, len(target)):
        if (_hide==True):
            mc.setAttr(target[i][0] + ".v", 0)
        else:
            mc.setAttr(target[i][0] + ".v", 1)
        try:
            k()
        except:
            pass
    try:
        k()
    except:
        pass

def gmlToPaintEffects(inputDir=None, brush=None, bake=True, reducePolys=0.1, maxPolys=0):
    if not inputDir:
        inputDir=openFileDialog("gml")
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
    newCurves = paintCurve(paintCurves, brush, bake, reducePolys, maxPolys)

# ~ ~ ~ BRUSHES ~ ~ ~

def paintBrushSelector(brush="fire"):
    if (brush=="fire"):
        brushFlameCurly()
    elif (brush=="oil"):
        brushThickOilRed()
    elif (brush=="neon"):
        brushNeonBlue()

def brushFlameCurly():
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

def brushThickOilRed():
    mel.eval("brushPresetSetup();bPset \"time\" 1; bPset \"globalScale\" 1; bPset \"depth\" 0; bPset \"modifyDepth\" 1; bPset \"modifyColor\" 1; bPset \"modifyAlpha\" 1; bPset \"illuminated\" 1; bPset \"castShadows\" 0; bPset \"branches\" 0; bPset \"twigs\" 0; bPset \"buds\" 0; bPset \"leaves\" 0; bPset \"flowers\" 0; bPset \"brushType\" 0; bPset \"brushWidth\" 0.016264; bPset \"screenspaceWidth\" 0; bPset \"stampDensity\" 3; bPset \"softness\" 0.21138; bPset \"edgeAntialias\" 1; bPset \"blurIntensity\" 4; bPset \"color1R\" 1; bPset \"color1G\" 0; bPset \"color1B\" 0; bPset \"color2R\" 1; bPset \"color2G\" 0; bPset \"color2B\" 0; bPset \"transparency1R\" 0.6235294342; bPset \"transparency1G\" 0.5529412031; bPset \"transparency1B\" 0.5529412031; bPset \"transparency2R\" 0; bPset \"transparency2G\" 0; bPset \"transparency2B\" 0; bPset \"incandescence1R\" 0; bPset \"incandescence1G\" 0; bPset \"incandescence1B\" 0; bPset \"incandescence2R\" 0; bPset \"incandescence2G\" 0; bPset \"incandescence2B\" 0; bPset \"specularColorR\" 0.9764705896; bPset \"specularColorG\" 0.9764705896; bPset \"specularColorB\" 0.9764705896; bPset \"specular\" 0; bPset \"specularPower\" 18.8616; bPset \"translucence\" 0.5122; bPset \"glow\" 0; bPset \"glowColorR\" 1; bPset \"glowColorG\" 1; bPset \"glowColorB\" 1; bPset \"glowSpread\" 1; bPset \"shaderGlow\" 0; bPset \"hueRand\" 0.01626; bPset \"satRand\" 0.05692; bPset \"valRand\" 0.03252; bPset \"rootFade\" 0.20326; bPset \"tipFade\" 0.14634; bPset \"fakeShadow\" 0; bPset \"shadowOffset\" 0.5; bPset \"shadowDiffusion\" 0.1; bPset \"shadowTransparency\" 0.8; bPset \"backShadow\" 0; bPset \"brightnessRand\" 0.0244; bPset \"centerShadow\" 0; bPset \"depthShadowType\" 0; bPset \"depthShadow\" 0; bPset \"depthShadowDepth\" 0; bPset \"realLights\" 0; bPset \"lightDirectionX\" 0.400000006; bPset \"lightDirectionY\" -0.200000003; bPset \"lightDirectionZ\" -0.6000000238; bPset \"gapSize\" 0; bPset \"gapSpacing\" 1; bPset \"gapRand\" 1; bPset \"flowSpeed\" 0; bPset \"timeClip\" 0; bPset \"strokeTime\" 0; bPset \"startTime\" 0; bPset \"endTime\" 1000; bPset \"tubes\" 1; bPset \"tubeCompletion\" 0; bPset \"tubesPerStep\" 6.2602; bPset \"tubeRand\" 0; bPset \"startTubes\" 0; bPset \"lengthMax\" 0.1199999973; bPset \"lengthMin\" 0.009999999776; bPset \"segments\" 23; bPset \"tubeWidth1\" 0.004066; bPset \"tubeWidth2\" 0.005692; bPset \"widthRand\" 0.43902; bPset \"widthBias\" -0.38212; bPset \"lengthFlex\" 1; bPset \"segmentLengthBias\" 0; bPset \"segmentWidthBias\" 0; bPset \"tubeDirection\" 0; bPset \"elevationMin\" 0.2; bPset \"elevationMax\" 0.5; bPset \"azimuthMin\" -0.1; bPset \"azimuthMax\" 0.1; bPset \"flatness1\" 0; bPset \"flatness2\" 0; bPset \"twist\" 0; bPset \"twistRate\" 0; bPset \"twistRand\" 1; bPset \"spiralMin\" 0; bPset \"spiralMax\" 0; bPset \"spiralDecay\" 0; bPset \"displacementDelay\" 0.2; bPset \"wiggle\" 0; bPset \"wiggleFrequency\" 5; bPset \"wiggleOffset\" 0; bPset \"curl\" 0; bPset \"curlFrequency\" 1; bPset \"curlOffset\" 0; bPset \"noise\" 0; bPset \"noiseFrequency\" 0.2; bPset \"noiseOffset\" 0; bPset \"splitMaxDepth\" 2; bPset \"splitRand\" 0; bPset \"splitAngle\" 30; bPset \"splitSizeDecay\" 0.7; bPset \"splitBias\" 0; bPset \"splitTwist\" 0.5; bPset \"startBranches\" 0; bPset \"numBranches\" 2; bPset \"branchDropout\" 0; bPset \"middleBranch\" 0; bPset \"minSize\" 0.0001; bPset \"pathFollow\" 1; bPset \"pathAttract\" 0; bPset \"curveFollow\" 0; bPset \"curveAttract\" 0; bPset \"curveMaxDist\" 0; bPset \"uniformForceX\" 0; bPset \"uniformForceY\" 0; bPset \"uniformForceZ\" 0; bPset \"turbulenceType\" 0; bPset \"turbulenceInterpolation\" 0; bPset \"turbulence\" 0.2; bPset \"turbulenceFrequency\" 0.2; bPset \"turbulenceSpeed\" 0.5; bPset \"turbulenceOffsetX\" 0; bPset \"turbulenceOffsetY\" 0; bPset \"turbulenceOffsetZ\" 0; bPset \"random\" 0; bPset \"gravity\" 0; bPset \"momentum\" 0.03252; bPset \"deflection\" 0; bPset \"deflectionMin\" 0; bPset \"deflectionMax\" 0.3; bPset \"twigsInCluster\" 1; bPset \"twigDropout\" 0; bPset \"twigAngle1\" 90; bPset \"twigAngle2\" 80; bPset \"twigTwist\" 0; bPset \"twigLength\" 0.5; bPset \"twigStart\" 0.5; bPset \"numTwigClusters\" 4; bPset \"twigBaseWidth\" 0.4; bPset \"twigTipWidth\" 0.2; bPset \"leavesInCluster\" 1; bPset \"leafDropout\" 0; bPset \"leafAngle1\" 75; bPset \"leafAngle2\" 25; bPset \"leafTwist\" 0; bPset \"leafSegments\" 5; bPset \"leafStart\" 0.5; bPset \"numLeafClusters\" 3; bPset \"leafFlatness\" 1; bPset \"leafLength\" 0.3; bPset \"leafBaseWidth\" 0.15; bPset \"leafTipWidth\" 0.05; bPset \"leafSizeDecay\" 0.7; bPset \"leafTranslucence\" 0.3; bPset \"terminalLeaf\" 0; bPset \"leafColor1R\" 0.200000003; bPset \"leafColor1G\" 0.6000000238; bPset \"leafColor1B\" 0.3000000119; bPset \"leafColor2R\" 0.400000006; bPset \"leafColor2G\" 0.6000000238; bPset \"leafColor2B\" 0.3000000119; bPset \"leafHueRand\" 0; bPset \"leafSatRand\" 0; bPset \"leafValRand\" 0; bPset \"leafUseBranchTex\" 1; bPset \"budSize\" 0.03; bPset \"budColorR\" 0.400000006; bPset \"budColorG\" 0.8000000119; bPset \"budColorB\" 0.200000003; bPset \"petalsInFlower\" 1; bPset \"petalDropout\" 0; bPset \"flowerAngle1\" 75; bPset \"flowerAngle2\" 25; bPset \"flowerTwist\" 0.23; bPset \"petalSegments\" 5; bPset \"flowerStart\" 1; bPset \"numFlowers\" 10; bPset \"petalFlatness\" 1; bPset \"petalLength\" 0.2; bPset \"petalBaseWidth\" 0.05; bPset \"petalTipWidth\" 0.1; bPset \"flowerSizeDecay\" 0.7; bPset \"flowerTranslucence\" 0.3; bPset \"petalColor1R\" 0.8000000119; bPset \"petalColor1G\" 0.200000003; bPset \"petalColor1B\" 0.1000000015; bPset \"petalColor2R\" 1; bPset \"petalColor2G\" 1; bPset \"petalColor2B\" 1; bPset \"flowerHueRand\" 0; bPset \"flowerSatRand\" 0; bPset \"flowerValRand\" 0; bPset \"flowerUseBranchTex\" 1; bPset \"simplifyMethod\" 2; bPset \"colorLengthMap\" 0; bPset \"transpLengthMap\" 0; bPset \"incandLengthMap\" 0; bPset \"widthLengthMap\" 0; bPset \"splitLengthMap\" 0; bPset \"mapColor\" 0; bPset \"mapOpacity\" 0; bPset \"textureType\" 3; bPset \"mapMethod\" 2; bPset \"texColorScale\" 1; bPset \"texColorOffset\" 0; bPset \"texOpacityScale\" 1; bPset \"texOpacityOffset\" 0; bPset \"texColor1R\" 1; bPset \"texColor1G\" 0.991538465; bPset \"texColor1B\" 0.8821457028; bPset \"texColor2R\" 0.8823529482; bPset \"texColor2G\" 0.8666666746; bPset \"texColor2B\" 1; bPset \"texAlpha1\" 1; bPset \"texAlpha2\" 0; bPset \"texUniformity\" 1; bPset \"fringeRemoval\" 0; bPset \"repeatU\" 0.02999999933; bPset \"repeatV\" 0.3000000119; bPset \"offsetU\" 0; bPset \"offsetV\" 0; bPset \"blurMult\" 0.39024; bPset \"smear\" 0.82114; bPset \"smearU\" 0; bPset \"smearV\" 0; bPset \"useFrameExtension\" 0; bPset \"frameExtension\" 1; bPset \"fractalRatio\" 0.8374; bPset \"fractalAmplitude\" 0.9187; bPset \"fractalThreshold\" 0.21952;") 
    mel.eval("bPsetName \"imageName\" \"\";")
    mel.eval("bPsetName \"leafImage\" \"leaftex\";")
    mel.eval("bPsetName \"flowerImage\" \"\";")
    mel.eval("bPsetName \"creationScript\" \"\";")
    mel.eval("bPsetName \"runtimeScript\" \"\";")
    mel.eval("brushPresetApply();")
    mel.eval("presetSetPressure 1 1 0.7073000073 1.5;") 
    mel.eval("presetSetPressure 2 5 0 1;")
    mel.eval("presetSetPressure 3 3 0 1;")
    mel.eval("rename (getDefaultBrush()) thickOilRed;")

def brushNeonBlue():
    mel.eval("brushPresetSetup();bPset \"time\" 1; bPset \"globalScale\" 0.4447684171; bPset \"depth\" 1; bPset \"modifyDepth\" 1; bPset \"modifyColor\" 1; bPset \"modifyAlpha\" 1; bPset \"illuminated\" 0; bPset \"castShadows\" 0; bPset \"branches\" 0; bPset \"twigs\" 0; bPset \"buds\" 0; bPset \"leaves\" 0; bPset \"flowers\" 0; bPset \"brushType\" 0; bPset \"brushWidth\" 0.03500000015; bPset \"screenspaceWidth\" 0; bPset \"stampDensity\" 5.8256; bPset \"softness\" -0.16504; bPset \"edgeAntialias\" 1; bPset \"blurIntensity\" 4; bPset \"color1R\" 0.1450980455; bPset \"color1G\" 0.07843137532; bPset \"color1B\" 0.04705882445; bPset \"color2R\" 1; bPset \"color2G\" 1; bPset \"color2B\" 1; bPset \"transparency1R\" 0.9450980425; bPset \"transparency1G\" 0.9450980425; bPset \"transparency1B\" 0.9450980425; bPset \"transparency2R\" 0.9450980425; bPset \"transparency2G\" 0.9450980425; bPset \"transparency2B\" 0.9450980425; bPset \"incandescence1R\" 0.01568627357; bPset \"incandescence1G\" 0.1411764771; bPset \"incandescence1B\" 0.3764705956; bPset \"incandescence2R\" 0.01196968555; bPset \"incandescence2G\" 0.1077273041; bPset \"incandescence2B\" 0.2872727215; bPset \"specularColorR\" 0; bPset \"specularColorG\" 0; bPset \"specularColorB\" 0; bPset \"specular\" 0; bPset \"specularPower\" 10; bPset \"translucence\" 0.2; bPset \"glow\" 0.60976; bPset \"glowColorR\" 1; bPset \"glowColorG\" 0; bPset \"glowColorB\" 0.6735985875; bPset \"glowSpread\" 6; bPset \"shaderGlow\" 0; bPset \"hueRand\" 0; bPset \"satRand\" 0; bPset \"valRand\" 0; bPset \"rootFade\" 0; bPset \"tipFade\" 0; bPset \"fakeShadow\" 1; bPset \"shadowOffset\" 0.36586; bPset \"shadowDiffusion\" 0.47572; bPset \"shadowTransparency\" 0.13592; bPset \"backShadow\" 0; bPset \"brightnessRand\" 0; bPset \"centerShadow\" 0; bPset \"depthShadowType\" 0; bPset \"depthShadow\" 0; bPset \"depthShadowDepth\" 0; bPset \"realLights\" 0; bPset \"lightDirectionX\" 0.5; bPset \"lightDirectionY\" 0.5; bPset \"lightDirectionZ\" -0.5; bPset \"gapSize\" 0; bPset \"gapSpacing\" 1; bPset \"gapRand\" 1; bPset \"flowSpeed\" 0; bPset \"timeClip\" 0; bPset \"strokeTime\" 0; bPset \"startTime\" 0; bPset \"endTime\" 1000; bPset \"tubes\" 0; bPset \"tubeCompletion\" 0; bPset \"tubesPerStep\" 0.5; bPset \"tubeRand\" 0; bPset \"startTubes\" 0; bPset \"lengthMax\" 0.1; bPset \"lengthMin\" 0.1; bPset \"segments\" 2; bPset \"tubeWidth1\" 0.02233; bPset \"tubeWidth2\" 0.024272; bPset \"widthRand\" 0; bPset \"widthBias\" 0; bPset \"lengthFlex\" 0; bPset \"segmentLengthBias\" 0; bPset \"segmentWidthBias\" 0; bPset \"tubeDirection\" 0; bPset \"elevationMin\" 0; bPset \"elevationMax\" 0; bPset \"azimuthMin\" -0.3; bPset \"azimuthMax\" -0.3; bPset \"flatness1\" 0; bPset \"flatness2\" 0; bPset \"twist\" 0; bPset \"twistRate\" 0; bPset \"twistRand\" 1; bPset \"spiralMin\" 0; bPset \"spiralMax\" 0; bPset \"spiralDecay\" 0; bPset \"displacementDelay\" 0.2; bPset \"wiggle\" 0; bPset \"wiggleFrequency\" 5; bPset \"wiggleOffset\" 0; bPset \"curl\" 0; bPset \"curlFrequency\" 1; bPset \"curlOffset\" 0; bPset \"noise\" 0; bPset \"noiseFrequency\" 0.2; bPset \"noiseOffset\" 0; bPset \"splitMaxDepth\" 2; bPset \"splitRand\" 0; bPset \"splitAngle\" 30; bPset \"splitSizeDecay\" 0.7; bPset \"splitBias\" 0; bPset \"splitTwist\" 0.5; bPset \"startBranches\" 0; bPset \"numBranches\" 2; bPset \"branchDropout\" 0; bPset \"middleBranch\" 0; bPset \"minSize\" 0.0001; bPset \"pathFollow\" 0; bPset \"pathAttract\" 0; bPset \"curveFollow\" 0; bPset \"curveAttract\" 0; bPset \"curveMaxDist\" 0; bPset \"uniformForceX\" 0; bPset \"uniformForceY\" 0; bPset \"uniformForceZ\" 0; bPset \"turbulenceType\" 0; bPset \"turbulenceInterpolation\" 0; bPset \"turbulence\" 0.2; bPset \"turbulenceFrequency\" 0.2; bPset \"turbulenceSpeed\" 0.5; bPset \"turbulenceOffsetX\" 0; bPset \"turbulenceOffsetY\" 0; bPset \"turbulenceOffsetZ\" 0; bPset \"random\" 0; bPset \"gravity\" 0; bPset \"momentum\" 1; bPset \"deflection\" 0; bPset \"deflectionMin\" 0; bPset \"deflectionMax\" 0.3; bPset \"twigsInCluster\" 1; bPset \"twigDropout\" 0; bPset \"twigAngle1\" 90; bPset \"twigAngle2\" 80; bPset \"twigTwist\" 0; bPset \"twigLength\" 0.5; bPset \"twigStart\" 0.5; bPset \"numTwigClusters\" 4; bPset \"twigBaseWidth\" 0.4; bPset \"twigTipWidth\" 0.2; bPset \"leavesInCluster\" 1; bPset \"leafDropout\" 0; bPset \"leafAngle1\" 75; bPset \"leafAngle2\" 25; bPset \"leafTwist\" 0; bPset \"leafSegments\" 5; bPset \"leafStart\" 0.5; bPset \"numLeafClusters\" 3; bPset \"leafFlatness\" 1; bPset \"leafLength\" 0.3; bPset \"leafBaseWidth\" 0.15; bPset \"leafTipWidth\" 0.05; bPset \"leafSizeDecay\" 0.7; bPset \"leafTranslucence\" 0.3; bPset \"terminalLeaf\" 0; bPset \"leafColor1R\" 0.200000003; bPset \"leafColor1G\" 0.6000000238; bPset \"leafColor1B\" 0.3000000119; bPset \"leafColor2R\" 0.400000006; bPset \"leafColor2G\" 0.6000000238; bPset \"leafColor2B\" 0.3000000119; bPset \"leafHueRand\" 0; bPset \"leafSatRand\" 0; bPset \"leafValRand\" 0; bPset \"leafUseBranchTex\" 1; bPset \"budSize\" 0.03; bPset \"budColorR\" 0.400000006; bPset \"budColorG\" 0.8000000119; bPset \"budColorB\" 0.200000003; bPset \"petalsInFlower\" 1; bPset \"petalDropout\" 0; bPset \"flowerAngle1\" 75; bPset \"flowerAngle2\" 25; bPset \"flowerTwist\" 0.23; bPset \"petalSegments\" 5; bPset \"flowerStart\" 1; bPset \"numFlowers\" 10; bPset \"petalFlatness\" 1; bPset \"petalLength\" 0.2; bPset \"petalBaseWidth\" 0.05; bPset \"petalTipWidth\" 0.1; bPset \"flowerSizeDecay\" 0.7; bPset \"flowerTranslucence\" 0.3; bPset \"petalColor1R\" 0.8000000119; bPset \"petalColor1G\" 0.200000003; bPset \"petalColor1B\" 0.1000000015; bPset \"petalColor2R\" 1; bPset \"petalColor2G\" 1; bPset \"petalColor2B\" 1; bPset \"flowerHueRand\" 0; bPset \"flowerSatRand\" 0; bPset \"flowerValRand\" 0; bPset \"flowerUseBranchTex\" 1; bPset \"simplifyMethod\" 2; bPset \"colorLengthMap\" 0; bPset \"transpLengthMap\" 0; bPset \"incandLengthMap\" 0; bPset \"widthLengthMap\" 0; bPset \"splitLengthMap\" 0; bPset \"mapColor\" 0; bPset \"mapOpacity\" 0; bPset \"textureType\" 2; bPset \"mapMethod\" 2; bPset \"texColorScale\" 1; bPset \"texColorOffset\" 0; bPset \"texOpacityScale\" 1; bPset \"texOpacityOffset\" 0; bPset \"texColor1R\" 1; bPset \"texColor1G\" 1; bPset \"texColor1B\" 1; bPset \"texColor2R\" 0.2196078449; bPset \"texColor2G\" 0.2196078449; bPset \"texColor2B\" 0.2196078449; bPset \"texAlpha1\" 0; bPset \"texAlpha2\" 1; bPset \"texUniformity\" 0.5; bPset \"fringeRemoval\" 1; bPset \"repeatU\" 2.35776; bPset \"repeatV\" 1.86992; bPset \"offsetU\" 0; bPset \"offsetV\" 0.57724; bPset \"blurMult\" 2.5; bPset \"smear\" 0.07318; bPset \"smearU\" 0; bPset \"smearV\" 0; bPset \"useFrameExtension\" 0; bPset \"frameExtension\" 1; bPset \"fractalRatio\" 0.7; bPset \"fractalAmplitude\" 1; bPset \"fractalThreshold\" 0; ")
    mel.eval("bPsetName \"imageName\" \"\";")
    mel.eval("bPsetName \"leafImage\" \"leaftex\";")
    mel.eval("bPsetName \"flowerImage\" \"\";")
    mel.eval("bPsetName \"creationScript\" \"\";")
    mel.eval("bPsetName \"runtimeScript\" \"\";")
    mel.eval("brushPresetApply();")
    mel.eval("presetSetPressure 1 8 0 1;")
    mel.eval("presetSetPressure 2 0 0 1;")
    mel.eval("presetSetPressure 3 9 0.3007999957 1;")
    mel.eval("rename (getDefaultBrush()) neonBlue;")
