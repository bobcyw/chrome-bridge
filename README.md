# Chrome Bridge

**AI-to-Browser bridge** — Let AI coding agents (Claude Code, Cursor, Copilot, etc.) control your **real Chrome browser** via WebSocket. No headless browser. No CDP detection. Your logins, cookies, and extensions stay intact.

## Quick Start

```bash
# 1. Install
pip install chrome-bridge          # pip
# uv tool install chrome-bridge    # or uv

# 2. Start the bridge server (background)
chrome-bridge serve --background

# 3. Load the Chrome Extension
#    Clone the repo: git clone https://github.com/bobcyw/chrome-bridge.git
#    Open chrome://extensions → Developer mode → Load unpacked → select extension/
#    → Click the Chrome Bridge icon in the toolbar to activate

# 4. Test
chrome-bridge ping
# → {"ok": true, "pong": true}

chrome-bridge new_tab url=https://www.example.com
chrome-bridge get_content
```

**Windows users**: Clone the repo and double-click `scripts\start_bridge.bat` to start everything with one click.

## Architecture

```
CLI / Python API ──HTTP POST :19877──▶ bridge/server.py ──WebSocket :19876──▶ Chrome Extension ──▶ Real Browser
```

Three components:
1. **Chrome Extension** (`extension/`) — executes commands inside the browser
2. **Bridge Server** (`bridge/server.py`) — HTTP API + WebSocket relay, two ports
3. **CLI / Python API** (`bridge/cli.py`, `bridge/api.py`) — sends commands via HTTP

## Command Reference

### Tab Management

| Command | Parameters | Description |
|---------|-----------|-------------|
| `new_tab` | `url=...` | Open new tab |
| `navigate` | `url=...` `tab_id=..` | Navigate to URL (waits for load) |
| `list_tabs` | — | List all tabs |
| `find_tab` | `keyword=..` | Search by title/URL |
| `close_tab` | `tab_id=..` | Close tab |
| `get_url` | `tab_id=..` | Get tab URL and title |
| `activate_tab` | `tab_id=..` | Switch to tab |
| `go_back` | `tab_id=..` | Navigate back |
| `go_forward` | `tab_id=..` | Navigate forward |
| `reload` | `tab_id=..` | Reload page |

### Mouse & Interaction

| Command | Parameters | Description |
|---------|-----------|-------------|
| `click` | `selector=..` `tab_id=..` | Click by CSS selector |
| `click_text` | `text=..` `mode=exact\|contains` | Click by visible text |
| `double_click` | `selector=..` | Double-click element |
| `right_click` | `selector=..` | Right-click (context menu) |
| `hover` | `selector=..` | Hover mouse over element |
| `scroll` | `direction=down\|up\|top\|bottom` `amount=500` | Scroll page |

### Keyboard & Input

| Command | Parameters | Description |
|---------|-----------|-------------|
| `type` | `selector=..` `text=..` | Type into input field |
| `type_active` | `text=...` | Type into focused element |
| `type_trusted` | `selector=...` `text=...` | Trusted typing via CDP (bypasses React/Vue) |
| `press_key` | `key=...` `selector=..` `modifiers=..` | Simulate key press. Keys: Enter/Tab/Escape/Backspace/Space/Delete/Arrow keys/PageUp/Down/Home/End/F1-F12. Modifiers: ctrl,alt,shift,meta |
| `select_option` | `selector=..` `value=..` `text=..` `index=..` | Select dropdown option |

### Content Extraction

| Command | Parameters | Description |
|---------|-----------|-------------|
| `get_content` | `tab_id=..` | Get visible page text |
| `get_html` | `tab_id=..` | Get full page HTML source |
| `get_attribute` | `selector=..` `attribute=..` | Get element attribute (or innerHTML/outerHTML/textContent/class) |
| `find_element` | `selector=..` | Check element. Returns `{found, tag, text, visible, rect}` |
| `screenshot` | `tab_id=..` | Capture screenshot (base64 dataUrl) |
| `eval` | `js=...` | Execute JavaScript in page |
| `get_images` | `max_wait_ms=15000` `min_large=1` | Collect visible image URLs |

### Wait & Dialogs

| Command | Parameters | Description |
|---------|-----------|-------------|
| `wait` | `ms=1000` | Wait N milliseconds |
| `wait_for_element` | `selector=..` `timeout=10000` `interval=300` | Poll until element appears |
| `handle_dialog` | `action=accept\|dismiss` `prompt_text=..` | Handle alert/confirm/prompt |

### Network, Cookies & Storage

| Command | Parameters | Description |
|---------|-----------|-------------|
| `fetch_api` | `url=...` `method=..` `body=..` `headers=..` | Fetch from page context |
| `get_cookies` | `url=..` | Get cookies |
| `set_cookie` | `url=..` `name=..` `value=..` `domain=..` `path=..` | Set cookie |
| `get_storage` | `key=..` `store=local\|session` | Read localStorage/sessionStorage |
| `set_storage` | `key=..` `value=..` `store=local\|session` | Write to localStorage/sessionStorage |

### File Upload

| Command | Parameters | Description |
|---------|-----------|-------------|
| `file_chooser_intercept` | `file_paths=...` `click_selector=...` | Intercept file chooser dialog |

### Connection

| Command | Parameters | Description |
|---------|-----------|-------------|
| `ping` | — | Test full pipeline |
| `version` | — | Show version and command list |

## Python API

```python
from bridge import Browser

b = Browser()

# Tab management
b.open("https://www.example.com")
b.find_tab("example")
b.navigate("https://github.com")
tabs = b.list_tabs()
b.go_back()
b.reload()
b.close_tab()

# Mouse & interaction
b.click("#login-btn")
b.click_text("Submit", mode="contains")
b.double_click(".row")
b.right_click(".item")
b.hover(".menu-item")
b.scroll("down", 800)

# Keyboard & form
b.type("#search", "hello world")
b.press_key("ArrowDown")
b.press_key("a", modifiers="ctrl")
b.type_trusted("#input", "text")     # CDP trusted input
b.select_option("#country", text="China")

# Content
content = b.get_content()
html = b.get_html()
cls = b.get_attribute(".btn", "class")
el = b.find_element(".modal")
b.screenshot("screenshot.png")
title = b.eval("document.title")

# Wait & dialogs
b.wait(2000)
b.wait_for_element(".dynamic-content", timeout=15000)
b.handle_dialog(action="accept")

# Network & storage
result = b.fetch_api("https://api.example.com/data")
cookies = b.get_cookies()
b.set_cookie("https://example.com", "token", "xyz")
data = b.get_storage(key="theme")
b.set_storage("theme", "dark")

print(b.ping())  # True
```

## Claude Code Integration

Chrome Bridge works out of the box with Claude Code. Drop this repo into your project and Claude can control your browser automatically.

See [CLAUDE.md](CLAUDE.md) for the built-in skill definition, or [docs/claude-code-setup.md](docs/claude-code-setup.md) for manual setup.

## Platform Support

| Platform | Start | Auto-Start |
|----------|-------|------------|
| Windows | `scripts\start_bridge.bat` (double-click) or `chrome-bridge serve --background` | `bash scripts/install_service.sh` → Startup folder shortcut |
| macOS | `chrome-bridge serve --background` or `bash scripts/start_bridge.sh -b` | `bash scripts/install_service.sh` → LaunchAgent plist |
| Linux | `chrome-bridge serve --background` or `bash scripts/start_bridge.sh -b` | `bash scripts/install_service.sh` → systemd user unit |

## Installation

```bash
# pip
pip install chrome-bridge

# uv
uv tool install chrome-bridge
# Then run: chrome-bridge serve --background
# Or one-shot: uvx chrome-bridge ping

# From source
git clone https://github.com/bobcyw/chrome-bridge.git
cd chrome-bridge
pip install -e .
```

The `chrome-bridge` command is available globally after install.

### Load the Chrome Extension

**From Chrome Web Store** (easiest):

Install from the [Chrome Web Store](https://chromewebstore.google.com) (coming soon).

**From source** (developer mode):

1. Clone the repo: `git clone https://github.com/bobcyw/chrome-bridge.git`
2. Open `chrome://extensions` in Chrome
3. Enable **Developer mode** (top right)
4. Click **Load unpacked** → select the `extension/` folder from the cloned repo
5. Click the **Chrome Bridge icon** in the toolbar to activate the service worker
   - _The icon must be clicked once after loading, or after Chrome restarts_

### Start the Server

```bash
# Daemon mode (recommended) — run in background, works on all platforms
chrome-bridge serve --background

# Foreground mode — see logs, Ctrl+C to stop
chrome-bridge serve

# Windows one-click (no terminal needed)
scripts\start_bridge.bat
```

**Ports**: WS `19876` + HTTP `19877`. Override via environment variables:

```bash
CHROME_BRIDGE_WS_PORT=9999 CHROME_BRIDGE_HTTP_PORT=9998 chrome-bridge serve
```

### Auto-Start on Login (optional)

```bash
bash scripts/install_service.sh
```

This auto-detects your OS and installs the right thing:
- **macOS** → LaunchAgent (`~/Library/LaunchAgents/com.chrome-bridge.plist`)
- **Linux** → systemd user unit (`~/.config/systemd/user/chrome-bridge.service`)
- **Windows** → Startup folder shortcut (runs `launch_silent.vbs`)

The server will start automatically every time you log in. To remove:

| OS | Uninstall |
|----|-----------|
| macOS | `launchctl unload ~/Library/LaunchAgents/com.chrome-bridge.plist` |
| Linux | `systemctl --user disable chrome-bridge.service` |
| Windows | Delete `ChromeBridge.lnk` from Startup folder |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Cannot connect to bridge server` | Server not running | `chrome-bridge serve --background` |
| Port 19876/19877 already in use | Another instance running | Kill existing process, or set `CHROME_BRIDGE_WS_PORT` / `CHROME_BRIDGE_HTTP_PORT` env vars |
| "No Chrome extension connected" | Extension SW suspended | Click extension icon in Chrome toolbar to activate |
| "No Chrome extension connected" (persists) | Extension not loaded/reloaded | Go to `chrome://extensions`, click refresh ↻ on Chrome Bridge |
| "Element not found" | Wrong selector / page not loaded | Use `get_content` to verify page state, or `wait_for_element` |
| Screenshot returns `canvas-fallback` | Tab not active | Click extension icon, then activate target tab |
| `eval` fails | Page CSP blocks eval | Use `click`/`click_text`/`get_content` instead |
| Dialog hangs the tab | Unhandled alert/confirm/prompt | Use `handle_dialog action=dismiss` |

## Requirements

- **Python** 3.10+
- **Chrome** 88+ (Manifest V3 support)
- **websockets** Python package (`pip install websockets`)

## License

MIT — see [LICENSE](LICENSE) for details.
