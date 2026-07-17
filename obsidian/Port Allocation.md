---
tags: [decision, infra]
---

# Port Allocation — Why 19876/19877

## Decision

Open-source version uses:
- **WS** `19876` — Chrome Extension WebSocket
- **HTTP** `19877` — CLI HTTP API

Private "special" version uses:
- **WS** `9876`
- **HTTP** `9877`

## Rationale

- Install both versions on the same machine without port conflicts
- Environment variable overrides (`CHROME_BRIDGE_WS_PORT`, `CHROME_BRIDGE_HTTP_PORT`) allow custom ports
- Extension `WS_URL` is the one piece NOT configurable via env (hardcoded in `background.js`)
  - Users needing custom WS ports must edit the extension source
  - See [[Known Issues#1]]

## Port Selection

Chose `19876` because:
- Near enough to `9876` to be memorable (prefix with `1`)
- Not in IANA well-known port range (0-1023)
- Not in common ephemeral port range (32768-60999 on Linux)
- Not conflicting with common dev tools:
  - 3000-3010: React/Next.js
  - 5000: Flask
  - 8000: Django
  - 8080: various
  - 8888: Jupyter
  - 9876: private version
