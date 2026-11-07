# JOB BOARD EXTENSION — IN BUILD (Session 107)

**Started:** 2026-11-07
**Status:** ACTIVE BUILD
**Target:** US H1B/OPT/H4 EAD contract candidates (PREM, ABHINAYA, Haritha)
**Effort:** 4 sessions (~13 hrs total)

---

## STRATEGIC PURPOSE

The Bench-Placement Agent currently only knows about jobs you forward by email.
Adding job-board ingestion gives:

- Passive discovery (24/7 intake)
- Worldwide coverage (not limited to Gmail inbox)
- Scale (hundreds/day, not dozens/week)

---

## CANDIDATE CONSTRAINT

All bench candidates are US contract workers:

| Candidate | Work Auth | Rate | Skills |
|---|---|---|---|
| PREM CHARAN | H1B | $75-90/hr | K8s, AWS, Terraform, Docker |
| ABHINAYA | (verify) | (verify) | (verify) |
| Haritha | (verify) | (verify) | (verify) |

Every ingested job MUST be filtered to US-eligible. EU-only, UK-only,
or region-restricted jobs are rejected at ingest time.

---

## TIER 1 SOURCES — BUILD FIRST (all legal, all free)

### Remotive (https://remotive.com/api/remote-jobs)

- Public API, no auth
- Worldwide remote tech jobs
- Attribution required (link in admin UI)
- Free
- Adapter complexity: LOW
- Effort: 1.5 hrs

### Arbeitnow (https://www.arbeitnow.com/api/job-board-api)

- Public API, no auth
- Worldwide remote + EU tech jobs
- Free
- Adapter complexity: LOW
- Effort: 1.5 hrs

### Himalayas (https://himalayas.app/api)

- Free tier (rate-limited)
- Worldwide remote tech jobs
- Adapter complexity: LOW-MEDIUM
- Effort: 2 hrs (Session 108+)

---

## TIER 2 SOURCES — BUILD SECOND (manual + careful)

### Dice.com

- US-only IT contract board — BEST FIT for bench candidates
- No public API
- Scraping requires care (respect robots.txt, rate-limit to 1 req/sec,
  rotate user-agent, honor 403)
- SAFER: manual paste (user pastes JD URL -> engine fetches once)
- Effort: 4 hrs

### TechFetch

- US bench-sales-focused board
- No public API
- Same scraping constraints as Dice
- SAFER: manual paste
- Effort: 3 hrs

---

## TIER 3 — SKIP ENTIRELY

| Board | Reason |
|---|---|
| LinkedIn | ToS forbids scraping. IP ban risk. |
| Indeed | ToS forbids scraping. IP ban risk. |
| Glassdoor | ToS forbids scraping. IP ban risk. |
| Monster | Requires paid API |
| Upwork | Freelance, not staffing fit |
| Toptal | Private vetted network |
| Wellfound | Manual only, small volume |
| WeWorkRemotely | RSS only, low volume |

If any of these become the ONLY source of a needed job, offer a
"paste this URL" manual flow. NEVER build a bulk scraper.

---

## ARCHITECTURE

    Cron (daily) OR manual click
        |
        v
    job_ingest_engine.ingest_all()
        |
        +-- ingest_remotive()   -> fetch -> filter US-eligible -> insert
        +-- ingest_arbeitnow()  -> fetch -> filter US-eligible -> insert
        +-- ingest_himalayas()  -> fetch -> filter US-eligible -> insert
        |
        v
    charvak_jobs (with source, external_job_id, raw_json)
        |
        v
    bench_matching_engine.match_candidates_to_jobs()
        |
        v
    charvak_bench_matches (with job_id FK, source='job_board')
        |
        v
    /admin/bench-matches dashboard shows both vendor-JD matches AND job-board matches

---

## SCHEMA CHANGES (migrations/20261107_job_sources.sql)

    ALTER TABLE charvak_jobs
      ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual',
      ADD COLUMN IF NOT EXISTS external_job_id TEXT,
      ADD COLUMN IF NOT EXISTS raw_json JSONB,
      ADD COLUMN IF NOT EXISTS is_us_eligible BOOLEAN DEFAULT TRUE,
      ADD COLUMN IF NOT EXISTS location TEXT;

    CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_source_external
      ON charvak_jobs (source, external_job_id)
      WHERE external_job_id IS NOT NULL;

    ALTER TABLE charvak_bench_matches
      ADD COLUMN IF NOT EXISTS job_id TEXT,
      ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'vendor_jd';

Idempotent. Safe to run on prod.

---

## ENGINE SPEC — job_ingest_engine.py

    class JobIngestEngine:
        def _ensure_tables(self): ...          # Idempotent DDL
        def ingest_remotive(self): ...         # -> {inserted, skipped, errors}
        def ingest_arbeitnow(self): ...        # -> same shape
        def ingest_himalayas(self): ...        # -> same shape
        def ingest_all(self): ...              # -> {source: result, ...}
        def _is_us_eligible(self, job): ...    # Filter: US or worldwide
        def _dedupe(self, source, external_id): ...  # Check existing
        def list_sources(self): ...            # For admin UI
        def sync_one(self, source_name): ...   # Trigger one

US-eligible filter logic:

    location = job.get("candidate_required_location", "").lower()

    US = ["usa", "united states", "us only", "us remote",
          "worldwide", "anywhere", "global"]

    EU = ["eu only", "europe", "uk", "germany", "france",
          "netherlands", "spain", "italy"]

    # Allow if location contains any US keyword
    # Reject if location is EU-only and doesn't mention US
    # Default: allow (benefit of the doubt)

---

## ROUTES

    POST /api/admin/job-sources/sync       # Trigger sync (auth required)
    GET  /api/admin/job-sources            # List sources + last sync
    GET  /admin/job-sources                # Admin page

---

## ADMIN UI — templates/admin-job-sources.html

Table:

| Source | Status | Last Sync | Total Jobs | US-Eligible | Actions |
|---|---|---|---|---|---|
| Remotive | Enabled | 2h ago | 145 | 98 | Sync Now |
| Arbeitnow | Enabled | 2h ago | 89 | 62 | Sync Now |
| Himalayas | Disabled | — | — | — | Enable |

Plus:
- "Sync All" button
- Attribution footer (required by Remotive API ToS)
- Recent ingest log (last 10 runs)

---

## SCHEDULE

| Week | Session | Deliverable |
|---|---|---|
| Week 1 | 107 (this) | C1: Remotive + Arbeitnow |
| Week 1 | (parallel) | Real-world testing: forward JDs, submit, track |
| Week 2 | 108 | C2: Dice manual paste adapter |
| Week 3 | 109 | C3: TechFetch manual paste adapter |
| Week 3 | 110 | C4: Admin UI + cron |
| Week 4+ | 111+ | Himalayas, CyberCoders, WeWorkRemotely (RSS) |

---

## METRICS TO WATCH

After C1 ships:

- **Ingest rate:** jobs/day per source
- **US-eligible rate:** % of raw jobs that pass filter
- **Match rate:** % of ingested jobs that match >=1 candidate at 60+
- **Submit rate:** % of 80+ matches that become submissions
- **Reply rate:** % of submissions that get any response

Watch for 2 weeks. If Remotive/Arbeitnow -> 0 matches, then move
Dice/TechFetch up in priority. If they -> 5+ matches/day, they are
working and don't need expansion.

---

## FILES

**Create:**
- `job_ingest_engine.py`
- `migrations/20261107_job_sources.sql`
- `templates/admin-job-sources.html`

**Modify:**
- `main.py` - add routes + template render
- `bench_matching_engine.py` - add `match_candidates_to_jobs()`
- `COMMITMENT.md` - session entry

**Do not touch:**
- `vendor_jd_engine.py` - email path unchanged
- `enhanced_email.py` - email templates unchanged
- `resume_pdf_engine.py` - PDF generation unchanged

---

## ROLLBACK

If Remotive/Arbeitnow ingestion turns out to be noise:

1. Disable in admin UI (sets `active=FALSE` in `charvak_job_sources`)
2. OR delete the job rows: `DELETE FROM charvak_jobs WHERE source IN ('remotive','arbeitnow')`
3. OR remove routes from `main.py`

All reversible. Zero risk to existing pipeline.

---

**Owner:** Bhavya M
**Created:** 2026-11-07
**Status:** ACTIVE BUILD
**Review:** After C1 ships (target: 2026-11-08)

---

## FILTER EDGE CASES — Flagged 2026-11-07 (Session 108)

**Discovered during Session 107 prod verification.**

The strict US/Canada filter has edge cases that let through German jobs:

1. **Berlin / Remote** -> has_non_us=True (berlin), has_global=True (remote) -> allowed (WRONG)
   A German job with remote option slips through.
   Fix: reject if has_non_us regardless of has_global

2. **Homeoffice** (German word) -> not in NON_US_CA list -> allowed (WRONG)
   Fix: add 'homeoffice' to NON_US_CA list

3. **Augsburg** -> not in NON_US_CA list -> allowed (WRONG)
   Fix: add 20+ German cities to NON_US_CA list

4. **(m/w/d) title suffix** -> German-market indicator
   Fix: reject if title contains (m/w/d), (w/m/d), (m/f/d), (w/m/x)

### Fix Plan (30 min, Session 108)

In `job_ingest_engine.py::_is_us_eligible()`:
Change logic — non-US always rejected, no 'remote' escape:
    if has_non_us_signal:
        return False

Add to NON_US_CA: homeoffice, augsburg, dortmund, essen, bremen, dresden, hanover, nuremberg, nürnberg, bonn, münster, karlsruhe, mannheim, wiesbaden, mainz, kiel, freiburg, erfurt, rostock, kassel, potsdam, saarbrücken, trier

Add title-level check in ingest_remotive / ingest_arbeitnow:
    import re
    if re.search(r'\(m/w/d\)|\(w/m/d\)|\(m/f/d\)|\(w/m/x\)', title, re.IGNORECASE):
        return False  # German-market role

### Impact
Current state (2026-11-07): 90 job_board matches, ~3-5 German jobs slipped through, all score below 54 (below min_score=60 filter), not user-visible.
After filter fix: those rows would be rejected at sync time. Cleaner data.
Why not critical: 60 min_score filter hides these already. Fix is polish, not blocker.

---

