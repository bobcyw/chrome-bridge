---
name: chrome-bridge
description: >-
  Universal Chrome browser control. Use when you need to operate a browser (open sites, click buttons,
  type text, take screenshots, scrape page content), fill forms, handle file uploads, manage dialogs,
  read/write cookies and storage, or access data from logged-in websites.
  Triggers: browser, Chrome, open webpage, click, type, screenshot, tab, page content, automation, form, dialog.
---

# Chrome Bridge — Browser Control Skill

Control the **user's real Chrome browser** via Chrome Extension + WebSocket bridge.
Websites cannot detect automation; login sessions and cookies are preserved.

## Architecture

```
bridge/cli.py ──write file──▶ runtime/.bridge_cmd.json
                                    │
                         bridge/server.py (background service, port 9876)
                                    │
                         WebSocket ◀─▶ Chrome Extension
                                    │
                           User's browser (real Chrome)
```

## Prerequisites

Check if the service is running before each operation:

```bash
python ~/chrome-bridge/bridge/cli.py ping
```

If it returns `"pong": true`, the service is healthy. If it times out or has no response, start the service:

```bash
bash ~/chrome-bridge/scripts/start_bridge.sh
```

If it still fails, the Chrome Extension is not connected. Ask the user to click the extension icon in `chrome://extensions`.

## Command Reference

All commands use the CLI tool:

```bash
python ~/chrome-bridge/bridge/cli.py <command> [key=value ...]
```

### Tab Management

| Command | Parameters | Description |
|---------|-----------|-------------|
| `new_tab` | `url=...` | Open new tab. Returns `{tabId, url, title}` |
| `navigate` | `url=...` `tab_id=..` | Navigate to URL (waits for page load, max 30s) |
| `list_tabs` | — | List all tabs `[{id, title, url, active}]` |
| `find_tab` | `keyword=..` | Search tabs by title/URL. Returns first match `tabId` |
| `close_tab` | `tab_id=..` | Close tab (default: current active) |
| `get_url` | `tab_id=..` | Get tab URL and title |
| `activate_tab` | `tab_id=..` | Switch to tab (makes it active) |
| `go_back` | `tab_id=..` | Navigate back in browser history |
| `go_forward` | `tab_id=..` | Navigate forward in browser history |
| `reload` | `tab_id=..` | Reload the current page |

### Page Interaction

| Command | Parameters | Description |
|---------|-----------|-------------|
| `click` | `selector=..` `tab_id=..` | Click by CSS selector |
| `click_text` | `text=..` `mode=exact\|contains` `tab_id=..` | Click by visible text. `contains` for fuzzy match |
| `double_click` | `selector=..` `tab_id=..` | Double-click element |
| `right_click` | `selector=..` `tab_id=..` | Right-click (fires contextmenu event) |
| `hover` | `selector=..` `tab_id=..` | Hover mouse over element (triggers menus, tooltips) |
| `type` | `selector=..` `text=..` `tab_id=..` | Type into input, fires input/change events |
| `type_active` | `text=...` `tab_id=..` | Type into currently focused element |
| `type_trusted` | `selector=...` `text=...` `tab_id=..` | Trusted typing via CDP (bypasses React/Vue event handling) |
| `press_key` | `key=...` `selector=..` `modifiers=..` `tab_id=..` | Simulate key press. Keys: Enter, Tab, Escape, Backspace, Space, Delete, ArrowUp/Down/Left/Right, PageUp/Down, Home, End, F1-F12. Modifiers: ctrl,alt,shift,meta (comma-separated) |
| `scroll` | `direction=down\|up\|top\|bottom` `amount=500` `tab_id=..` | Scroll page |
| `select_option` | `selector=..` `value=..` `text=..` `index=..` `tab_id=..` | Select option in \<select\>. Match by value, text, or index |
| `find_element` | `selector=..` `tab_id=..` | Check element. Returns `{found, tag, text, visible, rect}` |

### Content

| Command | Parameters | Description |
|---------|-----------|-------------|
| `get_content` | `tab_id=..` | Get visible page text |
| `get_html` | `tab_id=..` | Get full page HTML source |
| `get_attribute` | `selector=..` `attribute=..` `tab_id=..` | Get element attribute. Special: `innerHTML`, `outerHTML`, `textContent`, `class` |
| `screenshot` | `tab_id=..` | Screenshot. Returns `{dataUrl, method}` |
| `eval` | `js=...` `tab_id=..` | Execute JS (may be blocked by page CSP) |
| `get_images` | `max_wait_ms=15000` `min_large=1` `tab_id=..` | Poll for large visible images on page |
| `wait` | `ms=1000` `tab_id=..` | Wait N milliseconds |
| `wait_for_element` | `selector=..` `timeout=10000` `interval=300` `tab_id=..` | Poll until element appears. Returns `{found, tag, text, visible, elapsed}` |

### Dialogs

| Command | Parameters | Description |
|---------|-----------|-------------|
| `handle_dialog` | `action=accept\|dismiss` `prompt_text=..` `tab_id=..` | Handle alert/confirm/prompt dialog. Use `prompt_text` for prompt dialogs |

### Network

| Command | Parameters | Description |
|---------|-----------|-------------|
| `fetch_api` | `url=...` `method=POST` `body=...` `headers=...` `tab_id=..` | Fetch from within the page context. `headers` as JSON string |

### Cookies & Storage

| Command | Parameters | Description |
|---------|-----------|-------------|
| `get_cookies` | `url=..` | Get all cookies (optionally filtered by URL) |
| `set_cookie` | `url=..` `name=..` `value=..` `domain=..` `path=..` ... | Set a browser cookie |
| `get_storage` | `key=..` `store=local\|session` `tab_id=..` | Read localStorage/sessionStorage. Omit key to get all |
| `set_storage` | `key=..` `value=..` `store=local\|session` `tab_id=..` | Write to localStorage/sessionStorage |

### File Upload

| Command | Parameters | Description |
|---------|-----------|-------------|
| `file_chooser_intercept` | `file_paths=...` `click_selector=...` `tab_id=..` | Intercept file chooser dialog and inject files |

## Key Rules

1. **Wait after actions**: `navigate` auto-waits for load, but `click`/`click_text` may trigger page changes. Add `wait ms=1000~3000` after key interactions. Use `wait_for_element` to wait for dynamic content
2. **Reuse tabs**: Use `find_tab` to locate already-open pages; avoid repeated `new_tab`
3. **`click_text` fallback**: Try `mode=exact` first (default); if it fails, switch to `mode=contains`; if still failing, use `get_content` to verify actual page text
4. **Dropdowns**: Use `select_option` for native `<select>` elements; for custom dropdowns, use `click` to open + `click_text` to pick an option
5. **Hover first**: Many UI elements (submenus, tooltips, hidden buttons) only appear on hover — use `hover` before clicking hidden elements
6. **Keyboard navigation**: Use `press_key key=ArrowDown` for navigating lists, autocomplete suggestions, etc.
7. **Dialogs**: If a page triggers `alert()`/`confirm()`/`prompt()`, the tab will hang until you call `handle_dialog`
8. **Screenshot pre-check**: The target tab must be active (`captureVisibleTab` limitation); the system auto-activates inactive tabs
9. **eval limitations**: Some sites' CSP blocks `eval()` — use `click`/`click_text`/`get_content` instead
10. **No concurrency**: The cross-process architecture doesn't support simultaneous commands. Send one at a time, wait for result, then send the next

## Python API (optional)

For complex multi-step operations:

```python
import sys; sys.path.insert(0, '~/chrome-bridge')
from bridge import Browser
b = Browser()
b.open("https://www.example.com")
b.hover(".menu-item")
b.click_text("Login")
b.type("#username", "hello")
b.press_key("Tab")
b.type("#password", "world")
b.press_key("Enter")
b.wait_for_element(".dashboard")
content = b.get_content()
b.screenshot("result.png")
```

However, using the CLI directly is simpler and allows step-by-step AI decision-making.
