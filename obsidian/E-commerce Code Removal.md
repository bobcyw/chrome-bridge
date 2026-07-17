---
tags: [decision, security]
date: 2026-07-17
---

# E-commerce Code Removal

## What Was Removed

7 command handlers from `extension/background.js`:

| Handler | What it did |
|---------|-------------|
| `handleInjectHook` | Intercepted `queryCrossList` API calls to `__dld_hook__` |
| `handleReadHook` | Read captured `__dld_hook__` / `__dld_response__` |
| `handlePageSearch` | Called `api.dianleida.net/dld/api/selectAnalysis/queryCrossList` |
| `handleDomSearch` | Manipulated dianleida page DOM (模糊匹配, 开始查询) |
| `handleReadStore` | Read Nuxt/Vuex store for `offerTitle`/`offerId` |
| `handleGetLinks` | Extracted `1688.com/offer/*.html` links |
| `handleScrollTrusted` | Targeted `.ver-scroll-wrap` (dianleida CSS class) |

## Also Scanned and Cleaned

- `bridge/api.py:8` — docstring example changed from `taobao.com` to `example.com`
- `docs/SKILL.md` — removed "1688 product links" documentation
- All `dianleida` / `queryCrossList` / `offerTitle` / `offerId` / `1688` references

## Verification

```bash
grep -ri "taobao\|淘宝\|tmall\|天猫\|1688\|dianleida\|电雷达\|offerTitle\|queryCrossList" .
# → No matches (confirmed clean)
```

## Git History

Original commit `eaa0a0c` (containing e-commerce code) was destroyed. Current repo starts fresh at `69222f6` — clean initial commit.
