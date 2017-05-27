# SETUP

# for experimenting in the script window
from pymel.core import *
#~~
# for scripting
import pymel.core as py
import maya.cmds as mc
import maya.mel as mel
from math import *
from xml.dom.minidom import *
from random import uniform as rnd
import os
import sys
import re
import sys as sys
import xml.etree.ElementTree as etree
from operator import itemgetter
#~~
# MayaToolbox components
from mayatoolbox import *
from shaders import *
from animation import *
from modeling import *
from paint import *
from rigging import *
from mocap import *
from dynamics import *

#~~
# more packages
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/PIL/')
#sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/numpy/')