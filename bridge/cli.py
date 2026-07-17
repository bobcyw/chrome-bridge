"""
CLI tool for sending browser commands through the Chrome Bridge.
Usage: python bridge/cli.py <cmd> [key=value ...]
       python -m bridge.cli <cmd> [key=value ...]

Examples:
  python bridge/cli.py new_tab url=https://www.example.com
  python bridge/cli.py list_tabs
  python bridge/cli.py navigate tab_id=123 url=https://www.example.com
  python bridge/cli.py click selector=.login-btn
  python bridge/cli.py get_content
  python bridge/cli.py hover selector=.menu-item
  python bridge/cli.py press_key key=ArrowDown
"""
import json
import os
import sys
import time

# Force UTF-8 output to handle Chinese characters and special Unicode
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Project root is one level up from the bridge/ package
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME_DIR = os.path.join(PROJECT_DIR, 'runtime')
CMD_FILE = os.path.join(RUNTIME_DIR, '.bridge_cmd.json')
RESULT_FILE = os.path.join(RUNTIME_DIR, '.bridge_result.json')


def send_cmd(cmd, **kwargs):
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    # Clear old result
    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        f.write('')

    # Support js_file parameter: read JS content from file (avoids Windows command-line length limits)
    if 'js_file' in kwargs:
        js_path = kwargs.pop('js_file')
        with open(js_path, 'r', encoding='utf-8') as f:
            kwargs['js'] = f.read()

    # Write command
    cmd_data = {"cmd": cmd, "args": kwargs}
    with open(CMD_FILE, 'w', encoding='utf-8') as f:
        json.dump(cmd_data, f, ensure_ascii=False)

    # Wait for result (poll with timeout)
    timeout = 60  # seconds
    interval = 0.5
    elapsed = 0
    while elapsed < timeout:
        if os.path.exists(RESULT_FILE):
            with open(RESULT_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if content:
                result = json.loads(content)
                return result
        time.sleep(interval)
        elapsed += interval

    return {"ok": False, "error": "Timeout waiting for result"}


def parse_args(argv):
    """Parse key=value arguments, handling values with = in them."""
    kwargs = {}
    for arg in argv:
        if '=' in arg:
            key, value = arg.split('=', 1)
            # Try to parse numbers and booleans
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            else:
                # Try JSON first (arrays/objects)
                if (value.startswith('[') or value.startswith('{')) and (value.endswith(']') or value.endswith('}')):
                    try:
                        value = json.loads(value)
                    except (json.JSONDecodeError, ValueError):
                        pass
                    else:
                        kwargs[key] = value
                        continue
                # Try int first, then float
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
            kwargs[key] = value
    return kwargs


HELP_TEXT = """Usage: chrome-bridge <cmd> [key=value ...]

Server:
  serve                                 - Start the WebSocket bridge server

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
    if cmd == 'serve':
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
