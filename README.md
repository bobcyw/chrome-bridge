# Chrome Bridge

**AI-to-Browser bridge** — Let AI coding agents (Claude Code, Cursor, Copilot, etc.) control your **real Chrome browser** via WebSocket. No headless browser. No CDP detection. Your logins, cookies, and extensions stay intact.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Start the bridge server
python bridge/cli.py serve
# (or: chrome-bridge serve)

# 3. Load the Chrome Extension
#    Open chrome://extensions → Developer mode → Load unpacked → select extension/

# 4. Test
python bridge/cli.py ping
# → {"ok": true, "pong": true}

python bridge/cli.py new_tab url=https://www.example.com
python bridge/cli.py get_content
```

## Architecture

```
chrome-bridge <cmd> ──file──▶ runtime/.bridge_cmd.json
                                    │
                         bridge/server.py (WebSocket, port 9876)
                                    │
                         Chrome Extension ◀─▶ Your Real Browser
```

Three components work together:
1. **Chrome Extension** (`extension/`) — executes commands inside the browser
2. **Bridge Server** (`bridge/server.py`) — relays commands via WebSocket
3. **CLI / Python API** (`bridge/cli.py`, `bridge/api.py`) — sends commands

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

| Platform | Status | Notes |
|----------|--------|-------|
| Windows | ✅ | Use Git Bash or `chrome-bridge serve` for Python-native |
| macOS | ✅ | Full support |
| Linux | ✅ | Full support |

## Installation

```bash
# From source
git clone https://github.com/YOUR_USERNAME/chrome-bridge.git
cd chrome-bridge
pip install -r requirements.txt

# Or install as a package
pip install -e .
# Now available everywhere: chrome-bridge serve / ping / new_tab ...
```

### Load the Chrome Extension

1. Open `chrome://extensions` in Chrome
2. Enable **Developer mode** (top right)
3. Click **Load unpacked** → select the `extension/` folder
4. Click the Chrome Bridge icon in the toolbar to activate

### Start the Server

```bash
# Python-native (recommended — works on all platforms)
chrome-bridge serve

# Or via shell script
bash scripts/start_bridge.sh
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ping` timeout | Server not running | `chrome-bridge serve` |
| "No Chrome extension connected" | Extension SW suspended | Click extension icon in Chrome |
| "Element not found" | Wrong selector | Use `get_content` to verify page state |
| Screenshot returns `canvas-fallback` | Permission not active | Click extension icon, then retry |
| `eval` fails | Page CSP blocks eval | Use `click`/`click_text`/`get_content` instead |
| Dialog hangs the tab | Unhandled alert/confirm | Use `handle_dialog action=dismiss` |

## Requirements

- **Python** 3.10+
- **Chrome** 88+ (Manifest V3 support)
- **websockets** Python package (`pip install websockets`)

## License

MIT — see [LICENSE](LICENSE) for details.
