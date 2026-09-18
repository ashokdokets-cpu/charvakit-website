# Charvak - SESSION CONTEXT

**Purpose:** One-file resume pointer. Paste this file into a fresh chat to instantly orient.

**Last updated:** 2026-09-19 (end of Session K security + data integrity)
**HEAD at time of writing:** `3805feb docs: add Session K summary`
**Version:** `v3.1-security-K123-plus-K4-K8-20260919`

---

## Where we are

**Persistence project: 49 of 62 engines DB-backed (~79%). 9 verified skip. ~4 remaining.**

| Session | Engines | Status |
|---|---|---|
| A | kyc, candidate, training, lms | [OK] |
| B (partial) | enterprise, ats | [OK] |
| C | events, career_v2, exam_prep | [OK] |
| D | messaging, profile_network, badge, university, brand | [OK] |
| E | final_year_project, student_suite, ai_internship, team | [OK] |
| F | outreach, marketing_ai, exam_analytics, dynamic_role | [OK] |
| G | 6 na_module engines | [OK] |
| H | 8 ephemeral engines | [OK] |
| J | 6 backlog engines (audit gap) | [OK] |
| Tier E | payment fix + 3 verify | [OK] |
| **B-2** | **voice_to_web_engine** | [WAIT] |
| **K** | **bug cleanup (~15 KNOWN-ISSUES items)** | [WAIT] |
| **I** | **capstone + tag + final backup** | [WAIT] |

**Real bugs fixed across project:** ~18 (all 8 known AI JSON bugs resolved; only whatsapp_bot.py remains, external-blocked)

---

## What's in flight

**Nothing.** Working tree clean, all branches merged, prod verified.

---

## Next session recommendations

### Option 1 - Session B-2 (~1 hr)
Persist `voice_to_web_engine.py` (last Tier A engine, 7.5 KB).
- Currently: has in-memory state
- Pattern: same as Sessions A-J
- After B-2: all Tier A engines DB-backed

### Option 2 - Session K (~2-3 hr)
Bug cleanup pass on KNOWN-ISSUES.md. 3 security + 5 data integrity + ~7 misc items.

### Option 3 - Session I (~1 hr)
Capstone: backfill missing migration, doc consolidation, final audit, tag `v3.0-tier3-complete-YYYYMMDD`, final backup.

---

## Reference docs (all in repo root)

| File | Purpose |
|---|---|
| `SESSION-CONTEXT.md` | **this file** - resume pointer |
| `TIER3-PERSISTENCE-PROJECT.md` | sessions A-K + I plan |
| `TODO-MASTER.md` | master backlog, sessions + housekeeping |
| `KNOWN-ISSUES.md` | bug registry (fixed + open, categorized) |
| `MASTER-REFERENCE.md` | system-wide reference |
| `DEV-SETUP.md` | local dev workflow + PowerShell gotchas |

---

## Opener to paste into a fresh chat

Hello - resuming Charvak persistence work. Current HEAD is 056d321, 49/62 engines persisted. See SESSION-CONTEXT.md in the repo for full state. Let's continue with Session [B-2 / K / I].

Or paste this file's content directly.

---

## Prereqs to verify before starting

    Set-Location "C:\projects\charvakit-new"
    .\venv\Scripts\Activate.ps1
    Get-Service postgresql-x64-15     # expect Running
    git status --short                 # expect clean
    git log --oneline -3               # expect HEAD at 056d321
    git fetch origin --prune

If Postgres isn't running: `Start-Service postgresql-x64-15`

---

## Key operational facts

- **Local DB:** `postgresql://postgres:dev@localhost:5432/vouchai`
- **Always set `$env:DATABASE_URL` explicitly** before running smoke tests (`.env` points at prod)
- **Safety gate pattern** in all smoke tests: refuse prod unless `CHARVAK_ALLOW_PROD=1`
- **PowerShell gotchas** (documented in DEV-SETUP.md):
  - `Out-File -Encoding utf8` writes a BOM -> strip bytes 0-2
  - `python -c "..."` with nested quotes -> use temp `.py` files
  - `curl.exe` + JSON -> use `--data-binary @file.json`
- **Non-ASCII:** most engines must have non-ASCII = 0. Exception: `indian_language_ai.py` legitimately has ~1,750 bytes of Hindi/Tamil/etc. script.

---

## Useful commands

    # Apply migration to local
    python -c "import psycopg2, io; conn = psycopg2.connect('postgresql://postgres:dev@localhost:5432/vouchai'); cur = conn.cursor(); cur.execute(io.open('migrations/YYYYMMDD_name.sql','r',encoding='utf-8-sig').read().lstrip('\ufeff')); conn.commit(); cur.close(); conn.close(); print('done')"

    # Wipe a test table locally
    # (see KNOWN-ISSUES.md or any recent session summary for cleanup snippets)

    # Check what tables exist locally
    psql -U postgres -d vouchai -c "\dt charvak_*"

---

## Recent session summaries (in git log)

    git log --oneline -30

Look for commits starting with "Session X/N:" to see per-engine history.