# Session K Summary — 2026-09-19

**Purpose:** Record of all fixes completed in Session K (bug cleanup pass).
**HEAD at end:** `baf0a10 docs: mark K/8 (read includes replied) as fixed`
**Version:** `v3.1-security-K123-plus-K4-K8-20260919`

---
## Items Closed — 8 of 8 (security + data integrity)

### Security (3/3)

| # | Item | Commit | Verification |
|---|---|---|---|
| K/1 | Require auth on /api/exam/{progress,history,study-plan} | `e5c3c65` | Prod-verified: 401 on all no-auth scenarios |
| K/2 | Trim /api/payment/status to booleans | `910e044` | Prod-verified: no leaked key_ids/mode |
| K/3 | Require admin on /api/roles/custom | `7edadd9` | Prod-verified: anonymous POST returns 401 |

### Data integrity (5/5)

| # | Item | Commit | Verification |
|---|---|---|---|
| K/4 | revenue_engine double-count on tier changes | `3517ff9` | Local: counter consistent |
| K/5 | resume_engine sub-vendor counter on duplicates | `7052233` | Local: 3 dups -> counter stays 1 |
| K/6 | charvak_vms.approve_timecard idempotency | `f341535` | Local: 3 approvals -> history stays 1 |
| K/7 | outreach_engine UNIQUE on email | `e2a9c2c` | Local + prod indexes live |
| K/8 | messaging unread/read invariant | `22a9a5a` | Local: read + unread = total |

---
## Production Migration Applied

**K/7 migration** `migrations/20260919_outreach_unique_email.sql`:

- Applied to prod 2026-09-19 via Render Shell
- Output: `DELETE 0, DELETE 0, CREATE INDEX, CREATE INDEX`
- Verified: both UNIQUE indexes present in prod:
  - `uq_outreach_email_syncs_email`
  - `uq_outreach_premium_users_email`

---

## What's Left From K Session

- **Formal deferrals (4):** #11-14 — next up
- **Dead fields (16):** #24-39
- **Feature gaps (5):** #40-44
- **Cosmetic/a11y (5):** #45-49
- **Housekeeping (9):** #50-58

---

## Process Notes Learned

1. PowerShell here-string patch scripts with nested quotes are unreliable — use `[System.IO.File]::WriteAllText` + `ReadAllText` + `.Replace`.
2. Always use `git --no-pager diff` — bare `git diff` opens a pager that looks hung.
3. Prod URL is `https://www.charvakit.com` (bare domain SSL issue filed as #85).
4. Render Shell available for prod DB migrations: `psql $DATABASE_URL -f migrations/*.sql`.

---

## Next Sessions

1. Formal deferrals writeup — 30 min
2. B-2: voice_to_web_engine persistence — ~1 hr
3. Session I: capstone + tag + backup — ~1-2 hr

**Status: Session K security + data integrity complete.**