# CLAUDE.md

This file provides instructions for Claude Code when working with the Chrome Bridge project.

## First-Time Setup

When you first open this project, run these steps automatically:

```bash
# 1. Install the package
pip install -e .

# 2. Install the skill so Claude can use chrome-bridge in ANY project
mkdir -p .claude/skills/chrome-bridge
cp docs/SKILL.md .claude/skills/chrome-bridge/SKILL.md

# 3. Start the server in background
python bridge/cli.py serve --background
```

After setup, the skill is registered. Restart Claude Code and the `chrome-bridge` skill will be available globally.

For users who installed via PyPI (`pip install chrome-bridge`), only step 2-3 are needed.

## Chrome Bridge — Universal Browser Control

You can control the **user's real Chrome browser** through the Chrome Bridge extension + server. The browser is NOT headless — websites see a real Chrome with all logins and cookies intact.

### Architecture

```
CLI / API ──HTTP POST :19877──▶ bridge/server.py ──WebSocket :19876──▶ Chrome Extension ──▶ Browser
```

### Prerequisites Check

Always verify the bridge is alive before attempting browser operations:

```bash
python bridge/cli.py ping
```

If `"ok": true, "pong": true` — server is running and extension is connected. Proceed.

If "Cannot connect" — server isn't running. Start it:
```bash
python bridge/cli.py serve --background   # daemon mode
# or: bash scripts/start_bridge.bat       # Windows double-click
```

If "No Chrome extension connected" — ask the user to:
1. Open `chrome://extensions` in Chrome
2. Ensure "Chrome Bridge" extension is loaded and enabled
3. Click the extension icon in the toolbar to activate the service worker

**Ports**: This version uses WS `19876` + HTTP `19877`. Override via env:
- `CHROME_BRIDGE_WS_PORT` (default 19876)
- `CHROME_BRIDGE_HTTP_PORT` (default 19877)

### Command Reference (all via CLI)

```bash
python bridge/cli.py <command> [key=value ...]
```

#### Tab Management
```
new_tab url=...              - Open new tab. Returns {tabId, url, title}
navigate url=... tab_id=..   - Navigate to URL (auto-waits for load, max 30s)
list_tabs                    - List all tabs [{id, title, url, active}]
find_tab keyword=..          - Search tabs by title/URL. Returns first match tabId
close_tab tab_id=..          - Close tab (default: current active)
get_url tab_id=..            - Get tab URL and title
activate_tab tab_id=..       - Switch to tab
go_back tab_id=..            - Navigate back in history
go_forward tab_id=..         - Navigate forward in history
reload tab_id=..             - Reload page
```

#### Mouse & Interaction
```
click selector=.. tab_id=..         - Click by CSS selector
click_text text=.. mode=exact|contains tab_id=.. - Click by visible text
double_click selector=.. tab_id=..  - Double-click element
right_click selector=.. tab_id=..   - Right-click (context menu)
hover selector=.. tab_id=..         - Hover mouse over element
scroll direction=down|up|top|bottom amount=500 tab_id=.. - Scroll page
```

#### Keyboard & Input
```
type selector=.. text=.. tab_id=..  - Type into input field
type_active text=... tab_id=..      - Type into currently focused element
type_trusted selector=.. text=.. tab_id=.. - Trusted typing via CDP
press_key key=.. selector=.. modifiers=.. tab_id=.. - Key press
         Keys: Enter Tab Escape Backspace Space Delete
               ArrowUp ArrowDown ArrowLeft ArrowRight
               PageUp PageDown Home End F1-F12
         Modifiers: ctrl,alt,shift,meta (comma-separated)
select_option selector=.. value=.. text=.. index=.. tab_id=.. - Select dropdown
find_element selector=.. tab_id=..  - Check element. Returns {found, tag, text, visible, rect}
```

#### Content Extraction
```
get_content tab_id=..              - Get visible page text
get_html tab_id=..                 - Get full page HTML
get_attribute selector=.. attribute=.. tab_id=.. - Get element attribute (also: innerHTML, outerHTML, textContent, class)
screenshot tab_id=..               - Capture screenshot (base64 dataUrl)
eval js=... tab_id=..              - Execute JavaScript
get_images max_wait_ms=15000 min_large=1 tab_id=.. - Get visible image URLs
```

#### Wait & Dialogs
```
wait ms=1000 tab_id=..             - Wait N milliseconds
wait_for_element selector=.. timeout=10000 interval=300 tab_id=.. - Poll until element appears
handle_dialog action=accept|dismiss prompt_text=.. tab_id=.. - Handle alert/confirm/prompt
```

#### Network, Cookies & Storage
```
fetch_api url=.. method=.. body=.. headers=.. tab_id=.. - Fetch from page context
get_cookies url=..                             - Get cookies
set_cookie url=.. name=.. value=.. domain=.. path=.. - Set cookie
get_storage key=.. store=local|session tab_id=.. - Read localStorage/sessionStorage
set_storage key=.. value=.. store=local|session tab_id=.. - Write localStorage/sessionStorage
```

#### File Upload
```
file_chooser_intercept file_paths=.. click_selector=.. tab_id=.. - Intercept file chooser
```

#### Connection
```
ping                 - Test full pipeline
version              - Show version and command list
```

### Key Rules When Operating the Browser

1. **Wait after interactions**: `navigate` auto-waits, but `click`/`click_text` may trigger async changes. Add `wait ms=1000~3000` after key interactions. Use `wait_for_element` for dynamic content.
2. **Reuse tabs**: Use `find_tab` to locate already-open pages; avoid repeated `new_tab`.
3. **click_text fallback**: Try `mode=exact` first; fall back to `mode=contains`; if both fail, use `get_content` to verify actual page text.
4. **hover before hidden targets**: Menus, sub-items, and tooltips often only appear on hover. Use `hover` first.
5. **Dialogs block tabs**: If a page opens `alert()`/`confirm()`/`prompt()`, that tab is frozen until `handle_dialog` is called.
6. **Dropdowns**: Use `select_option` for native `<select>`. For custom dropdowns, use `click` to open + `click_text` to pick.
7. **eval limitations**: Sites with strict CSP may block eval. Fall back to `click`/`click_text`/`get_content`.
8. **No concurrency**: Send one command at a time, wait for result, then send the next.

### Starting a Browser Session

```bash
# 1. Ensure server is running
python bridge/cli.py ping

# 2. Open a site
python bridge/cli.py new_tab url=https://www.example.com

# 3. Interact
python bridge/cli.py get_content
python bridge/cli.py click_text text="Login"
python bridge/cli.py type selector="#username" text="user@example.com"
python bridge/cli.py press_key key=Tab
python bridge/cli.py type_active text="password123"
python bridge/cli.py press_key key=Enter

# 4. Wait and verify
python bridge/cli.py wait ms=3000
python bridge/cli.py wait_for_element selector=".dashboard"
python bridge/cli.py get_url
```

### Python API (for complex multi-step operations)

```python
import sys; sys.path.insert(0, '.')
from bridge import Browser

b = Browser()
b.open("https://www.example.com")
b.click_text("Login")
b.type("#email", "user@example.com")
b.press_key("Enter")
b.wait_for_element(".welcome")
content = b.get_content()
```

The CLI approach is simpler for step-by-step AI decision-making.

## Running Tests

```bash
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

## Publishing to PyPI

The publish script lives in `notes/publish.sh` (gitignored, contains the token).

```bash
bash notes/publish.sh
```

This auto-builds the wheel and uploads to PyPI. Before publishing:

1. Update version in `pyproject.toml`, `bridge/__init__.py`, `extension/background.js` (version command), and `bridge/server.py` (banner)
2. Run tests: `python -m pytest tests/ -v`
3. Commit and push
4. Run `bash obsidian/publish.sh`

If the token is expired or needs rotation, edit `notes/publish.sh` and replace `PYPI_TOKEN`.
