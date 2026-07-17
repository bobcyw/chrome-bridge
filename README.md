# Chrome Bridge

**AI-to-Browser bridge** — Let AI coding agents (Claude Code, Cursor, Copilot, etc.) control your **real Chrome browser** via WebSocket.

No headless browser. No CDP detection. Your logins, cookies, and extensions stay intact.

## Architecture

```
AI Agent ──CLI──▶ send_cmd.py ──file──▶ runtime/.bridge_cmd.json
                                              │
                                   bridge_server.py (WebSocket, port 9876)
                                              │
                                   Chrome Extension ◀──▶ Your Real Browser
```

## Why Chrome Bridge?

- **No automation detection** — websites see your real Chrome, not Playwright/Puppeteer
- **Keeps logins** — all cookies, sessions, and extensions preserved
- **Simple protocol** — file-based IPC means AI agents can drive it with a single CLI call
- **Claude Code native** — includes a Skill definition for one-click integration

## Quick Start

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
# Or: pip install chrome-bridge
```

### 2. Load the Chrome Extension

1. Open `chrome://extensions` in Chrome
2. Enable **Developer mode** (toggle in top right)
3. Click **Load unpacked** and select the `extension/` folder
4. Click the Chrome Bridge icon in the toolbar to activate

### 3. Start the Bridge Server

```bash
# One-command start
bash scripts/start_bridge.sh

# Check status
bash scripts/status_bridge.sh
```

### 4. Test the Connection

```bash
python bridge/cli.py ping
# {"ok": true, "pong": true}
```

## Usage

### CLI

```bash
# Tab management
python bridge/cli.py new_tab url=https://www.example.com
python bridge/cli.py list_tabs
python bridge/cli.py find_tab keyword=example

# Page interaction
python bridge/cli.py click selector=#login-btn
python bridge/cli.py click_text text="Submit" mode=contains
python bridge/cli.py type selector=#search text="hello world"
python bridge/cli.py press_key key=Enter

# Content extraction
python bridge/cli.py get_content
python bridge/cli.py screenshot
python bridge/cli.py eval js="document.title"

# Wait
python bridge/cli.py wait ms=2000
```

### Python API

```python
from bridge import Browser

b = Browser()

# Tab management
b.open("https://www.example.com")
b.find_tab("example")
tabs = b.list_tabs()

# Page interaction
b.click("#login-btn")
b.click_text("Submit", mode="contains")
b.type("#search", "hello world")
b.press_key("Enter")
b.scroll("down", 800)

# Content extraction
content = b.get_content()
b.screenshot("screenshot.png")
title = b.eval("document.title")

# Check status
print(b.ping())  # True
```

## Command Reference

### Tab Management

| Command | Parameters | Description |
|---------|-----------|-------------|
| `new_tab` | `url=...` | Open new tab. Returns `{tabId, url, title}` |
| `navigate` | `url=...` `tab_id=..` | Navigate tab to URL (waits for load, max 30s) |
| `list_tabs` | — | List all tabs `[{id, title, url, active}]` |
| `find_tab` | `keyword=..` | Search tabs by title/URL. Returns first match `tabId` |
| `close_tab` | `tab_id=..` | Close tab (default: current active) |
| `get_url` | `tab_id=..` | Get tab URL and title |

### Page Interaction

| Command | Parameters | Description |
|---------|-----------|-------------|
| `click` | `selector=..` `tab_id=..` | Click element by CSS selector |
| `click_text` | `text=..` `mode=exact\|contains` | Click by visible text |
| `type` | `selector=..` `text=..` | Type into input field |
| `press_key` | `key=Enter\|Tab\|Escape\|Backspace\|Space` | Simulate key press |
| `scroll` | `direction=down\|up\|top\|bottom` `amount=500` | Scroll page |
| `find_element` | `selector=..` | Check element. Returns `{found, tag, text, visible, rect}` |

### Content

| Command | Parameters | Description |
|---------|-----------|-------------|
| `get_content` | `tab_id=..` | Get visible page text |
| `screenshot` | `tab_id=..` | Capture screenshot (base64 dataUrl) |
| `eval` | `js=...` `tab_id=..` | Execute JavaScript (may be blocked by CSP) |
| `wait` | `ms=1000` `tab_id=..` | Wait N milliseconds |
| `ping` | — | Test full pipeline |

## Claude Code Integration

Chrome Bridge includes a Claude Code Skill for seamless AI-driven browser control. See [docs/claude-code-setup.md](docs/claude-code-setup.md) for setup instructions.

Once configured, Claude Code can:
- Open websites and navigate pages
- Click buttons, fill forms, type text
- Extract page content and screenshots
- Search tabs and operate on specific pages

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ping` timeout | Server not running | `bash scripts/start_bridge.sh` |
| "No Chrome extension connected" | Extension SW suspended | Click extension icon in Chrome |
| "Element not found" | Wrong selector | Use `get_content` to verify page state |
| Screenshot returns `canvas-fallback` | Permission not active | Click extension icon, then retry |
| `eval` fails | Page CSP blocks eval | Use `click`/`click_text`/`get_content` instead |

## Requirements

- **Python** 3.10+
- **Chrome** 88+ (Manifest V3 support)
- **websockets** Python package (`pip install websockets`)

## Platform Support

| Platform | Status |
|----------|--------|
| Windows | Full support (Git Bash or WSL for shell scripts) |
| macOS | Full support |
| Linux | Full support |

## License

MIT — see [LICENSE](LICENSE) for details.
