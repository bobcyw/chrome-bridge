---
tags: [changelog]
---

# Changelog

## v4.0.0 (2026-07-17) — First Open Source Release

### Architecture
- **BREAKING**: File IPC replaced with HTTP API (server now dual-protocol: WS :19876 + HTTP :19877)
- Default ports changed to 19876/19877 (avoid conflict with private version)
- `chrome-bridge serve --background` daemon mode on all platforms

### New Features (since v1.0 prototype)
Added 17 new commands: `hover`, `double_click`, `right_click`, `select_option`, `go_back`, `go_forward`, `reload`, `get_html`, `get_attribute`, `wait_for_element`, `handle_dialog`, `get_cookies`, `set_cookie`, `get_storage`, `set_storage`, `serve`, `type_active`

### Upgraded
- `press_key`: 5 keys → 25 keys + modifier support (ctrl/alt/shift/meta)
- `fetch_api`: custom headers, returns status codes + response headers
- `click`: scrolls element into view before clicking

### Cross-Platform
- macOS: LaunchAgent plist for auto-start
- Linux: systemd user unit for auto-start
- Windows: `start_bridge.bat` one-click launcher, fixed `launch_silent.vbs` auto-detect Python
- All shell scripts use Python socket for port detection (no `netstat` dependency)

### Testing
- 89 tests: API, CLI, Server
- GitHub Actions CI: 3 OS × 4 Python versions

### Documentation
- Complete README rewrite: 32-command reference, Python API examples
- CLAUDE.md: auto-loaded Claude Code integration
- Auto-start install guide for all platforms

### Removed
- 7 e-commerce-specific commands (`inject_hook`, `read_hook`, `page_search`, `dom_search`, `read_store`, `get_links`, `scroll_trusted`)
- All `dianleida.net` / `1688.com` / `taobao.com` references
- File watcher polling loop (~80 lines)

## v1.0.0 (earlier) — Internal Prototype

- Basic Chrome Extension + WebSocket server
- File-based IPC
- 15 basic commands
- E-commerce integration code (removed before public release)
