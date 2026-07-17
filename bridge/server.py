"""
Chrome Bridge Server - WebSocket relay between CLI and Chrome Extension.
Monitors a command file and forwards commands to connected Chrome extensions.

Usage: python -m bridge.server
       python bridge/server.py
"""
import asyncio
import json
import os
import sys
import time

import websockets

# Force UTF-8 output to handle Chinese characters and special Unicode
if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure') and sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Project root is one level up from the bridge/ package
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME_DIR = os.path.join(PROJECT_DIR, 'runtime')
CMD_FILE = os.path.join(RUNTIME_DIR, '.bridge_cmd.json')
RESULT_FILE = os.path.join(RUNTIME_DIR, '.bridge_result.json')

connected_ws = []
pending_responses = {}


async def handler(websocket):
    connected_ws.append(websocket)
    print(f"[+] Extension connected ({len(connected_ws)} total)", flush=True)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue
            msg_id = data.get('id')
            if msg_id and msg_id in pending_responses:
                future = pending_responses[msg_id]
                if not future.done():
                    result = data.get('data', data)
                    future.set_result(result)
                continue
            if data.get('cmd') == 'ping':
                continue
    except Exception as e:
        print(f"[!] Connection error: {e}", flush=True)
    finally:
        if websocket in connected_ws:
            connected_ws.remove(websocket)
        print(f"[-] Extension disconnected", flush=True)


async def file_watcher():
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    for f in [CMD_FILE, RESULT_FILE]:
        if not os.path.exists(f):
            with open(f, 'w') as fh:
                fh.write('')
    last_content = ''
    print("[*] File watcher started", flush=True)

    while True:
        try:
            if not os.path.exists(CMD_FILE):
                await asyncio.sleep(0.3)
                continue
            current_size = os.path.getsize(CMD_FILE)
            if current_size == 0:
                await asyncio.sleep(0.3)
                continue
            with open(CMD_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if not content or content == last_content:
                await asyncio.sleep(0.3)
                continue
            last_content = content
            try:
                cmd_data = json.loads(content)
            except json.JSONDecodeError:
                await asyncio.sleep(0.3)
                continue
            with open(CMD_FILE, 'w', encoding='utf-8') as f:
                f.write('')
            last_content = ''
            cmd = cmd_data.get('cmd', '')
            args = cmd_data.get('args', {})
            print(f"[>] {cmd} {json.dumps(args, ensure_ascii=False)[:80]}", flush=True)

            if not connected_ws:
                result = {"ok": False, "error": "No Chrome extension connected"}
                with open(RESULT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False)
                print(f"[!] No extension connected", flush=True)
                continue

            cmd_id = f"cmd_{int(time.time() * 1000)}"
            future = asyncio.get_event_loop().create_future()
            pending_responses[cmd_id] = future
            msg = json.dumps({"id": cmd_id, "cmd": cmd, "args": args})
            ws = connected_ws[0]
            try:
                await ws.send(msg)
                result = await asyncio.wait_for(future, timeout=30)
                with open(RESULT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False)
                print(f"[<] OK: {json.dumps(result, ensure_ascii=False)[:120]}", flush=True)
            except asyncio.TimeoutError:
                result = {"ok": False, "error": "Extension response timeout"}
                with open(RESULT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False)
                print(f"[!] Timeout", flush=True)
            except Exception as e:
                result = {"ok": False, "error": str(e)}
                with open(RESULT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False)
                print(f"[!] Error: {e}", flush=True)
            finally:
                pending_responses.pop(cmd_id, None)
        except Exception as e:
            print(f"[!] Watcher error: {e}", flush=True)
        await asyncio.sleep(0.3)


async def main():
    print("=" * 50, flush=True)
    print("  Chrome Bridge Server", flush=True)
    print(f"  WS:  ws://127.0.0.1:9876", flush=True)
    print(f"  CMD: {CMD_FILE}", flush=True)
    print("=" * 50, flush=True)

    async with websockets.serve(handler, '127.0.0.1', 9876, max_size=10*1024*1024):
        print("[*] WebSocket server listening", flush=True)
        watcher = asyncio.create_task(file_watcher())
        print("[*] Watcher task created", flush=True)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
