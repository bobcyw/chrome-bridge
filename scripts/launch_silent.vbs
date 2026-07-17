' Chrome Bridge - Silent Launcher (Windows)
' Auto-detects Python and launches server without a console window.
' Place a shortcut to this file in your Startup folder for auto-start.

Dim WshShell, pythonPath, projectDir, cmd, result

Set WshShell = CreateObject("WScript.Shell")

' ── Get project directory (same folder as this script) ──
projectDir = WshShell.CurrentDirectory
If Right(projectDir, 7) = "scripts" Then
    projectDir = Left(projectDir, Len(projectDir) - 7)
End If

' ── Try to find Python ──
pythonPath = "python"  ' fallback

' Try: where python
On Error Resume Next
Dim exec, output
Set exec = WshShell.Exec("cmd /c where python 2>nul")
output = exec.StdOut.ReadAll()
If exec.ExitCode = 0 And output <> "" Then
    pythonPath = Trim(Split(output, vbCrLf)(0))
End If
On Error Goto 0

' ── Launch ──
cmd = """" & pythonPath & """ -u """ & projectDir & "\bridge\server.py"" >> """ & projectDir & "\runtime\server.log"" 2>&1"

Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FolderExists(projectDir & "\runtime") Then
    fso.CreateFolder projectDir & "\runtime")
End If

' Run hidden: 0 = hide window, False = don't wait
WshShell.Run "cmd /c " & cmd, 0, False
