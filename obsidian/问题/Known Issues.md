---
tags: [bug, tracking]
---

# Known Issues

## Active

### #1 Extension port hardcoded
- **File**: `extension/background.js:5`
- **Issue**: `WS_URL` is hardcoded to `ws://127.0.0.1:19876`. No way to change at runtime.
- **Impact**: Can't use env-based port overrides with the extension
- **Fix**: Pass port via content script message or extension storage

### #2 `serve --background` Windows subprocess
- **File**: `bridge/cli.py` serve handler
- **Issue**: Uses `subprocess.CREATE_NO_WINDOW` which may not exist on all Python/Windows combos
- **Impact**: Potential `AttributeError` on older Python or Wine
- **Fix**: Already guarded with `hasattr`, but should test on more Windows versions

### #3 No concurrent command support
- **Issue**: Architecture is fundamentally serial — one command at a time
- **Impact**: Can't do "scroll while waiting for element" or "type in two fields simultaneously"
- **Workaround**: Use `eval` to batch multiple JS operations
- **Long-term**: v5.0 concurrent tab support

### #4 Screenshot requires active tab
- **Issue**: `chrome.tabs.captureVisibleTab()` only works on the active tab
- **Workaround**: Server auto-activates the target tab, then captures
- **Impact**: Brief visual flicker when screenshooting inactive tabs

### #5 CSP bypass reliability
- **File**: `extension/background.js` CSP section
- **Issue**: Some sites with very strict CSP may still block `eval`
- **Impact**: `eval` command fails silently on those sites
- **Workaround**: Use `get_content` + other commands instead

### #6 No response size limit handling
- **Issue**: If a page returns enormous content, the WebSocket message could theoretically be truncated (max 10MB configured)
- **Impact**: `get_html` on very large pages (>10MB) would fail
- **Fix**: Add chunked transfer for large responses

## Resolved

- [x] ~~File IPC latency~~ → Replaced with HTTP API (v4.0)
- [x] ~~CLI 300ms polling delay~~ → Now ~5ms HTTP roundtrip (v4.0)
- [x] ~~E-commerce code contamination~~ → All stripped (v4.0)
- [x] ~~`netstat` incompatibility on macOS~~ → Python socket port check (v4.0)
- [x] ~~Old git history with e-commerce code~~ → Squashed to clean initial commit (v4.0)
