@echo off

set TARGET1="%homepath%\Documents\maya\2016\scripts"
set TARGET2="%homepath%\Documents\maya\2017\scripts"

cd %cd%

xcopy /s /y *.*  %TARGET1%
xcopy /s /y *.*  %TARGET2%

@pause