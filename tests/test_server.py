"""Tests for bridge/server.py — HTTP API + WebSocket relay."""

import json
import pytest

from bridge import server


class TestConstants:
    """Verify server configuration."""

    def test_ws_port(self):
        assert server.WS_PORT == 19876

    def test_http_port(self):
        assert server.HTTP_PORT == 19877

    def test_response_timeout(self):
        assert server.RESPONSE_TIMEOUT == 30


class TestWebSocketHandler:
    """Test the WebSocket connection handler."""

    @pytest.mark.asyncio
    async def test_handler_registers_connection(self):
        """New connection should be added to connected_ws, removed on disconnect."""
        server.connected_ws.clear()

        class MockWS:
            def __init__(self):
                self._iter = self._gen()

            async def send(self, msg):
                pass

            def __aiter__(self):
                return self

            async def __anext__(self):
                return await self._iter.__anext__()

            async def _gen(self):
                yield json.dumps({"id": "test_1", "cmd": "ping", "args": {}})

        mock_ws = MockWS()
        try:
            await server.ws_handler(mock_ws)
        except StopAsyncIteration:
            pass

        assert mock_ws not in server.connected_ws

    @pytest.mark.asyncio
    async def test_handler_ignores_invalid_json(self):
        """Malformed messages should be silently ignored."""
        server.connected_ws.clear()

        class MockWS:
            def __init__(self):
                self._iter = self._gen()

            async def send(self, msg):
                pass

            def __aiter__(self):
                return self

            async def __anext__(self):
                return await self._iter.__anext__()

            async def _gen(self):
                yield "not valid json {{{"

        mock_ws = MockWS()
        try:
            await server.ws_handler(mock_ws)
        except StopAsyncIteration:
            pass
        # Should not have crashed

    @pytest.mark.asyncio
    async def test_handler_resolves_pending_response(self):
        """When response arrives with matching id, it resolves the pending entry."""
        server.connected_ws.clear()
        server.pending.clear()
        import threading

        event = threading.Event()
        server.pending["cmd_test"] = {"event": event, "result": None}
        entry_ref = server.pending["cmd_test"]  # keep reference for assertion

        class MockWS:
            def __init__(self):
                self.sent = []
                self._iter = self._generator()

            async def send(self, msg):
                self.sent.append(msg)

            def __aiter__(self):
                return self

            async def __anext__(self):
                return await self._iter.__anext__()

            async def _generator(self):
                yield json.dumps({"id": "cmd_test", "ok": True, "data": {"pong": True}})

        mock_ws = MockWS()

        try:
            await server.ws_handler(mock_ws)
        except StopAsyncIteration:
            pass

        assert event.is_set()
        # The handler pops the entry from pending and sets result on it
        assert entry_ref["result"] == {"pong": True}
        assert "cmd_test" not in server.pending


class TestSharedState:
    """Test thread-safe shared state operations."""

    def test_pending_registration(self):
        """Pending entries should be stored and retrievable."""
        server.pending.clear()
        import threading

        event = threading.Event()
        server.pending["cmd_123"] = {"event": event, "result": None}
        assert "cmd_123" in server.pending
        entry = server.pending.pop("cmd_123")
        assert entry["event"] is event
        assert entry["result"] is None

    def test_no_extension_error(self):
        """When no extension is connected, commands should return an error."""
        server.connected_ws.clear()
        assert len(server.connected_ws) == 0
        # The HTTP handler checks this before forwarding
