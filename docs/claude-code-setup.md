# Claude Code Setup

This guide explains how to integrate Chrome Bridge with Claude Code.

## Step 1: Install Chrome Bridge

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/chrome-bridge.git ~/chrome-bridge

# Install dependencies
cd ~/chrome-bridge
pip install -r requirements.txt
```

## Step 2: Load the Extension

1. Open `chrome://extensions` in Chrome
2. Enable **Developer mode**
3. Click **Load unpacked** → select `~/chrome-bridge/extension/`
4. Click the Chrome Bridge icon in the toolbar

## Step 3: Start the Bridge Server

```bash
bash ~/chrome-bridge/scripts/start_bridge.sh
```

## Step 4: Install the Skill

Copy the skill definition into your project's `.claude/skills/` directory:

```bash
mkdir -p .claude/skills/chrome-bridge
cp ~/chrome-bridge/docs/SKILL.md .claude/skills/chrome-bridge/SKILL.md
```

Or install it globally for all projects:

```bash
mkdir -p ~/.claude/skills/chrome-bridge
cp ~/chrome-bridge/docs/SKILL.md ~/.claude/skills/chrome-bridge/SKILL.md
```

## Step 5: Verify

Open Claude Code and type:

```
open https://www.example.com and tell me the page title
```

Claude should use the `chrome-bridge` skill automatically.

## Configuration

If you installed Chrome Bridge in a non-default location, edit `SKILL.md` and update the paths:

```bash
# Find/replace in SKILL.md:
~/chrome-bridge/  →  /your/actual/path/to/chrome-bridge/
```

## Troubleshooting

**Skill not appearing:** Restart Claude Code after creating the skill file.

**"No Chrome extension connected":** Click the Chrome Bridge icon in the Chrome toolbar, then retry.

**Server not running:** Run `bash ~/chrome-bridge/scripts/start_bridge.sh` before using the skill.
