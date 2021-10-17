@echo off
title uiÎÄ¼þ×ª»»
:ui2py
for %%i in (*.ui) do (
    pyside6-uic -o "%%~ni.py" "%%i"
)