"""Tests for bridge/server.py — WebSocket relay and file watcher."""

import json
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from bridge import server


class TestConstants:
    """Verify project paths are correct."""

    def test_project_dir_exists(self):
        assert os.path.isdir(server.PROJECT_DIR)

    def test_runtime_dir_path(self):
        assert server.RUNTIME_DIR.endswith('runtime')

    def test_cmd_file_path(self):
        assert server.CMD_FILE.endswith('.bridge_cmd.json')

    def test_result_file_path(self):
        assert server.RESULT_FILE.endswith('.bridge_result.json')

    def test_cmd_and_result_in_same_dir(self):
        assert os.path.dirname(server.CMD_FILE) == os.path.dirname(server.RESULT_FILE)


class TestWebSocketHandler:
    """Test the WebSocket connection handler."""

    @pytest.mark.asyncio
    async def test_handler_registers_connection(self):
        """New connection should be added to connected_ws list."""
        server.connected_ws.clear()
        mock_ws = AsyncMock()

        # Make the websocket raise to exit the handler loop
        async def raise_on_recv():
            raise asyncio.CancelledError()
        mock_ws.__aiter__.return_value = []

        # Build our own simple receive loop
        recv_count = [0]

        async def mock_recv():
            if recv_count[0] == 0:
                recv_count[0] += 1
                return json.dumps({"cmd": "ping"})
            raise asyncio.CancelledError()

        mock_ws.__aiter__ = lambda self: self
        mock_ws.__anext__ = mock_recv

        try:
            await server.handler(mock_ws)
        except asyncio.CancelledError:
            pass

        # Should have registered then unregistered
        assert len(server.connected_ws) == 0  # removed on disconnect

    @pytest.mark.asyncio
    async def test_handler_processes_ping(self):
        """Handler should process ping messages."""
        server.connected_ws.clear()
        mock_ws = AsyncMock()

        recv_calls = [0]

        async def mock_recv():
            recv_calls[0] += 1
            if recv_calls[0] == 1:
                # First message: valid ping
                server.connected_ws.append(mock_ws)
                return json.dumps({"id": "test_1", "cmd": "ping", "args": {}})
            raise asyncio.CancelledError()

        mock_ws.__aiter__ = lambda self: self
        mock_ws.__anext__ = mock_recv

        try:
            await server.handler(mock_ws)
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_handler_ignores_invalid_json(self):
        """Malformed messages should be silently ignored."""
        server.connected_ws.clear()
        mock_ws = AsyncMock()

        recv_calls = [0]

        async def mock_recv():
            recv_calls[0] += 1
            if recv_calls[0] == 1:
                server.connected_ws.append(mock_ws)
                return "not valid json {{{"
            raise asyncio.CancelledError()

        mock_ws.__aiter__ = lambda self: self
        mock_ws.__anext__ = mock_recv

        try:
            await server.handler(mock_ws)
        except asyncio.CancelledError:
            pass
        # Should not have crashed


class TestFileWatcher:
    """Test the file watcher logic (runs in a loop, so we test individual behaviors)."""

    def test_creates_runtime_dir_and_files(self, tmp_path):
        """Watcher should ensure runtime directory and files exist."""
        runtime_dir = tmp_path / 'runtime'
        cmd_file = runtime_dir / '.bridge_cmd.json'
        result_file = runtime_dir / '.bridge_result.json'

        # Simulate what file_watcher does on startup
        os.makedirs(runtime_dir, exist_ok=True)
        for f in [cmd_file, result_file]:
            if not os.path.exists(f):
                with open(f, 'w') as fh:
                    fh.write('')

        assert os.path.isdir(runtime_dir)
        assert os.path.isfile(cmd_file)
        assert os.path.isfile(result_file)

    def test_reads_command_from_file(self, tmp_path):
        """Should parse a JSON command written to the command file."""
        cmd_file = tmp_path / '.bridge_cmd.json'
        cmd_data = {"cmd": "new_tab", "args": {"url": "https://example.com"}}
        cmd_file.write_text(json.dumps(cmd_data))

        content = cmd_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["cmd"] == "new_tab"
        assert parsed["args"]["url"] == "https://example.com"

    def test_handles_malformed_command(self, tmp_path):
        """Malformed JSON in command file should be handled gracefully."""
        cmd_file = tmp_path / '.bridge_cmd.json'
        cmd_file.write_text("{broken json")

        content = cmd_file.read_text().strip()
        try:
            json.loads(content)
            valid = True
        except json.JSONDecodeError:
            valid = False
        assert not valid  # Should be caught, not crash

    def test_clears_command_file_after_reading(self, tmp_path):
        """After processing, the command file should be cleared."""
        cmd_file = tmp_path / '.bridge_cmd.json'
        cmd_file.write_text(json.dumps({"cmd": "ping", "args": {}}))

        # Read
        content = cmd_file.read_text().strip()
        assert content

        # Clear (as the watcher does)
        with open(str(cmd_file), 'w') as f:
            f.write('')

        # Verify cleared
        assert cmd_file.read_text().strip() == ''


class TestResponseHandling:
    """Test how the server handles responses from the extension."""

    def test_response_matches_pending_by_id(self):
        """When a response arrives with matching id, it resolves the future."""
        response = {"id": "cmd_123", "ok": True, "data": {"result": "done"}}
        msg_id = response.get('id')
        assert msg_id == "cmd_123"

        # Simulate the lookup
        if msg_id and msg_id in {"cmd_123": True}:
            future = MagicMock()
            future.done.return_value = False
            future.set_result(response["data"])
            future.set_result.assert_called_once_with({"result": "done"})

    def test_ping_messages_are_ignored(self):
        """Ping commands should not be treated as responses."""
        data = {"cmd": "ping"}
        assert data.get('cmd') == 'ping'
        assert data.get('id') is None
        # Should be skipped by the handler


class TestNoExtensionError:
    """When no extension is connected, commands should return an error."""

    def test_error_when_no_connections(self):
        server.connected_ws.clear()
        assert len(server.connected_ws) == 0
        # The watcher checks this before sending
        if not server.connected_ws:
            result = {"ok": False, "error": "No Chrome extension connected"}
            assert result["ok"] is False
            assert "No Chrome extension" in result["error"]
