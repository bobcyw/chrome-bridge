#!/usr/bin/env bash
# Chrome Bridge — one-click startup script
# Usage: bash start_bridge.sh [--background]
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BRIDGE_SCRIPT="$PROJECT_DIR/bridge/server.py"
LOG_FILE="$PROJECT_DIR/runtime/server.log"
PYTHON="${PYTHON:-python}"

echo "=========================================="
echo "  Chrome Bridge — Startup"
echo "=========================================="

# 1. Check Python
if ! command -v "$PYTHON" &>/dev/null; then
  echo "[ERROR] Python not found: $PYTHON"
  echo "  Install Python 3.10+ from https://python.org"
  exit 1
fi
echo "[OK] $( $PYTHON --version 2>&1 )"

# 2. Check websockets
if ! "$PYTHON" -c "import websockets" 2>/dev/null; then
  echo "[SETUP] Installing websockets..."
  "$PYTHON" -m pip install websockets -q
fi
echo "[OK] websockets available"

# 3. Create runtime dir
mkdir -p "$PROJECT_DIR/runtime"

# 4. Check if already running
if netstat -ano 2>/dev/null | grep -q ":19876.*LISTEN"; then
  echo "[INFO] Server already running on port 19876"
  echo "  To restart: kill the process first"
  exit 0
fi

# 5. Start
if [ "${1:-}" = "--background" ] || [ "${1:-}" = "-b" ]; then
  echo "[START] Launching in background..."
  nohup "$PYTHON" -u "$BRIDGE_SCRIPT" > "$LOG_FILE" 2>&1 &
  echo "[OK] PID: $!"
else
  echo "[START] Launching server (Ctrl+C to stop)..."
  exec "$PYTHON" -u "$BRIDGE_SCRIPT"
fi
