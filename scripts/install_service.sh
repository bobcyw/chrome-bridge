#!/usr/bin/env bash
# Chrome Bridge — cross-platform auto-start installer
# Usage: bash install_service.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/runtime/server.log"

detect_os() {
    case "$(uname -s)" in
        Darwin)  echo "macos" ;;
        Linux)   echo "linux" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *)       echo "unknown" ;;
    esac
}

OS=$(detect_os)
echo "=========================================="
echo "  Chrome Bridge — Auto-Start Installer"
echo "  OS: $OS"
echo "=========================================="

# ── macOS: LaunchAgent ─────────────────────────────────────────
install_macos() {
    local plist_src="$SCRIPT_DIR/com.chrome-bridge.plist"
    local plist_dst="$HOME/Library/LaunchAgents/com.chrome-bridge.plist"
    local python_path
    python_path=$(command -v python3 || command -v python)

    echo "[*] Installing macOS LaunchAgent..."

    # Ensure runtime dir
    mkdir -p "$PROJECT_DIR/runtime"

    # Build plist with actual paths
    cat > "$plist_dst" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.chrome-bridge</string>
    <key>ProgramArguments</key>
    <array>
        <string>$python_path</string>
        <string>-u</string>
        <string>$PROJECT_DIR/bridge/server.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key>
    <string>$LOG_FILE</string>
    <key>StandardErrorPath</key>
    <string>$LOG_FILE</string>
</dict>
</plist>
EOF

    # Unload old, load new
    launchctl unload "$plist_dst" 2>/dev/null || true
    launchctl load "$plist_dst"

    echo "[OK] LaunchAgent installed and loaded"
    echo "  Config: $plist_dst"
    echo "  Log:    $LOG_FILE"
    echo "  To stop: launchctl unload $plist_dst"
}

# ── Linux: systemd user unit ───────────────────────────────────
install_linux() {
    local unit_dir="$HOME/.config/systemd/user"
    local unit_file="$unit_dir/chrome-bridge.service"
    local python_path
    python_path=$(command -v python3 || command -v python)

    echo "[*] Installing Linux systemd user unit..."

    mkdir -p "$unit_dir" "$PROJECT_DIR/runtime"

    cat > "$unit_file" << EOF
[Unit]
Description=Chrome Bridge — AI-to-Browser relay
After=network.target

[Service]
Type=simple
ExecStart=$python_path -u $PROJECT_DIR/bridge/server.py
WorkingDirectory=$PROJECT_DIR
Restart=on-failure
RestartSec=5
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

[Install]
WantedBy=default.target
EOF

    systemctl --user daemon-reload
    systemctl --user enable chrome-bridge.service
    systemctl --user restart chrome-bridge.service

    echo "[OK] systemd user unit installed and started"
    echo "  Config: $unit_file"
    echo "  Status: systemctl --user status chrome-bridge"
    echo "  Log:    $LOG_FILE"
    echo "  To stop: systemctl --user stop chrome-bridge"

    # Enable lingering if needed (allow user services to run at boot)
    if command -v loginctl &>/dev/null; then
        loginctl enable-linger "$USER" 2>/dev/null || true
    fi
}

# ── Windows: Startup folder shortcut ───────────────────────────
install_windows() {
    local launcher="$SCRIPT_DIR/launch_silent.vbs"
    local startup_dir="$APPDATA/Microsoft/Windows/Start Menu/Programs/Startup"
    local shortcut="$startup_dir/ChromeBridge.lnk"

    echo "[*] Installing Windows Startup shortcut..."

    if [ ! -f "$launcher" ]; then
        echo "[ERROR] VBS launcher not found: $launcher"
        exit 1
    fi

    rm -f "$shortcut"
    powershell -NoProfile -Command "
        \$ws = New-Object -ComObject WScript.Shell
        \$s  = \$ws.CreateShortcut('$shortcut')
        \$s.TargetPath = 'wscript.exe'
        \$s.Arguments  = '\"$launcher\"'
        \$s.WindowStyle = 7
        \$s.Description = 'Chrome Bridge'
        \$s.Save()
    "

    # Start immediately
    echo "[START] Launching now..."
    wscript.exe "$launcher" 2>/dev/null || true

    echo "[OK] Startup shortcut created"
    echo "  Shortcut: $shortcut"
    echo "  To remove: delete $shortcut"
}

# ── Run ────────────────────────────────────────────────────────
case "$OS" in
    macos)   install_macos ;;
    linux)   install_linux ;;
    windows) install_windows ;;
    *)
        echo "[ERROR] Unsupported OS: $(uname -s)"
        echo "  See README.md for manual setup instructions."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  Done! Bridge will auto-start on login."
echo "=========================================="
