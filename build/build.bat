@echo off

cd %~dp0

set BUILD_TARGET=..\mayatoolbox.py

del %BUILD_TARGET%

copy /b mayatoolbox_main.py+mayatoolbox_animation.py+mayatoolbox_dynamics.py+mayatoolbox_mocap.py+mayatoolbox_modeling.py+mayatoolbox_paint.py+mayatoolbox_rigging.py+mayatoolbox_shaders.py %BUILD_TARGET%

copy %BUILD_TARGET% %homepath%\Documents\maya\2018\scripts\

rem set TARGET=%homepath%\Documents\maya\2018\

rem xcopy /s /y *.py  %TARGET%scripts\
rem xcopy /s /y *.mel  %TARGET%prefs\
rem xcopy /s /y *.txt  %TARGET%scripts\
rem xcopy /s /y *.png  %TARGET%prefs\
rem xcopy /s /y *.psd  %TARGET%prefs\
rem xcopy /s /y *.ico  %TARGET%prefs\

@pause