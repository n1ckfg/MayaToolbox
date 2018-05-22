#
# as_polyFracture.py v0.5 beta
#
#
# Python script for Maya
#
#
#	by Alin Sfetcu
#		aSfetcu @ gmail.com
#
#
#	Creation date:	08-may-2009
#	Last update:	05-dec-2011
#
#
#  Installation:
#  ---------------
#	- copy script file (.py) from the .zip file in your ..\maya\scripts
#	- add a new (python) button to your shelf with code :
#
#				import as_polyFracture as pf
#				reload(pf)
#				pf.pub_polyVoronoi()
#
#
#  Run:
#  ---------------
#	- press that shelf button
#
#
#  Description:
#  ---------------
#	- this script lets you :
#		- break an object using a 3D voronoi algorithm
#		- have a look here ( http://vimeo.com/3399172 )
#
#
#  Usage:
#  ---------------
#	- break stuff :)
#
#
#  Limitations:
#  ---------------
#  - doesn`t like concave geometry (cups, glasses etc)
#
#
#  To do:
#  ---------------
#	- find time to add more features
#	- fix the bug with concave objects
#	- assign other shader to interior faces
#
#
#  History:
#  ---------------
#	-v0.5c: [  05-dec-2011 ]
#		- i have deactivated step 3. You need to clean the locators found outside your mesh by hand.
#
#	-v0.5: [  21-oct-2010 ]
#		- i hope this time that pestering bug inside the clean step is fixed.
#
#	-v0.4: [  29-may-2010 ]
#		- fixed a bug with Maya 2011 when trying to "clean" the locators.
#		
#	-v0.3: [  11-apr-2010 ]
#		- fixed a bug where trying to break a resulting piece even more was generating an error.
#
#	-v0.2: [  14-mar-2010 ]
#		- fixed a bug where the embedded Python found in Maya 2009 has no idea what math.isnan is :)
#
#	-v0.1: [  10-mar-2010 ]
#		- first release
#
#
#  ..and of course,
#  ----------------
#
#  YOU ARE USING THIS PROGRAM AT YOUR OWN RISK! I SHALL NOT BE LIABLE FOR ANY KIND OF DAMAGE TO
#  YOUR SYSTEM RESULTED FROM THE USE OF THIS PROGRAM. ALTHOUGH TESTED AND DISTRIBUTED WITH
#  NO HARM INTENDED, I MAY NOT GUARANTEE ANY SAFETY UPON USING THIS PIECE OF SOFTWARE.
#
#  You may use this script free of charge.
#
#  DO NOT MODIFY THIS SCRIPT UNLESS YOU HAVE MY PERMISSION.
#
#  If you need help, advices, questions regarding this script or if you find a bug please contact
#  me at aSfetcu@gmail.com. If you report a bug please include a precise description of the bug.
#
#  Thank you!
#
#
#
#
# as_polyFracture.py v0.5 beta
#
#	by Alin Sfetcu
#		aSfetcu @ gmail.com
#
#	Creation date:	08-may-2009
#	Last update:	05-dec-2011
#
#

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
import random as rnd
import math as mt

#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/ utility procedures.
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
def ui_inputDlg ( _title, _message, _text):

	_value = ''

	_result = mc.promptDialog(
			title = _title,
			message = _message,
			text = _text,
			button = ['OK', 'Cancel'],
			defaultButton = 'OK',
			cancelButton = 'Cancel',
			dismissString = 'Cancel')

	if _result == 'OK':
		_value = mc.promptDialog(query=True, text=True)

	return _value
#/////////////////////////////////////////////////////////////////////////////////////////////
def ui_alertv( _title, _message ):

	mc.confirmDialog(
			title = _title,
			message = _message,
			button = ['OK'],
			defaultButton = 'OK')
#/////////////////////////////////////////////////////////////////////////////////////////////
def ui_confirm( _title, _message ):

	_result = mc.confirmDialog(
			title = _title,
			message = _message,
			button = ['Yes', 'No'],
			defaultButton = 'No',
			cancelButton = 'No',
			dismissString = 'No')

	if _result == 'Yes':
		return True
	elif _result == 'No':
		return False
	else:
		return False
#/////////////////////////////////////////////////////////////////////////////////////////////
def ui_addPB( _operation, _value, _caption, _maxValue):
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar');

	if _operation == "add":
		if ( _caption == "") | (_maxValue == 0):
				assert "Progressbar initialization failure!"

		# handle progress bar
		mc.progressBar( gMainProgressBar,
				edit=True,
				beginProgress=True,
				isInterruptable=True,
				status= _caption,
				maxValue= _maxValue )

	elif _operation == "edit":

		if (_caption == "") | (_value == 0):
			assert "Progressbar update failure!"

		#gMainProgressBar = mm.eval('$tmp = $gMainProgressBar');
		#if mc.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
		#	break
		mc.progressBar( gMainProgressBar,
				edit=True,
				status= _caption,
				step= _value )

	else:
		# closes the progressBar
		mc.progressBar( gMainProgressBar,
				edit=True,
				endProgress=True )
#/////////////////////////////////////////////////////////////////////////////////////////////				
def priv_getVer():
	version = mc.about( version=True )
	return version[0:4]
#/////////////////////////////////////////////////////////////////////////////////////////////				
def priv_getSceneUnit():
	curVal = mc.currentUnit( query=True, linear=True )
	return curVal
#/////////////////////////////////////////////////////////////////////////////////////////////				
def priv_getSceneUnitValue():
	curUnit = priv_getSceneUnit()
#	print "scena lu peste este in %s" % curUnit
	defVal = 1

	if curUnit == "m":
		defVal = 0.01	
	elif curUnit == "cm":
		defVal = 1
	elif curUnit == "mm":
		defVal = 10
	elif curUnit == "in":
		defVal = 0.3937008
		
	return defVal	
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/ step 1.
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
def pub_spawnPoints():
	_sel = mc.ls(sl=True)
	if len(_sel) > 0:
		# template the object
		mc.setAttr ( _sel[0] + ".template", 1)
		# get object BB and position in worldspace
		_objBB = mc.xform( _sel[0], q=True, bb=True)
		_objPos = mc.xform( _sel[0], ws=True, q=True, rp=True)
		# set the position of the plane under the object
		_poz = [0, 0, 0]
		_poz[0] = _objPos[0]
		_poz[1] = _objPos[1] - (( _objBB[4] - _objBB[1]) / 1.75)
		_poz[2] = _objPos[2]
		# scale the plane larger than the bounding box
		_scale = [0, 0, 0]
		_scale[0] = ( _objBB[0] - _objBB[3]) * 1.2
		_scale[2] = ( _objBB[2] - _objBB[5]) * 1.2
		# create, place, scale and rename the plane
		mc.nurbsPlane( p=(0, 0, 0), ax=(0, 1, 0), w=1, lr=1, d=3, u=1, v=1, ch=0)
		mc.move( _poz[0], _poz[1], _poz[2])
		mc.scale( _scale[0], 0, _scale[2])
		_nPlane = mc.rename( "emissionPlane_" + _sel[0] )
		# create the emitter
		mc.emitter( _nPlane, type='surface', r=20, sro=0, nuv=1, cye='none', cyi=1, spd=2, srn=1, nsp=1, tsp=0, mxd=0, mnd=0, sp=0)
		_emitter = mc.rename( "emitter_" + _sel[0] )
		# create the particle object
		mc.particle( n="xxx")
		_pParticle = mc.rename( "particle_" + _sel[0] )
		# connect the emitter to the particle object
		mc.connectDynamic( _pParticle, em=_emitter )
		# template the plane and the particle object
		mc.setAttr ( _nPlane + ".template", 1)
		mc.setAttr ( _pParticle + ".template", 1)
	else:
		assert "No object selected!"
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/ step 2.
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
def priv_particleLocators( _numPoints, _pos ):
	mc.select(cl=True)
	_mayaVer = priv_getVer()
	_sceneSize = priv_getSceneUnitValue()

	_grp = mc.group(em=True, name=("GRP_%d_locators" % _numPoints))
	mc.xform(os=True, piv=(0, 0, 0))

	_startPlaceTime = mc.timerX()
	ui_addPB( "add", 0, "Preparing to spawn points...", _numPoints)

	for _i in range (0, _numPoints, 1):
		_loc = mc.spaceLocator(p=(0, 0, 0))

		
		# position the locator
		if ((_mayaVer == "2011") | (_mayaVer == "2012")) :	
			_vPosition = om.MFloatVector( _pos[ _i ][ 0 ], _pos[ _i ][ 1 ], _pos[ _i ][ 2 ] )
		else:
			_vPosition = om.MFloatVector( _pos[3 * _i + 0], _pos[3 * _i + 1], _pos[3 * _i + 2] )					
		mc.move( _vPosition.x * _sceneSize, _vPosition.y * _sceneSize, _vPosition.z * _sceneSize, _loc)		
		
		# scale the locator
		_vScale = om.MFloatVector( 1, 1, 1 )
		mc.scale(_vScale.x * _sceneSize, _vScale.y * _sceneSize, _vScale.z * _sceneSize, _loc)
		#rename and parent
		_newName = mc.rename( "loc__%d" % _i )
		mc.parent( _newName, _grp )

		#ui_addPB( "edit", _i, "Spawning points %d/%d   " % (_i, _numPoints) , 0)
		ui_addPB( "edit", 1, "Spawning points %d/%d   " % (_i, _numPoints) , 0)

	mc.select(cl=True)
	ui_addPB( "del", 0, "", 0)
	_totalPlaceTime = mc.timerX( startTime= _startPlaceTime)
	print ( "Placing %d points took %g s to complete." % (_numPoints, _totalPlaceTime) )
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
def pub_placeLocators():
	_objs = mc.ls(sl=True)
	mc.select(cl=True)

	if len(_objs) > 0:
		for _obj in _objs:
			_shps = mc.listRelatives( _obj, shapes=True)
			if mc.objectType( _shps[0]) == "particle":
				_numParticles = mc.getAttr( _shps[0] + ".count" )
				_pos = mc.getAttr( _shps[0] + ".worldPosition" )
				priv_particleLocators( _numParticles, _pos)
	else:
		print "No object selected!"
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/ step 3.
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
def priv_rayIntersect(_point, _object):

	#creaza o selectie goala la care adaug obiectul meu
	_selList = om.MSelectionList()
	_selList.add(_object)
	
	_objDagPath = om.MDagPath()
	_selList.getDagPath(0, _objDagPath)

	meshFn = om.MFnMesh()
	meshFn.setObject( _objDagPath )
	
	#	 source point
	sourceWP = mc.xform(_point, q=1, rp=1, ws=1)
	raySource = om.MFloatPoint( sourceWP[0], sourceWP[1], sourceWP[2] )

	#	 direction
	rayDirection = om.MFloatVector( rnd.randint(-1, 1), rnd.randint(-1, 1), rnd.randint(-1, 1) )
	rayDirection = rayDirection.normal()

	hitFacePtr = om.MScriptUtil().asIntPtr()
	hitPoint   = om.MFloatPoint()

	idsSorted          = False
	faceIds            = None
	triIds             = None
	worldSpace         = om.MSpace.kWorld
	maxParamPtr        = 99999999
	testBothDirections = True
	accelParams        = om.MFnMesh.autoUniformGridParams()
	hitRayParam        = None
	hitTriangle        = None
	hitBary1           = None
	hitBary2           = None

	hit = meshFn.closestIntersection(raySource,
									rayDirection,
									faceIds,
									triIds,
									idsSorted,
									worldSpace,				# om.MSpace.kWorld
									maxParamPtr,			# 99999999
									testBothDirections,		# True
									accelParams,			# om.MFnMesh.autoUniformGridParams()
									hitPoint,
									hitRayParam,
									hitFacePtr,
									hitTriangle,
									hitBary1,
									hitBary2)

	if hit:

		hitFace = om.MScriptUtil ( hitFacePtr ).asInt()
		faceNumber = hitFace

		_normala = om.MVector()

		NormalFn = om.MFnMesh( _objDagPath )
		NormalFn.getPolygonNormal(faceNumber, _normala, worldSpace)
		hitFace = om.MScriptUtil ( hitFacePtr ).asInt()

		_rezult = om.MFloatVector( (sourceWP[0] - hitPoint[0]) , (sourceWP[1] - hitPoint[1]), (sourceWP[2] - hitPoint[2]))
		_dotProduct = (_rezult.x * _normala.x) + (_rezult.y * _normala.y) + ( _rezult.z * _normala.z)

#		print "dot is: %f" % _dotProduct
		if _dotProduct < 0:
			print "inSide"
#			print iter.partialPathName()
#			print "The hit point in X is %f " % hitPoint[0]
#			print "The hit point in Y is %f " % hitPoint[1]
#			print "The hit point in Z is %f " % hitPoint[2]
#			print "The number of the face hit is %d" %hitFace
#			print "The normal of the hit face is %f in x" % _normala.x
#			print "The normal of the hit face is %f in y" % _normala.y
#			print "The normal of the hit face is %f in z" % _normala.z
			return 1;
		else:
			print "outSide"
			return 0;
	else:
		print "no hit"
		#if priv_rayIntersect(_point, _object) == 0:
		return 0;
#	om.MFnMesh.freeCachedIntersectionAccelerator(meshFn)
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
def pub_cleanLocatorsMSG():
	ui_alertv("Error","In Maya 2011/2012 this step fails, please delete the locators \nfound outside your mesh by hand and the continue with step 4. \n\n\tSorry about the mess.")
	
def pub_cleanLocators():
	_sel = mc.ls(sl=True)
#START - get the number of pieces
	_pieceNumber = len(_sel) - 1
	if ( _pieceNumber <= 0):
		#print "Not enough cutting points!"
		mm.eval('error -showLineNumber False "Not enough cutting points!";')
#END - get the number of pieces
#
#START - get the object to cut and check if it`s valid
	_baseObj = _sel[ len(_sel) - 1]
	_shps = mc.listRelatives( _baseObj, shapes=True )
	for _shp in _shps:
		#print mc.objectType( _shp )
		if mc.objectType(_shp) != "mesh":
			mm.eval('error -showLineNumber False "Make sure the last object selected is a polygon object!";')
			#print "Make sure the last object selected is a polygon object!"
# END - get the object to cut and check if it`s valid
#
#
# START - clean the object for anouther round :)
	if mc.attributeQuery( 'factureCrack', node=_baseObj, ex=True) == 1:
		mc.deleteAttr( _baseObj, at='factureCrack' )
# END - clean the object for anouther round :)
#
# START - Preparing progressBar
	ui_addPB( "add", 0, "Preparing cut points...", _pieceNumber)
# END - Preparing progressBar

	_startTime = mc.timerX()

	for _i in range (0, _pieceNumber):
		_loc = _sel[_i];

		gMainProgressBar = mm.eval('$tmp = $gMainProgressBar');
		if mc.progressBar(gMainProgressBar, query=True, isCancelled=True ):
			break

		ui_addPB( "edit", 1, "Testing cut point %d/%d   " % (_i, _pieceNumber), 0)

		print "Locator " + _loc + ":"
		#priv_rayIntersect(_loc, _baseObj )
		if priv_rayIntersect(_loc, _baseObj ) == 0:
			#mc.select( _loc, replace=True )
			mc.delete( _loc )

#START - close the progressBar
	ui_addPB( "del", 0, "", 0)
#END - close the progressBar
#
#START - show some statistics
	_totalTime = mc.timerX( startTime= _startTime)
	print ("Sorting %d cutting points took %g s to complete." % (_pieceNumber, _totalTime))
#END - show some statistics
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/ step 4.
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
def priv_doCut( _way, _loc1, _loc2, _object, _crack):
	# make sure it`s a positive value, a negative value will make pieces grow and overlap
	if _crack < 0:
		_crack = 0

	_start = []
	_end = []

	if _way == 0:
		_start = mc.xform( _loc1, q=True, ws=True, t=True)
		_end = mc.xform( _loc2, q=True, ws=True, t=True )
	else:
		_start = mc.xform( _loc2, q=True, ws=True, t=True )
		_end = mc.xform( _loc1, q=True, ws=True, t=True )

	_distFactor = 0.5 + _crack
	_dir = om.MFloatVector( (_end[0] - _start[0]), (_end[1] - _start[1]), (_end[2] - _start[2]) )
	_planePos = om.MFloatVector( _start[0] + (_dir[0] * _distFactor), _start[1] + (_dir[1] * _distFactor), _start[2] + (_dir[2] * _distFactor) )

	_dir = _dir.normal()

	_xrot = - mt.degrees(mt.asin( _dir.y ))
	_yrot = mt.degrees(mt.atan2( _dir.x, _dir.z ))

	mc.select( _object, r=True )

	#mc.polyCut( constructionHistory=False, deleteFaces=True, cutPlaneCenter=( _planePos.x, _planePos.y, _planePos.z), cutPlaneRotate=( _xrot, _yrot, 0), cch=True )
	mc.polyCut( constructionHistory=False, deleteFaces=True, cutPlaneCenter=( _planePos.x, _planePos.y, _planePos.z), cutPlaneRotate=( _xrot, _yrot, 0) )
	mc.polyCloseBorder( constructionHistory=False )
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
def pub_cutAll():
	_sel = mc.ls(sl=True)
# START - get the number of pieces
	_pieceNumber = len(_sel) - 1
	if ( _pieceNumber <= 0):
		#print "Not enough cutting points!"
		mm.eval('error -showLineNumber False "Not enough cutting points!";')
# END - get the number of pieces
#
#
# START - get the object to cut and check if it`s valid
	_baseObj = _sel[-1]	# same thing with  _sel[ len(_sel) - 1]
	_shps = mc.listRelatives( _baseObj, shapes=True )
	for _shp in _shps:
#		print mc.objectType( _shp )
		if mc.objectType(_shp) != "mesh":
			#print "Make sure the last object selected is a polygon object!"
			mm.eval('error -showLineNumber False "Make sure the last object selected is a polygon object!";')
# END - get the object to cut and check if it`s valid
#
# START - ask for crack value
	_crack = 0.0;
	_retValue = ui_inputDlg("polyFracture", "Cut offset value (e.g. 0.005):", "0.0")
	if _retValue == "":
		ui_alertv( "Warning", "No value was typed ! Using default: 0" );
	else:
		if mc.about(version=True) == '2010':
			#print('2010')
			if mt.isnan( float( _retValue ) ) == False:
				_crack = float( _retValue )
		else:
			#print('2009')
			if float( _retValue ) != _crack:
				_crack = float( _retValue )
# END - ask for crack value
#
# START - ask user for visual refresh
	_visualRefresh = ui_confirm('Visual refresh', 'Do you wanna see it happening ? :)')
# END - ask user for visual refresh
#
#	 cutting timer
	_startCutTime = mc.timerX()

	_locCenter = "";
	_locToRemove = "";
	_val = -1;

#	 create a group to hold the pieces
	_grp = mc.group(em=True, name=("GRP_" + _baseObj + "_Pieces"))
	mc.xform(os=True, piv=(0, 0, 0))

#START - change current mode to select tool
#	global string $gSelect; setToolTo $gSelect;
#START - Change current selection mode to Select
#START - Preparing Maya statusbar
	ui_addPB( "add", 0, "Preparing fracture data ...", _pieceNumber)
#END - Preparing Maya statusbar
#
#
#START - deactivate undo queue if neccesary
	mc.flushUndo()
	_undoVal = mc.undoInfo( q=True, state=True )
	if _undoVal == 1:
		mc.undoInfo( state=False )
#END - deactivate undo queue if neccesary
#
#
#START - main loop
	for _i in range (0, _pieceNumber):

		gMainProgressBar = mm.eval('$tmp = $gMainProgressBar');
		if mc.progressBar( gMainProgressBar, query=True, isCancelled=True ) :
			break

		 #per piece timer
		_startTime = mc.timerX()

		_obj = mc.duplicate( _baseObj )

		for _j in range (0, _pieceNumber):

			if _i < _j:
				_val = 1
				_locCenter = _sel[_i]
				_locToRemove = _sel[_j]
			else:
				_val = 0
				_locCenter = _sel[_j]
				_locToRemove = _sel[_i]

			if _i != _j:
				priv_doCut(_val, _locCenter, _locToRemove, _obj[0], _crack)

		# add _crack attribute
		mc.addAttr( _obj[0], ln="factureCrack", at="float", keyable=False)
		mc.setAttr( _obj[0] + ".factureCrack", _crack)
		#connect the locator to the piece - later to be used if a cleaning is required
		mc.connectAttr(_obj[0] + ".displayHandle", _sel[_i] + ".displayHandle", force=True)
		mc.setAttr ( _obj[0] + ".visibility", 1)
		mc.setAttr ( _obj[0] + ".template", 0)
		#
		# rename and group
		_newName = mc.rename ( _obj[0], _baseObj + "_p_%d" % _i )
		mc.parent( _newName, _grp)

		if (_i % 10) == 0:
			mc.flushUndo()

		if _visualRefresh == True:
			mc.refresh(cv=True)

		# START - update progresBar
		_totalTime = mc.timerX( startTime= _startTime)
		ui_addPB( "edit", 1, "Calculating piece: %d/%d [ %gs ]   " % (_i, _pieceNumber, _totalTime), 0)
		# END - update progresBar
	mc.select(cl=True)
#START - close the progressBar
	ui_addPB("del", 0, "", 0)
#END - close the progressBar
#
#START - reactivate undo queue if neccesary
	if _undoVal == 1:
		mc.undoInfo( state=True )
#END - reactivate undo queue if neccesary
#
#START - show some statistics
	_totalCutTime = mc.timerX( startTime= _startCutTime)
	print ("Cutting " + _baseObj + " in %d pieces took %g s to complete." % ( _pieceNumber, _totalCutTime ))
#END - show some statistics
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
def pub_polyVoronoi():

#	_mainWn;
#	_value = mc.window( _mainWn, exists = True)
#	if _value == True:
#		mc.deleteUI( _mainWn, window = True )

#	setUITemplate -pushTemplate NONE;

	# Make a new window
	_mainWn = mc.window( maximizeButton = False,
		resizeToFitChildren = True,
		menuBar = False,
		menuBarVisible = False,
		sizeable = True,
		title = 'as_polyFracture v0.5c - Alin Sfetcu',
		iconName = 'as_polyVoronoi'
		)

	_as_pv_formLayout = mc.columnLayout( 'as_pv_formLayout',
										width = 250,
										adjustableColumn = True,
										rowSpacing = 1,
										columnAlign = 'center',
										columnAttach = ('both', 1))

	mc.text(label=' ' )
	mc.text(align='left', label='     1. select your object then press the button' )
	mc.button( label='1.place', command=('pf.pub_spawnPoints()'), parent = _as_pv_formLayout  )

	mc.text(label=' ' )
	mc.text(align='left', label='     2a. play the scene' )
	mc.text(align='left', label='     2b. select the particle and ...' )
	mc.button( label='2.spawn', command=('pf.pub_placeLocators()'), parent = _as_pv_formLayout  )

	mc.text(label=' ' )
	mc.text(align='left', label='     3. select the locators, then your object again ...' )
	mc.button( label='3.clean', command=('pf.pub_cleanLocatorsMSG()'), parent = _as_pv_formLayout  )

	mc.text(label=' ' )
	mc.text(align='left', label='     4a. ready to cut ?' )
	mc.text(align='left', label='     4b. select remaining locators, then your object ...' )
	mc.button( label='4.cut', command=('pf.pub_cutAll()'), parent = _as_pv_formLayout  )
	mc.text(label=' ' )
	mc.text(align='center', label='as_polyFracture v0.5b - Alin Sfetcu (21-oct-2010)' )

	mc.showWindow( _mainWn )
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
def pub_cutPiece(_baseObj, _locName, _crack, _sel):
	if len(_sel) == 0:
		_locs = mc.ls(sl=True)
	else:
		_locs = _sel

	_locCenter = ""
	_locToRemove = ""

	_val = -1
	_pieceNumber = len(_locs)

	for _i in range (0, _pieceNumber):

		if _locName == _locs[ _i ]:

			_obj = mc.duplicate( _baseObj )
			mc.setAttr( _obj[0] + ".visibility", 1)
			mc.setAttr( _obj[0] + ".template", 0)
			for _j in range (0, _pieceNumber):

				if _i < _j:
					_val = 1
					_locCenter = _locs[_i]
					_locToRemove = _locs[_j]
				else:
					_val = 0
					_locCenter = _locs[_j]
					_locToRemove = _locs[_i]

				if _i != _j:
					priv_doCut(_val, _locCenter, _locToRemove, _obj[0], _crack)

			# add _crack attribute
			mc.addAttr( _obj[0], ln="factureCrack", at="float", keyable=False)
			mc.setAttr( _obj[0] + ".factureCrack", _crack)
			#connect the locator to the piece - later to be used is a cleaning is required
			mc.connectAttr(_obj[0] + ".displayHandle", _locs[_i] + ".displayHandle", force=True)

			mc.setAttr( _obj[0] + ".visibility", 1)
			mc.setAttr( _obj[0] + ".template", 0)

	mc.flushUndo()
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/
def pub_cleanPiece(_baseObj):
	_sel = mc.ls(sl=True)
	_centerLoc = ''
	_pieceName = _sel[-1]
	_sel.remove( _sel[-1] )

	# daca attr exista inseamna ca este vorba de o piece
	if mc.attributeQuery( "factureCrack", node=_pieceName, exists=True ) == 1:
		_crack = mc.getAttr(_pieceName + '.factureCrack')
		#gaseste locatorul conectat la bucata
		_cons = mc.listConnections('nurbsToPoly2.displayHandle', d=True, s=False )
		if len( _cons ) > 0:
			_centerLoc = _cons[0]
			#toate bune pana aici e timpul sa inversam selectia
			_sel.reverse()
			#si taie
			pub_cutPiece(_baseObj, _centerLoc, _crack, _sel)
#/
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/


#import as_polyFracture as pf
#reload(pf)
#pf.pub_polyVoronoi()