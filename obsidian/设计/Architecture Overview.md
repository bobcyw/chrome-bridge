---
tags: [design, architecture]
---

# Architecture Overview

## High-Level

```
┌──────────────┐     HTTP POST      ┌──────────────┐     WebSocket      ┌───────────┐
│  CLI / API   │ ──────────────────▶│  server.py   │ ──────────────────▶│ Extension │
│  (短命进程)   │ ◀──────────────────│  (常驻进程)   │ ◀──────────────────│ (常驻)     │
└──────────────┘     JSON response  └──────────────┘     JSON message   └───────────┘
      :19877                              :19877 + :19876                    :19876
```

## Components

### 1. Chrome Extension (`extension/`)
- **Type**: Manifest V3 Service Worker
- **Role**: Executes browser commands via Chrome APIs
- **Key files**: `background.js` (command handler), `manifest.json`, `csp-bypass.js`
- **Connection**: Persistent WebSocket to server on `:19876`
- **Commands**: `new_tab`, `click`, `type`, `screenshot`, `eval`, etc. (32 total)
- **Special**: CSP bypass via CDP `Page.setBypassCSP`, trusted typing via `Input.insertText`

### 2. Bridge Server (`bridge/server.py`)
- **Type**: Python asyncio + threading
- **Role**: Protocol relay — HTTP ↔ WebSocket
- **Ports**:
  - `:19876` — WebSocket server (Extension connects here)
  - `:19877` — HTTP server (CLI sends commands here)
- **Thread model**:
  - Main thread: asyncio event loop (WebSocket)
  - Daemon thread: `http.server.HTTPServer`
  - Cross-thread sync: `threading.Lock` + `threading.Event` + `asyncio.run_coroutine_threadsafe()`
- **Flow**:
  1. HTTP POST `/cmd` arrives
  2. Command forwarded via WebSocket to Extension
  3. `threading.Event` blocks HTTP thread
  4. Extension response sets `Event`, wakes HTTP thread
  5. JSON response returned to CLI

### 3. CLI (`bridge/cli.py`)
- **Type**: Short-lived Python process
- **Role**: Send command, print result
- **Protocol**: HTTP POST to `127.0.0.1:19877/cmd`
- **Args**: `key=value` pairs, parsed into typed kwargs
- **Built-in subcommands**: `serve` (foreground), `serve --background` (daemon)

### 4. Python API (`bridge/api.py`)
- **Type**: Python library
- **Role**: High-level `Browser` class wrapping CLI calls
- **Model**: Each method calls `_run()` which spawns `bridge/cli.py` as subprocess
- **Usage**: `from bridge import Browser`

## Data Flow

```
b.open("https://example.com")
  → Browser.open() calls _run("new_tab", url="...")
    → _run() spawns: python bridge/cli.py new_tab url=https://example.com
      → cli.py: urllib POST {"cmd":"new_tab","args":{"url":"..."}}
        → server.py HTTP handler: forward via WS to extension
          → extension background.js: chrome.tabs.create({url})
            → extension response via WS: {"ok":true, "tabId":42}
          → server sets threading.Event
        → HTTP response: {"ok":true, "tabId":42}
      → cli.py stdout: {"ok":true, "tabId":42}
    → _run() returns parsed dict
  → Browser.open() returns {"tabId":42}
```

## Design Principles

1. **Zero extra dependencies** — everything beyond `websockets` uses stdlib
2. **Real browser, no detection** — extension runs in user's Chrome, not a headless copy
3. **Serial by design** — one command at a time (simplifies state, avoids race conditions)
4. **Localhost only** — all ports bind to `127.0.0.1`, never exposed to network
5. **Stateless CLI** — CLI has no memory between invocations; tab tracking is caller's responsibility

## Related

- [[ADR - HTTP over File IPC]] — why HTTP instead of file polling
- [[Port Allocation]] — why 19876/19877
- [[E-commerce Code Removal]] — what was stripped
- [[../问题/Known Issues]] — current limitations
