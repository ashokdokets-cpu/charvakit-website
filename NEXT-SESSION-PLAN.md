# NEXT-SESSION-PLAN

**Purpose:** Forward-looking plan for upcoming sessions.
**Last updated:** 2026-11-08 (Session 108 complete)
**Historical reference:** `git log --all --oneline -- NEXT-SESSION-PLAN.md`

---

## Session 109 - NEXT (not yet started)

### Priority 1 - Security (do first)

- [ ] Rotate CRON_SECRET on Render (web service + cron job)
- [ ] Rotate hr@charvakit.com admin password
- [ ] Verify cron ran at 6 AM UTC (11:30 AM IST)

### Priority 2 - Verification of Session 108

- [ ] Check /admin/job-sources — see today's ingestion counts
- [ ] Check /admin/rejected-jds — confirm count is ~58 (not 642)
- [ ] Check /admin/retention — confirm tiered config visible
- [ ] Check /admin/migrations — dashboard renders (129 pending is cosmetic)

### Priority 3 - Session 109 Build (choose one)

**Option A - Track D Phase A (~1 session)**
- Wire JD parser into /ai-assessment Step 1
- "I have a JD" toggle + prefill role/industry/level
- Update /jd-assessment CTA to carry prefill URL params
- Files: templates/ai-assessment.html, templates/jd-assessment.html
- No external blockers

**Option B - 108E follow-up (~30 min)**
- Add "hugging face" -> ai alias
- Lower title-match length threshold from 3 to 2
- Improves ML Inference job pass rate (edge case)

**Option C - Migration backfill (~5 min)**
- Mark all 129 old migrations as applied in tracker
- Cosmetic only — dashboard works without it

---

## Session 110+ - Queued (blocked or deferred)

### Blocked on external event
- Track C (Amrita CDC pilot) — blocked on Amrita signing
- Track E (Behavioral readiness) — blocked on Amrita signing
- Track F (Verified Jobs Board) — blocked on 3+ employer demand
- Inverted marketplace — blocked on paying customer
- Auto-Apply Agent — blocked on 10+ bench placements first

### Demand-triggered
- Dice API — requires paid partner contract (not a build task)
- TechFetch, Ardent — manual subscriptions, covered in VENDOR-INFLOW-SETUP.md
- Enterprise F5-F8 — blocked on enterprise customer requesting
- A4 LMS Bridge — blocked on institution asking

### Scheduled reminders
- GPT-4o-mini retirement: Jan 14, 2027 (see GPT-RETIREMENT-REMINDER.md)

---

## Historical note

Sessions 1-108 are preserved in git commit messages. Full history:
  git log --all --oneline

Session 108 shipped:
- 108A: VENDOR-INFLOW-SETUP.md
- 108B: 6 new API sources + tech-role filter
- 108C: Retention engine + tiered rejections
- 108D: Daily cron automation (11:30 AM IST)
- 108E: Filter synonym expansion (104 aliases) + fallbacks
- 108F: Migration status dashboard
- 108G: Bench-relevance filter (visa + location + skills)

---

**Next session:** 109 (start with Security priorities)