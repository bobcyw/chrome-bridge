#!/usr/bin/env bash
# Chrome Bridge — cross-platform startup script
# Usage: bash start_bridge.sh [--background]
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BRIDGE_SCRIPT="$PROJECT_DIR/bridge/server.py"
LOG_FILE="$PROJECT_DIR/runtime/server.log"
PYTHON="${PYTHON:-python3}"
# macOS: python3 is typical; fall back to python
command -v "$PYTHON" &>/dev/null || PYTHON="python"

# ── Helpers ──

port_in_use() {
    "$PYTHON" -c "
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.3)
try:
    s.connect(('127.0.0.1', int(sys.argv[1])))
    s.close()
    exit(0)
except:
    exit(1)
" "$1" 2>/dev/null
}

# ── Main ──

echo "=========================================="
echo "  Chrome Bridge — Startup"
echo "=========================================="

# 1. Python
if ! command -v "$PYTHON" &>/dev/null; then
    echo "[ERROR] Python not found. Install Python 3.10+ from https://python.org"
    exit 1
fi
echo "[OK] $($PYTHON --version 2>&1)"

# 2. websockets
if ! "$PYTHON" -c "import websockets" 2>/dev/null; then
    echo "[SETUP] Installing websockets..."
    "$PYTHON" -m pip install websockets -q
fi
echo "[OK] websockets available"

# 3. Runtime dir
mkdir -p "$PROJECT_DIR/runtime"

# 4. Already running?
if port_in_use 19877; then
    echo "[INFO] Server already running (port 19877 in use)"
    echo "  Stop the existing server first, or use: chrome-bridge ping"
    exit 0
fi

# 5. Start
if [ "${1:-}" = "--background" ] || [ "${1:-}" = "-b" ]; then
    echo "[START] Launching in background..."
    nohup "$PYTHON" -u "$BRIDGE_SCRIPT" > "$LOG_FILE" 2>&1 &
    PID=$!
    sleep 2
    if port_in_use 19877; then
        echo "[OK] Server started (PID: $PID)"
        echo "  Log: $LOG_FILE"
    else
        echo "[ERROR] Server failed to start. Check log:"
        tail -10 "$LOG_FILE" 2>/dev/null
        exit 1
    fi
else
    echo "[START] Launching (Ctrl+C to stop)..."
    exec "$PYTHON" -u "$BRIDGE_SCRIPT"
fi
