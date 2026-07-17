---
tags: [ux, platform]
---

# Platform Support

## Current Status

| | Windows | macOS | Linux |
|---|---------|-------|-------|
| Python serve | ✅ | ✅ | ✅ |
| serve --background | ✅ `CREATE_NO_WINDOW` | ✅ double-fork | ✅ double-fork |
| start_bridge.sh | ⚠️ needs Git Bash | ✅ native | ✅ native |
| start_bridge.bat | ✅ native | ❌ N/A | ❌ N/A |
| Auto-start | ✅ Startup folder | ✅ LaunchAgent | ✅ systemd user |
| Port check | ✅ Python socket | ✅ Python socket | ✅ Python socket |

## Platform Quirks

### Windows
- `netstat -ano` works in Git Bash and cmd
- `taskkill //PID` for killing processes
- `start /B` for background in .bat
- VBS `WshShell.Run cmd, 0, False` for silent launch
- Startup folder: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- `pip install -e .` registers `chrome-bridge.exe` in `Scripts\`

### macOS
- `python3` is the default (not `python`). Scripts try `python3` first, fall back to `python`.
- `launchctl` for LaunchAgent management
- `~/Library/LaunchAgents/` for user agents
- `netstat` has different flags than Linux/Windows → scripts use Python socket instead
- `lsof -i :19876` is an alternative
- No `nohup` needed — LaunchAgent handles daemonizing

### Linux
- `systemctl --user` for user-level systemd units
- `loginctl enable-linger` required for user units to start at boot
- `~/.config/systemd/user/` for unit files
- `ss -tlnp` is preferred over `netstat` (deprecated) → scripts use Python socket
- `python3` is the default on most distros

## Shared

All platforms use **Python socket** for port detection in scripts. This was a deliberate choice to avoid platform-specific netstat/ss/lsof commands. One Python one-liner works everywhere.

```bash
python -c "import socket; s=socket.socket(); s.settimeout(0.3)
try: s.connect(('127.0.0.1', 19877)); exit(0)
except: exit(1)"
```

## Gaps

- [ ] Chrome Extension port (19876) is hardcoded in `background.js` — can't use env overrides
- [ ] No auto-start for Chrome Extension itself (Chrome limitation)
- [ ] Firefox not supported (uses WebExtensions but different APIs for some features)
- [ ] No Docker/devcontainer setup for reproducible dev environment

## Related

- [[User Journey]] — end-to-end flow
- [[../设计/Port Allocation]] — why these port numbers
- [[../问题/Known Issues#1]] — extension port hardcoded
