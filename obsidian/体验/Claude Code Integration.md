---
tags: [ux, claude-code, ai]
---

# Claude Code Integration

## How It Works

1. User opens Chrome Bridge project in Claude Code
2. Claude reads `CLAUDE.md` automatically (project-level instructions)
3. CLAUDE.md tells Claude: "Use `python bridge/cli.py <cmd>` to control the browser"
4. Claude calls the CLI as a subprocess, parses JSON output, acts on results

## Files Involved

| File | Role |
|------|------|
| `CLAUDE.md` | Auto-loaded instructions — Claude's "browser manual" |
| `docs/SKILL.md` | Optional: install as global skill for cross-project use |
| `docs/claude-code-setup.md` | Human-readable setup guide |

## What Claude Can Do

Claude has access to all 32 commands through the CLI. It can:

1. **Open and navigate**: `new_tab url=...`, `navigate`, `go_back`, `reload`
2. **Interact**: `click`, `click_text`, `hover`, `double_click`, `right_click`
3. **Fill forms**: `type`, `type_trusted`, `select_option`, `press_key`
4. **Extract**: `get_content`, `get_html`, `get_attribute`, `screenshot`
5. **Handle dialogs**: `handle_dialog action=accept\|dismiss`
6. **Read storage**: `get_cookies`, `get_storage`
7. **Upload files**: `file_chooser_intercept`

## Prompt Patterns

User says:
> "Open GitHub and find the most starred Python browser automation project"

Claude executes:
```bash
python bridge/cli.py new_tab url=https://github.com/search?q=browser+automation+python&type=repositories
python bridge/cli.py wait ms=3000
python bridge/cli.py get_content  # reads results
# → parses stars, navigates to top result, extracts readme
```

## Design Decisions

- **CLI over Python API**: CLAUDE.md uses CLI commands (not `from bridge import Browser`) because:
  - CLI is simpler for step-by-step AI reasoning
  - Each step is atomic and verifiable
  - Subprocess output = JSON = structured data
- **No concurrency**: Commands are serial. Claude must wait for each result before sending next command. This maps naturally to AI reasoning loops.
- **Error handling**: CLAUDE.md teaches Claude to check `"pong": true` before operating, and to interpret error messages like "No extension connected"

## Improvement Ideas

- [ ] MCP server mode: expose as MCP tools, any MCP client can use it (not just Claude Code)
- [ ] Screenshot + vision: combine screenshot with VL model for visual understanding
- [ ] Natural language selectors: "the blue login button" → CSS selector (needs vision model)
- [ ] Pre-built Claude Code "recipes" for common tasks (login, search, fill form, extract table)

## Related

- [[User Journey]] — step 5: using via Claude Code
- [[../设计/Architecture Overview]] — how commands flow
