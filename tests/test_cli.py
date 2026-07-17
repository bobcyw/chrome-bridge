"""Tests for bridge/cli.py — argument parsing and HTTP command dispatch."""

import json
import io
import sys
import pytest
from unittest.mock import patch

from bridge import cli


class TestParseArgs:
    """Argument parsing: key=value → typed kwargs dict."""

    def test_empty_args(self):
        assert cli.parse_args([]) == {}

    def test_string_value(self):
        result = cli.parse_args(["url=https://example.com"])
        assert result == {"url": "https://example.com"}

    def test_int_value(self):
        result = cli.parse_args(["timeout=5000"])
        assert result == {"timeout": 5000}
        assert isinstance(result["timeout"], int)

    def test_float_value(self):
        result = cli.parse_args(["amount=3.14"])
        assert result == {"amount": 3.14}
        assert isinstance(result["amount"], float)

    def test_bool_true(self):
        result = cli.parse_args(["secure=true"])
        assert result == {"secure": True}
        assert isinstance(result["secure"], bool)

    def test_bool_false(self):
        result = cli.parse_args(["httpOnly=false"])
        assert result == {"httpOnly": False}

    def test_true_uppercase(self):
        result = cli.parse_args(["flag=True"])
        assert result == {"flag": True}

    def test_json_array(self):
        result = cli.parse_args(['file_paths=["a.txt","b.txt"]'])
        assert result == {"file_paths": ["a.txt", "b.txt"]}

    def test_json_object(self):
        result = cli.parse_args(['headers={"Authorization":"Bearer xyz"}'])
        assert result == {"headers": {"Authorization": "Bearer xyz"}}

    def test_invalid_json_falls_back_to_string(self):
        result = cli.parse_args(["data={incomplete"])
        assert result == {"data": "{incomplete"}

    def test_multiple_args(self):
        result = cli.parse_args(
            [
                "url=https://example.com",
                "timeout=30",
                "secure=true",
            ]
        )
        assert result == {
            "url": "https://example.com",
            "timeout": 30,
            "secure": True,
        }

    def test_value_containing_equals(self):
        result = cli.parse_args(["url=https://example.com?a=1&b=2"])
        assert result == {"url": "https://example.com?a=1&b=2"}

    def test_negative_int(self):
        result = cli.parse_args(["delta_y=-500"])
        assert result == {"delta_y": -500}

    def test_zero(self):
        result = cli.parse_args(["index=0"])
        assert result == {"index": 0}


class TestSendCmd:
    """HTTP-based command dispatch."""

    def test_sends_post_with_correct_payload(self):
        """send_cmd should POST JSON to the bridge server and return the response."""
        mock_response = io.BytesIO(json.dumps({"ok": True, "pong": True}).encode())

        with patch(
            "urllib.request.urlopen", return_value=mock_response
        ) as mock_urlopen:
            result = cli.send_cmd("ping")
            assert result == {"ok": True, "pong": True}

            # Verify the request was built correctly
            call_args = mock_urlopen.call_args[0][0]
            assert call_args.method == "POST"
            assert call_args.full_url == cli.BRIDGE_URL
            sent_data = json.loads(call_args.data)
            assert sent_data == {"cmd": "ping", "args": {}}

    def test_sends_args(self):
        """kwargs should be sent as the 'args' object."""
        mock_response = io.BytesIO(json.dumps({"ok": True, "tabId": 42}).encode())

        with patch(
            "urllib.request.urlopen", return_value=mock_response
        ) as mock_urlopen:
            result = cli.send_cmd("new_tab", url="https://example.com")
            assert result == {"ok": True, "tabId": 42}

            call_args = mock_urlopen.call_args[0][0]
            sent_data = json.loads(call_args.data)
            assert sent_data["cmd"] == "new_tab"
            assert sent_data["args"] == {"url": "https://example.com"}

    def test_js_file_parameter(self, tmp_path):
        """js_file= should read the file and pass its content as js=."""
        js_file = tmp_path / "script.js"
        js_file.write_text("document.title")

        mock_response = io.BytesIO(
            json.dumps({"ok": True, "result": "Example"}).encode()
        )

        with patch(
            "urllib.request.urlopen", return_value=mock_response
        ) as mock_urlopen:
            result = cli.send_cmd("eval", js_file=str(js_file))
            assert result["ok"] is True

            call_args = mock_urlopen.call_args[0][0]
            sent_data = json.loads(call_args.data)
            assert sent_data["args"]["js"] == "document.title"
            assert "js_file" not in sent_data["args"]

    def test_connection_error(self):
        """If server is not running, return a descriptive error."""
        import urllib.error

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("Connection refused"),
        ):
            result = cli.send_cmd("ping")
            assert result["ok"] is False
            assert "Cannot connect" in result["error"]

    def test_server_error(self):
        """HTTP errors from the server should be parsed and returned."""
        import urllib.error

        error_body = json.dumps(
            {"ok": False, "error": "No Chrome extension connected"}
        ).encode()
        fp = io.BytesIO(error_body)
        http_error = urllib.error.HTTPError(
            "http://127.0.0.1:9877/cmd", 503, "Service Unavailable", {}, fp
        )
        with patch("urllib.request.urlopen", side_effect=http_error):
            result = cli.send_cmd("ping")
            assert result["ok"] is False
            assert "No Chrome extension connected" in result["error"]


class TestHelpText:
    """Help text should document all commands."""

    def test_help_text_not_empty(self):
        assert len(cli.HELP_TEXT) > 500

    def test_all_major_commands_documented(self):
        essential_commands = [
            "new_tab",
            "navigate",
            "list_tabs",
            "find_tab",
            "close_tab",
            "click",
            "click_text",
            "hover",
            "double_click",
            "right_click",
            "type",
            "press_key",
            "scroll",
            "select_option",
            "get_content",
            "get_html",
            "screenshot",
            "eval",
            "wait",
            "wait_for_element",
            "handle_dialog",
            "get_cookies",
            "get_storage",
            "ping",
            "version",
            "serve",
        ]
        for cmd in essential_commands:
            assert cmd in cli.HELP_TEXT, f"Command '{cmd}' missing from help text"


class TestMain:
    """CLI entry point."""

    def test_no_args_prints_help(self, capsys):
        original_argv = sys.argv
        sys.argv = ["cli.py"]
        try:
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 0
        finally:
            sys.argv = original_argv

        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert "Tab Management" in captured.out
