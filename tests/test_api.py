"""Tests for bridge/api.py — Browser class high-level API."""

import json
import os
import sys
import subprocess
from unittest.mock import patch, MagicMock, call
import pytest

from bridge.api import Browser, _require_ok


# ================================================================
# _require_ok
# ================================================================

class TestRequireOk:
    def test_ok_result_passes_through(self):
        result = {"ok": True, "data": 42}
        assert _require_ok(result) == result

    def test_not_ok_raises(self):
        with pytest.raises(RuntimeError, match="Chrome Bridge error"):
            _require_ok({"ok": False, "error": "something broke"})

    def test_not_ok_with_action_label(self):
        with pytest.raises(RuntimeError, match=r"Chrome Bridge error \[click\(.btn\)\]"):
            _require_ok({"ok": False, "error": "not found"}, "click(.btn)")

    def test_implicit_not_ok(self):
        """Missing 'ok' key is also an error."""
        with pytest.raises(RuntimeError):
            _require_ok({"result": "no ok field"})


# ================================================================
# Browser — all methods (mocked CLI)
# ================================================================

@pytest.fixture
def browser():
    """A Browser instance for testing."""
    return Browser()


@pytest.fixture
def mock_run():
    """Patch _run to return fake CLI results."""
    with patch('bridge.api._run') as mock:
        yield mock


# ── Tab Management ──────────────────────────────────────────────

class TestTabManagement:
    def test_open_new_tab(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "tabId": 10, "url": "https://example.com", "title": "Example"}
        result = browser.open("https://example.com")
        mock_run.assert_called_once_with("new_tab", url="https://example.com")
        assert result["tabId"] == 10
        assert browser.tab_id == 10

    def test_navigate_existing_tab(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "tabId": 5, "url": "https://github.com"}
        browser.navigate("https://github.com", tab_id=5)
        mock_run.assert_called_once_with("navigate", url="https://github.com", tab_id=5)

    def test_navigate_uses_stored_tab_id(self, browser, mock_run):
        browser.tab_id = 8
        mock_run.return_value = {"ok": True, "tabId": 8}
        browser.navigate("https://example.com")
        mock_run.assert_called_once_with("navigate", url="https://example.com", tab_id=8)

    def test_list_tabs(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "tabs": [{"id": 1}, {"id": 2}]}
        tabs = browser.list_tabs()
        mock_run.assert_called_once_with("list_tabs")
        assert len(tabs) == 2

    def test_list_tabs_empty(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "tabs": []}
        tabs = browser.list_tabs()
        assert tabs == []

    def test_find_tab_updates_tab_id(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "tabId": 42, "count": 1}
        result = browser.find_tab("example")
        mock_run.assert_called_once_with("find_tab", keyword="example")
        assert result["tabId"] == 42
        assert browser.tab_id == 42

    def test_find_tab_not_found(self, browser, mock_run):
        mock_run.return_value = {"ok": False, "error": "No tab found"}
        with pytest.raises(RuntimeError):
            browser.find_tab("nonexistent")

    def test_close_tab_default(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.close_tab()
        mock_run.assert_called_once_with("close_tab")

    def test_close_tab_specific(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.close_tab(tab_id=99)
        mock_run.assert_called_once_with("close_tab", tab_id=99)

    def test_get_url(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "url": "https://example.com", "title": "Example"}
        result = browser.get_url()
        mock_run.assert_called_once_with("get_url")
        assert result["url"] == "https://example.com"


# ── Mouse ───────────────────────────────────────────────────────

class TestMouse:
    def test_click(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.click(".btn")
        mock_run.assert_called_once_with("click", selector=".btn")

    def test_click_text_exact(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.click_text("Submit")
        mock_run.assert_called_once_with("click_text", text="Submit", mode="exact")

    def test_click_text_contains(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.click_text("Sub", mode="contains")
        mock_run.assert_called_once_with("click_text", text="Sub", mode="contains")

    def test_hover(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.hover(".menu-item")
        mock_run.assert_called_once_with("hover", selector=".menu-item")

    def test_double_click(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.double_click(".row")
        mock_run.assert_called_once_with("double_click", selector=".row")

    def test_right_click(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.right_click(".item")
        mock_run.assert_called_once_with("right_click", selector=".item")


# ── Keyboard & Input ────────────────────────────────────────────

class TestKeyboard:
    def test_type(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.type("#q", "hello")
        mock_run.assert_called_once_with("type", selector="#q", text="hello")

    def test_press_key_default(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.press_key()
        mock_run.assert_called_once_with("press_key", key="Enter")

    def test_press_key_with_modifiers(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.press_key("a", modifiers="ctrl")
        mock_run.assert_called_once_with("press_key", key="a", modifiers="ctrl")

    def test_press_key_arrow(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.press_key("ArrowDown", selector="#list")
        mock_run.assert_called_once_with("press_key", key="ArrowDown", selector="#list")


# ── Form ────────────────────────────────────────────────────────

class TestForm:
    def test_select_option_by_value(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.select_option("#country", value="CN")
        mock_run.assert_called_once_with("select_option", selector="#country", value="CN")

    def test_select_option_by_text(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.select_option("#country", text="China")
        mock_run.assert_called_once_with("select_option", selector="#country", text="China")

    def test_select_option_by_index(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.select_option("#country", index=2)
        mock_run.assert_called_once_with("select_option", selector="#country", index=2)


# ── Navigation ──────────────────────────────────────────────────

class TestNavigation:
    def test_go_back(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.go_back()
        mock_run.assert_called_once_with("go_back")

    def test_go_forward(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.go_forward()
        mock_run.assert_called_once_with("go_forward")

    def test_reload(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.reload()
        mock_run.assert_called_once_with("reload")


# ── Content Extraction ──────────────────────────────────────────

class TestContent:
    def test_get_content(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "text": "Hello World"}
        text = browser.get_content()
        mock_run.assert_called_once_with("get_content")
        assert text == "Hello World"

    def test_get_html(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "html": "<html><body>hi</body></html>"}
        html = browser.get_html()
        mock_run.assert_called_once_with("get_html")
        assert "<body>" in html

    def test_get_attribute(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "value": "my-class"}
        val = browser.get_attribute(".btn", "class")
        mock_run.assert_called_once_with("get_attribute", selector=".btn", attribute="class")
        assert val == "my-class"

    def test_find_element_found(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "found": True, "tag": "BUTTON", "visible": True}
        result = browser.find_element(".btn")
        mock_run.assert_called_once_with("find_element", selector=".btn")
        assert result["found"] is True

    def test_find_element_not_found(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "found": False}
        result = browser.find_element(".nonexistent")
        assert result["found"] is False

    def test_screenshot(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "dataUrl": "data:image/png;base64,AAAA"}
        result = browser.screenshot()
        mock_run.assert_called_once_with("screenshot")
        assert result.startswith("data:")

    def test_screenshot_save_to_file(self, browser, mock_run, tmp_path):
        mock_run.return_value = {"ok": True, "dataUrl": "data:image/png;base64,iVBORw0KGgo="}
        filepath = str(tmp_path / "screenshot.png")
        result = browser.screenshot(filepath=filepath)
        assert os.path.exists(filepath)

    def test_eval(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "result": "Example Title"}
        result = browser.eval("document.title")
        mock_run.assert_called_once_with("eval", js="document.title")
        assert result == "Example Title"


# ── Wait & Dialogs ──────────────────────────────────────────────

class TestWait:
    def test_wait_default(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.wait()
        mock_run.assert_called_once_with("wait", ms=1000)

    def test_wait_custom(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.wait(ms=3000)
        mock_run.assert_called_once_with("wait", ms=3000)

    def test_wait_for_element(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "found": True, "tag": "DIV", "visible": True, "elapsed": 1200}
        result = browser.wait_for_element(".dynamic-content")
        mock_run.assert_called_once_with("wait_for_element", selector=".dynamic-content", timeout=10000, interval=300)
        assert result["found"] is True

    def test_handle_dialog_accept(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "action": "accept", "dialogType": "confirm"}
        result = browser.handle_dialog(action="accept")
        mock_run.assert_called_once_with("handle_dialog", action="accept", prompt_text="")
        assert result["action"] == "accept"

    def test_handle_dialog_with_prompt(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "action": "accept"}
        browser.handle_dialog(action="accept", prompt_text="John")
        mock_run.assert_called_once_with("handle_dialog", action="accept", prompt_text="John")


# ── Cookies & Storage ───────────────────────────────────────────

class TestCookies:
    def test_get_cookies_all(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "cookies": [{"name": "session", "value": "abc"}]}
        cookies = browser.get_cookies()
        mock_run.assert_called_once_with("get_cookies")
        assert len(cookies) == 1

    def test_get_cookies_filtered(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "cookies": []}
        browser.get_cookies(url="https://example.com")
        mock_run.assert_called_once_with("get_cookies", url="https://example.com")

    def test_set_cookie(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "cookie": {"name": "token", "value": "xyz"}}
        result = browser.set_cookie("https://example.com", "token", "xyz")
        mock_run.assert_called_once_with("set_cookie", url="https://example.com", name="token", value="xyz")
        assert result["name"] == "token"

    def test_set_cookie_with_options(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "cookie": {}}
        browser.set_cookie("https://a.com", "k", "v", domain=".a.com", path="/", secure=True)
        call_args = mock_run.call_args
        # Check that optional params were passed
        assert call_args[1]["domain"] == ".a.com"
        assert call_args[1]["path"] == "/"
        assert call_args[1]["secure"] is True


class TestStorage:
    def test_get_storage_all(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "data": {"theme": "dark", "lang": "en"}}
        data = browser.get_storage()
        mock_run.assert_called_once_with("get_storage", store="local")
        assert data == {"theme": "dark", "lang": "en"}

    def test_get_storage_single_key(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "data": {"key": "theme", "value": "dark"}}
        data = browser.get_storage(key="theme")
        mock_run.assert_called_once_with("get_storage", store="local", key="theme")
        assert data == {"key": "theme", "value": "dark"}

    def test_get_storage_session(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "data": {}}
        browser.get_storage(store="session")
        mock_run.assert_called_once_with("get_storage", store="session")

    def test_set_storage(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.set_storage("theme", "dark")
        mock_run.assert_called_once_with("set_storage", key="theme", value="dark", store="local")


# ── Misc ────────────────────────────────────────────────────────

class TestMisc:
    def test_ping_ok(self, browser, mock_run):
        mock_run.return_value = {"ok": True, "pong": True}
        assert browser.ping() is True
        mock_run.assert_called_once_with("ping")

    def test_ping_fail(self, browser, mock_run):
        mock_run.return_value = {"ok": False, "error": "timeout"}
        assert browser.ping() is False

    def test_scroll(self, browser, mock_run):
        mock_run.return_value = {"ok": True}
        browser.scroll("down", 800)
        mock_run.assert_called_once_with("scroll", direction="down", amount=800)

    def test_tab_id_property(self, browser):
        assert browser.tab_id is None
        browser.tab_id = 55
        assert browser.tab_id == 55

    def test_repr(self, browser):
        assert "current" in repr(browser)
        browser.tab_id = 10
        assert "10" in repr(browser)


# ================================================================
# Edge cases & Error handling
# ================================================================

class TestErrorHandling:
    def test_open_fails(self, browser, mock_run):
        mock_run.return_value = {"ok": False, "error": "No extension connected"}
        with pytest.raises(RuntimeError, match="No extension connected"):
            browser.open("https://example.com")

    def test_navigate_fails(self, browser, mock_run):
        mock_run.return_value = {"ok": False, "error": "Tab not found"}
        with pytest.raises(RuntimeError, match="Tab not found"):
            browser.navigate("https://example.com", tab_id=999)

    def test_json_decode_error_in_run(self):
        """If CLI returns non-JSON, _run should return an error dict, not crash."""
        from bridge.api import _run
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = subprocess.CompletedProcess(
                args=[], returncode=1, stdout="Something went wrong", stderr=""
            )
            result = _run("ping")
            assert result["ok"] is False
            assert "Something went wrong" in result["error"]
