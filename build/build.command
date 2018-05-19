#!/bin/bash

BUILD_TARGET="../mayatoolbox.py"

cd $PWD

rm $BUILD_TARGET
touch $BUILD_TARGET

cat "mayatoolbox_main.py" "mayatoolbox_animation.py" "mayatoolbox_dynamics.py" "mayatoolbox_mocap.py" "mayatoolbox_modeling.py" "mayatoolbox_paint.py" "mayatoolbox_rigging.py" "mayatoolbox_shaders.py" > $BUILD_TARGET

#cp $BUILD_TARGET "/Applications/Adobe After Effects CS6/Scripts/ScriptUI Panels/"

#cp * ~/Library/Preferences/Autodesk/maya/2017/scripts/
#cp icons/* ~/Library/Preferences/Autodesk/maya/2017/prefs/icons
#cp shelves/* ~/Library/Preferences/Autodesk/maya/2017/prefs/shelves

