@echo off

set TARGET="%homepath%\Documents\maya\2016\scripts"

cd %cd%

xcopy /s /y *.*  %TARGET%

@pause