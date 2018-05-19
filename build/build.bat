@echo off

cd %~dp0

set BUILD_TARGET=..\mayatoolbox.py

del %BUILD_TARGET%

copy /b mayatoolbox_main.py+mayatoolbox_animation.py+mayatoolbox_dynamics.py+mayatoolbox_mocap.py+mayatoolbox_modeling.py+mayatoolbox_paint.py+mayatoolbox_rigging.py+mayatoolbox_shaders.py %BUILD_TARGET%

rem copy %BUILD_TARGET% "C:\Program Files\Adobe\Adobe After Effects CS6\Support Files\Scripts\ScriptUI Panels\"

@pause