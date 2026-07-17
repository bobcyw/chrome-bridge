#!/usr/bin/env bash
# Chrome Bridge — status check
# Usage: bash status_bridge.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLI_PATH="$PROJECT_DIR/bridge/cli.py"
LOG_FILE="$PROJECT_DIR/runtime/server.log"
PYTHON="${PYTHON:-python}"

echo "=========================================="
echo "  Chrome Bridge — Status"
echo "=========================================="
echo ""

# 1. HTTP API
if netstat -ano 2>/dev/null | grep -q ":19877.*LISTEN"; then
  echo "[OK] HTTP API  http://127.0.0.1:19877"
else
  echo "[FAIL] HTTP API not running"
  echo "  Start: bash $SCRIPT_DIR/start_bridge.sh --background"
  exit 1
fi

# 2. WebSocket
if netstat -ano 2>/dev/null | grep -q ":19876.*LISTEN"; then
  echo "[OK] WebSocket  ws://127.0.0.1:19876"
else
  echo "[WARN] WebSocket not listening"
fi

# 3. Extension connection
if netstat -ano 2>/dev/null | grep -q ":19876.*ESTABLISHED"; then
  echo "[OK] Chrome extension connected"
else
  echo "[WARN] Chrome extension NOT connected"
  echo "  → Click the Chrome Bridge icon in Chrome toolbar"
  echo "  → Or reload at chrome://extensions"
  echo ""
  tail -3 "$LOG_FILE" 2>/dev/null
fi

# 4. Ping
echo ""
echo "[TEST] Full pipeline ping..."
RESULT=$("$PYTHON" "$CLI_PATH" ping 2>&1)
if echo "$RESULT" | grep -q '"pong": true'; then
  echo "[OK] All systems go!"
else
  echo "[FAIL] Ping failed:"
  echo "  $RESULT"
fi
echo ""
