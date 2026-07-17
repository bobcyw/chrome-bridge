"""
CLI tool for sending browser commands through the Chrome Bridge.
Usage: python bridge/cli.py <cmd> [key=value ...]
       python -m bridge.cli <cmd> [key=value ...]
       chrome-bridge <cmd> [key=value ...]
       chrome-bridge serve           (start the bridge server)

Examples:
  chrome-bridge new_tab url=https://www.example.com
  chrome-bridge list_tabs
  chrome-bridge click selector=.login-btn
  chrome-bridge get_content
  chrome-bridge hover selector=.menu-item
  chrome-bridge press_key key=ArrowDown
"""

import json
import os
import sys
import urllib.request
import urllib.error

# Ensure project root is on sys.path for direct script execution
_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_DIR not in sys.path:
    sys.path.insert(0, _PROJECT_DIR)

# Force UTF-8 output
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Bridge server HTTP endpoint
BRIDGE_HTTP_PORT = os.environ.get("CHROME_BRIDGE_HTTP_PORT", "19877")
BRIDGE_URL = os.environ.get(
    "CHROME_BRIDGE_URL", f"http://127.0.0.1:{BRIDGE_HTTP_PORT}/cmd"
)


def send_cmd(cmd, **kwargs):
    """Send a command to the bridge server via HTTP POST and return the result."""

    # Support js_file parameter: read JS content from file
    if "js_file" in kwargs:
        js_path = kwargs.pop("js_file")
        with open(js_path, "r", encoding="utf-8") as f:
            kwargs["js"] = f.read()

    payload = json.dumps({"cmd": cmd, "args": kwargs}).encode("utf-8")

    req = urllib.request.Request(
        BRIDGE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=65) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
            return body
        except Exception:
            return {"ok": False, "error": f"Server error ({e.code})"}
    except urllib.error.URLError as e:
        return {"ok": False, "error": f"Cannot connect to bridge server: {e.reason}"}
    except json.JSONDecodeError:
        return {"ok": False, "error": "Invalid response from server"}


def parse_args(argv):
    """Parse key=value arguments, handling values with = in them."""
    kwargs = {}
    for arg in argv:
        if "=" in arg:
            key, value = arg.split("=", 1)
            # Try to parse numbers and booleans
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            else:
                # Try JSON first (arrays/objects)
                if (value.startswith("[") or value.startswith("{")) and (
                    value.endswith("]") or value.endswith("}")
                ):
                    try:
                        value = json.loads(value)
                    except (json.JSONDecodeError, ValueError):
                        pass
                    else:
                        kwargs[key] = value
                        continue
                # Try int first, then float
                try:
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
            kwargs[key] = value
    return kwargs


HELP_TEXT = """Usage: chrome-bridge <cmd> [key=value ...]

Server:
  serve                                 - Start the bridge server (foreground)
  serve --background (-b)               - Start in background (daemon)

Tab Management:
  new_tab     url=...                    - Open new tab
  navigate    url=... [tab_id=..]        - Navigate existing tab
  list_tabs                              - List all tabs
  find_tab    keyword=..                 - Search tabs by title/URL
  close_tab   [tab_id=..]                - Close tab
  get_url     [tab_id=..]                - Get tab URL and title
  activate_tab tab_id=..                 - Switch to tab
  go_back     [tab_id=..]                - Navigate back
  go_forward  [tab_id=..]                - Navigate forward
  reload      [tab_id=..]                - Reload page

Page Interaction:
  click       selector=.. [tab_id]       - Click element
  click_text  text=.. [mode=..] [tab_id] - Click by visible text (exact/contains)
  double_click selector=.. [tab_id]      - Double-click element
  right_click selector=.. [tab_id]       - Right-click (context menu)
  hover       selector=.. [tab_id]       - Hover mouse over element
  type        selector=.. text=..        - Type into input
  type_active text=.. [tab_id=..]        - Type into focused element
  type_trusted selector=.. text=..       - Trusted typing via CDP
  press_key   key=.. [selector=..] [modifiers=..] - Simulate key press
              Keys: Enter/Tab/Escape/Backspace/Space/Delete/Arrow keys/PageUp/Down/Home/End/F1-F12
              Modifiers: ctrl,alt,shift,meta (comma-separated)
  scroll      [direction=..] [amount=..] - Scroll page
  select_option selector=.. [value=..] [text=..] [index=..] - Select dropdown option
  find_element selector=.. [tab_id]      - Check element existence

Content:
  get_content [tab_id=..]                - Get visible page text
  get_html    [tab_id=..]                - Get full page HTML source
  get_attribute selector=.. attribute=.. - Get element attribute (or innerHTML/outerHTML/textContent/class)
  screenshot  [tab_id=..]                - Capture screenshot (base64)
  eval        js=... [tab_id=..]         - Execute JavaScript
  get_images  [max_wait_ms=..] [min_large=..] - Collect visible image URLs

Wait & Dialogs:
  wait        [ms=1000] [tab_id=..]      - Wait N milliseconds
  wait_for_element selector=.. [timeout=..] [interval=..] - Wait for element to appear
  handle_dialog action=accept|dismiss [prompt_text=..] - Handle alert/confirm/prompt

Network:
  fetch_api   url=... [method=..] [body=..] [headers=..] - Fetch from page context

Cookies & Storage:
  get_cookies [url=..]                   - Get cookies (optionally filtered by URL)
  set_cookie  url=.. name=.. value=.. [domain=..] [path=..] [secure] [httpOnly] [expirationDate=..]
  get_storage [key=..] [store=local|session] - Read localStorage/sessionStorage
  set_storage key=.. value=.. [store=local|session] - Write to localStorage/sessionStorage

File Upload:
  file_chooser_intercept file_paths=.. [click_selector=..] - Intercept file chooser and inject files

Connection:
  ping                                   - Test full pipeline
  version                                - Show version and command list

For more details: https://github.com/your-username/chrome-bridge
"""


def main():
    if len(sys.argv) < 2:
        print(HELP_TEXT)
        sys.exit(0)

    cmd = sys.argv[1]

    # Built-in: serve — start the WebSocket bridge server
    if cmd == "serve":
        background = "--background" in sys.argv or "-b" in sys.argv
        if background:
            # Daemonize: detach from terminal and run in background
            if sys.platform == "win32":
                # Windows: use pythonw to run without console
                import subprocess

                script = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "server.py"
                )
                subprocess.Popen(
                    [sys.executable, "-u", script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=(
                        subprocess.CREATE_NO_WINDOW
                        if hasattr(subprocess, "CREATE_NO_WINDOW")
                        else 0
                    ),
                )
            else:
                # Unix: classic double-fork daemon
                pid = os.fork()
                if pid > 0:
                    print(f"[*] Server started in background (PID: {pid})")
                    sys.exit(0)
                # Child: detach and run
                os.setsid()
                pid2 = os.fork()
                if pid2 > 0:
                    sys.exit(0)
                # Grandchild: the actual server
                sys.stdout = open(os.devnull, "w")
                sys.stderr = open(os.devnull, "w")
                from bridge.server import main as server_main
                import asyncio

                asyncio.run(server_main())
            sys.exit(0)

        from bridge.server import main as server_main
        import asyncio

        try:
            asyncio.run(server_main())
        except KeyboardInterrupt:
            print("\n[*] Server stopped.")
        sys.exit(0)

    kwargs = parse_args(sys.argv[2:])

    result = send_cmd(cmd, **kwargs)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
