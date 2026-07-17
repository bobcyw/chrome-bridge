---
tags: [decision, architecture]
date: 2026-07-17
status: implemented
---

# ADR: HTTP API over File IPC

## Context

The original architecture used file-based IPC:
- CLI writes command to `runtime/.bridge_cmd.json`
- Server polls the file every 300ms
- Extension executes and returns via WebSocket
- Server writes result to `runtime/.bridge_result.json`
- CLI polls result file

This had ~300ms latency and complex polling logic.

## Options Considered

### A: Native Messaging
Chrome `connectNative()` — CLI talks to extension via stdin/stdout.
- ❌ 1 MB message limit (screenshots 2-5 MB would fail)
- ❌ Requires system-level manifest registration

### B: HTTP API ✅ (chosen)
CLI → HTTP POST → Server → WebSocket → Extension.
- ✅ No message size limits
- ✅ 5ms latency (vs 300ms)
- ✅ Zero new dependencies (stdlib `http.server` + `urllib`)
- ✅ Architecture simplified (-48 lines net)

### C: Keep file IPC
- ❌ 300ms latency
- ❌ Complex polling code
- ❌ File system dependency

## Implementation

Server runs two protocols in one process:
- `:19877` HTTP API (for CLI) — `http.server` in daemon thread
- `:19876` WebSocket (for extension) — `websockets.serve` in asyncio

Cross-thread sync via `threading.Event` + `asyncio.run_coroutine_threadsafe()`.

## Consequences

- ✅ Latency: 300ms → 5ms
- ✅ Code: -48 lines (deleted file watcher, added HTTP handler)
- ✅ Portability: removed file system dependency for IPC
- ⚠️ New dependency on `asyncio` + threading coordination (stdlib, not a problem)
- ⚠️ HTTP server runs in a daemon thread — killed on main thread exit
