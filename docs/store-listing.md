# Chrome Web Store Listing

## Short Description (≤ 132 characters)

```
Let AI coding agents (Claude Code, Cursor, Copilot) control your real Chrome browser. No headless mode, no detection, keeps all logins.
```

## Detailed Description (English)

```
Chrome Bridge connects AI coding assistants to your real Chrome browser via a local WebSocket server. Unlike Playwright or Puppeteer, websites see your actual browser — no automation detection, no CAPTCHA issues, and all your login sessions, cookies, and extensions remain intact.

━━━━━━━━━━━━━━━━━━━━━━━━
HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━

1. Install the Chrome Bridge Python package: pip install chrome-bridge
2. Load this extension in Chrome (Developer mode → Load unpacked)
3. Start the bridge server: bash scripts/start_bridge.sh
4. Your AI agent can now control Chrome via CLI or Python API

━━━━━━━━━━━━━━━━━━━━━━━━
WHAT AI AGENTS CAN DO
━━━━━━━━━━━━━━━━━━━━━━━━

Tab Management
  • Open, close, navigate, search tabs by keyword
  • Switch between tabs, go back/forward, reload

Page Interaction
  • Click elements (by CSS selector or visible text)
  • Type into input fields (including trusted CDP typing)
  • Double-click, right-click, hover
  • Press keyboard keys with modifier support
  • Scroll pages, select dropdown options

Content Extraction
  • Get visible page text or full HTML source
  • Take screenshots (real captureVisibleTab)
  • Execute JavaScript in page context
  • Read element attributes and properties
  • Get images with lazy-load polling

Cookies & Storage
  • Read/write browser cookies
  • Access localStorage/sessionStorage

File Upload
  • Intercept file chooser dialogs and inject files

Network
  • Make fetch requests from within the page context
  • Inject XHR/fetch interceptors to capture API calls

Dialog Handling
  • Handle alert/confirm/prompt dialogs automatically

━━━━━━━━━━━━━━━━━━━━━━━━
WHY NOT PLAYWRIGHT / PUPPETEER?
━━━━━━━━━━━━━━━━━━━━━━━━

• No automation detection — uses your real Chrome
• All logins preserved — no need to re-authenticate
• Real browser fingerprint — passes anti-bot checks
• Zero configuration for authenticated sites
• Works with sites that block headless browsers

━━━━━━━━━━━━━━━━━━━━━━━━
PRIVACY & SECURITY
━━━━━━━━━━━━━━━━━━━━━━━━

• 100% local — all communication stays on 127.0.0.1
• No telemetry, no analytics, no third-party services
• No data collection of any kind
• WebSocket connection never leaves your machine
• Open source (Apache 2.0) — audit the code yourself

━━━━━━━━━━━━━━━━━━━━━━━━
GETTING STARTED
━━━━━━━━━━━━━━━━━━━━━━━━

Full documentation and source code:
https://github.com/bobcyw/chrome-bridge

Python package:
pip install chrome-bridge
```

## 中文短描述

```
让 AI 编程助手（Claude Code、Cursor 等）操控你的真实 Chrome 浏览器。无头模式零检测，登录态全部保留。
```

## 中文详细描述

```
Chrome Bridge 通过本地 WebSocket 服务将 AI 编程助手与你的真实 Chrome 浏览器连接起来。与 Playwright/Puppeteer 不同，网站看到的是你的真实浏览器——无自动化检测、无验证码困扰，所有登录态、Cookie 和扩展全部保留。

核心功能：
• 标签页管理：打开、关闭、导航、关键词搜索标签页
• 页面交互：CSS选择器/文字点击、表单输入、键盘模拟、滚动、下拉选择
• 内容获取：页面文本/HTML、真实截图、JavaScript 执行
• Cookie/Storage：读写浏览器 Cookie 和 localStorage/sessionStorage
• 文件上传：拦截文件选择器并注入文件
• 弹窗处理：自动处理 alert/confirm/prompt

完全本地运行，无数据采集，无遥测，开源（Apache 2.0）。
```

## Category

Developer Tools

## Language

English (United States) — primary
Chinese (Simplified) — secondary
