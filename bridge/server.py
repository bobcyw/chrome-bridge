"""
Chrome Bridge Server — HTTP API + WebSocket relay.

Two ports:
  HTTP  : http://127.0.0.1:9877/cmd — CLI sends commands here
  WebSocket: ws://127.0.0.1:9876    — Chrome Extension connects here

Usage: python -m bridge.server
       python bridge/server.py
       chrome-bridge serve
"""

import asyncio
import json
import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

import websockets

# Force UTF-8 output
if hasattr(sys.stdout, "reconfigure") and sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure") and sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Configuration ────────────────────────────────────────────────

WS_PORT = int(os.environ.get("CHROME_BRIDGE_WS_PORT", "19876"))
HTTP_PORT = int(os.environ.get("CHROME_BRIDGE_HTTP_PORT", "19877"))
RESPONSE_TIMEOUT = 30  # seconds

# ── Shared State ─────────────────────────────────────────────────

_lock = threading.Lock()
connected_ws = []  # list of WebSocket connections
pending = {}  # cmd_id -> {"event": threading.Event, "result": dict}

_event_loop = None  # asyncio event loop reference (set after start)


# ── WebSocket (Extension) ───────────────────────────────────────


async def ws_handler(websocket):
    with _lock:
        connected_ws.append(websocket)
    print(f"[+] Extension connected ({len(connected_ws)} total)", flush=True)

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            msg_id = data.get("id")
            if msg_id:
                with _lock:
                    entry = pending.pop(msg_id, None)
                if entry:
                    result = data.get("data", data)
                    entry["result"] = result
                    entry["event"].set()
                    continue

            if data.get("cmd") == "ping":
                continue
    except Exception as e:
        print(f"[!] WS connection error: {e}", flush=True)
    finally:
        with _lock:
            if websocket in connected_ws:
                connected_ws.remove(websocket)
        print("[-] Extension disconnected", flush=True)


async def _send_to_extension(msg: str):
    """Send a message to the first connected extension. Thread-safe via call_soon_threadsafe."""
    with _lock:
        clients = list(connected_ws)
    if not clients:
        return False
    try:
        await clients[0].send(msg)
        return True
    except Exception:
        return False


# ── HTTP (CLI) ──────────────────────────────────────────────────


class CmdHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # suppress access logs

    def do_POST(self):
        if self.path != "/cmd":
            self.send_error(404)
            return

        # Read request body
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            cmd_data = json.loads(body)
        except Exception as e:
            self._reply(400, {"ok": False, "error": f"Invalid request: {e}"})
            return

        cmd = cmd_data.get("cmd", "")
        args = cmd_data.get("args", {})
        cmd_id = f"cmd_{int(time.time() * 1000)}"

        # Check extension is connected
        with _lock:
            if not connected_ws:
                self._reply(
                    503,
                    {
                        "ok": False,
                        "error": "No Chrome extension connected",
                        "hint": "Open chrome://extensions, find Chrome Bridge, click the icon to activate the service worker",
                    },
                )
                return

        # Register pending response
        event = threading.Event()
        entry = {"event": event, "result": None}
        with _lock:
            pending[cmd_id] = entry

        # Send to extension via asyncio
        msg = json.dumps({"id": cmd_id, "cmd": cmd, "args": args})
        future = asyncio.run_coroutine_threadsafe(_send_to_extension(msg), _event_loop)

        try:
            sent = future.result(timeout=5)
        except Exception:
            sent = False

        if not sent:
            with _lock:
                pending.pop(cmd_id, None)
            self._reply(
                502, {"ok": False, "error": "Failed to send command to extension"}
            )
            return

        print(f"[>] {cmd} {json.dumps(args, ensure_ascii=False)[:80]}", flush=True)

        # Wait for response
        if event.wait(timeout=RESPONSE_TIMEOUT):
            result = entry["result"] or {}
            self._reply(200, result)
            print(f"[<] OK: {json.dumps(result, ensure_ascii=False)[:120]}", flush=True)
        else:
            with _lock:
                pending.pop(cmd_id, None)
            self._reply(504, {"ok": False, "error": "Extension response timeout"})
            print(f"[!] Timeout: {cmd}", flush=True)

    def do_GET(self):
        if self.path == "/health":
            self._reply(200, {"ok": True, "connections": len(connected_ws)})
        else:
            self.send_error(404)

    def _reply(self, code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


# ── Main ────────────────────────────────────────────────────────


def _start_http_server():
    """Run HTTP server in a daemon thread."""
    httpd = HTTPServer(("127.0.0.1", HTTP_PORT), CmdHandler)
    print(f"[*] HTTP API listening on http://127.0.0.1:{HTTP_PORT}", flush=True)
    httpd.serve_forever()


async def main():
    global _event_loop
    _event_loop = asyncio.get_running_loop()

    print("=" * 50, flush=True)
    print("  Chrome Bridge Server  v1.0", flush=True)
    print(f"  WS:  ws://127.0.0.1:{WS_PORT}", flush=True)
    print(f"  HTTP: http://127.0.0.1:{HTTP_PORT}/cmd", flush=True)
    print("=" * 50, flush=True)

    # Start HTTP server in a background thread
    http_thread = threading.Thread(target=_start_http_server, daemon=True)
    http_thread.start()

    # Start WebSocket server in the main asyncio event loop
    print("[*] WebSocket server listening", flush=True)
    async with websockets.serve(
        ws_handler, "127.0.0.1", WS_PORT, max_size=10 * 1024 * 1024
    ):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
