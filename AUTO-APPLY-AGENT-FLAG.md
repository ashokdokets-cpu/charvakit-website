# AUTO-APPLY AGENT — BUILD LATER

**Flagged:** 2026-11-05
**Status:** FLAGGED — build after 10+ bench placements
**Effort:** 5 sessions (~35-40 hours)
**Trigger:** 10+ successful bench placements AND 100+ US-based candidates in Charvak network

---

## PRODUCT OVERVIEW

**Name:** Charvak Auto-Apply Agent
**Purpose:** Candidate-facing agent that finds US contract roles, matches to Charvak US candidates, notifies candidates, handles approval, submits to direct clients.
**User:** US-based candidates on Charvak (B2C).
**Legal risk:** Medium — requires candidate consent per application.

**Why build later:**
- Requires 5-10 direct client relationships (you have 0)
- Requires 100+ US-based candidates in Charvak (you have 0)
- Requires candidate approval flow (not built)
- Bench-Placement Agent builds the pipeline this agent needs

**Do NOT build until:**
- 10+ bench placements completed
- 100+ US-based candidates in Charvak
- 5-10 direct client relationships established

---

## THE 5-SESSION BUILD (WHEN TRIGGERED)

### Session 5 — Direct Client Role Pipeline

**Purpose:** Store US contract roles from your direct clients (not job boards, not ATS).

**Deliverables:**
1. `charvak_direct_roles` table
2. `direct_roles_engine.py`
3. `/contract-roles` page (private, gated)
4. Manual entry UI for 5-10 roles

**Not from:**
- Workday, Greenhouse, Lever, Taleo (ATS — prohibited)
- LinkedIn Easy Apply (prohibited)
- Indeed Apply (prohibited)

**Only from:**
- Your direct clients
- CBREX network
- Referrals
- Vendor relationships

### Session 6 — Candidate-Facing Matching

**Purpose:** Extend matching engine to match roles to Charvak's US candidate network.

**Deliverables:**
1. `charvak_candidate_matches` table
2. Reuse `bench_matching_engine.py` with new output target
3. Match score 0-100 (same methodology)

**Filters:**
- US work auth required (no sponsorship candidates excluded)
- US hours availability
- Available to start

### Session 7 — Candidate Approval Flow

**Purpose:** Email candidate → reply YES/NO → submit only on YES.

**Deliverables:**
1. `charvak_candidate_responses` table
2. SendGrid email template
3. Reply detection (YES/NO parsing)
4. Tracking per candidate per role

**Email format:**
"Hi [Candidate], This role matches your profile: [Role] at [Company], [Rate], [Location]. Why you match: [breakdown]. Your certificate: [URL]. Reply YES to submit, NO to skip."

### Session 8 — Client Submission

**Purpose:** On candidate YES, send email to your direct client contact.

**Deliverables:**
1. `charvak_candidate_submissions` table
2. SendGrid email to client with resume + cert URL + JD fit
3. Tracking submission → response → interview → placement

### Session 9 — Auto-Apply Dashboard

**Purpose:** Admin dashboard for the auto-apply agent.

**Deliverables:**
1. `/admin/auto-apply` page
2. KPIs: matches, notifications, approvals, submissions, interviews, placements
3. Filters: candidate, role, status, date
4. Weekly summary

**Total: 5 sessions (~35-40 hours)**

---

## LEGAL CONSTRAINTS (NON-NEGOTIABLE)

The Auto-Apply Agent MUST NEVER:
- ❌ Submit to Workday, Greenhouse, Lever, Taleo
- ❌ Submit to LinkedIn Easy Apply
- ❌ Submit to Indeed Apply
- ❌ Submit without candidate approval (per application)
- ❌ Mass-apply to 50 roles/candidate/day

The Auto-Apply Agent MUST ALWAYS:
- ✅ Candidate reviews each role before applying
- ✅ Candidate replies YES to authorize submission
- ✅ Submit only to YOUR direct client contacts
- ✅ 3-5 high-quality matches per candidate per week (not 50/day)
- ✅ Full audit trail per submission

**Violating these rules = ToS violation + candidate account bans + GDPR/DPDP violation + destroyed reputation.**

---

## REVENUE MODEL

**Per placement:**
- 15% of first-year base salary
-  role = .5K per placement
-  role =  per placement

**Realistic target (after trigger):**
- Month 1-2 (build): 0 placements
- Month 3-4 (early): 1-3 placements (-)
- Month 5-6 (scaling): 3-6 placements (-)
- Month 7-12 (mature): 6-12 placements/month (-/month)

**Year 1 (after build) target: - in placement fees.**

---

## PREREQUISITES (Before Session 5)

1. **10+ bench placements completed** — proves the matching engine + submission flow works
2. **100+ US-based candidates in Charvak** — source via LinkedIn, Naukri US, Hired, Wellfound
3. **5-10 direct client relationships** — clients who will receive candidate submissions
4. **Legal review** — GDPR/DPDP compliance for candidate data + consent flow

---

## RELATED FILES

- See `BENCH-PLACEMENT-AGENT-FLAG.md` (product 1, build NOW)
- See `INVERTED-MARKETPLACE-FLAG.md` (candidate-facing ecosystem)
- See `END-TO-END-PIPELINE-EXTENSION-FLAG.md` (Discover, Fit %, Reach)

---

**Last updated:** 2026-11-05
**Next review:** When trigger fires (10+ bench placements)
**Owner:** Bhavya M