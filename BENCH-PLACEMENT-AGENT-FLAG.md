# BENCH-PLACEMENT AGENT — BUILD NOW

**Flagged:** 2026-11-05
**Status:** ACTIVE BUILD — Session 1 starts this week
**Effort:** 4 sessions (~30-35 hours)
**Trigger:** Now — active build for US staffing business

---

## PRODUCT OVERVIEW

**Name:** Charvak Bench Agent
**Purpose:** Internal sales tool for US staffing — finds US contract roles that match the H1B/OPT bench, surfaces them daily, lets you submit with one click.
**User:** You (Bhavya) and any recruiters on the Charvak team.
**Legal risk:** Zero — your own inbox, your own bench, your own vendor emails.

**Why this is legal:**
- Parses emails to YOUR OWN inbox (jd-parser@charvakit.com)
- Matches against YOUR OWN bench candidates
- Surfaces matches to YOU (not to candidates)
- YOU email the vendor (not a bot)
- No ATS automation, no LinkedIn scraping, no GDPR/DPDP violation

---

## THE 4-SESSION FULL BUILD

### Session 1 — Vendor JD Inbox Parser

**Purpose:** Ingest all vendor JD emails into a searchable database.

**Deliverables:**
1. `charvak_vendor_jds` table (13 columns)
2. `vendor_jd_engine.py` (~250 lines)
3. `/admin/vendor-jds` page (template + JS)
4. `POST /api/vendor-jds/ingest` webhook
5. `GET /admin/vendor-jds` page
6. `GET /api/vendor-jds` JSON
7. Email forwarder setup (SendGrid Inbound Parse OR Gmail Apps Script)

**Database schema:**
- jd_id, source_email, vendor_name, vendor_contact
- role_title, skills_required, rate_min, rate_max
- location, work_auth_required, duration, client_name
- jd_text, parsed_at, status

**Test:**
- Forward 5 vendor JDs → all appear in DB
- Fields parsed correctly
- Filters work (rate, work auth, skills, location)
- Search works

**Effort:** 1 session (~6-8 hours)

### Session 2 — Bench Candidate Profile

**Purpose:** Manage H1B/OPT bench candidates with US-specific fields.

**Deliverables:**
1. `charvak_candidates` extended (7 new columns)
2. `bench_engine.py` (~200 lines)
3. `/admin/bench` page (template + JS)
4. CSV import flow
5. 4 routes (add, list, import, stats)

**New columns:**
- work_auth_status, availability, rate_min, rate_max
- visa_expiry, has_verified_cert, bench_since

**Test:**
- Add 3 candidates manually
- Import 5 from CSV
- All 8 appear in /admin/bench
- Filters work
- Stats show correct counts

**Effort:** 1 session (~6-8 hours)

### Session 3 — Matching Engine

**Purpose:** Score every vendor JD against every bench candidate.

**Deliverables:**
1. `charvak_bench_matches` table
2. `bench_matching_engine.py` (~300 lines)
3. 3 routes (match one, list, match all)
4. Cron `bench-agent-daily-match` at 8 AM IST

**Match score:** 0-100 based on:
- Skill overlap (60%)
- Work auth fit (20%)
- Rate fit (10%)
- Availability fit (10%)

**Reuses:**
- `jd_calibration.py` (skill extraction)
- `skill_catalog.py` (518 skills)
- `career_assessment_engine` (candidate skills)

**Test:**
- 5 JDs + 8 candidates → ~40 matches created
- Top 5 matches sensible
- Scores 0-100 with breakdown
- Cron runs daily at 8 AM

**Effort:** 1 session (~6-8 hours)

### Session 4 — Daily Digest + Submission Workflow

**Purpose:** Daily email + one-click submission to vendors.

**Deliverables:**
1. `charvak_bench_submissions` table
2. `bench_agent_engine.py` (~350 lines)
3. `/admin/bench-agent` dashboard
4. Daily digest email (9 AM IST)
5. Pre-filled vendor submission email
6. 5 routes (digest, submit, update, stats)

**Daily digest includes:**
- Top 20 matches (role + bench candidate + score + why-they-match)
- One-click "Submit" button per match
- KPIs: matches today, submitted, responded, interviews, placements

**Submission email pre-fills:**
- Vendor email address
- Candidate name, cert URL, resume, rate
- Fee terms (15% on hire)
- 90-day replacement

**Test:**
- Daily digest arrives at 9 AM
- Click Submit → pre-filled email
- Update status to responded/interview/placement
- KPIs update
- Weekly summary shows revenue

**Effort:** 1 session (~6-8 hours)

**Total: 4 sessions (~30-35 hours)**

---

## PREREQUISITES (Before Session 1)

1. **Dedicated email address:** `jd-parser@charvakit.com` — set up on GoDaddy OR forward from `hr@charvakit.com` via Gmail filter
2. **SendGrid Inbound Parse** configured (OR Gmail Apps Script forwarding)
3. **Bench candidates identified** — you should have 10-100 H1B/OPT candidates to add in Session 2
4. **Vendor emails flowing** — 20-50 vendor JDs per week is the target volume

---

## REVENUE MODEL

**Per placement:**
- 15% of first-year base salary
-  role = .5K per placement
-  role =  per placement

**Realistic target:**
- Month 1-2 (build + first placements): 0-3 placements
- Month 3-4: 3-5 placements (-)
- Month 5-6: 5-10 placements (-)
- Month 7-12: 10-15 placements/month (-/month)

**Year 1 target: - in placement fees.**

---

## RELATED FILES

- See `BENCH-AGENT-IMPLEMENTATION.md` (created during Session 1)
- See `AUTO-APPLY-AGENT-FLAG.md` (product 2, build later)
- See `INVERTED-MARKETPLACE-FLAG.md` (candidate-facing ecosystem, build later)

---

**Last updated:** 2026-11-05
**Next review:** After Session 4 (first working product)
**Owner:** Bhavya M