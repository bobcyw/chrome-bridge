---
tags: [ux, onboarding]
---

# User Journey

## Complete Flow

```
安装 → 启动服务器 → 加载扩展 → 验证 → 使用
 30s     5s          60s        2s      ∞
```

### Step 1: 安装 (30s)

```bash
git clone ... && cd chrome-bridge && pip install -e .
```

**Friction**: User must know `pip install -e .` (editable install). `pip install -r requirements.txt` alone won't register the `chrome-bridge` command.

**Ideal state**: `pip install chrome-bridge` from PyPI.

### Step 2: 启动服务器 (5s)

```bash
chrome-bridge serve --background
```

Or:
- Windows: double-click `start_bridge.bat`
- macOS/Linux: `bash scripts/start_bridge.sh -b`
- Auto-start: `bash scripts/install_service.sh`

**Friction**: User opens terminal, runs command, terminal can be closed. Works. The `--background` flag was added specifically to avoid "stuck terminal" complaints.

**Edge case**: If ports are occupied, user sees "Port already in use" — must kill existing process or change ports via env vars. Not obvious.

### Step 3: 加载扩展 (60s, one-time)

1. Open `chrome://extensions`
2. Enable Developer mode
3. Load unpacked → select `extension/`
4. Click Chrome Bridge icon to activate

**Friction**: Step 4 is critical and easy to miss. If skipped, `ping` returns "No extension connected" which is confusing if user thinks they already loaded it.

**Improvement idea**: Extension could auto-activate on install via `chrome.runtime.onInstalled`.

### Step 4: 验证 (2s)

```bash
chrome-bridge ping
# → {"ok": true, "pong": true}
```

**Friction**: If it fails, error messages guide user. This step is clear.

### Step 5: 使用

Three modes:

| Mode | Command | Audience |
|------|---------|----------|
| CLI | `chrome-bridge new_tab url=...` | Terminal users |
| Python | `from bridge import Browser; b = Browser()` | Devs scripting automation |
| Claude Code | "Open example.com" (via CLAUDE.md) | AI-assisted |

## Decision Points

### Why the user stays
- Real browser = no bot detection
- Keeps their logins
- Simple CLI, no config files

### Why the user leaves
- "It's too complicated" → 3 moving parts (extension + server + CLI)
- "Chrome only?" → Firefox/Edge users can't use it
- "pip install doesn't work" → Needs setup
- Extension needs manual loading → Can't be fully automated

## Friction Scorecard

| Step | Friction | Status |
|------|----------|--------|
| Install | 🟡 pip install -e . not obvious | Acceptable for now; PyPI later |
| Start server | 🟢 one command, works | Done |
| Load extension | 🔴 manual, easy to miss activation | Chrome limitation; doc warns about it |
| Verify | 🟢 clear error messages | Done |
| Use (CLI) | 🟢 simple key=value | Done |
| Use (Claude) | 🟢 automatic via CLAUDE.md | Done |

## Related

- [[Platform Support]] — per-OS details
- [[Claude Code Integration]] — AI agent experience
- [[../发布/Release v4.0 Checklist]] — what's blocking launch
