# Privacy Policy — Chrome Bridge Extension

**Last updated**: 2026-07-17

## Data Collection

Chrome Bridge does **not** collect, transmit, or store any user data. All browser commands are sent exclusively to `127.0.0.1` (localhost) — no data ever leaves your machine.

## Permissions Explanation

| Permission | Why It's Needed |
|-----------|----------------|
| `tabs` | Open, close, navigate, and list browser tabs |
| `scripting` | Execute click/type/scroll/content-extraction commands in web pages |
| `debugger` | CSP bypass for JavaScript execution, trusted typing via CDP, file chooser interception, dialog handling |
| `webNavigation` | Monitor page load completion for `navigate` command |
| `cookies` | Read/write browser cookies via `get_cookies`/`set_cookie` |
| `alarms` | Keepalive timer to prevent service worker suspension |
| `storage` | Local extension state management |
| `<all_urls>` | Content script injection for CSP bypass on all pages |
| `127.0.0.1` access | WebSocket connection to local bridge server |

## Data Transmission

The extension communicates exclusively over WebSocket to `ws://127.0.0.1:19876`. This connection never leaves the local machine. No analytics, telemetry, or third-party services are used.

## Third-Party Services

None. This extension operates entirely locally.

## Contact

For privacy concerns, open an issue at https://github.com/bobcyw/chrome-bridge/issues
