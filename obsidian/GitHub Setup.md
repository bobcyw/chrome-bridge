---
tags: [release, infra]
---

# GitHub Setup — Before Going Public

## Repo Configuration

- [ ] Create repo at `github.com/<user>/chrome-bridge`
- [ ] Push this codebase: `git remote add origin ... && git push -u origin master`
- [ ] Settings → Branches → Add rule for `master`:
  - Require pull request before merging
  - Require status checks to pass (`test` workflow)
  - Require branches to be up to date
- [ ] Settings → Actions → General:
  - Allow all actions
  - Workflow permissions: Read and write

## Repo Metadata

- [ ] Description: "AI-to-Browser bridge — Let AI coding agents control your real Chrome browser"
- [ ] Website: (leave empty or link to docs)
- [ ] Topics: `browser-automation`, `claude-code`, `chrome-extension`, `ai-agents`, `python`, `websocket`, `automation`
- [ ] Social preview image: create a banner

## Security Review

- [ ] No API keys, tokens, or credentials in code
- [ ] No internal URLs (`dianleida.net`, etc.) — confirmed removed
- [ ] Ports are localhost-only (127.0.0.1, not 0.0.0.0)
- [ ] Extension `host_permissions` are scoped appropriately
- [ ] No telemetry, no phone-home code

## README Polish

- [ ] Replace `YOUR_USERNAME` with actual GitHub username
- [ ] Add actual clone URL
- [ ] Add demo GIF/screenshot
- [ ] Test every command example in README works

## Release

- [ ] Tag: `git tag v4.0.0 && git push --tags`
- [ ] Create GitHub Release from tag
- [ ] Release notes from [[Release v4.0]]
- [ ] Attach `extension/` as a zip for manual install
