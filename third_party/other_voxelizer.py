### Voxelizer v1.0 ###
'''
http://zoomy.net/2010/06/22/voxelizer1.0/
this script builds an array of cubes to match the shape of
a given mesh.

Usage: copy this script and paste into a Python tab in Maya,
select target meshes and run. Optionally, paste into the script
editor, select all, and drag to the shelf to create a button.

- If nothing is selected, if a group called "voxelGeo" exists
  the meshes inside it will be used as the targets.
- If an object named "voxelScaleCtrl" exists, the voxel system
  will take its scale value from it.
- If an object named "cubeScaleCtrl" exists, each cube will take
  its scale value from it.

The script samples color and alpha values, but only one value
per face; for higher resolution color sampling, subdivide
your mesh's faces.

This script will result in one shader per face; if you run the script
more than once, optimize your scene with File > Optimize Scene Size
to remove unused nodes.

Maya's color sampling routines may have trouble with multiple
shadow-casting lights; this may depend in part on your video card.

Performance toggles:
"Verbose output" will print performance statistics during execution.
"Show Maya messages" will allow the display of any errors and command results.
"Profiling" will enable the Python profiler and display detailed statistics about function usage at the end of execution.
"Disable undo" if you're running out of memory during execution. The script will re-enable undo afterward (if it was on in the first place.)

Sample Maya 2008 scene at http://zoomy.net/pub/Voxelizer1.0_test.ma
'''
###

import maya.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel

################
### UI SETUP ###
################

def useVoxCheck(arg):
  global useVoxCtrl
  useVoxCtrl = True if arg == "true" else False
  cmds.floatFieldGrp('voxSizeText', edit=True,
      enable=1 if arg == "false" else 0)

def useCubeCheck(arg):
  global useCubeCtrl
  useCubeCtrl = True if arg == "true" else False
  cmds.floatFieldGrp('cubeSizeText', edit=True,
      enable=1 if arg == "false" else 0)

def useLightsRadio(arg):
  global lightRadios, useAmbient, useShadows, lastShadowCheck
  selected = cmds.radioButtonGrp(lightRadios, q=1, select=1)
  if selected == 1: # Scene lights
    cmds.checkBox('shadowsCheck', edit=True, enable=1, value=lastShadowCheck)
    useAmbient = False
  if selected == 2: # Ambient light
    cmds.checkBox('shadowsCheck', edit=True, enable=0, value=0)
    useAmbient = True

def useShadowsCheck(arg):
  global useShadows, lastShadowCheck
  useShadows = True if arg == "true" else False
  lastShadowCheck = useShadows

def setFrameText(arg):
  global frameRange
  firstFrame = int(cmds.playbackOptions(query=True, min=True))
  lastFrame = int(cmds.playbackOptions(query=True, max=True))
  cmds.floatFieldGrp('frameRangeText', edit=True,
      value=(firstFrame, lastFrame, 3.0, 3.0) )
  
def setVerbose(arg):
  global verboseOutput
  verboseOutput = True if arg == "true" else False

def setMessages(arg):
  global showCommands
  showCommands = True if arg == "true" else False

def setProfiling(arg):
  global doProfiling
  doProfiling = True if arg == "true" else False

def setUndos(arg):
  global disableUndos
  disableUndos = True if arg == "true" else False

def killVoxWindow(arg):
  cmds.deleteUI('voxSetup', window=True)

def finishSetup(arg):
  global doProfiling, frameRange, voxelSize, cubeSize, siState, srState, swState
  frameRange = cmds.floatFieldGrp('frameRangeText', query=True,
    value=True)
  if not useVoxCtrl:
    voxelSize = cmds.floatFieldGrp('voxSizeText', q=True, value=1)[0]
  if not useCubeCtrl:
    cubeSize = cmds.floatFieldGrp('cubeSizeText', q=True, value=1)[0]
  # store script editor message settings
  siState = cmds.scriptEditorInfo(q=True, si=True)
  srState = cmds.scriptEditorInfo(q=True, sr=True)
  swState = cmds.scriptEditorInfo(q=True, sw=True)
  
  killVoxWindow(0)

  if doProfiling:
    import cProfile
    cProfile.run('doit()', 'results')
    import pstats
    p = pstats.Stats('results')
    p.sort_stats('cumulative').print_stats(10)
  else:
    doit()

### BUILD UI ###

def promptSetup():
  if cmds.window('voxSetup', exists=True):
    killVoxWindow(0)
  cmds.window('voxSetup', widthHeight=[200, 400],
      title="Voxelize Meshes 1.0", resizeToFitChildren=True)
  cmds.columnLayout(columnAttach=("both", 5),
      columnAlign="left", columnWidth=200)
  
## Voxels section ##
                        
  global useVoxCtrl, useCubeCtrl, voxelSize, cubeSize
  cmds.text( label='Voxels', align="left", font="boldLabelFont", height=25)

  cmds.floatFieldGrp("voxSizeText",
      label='Voxel size',
      cw2=(60, 50),
      columnAlign2=("left", "left"),
      value=(1.0, 1.0, 1.0, 1.0))
                  
  cmds.checkBox("useVoxCtrl",
      label="Use voxelScaleCtrl (not found)",
      align="left",
      enable=0,
      value=0,
      changeCommand=useVoxCheck)

  cmds.floatFieldGrp('cubeSizeText', label='Cube size',
      cw2=(60, 50),
      columnAlign2=("left", "left"),
      value=(1.0, 1.0, 1.0, 1.0) )

  cmds.checkBox("useCubeCtrl",
      label="Use cubeScaleCtrl (not found)",
      align="left",
      enable=0,
      value=0,
      changeCommand=useCubeCheck)
  
  if cmds.objExists('voxelScaleCtrl'):
    cmds.checkBox("useVoxCtrl",
      edit=True,
      enable=1,
      value=1,
      label="Use voxelScaleCtrl") 
    cmds.floatFieldGrp('voxSizeText', edit=True, enable=0)
    useVoxCtrl = True
    voxelSize = round(cmds.getAttr('voxelScaleCtrl.scaleX'), 2)
  else: useVoxCtrl = False
    
  if cmds.objExists('cubeScaleCtrl'):
    cmds.checkBox("useCubeCtrl",
      edit=True,
      enable=1,
      value=1,
      label="Use cubeScaleCtrl") 
    cmds.floatFieldGrp('cubeSizeText', edit=True, enable=0)
    useCubeCtrl = True
    cubeSize = round(cmds.getAttr('cubeScaleCtrl.scaleX'), 2)
  else: useCubeCtrl = False
  
  cmds.separator(height=10, width=200)

## Lights section ##
                        
  cmds.text( label='Lights', align="left", font="boldLabelFont", height=25)
  global useAmbient, useShadows, lightRadios, lastShadowCheck
  useAmbient = False
  useShadows = False
  lastShadowCheck = False

  lightRadios = cmds.radioButtonGrp(
    vertical=True,
    numberOfRadioButtons=2,
    labelArray2=("Scene lights", "Ambient light"),
    changeCommand=useLightsRadio)
  cmds.checkBox("shadowsCheck",
    enable=1,
    value=0,
    label="Use shadows",
    changeCommand=useShadowsCheck)
    
  cmds.radioButtonGrp( lightRadios, edit=True, select=1 )

  # if no lights in scene
  if (len(cmds.ls(lt=True)) == 0):
    useAmbient = True
    useShadowsCheck("false")
    cmds.radioButtonGrp(lightRadios,
      edit=True,
      enable1=0,
      label1=("Scene lights (none found)"),
      select=2)
    cmds.checkBox("shadowsCheck",
      edit=1,
      enable=0,
      value=0)

  cmds.separator(height=10, width=200)

## Frame range ##

  cmds.text(label='Frame range', align="left", font="boldLabelFont", width=100, height=25)
  cmds.floatFieldGrp('frameRangeText',
      numberOfFields=2,
      cw2=(50, 50),
      columnAlign3=("left", "left", "left"),
      value=(0.0, 0.0, 0.0, 0.0))

  cmds.button("currentFrames",
      width=100, 
      label="Set to current frame range",
      align="center",
      command=setFrameText)

  setFrameText(0)

  cmds.separator(height=10, width=200)

## Performance section ##

  cmds.text(label='Performance', align="left", font="boldLabelFont", width=100, height=25)
  global verboseOutput, showCommands, doProfiling, disableUndos
  verboseOutput = False
  showCommands = False
  doProfiling = False
  disableUndos = False
  
  cmds.checkBox('Verbose output',
    enable=1,
    value=0,
    changeCommand=setVerbose) 
  cmds.checkBox('Show Maya messages',
    enable=1,
    value=0,
    changeCommand=setMessages) 
  cmds.checkBox('Profiling',
    enable=1,
    value=0,
    changeCommand=setProfiling) 
  cmds.checkBox('Disable undo',
    enable=1,
    value=0,
    changeCommand=setUndos) 

  cmds.separator(height=10, width=200)

## Buttons section ##

  cmds.columnLayout(columnAlign="center", columnWidth=200)
  cmds.rowLayout(nc=2, cw2=(60,60))
  cmds.button("Go", width=50, command=finishSetup, align="right")
  cmds.button("Cancel", width=50, command=killVoxWindow)
  cmds.showWindow()

######################
### MAIN FUNCTIONS ###
######################

# shoot a ray from point in direction and return all hits with mesh
def rayIntersect(mesh, point, direction=(0.0, 0.0, -1.0)):
  # get dag path of mesh - so obnoxious
  om.MGlobal.clearSelectionList()
  om.MGlobal.selectByName(mesh)
  sList = om.MSelectionList()
  om.MGlobal.getActiveSelectionList(sList)
  item = om.MDagPath()
  sList.getDagPath(0, item)
  item.extendToShape()
  fnMesh = om.MFnMesh(item)

  raySource = om.MFloatPoint(point[0], point[1], point[2], 1.0)
  rayDir = om.MFloatVector(direction[0], direction[1], direction[2])
  faceIds            = None
  triIds             = None
  idsSorted          = False
  worldSpace         = om.MSpace.kWorld
  maxParam           = 99999999
  testBothDirections = False
  accelParams        = None
  sortHits           = True
  hitPoints          = om.MFloatPointArray()
  hitRayParams       = om.MFloatArray()
  hitFaces           = om.MIntArray()
  hitTris            = None
  hitBarys1          = None
  hitBarys2          = None
  tolerance          = 0.0001

  hit = fnMesh.allIntersections(raySource, rayDir, faceIds, triIds, idsSorted, worldSpace, maxParam, testBothDirections, accelParams, sortHits, hitPoints, hitRayParams, hitFaces, hitTris, hitBarys1, hitBarys2, tolerance)

  # clear selection as may cause problems if called repeatedly
  om.MGlobal.clearSelectionList()
  result = []
  faces = []
  for x in range(hitPoints.length()):
    result.append((hitPoints[x][0], hitPoints[x][1], hitPoints[x][2]))
  for x in range(hitFaces.length()):
     faces.append(hitFaces[x])
  result = [result, faces]
  return result

# round to nearest fraction in decimal form: 1, .5, .25
def roundToFraction(input, denominator):
  factor = 1/denominator
  return round(input*factor)/factor

# progress bar, enabling "Esc"
def makeProgBar(length):
  global gMainProgressBar
  gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
  cmds.progressBar(gMainProgressBar,
        edit=True,
        beginProgress=True,
        isInterruptable=True,
        minValue=0,
        maxValue=abs(length))

# make an array of points in space to shoot rays from
def setLocs(mesh):
  global voxelSize, cubeSize, xmin, xmax, ymin, ymax, zmin, zmax, xLocs, yLocs, zLocs
  bb = cmds.exactWorldBoundingBox(mesh)
  xmin = bb[0]
  ymin = bb[1]
  zmin = bb[2]
  xmax = bb[3]
  ymax = bb[4]
  zmax = bb[5]
  
  # make 3 arrays of ray start points, one for each axis
  xLocs = []
  yLocs = []
  zLocs = []

  fac = 1/voxelSize
  
  for y in range(int(ymin*fac), int(ymax*fac+1)):
    for z in range(int(zmin*fac), int(zmax*fac+1)):
      loc = (xmax, y*voxelSize, z*voxelSize)
      xLocs.append(loc)
  for z in range(int(zmin*fac), int(zmax*fac+1)):
    for x in range(int(xmin*fac), int(xmax*fac+1)):
      loc = (x*voxelSize, ymax, z*voxelSize)
      yLocs.append(loc)
  for x in range(int(xmin*fac), int(xmax*fac+1)):
    for y in range(int(ymin*fac), int(ymax*fac+1)):
      loc = (x*voxelSize, y*voxelSize, zmax)
      zLocs.append(loc)

def objIsVisible(obj):
  visible = cmds.getAttr(obj+".visibility")
  # If this is an intermediate mesh, it's not visible.
  if cmds.attributeQuery("intermediateObject", node=obj, exists=True) == 0:
    visible = visible and cmds.getAttr(obj+".intermediateObject") == 0

  # If the object is in a displayLayer, and the displayLayer is hidden,
  # then the object is hidden.
  if cmds.attributeQuery("overrideEnabled", node=obj, exists=True) and cmds.getAttr(obj+".overrideEnabled"):
    visible = visible and cmds.getAttr(obj+".overrideVisibility")

  # Ascend the hierarchy and check all of the parent nodes
  if visible:
    parents = cmds.listRelatives(obj, parent=True)
    if parents != None and len(parents) > 0:
      visible = visible and objIsVisible(parents[0])

  return visible

def docancel():
  global gMainProgressBar, useAmbient, allLights, amb, disableUndos
  if disableUndos: cmds.undoInfo(state=True)
  if useAmbient:
    cmds.delete(cmds.listRelatives(amb, parent=True)[0])
  if allLights != None and len(allLights) > 0: cmds.sets(allLights, add="defaultLightSet")
  print "Voxelizer cancelled at frame %s."%cmds.currentTime(q=True)
  cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

  return 0

## main procedure ##

def doit():
  global voxelSize, cubeSize, cubeDict, allLights, amb, useAmbient, useShadows, disableUndos, showCommands, useVoxCtrl, useCubeCtrl, frameRange, verboseOutput, xmin, xmax, ymin, ymax, zmin, zmax, xLocs, yLocs, zLocs

  cubeDict = {}
  shaderDict = {}
  SGDict = {}

  if useAmbient:
      # disable and store all existing lights
      allLights = cmds.sets("defaultLightSet", q=1)
      cmds.sets(clear="defaultLightSet")
      # make an ambient light
      amb = cmds.ambientLight(i=True, ambientShade=0)
  else: allLights = None

  # identify control objects
  sel = cmds.ls(sl=True)
  if len(sel) > 0:
    # filter for polymeshes
    ctrl = cmds.filterExpand(sel, fullPath=0, selectionMask=12)
    cmds.select(cl=1)
    sel = []
    if ctrl == None:
      print "No meshes found in selection, checking scene..."
      # check for object or group named "voxelGeo"
      if cmds.objExists("voxelGeo"):
        cmds.select("voxelGeo")
        sel = cmds.ls(sl=1)
  if len(sel) == 0: # select all dag objects
    cmds.select(ado=True)
    sel = cmds.ls(sl=True)
  if sel == None or sel == []:
    cmds.confirmDialog( title='Mesh selection', message= 'No meshes found in scene.', button=['OK'])
    return 0
  else: # filter for polymeshes
    ctrl = cmds.filterExpand(sel, fullPath=0, selectionMask=12)
    if ctrl == None:
      cmds.confirmDialog( title='Mesh selection', message= 'No meshes found in scene.', button=['OK'])
      return 0

  if disableUndos: cmds.undoInfo(state=False)
  if not showCommands: cmds.scriptEditorInfo(sr=True, sw=True, si=True)
  firstFrame = frameRange[0]
  lastFrame = frameRange[1]
  duration = abs(int(lastFrame-firstFrame))+1

  # deal with backwards frame ranges
  if lastFrame < firstFrame:
    lastFrame -= 1
    frameStep = -1
  else:
    lastFrame += 1
    frameStep = 1

  startTime= cmds.timerX()
  makeProgBar(duration*len(ctrl))
  cmds.progressBar(gMainProgressBar, edit=True, beginProgress=True)
  s = "s" if duration > 1 else ""
  print "Voxelizer animating over", duration, "frame%s..."%s
  print "Press ESC to cancel"

  resetList = []
  directions = [(-1.0, 0.0, 0,0), (0.0, -1.0, 0,0), (0.0, 0.0, -1.0)]
  cubegroup = cmds.group(em=True, n='cubes')
  cmds.select(cl=1)

  #for f in range(firstFrame,lastFrame,frameStep): # for each frame
  for f in range(int(firstFrame),int(lastFrame),int(frameStep)): # for each frame
    stepTime= cmds.timerX()
    if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ):
      return docancel()
    cmds.currentTime(f, edit=True, update=True)

    # get sizes from control objects, if available
    if useVoxCtrl:
      voxelSize = round(cmds.getAttr('voxelScaleCtrl.scaleX'), 3)
    if useCubeCtrl:
      cubeSize = round(cmds.getAttr('cubeScaleCtrl.scaleX'), 3)

    # hide visible cubes
    for x in resetList:
      cmds.setKeyframe(x, at="scale", v=0, t=f)
    resetList = []

    # for every target control object:
    for c in ctrl:
      if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ):
        return docancel()
      cmds.progressBar(gMainProgressBar, edit=True, step=True)
      # if ctrl object is invisible, skip to the next one
      if objIsVisible(c) == 0:
        continue

      # bake textures into verts
      cmds.select(c)
      cmds.polyGeoSampler(sampleByFace=True, computeShadows=useShadows, rs=useShadows)
      
      # set ray starting points
      setLocs(c)
      locArrays = [xLocs, yLocs, zLocs]

      # for each axis:
      for i in range(3):
        # for every gridpoint:
        for loc in locArrays[i]:
          hits = []
          # zap a ray through the object
          rayInt = rayIntersect(c, loc, directions[i])
          hits = rayInt[0]
          hfaces =  rayInt[1]
          for j, x in enumerate(hits):
            # snap hit locations to cubegrid
            x = (roundToFraction(x[0], voxelSize), roundToFraction(x[1], voxelSize), roundToFraction(x[2], voxelSize) )

            # if location isn't in cubeDict: make a new cube
            if x not in cubeDict:
              # add location and new cube to cubeDict
              cubeDict[x] = cmds.polyCube(sz=1, sy=1, sx=1, cuv=4, d=1, h=1, w=1, ch=1)[0]
              cube = cubeDict[x]
              if useShadows:
                # prevent cubes from casting shadows onto the ctrl objs
                cmds.setAttr(cube+".castsShadows", 0)
              cmds.parent(cube, cubegroup)
              # move cube to location
              cmds.xform(cube, t=x)

              # shader coloring method: uses one shader per cube
              shader = cmds.shadingNode("lambert", asShader=1)
              # create a shading group
              shaderSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader+"SG")
              # connect the shader to the shading group
              cmds.connectAttr('%s.outColor'%shader, '%s.surfaceShader'%shaderSG, f=True)
              # add cube to the shaderSG
              shape = cmds.listRelatives(cube, shapes=1)[0]
              cmds.sets('%s'%shape, e=True, fe='%s'%shaderSG)

              shaderDict[cube] = shader
              SGDict[cube] = shaderSG

              # set scale key of 0 on the previous frame
              cmds.setKeyframe(cube, at="scale", v=0, t=(f-1))

            cube = cubeDict[x]
            cubeshape = cmds.listRelatives(cube, shapes=1)[0]

            # add cube to resetList
            resetList.append(cube)

            if len(hfaces) > 0:
              # check the alpha of the face
              alpha = cmds.polyColorPerVertex(c+'.f['+str(hfaces[j])+']', q=True, a=True, cdo=True)
              
              if alpha[0] > 0.5: # if more than half opaque
                # get the color of the face
                fcolor = cmds.polyColorPerVertex(c+'.f['+str(hfaces[j])+']', q=True, rgb=True, cdo=True, nun=True)
                cmds.setKeyframe(shaderDict[cube]+'.colorR', v=fcolor[0])
                cmds.setKeyframe(shaderDict[cube]+'.colorG', v=fcolor[1])
                cmds.setKeyframe(shaderDict[cube]+'.colorB', v=fcolor[2])

                # set a scale key
                cmds.setKeyframe(cube, at="scale", v=cubeSize, t=f, breakdown=0, hierarchy="none", controlPoints=0, shape=0)

                # if previous frame didn't have a scale key, set it to 0
                tempCurTime = cmds.currentTime(q=True)-1
                lastKey = cmds.keyframe(cube, at="scale", q=True, t=(tempCurTime,tempCurTime), valueChange=True)
                if lastKey == None:
                  cmds.setKeyframe(cube, at="scale", v=0, t=(f-1))

    if verboseOutput:
      stepTime = cmds.timerX(st=stepTime)
      totalTime = cmds.timerX(st=startTime)
      print "frame:", cmds.currentTime(q=True), "\tkeyed cubes:", len(resetList), "\ttotal cubes:", len(cubeDict)
      cps = "inf" if stepTime == 0 else round(len(resetList)/stepTime, 2)
      if useVoxCtrl or useCubeCtrl:
        print "\t\tvoxelSize:", voxelSize, "\tcubeSize: ", cubeSize
      print "\t\tstepTime:", round(stepTime, 2), "\ttotal time:", round(totalTime, 2), "\tcubes per second:", cps

  # restore scene state
  if useAmbient:
    if cmds.objExists(amb): cmds.delete(cmds.listRelatives(amb, parent=True)[0])
    cmds.sets(allLights, add="defaultLightSet")
  elif useShadows:
    # turn the cubes' shadows back on
    for x in cubeDict:
      cmds.setAttr(cubeDict[x]+".castsShadows", 1)
  if not showCommands: cmds.scriptEditorInfo(sr=srState, sw=swState, si=siState)
  if disableUndos: cmds.undoInfo(state=True)

  cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
  totalTime = cmds.timerX(st=startTime)
  print("Voxelizer finished: "+str(round(totalTime, 2))+ " seconds ("+str(round(totalTime/60, 2)) + " minutes)")

promptSetup()

### End Voxelizer 1.0 ###