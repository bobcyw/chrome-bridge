---
tags: [release]
version: 4.0.0
target_date:
status: preparing
---

# Release v4.0.0 — First Open Source Release

## Pre-Release Checklist

### Code Quality
- [x] Remove all e-commerce business code → [[../设计/E-commerce Code Removal]]
- [x] Architecture upgrade: file IPC → HTTP API → [[../设计/ADR - HTTP over File IPC]]
- [x] 32 browser commands covering full web automation surface
- [x] 89 tests, GitHub Actions CI matrix
- [x] New ports (19876/19877) to avoid conflict with private version → [[../设计/Port Allocation]]
- [ ] Final code review pass
- [ ] Run linter (black/flake8) across Python code
- [ ] Verify all JS code is clean (no console.log spam)

### Documentation
- [x] README.md — complete rewrite with all commands
- [x] CLAUDE.md — Claude Code auto-integration
- [x] docs/SKILL.md — skill definition
- [x] docs/claude-code-setup.md — setup guide
- [ ] Add code comments / docstrings to any bare functions
- [ ] Write CONTRIBUTING.md
- [ ] Choose and apply LICENSE (MIT already present)

### GitHub
- [ ] → [[GitHub Setup]]
- [ ] Create repo under target org/username
- [ ] Push with clean history (no e-commerce code ever existed)
- [ ] Set up branch protection rules for `main`
- [ ] Enable GitHub Actions
- [ ] Add repo description, topics, website link
- [ ] Create first GitHub Release with release notes

### Distribution
- [ ] Publish to PyPI as `chrome-bridge`
- [ ] Test `pip install chrome-bridge` from scratch
- [ ] Chrome Web Store? (optional — unpacked works for dev tools)
- [ ] Record a 60s demo GIF for README

### Community
- [ ] Write launch blog post / tweet
- [ ] Post on relevant forums (r/programming, Hacker News?)
- [ ] Set up GitHub Discussions?

## Release Notes (draft)

Chrome Bridge v4.0 — Universal browser automation for AI agents.

- **32 commands**: full keyboard/mouse/form/dialog/cookie/file coverage
- **HTTP API architecture**: 5ms latency, zero polling
- **Claude Code native**: drop in and AI can drive your browser
- **Cross-platform**: Windows/macOS/Linux, one-command daemon, systemd/LaunchAgent support
- **Zero extra deps**: Python stdlib + websockets
- **Real Chrome**: no headless, no CDP detection, keeps your logins
