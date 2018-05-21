from pymel.core import *
"""
                        Maya Bezier Curve Import Overview

    Maya -- curve( p=[(...), (...), (...), (...)], k = [...], d=3 )
                        |                  | |            |
                        |   relative-------| |            ------- numCVs + deg -1
                       abs  |             (x y) + prev(x y)
                        |   |              | |
    SVG  -- <path d =" (C ? c) x2 y2 x1 y1 x y"/>

                                            http://www.w3.org/TR/SVG/paths.html#PathDataGeneralInformation
"""
"""
07/16/2010 -- Mike Ton (mike.ton@gmail.com)
"""

def main_CurvefromSVG(degree):
    """
    main : Load File -> filter SVG Data to Maya's format -> passes xformed data to Maya cmd
    """
    tokens = loadFile("svg")
    SVG = tokenToSVG(tokens)
    curvePosArray = SVGtoArray(SVG)
    numCVs = 0
    for entry in SVG.arrLength:
        numCVs += entry
    arrKnot = genBzKnot(numCVs/2, degree)
    curve( p=curvePosArray, k =arrKnot) 

class objSVG(object):
    """
    objSVG holds primary SVG data: cmdKeywords, CVpos and numofCVpos between cmdKeywords
    """
    def __init__(self):
        self.arrCmd        = []    #m/M/c/C - move, curve(bezier): up-abs pos, low-relative pos
        self.arrLength     = []    #Count of pos data between cmds
        self.arrPos        = []    #array of xy position
        print 'objSVG init!'        
    def echo(self):
        print self.arrCmd, self.arrLength, self.arrPos, self

def genBzKnot(numofCV, degree):
    """
    generates Knot array -> numof CVs + degree -1
    """
    numofKnots = numofCV + degree - 1
    result = []
    knot = 0
    for i in range(numofKnots):
        result.append(knot)
        if(i%3 >= 2):
            knot += 1
    return result 
    
def getSVGpath(filePath):
    """
    reads SVG file, and filters <path.../> data
    """
    openfile = open(filePath, 'r')
    textFile = openfile.read()
    openfile.close()
    textSel = re.search('<path[^/>]*..', textFile).group()
    textPathPos = re.search('d="[^"]*', textSel).group()
    tokens = re.split('[\s,"]', textPathPos)
    return tokens

def loadFile(filterExt):
    """
    file Dialog -> user specifies path to SVG file
    """
    basicFilter = "*." + filterExt
    filePath = fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=1)
    if(filePath != None):
        #openfile = open('/Users/camtton/Desktop/drawing.svg', 'r')
        tokens = getSVGpath(filePath[0])
        return tokens
    else:
        print 'Please select a %s file'%(filterExt)

def tokenToSVG(tokens):
    """
    inits objSVG and fills with data: cmdKeywords, CVpos and numofCVpos between cmdKeywords 
    """
    SVG = objSVG()
    for i in range(1, len(tokens)):    #Hack: Setting start to 1 skips having to deal with filtering "d="
        if(tokens[i].lower() == 'm') or (tokens[i].lower() == 'c')  :  
            SVG.arrCmd.append(tokens[i])
            SVG.arrLength.append(0)     
        else:    
            SVG.arrPos.append(float(tokens[i]))        #cast to float
            SVG.arrLength[len(SVG.arrLength)-1] += 1   #increment length of current pos data
    SVG.echo()
    return SVG

def SVGtoArray(SVG):
    """        
    xform SVG data (abs/rel position) to Maya Curve command
    """
    t = {
            'posXform': [0,0],    #store return/xform pos
            'posPrev' : [0,0],    #store prev pos here
            'off'     : 0,        #offset
        }
    curvePosArray = []
    for i in range(len(SVG.arrCmd)):
        if i > 0 :
            t['off'] += SVG.arrLength[i-1]
        for j in range(SVG.arrLength[i]):
            jj = j + t['off']
            switch = j%2        #modulate between 0 and 1
            xformPos = SVG.arrPos[jj] + t['posPrev'][switch]
            if (SVG.arrCmd[i] == 'M') or (SVG.arrCmd[i] == 'C'):
                #True = data is abs: store values
                t['posXform'][switch] = SVG.arrPos[jj]
            else:
                #False = data is relative: xform, then store values
                t['posXform'][switch] = xformPos    
                if (SVG.arrCmd[i] == 'm'):    
                    t['posPrev'][switch] = xformPos
                else:
                    bez = j%6
                    if bez >= 4:
                        t['posPrev'][switch] = xformPos
            if switch == 1 :
                curvePos = (t['posXform'][0], t['posXform'][1], 0)
                curvePosArray.append(curvePos)
            if switch == 0 : print ""
            print SVG.arrCmd[i], SVG.arrLength[i], i, j, SVG.arrPos[jj]
    return curvePosArray
    
#main_CurvefromSVG(3)
#tokens = getSVGpath('/Users/camtton/Desktop/drawing.svg')