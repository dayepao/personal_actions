@echo off
title ui�ļ�ת��
:ui2py
for %%i in (*.ui) do (
    pyside6-uic -o "%%~ni.py" "%%i"
)