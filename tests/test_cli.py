"""Tests for bridge/cli.py — argument parsing and command dispatch."""

import json
import os
import sys
import time
import threading
import pytest

# Import the module under test
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
        assert isinstance(result["httpOnly"], bool)

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
        """Malformed JSON should be kept as a plain string."""
        result = cli.parse_args(['data={incomplete'])
        assert result == {"data": "{incomplete"}

    def test_multiple_args(self):
        result = cli.parse_args([
            "url=https://example.com",
            "timeout=30",
            "secure=true",
        ])
        assert result == {
            "url": "https://example.com",
            "timeout": 30,
            "secure": True,
        }

    def test_value_containing_equals(self):
        """Value with = should only split on the first =."""
        result = cli.parse_args(["url=https://example.com?a=1&b=2"])
        assert result == {"url": "https://example.com?a=1&b=2"}

    def test_negative_int(self):
        result = cli.parse_args(["delta_y=-500"])
        assert result == {"delta_y": -500}

    def test_zero(self):
        result = cli.parse_args(["index=0"])
        assert result == {"index": 0}


class TestSendCmd:
    """Command dispatch via file IPC."""

    def _patch_paths(self, tmp_path):
        """Override CMD_FILE and RESULT_FILE to use temp directory."""
        cmd_file = tmp_path / ".bridge_cmd.json"
        result_file = tmp_path / ".bridge_result.json"
        self._orig_cmd = cli.CMD_FILE
        self._orig_result = cli.RESULT_FILE
        cli.CMD_FILE = str(cmd_file)
        cli.RESULT_FILE = str(result_file)
        return cmd_file, result_file

    def _restore_paths(self):
        cli.CMD_FILE = self._orig_cmd
        cli.RESULT_FILE = self._orig_result

    def _write_result_after_delay(self, result_file, data, delay=0.05):
        """Write result file after a short delay (simulates server response)."""
        def _write():
            time.sleep(delay)
            result_file.write_text(json.dumps(data))
        t = threading.Thread(target=_write, daemon=True)
        t.start()
        return t

    def test_writes_command_file(self, tmp_path):
        """send_cmd should write cmd_data to the command file and read result."""
        cmd_file, result_file = self._patch_paths(tmp_path)
        try:
            self._write_result_after_delay(result_file, {"ok": True, "pong": True})
            result = cli.send_cmd("ping")
            assert result == {"ok": True, "pong": True}

            # Verify command file content
            cmd_content = json.loads(cmd_file.read_text())
            assert cmd_content["cmd"] == "ping"
            assert cmd_content["args"] == {}
        finally:
            self._restore_paths()

    def test_send_cmd_with_args(self, tmp_path):
        """send_cmd should include kwargs as args."""
        cmd_file, result_file = self._patch_paths(tmp_path)
        try:
            self._write_result_after_delay(result_file, {"ok": True, "tabId": 42})
            result = cli.send_cmd("new_tab", url="https://example.com")
            assert result == {"ok": True, "tabId": 42}

            cmd_content = json.loads(cmd_file.read_text())
            assert cmd_content["cmd"] == "new_tab"
            assert cmd_content["args"] == {"url": "https://example.com"}
        finally:
            self._restore_paths()

    def test_js_file_parameter(self, tmp_path):
        """js_file= should read the file and pass its content as js=."""
        cmd_file, result_file = self._patch_paths(tmp_path)
        js_file = tmp_path / "script.js"
        js_file.write_text("document.title")

        try:
            self._write_result_after_delay(result_file, {"ok": True, "result": "Example"})
            result = cli.send_cmd("eval", js_file=str(js_file))
            assert result == {"ok": True, "result": "Example"}

            cmd_content = json.loads(cmd_file.read_text())
            assert cmd_content["cmd"] == "eval"
            assert cmd_content["args"] == {"js": "document.title"}
            assert "js_file" not in cmd_content["args"]
        finally:
            self._restore_paths()

    def test_command_file_structure(self, tmp_path):
        """Verify command file JSON structure after send_cmd writes it."""
        cmd_file, result_file = self._patch_paths(tmp_path)
        try:
            self._write_result_after_delay(result_file, {"ok": True})
            cli.send_cmd("click", selector=".btn", tab_id=5)

            cmd_content = json.loads(cmd_file.read_text())
            assert cmd_content["cmd"] == "click"
            assert cmd_content["args"]["selector"] == ".btn"
            assert cmd_content["args"]["tab_id"] == 5
        finally:
            self._restore_paths()


class TestHelpText:
    """Help text should document all commands."""

    def test_help_text_not_empty(self):
        assert len(cli.HELP_TEXT) > 500

    def test_all_major_commands_documented(self):
        """Every command in the version list should appear in help text."""
        essential_commands = [
            "new_tab", "navigate", "list_tabs", "find_tab", "close_tab",
            "click", "click_text", "hover", "double_click", "right_click",
            "type", "press_key", "scroll", "select_option",
            "get_content", "get_html", "screenshot", "eval",
            "wait", "wait_for_element", "handle_dialog",
            "get_cookies", "get_storage",
            "ping", "version",
        ]
        for cmd in essential_commands:
            assert cmd in cli.HELP_TEXT, f"Command '{cmd}' missing from help text"


class TestMain:
    """CLI entry point."""

    def test_no_args_prints_help(self, capsys):
        """Running with no arguments should print help and exit 0."""
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
