#!/usr/bin/env bash
# Chrome Bridge — cross-platform status check
# Usage: bash status_bridge.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLI_PATH="$PROJECT_DIR/bridge/cli.py"
LOG_FILE="$PROJECT_DIR/runtime/server.log"
PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" &>/dev/null || PYTHON="python"

echo "=========================================="
echo "  Chrome Bridge — Status"
echo "=========================================="
echo ""

# 1. HTTP API
if "$PYTHON" -c "
import socket; s=socket.socket(); s.settimeout(0.3)
try: s.connect(('127.0.0.1',19877)); s.close(); exit(0)
except: exit(1)
" 2>/dev/null; then
    echo "[OK] HTTP API  http://127.0.0.1:19877"
else
    echo "[FAIL] HTTP API not running"
    echo "  Start: bash $SCRIPT_DIR/start_bridge.sh --background"
    exit 1
fi

# 2. WebSocket
if "$PYTHON" -c "
import socket; s=socket.socket(); s.settimeout(0.3)
try: s.connect(('127.0.0.1',19876)); s.close(); exit(0)
except: exit(1)
" 2>/dev/null; then
    echo "[OK] WebSocket  ws://127.0.0.1:19876"
else
    echo "[WARN] WebSocket not listening"
fi

# 3. Ping
echo ""
echo "[TEST] Full pipeline ping..."
RESULT=$("$PYTHON" "$CLI_PATH" ping 2>&1 || true)
if echo "$RESULT" | grep -q '"pong": true'; then
    echo "[OK] All systems go!"
elif echo "$RESULT" | grep -q "No Chrome extension"; then
    echo "[WARN] Server OK, but no extension connected"
    echo "  → Click the Chrome Bridge icon in Chrome toolbar"
    echo "  → Or reload extension at chrome://extensions"
elif echo "$RESULT" | grep -q "Cannot connect"; then
    echo "[FAIL] Server not reachable. Start it first."
else
    echo "[FAIL] Ping failed: $RESULT"
fi
echo ""
