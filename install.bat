@echo off

set TARGET=%homepath%\Documents\maya\2018\

cd %cd%

xcopy /s /y *.py  %TARGET%scripts\
xcopy /s /y *.mel  %TARGET%prefs\
xcopy /s /y *.txt  %TARGET%scripts\
xcopy /s /y *.png  %TARGET%prefs\
xcopy /s /y *.psd  %TARGET%prefs\
xcopy /s /y *.ico  %TARGET%prefs\

@pause