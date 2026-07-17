# Contributing to Chrome Bridge

Thanks for your interest! Here's how to contribute.

## Setup

```bash
git clone https://github.com/bobcyw/chrome-bridge.git
cd chrome-bridge
pip install -e ".[test]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

Tests run automatically on push/PR via GitHub Actions (3 OS × 4 Python versions).

## Code Style

```bash
pip install black flake8
black bridge/ tests/
flake8 bridge/ tests/ --max-line-length=100 --extend-ignore=E501,W503
```

- **Python**: black for formatting, flake8 for linting
- **JavaScript**: Keep consistent with `extension/background.js` style (2-space indent, single quotes)

## Project Structure

```
bridge/         Python package (CLI + server + API)
extension/      Chrome Extension (background.js + manifest)
tests/          pytest test suite
docs/           Integration docs (Claude Code setup, skill definition)
scripts/        Platform launchers
```

## Architecture

- `bridge/cli.py` sends HTTP POST to `bridge/server.py` (port 19877)
- `bridge/server.py` relays commands via WebSocket to Chrome Extension (port 19876)
- Extension executes commands via Chrome APIs

See `notes/设计/Architecture Overview.md` for full details (local Obsidian vault).

## Adding a New Command

1. Add handler function to `extension/background.js`
2. Add `case` in the command switch
3. Add CLI help text in `bridge/cli.py`
4. Add Python API method in `bridge/api.py`
5. Add test in `tests/test_api.py`

## Pull Requests

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Ensure tests pass: `python -m pytest tests/ -v`
5. Ensure linting passes: `flake8 bridge/ tests/`
6. Open a PR against `main`

## Questions?

Open an issue or start a discussion.
