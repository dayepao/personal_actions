@echo off
title uiÎÄ¼þ×ª»»
:ui2py
for %%i in (*.ui) do (
    pyuic6 -o "%%~ni.py" "%%i"
)