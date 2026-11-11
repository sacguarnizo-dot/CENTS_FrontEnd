@echo off
set KIVY_HOME=%~dp0.kivy

if exist "C:\Users\I.L.M\AppData\Local\Programs\Python\Python310\python.exe" (
    "C:\Users\I.L.M\AppData\Local\Programs\Python\Python310\python.exe" "%~dp0principal.py"
) else (
    python "%~dp0principal.py"
)
pause
