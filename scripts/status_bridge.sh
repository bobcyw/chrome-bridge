#!/usr/bin/env bash
# Chrome Bridge — status check script
# Usage: bash status_bridge.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLI_PATH="$PROJECT_DIR/bridge/cli.py"
LOG_FILE="$PROJECT_DIR/runtime/server.log"

PYTHON="${PYTHON:-python}"

echo "=========================================="
echo "  Chrome Bridge — Status"
echo "=========================================="
echo ""

# 1. Check HTTP API
HTTP_CHECK=$(netstat -ano 2>/dev/null | grep ":9877.*LISTEN" | head -1)
if [ -n "$HTTP_CHECK" ]; then
  echo "[OK] HTTP API: http://127.0.0.1:9877"
else
  echo "[FAIL] HTTP API: NOT RUNNING"
  echo "  Start it with: bash $SCRIPT_DIR/start_bridge.sh"
  exit 1
fi

# 2. Check WebSocket
WS_CHECK=$(netstat -ano 2>/dev/null | grep ":9876.*LISTEN" | head -1)
if [ -n "$WS_CHECK" ]; then
  echo "[OK] WebSocket: ws://127.0.0.1:9876"
else
  echo "[WARN] WebSocket: NOT LISTENING"
fi

# 3. Check extension connection
ESTABLISHED=$(netstat -ano 2>/dev/null | grep ":9876.*ESTABLISHED" | head -1)
if [ -n "$ESTABLISHED" ]; then
  echo "[OK] Chrome extension: CONNECTED"
else
  echo "[WARN] Chrome extension: NOT CONNECTED"
  echo "  Reload the extension or click its icon in Chrome"
  echo ""
  echo "  Log tail:"
  tail -5 "$LOG_FILE" 2>/dev/null
fi

# 4. Send a test ping
echo ""
echo "[TEST] Sending ping..."
RESULT=$("$PYTHON" "$CLI_PATH" ping 2>&1)
if echo "$RESULT" | grep -q '"pong": true'; then
  echo "[OK] Ping test: PASSED"
else
  echo "[FAIL] Ping test: FAILED"
  echo "  $RESULT"
fi

echo ""
echo "=========================================="
