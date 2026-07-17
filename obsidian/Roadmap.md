---
tags: [planning]
---

# Roadmap

## v4.0.x — Polish

- [ ] Add `CHROME_BRIDGE_WS_PORT` support to the Chrome Extension (currently hardcoded)
- [ ] Better error messages: include troubleshooting hints in JSON responses
- [ ] Support `file_chooser_intercept` without requiring the click target (just intercept next dialog)
- [ ] Add `fetch_api` response header passthrough to CLI output
- [ ] Performance: reduce `wait_for_element` polling overhead with MutationObserver

## v4.1 — Quality of Life

- [ ] `Browser` context manager (`with Browser() as b: ...`)
- [ ] `browser.wait_for_navigation()` — detect page transitions after click
- [ ] `browser.get_network_requests()` — capture XHR/fetch traffic
- [ ] `browser.emulate_device(viewport, user_agent)` — mobile emulation
- [ ] `browser.download_file(url, path)` — trigger + intercept download
- [ ] Session recording: save + replay browser interactions
- [ ] Screenshot: support element-level screenshots (not just full page)

## v4.2 — Ecosystem

- [ ] Playwright-compatible API adapter (`browser = chrome_bridge.Browser(); browser.new_page()`)
- [ ] MCP server mode: expose as MCP tools for any MCP-compatible client
- [ ] VSCode extension: browser panel inside the editor
- [ ] Docker support (headful Chrome in container + extension)

## v5.0 — Multi-Browser

- [ ] Firefox extension (WebExtensions API compatible)
- [ ] Edge support (mostly works via Chrome Web Store?)
- [ ] Browser-agnostic protocol abstraction

## Ideas (Unscheduled)

- [ ] Remote browser: control a browser on another machine
- [ ] Concurrent tab operations (currently serial only)
- [ ] Visual element picker (click in browser → returns selector)
- [ ] Natural language to selector: "the blue login button" → CSS selector
- [ ] WebSocket API for non-Python clients (Go, Rust, Node SDKs)
