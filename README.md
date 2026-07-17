# Chrome Bridge

**AI-to-Browser bridge** — Let AI coding agents control your **real Chrome browser**. No headless mode. No bot detection. All logins and cookies preserved.

## Install via Claude Code

Copy this into Claude Code and tell it to set up:

```
https://github.com/bobcyw/chrome-bridge
```

Claude will read `CLAUDE.md`, install the package, register the skill, and start the server. Then you can say:

> *"Open GitHub, search for chrome-bridge, and tell me the star count"*

## Quick Start

```bash
pip install chrome-bridge          # or: uv tool install chrome-bridge
chrome-bridge serve --background   # start the bridge
chrome-bridge ping                 # test it
# → {"ok": true, "pong": true}
```

You also need the Chrome Extension — see [Load the Extension](#load-the-chrome-extension) below (one-time setup).

## Architecture

```
CLI / Python API ──HTTP :19877──▶ server.py ──WebSocket :19876──▶ Chrome Extension ──▶ Browser
```

Three pieces: **Chrome Extension** (runs in browser), **Bridge Server** (relay), **CLI / Python API** (you).

## Python API

```python
from bridge import Browser
b = Browser()

# Navigate
b.open("https://www.example.com")
b.go_back()
b.reload()

# Interact
b.click("#login-btn")
b.click_text("Submit", mode="contains")
b.hover(".menu-item")
b.double_click(".row")
b.right_click(".item")

# Type & forms
b.type("#search", "hello")
b.press_key("Enter")
b.press_key("a", modifiers="ctrl")
b.select_option("#country", text="China")

# Extract
text = b.get_content()
html = b.get_html()
cls = b.get_attribute(".btn", "class")
b.screenshot("page.png")
title = b.eval("document.title")

# Wait & dialogs
b.wait(2000)
b.wait_for_element(".results", timeout=15000)
b.handle_dialog(action="accept")

# Storage
cookies = b.get_cookies()
b.set_cookie("https://example.com", "token", "xyz")
b.get_storage(key="theme")
```

## Command Reference

<details>
<summary>Click to expand — 32 commands</summary>

### Tab Management

| Command | Parameters | Description |
|---------|-----------|-------------|
| `new_tab` | `url=...` | Open new tab |
| `navigate` | `url=...` `tab_id=..` | Navigate tab (waits for load) |
| `list_tabs` | — | List all tabs |
| `find_tab` | `keyword=..` | Search by title/URL |
| `close_tab` | `tab_id=..` | Close tab |
| `get_url` | `tab_id=..` | Get URL and title |
| `activate_tab` | `tab_id=..` | Switch to tab |
| `go_back` / `go_forward` / `reload` | `tab_id=..` | History navigation |

### Mouse & Keyboard

| Command | Parameters | Description |
|---------|-----------|-------------|
| `click` | `selector=..` | Click by CSS selector |
| `click_text` | `text=..` `mode=exact\|contains` | Click by visible text |
| `double_click` | `selector=..` | Double-click |
| `right_click` | `selector=..` | Right-click |
| `hover` | `selector=..` | Hover (triggers menus/tooltips) |
| `scroll` | `direction=down\|up\|top\|bottom` `amount=500` | Scroll page |
| `type` | `selector=..` `text=..` | Type into input |
| `type_active` | `text=...` | Type into focused element |
| `type_trusted` | `selector=...` `text=...` | CDP trusted typing |
| `press_key` | `key=...` `modifiers=..` | 25 keys + ctrl/alt/shift/meta |
| `select_option` | `selector=..` `value=..` `text=..` | Select dropdown |
| `find_element` | `selector=..` | Check element existence |

### Content

| Command | Parameters | Description |
|---------|-----------|-------------|
| `get_content` | `tab_id=..` | Visible page text |
| `get_html` | `tab_id=..` | Full HTML source |
| `get_attribute` | `selector=..` `attribute=..` | Element attribute |
| `screenshot` | `tab_id=..` | Capture screenshot (base64) |
| `eval` | `js=...` | Execute JavaScript |
| `get_images` | `max_wait_ms=15000` `min_large=1` | Visible image URLs |

### Wait, Dialogs & Network

| Command | Parameters | Description |
|---------|-----------|-------------|
| `wait` | `ms=1000` | Wait N milliseconds |
| `wait_for_element` | `selector=..` `timeout=10000` | Poll until element appears |
| `handle_dialog` | `action=accept\|dismiss` | Handle alert/confirm/prompt |
| `fetch_api` | `url=...` `method=..` `headers=..` | Fetch from page context |

### Cookies, Storage & Upload

| Command | Parameters | Description |
|---------|-----------|-------------|
| `get_cookies` / `set_cookie` | `url=..` `name=..` `value=..` | Cookie read/write |
| `get_storage` / `set_storage` | `key=..` `store=local\|session` | localStorage/sessionStorage |
| `file_chooser_intercept` | `file_paths=...` `click_selector=...` | Upload files |
| `ping` / `version` | — | Health check |

</details>

## Load the Chrome Extension

The extension is **not** in the pip package — it lives in the browser. You need to load it once:

1. Clone the repo: `git clone https://github.com/bobcyw/chrome-bridge.git`
2. Open `chrome://extensions` → **Developer mode** (top right)
3. **Load unpacked** → select `extension/` from the cloned repo
4. Click the **Chrome Bridge icon** in the toolbar to activate

> **Windows**: double-click `scripts\start_bridge.bat` instead of step 2 above — it starts the server automatically.

## Platform Support

| Platform | Start server | Auto-start on login |
|----------|-------------|---------------------|
| **Windows** | `chrome-bridge serve --background` or double-click `start_bridge.bat` | `bash scripts/install_service.sh` |
| **macOS** | `chrome-bridge serve --background` | `bash scripts/install_service.sh` |
| **Linux** | `chrome-bridge serve --background` | `bash scripts/install_service.sh` |

`install_service.sh` auto-detects your OS and installs a LaunchAgent (macOS), systemd unit (Linux), or Startup shortcut (Windows).

**Ports**: WS `19876` + HTTP `19877`. To change them:

```bash
CHROME_BRIDGE_WS_PORT=9999 CHROME_BRIDGE_HTTP_PORT=9998 chrome-bridge serve
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Cannot connect` | Server not running → `chrome-bridge serve --background` |
| Port already in use | `CHROME_BRIDGE_WS_PORT=... CHROME_BRIDGE_HTTP_PORT=...` |
| No extension connected | Click the Chrome Bridge icon in the Chrome toolbar |
| Element not found | Try `wait_for_element` or `get_content` to check page state |
| Screenshot fails | Activate the target tab first |
| `eval` blocked by CSP | Use `click` / `click_text` / `get_content` instead |
| Dialog hangs the tab | `handle_dialog action=dismiss` |

## Requirements

- **Python** ≥ 3.10
- **Chrome** ≥ 88 (Manifest V3)
- **websockets** ≥ 12.0 (`pip install websockets`)

## License

Apache 2.0 — [LICENSE](LICENSE)
