#!/usr/bin/env bash
# Chrome Bridge — Install auto-start via Windows Startup folder
# No admin rights needed. Places a VBS launcher shortcut in Startup folder.
# Usage: bash install_service.sh

# Determine script and project directories
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LAUNCHER="$SCRIPT_DIR/launch_silent.vbs"
STARTUP_DIR="$APPDATA/Microsoft/Windows/Start Menu/Programs/Startup"
SHORTCUT="$STARTUP_DIR/ChromeBridge.lnk"

echo "=========================================="
echo "  Install Chrome Bridge Auto-Start"
echo "=========================================="

# 1. Check VBS launcher
if [ ! -f "$LAUNCHER" ]; then
  echo "[ERROR] VBS launcher not found: $LAUNCHER"
  exit 1
fi
echo "[OK] VBS launcher found"

# 2. Remove old shortcut if exists
rm -f "$SHORTCUT"
echo "[OK] Cleaned old shortcut"

# 3. Create shortcut using PowerShell
powershell -NoProfile -Command "
  \$ws = New-Object -ComObject WScript.Shell
  \$s  = \$ws.CreateShortcut('$SHORTCUT')
  \$s.TargetPath = 'wscript.exe'
  \$s.Arguments  = '\"$LAUNCHER\"'
  \$s.WindowStyle = 7
  \$s.Description = 'Chrome Bridge'
  \$s.Save()
"
if [ $? -eq 0 ]; then
  echo "[OK] Shortcut created in Startup folder"
else
  echo "[ERROR] Failed to create shortcut"
  exit 1
fi

# 4. Launch immediately
echo "[START] Launching bridge now..."
wscript.exe "$LAUNCHER"
sleep 3

# 5. Verify
echo ""
bash "$SCRIPT_DIR/status_bridge.sh"

echo ""
echo "=========================================="
echo "  Done! Bridge will auto-start on login."
echo "=========================================="
echo ""
echo "  Startup: $SHORTCUT"
echo "  To remove: delete that shortcut file"
echo ""
