' Chrome Bridge - Silent Launcher
' Launches bridge_server.py without a console window
'
' EDIT THIS FILE to set your Python path before first use:
'   1. Run "where python" in terminal to find your Python path
'   2. Replace PYTHON_PATH below
'   3. Replace PROJECT_DIR below with the path to this project

Dim PYTHON_PATH, PROJECT_DIR, cmd

' === CONFIGURE THESE PATHS ===
PYTHON_PATH = "python"
PROJECT_DIR = CreateObject("WScript.Shell").CurrentDirectory

' === DO NOT EDIT BELOW ===
cmd = PYTHON_PATH & " -u """ & PROJECT_DIR & "\bridge\server.py"" >> """ & PROJECT_DIR & "\runtime\server.log"" 2>&1"

Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
' Run hidden (0 = hide window, False = don't wait for exit)
WshShell.Run cmd, 0, False
