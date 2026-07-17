"""
Chrome Bridge — Python API Wrapper
High-level browser automation API.

Usage:
    from bridge import Browser
    b = Browser()
    b.open("https://www.example.com")
    b.click_text("Submit")
    b.type("#q", "hello")
    b.press_key("Enter")
    content = b.get_content()
    b.screenshot("output.png")
"""

import json
import os
import subprocess
import sys

_BRIDGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CLI_PATH = os.path.join(_BRIDGE_DIR, "bridge", "cli.py")
_PYTHON = sys.executable


def _run(cmd: str, **kwargs) -> dict:
    """Execute a bridge command and return parsed result."""
    args = [_PYTHON, _CLI_PATH, cmd]
    for k, v in kwargs.items():
        if v is True:
            v = "true"
        elif v is False:
            v = "false"
        args.append(f"{k}={v}")

    result = subprocess.run(
        args, capture_output=True, text=True, timeout=65, cwd=_BRIDGE_DIR
    )
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"ok": False, "error": result.stdout.strip() or result.stderr.strip()}


def _require_ok(result: dict, action: str = "") -> dict:
    """Raise if bridge returned an error."""
    if not result.get("ok"):
        raise RuntimeError(
            f"Chrome Bridge error [{action}]: {result.get('error', 'unknown')}"
        )
    return result


class Browser:
    """High-level browser control via Chrome Bridge."""

    def __init__(self, tab_id: int = None):
        self._tab_id = tab_id

    # ── Tab Management ──────────────────────────────────────────

    def open(self, url: str) -> dict:
        """Open a new tab and navigate to URL. Returns {tabId, url, title}."""
        r = _require_ok(_run("new_tab", url=url), f"open({url})")
        self._tab_id = r.get("tabId")
        return r

    def navigate(self, url: str, tab_id: int = None) -> dict:
        """Navigate an existing tab to URL."""
        tid = tab_id or self._tab_id
        kwargs = {"url": url}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("navigate", **kwargs), f"navigate({url})")
        return r

    def list_tabs(self) -> list:
        """Return list of all open tabs [{id, title, url, active}]."""
        r = _require_ok(_run("list_tabs"), "list_tabs")
        return r.get("tabs", [])

    def find_tab(self, keyword: str) -> dict:
        """Search tabs by keyword (matches title or URL). Returns {tabId, count, tabs}."""
        r = _run("find_tab", keyword=keyword)
        if r.get("ok") and r.get("tabId"):
            self._tab_id = r["tabId"]
        _require_ok(r, f"find_tab({keyword})")
        return r

    def close_tab(self, tab_id: int = None):
        """Close a tab. Defaults to current active tab."""
        tid = tab_id or self._tab_id
        kwargs = {}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("close_tab", **kwargs), "close_tab")

    def get_url(self, tab_id: int = None) -> dict:
        """Get current tab URL and title. Returns {url, title, tabId}."""
        tid = tab_id or self._tab_id
        kwargs = {}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("get_url", **kwargs), "get_url")
        return r

    # ── Page Interaction ────────────────────────────────────────

    def click(self, selector: str, tab_id: int = None):
        """Click an element by CSS selector."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("click", **kwargs), f"click({selector})")

    def click_text(self, text: str, mode: str = "exact", tab_id: int = None):
        """Click an element by visible text. mode='exact' or 'contains'."""
        tid = tab_id or self._tab_id
        kwargs = {"text": text, "mode": mode}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("click_text", **kwargs), f"click_text({text})")

    def type(self, selector: str, text: str, tab_id: int = None):
        """Type text into an input field."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector, "text": text}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("type", **kwargs), f"type({selector})")

    def press_key(
        self,
        key: str = "Enter",
        selector: str = None,
        modifiers: str = None,
        tab_id: int = None,
    ):
        """Simulate key press. Supported keys: Enter, Tab, Escape, Backspace, Space, Delete, ArrowUp/Down/Left/Right, PageUp/Down, Home, End, F1-F12. modifiers: comma-separated (ctrl,alt,shift,meta)."""
        tid = tab_id or self._tab_id
        kwargs = {"key": key}
        if selector:
            kwargs["selector"] = selector
        if modifiers:
            kwargs["modifiers"] = modifiers
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("press_key", **kwargs), f"press_key({key})")

    def hover(self, selector: str, tab_id: int = None):
        """Hover mouse over an element (fires mouseover/mouseenter/mousemove events)."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("hover", **kwargs), f"hover({selector})")

    def double_click(self, selector: str, tab_id: int = None):
        """Double-click an element."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("double_click", **kwargs), f"double_click({selector})")

    def right_click(self, selector: str, tab_id: int = None):
        """Right-click an element (context menu)."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("right_click", **kwargs), f"right_click({selector})")

    def select_option(
        self,
        selector: str,
        value: str = None,
        text: str = None,
        index: int = None,
        tab_id: int = None,
    ):
        """Select an option in a <select> element. Match by value, text, or index."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector}
        if value:
            kwargs["value"] = value
        if text:
            kwargs["text"] = text
        if index is not None:
            kwargs["index"] = index
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("select_option", **kwargs), f"select_option({selector})")

    def go_back(self, tab_id: int = None):
        """Navigate back in browser history."""
        tid = tab_id or self._tab_id
        kwargs = {}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("go_back", **kwargs), "go_back")

    def go_forward(self, tab_id: int = None):
        """Navigate forward in browser history."""
        tid = tab_id or self._tab_id
        kwargs = {}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("go_forward", **kwargs), "go_forward")

    def reload(self, tab_id: int = None):
        """Reload the current page."""
        tid = tab_id or self._tab_id
        kwargs = {}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("reload", **kwargs), "reload")

    def get_html(self, tab_id: int = None) -> str:
        """Get full page HTML source."""
        tid = tab_id or self._tab_id
        kwargs = {}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("get_html", **kwargs), "get_html")
        return r.get("html", "")

    def get_attribute(self, selector: str, attribute: str, tab_id: int = None) -> str:
        """Get an element's attribute value. Special: 'innerHTML', 'outerHTML', 'textContent', 'class'."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector, "attribute": attribute}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("get_attribute", **kwargs), f"get_attribute({selector})")
        return r.get("value", "")

    def wait_for_element(
        self,
        selector: str,
        timeout: int = 10000,
        interval: int = 300,
        tab_id: int = None,
    ) -> dict:
        """Poll until an element matching selector appears. Returns {found, tag, text, visible, elapsed}."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector, "timeout": timeout, "interval": interval}
        if tid:
            kwargs["tab_id"] = tid
        return _require_ok(
            _run("wait_for_element", **kwargs), f"wait_for_element({selector})"
        )

    def handle_dialog(
        self, action: str = "dismiss", prompt_text: str = "", tab_id: int = None
    ) -> dict:
        """Handle alert/confirm/prompt dialog. action='accept' or 'dismiss'. Provide prompt_text for prompt dialogs."""
        tid = tab_id or self._tab_id
        kwargs = {"action": action, "prompt_text": prompt_text}
        if tid:
            kwargs["tab_id"] = tid
        return _require_ok(_run("handle_dialog", **kwargs), f"handle_dialog({action})")

    def get_cookies(self, url: str = "") -> list:
        """Get cookies. Optionally filter by URL. Returns list of cookie objects."""
        kwargs = {}
        if url:
            kwargs["url"] = url
        r = _require_ok(_run("get_cookies", **kwargs), "get_cookies")
        return r.get("cookies", [])

    def set_cookie(
        self,
        url: str,
        name: str,
        value: str,
        domain: str = None,
        path: str = None,
        secure: bool = False,
        http_only: bool = False,
        expiration_date: int = None,
    ) -> dict:
        """Set a browser cookie. Returns the created cookie object."""
        kwargs = {"url": url, "name": name, "value": value}
        if domain:
            kwargs["domain"] = domain
        if path:
            kwargs["path"] = path
        if secure:
            kwargs["secure"] = True
        if http_only:
            kwargs["httpOnly"] = True
        if expiration_date:
            kwargs["expirationDate"] = expiration_date
        r = _require_ok(_run("set_cookie", **kwargs), f"set_cookie({name})")
        return r.get("cookie", {})

    def get_storage(
        self, key: str = None, store: str = "local", tab_id: int = None
    ) -> dict:
        """Read localStorage (store='local') or sessionStorage (store='session'). Returns all items or a single key."""
        tid = tab_id or self._tab_id
        kwargs = {"store": store}
        if key:
            kwargs["key"] = key
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("get_storage", **kwargs), "get_storage")
        return r.get("data", {})

    def set_storage(
        self, key: str, value: str, store: str = "local", tab_id: int = None
    ):
        """Write to localStorage (store='local') or sessionStorage (store='session')."""
        tid = tab_id or self._tab_id
        kwargs = {"key": key, "value": value, "store": store}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("set_storage", **kwargs), f"set_storage({key})")

    def scroll(self, direction: str = "down", amount: int = 500, tab_id: int = None):
        """Scroll page. direction: up/down/top/bottom."""
        tid = tab_id or self._tab_id
        kwargs = {"direction": direction, "amount": amount}
        if tid:
            kwargs["tab_id"] = tid
        _require_ok(_run("scroll", **kwargs), f"scroll({direction})")

    def find_element(self, selector: str, tab_id: int = None) -> dict:
        """Check if element exists. Returns {found, tag, text, visible, rect}."""
        tid = tab_id or self._tab_id
        kwargs = {"selector": selector}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("find_element", **kwargs), f"find_element({selector})")
        return r

    # ── Content Extraction ──────────────────────────────────────

    def get_content(self, tab_id: int = None) -> str:
        """Get visible page text."""
        tid = tab_id or self._tab_id
        kwargs = {}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("get_content", **kwargs), "get_content")
        return r.get("text", "")

    def screenshot(self, filepath: str = None, tab_id: int = None) -> str:
        """Take screenshot. Returns base64 dataUrl, or saves to filepath if given."""
        tid = tab_id or self._tab_id
        kwargs = {}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("screenshot", **kwargs), "screenshot")
        data_url = r.get("dataUrl", "")
        if filepath and data_url:
            import base64

            header, encoded = data_url.split(",", 1)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(encoded))
        return data_url

    def eval(self, js: str, tab_id: int = None) -> str:
        """Execute JavaScript in page and return result."""
        tid = tab_id or self._tab_id
        kwargs = {"js": js}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("eval", **kwargs), "eval(...)")
        return r.get("result", "")

    def wait(self, ms: int = 1000, tab_id: int = None) -> dict:
        """Wait N milliseconds."""
        tid = tab_id or self._tab_id
        kwargs = {"ms": ms}
        if tid:
            kwargs["tab_id"] = tid
        r = _require_ok(_run("wait", **kwargs), f"wait({ms})")
        return r

    # ── Convenience ─────────────────────────────────────────────

    def ping(self) -> bool:
        """Test if bridge is alive."""
        r = _run("ping")
        return r.get("pong", False)

    @property
    def tab_id(self) -> int:
        return self._tab_id

    @tab_id.setter
    def tab_id(self, value: int):
        self._tab_id = value

    def __repr__(self):
        return f"<Browser tab_id={self._tab_id or 'current'}>"


# ── Quick test ──────────────────────────────────────────────────
if __name__ == "__main__":
    b = Browser()
    print(f"Ping: {b.ping()}")
    print(f"Tabs: {len(b.list_tabs())} open")
