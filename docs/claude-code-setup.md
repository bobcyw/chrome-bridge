# Claude Code Setup

Chrome Bridge integrates with Claude Code automatically via `CLAUDE.md`.

## Automatic (Recommended)

Just open the Chrome Bridge project in Claude Code. The `CLAUDE.md` file at the repo root is loaded automatically and gives Claude everything it needs to control your browser.

```bash
cd ~/chrome-bridge
claude
```

Now ask Claude in natural language:
- "Open example.com and tell me what's on the page"
- "Log in to GitHub with username X and password Y"
- "Search for 'python' on Google and give me the top 5 results"

## Manual Skill Installation (optional)

If you want the skill available globally across all projects:

```bash
mkdir -p ~/.claude/skills/chrome-bridge
cp ~/chrome-bridge/docs/SKILL.md ~/.claude/skills/chrome-bridge/SKILL.md
```

Or for a single project:

```bash
mkdir -p .claude/skills/chrome-bridge
cp ~/chrome-bridge/docs/SKILL.md .claude/skills/chrome-bridge/SKILL.md
```

## Prerequisites

Before Claude can control the browser:

```bash
# 1. Start the bridge server
cd ~/chrome-bridge
python bridge/cli.py serve &

# 2. Verify it's running
python bridge/cli.py ping
# → {"ok": true, "pong": true}
```

Make sure the Chrome Extension is loaded and connected.

## Configuration

If you installed Chrome Bridge in a non-default location, edit `CLAUDE.md` and update the paths from `python bridge/cli.py` to the full path.

## Troubleshooting

**Skill not appearing:** Restart Claude Code after creating the skill file.

**"No Chrome extension connected":** Click the Chrome Bridge icon in the Chrome toolbar, then retry.

**Server not running:** Run `python bridge/cli.py serve` before using the skill.
