---
tags: [dashboard]
created: 2026-07-17
---

# Chrome Bridge — Project Dashboard

## Current Status

- **Version**: 4.0.0
- **Git**: `master` — 9 commits, clean history
- **Tests**: 89 passing, GitHub Actions CI (3 OS × 4 Python)
- **Release readiness**: See [[发布/Release v4.0 Checklist]]

## Directory

```
obsidian/
├── Home.md                          ← 你在这里
├── Roadmap.md                       ← 未来规划
├── 发布/                            ← 版本发布跟踪
│   ├── Release v4.0 Checklist.md
│   ├── GitHub Setup.md
│   └── Changelog.md
├── 体验/                            ← 用户视角
│   ├── User Journey.md
│   ├── Platform Support.md
│   └── Claude Code Integration.md
├── 设计/                            ← 技术决策
│   ├── Architecture Overview.md
│   ├── ADR - HTTP over File IPC.md
│   ├── Port Allocation.md
│   └── E-commerce Code Removal.md
└── 问题/                            ← 缺陷跟踪
    └── Known Issues.md
```

## Quick Links

### 发布
- [[发布/Release v4.0 Checklist]] — launch checklist
- [[发布/GitHub Setup]] — before going public
- [[发布/Changelog]] — version history

### 用户体验
- [[体验/User Journey]] — end-to-end user flow
- [[体验/Platform Support]] — Windows/macOS/Linux details
- [[体验/Claude Code Integration]] — AI agent experience

### 设计
- [[设计/Architecture Overview]] — high-level design
- [[设计/ADR - HTTP over File IPC]] — why HTTP instead of file polling
- [[设计/Port Allocation]] — why 19876/19877
- [[设计/E-commerce Code Removal]] — what was stripped

### 问题
- [[问题/Known Issues]] — active bugs and resolved items

### 规划
- [[Roadmap]] — v4.0 → v5.0
