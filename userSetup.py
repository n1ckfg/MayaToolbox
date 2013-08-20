from pymel.core import *
from xml.dom.minidom import *
from random import uniform as rnd
import os

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GENERAL

def t(_t):
	currentTime(_t)

def getPos():
	target = ls(sl=1)
	p = xform(target[0], q=True, t=True, ws=True)
	return p

def showHide():
	target = ls(sl=1)

	for i in range(0,len(target)):
	    visible = getAttr(target[i] + ".v")
	    if(visible==False):
	       setAttr(target[i] + ".v",1)
	    if(visible==True):
	       setAttr(target[i] + ".v",0) 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SHADERS

def createShader(shaderType,shaderColor,useTexture):
	#1. get selection
	target = ls(sl=True)
	#2. initialize shader
	shader=shadingNode(shaderType,asShader=True)
	#3. create a file texture node
	if(useTexture==True):
		file_node=shadingNode("file",asTexture=True)
	#4. create a shading group
	shading_group= sets(renderable=True,noSurfaceShader=True,empty=True)
	#5. set the color
	setRGBA(shader,shaderColor)
	#6. connect shader to sg surface shader
	connectAttr('%s.outColor' %shader ,'%s.surfaceShader' %shading_group)
	#7. connect file texture node to shader's color
	if(useTexture==True):
		connectAttr('%s.outColor' %file_node, '%s.color' %shader)
	#9. restore selection
	select(target)
	#10. return the completed shader
	return shader

def setShader(shader):
	hyperShade(a=shader)

def getShader():
	# get shapes of selection:
	shapesInSel = ls(dag=1,o=1,s=1,sl=1)
	# get shading groups from shapes:
	shadingGrps = listConnections(shapesInSel,type='shadingEngine')
	# get the shaders:
	shader = ls(listConnections(shadingGrps),materials=1)
	return shader[0] 

def quickShader(shaderColor):
	if(len(shaderColor)==3):
		shaderColor.append(255)
    shader = createShader("lambert",shaderColor,False)
	setShader(shader)
	return shader

#~~

#set RGBA, RGB, A at shader level
def setRGBA(s,c):
	r = float(c[0]) / 255.0
	g = float(c[1]) / 255.0
	b = float(c[2]) / 255.0
	a = abs(1-(float(c[3]) / 255.0))
	setAttr(s + ".color", (r,g,b))
	setAttr(s + ".transparency", (a,a,a))

def setRGB(s,c):
	r = float(c[0]) / 255.0
	g = float(c[1]) / 255.0
	b = float(c[2]) / 255.0
	setAttr(s + ".color", (r,g,b))

def setA(s,c):
	a = abs(1-(float(c) / 255.0))
	setAttr(s + ".transparency", (a,a,a))	

#~~

# set RGB color 0-255, any number of selections
def setColor(c):
	target = ls(sl=1)
	for i in range(0,len(target)):
		select(target[i])
		s = getShader()
		r = float(c[0]) / 255.0
		g = float(c[1]) / 255.0
		b = float(c[2]) / 255.0
		setAttr(s + ".color", (r,g,b))		

# returns RGB color 0-255 of first selection
def getColor():
	target = ls(sl=1)
	select(target[0])
	s = getShader()
	c = getAttr(s + ".color")	
	r = float(c[0]) / 255.0
	g = float(c[1]) / 255.0
	b = float(c[2]) / 255.0
	return (r,g,b)
#~~

# set transparency 0-255, any number of selections
def setAlpha(c):
	target = ls(sl=1)
	for i in range(0,len(target)):
		select(target[i])
		s = getShader()
		a = abs(1-(float(c) / 255.0))
		setAttr(s + ".transparency", (a,a,a))	

# returns transparency 0-255 from first selection
def getAlpha():
	target = ls(sl=1)
	select(target[0])
	s = getShader()
	aa = getAttr(s + ".transparency")
	a = 255 * abs(1-aa[0])
	return a

# keyframe transparency 0-255, any number of selections
def keyAlpha(c):
	target = ls(sl=1)
	for i in range(0,len(target)):
		select(target[i])
		s = getShader()
		setA(s,c)
		mel.eval("setKeyframe { \"" + s + ".it\" };")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# JOINTS

def keyAllJoints():
	target=ls(sl=1)

	for i in range(0,len(target)):
		select(target[i])
		setKeyframe()

		try:
			kids = listRelatives(ls(selection=True), children=True, type="joint", allDescendents=True)
			for k in kids:
				select(k)
				setKeyframe()
		except:
			print "No child joints."

	select(target)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODELING

def booleanLoop():
	#1. Make an array of all selections
	target = ls(sl=True)

	#2. Boolean union each item in the array to the next
	for i in range(0,len(target)-1,2):
	    polyBoolOp(target[i],target[i+1])
	    
	    #3. Delete construction history
	    delete(ch=True)

	    #4. Recenter the pivot
	    xform(cp=True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCATORS

def addLocator():
	#1. make an array of all selected objects
	target = ls(sl=True)

	#2. if no selection, just make a locator at 0,0,0...
	if(len(target)==0):
		spaceLocator()

	else:
		#3. otherwise, for each selected object...
		for i in range(0,len(target)):
		
			#4. ...if there are child joints, give them locators too
			try:
				kids = listRelatives(ls(selection=True), children=True, type="joint", allDescendents=True)
				for k in kids:
					locName = k + "_loc"
					locPos = xform(k, q=True, t=True, ws=True)
					loc = spaceLocator(n=locName)
					move(locPos[0],locPos[1],locPos[2])
			except:
				print "No child joints."

			#5. get the original selection's name
			locName = target[i] + "_loc"
		
			#6. get its position
			locPos = xform(target[i], q=True, t=True, ws=True)
		
			#7. create a new locator with that name at that position
			loc = spaceLocator(n=locName)
			move(locPos[0],locPos[1],locPos[2])
#~~

def moveToSelected():
	#1. make an array of all selected objects
	target = ls(sl=True)

	#2. get the position of the last selected object
	pos = xform(target[len(target)-1], q=True, t=True, ws=True)

	#3. move the other objects to the last selected object
	for i in range(0,len(target)-1):
		select(target[i])
		move(pos[0],pos[1],pos[2])
		
#~~

def showHide():
	target = ls(sl=1)

	for i in range(0,len(target)):
		visible = getAttr(target[i] + ".v")
		if(visible==False):
			setAttr(target[i] + ".v",1)
		if(visible==True):
			setAttr(target[i] + ".v",0) 
			
#~~

def parentLast():
	#1. make an array of all selected objects
	target = ls(sl=True)

	#2. parent each selected object to the last object
	for i in range(0,len(target)-1):
		select(target[i])
		parent(target[i],target[len(target)-1])


	#3. select last object
	select(target[len(target)-1])
	
#~~

def instanceFirst(doShaders):
	#1. make an array of all selected objects
	target = ls(sl=True)

	#2. if only one selection, just make a new instance at the same coordinates...
	if(len(target)==1):
		instance()

	else:
		#3. ...otherwise, for each selected object...
		for i in range(1,len(target)):

			#4. ...get current selection's position and copy keyframes and shader
			select(target[i])
			pos = xform(target[i], q=True, t=True, ws=True)
			shader = getShader()
			try:
				copyKey()
			except:
				print "Couldn't copy keys."

			#5. instance the first selection
			select(target[0])
			instance()
		
			#6. move first selection to position and paste keyframes and shader
			move(pos[0],pos[1],pos[2])
			if(doShaders==True):
				setShader(shader)
			try:
				pasteKey()
			except:
				print "Couldn't paste keys."
		   
			#7. delete selection
			delete(target[i])

#~~

def duplicateFirst(doShaders):
	#1. make an array of all selected objects
	target = ls(sl=True)

	#2. if only one selection, just make a new duplicate at the same coordinates...
	if(len(target)==1):
		#call through mel because python has no rc option!
		mel.eval("duplicate -un -ic -rc")

	else:
		try:
			#3. check if the first selection is skinned.
			select(target[0])
			skinCluster(q=True)
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			print "Select the root joint for this to work properly."
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		except:
			#4. ...otherwise, for each selected object...
			for i in range(1,len(target)):

				#5. ...get current selection's position and copy keyframes and shader
				select(target[i])
				pos = xform(target[i], q=True, t=True, ws=True)
				shader = getShader()
				try:
					copyKey()
				except:
					print "Couldn't copy keys."

				#6. duplicate the first selection
				select(target[0])
				#call through mel because python has no rc option!
				mel.eval("duplicate -un -ic -rc")
			
				#7. move first selection to position and paste keyframes and shader
				move(pos[0],pos[1],pos[2])
				if(doShaders==True):
					setShader(shader)
				try:
					pasteKey()
				except:
					print "Couldn't paste keys."
			   
				#8. delete selection
				delete(target[i])
				
#~~


def duplicateSpecial():
	#1. make an array of all selected objects
	target = ls(sl=True)

	#2. for each selected object...
	for i in range(0,len(target)):
		#3. ...select and duplicated with bones and keyframes
		select(target[i])
		#call through mel because python has no rc option!
		mel.eval("duplicate -un -ic -rc")



