#!/usr/bin/env bash
# Chrome Bridge — one-click startup script
# Checks prerequisites and starts the bridge server
# Usage: bash start_bridge.sh

set -e

# Determine script and project directories
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BRIDGE_SCRIPT="$PROJECT_DIR/bridge/server.py"
RUNTIME_DIR="$PROJECT_DIR/runtime"
LOG_FILE="$RUNTIME_DIR/server.log"

# Use Python from PATH, allow override via PYTHON env var
PYTHON="${PYTHON:-python}"

echo "=========================================="
echo "  Chrome Bridge — Startup"
echo "=========================================="

# 1. Check Python
if ! command -v "$PYTHON" &>/dev/null; then
  echo "[ERROR] Python not found: $PYTHON"
  echo "  Install Python 3.10+ and ensure it's in PATH."
  exit 1
fi
echo "[OK] Python found: $($PYTHON --version 2>&1)"

# 2. Check websockets package
if ! "$PYTHON" -c "import websockets" 2>/dev/null; then
  echo "[SETUP] Installing websockets package..."
  "$PYTHON" -m pip install websockets -q
  echo "[OK] websockets installed"
else
  echo "[OK] websockets package available"
fi

# 3. Check bridge script
if [ ! -f "$BRIDGE_SCRIPT" ]; then
  echo "[ERROR] Bridge server not found: $BRIDGE_SCRIPT"
  echo "  Make sure you're running this script from the chrome-bridge project directory."
  exit 1
fi
echo "[OK] Bridge server: $BRIDGE_SCRIPT"

# 4. Create runtime directory
mkdir -p "$RUNTIME_DIR"
echo "[OK] Runtime directory: $RUNTIME_DIR"

# 5. Check if server is already running
PORT_CHECK=$(netstat -ano 2>/dev/null | grep ":9876.*LISTEN" | head -1)
if [ -n "$PORT_CHECK" ]; then
  echo "[INFO] Bridge server already running on port 9876"
  echo "  $PORT_CHECK"
  echo ""
  echo "  To restart: kill the process first, then run this script again."
  echo "  To check status: bash $SCRIPT_DIR/status_bridge.sh"
  exit 0
fi

# 6. Start server
echo "[START] Launching bridge server..."
nohup "$PYTHON" -u "$BRIDGE_SCRIPT" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "[OK] Server started (PID: $SERVER_PID)"

# 7. Wait and verify
sleep 2
if netstat -ano 2>/dev/null | grep -q ":9876.*LISTEN"; then
  echo "[OK] Server listening on ws://127.0.0.1:9876"
  echo ""
  echo "=========================================="
  echo "  Bridge is ready!"
  echo "=========================================="
  echo ""
  echo "  Log file: $LOG_FILE"
  echo "  Status:   bash $SCRIPT_DIR/status_bridge.sh"
  echo ""
  echo "  Next: Make sure the Chrome extension is loaded"
  echo "  and the Service Worker is active."
  echo ""
else
  echo "[ERROR] Server failed to start. Check log:"
  cat "$LOG_FILE" 2>/dev/null
  exit 1
fi
