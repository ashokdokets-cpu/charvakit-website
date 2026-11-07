# Charvak - Commitment Tracker

**Purpose:** Track every planned-but-not-completed item and session progress.
**Last updated:** 2026-11-08 (Session 108 active)
**Historical reference:** `git log --all --oneline -- COMMITMENT.md` shows every commit.

---

## Session 108 - ACTIVE (2026-11-08)

**Purpose:** Multi-source job inflow + bench-relevance filter + retention engine

### Task Status

| # | Task | Status | Effort | Deliverable |
|---|---|---|---|---|
| 108A | Vendor email inflow setup guide | Complete | 30 min | VENDOR-INFLOW-SETUP.md |
| 108G | Bench-relevance filter (skills + visa + location) | Complete | 2-3 hrs | bench_jd_filter.py + /admin/relevance-config |
| 108B | Add 5-6 API sources | Pending | 4-6 hrs | Extended job_ingest_engine.py |
| 108C | Retention engine + purge logic | Pending | 2-3 hrs | data_retention_engine.py |
| 108D | Cron automation (daily sync + cleanup) | Pending | 2 hrs | Render cron + endpoints |
| 108E | Filter edge case fix | Pending | 30 min | job_ingest_engine.py patch |
| 108F | Auto-migration hook | Pending | 1 hr | main.py startup hook |

### Session 108 Shipped

**108A - Vendor Inflow Setup Guide**
- VENDOR-INFLOW-SETUP.md (~9 KB)
- Documents 6-8 email channels: Ardent, Talentify, TechFetch, Dice, Indeed, LinkedIn, Wellfound
- Gmail forwarding rules for each
- CBREX already configured separately

**108G - Bench-Relevance Filter**
- bench_jd_filter.py (~400 lines)
- 3 gates: visa compatibility + location (US/CA only) + skill overlap (30% threshold)
- Rate is NOT a gate (used only for scoring)
- Rejected JDs logged to charvak_rejected_jds
- Migration 20261108_relevance_filter.sql - 3 tables
- 6 routes in main.py
- 2 admin UIs: /admin/relevance-config, /admin/rejected-jds
- Integrated into vendor_jd_engine.py (email path) + job_ingest_engine.py (API path)
- Applied to prod, deployed, tested with 83 rejections / 0 errors

### Files delivered Session 108

- VENDOR-INFLOW-SETUP.md
- bench_jd_filter.py
- migrations/20261108_relevance_filter.sql
- templates/admin-relevance-config.html
- templates/admin-rejected-jds.html
- main.py (6 new routes)
- vendor_jd_engine.py (filter hook)
- job_ingest_engine.py (filter hook)

### Tracker File Rules (critical)

COMMITMENT.md was 70 MB due to repeated PowerShell encoding corruption.
The file was rebuilt from scratch 2026-11-08. Historical commits contain mojibake
and are NOT recoverable. Full history: git log --all --oneline -- COMMITMENT.md

Rules going forward:
- Never use `>` or `>>` for UTF-8 content (PS 5.1 converts to UTF-16, doubles size)
- Never use `Out-File -Encoding UTF8` (adds BOM, may re-encode)
- Never use `Add-Content` with here-strings containing Unicode
- For git extraction: cmd /c "git show HASH:file > file"
- For content writes: [System.IO.File]::WriteAllText($path, $text, $utf8NoBom)
- For content appends: [System.IO.File]::AppendAllText($path, $text, $utf8NoBom)
- Always verify file size delta matches expected bytes

### Historical milestones (for reference)

Sessions 1-107 are preserved in git commit messages. Highlights:
- Session 1-4: Bench candidates + matching engine + submit workflow
- Session 22-24: Client staffing pipeline + CBREX roles
- Session 27-28: Assessment integrity + Judge0
- Session 30-33: Unified candidate profile + jobs feed
- Session 46-52: Waves 1-2 (passport, skill-twin, cohorts, Trust API, CAS)
- Session 83-84: Enterprise features (scorecard, compliance, screen agent, recruiter dashboard)
- Session 101: Privacy-first passport visibility
- Session 106: 518-skill catalog + auto-calibrator
- Session 107: Job board ingestion (Remotive + Arbeitnow) + admin UI
- Session 108: Vendor inflow guide + bench-relevance filter

---

**Session 108 next:** 108B, 108C, 108D, 108E, 108F