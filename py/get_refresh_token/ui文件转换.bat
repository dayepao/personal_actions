@echo off
title ui�ļ�ת��
:ui2py
for %%i in (*.ui) do (
    pyuic6 -o "%%~ni.py" "%%i"
)