---
tags: [dashboard]
created: 2026-07-17
---

# Chrome Bridge — Project Dashboard

## Current Status

- **Version**: 4.0.0
- **Git**: `master` — 4 commits, clean history
- **Tests**: 89 passing, GitHub Actions CI (3 OS × 4 Python)
- **Release readiness**: See [[Release v4.0]]

## Quick Links

- [[Release v4.0]] — launch checklist
- [[Roadmap]] — what's next
- [[Changelog]] — version history
- [[Known Issues]] — bugs and limitations
- [[GitHub Setup]] — before going public

## Architecture Snapshot

```
CLI / Python API ──HTTP :19877──▶ server.py ──WebSocket :19876──▶ Chrome Extension ──▶ Browser
```

32 commands | 3 platforms | 0 extra dependencies

## Key Decisions Log

- [[Port Allocation]] — why 19876/19877 vs 9876/9877
- [[Architecture Decision - HTTP over File IPC]] — why Plan B
- [[E-commerce Code Removal]] — what was stripped before going open source
