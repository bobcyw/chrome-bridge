#!/usr/bin/env bash
# Chrome Bridge — status check script
# Shows server status, extension connection, and quick test
# Usage: bash status_bridge.sh

# Determine script and project directories
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLI_PATH="$PROJECT_DIR/bridge/cli.py"
LOG_FILE="$PROJECT_DIR/runtime/server.log"

PYTHON="${PYTHON:-python}"

echo "=========================================="
echo "  Chrome Bridge — Status"
echo "=========================================="
echo ""

# 1. Check server process
PORT_CHECK=$(netstat -ano 2>/dev/null | grep ":9876.*LISTEN" | head -1)
if [ -n "$PORT_CHECK" ]; then
  echo "[OK] Bridge server: RUNNING"
  echo "  $PORT_CHECK"
else
  echo "[FAIL] Bridge server: NOT RUNNING"
  echo "  Start it with: bash $SCRIPT_DIR/start_bridge.sh"
  exit 1
fi

# 2. Check extension connection
ESTABLISHED=$(netstat -ano 2>/dev/null | grep ":9876.*ESTABLISHED" | head -1)
if [ -n "$ESTABLISHED" ]; then
  echo "[OK] Chrome extension: CONNECTED"
else
  echo "[WARN] Chrome extension: NOT CONNECTED"
  echo "  Reload the extension or click its icon in Chrome"
  echo ""
  echo "  Log tail:"
  tail -5 "$LOG_FILE" 2>/dev/null
  exit 0
fi

# 3. Send a test ping
echo ""
echo "[TEST] Sending ping..."
RESULT=$("$PYTHON" "$CLI_PATH" ping 2>&1)
if echo "$RESULT" | grep -q '"pong": true'; then
  echo "[OK] Ping test: PASSED"
else
  echo "[FAIL] Ping test: FAILED"
  echo "  $RESULT"
fi

# 4. List tabs
echo ""
echo "[TEST] Listing tabs..."
"$PYTHON" "$CLI_PATH" list_tabs 2>&1 | head -30

echo ""
echo "=========================================="
echo "  All systems go!"
echo "=========================================="
