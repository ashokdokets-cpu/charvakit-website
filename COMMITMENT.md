## Session 26 CLOSED (2026-10-05) - Security sweep + cautious cleanup

## Session 36 CLOSED (2026-10-07) - Two-tier AI course unlock

Restructured the AI-designed course into a freemium product.

**Commit:** 3ea3320 (7 files, +549/-21)
Plus: email_verification.py (Session 35 dev flag)

**Product shape:**
- Design: 50 credits
- Weeks 1-2: free to consume
- Unlock: 150 credits (weeks 3+ + certificate + AI tutor)

**Session 37 candidates:**
- A (recommended): Admin UI for integrity events
- B: Roll unified panel to /my-results, /profile
- C: Certificate round 2
- D: AuditBot Continuous


## Session 34 CLOSED (2026-10-07) - AI course designer

Zero dead ends achieved. Every weak topic now produces a course.

**Commit:** ce34cfe

**Files:**
- main.py (+20 free-enroll branch, -5 auto-enroll lines)
- templates/ai-assessment.html (adaptive weeks + Review course CTA + escaped call site)
- templates/course-detail.html (dynamic login hint)

**Verified:**
- create-order returns {status: exists, free: true} for Rs 0 courses
- Enroll Now skips Razorpay and lands in the lesson player
- Adaptive weeks (6/4/3) confirmed

**Session 35 candidates:**
- A (recommended): cleanup + polish (Postgres rotation, DEV_SKIP flag, Rs 0 EMI fix, panel rollouts)
- B: Admin UI for integrity events
- C: Certificate round 2
- D: AuditBot Continuous


## Session 33 CLOSED (2026-10-07) - Assess -> Upskill loop

Fourth step of the unification arc. Arc complete.

**Commit:** <hash>

**Files:**
- career_assessment_engine.py (prompt + rule + normalize)
- templates/ai-assessment.html (renderLearningPath course card)

**Verified:**
- fills_topic populated on all new paths
- Browser renders badge + CTA
- Start course -> course detail works

**Local env fix:**
- Applied charvak_course_levels migrations to local DB (75 rows)

**Session 34 candidates:**
- A (recommended): AI course designer (Session 18 reuse)
- B: Render password rotation + docs polish
- C: Admin UI for integrity events
- D: Certificate round 2


## Session 32 CLOSED (2026-10-07) - Unified candidate signup (Phase 3)

Third step of the unification arc. Write-side unification complete.

**Commit:** ffa00dc

**Files:**
- candidates_engine.py (ALLOWED_FIELDS 23 -> 37, _ensure_columns, get_me 25 -> 39 cols)
- candidate_engine.py (register_candidate delegates to upsert)
- main.py (+new route, 2 redirects)
- templates/candidate-signup.html (252-line form -> 60-line gate)
- templates/profile.html (+5 fields +prefill)
- templates/base.html (nav merged 2 -> 1)
- templates/about.html, how-it-works.html, reverse-staffing.html, register.html (link repoints)

**Verified:**
- signup_source self-heals + validates
- get_me round-trips all fields
- Legacy register endpoint delegates
- /candidate/signup redirects authed users to /profile
- /profile writes and prefills the 5 new fields
- Prod: all four endpoints return expected codes

**Session 33 candidates:**
- A (recommended): Assess -> Upskill loop
- B: Roll unified panel to /my-results, /profile
- C: Top-3 jobs in /career-center panel
- D: Docs + backup polish


## Session 31 CLOSED (2026-10-06) - Unified jobs feed (Phase 2)

Second step of the unification arc.

**Commit:** d0d9d77

**Files:**
- jobs_unified_engine.py (new, ~230 lines)
- main.py (+4 lines: import + /career-center/jobs route + /api/jobs/unified)
- templates/career-jobs.html (new, ~280 lines)
- templates/career-v2.html (+1 panel link, +9 lines refresh feedback)

**Verified:**
- 8-scenario HTTP matrix on /api/jobs/unified
- Sanitization over HTTP (no staffing leaks)
- Browser: 8 items, filters work, search works, cards navigate
- Prod: /career-center/jobs and /api/jobs/unified both 200

**Session 32 candidates:**
- A (recommended): unified candidate signup entry point
- B: Close the Assess -> Upskill loop
- C: Roll unified panel to /my-results and /profile
- D: Show top 3 jobs inline in the /career-center panel


## Session 30 CLOSED (2026-10-06) - Unified candidate profile (Phase 1)

First step of the unification arc.

**Commits:**
- 2040caf feat(candidate): unified candidate profile endpoint
- 8a4025d feat(candidate): unified activity panel in Career Center

**Files:**
- candidate_profile_engine.py (new, ~290 lines)
- main.py (+54 lines: 1 import + 1 route)
- templates/career-v2.html (+170 lines: panel HTML + JS)

**Sections delivered (10):**
identity, profile, assessments, certificates, applications,
training, career_engine, integrity, credits, doketsrb

**Session 31 candidates:**
- A (recommended): /api/jobs/unified — merge job-board + staffing + micro-projects
  into one feed, new /career-center/jobs page
- B: Unified /candidate/signup entry point (deprecate /developer-signup)
- C: Close the Assess -> Upskill loop (assessment result -> course enrollment)
- D: Roll the unified panel to other pages (/my-results, /profile)

**Longer-term arc (from the unification discussion):**
- 31: unified jobs feed (read)
- 32: unified candidate signup (write)
- 33: assessment-to-course loop

**Reminder:** Render Postgres password rotation still pending (since Session 19).


## Session 29 CLOSED (2026-10-06) - Career Assessment Phase 2b COMPLETE

SQL format shipped. Phase 2b is done — all 10 formats live.

**Commit:** a649f80

**Files:**
- career_assessment_engine.py (+239 lines: _prompt_sql, _normalize_question
  sql branch, _strip_answers_for_frontend sql branch, _score_sql_batch,
  _sql_outputs_match helper, _dispatch_scoring wiring, registry flip)
- templates/ai-assessment.html (+3 lines: sql renderer branch; textarea
  starter prefill removed for both coding and sql)

**Three bugs caught and fixed in-session:**
1. AI included 'id' column in expected_output for single-column tasks
   → prompt rule: only include columns the task names
2. AI included sort key in expected_output (name|age for "names by age")
   → prompt rule: sort keys are NOT output columns
3. AVG returned 150.0 but AI wrote 150
   → Python-side comparison with float tolerance instead of Judge0 exact match

**Bonus fix:** textareas (coding + sql) had starter_code prefilled, so
blank submissions submitted the starter text. Now empty + placeholder.

**Session 30 candidates:**
- A: Admin UI for integrity events (Session 27 data)
- B: Roll Layer A out to other assessments
- C: Phase 4 certificates for coding/sql
- D: Backup + docs polish session


## Session 28 CLOSED (2026-10-06) - Career Assessment Phase 2b (coding)

Coding format is now live. Real code execution, real test-case scoring.

**Commits:**
- deca0c0 feat(judge0): Session 28a - Judge0 client (242 lines)
- c65d118 feat(coding): Session 28b - coding format (164 lines changed)

**Files:**
- judge0_client.py (new)
- career_assessment_engine.py (5 methods + registry flip)
- templates/ai-assessment.html (renderQuestionBody coding branch)

**Verified E2E:**
- 10 coding questions generated (real OpenAI)
- Judge0 executed candidate submissions
- Score persisted, per-answer feedback populated
- Result page renders correctly on prod

**Session 29 candidates:**
- A: SQL format (completes Phase 2b; 1 session)
- B: Admin UI for integrity events (Session 27 output)
- C: Roll Layer A + coding to Versant/Mock/CBAT/IELTS


## Session 27 CLOSED (2026-10-06) - Anti-Cheating Layer A

Shipped environment-signal capture on Career Assessments. Framework
ships standalone (integrity_engine.py); frontend integration is a
self-contained block in ai-assessment.html.

**Commits:**
- 1124a38 feat(integrity): engine + schema + 2 routes
- 91e1b1f feat(integrity): frontend capture

**Files:**
- integrity_engine.py (new)
- migrations/20261005_assessment_integrity.sql (new)
- main.py (import + 2 routes, +465 lines)
- templates/ai-assessment.html (+250 lines)

**Verified:**
- 8-scenario curl matrix (401 / 200 / 404 / 400 / 400 / 200 / 403)
- Engine unit test (record, read, summarize, classify)
- Browser E2E: all 5 event types land in the DB
- Input hardening: list-shaped payload returns 400

**Session 28 candidates:**

- A) Career Assessment Phase 2b — coding + SQL via Judge0. Layer A
  now unblocks this commercially. Recommendation: A.
- B) Admin UI for integrity events — surface them where employers
  see them.
- C) Roll out Layer A to Versant, Mock, CBAT, IELTS — each is a
  small frontend addition.

**Reminder:**
- Render Postgres password rotation still pending (manual task
  flagged since Session 19).


Security sweep on all new admin endpoints: PASSED (zero gaps).

Legacy /api/assessment/* routes: KEPT (deep audit found live
engine-method callers, historical docs, no proof of zero external
callers). Tombstone comment added.

charvak_jobs table: LIVE (DoketsRB sync + ATS engine + 4 public job
board routes verified 200). No cleanup needed.

**Session 27 scope (recommended):**
- Anti-cheating Layer A
- Career Assessment Phase 2b (coding + SQL via Judge0)

**Alternatives for Session 27:**
- AuditBot Continuous
- Silent-Killer 9b polish

---

## Session 25 CLOSED (2026-10-05) - Admin applicant actions

Three patches: status+notes UI, batch download ZIP, dashboard card.
Full admin workflow now runs from the browser.

**Session 26 scope (recommended):**
- Security sweep on new admin endpoints
- Legacy /api/assessment/* route cleanup
- Anti-cheating Layer A

**Alternatives for Session 26:**
- Career Assessment Phase 2b (coding + SQL sandbox)
- AuditBot Continuous
- Silent-Killer 9b cron polish

---

## Session 24 CLOSED (2026-10-05) - Client Roles admin UI

37f978f — full admin interface for staffing pipeline.

**Shipped:**

- `/admin/client-roles` list + stats + filters
- `/admin/client-roles/{role_id}` detail + applicants + modal
- View applicant modal + Download Package button

**Bugs fixed:**

- Modal stacking context, Jinja-in-JS-comment parse error,
  delegation restore, window-scoped load functions

**Session 25 scope (recommended):**

- Status update UI in the applicant modal (shortlist / submitted / hired)
- Recruiter notes textarea
- Batch download ZIP (all applicants per role)

**Alternatives for Session 25:**

- Security sweep on new admin endpoints
- Admin dashboard card linking to /admin/client-roles

---

## Session 23 CLOSED (2026-10-05) - Submission package generator

JSON + PDF + ZIP endpoints live. Zero CBREX references on user-facing
surfaces. See SESSION-CONTEXT.md for details.

**Session 24 scope (recommended):** admin UI
- /admin/client-roles          (list page)
- /admin/client-roles/{role_id} (detail + applicants + downloads)
- Link in admin dropdown
- All backend endpoints already exist; pure frontend work

---

## Session 22.5 CLOSED (2026-10-05) - Staffing pipeline launched

7 real CBREX roles loaded to prod (4 NCS urgent, 2 Lenze normal,
1 Middle East normal). 92 screening questions. HR email notification
live on every application. See SESSION-CONTEXT.md for full details.

**Session 23 scope:** CBREX package generator (JSON + PDF + ZIP per
application).

**Alternatives for Session 23:**
- Admin UI (/admin/client-roles list + role detail)
- Nav link to /admin/client-roles in admin dropdown

---

## Session 22 CLOSED (2026-10-05) - Sprint B: /open-roles pipeline

Shipped the full client-staffing pipeline: public role listing, detail
page, apply modal with dynamic screening questions, consent capture,
inline profile upsert, and automatic retry. CBREX-mediated staffing
is now a working product.

**6 commits (see SESSION-CONTEXT.md for details):**
e23b853, 41a91a1, 598101e, b95d39d + 2 micro-fixes.

**Session 23 scope (recommended):**
CBREX package generator - one-click PDF/ZIP export per application
containing resume, Charvak evaluation, certificate PDF, and consent
proof. This is the piece that makes the pipeline immediately useful
to the team's daily work.

**Alternatives for Session 23:**
- Admin dashboard (/admin/client-roles UI) - 1-2 sessions
- Nav link + candidate profile page (/profile) - 1 short session
- Session 22 retrospective + doc sync pass - 1 session

---

# Charvak — Commitment Tracker

## Sessions 19-21 CLOSED (2026-10-04) - Certificate v2

Three sessions shipped as one certificate-v2 release. See SESSION-CONTEXT.md
for details.

**Session 19 — Size upgrade CTA + supersedes chain** (1 session)
**Session 20 — Certificate polish (Best Score, latest toggle, email)** (1 session)
**Session 21 — Certificate PDF download** (1 session)

**Session 22 scope (recommended):**
Sprint B /my-jobs — verified job matching. The certificate is now a
real shareable artifact; the next move is connecting it to open roles.
Effort: 2 sessions.

**Alternatives for Session 22:**
- Certificate round 2 (QR, watermark, multi-language) — 1 session
- Anti-cheating Layer A (environment signals) — 1 session

---

## Session 18 CLOSED - Custom-course generator + Train stage resurrection (2026-10-04)

Biggest single-fix session of the year. What was scoped as "custom-course
generator (Phase 1)" turned into a full resurrection of the Train stage.

### Shipped (commit series fa50ccd + follow-ups)

**Custom-course generator (the original Phase 1 scope)**
- New credit key custom_course_generation: 50
- ai_courses.generate_custom_course(email, topic, level, weeks, role_hint)
  - reuses plan_curriculum() to build a real multi-week curriculum
  - persists as a private course scoped to the requesting user
- New columns on charvak_courses: is_custom, generated_for_email,
  generated_from_topic, generated_at
- Learning path prompt no longer references external platforms
- Response includes custom_course_candidates — weak topics without a match
- New POST /api/ai-course/generate-custom (auth + 50 cr, idempotent)
- Frontend: "Custom Courses for Your Gaps" section with per-topic Generate CTA

**Train stage bug fixes (unplanned, but critical)**
- charvak_enrollments was missing recipient_name column — the lesson player
  had NEVER worked
- charvak_certificates was missing recipient_name column — certificate insert
  had NEVER succeeded
- my-course.html was missing updateProgress() function — progress stats
  showed dashes forever
- my-course.html POST fetches were missing Authorization headers — clicking
  "Mark Week Complete" redirected to /login
- complete_week() marked enrollment as 'completed' but never called
  complete_course() — certificates were silently never issued
- Course completion UX: after all weeks done, the button now says
  "View Certificate" and links to the certificate page

**Verified E2E**
- Generated a custom course for "Evaluation & Experimentation" weak topic
- Completed all 4 weeks through the browser
- Certificate CERT-9C1DBCD84B4E issued, page renders with recipient name
- Verify URL live at /certificate/{id}

### Session 19 scope (next)

**Session 18 Phase 2 — Size upgrade CTA**
- The free quick readiness check is 10 questions
- Below-benchmark results should offer: "Want a more precise score?
  Take the 20-question Standard check for 25 credits"
- Location: /readiness/{id} certificate page + ai-assessment result page
- Effort: 1 session
- Business impact: converts curiosity into revenue, natural upsell

### Session 20 scope

**Certificate enhancement (Phase 3)**
- Visual signature image on certificate (handwritten scan)
- HMAC verification hash column + /api/certificate/verify/{hash} endpoint
- QR code on certificate that encodes the verify URL
- Public revocation list for cancelled certificates
- Effort: ~2 hours
- Note: legal DSC (Aadhaar eSign/DocuSign) NOT needed for course completions

### Session 21 scope

**Sprint B — /my-jobs verified job matching**
- Certificate becomes useful when it unlocks matched jobs
- Applications carry certificate_id for employer-side verification
- Effort: 2 sessions

---

## Sprint A SHIPPED — Role Readiness Certificate (2026-10-04)

The free, shareable Role Readiness Certificate is live end-to-end.
7 commits: 14b2bb8 through the current HEAD.

**Live routes:** /readiness-check, /readiness/{id}, /api/readiness/*
**Tables:** charvak_readiness_certificates
**Engine:** career_assessment_engine.compute_role_readiness()
**Verified:** full flow works on local, 5 certificates generated

### Follow-ups flagged for Session 18

1. **Custom-course generator** — the learning path currently links to
   external providers (Khan Academy, Coursera). This sends users OFF
   Charvak. Replace with an on-platform custom course generator:
   when no Charvak course matches a weak topic, offer to generate one
   in-house (same shape as the 25-course catalog). No external links.
   Effort: 1.5-2 sessions. Impact: keeps users on-platform, adds
   revenue, closes the learning loop with a Charvak certificate.

2. **Size upgrade CTA** — the free quick check is 10 questions. On
   below-benchmark results, add a CTA to upgrade to a 20-question
   Standard check. Converts curiosity into revenue. Effort: 1 session.

3. **Sprint B — /my-jobs** — verified job matching. The certificate
   becomes useful when it unlocks matched jobs. Effort: 2 sessions.

---

## STRATEGIC GAPS - from COMPETITIVE-STRATEGY.md (2026-10-04)

Four critical gaps identified at the close of Session 16. See
`COMPETITIVE-STRATEGY.md` for the full analysis, roadmap, and metrics.

### FLAGGED - Gap 1 - Role Readiness Score (Session 17, Priority 1)

**What:** Career Assessment produces a raw score. Global leaders (Knovia)
sell a "Role Readiness Score" calibrated to what employers actually need
for a specific (role x industry x level) combination.

**Why:** Converts a self-improvement tool into an employer-facing artifact.
The natural monetization point.

**How:** Add `compute_role_readiness()` to `career_assessment_engine.py`.
Blend topic coverage + ability baseline + market benchmark. Publish a
shareable certificate at `/readiness/{assessment_id}`.

**Effort:** 1-2 sessions.

**Verdict:** SCHEDULED - Session 17

### FLAGGED - Gap 3 - Anti-Cheating Layer A (Session 17, Priority 2)

**What:** No integrity signals on coding/SQL assessments. Employers will
dismiss results without them.

**Why:** AI-assisted cheating is the existential problem of the assessment
industry in 2026. It is the differentiator for trusted assessments.

**How:** Layer A (environment signals - copy/paste, tab-switch, keystroke
velocity) ships with Phase 2b. Layer B (question design) is a habit. Layer C
(behavioral analytics) is Session 18+.

**Effort:** 1-2 sessions.

**Verdict:** SCHEDULED - Session 17 (Layer A alongside Phase 2b)

### FLAGGED - Gap 2 - Multilingual Voice AI (Sessions 20+)

**What:** No voice modality. Competitors (Hunar.AI, Vahan.ai) are winning
the frontline/blue-collar Indian market with 20+ language voice AI.

**Why:** Massive Indian market. Charvak has ElevenLabs + Whisper already.

**How:** Voice Screening pilot - candidate calls a number, IVR in their
language, AI asks questions, answers scored. Telugu/Tamil/Hindi first.

**Effort:** 3-5 sessions.

**Verdict:** DEFERRED - Session 20+ (do not start without a paying
frontline/staffing client)

### FLAGGED - Gap 4 - AuditBot Continuous Compliance (Sessions 18-19)

**What:** AuditBot is a one-time PDF report. Enterprise CISOs need
continuous monitoring. SonarQube/Snyk sell this as recurring SaaS.

**Why:** Converts one-time purchase into a subscription - biggest revenue
multiplier available. Pattern proven by Silent-Killer cron.

**How:** Phase 1 - repo scanner + `/my-repos` dashboard + daily cron +
email alerts on new HIGH/CRITICAL findings.

**Effort:** 2-3 sessions.

**Verdict:** SCHEDULED - Session 18-19


---



### RESOLVED — Premium Report product (Rs 199 PDF unlock) (2026-10-04, 980bbdc)

Shipped end-to-end across Session 16, commits `aa8a279` through `980bbdc`.

- `pdf_engine.py` — fpdf2-based PDF renderer with branded cover page + DejaVu fonts
- `premium_report_engine.py` — one OpenAI call produces 5 AI sections from the source product's free-tier data
- `charvak_premium_reports` table + migration `20261004_premium_reports.sql`
- Credit key `premium_product_report` (400 cr)
- 3 routes: POST /api/premium-report/generate, GET /api/premium-report/list/{email}, GET /api/premium-report/{report_id}/download
- SendGrid email with PDF attachment
- Frontend unlock flow on 3 products: AuditBot, Lock-In Breaker, Skill-Twin
- `/my-reports` dashboard

Verified E2E: real AI content, 400-credit deduction, PDF download works from browser and email link.

**Verdict:** RESOLVED


**Purpose:** Track every planned-but-not-completed item. Nothing gets lost again.
**Created:** 2026-09-20
**Last updated:** 2026-10-04 (Session 18 CLOSED - Train stage resurrection)
**HEAD:** e28c781 (ai-slop) / f58e63f (auth + cache)

### FLAGGED — Premium Report product (₹199 PDF unlock) (2026-09-27)

The `premium-upsell.html` include appears on every product page with a
"Unlock Full Report — ₹199" button. Currently wired to `notifyMe()` (interest
capture only) — no actual purchase flow, no PDF generation.

**To ship as a real product:**

1. **Product feature**
   - PDF generator: takes the free scan result + adds extra AI analysis
     (deeper recommendations, competitor comparisons, action roadmap)
   - Uses a templating library (WeasyPrint, ReportLab) or headless browser
     (Playwright) to render the free result into a formatted PDF
   - Est: 2-3 hours

2. **Payment flow**
   - Razorpay order creation for ₹199 (using existing `payment_engine`)
   - Server-side signature verification (existing pattern)
   - Idempotent webhook (existing pattern)
   - Est: 1-2 hours

3. **Delivery**
   - Store generated PDF in S3/R2/DB (currently no file storage layer)
   - Email PDF as attachment via SendGrid (currently only text HTML)
   - Provide a re-download link in user dashboard
   - Est: 2-3 hours

4. **Admin dashboard**
   - List purchases: who, when, which product, revenue
   - Manual re-send option
   - Est: 1-2 hours

**Total estimate: 8-12 hours.** This is a real product feature — its own
session (or two). Do NOT tack it onto a cleanup pass.

**Design consideration:** Should the premium report be per-product (different
reports for AuditBot vs Lock-In Breaker) or generic (a "fuller analysis" of
any product result)? Per-product is more valuable but 5-6× the work.

**Verdict:** SCHEDULED — dedicated product session

### RESOLVED — processToolPayment referenced but never defined (2026-09-27)

**Resolved 2026-09-28.** Fixed 2026-09-27 (`335b755`) for `premium-upsell.html`; remaining `background-verification.html` fixed 2026-09-28 (`657d1ce`). Replaced with `notifyMe()` interest capture. All 4 originally-flagged templates now clean.


`processToolPayment(amount, description, callback)` is called from at least
4 templates (background-verification.html, bounty-swap.html, ref-swap.html,
ghost-tracker.html) but is not defined anywhere in the codebase.

Every call site throws ReferenceError — user clicks and nothing happens.

Fixed tonight: premium-upsell.html (replaced with notifyMe fallback).

Still broken:
- background-verification.html:43
- bounty-swap.html
- ref-swap.html
- ghost-tracker.html

Fix: replace each with a real payment flow OR notifyMe interest capture.

Verdict: FLAGGED — needs its own cleanup pass

### RESOLVED — reverse-staffing experience field clears after submit (2026-09-27)

**Resolved 2026-09-28.** Fixed 2026-09-27 (`6505695`). Removed `value="3"` default that was resetting the field.


The "Years of Experience" input on /reverse-staffing doesn't reliably
send the typed value. After submit, `document.getElementById('rsExp').value`
returns ''.

Likely cause: `type="number"` blur/commit quirk in Chrome, or the
`parseInt(value) || 0` fallback masking an empty value.

Workaround options:
- Server-side default: `experience = int(data.get("experience_years", 0) or 3)`
- Frontend: read `getAttribute('value')` as fallback

Verdict: FLAGGED — cosmetic, doesn't block the feature

### RESOLVED — "AI-Slop Report Card" teaser shows hardcoded numbers (2026-09-28)

**Resolved 2026-09-28.** The ai-contamination-detector.html page was fabricating all numbers via Math.random(). Replaced with a real fetch to /api/products/ai-slop/scan (25 cr, same backend as /ai-slop-quarantine). Badge: 25 credits per scan. Button: Scan Site (25 cr).

The AI-Slop Quarantine page shows a second card labeled "AI-Slop Report
Card" with sample stats like "45% AI Slop Detected", "7 WCAG Fails",
"Code Bloat 34%". These are static demo numbers, not tied to the user's
actual scan.

Source: rendered from `includes/premium-upsell.html` or a similar shared
partial (the strings aren't in the ai-slop-quarantine.html template).

Concern: a user who just ran a real scan (e.g. 40/100 cleanliness, 5 issues)
might be confused when a card below shows "45% AI Slop Detected" — the
numbers don't match their result.

Two options for a future session:
- (a) Wire the teaser to the actual scan result (cleanliness_score,
  issue_count) — pass them into the include.
- (b) Remove the teaser card and let the real scan output stand alone.

Verdict: FLAGGED — cosmetic, low priority


### RESOLVED — three-file verification pass (2026-09-27)

Audited the three "unknown state" files flagged by earlier sessions:

| File | Verdict | Notes |
|---|---|---|
| `tools_engine.py` | ❌ Doesn't exist | Stale tracker entry; file was never committed or was removed in a prior cleanup |
| `enhanced_assessment_engine.py` | ✅ Healthy | Active (main.py:6603+, universal_company.py:167). OpenAI call uses `requests.post(timeout=20)` — valid sync call, not the Session bug. Has `response_format={"type":"json_object"}`, fence stripping, regex fallback, and real logging. No changes needed. |
| `chatbot_engine.py` | ✅ Healthy | Active (main.py:61, 3611-3633). Uses official `openai.OpenAI` SDK. Returns plain text (chat prose), not JSON — so "AI JSON mode missing" was a false positive. Real logging. No changes needed. |

**Commit:** `<hash>` (docs only — no code changes)

**Verdict:** ✅ All three closed 2026-09-27

### RESOLVED — three-file verification pass (2026-09-27)

**Resolved 2026-09-28.** Resolved 2026-09-27 (`d5592b9`). All three files audited: `tools_engine.py` doesn't exist; `enhanced_assessment_engine.py` + `chatbot_engine.py` both healthy.


Three engines flagged in earlier sessions, never verified. Each needs a
15-30 min audit. Do as one session.

| File | Question | Likely answer |
|---|---|---|
| `tools_engine.py` | Scope unclear — legacy of `tools_ai_backend.py`? Dead code? | Read + grep for imports |
| `enhanced_assessment_engine.py` | Active or legacy? Not referenced by `/api/assessment/*` (those use `advanced_assessment_engine`) | Grep for imports |
| `chatbot_engine.py` | AI JSON mode present? | Read every OpenAI call |

**Why they're flagged:** all three are the same class of risk as the 4
`ai_service` functions found tonight — code that looks fine but may be
silently returning empty on structured responses.

**Approach per file:**
1. Grep for imports to determine active/legacy
2. If active: test the function with a live call (same pattern as tonight's
   verification sweep)
3. If dead: flag for deletion in a cleanup session
4. If JSON mode missing: apply the same 3-part fix (json_mode=True + fence
   strip + print on error)

**Est:** 45-90 min depending on findings.
**Verdict:** SCHEDULED — one focused session

### Session 2026-09-27 (evening) — small-items sweep + ai_service verification

**Commits:**
- `3cee5c4` feat(lms): auth header + email in all 9 fetches
- `d116dc6` fix(bridge): replace broken premium flow with notifyMe
- `80e5b74` feat(contact): honeypot + backend bot heuristics
- `3eccc8b` fix(database): add module logger — silent save_contact failure
- `f893747` docs: session summary
- `dcc6a63` fix(currency): Voice-to-Web prompt + micro-trial USD → INR
- `1e4a0ba` docs(main): legacy banner on /api/assessment/* routes
- `<ai_service hash>` fix(ai_service): json_mode + fence-stripping on 4 JSON functions

**Real bugs found and fixed this evening:**
1. `database.save_contact()` — `logger` was never defined in `database.py`. Every
   contact submission was silently failing to save to DB.
2. `ai_service` — 4 more functions had the missing-json_mode pattern.
3. `lms.html` — 9 fetches unauthenticated against now-auth-gated routes.
4. `bridge.html` — premium flow posted to a 404 route.

**Resolved flags:** post-ai_service verification sweep, currency hardcode,
contact anti-bot, lms.html auth wiring, bridge.html premium 404.

**Remaining major work:** C7 (14 templates), 11 product frontends, dead
`/api/assessment/*` routes (legacy-marked, cleanup candidate).


### RESOLVED — post-ai_service-fix verification sweep (2026-09-27)

Ran the sweep. Found and fixed **4 more functions** with the same
"missing json_mode + bare except + no fence-strip" pattern:

- `generate_assessment_questions` → was returning `[]`
- `localize_website` → was returning `{}`
- `analyze_legacy_code` → was returning `{}`
- `generate_agent_schema` → was returning `{}` (not in original scope — found during fix)

**All 6 tested functions now return real output:**
- neural_wireframe_to_code ✅
- generate_legal_contract ✅
- generate_assessment_questions ✅ (fixed this session)
- localize_website ✅ (fixed this session)
- analyze_legacy_code ✅ (fixed this session)
- generate_agent_schema ✅ (fixed this session)

**Also fixed during the sweep:**
- `_strip_fences` helper added to `ai_service.py`
- micro_trial currency hardcode USD → INR
- Voice-to-Web prompt anchored to INR

**Not verified in this sweep (kept as separate flags):**
- `tools_engine.py` — scope audit (inventory #80)
- `enhanced_assessment_engine.py` — active or legacy? (inventory #83)
- `chatbot_engine.py` — AI JSON mode present? (inventory #84)

**Also found and resolved during the sweep:**
- Repo-wide grep for `requests.Session(timeout=` → zero remaining matches (all fixed tonight)
- AI Tools Suite and 11 AI Products backend auth/credits verified earlier
- student_suite_engine.assist_* verified working earlier this session

**Verdict:** ✅ DONE 2026-09-27


## Session 2026-09-26 / 2026-09-27 — Auth sweep + feature audit

**Shipped:** ~30 commits over 2 days.

**Feature completed:**
- Voice-to-Web Option 2 (auto-deploy, `/sites/{slug}`)
- AI Tools Suite auth + credits + frontend wiring
- Student Suite assist flows
- FYP backend + frontend + roadmap (7 features logged)
- Mock Drives + Versant auth

**Bugs fixed:**
1. `ai_service.call_openai()` — invalid `requests.Session(timeout=30)`, blocked 6 AI functions
2. `tools_ai_backend.call_ai()` — same bug, blocked 8 tools
3. `/api/ai/voice-to-web` — double credit charge
4. Student Suite — `assistAssignment`/`assistResearch` undefined functions
5. Missing `require_auth_for_email` on **~60 routes** across 10 clusters (IDOR pattern)
6. `email_verification.is_verified()` — bare except (hygiene)

**Flagged (deferred, well-scoped):**
- 10 product templates need real forms (product decision)
- `lms.html` minified JS needs manual auth wiring
- `bridge.html` premium flow → `/api/bridge/premium` (nonexistent route)
- 5 unverified `ai_service` functions
- Voice-to-Web currency hardcode (USD → INR fix)
- Anti-bot for `/contact`
- C7: 14 templates with dead payment buttons
- Dead `/api/assessment/*` routes (candidates for deletion)

**Next session:** Mock/Versant done. Next natural step is either:
- Product sprint for 11 AI Products frontend (5-8 hrs)
- C7 template sweep (14 remaining)
- `lms.html` manual patch (30-45 min)

### RESOLVED — Mock Drives + Versant routes auth (2026-09-26)

**Commits:** `2b972a0` (backend) → `<frontend commit>` (frontend)

**Backend:** 10 routes now require `require_auth_for_email`:
- POST /api/versant/start-session
- POST /api/versant/record-audio (multipart — auth email read from form)
- POST /api/versant/submit-text
- POST /api/versant/complete
- GET  /api/versant/sections (auth-only)
- POST /api/mock/start-complete
- POST /api/mock/submit-complete
- POST /api/mock/complete-full
- GET  /api/company-patterns/{id} (auth-only)
- POST /api/voice/tts

**Frontend:** 
- `templates/versant.html` — 5 fetches now send `Authorization` header
- `templates/companies.html` — 4 fetches now send `Authorization` header + email in body

**Verified:** mismatch email → 403, missing email → 401, valid request → route runs.

**Note:** Two routes (`submit-complete`, `complete-full`) previously sent no email in the body. Frontend updated.

**Follow-up:** `/api/voice/tts` is called from `versant.html` (TTS playback). Needs manual verification of the auth header patch — wasn't in the frontend batch because the call is generated dynamically. Flag for spot-check.

**Verdict:** DONE 2026-09-26

### RESOLVED — /api/assessment/* routes appear to be dead code (2026-09-26)

**Resolved 2026-09-28.** Marked legacy 2026-09-27 (`1e4a0ba`) with banner comment in `main.py`. Decision: leave in place (harmless, no callers); no deletion needed.


The 6 `/api/assessment/*` routes we auth-gated on 2026-09-26 have no
frontend callers. Grep of all templates + static/js confirms zero usage:
- POST /api/assessment/versant/start
- POST /api/assessment/mcq/generate
- POST /api/assessment/mock-drive
- POST /api/assessment/skill-gap
- GET  /api/assessment/companies
- GET  /api/assessment/scorecard/{email}

Real usage is via different prefixes:
- `/api/versant/*` (5 routes) — versant.html
- `/api/mock/*` (3 routes) — companies.html
- `/api/mcq/questions/*` — mcq.html
- `/api/company-patterns/*` — companies.html

The auth gate we added is harmless (no callers to break), but these routes
are likely legacy from an earlier assessment system. Candidate for deletion
in a future cleanup session.

**Verdict:** FLAGGED — cleanup candidate.



### RESOLVED — Mock Drives + Versant routes lack auth (2026-09-26)

**Resolved 2026-09-28.** Fixed 2026-09-26 (`2b972a0`). Added `require_auth_for_email` to 10 routes; frontend `versant.html` + `companies.html` updated to send Authorization header.


**Discovered during:** frontend audit for the assessment cluster.

**The problem:** 9 routes with real frontend callers have no
`require_auth_for_email`. Same IDOR pattern we've fixed across 7 other
clusters today. An authenticated user can charge credits on another user's
email by sending `{"email": "victim@example.com", ...}` with their own token.

| Route | Credits | Frontend caller |
|---|---|---|
| POST /api/versant/start-session | 20 | versant.html:162 |
| POST /api/versant/record-audio | 3 (multipart) | versant.html:301 |
| POST /api/versant/submit-text | 5 | versant.html:335 |
| POST /api/versant/complete | 15 | versant.html:404 |
| GET  /api/versant/sections | — | versant.html:457 |
| POST /api/mock/start-complete | 25 | companies.html:128 |
| POST /api/mock/submit-complete | — | companies.html:195 |
| POST /api/mock/complete-full | — | companies.html:223 |
| GET  /api/company-patterns/{id} | — | companies.html:88 |

**The fix:** same pattern as the 7 clusters fixed on 2026-09-26.
- Backend: add `require_auth_for_email(request, email)` to all 9
- Frontend:
  - `versant.html` — 5 fetches need `Authorization` header; multipart
    (`/record-audio`) needs `headers: {'Authorization': 'Bearer '+authToken}` only
  - `companies.html` — 4 fetches need `Authorization` header + `email` in body

**Must do together.** Adding backend auth without frontend wiring breaks both
features for real users.

**Est:** 45-60 min. Requires careful edits for multipart form data
(versant.html:301) and session-state flow (companies.html).

**Verdict:** SCHEDULED — next session, first task.

### RESOLVED — lms.html minified JS needs manual auth wiring (2026-09-27)

**Resolved 2026-09-28.** Fixed 2026-09-27 (`3cee5c4`). All 9 fetches now send `Authorization: Bearer <token>` + email. Verified by grep 2026-09-28: 10 auth references present.


`templates/lms.html` has 8 single-line minified JS functions, each fetching
a different `/api/lms/*` endpoint. Backend routes are now auth-gated (commit
4d234b5). The frontend still sends no `Authorization` header and no `email`.

The functions are (lines 154–162):
- rateCourse → POST /api/lms/rate
- submitQuiz → POST /api/lms/quiz/submit
- issueCert → POST /api/lms/certificate/issue
- postDiscussion → POST /api/lms/discussion/post
- checkProgress → GET /api/lms/progress/{id}
- getRecommendations → GET /api/lms/recommendations/{email}
- addLesson → POST /api/lms/lesson/add
- requestPayout → POST /api/lms/payout/request
- searchCourses → GET /api/lms/search?query=

Each needs:
- `Authorization: Bearer <token>` header (POST and GET)
- `email:` field added to the JSON body (POST) or used for auth validation (GET)

**Approach:** Manual edit in Notepad, one function at a time. Minified JS is
not safe to batch-patch with regex. Estimated 30-45 min.

**Verdict:** SCHEDULED — manual cleanup session.


---

## C7 PAID-TIER PROGRESS (2026-09-30)

The C7 gap is "product pages that advertise paid tiers but have no
real purchase flow." Building these as credits-based flows, not
separate Razorpay charges. Pattern proven twice.

### Shipped

**AuditBot** (`52fc994`, 2026-09-29)
- One-Time Fix: 600 credits, POST /api/products/auditbot/fix
- Continuous: 400 credits/30d, POST /api/products/auditbot/subscribe
- Both persist to charvak_auditbot_fixes / charvak_auditbot_subscriptions
- Frontend: templates/auditbot.html - real handlers replace notifyMe

**Lock-In Breaker** (`24c9955`, 2026-09-30)
- One-Time Migration: 1000 credits, POST /api/products/lock-in-breaker/migration-plan
- Continuous Protection: 1000 credits/30d, POST /api/products/lock-in-breaker/protection
- Both persist to charvak_lock_in_engagements (tier column)
- Frontend: templates/lock-in-breaker.html - real handlers
- Also: templates/lock-in-breaker-pricing.html became reference-only;
  killed a latent Razorpay flow that charged without server-side record

### Still open

**Micro-Squads** (`1deb4fa`, 2026-09-30)
Different shape: sales-lead flow, not self-serve checkout. At Rs 49,999
a click-to-pay would be unusual.
- Route: POST /api/products/micro-squads/lead
- Table: charvak_micro_squad_leads
- No credit deduction (lead, not paid feature)
- HR notification + user confirmation email
- Frontend: modal lead form, prefilled email, hidden squad_id backref
- CTA appears after free scan completes

**Sessions 6+ - Remaining ~10 C7 templates**
Small (< 1 hr): Marketing AI, Background Verification, Bridge,
Developer Entropy, AI-Slop Quarantine
Medium (1-2 hrs): Design-Token, Geo-Compliance, Agency-Twin,
Team Dashboard, Reverse Staffing, LMS, University
Large (2-4 hrs): Legacy-Shift, Skill-Twin (also needs persistence -
see AA4d)

### Credit-to-INR ratio
1 credit = Rs 0.50 (Pro plan mid-range). Tier credit amounts derived
from the prices shown on the existing templates, not invented.

### Reusable pattern (per template)
1. Migration for the new table
2. Credit keys in FEATURE_CREDITS
3. Engine methods with _ensure_tables() auto-create
4. Routes with require_auth_for_email + require_credits_from_data
5. Frontend: esc() helper, real fetch, 401/402 handling, render inline
6. Verify E2E via curl + DB check
7. Commit

This has now worked identically for AuditBot (2 tiers) and
Lock-In Breaker (2 tiers).


---

### RESOLVED — duplicate `_call_openai_json` in ai_internship_engine.py (2026-09-28)

**Resolved 2026-09-28.** Fixed 2026-09-28 (`69ce767`). Wasn't just shadowing — the curriculum-designer prompt was being replaced by the mentor prompt at 3 call sites. Renamed mentor version to `_call_openai_json_mentor`; restored correct behavior.


Two definitions of `_call_openai_json` now exist in `ai_internship_engine.py`:
- Line 249 — original, used by `_generate_rich_scenario` (curriculum designer prompt, temp 0.6, regex fence strip)
- Line 743 — new, used by `_evaluate_submission_ai` (mentor prompt, temp 0.4)

Python keeps the last definition, so the line 249 version is **shadowed**. Both
work in practice because the shadowed one is never called — but it is dead code
and a maintenance hazard (edit the wrong one, changes silently ignored).

**Fix:** consolidate into a single helper that takes a `temperature` and
`system_prompt` argument, then delete both originals. ~15 min. Low priority.

**Verdict:** FLAGGED — cleanup candidate


### RESOLVED — bridge.html premium flow broken (2026-09-27)

**Resolved 2026-09-28.** Fixed 2026-09-27 (`d116dc6`). Replaced POST to nonexistent `/api/bridge/premium` with `notifyMe()` interest capture.


`templates/bridge.html:200` posts to `/api/bridge/premium` after Razorpay
verification. **That route does not exist in main.py.** The fetch will 404.

Options:
- (a) Delete the premium flow from bridge.html if the feature is abandoned
- (b) Add the `/api/bridge/premium` route if the feature should ship
- (c) Redirect to `/api/ai-bridge/premium` (which does exist)

**Note:** `bridge.html` and `ai-bridge.html` are two different products. The
premium flow on bridge.html was likely copy-pasted from ai-bridge without
updating the endpoint. Decide intent, then fix.

**Verdict:** FLAGGED — product decision required.

---

### REFERENCE — auth wiring status by cluster (2026-09-27)

**Reference 2026-09-28.** Status table — not an open item. All clusters verified by 2026-09-27.


After this session:

| Cluster | Backend | Frontend |
|---|---|---|
| AI Tools Suite (13) | ✅ | ✅ |
| Voice-to-Web | ✅ | ✅ |
| Student Suite | ✅ | ✅ |
| FYP | ✅ | ✅ |
| 11 AI Products | ✅ | ❌ (10 need forms — separate project) |
| AI Bridge | ✅ | ✅ |
| Bridge | ✅ | ✅ (except premium flow) |
| Marketing AI | ✅ | ✅ |
| Indian Language AI | ✅ | ✅ |
| Interview Prep | ✅ | ✅ |
| LMS AI | ✅ | ❌ (lms.html — see above) |
| Assessment | ✅ | Unknown — needs audit |

**Remaining unverified cluster:** Assessment engines (6 routes: start_versant,
generate_mcq, start_mock_drive, analyze_skill_gap — auth-gated backend, but
frontend templates not yet audited).

**Verdict:** Assessment frontend audit → SCHEDULED.

### RESOLVED — 11 product templates: frontend wiring required (2026-09-26)

**Resolved 2026-09-28.** Completed 2026-09-27 (sprint `7f178b9` through `37df5b1`). All 11 templates now have real forms + AI calls + results render. Verified by grep 2026-09-28: every template has both a `fetch('/api/products/...` call and a `notifyMe(` premium-tier upsell.


**Backend status: DONE** (commit `abbcabe`). All 11 `/api/products/*` routes have
`require_auth_for_email` + `require_credits_from_data`. Verified E2E for auditbot:
real AI output, single credit deduction, 401 without auth.

**Frontend status: 10 of 11 are notify-me stubs.**

| # | Product | Route | Frontend state |
|---|---|---|---|
| 1 | Lock-In Breaker | /api/products/lock-in-breaker/audit | notify-me |
| 2 | Reverse Staffing | /api/products/reverse-staffing/match | real fetch (no auth) |
| 3 | AuditBot | /api/products/auditbot/scan | notify-me |
| 4 | Skill Twin | /api/products/skill-twin/assess | notify-me |
| 5 | Micro Squads | /api/products/micro-squads/assemble | notify-me |
| 6 | Agency Twin | /api/products/agency-twin/automate | notify-me |
| 7 | Geo Compliance | /api/products/geo-compliance/check | notify-me |
| 8 | Design Token | /api/products/design-token/check | notify-me |
| 9 | Silent Killer | /api/products/silent-killer/monitor | notify-me |
| 10 | AI Slop | /api/products/ai-slop/scan | notify-me |
| 11 | Developer Entropy | /api/products/developer-entropy/score | notify-me |

**This is a product decision, not a bug.** The templates were deliberately left
as interest-capture during Session G6. To ship each product, decide per-product:

- **(a) Ship real form** — replace demo UI with real inputs, wire fetch with
  auth header + email, render return shape. ~30-60 min per product.
- **(b) Keep notify-me** — no code change. Backend route stays dormant until
  product is prioritized.

**Recommended order (highest commercial value first):**
1. AuditBot — security scan, clear value prop, engine output tested
2. Lock-In Breaker — cloud cost savings, enterprise buyer
3. Reverse Staffing — has partial UI already

**Est (if shipping all 10):** 5-8 hours, multi-session. Do as a focused
product sprint, not bolt-on fixes.

**Verdict:** SCHEDULED — product sprint session(s). Backend is ready; frontend
is the only work.

### FYP ROADMAP — planned enhancements (logged 2026-09-26)

Current FYP has 4 features working: topics, proposal, documentation outline,
viva questions. The audit/fix on 2026-09-26 made them auth-gated + credit-charged
and verified E2E.

The following are **product enhancements**, not bugs. Sized and prioritized.

---

#### 1. Viva Answers (30 min) — RECOMMENDED FIRST

**What:** Viva questions currently return only question text. Extend to return
question + model answer per item, rendered as collapsible cards.

**Why:** Students preparing for viva don't just want questions — they want
model answers to compare against. This is the single highest-value
per-credit-improvement feature.

**Backend:**
- Modify `final_year_project_engine.generate_viva_ai()` prompt:
  - OLD: `{"questions": [...], "tips": [...]}`
  - NEW: `{"questions": [{"q": "...", "a": "..."}], "tips": [...]}`
- Handle legacy shape in frontend (backward compat)

**Frontend:**
- Each question renders as a card with "Show answer" toggle
- Answer text uses the same safe-escape pattern as student-suite

**Credit cost:** unchanged (10 credits) OR bump to 20 to reflect added value.
Recommend bump to 20 — it's a genuinely deeper deliverable.

---

#### 2. Per-Chapter Content Expand (1.5 hrs) — RECOMMENDED SECOND

**What:** `generate-documentation` returns a chapter outline. Each chapter
becomes clickable → fetches full chapter content via a new lazy endpoint.

**Why:** Documentation outline is useful as an index; students need actual
content per chapter. Option B (lazy) keeps cost linear with depth used.

**Backend:**
- New engine method: `expand_chapter_ai(topic, chapter_title, chapter_outline)`
- New route: `POST /api/fyp/expand-chapter` with `require_auth_for_email` +
  `require_credits_from_data(data, "fyp_expand_chapter")`
- New credit key: `fyp_expand_chapter` (10 credits)

**Frontend:**
- Each chapter row gets an "Expand" button
- On click → fetch → replace outline with full content
- Cache expanded content in DOM (don't re-fetch on re-render)

**Schema:** none — no new tables needed.

---

#### 3. Milestone / Timeline Roadmap (45 min)

**What:** New tab "Project Roadmap" returns week-by-week plan for the entire FYP.

**Why:** Students don't know how to sequence work. A 6-8 week plan with
weekly deliverables is high-value and cheap to generate.

**Backend:**
- New engine method: `roadmap_ai(topic, duration_weeks)`
- New route: `POST /api/fyp/roadmap`
- Credit key: `fyp_roadmap` (15 credits)

**Frontend:**
- New tab/panel in the FYP page
- Simple form: topic + duration
- Render week cards with milestones

---

#### 4. Refine Section — interactive rewrite (2 hrs)

**What:** After a chapter is expanded, user types an instruction ("make formal",
"add examples", "shorten") and AI returns the revised text.

**Why:** Turns one-shot generation into collaborative editing. This is where
FYP becomes a *workflow* product, not a *generator*.

**Backend:**
- New engine method: `refine_section_ai(current_text, instruction)`
- New route: `POST /api/fyp/refine-section`
- Credit key: `fyp_refine_section` (5 credits per instruction)

**Frontend:**
- Text area + chat-style UI in each expanded chapter
- History of refinements preserved in DOM
- "Revert to previous" button

---

#### 5. Plagiarism-Safe Rewriter (1 hr)

**What:** Rewrites AI-generated content in the student's own voice to avoid
AI-detection tools.

**Why:** Biggest anxiety for students. Natural paid add-on.

**Backend:**
- New engine method: `humanize_text_ai(text)`
- New route: `POST /api/fyp/humanize`
- Credit key: `fyp_humanize` (15 credits)

**Frontend:**
- "Humanize this chapter" button on each expanded chapter

---

#### 6. Citation Helper (30 min)

**What:** Extracts key concepts from a chapter and generates IEEE/APA/MLA
references for each.

**Why:** Citations are the #1 formatting headache for students.

**Backend:**
- New engine method: `citations_ai(topic, chapter_content)`
- New route: `POST /api/fyp/citations`
- Credit key: `fyp_citations` (8 credits)

---

#### 7. Viva Simulator — chat mode (3 hrs)

**What:** Chat-style viva practice. AI asks questions, evaluates answers,
gives a mock score, escalates based on performance.

**Why:** Premium tier feature. Requires session state (DB table for progress).

**Backend:**
- New table: `charvak_fyp_viva_sessions`
- New engine methods: `start_viva_session()`, `answer_viva_question()`, `end_viva_session()`
- New routes: `POST /api/fyp/viva-session/{start,answer,end}`
- Credit key: `fyp_viva_simulation` (20 credits per session)

**Frontend:**
- Chat UI page

**Deferred:** larger scope, better as its own session.

---

### Monetization recommendation (logged for discussion)

Shift FYP from subscription-only to credits + optional subscription:

| Feature | Credits |
|---|---|
| Suggest topics | 5 |
| Generate proposal | 15 |
| Documentation outline | 30 |
| Expand chapter | 10 (new) |
| Viva Q&A | 20 (bumped from 10) |
| Roadmap | 15 (new) |
| Refine section | 5 (new) |
| Humanize | 15 (new) |
| Citations | 8 (new) |
| Viva simulation | 20/session (new) |

Keep subscription tiers as "power user" bundles:
- Starter top-up: 100 credits / ₹99
- Student pack: 500 credits / ₹399
- Pro pack: 1500 credits / ₹999

Rationale: typical student journey ≈ 135 credits (~₹80-100 in credits).
Subscription at ₹299 is overkill for most. Credits capture more spend across
price-sensitive students.

### Recommended sequence
1. Viva Answers (30 min)
2. Per-Chapter Expand (1.5 hrs)
3. Milestone Roadmap (45 min)
4. Everything else by user demand

### Verdict
- Viva Answers + Per-Chapter Expand: **SCHEDULED** — next FYP session
- Roadmap: **SCHEDULED** — follow-up
- Rest: **FLAGGED** — pick by user feedback
- Monetization shift: **DISCUSSION** — no code change until you decide

### REFERENCE — AI feature verification sweep — full list (2026-09-26)

**Reference 2026-09-28.** Full-sweep checklist — superseded by the 2026-09-27 individual verifications. Kept as reference for what was checked.


Tonight we audited + fixed:
- Voice-to-Web (auto-deploy) ✅
- AI Tools Suite (13 routes + 9 templates) ✅
- Student Suite (2 assist routes + template) ✅

Still uninspected — same class of bug risk:

| Area | Routes | Engine | Frontend |
|---|---|---|---|
| Final Year Project | 4 | final_year_project_engine.py | final-year-project.html |
| 11 AI Products | 11 | products_engine.py | 11 templates |
| AI Bridge | 3 | ai_bridge_engine.py | ai-bridge.html, bridge.html |
| Marketing AI | 3 | marketing_ai_engine.py | marketing-ai.html |
| Indian Language AI | 2 | indian_language_ai.py | indian-language-ai.html |
| Interview Prep | 2+ | interview_prep_engine.py | interview-*.html |
| LMS AI | 8+ | lms_engine.py | lms.html |
| Assessment engines | 8+ | multiple | several templates |

For each:
- [ ] Route has require_auth_for_email
- [ ] AI wrapper (which one?) uses httpx, not requests.Session(timeout=)
- [ ] AI wrapper uses response_format={"type":"json_object"} where JSON expected
- [ ] Frontend sends Authorization + email
- [ ] Frontend function definitions exist (not just referenced)
- [ ] E2E: browser test passes, real AI output, one credit deduction

Est: 4-6 hours for full sweep. Schedule as multi-session work.

Verdict: SCHEDULED — highest-value cleanup remaining.


### RESOLVED — student_suite auth gap (2026-09-26)

**Resolved 2026-09-28.** Fixed 2026-09-28 (`657d1ce`). Added `require_auth_for_email` to `/api/student/subscribe` and `require_admin` to `/api/student/stats`.


`/api/student/assignment` and `/api/student/research` now call
`require_auth_for_email` (fixed in Phase 3 of tonight's session).

Still missing: `/api/student/subscribe` has NO auth check. Anyone can create a
subscription row for any email. Same IDOR pattern.

Also `/api/student/stats` has NO auth — leaks global subscription/usage counts.

Fix: add `require_auth_for_email(request, email)` to subscribe, and
`require_admin(request)` to stats. ~5 min.

Verdict: FLAGGED — small follow-up

### RESOLVED — uvicorn reload invalidates browser tokens (2026-09-26)

**Resolved 2026-09-29 (commit f58e63f).** Persisted to `charvak_auth_tokens`. Verified: log in -> restart uvicorn -> same cookie returns 200.

`auth.active_tokens` is in-memory. Every `uvicorn --reload` restart wipes it.
Browser localStorage keeps the stale token, causing 401/403 on every API call
until the user clears localStorage and logs in again. Confusing during dev.
In production (long-running process) this only happens on deploy.

Possible fixes (future):
- Persist tokens to DB with expiry
- Add a frontend handler that auto-clears localStorage on repeated 401
- Dev-only: warn on reload that tokens are invalidated

Verdict: DEFERRED — low priority for prod, annoying for dev.

### RESOLVED — ai_service/generate_* functions still unverified (2026-09-26)

**Resolved 2026-09-28.** Resolved 2026-09-27 (`55dd435` + `8592d19`). 4 more functions received `json_mode` + fence-stripping; all 6 verified E2E.


Already in tracker from earlier tonight. 5 functions routed through
ai_service.call_openai() have not been E2E-tested since the fix:
- neural_wireframe_to_code
- localize_website
- generate_legal_contract
- analyze_legacy_code
- generate_assessment_questions

Verdict: SCHEDULED — own session

### RESOLVED — 11 AI Products need same audit as tools (2026-09-26)

**Resolved 2026-09-28.** Fixed 2026-09-26 (`abbcabe`). Added `require_auth_for_email` to 11 `/api/products/*` routes; verified E2E.


- **Trigger:** Tonight we audited and fixed the 12-tool AI Tools Suite
  (`/api/tools/*`). The same class of bug exists in the 11 AI Products
  (`/api/products/*`) but has never been verified.

- **Products in scope:**
  1. product_lock_in_breaker — /api/products/lock-in-breaker
  2. product_reverse_staffing
  3. product_auditbot_scan
  4. product_skill_twin
  5. product_micro_squads
  6. product_agency_twin
  7. product_geo_compliance
  8. product_design_token
  9. product_silent_killer
  10. product_ai_slop
  11. product_developer_entropy

- **Suspected issues (same as tools had):**
  - No `require_auth_for_email` — anyone with a valid token can charge anyone
  - Unknown whether the AI calls go through `ai_service.call_openai` (was broken
    until commit bd41ab9) or `tools_ai_backend.call_ai` (broken until 3d1fb36)
    or their own client — each needs a live test
  - Frontend templates at `/products/*.html` may not send auth headers
  - Fallback dicts may be hiding broken AI calls (same pattern as tools)

- **Verification checklist per product:**
  - [ ] Route has `require_auth_for_email`
  - [ ] Route has `require_credits_from_data` (already present per grep)
  - [ ] AI function returns real output, not canned fallback
  - [ ] Frontend sends `Authorization` + `email`
  - [ ] E2E via browser: real output, one credit deduction

- **Est:** 1-2 hours for full audit + patch + verify.
- **Priority:** Medium-High — same revenue leak + trust issue as tools.
- **Verdict:** SCHEDULED — own session

### RESOLVED — Post-ai_service-fix verification sweep (2026-09-26)

**Resolved 2026-09-28.** Resolved 2026-09-27 (`8592d19`). Full sweep complete — 6 functions verified.


- **Trigger:** Fixed `ai_service.call_openai()` tonight. It had been silently
  failing on every call since the file was written. Six functions route through it.
  We only E2E-verified `voice_to_website()`. The other five are unknown.

- **Scope:**
  1. `neural_wireframe_to_code` — call it, confirm non-empty output
  2. `localize_website` — call it, confirm non-empty output
  3. `generate_legal_contract` — call it, confirm non-empty output
  4. `analyze_legacy_code` — call it, confirm non-empty output
  5. `generate_assessment_questions` — call it, confirm non-empty output

- **Extended scope (same class of bug, never verified):**
  1. `tools_engine.py` — scope audit (never done per inventory #80)
  2. All 12 AI Tools (`/tools/*`) — backend route exists? AI call works? credits charge?
  3. `student_suite_engine.assist_assignment` / `assist_research` — real AI or stub?
  4. `enhanced_assessment_engine.py` — active or legacy? (inventory #83)
  5. `chatbot_engine.py` — AI JSON mode present? (inventory #84)
  6. Repo-wide grep for `requests.Session(timeout=` — find every copy of tonight's bug
  7. Repo-wide grep for `openai.chat.completions` (or `.chat.completions`) — every
     direct OpenAI call site needs `response_format={"type":"json_object"}` if it
     expects JSON

- **Est:** 2-3 hours for a thorough pass.
- **Priority:** Medium-High. The AI Service fix proves that "code-reviewed" is not
  the same as "verified working." We don't know what else is silently failing.

- **Verdict:** SCHEDULED — own session

### RESOLVED — Voice-to-Web hardcodes USD in generated prices (2026-09-26)

**Resolved 2026-09-28.** Fixed 2026-09-27 (`dcc6a63`). Prompt anchored to INR.


- **Symptom:** A user describing an Indian business (Bangalore yoga studio, +91 phone,
  Indian address) received a generated site with prices shown as `$15` instead of `₹15`.
- **Cause:** `ai_service.voice_to_website()` prompt says `services: list of objects with
  keys "name" and "price"` — no currency anchor. `gpt-4o-mini` defaults to `$` for
  unmarked "price" fields.
- **Quick fix (Option A):** one-line prompt change in `ai_service.py`:
    `- services: list of objects with keys "name" and "price" (prices in Indian Rupees, format as "₹1,500")`
  Ships in 5 minutes, no new code paths. Honest short-term patch.
- **Proper fix (Option C — region-aware):** anchor currency to the caller's region.
  - Frontend already detects region via `/api/region` (returns `{country, currency}`)
  - Pass `country_code` (or currency symbol) through the API call
  - Prompt becomes `(prices in {currency_name}, format as "{symbol}1,500")`
  - Requires: frontend change (voice-to-web.html sends `country_code`), route change
    (`/api/ai/voice-to-web` forwards it to `voice_to_website()`), prompt change.
  - Est: ~30-45 min once you sit down to it.
- **Verdict:** DEFERRED — quick fix Option A to ship in a follow-up session;
  full Option C to land as a dedicated follow-up. Same pattern as the `PAYMENT_MODE`
  footgun: flag, fix minimally, do the full version when there's appetite.

### RESOLVED — `email_verification.is_verified()` bare except (2026-09-26)

**Resolved 2026-09-28.** Fixed 2026-09-26 (`63a7672`). Added exception logging before returning False.


- **File:** `email_verification.py` line ~134
- **Original code:** `except:` with no exception class, no logging.
- **Consequence:** any error inside `is_verified()` (DB connection issue, pool
  exhaustion, etc.) silently returns `False`. Users see "verify your email" even
  when their verification row exists. This wasted ~30 minutes during Option 2 E2E
  debugging — the exception was hidden and we assumed the row was missing.
- **Status:** FIXED this session (`refactor(email_verification): log exception in
  is_verified instead of swallowing it`). `except Exception as e:` now logs the
  exception type and message before returning `False`.
- **Not fixed (adjacent):** other bare/blanket `except` blocks may exist in the
  codebase. Worth a repo-wide grep for `except:` and `except Exception:` followed
  by `return` with no logging. Same class of bug as the AI JSON parsing issues in
  `ai_service.py` (silent swallow on parse failure).

### RESOLVED — Voice-to-Web Option 2 — auto-deploy infrastructure (2026-09-28)

**Resolved 2026-09-28.** Infrastructure shipped 2026-09-26 — html_content + slug columns, /sites/{slug} route, real URL, two-call frontend. Flag never updated. Session 2026-09-28 (commit 45ec344) added My Websites dashboard + GET /api/voice-to-web/my-sites/{email} + copy cleanup + data cleanup. Verified: goa-surf-shop, bangalore-yoga-studio, cozy-cafe all render.

- **Trigger:** Model A shipped as concierge beta. Website drafts are generated and stored,
  but the returned URL (`https://{business-name}.charvakit.com`) is computed-only and does
  not serve anything. Delivery is currently manual (team emails the draft).
- **What Option 2 needs to build:**
  - Add `html_content TEXT` column to `charvak_voice_to_web_sites`
  - Wire `voice_to_website()` output into `create_website()` — store the generated HTML
  - Public route `GET /sites/{slug}` that serves the stored HTML with proper caching
  - Change returned URL from fake subdomain to `/sites/{slug}` — no DNS needed
  - Optional: wildcard DNS `*.charvakit.com` → Render with Host-header routing
  - Update copy back to "Live in 3 minutes" once it's real
- **Effort:** 2–4 hours (real product work — deserves its own session)
- **Verdict:** SCHEDULED — separate session

### Voice-to-Web — Model A shipped as concierge beta (2026-09-25)

- **Commit:** <hash>
- **What shipped:**
  - **Frontend rewrite of `voice-to-web.html`:** removed the ₹499/mo Pro card and the broken
    Razorpay flow. Replaced with a single "Start Free" CTA that runs the correct two-call
    sequence:
    1. `POST /api/ai/voice-to-web` → generate HTML content (free)
    2. `POST /api/voice-to-web/create` → create DB record (30 credits)
  - **Engine:** removed `plan != 'pro'` gate from `setup_custom_domain`, `enable_ai_seo`,
    and `request_update`. Credits (enforced by route guards) are now the sole gate.
  - **Add-ons documented on-page:** Custom domain (5cr), AI SEO (8cr), Update (5cr),
    Support (3cr)
  - **Copy repositioned as "Concierge Beta"** — honest about the current delivery model:
    AI generates a draft, team emails it within 24 hours, then deploys on approval.
  - **Beta form** now posts to `/api/features/notify`
- **What was broken (audited):**
  - Free path called `/api/ai/voice-to-web` with `{email, plan}` → Pydantic 422. No site created.
  - Pro path called the same route after Razorpay capture → 422. **Users who paid ₹499 got
    nothing.**
  - `plan != 'pro'` gate meant even a successful payment wouldn't unlock features.
- **Model decision:** Voice-to-Web is **credits-only**. No subscription.
- **Verified:**
  - Two-call sequence works in test script
  - All 5 credit-gated features reachable after 30-credit site creation
  - Support at 2 remaining credits → **402** — proves credit gate is the gate
- **HEAD after:** <hash>

### Voice-to-Web monetization — Model A decision (2026-09-25)

- **Current state (audited):**
  - 5 credit keys defined and enforced: `ai_voice_to_web` (30), `voice_to_web_domain` (5),
    `voice_to_web_seo` (8), `voice_to_web_update` (5), `voice_to_web_support` (3)
  - `voice-to-web.html` has both a "Free" card and a "Pro ₹499/mo" card
  - Frontend's Free path calls `/api/ai/voice-to-web` (the AI generation route) instead of
    `/api/voice-to-web/create` (the record creation route) — so the call doesn't create a
    website record
  - Frontend's Pro path: Razorpay → verify → calls `/api/ai/voice-to-web` with
    `{plan:'pro', payment_id}` — wrong endpoint again, and the AI route doesn't read those
    fields. **Pro users pay ₹499 and get nothing.**
  - The engine's `plan != 'pro'` gate on domain/SEO/update/support means Pro features are
    unreachable even for users who paid
  - **Effectively: monetization is broken in both directions.** Free doesn't create sites.
    Pro charges but doesn't deliver.
- **Product decision (made):** **Model A — Credits only.**
  - Remove the ₹499/mo Pro plan
  - All Voice-to-Web actions cost credits (existing costs stand)
  - Remove the `plan != 'pro'` gate from the engine
  - Fix the Free flow to call `/api/voice-to-web/create`
  - If a "Pro plan" is ever wanted, layer it as a monthly credit bundle via the existing
    credits system — no new billing path
- **Status:** IN PROGRESS — awaiting discovery of `voice_to_website()` return shape
- **Commits:** (pending)

### C2 — voice_to_web_engine persistence (2026-09-25)

- **Commit:** `1675359`
- **What shipped:**
  - **5 new tables:** `charvak_voice_to_web_sites`, `_domains`, `_updates`, `_tickets`, `_seo`
  - **Migration:** `migrations/20260925_voice_to_web.sql` (~3 KB, idempotent)
  - **Engine refactor:** `voice_to_web_engine.py` fully DB-backed — 8 methods, no in-memory state
  - **`_ensure_tables()`** at init — tables created on import even without the migration
  - **Cascade deletes:** child tables use `ON DELETE CASCADE` (domains, seo, updates);
    tickets use `ON DELETE SET NULL` so historical tickets survive site removal
  - **No public signature changes** — `main.py` routes untouched
- **Verified:**
  - All 5 tables populated after E2E test (create → domain → seo → update → ticket)
  - **Cross-restart persistence confirmed:** `get_website_status('V2W-...')` returned
    `success` from a fresh Python process (previously returned `Website not found` —
    data was in RAM only)
  - `get_stats()` returns correct counts
  - Cascade deletes verified (all tables back to 0 rows after cleanup)
- **No WhatsApp dependency** — the engine is a storage layer. `whatsapp_bot.py` is the
  separate input channel (still external-blocked on Meta). Confirmed zero code coupling
  between the two engines.
- **C2 closes the persistence project at 100%:**
  - 62 engines total: 51 DB-backed, 10 stateless (verified skip), 1 external-blocked
  - No remaining in-memory engines
- **HEAD after:** `1675359`
- **Next:** `marketing-ai.html` (last Tier 1 item)

### AA4b — micro-internship.html unblocked + real escrow payment (2026-09-25)

- **Commits:** <hash1> (payments) → <hash2> (micro-internship)
- **What shipped:**
  - **Real payment gate:** `/api/micro-internship/project/post` now requires a verified
    Razorpay `payment_id`. Verifies `status_field == "captured"` and `amount >= budget_inr`
    via `payment_engine.fetch_razorpay_payment()`.
  - **Escrow integration:** backend creates a `charvak_escrow_transactions` row with
    `platform_fee_percent=10.0`, then immediately calls `deposit_funds()` to flip
    status to `funds_held` (payment already captured).
  - **10% intern-side fee:** client pays listed budget, intern receives 90% on release.
    VouchAI's 1% default is preserved.
  - **`escrow_engine.create_escrow` accepts per-call `platform_fee_percent`** — defaults
    to `PLATFORM_FEE_PERCENT` (1.0) when not provided.
  - **`micro_internship_engine.post_project` no longer creates its own escrow** — it
    receives `escrow_id` in `data` from the route and links it to the project row.
  - **Frontend rewrite of `post-micro-project.html`:**
    - Snapshot form values before Razorpay modal opens (DOM is unreliable while modal is up)
    - Email falls back to `localStorage.userEmail` if the field is empty
    - Removed `client_id: 'CLIENT-DEMO'` hardcode
    - Removed localStorage fake-success fallback
    - Budget validated client-side and server-side (minimum ₹500)
  - **`micro-internship.html`:** "Post a Micro-Project" button now links to
    `/post-micro-project` (was `notifyMe()`)
- **Also fixed:** `payment_engine.py` now calls `load_dotenv(".env.local", override=True)`
  + `load_dotenv()` so `RAZORPAY_KEY_ID` resolves even when `payment_engine` is
  imported without `database` first.
- **Verified end-to-end with real Razorpay test keys:**
  - Project `PROJ-20260925-A9BD3138` created, budget ₹500, escrow `ESC-20260925-171DE03D`
    linked, status `open`
  - Escrow `ESC-20260925-171DE03D`: amount ₹500, `platform_fee` ₹50,
    `vendor_payout` ₹450, status `funds_held`
- **Discovered & fixed during E2E testing (five separate bugs that would each have hit prod):**
  1. Form email not pre-filled from localStorage when Razorpay modal opens
  2. `PAYMENT_MODE=test` in `.env` fabricated fake `order_test_*` order ids — Razorpay
     rejected them. Correct value with test keys is `PAYMENT_MODE=live` (Razorpay's own
     test env is selected by the `rzp_test_` key prefix, not by this flag).
  3. Form state invalidated by the Razorpay modal → `finalizeProject` saw empty fields
  4. Budget `parseFloat("")` → `NaN` → `JSON.stringify` → `null` → server 400
  5. Snapshot-based fix for (3) and (4)
- **C7 progress:** 4 of 18 templates complete (events, ats, reports, micro-internship)
- **Follow-ups:**
  - `PAYMENT_MODE` flag semantics are a footgun — either remove the fake-order branch
    entirely or rename to `PAYMENT_MOCK`. Flagged for a future cleanup session.
  - Intern-side release UI (`/api/escrow/release`) still uses admin manual payout path.
- **Next:** C2 — `voice_to_web_engine` persistence (last Tier 1 item)

### fix(ielts) — Speaking results persist under caller email (2026-09-25)

- **Commit:** <hash>
- **Bug:** `evaluate_speaking()` in `ielts_engine.py` persisted to
  `charvak_assessment_results` with a hardcoded `email="anon@charvak.local"`.
  Every user's Speaking result went into one shared bucket — nobody saw their
  own Speaking results in `/my-results`.
- **Fix:**
  - Added `email: str = None` parameter to `evaluate_speaking()`
  - Route `/api/ielts/speaking/evaluate` now passes `data.get("email")`
  - Persist uses `email or "anon@charvak.local"` as fallback
- **Verified:** Dev admin's Speaking eval persists under `hr@charvakit.com`
- **Also corrected:** X5 tracker note claiming Listening/Reading weren't persisted
  was stale — both `evaluate_listening()` and `evaluate_reading()` already call
  `record_assessment_result()` (lines 488 and 658)
- **Status:** RESOLVED

### security(idor) — IDOR sweep + admin hardening (2026-09-25)

- **Commits:** `0abd746` (IDOR) → `2c2651d` (admin)
- **What shipped:**
  - **IDOR fix:** `require_auth_for_email(request, email)` helper in main.py
    - Applied to 34 `GET /api/*/{email}` routes (was: no auth, full user-data leak)
    - Delegates to `require_auth` then checks email match
    - Admins bypass via `ADMIN_EMAILS` set
    - 19 routes had docstrings reordered (auth call must come after docstring, not before)
  - **Frontend:** 12 fetch call sites across 10 templates now send
    `Authorization: Bearer <token>` header
    - base.html, ai_credits_pricing.html, credit_dashboard.html, exam-prep.html,
      interview-dashboard.html, interview-prep.html, my-courses.html,
      my-results.html, referral-dashboard.html, reports.html
  - **Login loop fix:** 401 handler in base.html guards against redirect when already
    on an auth page (login/register/forgot-password/reset-password/verify-email)
  - **Credits nav fetch:** skips request when no auth token in localStorage
  - **Admin hardening:** `role == "admin"` no longer grants admin in 3 places
    - middleware `admin_auth_guard` (line 280)
    - `require_self_or_admin` helper (line 562)
    - `api_login` cookie setter (line 1288)
    - Only `ADMIN_EMAILS = {"charvakit@gmail.com", "hr@charvakit.com"}` grants admin
- **Verified:**
  - `hr@charvakit.com` / `charvakit@gmail.com` are the only 2 admin rows in prod
  - No other code path sets `users.role = 'admin'`
  - Login endpoint works (`POST /api/auth/login` → 200)
- **Follow-ups:**
  - `email_verification.is_verified()` blocks non-admin test accounts. Dev users must be
    verified before login. Consider adding a dev-only bypass flag.
- **C7 progress:** unchanged (3/18)

### RESOLVED — Anti-bot for /contact (2026-09-25)

**Resolved 2026-09-28.** Fixed 2026-09-27 (`80e5b74`). Honeypot field + backend heuristics.


- **Trigger:** Two bot spam submissions found in prod `contacts` table
  - `Vxjoojou Oohmz` / `m.ogz.vp.h.n.5.87@gmail.com` (deleted)
  - `Zfgit Wmevm` / `yar.ivic.id.i9.6@gmail.com` (pending delete)
- **Pattern:** Random consonant-cluster names, dot-separated email local parts,
  10-digit numeric message bodies, "Business / Employer" dropdown
- **Not a breach:** verified admin users (only charvakit@gmail.com + hr@charvakit.com),
  no unauthorized signups, no suspicious credit purchases
- **Fix (do immediately after current work):**
  - Option 1: Honeypot field on `/contact` form (~5 min)
  - Option 2: Cloudflare Turnstile (~15 min) — visible/invisible CAPTCHA
  - Combined: ~20 min
- **Optional stopgap:** message-only-numeric + consonant-cluster regex filters on
  the `/api/contact` POST handler

### N1 follow-up — apex domain 404 (2026-09-24 RESOLVED)

- **Reality:** `charvakit.com` forwards to `https://www.charvakit.com` via GoDaddy
  domain forwarding (Permanent 301). Verified in browser — the redirect works.
- **Why the tracker said "404":** `curl.exe` on Windows fails the TLS handshake
  with GoDaddy's forwarding server (`SEC_E_ILLEGAL_MESSAGE` / schannel error).
  Browsers work fine. This is a local curl issue, not a site issue.
- **Action:** none required. Delete the "apex redirect" follow-up from the tracker.
- **Lesson:** never trust `curl.exe` alone on Windows for TLS verification;
  cross-check in a browser.

### AA4d — skill-twin.html / skill-check.html — REAL SCOPE (2026-09-24)

- **Discovery finding:** `skill-twin.html` and `skill-check.html` are **not** a quick unblock like
  `reports.html`. The engines exist (`products_engine.skill_twin_assess` is real, returns
  `twin_id`, `verified_score`, `badge_eligible`, etc.), but two things are missing:

  1. **No persistence.** `skill_twin_assess` writes nothing to the DB. No `charvak_skill_twin*`
     table exists. Every scorecard is ephemeral.
  2. **Fake payment on `skill-check.html`.** `buyBadge()` calls `alert('Payment successful!')` with
     no Razorpay integration. Badge IDs are generated client-side (`Math.random()`), stored in
     `localStorage`, never sent to the server. `/badge?name=...` is a phantom route.

- **Scope to ship properly:**
  - Phase A — server-side persistence for free check (`charvak_skill_check_results` table,
    `POST /api/skill-check/submit`, rewrite `buyBadge()` to use real Razorpay)
  - Phase B — wire `skill-twin.html`'s ₹499 to the backend
  - Phase C — public verify URL `/badge/{badge_id}` reading from DB
  - Est: ~2.5 hours

- **Verdict:** DEFERRED — dedicated session required. Not a quick unblock.
- **C7 progress:** 3 of 18 templates complete (events, ats, reports)
- **Next candidate:** `agent-ready.html` (₹399, likely single-feature unblock)

### fix(credits) — get_user_credits only auto-creates for registered users (2026-09-24)

- **Commit:** <hash>
- **Bug (Change 2):** `ai_credit_engine.get_user_credits` called `initialize_user` for any email,
  creating a phantom `charvak_user_credits` row (50 free credits) for emails that had never
  registered. Hitting `/api/credits/<random@example.com>` created an account.
- **Fix:** `get_user_credits` now checks `db.get_user_by_email(email)` first. If no `users` row
  exists, return `{'status': 'error', 'message': 'No account found for this email.'}`.
  `check_and_deduct` was already fixed earlier today; this closes the sibling hole.
- **Verified:**
  - Unknown email → error, no DB row created ✅
  - Fresh registered user → 50 free credits ✅
  - Existing user (admin) → unchanged ✅
- **Status:** RESOLVED — credits system now fails closed on both read and write paths

### fix — global 401/402 handlers in base.html (2026-09-24)

- **Commit:** <hash>
- **Bug:** `main.js` dispatched `charvak:401` and `charvak:402` events site-wide, but the only
  listeners lived inside `exam-prep.html`. Every other gated route (reports, ats, etc.) got
  dispatched events into the void. Root cause: `base.html` had a stray `</body>` at line 578,
  pushing the cookie banner and credits-nav script outside `<body>` — nobody noticed the layout
  issue, so nobody added the handlers to `base.html`.
- **What shipped:**
  - Moved both handlers to `base.html` (site-wide)
  - Removed the stray `</body>` — `base.html` now has exactly one closing body tag
  - Deleted duplicate handlers from `exam-prep.html`
  - 401 handler now uses `login_url` from event detail when present, else `/login?next=<path>`
- **Verified:**
  - 402 → alert + redirect to `/ai-credits-pricing` ✅
  - 401 → confirm + redirect to `/login?next=...` ✅
  - `base.html` has exactly 2 handler registrations and 1 `</body>`
- **Status:** RESOLVED

### fix(credits) — check_and_deduct no longer auto-grants free trial (2026-09-24)

- **Commit:** <hash>
- **Bug:** `ai_credit_engine.check_and_deduct` called `initialize_user` for any unknown email,
  silently creating a `charvak_user_credits` row with 50 free credits. Affected all 92
  credit-gated routes. Admin bypass in tests masked the problem.
- **Evidence:** `never-registered-xyz@example.com` received 2 × 25-credit deductions
  with a final balance of 0, generating 2 reports without ever registering.
- **Fix:** `check_and_deduct` now returns 402 (`No account found...`) instead of auto-creating.
  `get_user_credits` still auto-creates for the registered-user flow (navbar call on welcome page),
  so the free-trial grant is unchanged for real users.
- **Verified:**
  - Unknown email on gated route → 402 + alert + redirect ✅
  - Registered user with credits → 200, 25 deducted ✅
  - Admin bypass → still works, 0 deduction ✅
- **Status:** RESOLVED

### V4 — Dev/prod DB isolation (2026-09-24)

- **Commit:** <hash>
- **What shipped:**
  - `database.py` now loads `.env.local` first (with `override=True`), then `.env`
  - `.env.local` (gitignored) points at local Postgres: `charvak_dev` on `localhost:5432`
  - Local Postgres 15 password reset via `pg_hba.conf` trust flip → `ALTER USER` → revert
- **Verified:**
  - With `.env.local`: `SELECT current_database()` → `charvak_dev`
  - Without: → `vouchai` (prod, 144 tables)
- **Rules:**
  - To test against prod data locally: rename `.env.local` → `.env.local.off`, run, rename back
  - Never set `$env:DATABASE_URL` in the shell (V5 trap — shell wins over everything)
  - `.env.local` is gitignored; never commit it
- **Closes:** V4 escalation trigger #2 (safe to onboard a second developer)
- **Verdict:** ✅ RESOLVED 2026-09-24


### AA4c — reports.html unblocked (2026-09-24)

- **Commit:** <hash>
- **Discovery:** `assessment_report_engine.py` was already fully built (12 methods, DB-backed,
  `charvak_assessment_reports` with 3 indexes). Session G6 had added a second `<script>` block
  to `reports.html` that hijacked `generateReport()` → `notifyMe()`. That was the only blocker.
- **What shipped:**
  - Removed G6 hijack script block from `reports.html`; rebuilt layout in clean UTF-8
  - Added `premium_report` credit key (25 cr)
  - Guarded `POST /api/report/generate` with `require_credits_from_data`
  - Fixed `_http_status` key in 2 routes (report generate + ATS score-link)
- **Verified:**
  - Admin bypass: 0 credits used
  - Candidate with credits: 25 deducted, audit row in `charvak_credit_usage_history`
  - Candidate without credits: 402 + upgrade modal ✅
  - Verify endpoint: returns candidate/score/PASS
  - My Reports: returns list
- **C7 progress:** 3 of 18 templates complete (events, ats, reports)
- **Follow-ups:**
  - `main.js:250` renders 401 and 402 identically — split to /login vs upgrade modal
  - `/api/report/candidate/{email}` has no auth — security note for a future session
- **Next:** AA4d — `skill-twin` (check if guard `product_skill_twin` already wired — likely another quick unblock)

### ATS-1 + ATS-2 — Charvak ATS + DoketsRB bridge (2026-09-24)

- **Commits:** `f421303` (ATS-1 bridge) → `a338380` (URL fix) → `721a89c` (ATS-2 dashboard)
- **What shipped:**
  - **ATS-1:** `doketsrb_integration` scoring bridge
    - `request_score_link`, `record_external_score`, `consume_score_callback`
    - Tables: `charvak_doketsrb_score_tokens`, `charvak_doketsrb_score_events`
    - Routes: `GET /api/ats/candidates`, `POST /api/ats/candidates/{id}/score-link`,
      `GET /api/ats/score-callback`, `POST /api/ats/candidates/{id}/score-manual`
    - Credit key: `ats_jd_score` (5 cr, gated when `target_role` is set)
    - Env: `DOKETSRB_SCORE_SECRET`
  - **ATS-2:** `templates/ats.html` full rewrite
    - 4 tabs: Candidates / Integrations / Sync Log / DoketsRB Bundles
    - Filter row (skill / location / min score / min years)
    - Per-row "Get Score Link" → opens `doketsrb.com/#ats-scanner` → prompts for score → writes back
    - Mojibake fixed throughout
- **Verified in prod:** `CAND-FA310E2E` scored 82 → 65, status moves with threshold (`badge_earned` ≥ 70)
- **Bugs fixed during build:**
  - Missing `import time`
  - `request_score_link` line-238 indent (16 → 8)
  - Naive-datetime `.timestamp()` IST shift in expiry → moved to DB-side `AT TIME ZONE 'UTC'`
  - HMAC payload instability — dropped timestamp from signature, now `token:candidate_id`
- **Follow-ups:**
  - Razorpay wiring for ATS bundle purchases (currently "Notify Me")
  - DoketsRB: build `/ats-check` route with `return_url` support to replace manual paste
  - C7 tracker correction: `ats.html` is ATS-integration, not "₹999 resume score"
- **C7 progress:** 2 of 18 templates complete (events + ats)

### Z — Analytics + IELTS polish (2026-09-23)

- **Commits:** `8537db3` `a4565fe` `fe53e3a` `a4dad63` `22a8da8` `311662d` `4d26e36` `f99c42b` + release-notes tag
- **What shipped:**
  - **Z1** — Refined IELTS section metadata (`content_type`, `total_questions_available`)
  - **Z2a** — `/ielts-writing` polish (criteria cards, toggle labels, richer intro)
  - **Z2b** — `/ielts-listening` polish (tab counts, section descriptions, JS-driven)
  - **Z2c** — `/ielts-reading` polish (3 tier cards, exam strategy, tab counts)
  - **Z3a-d** — Real, DB-backed analytics dashboard
    - `admin_metrics_engine.py` (6 metrics)
    - `/admin/analytics` + 5 API endpoints
    - 209-line dashboard page with KPIs, funnel, IELTS bars, tables
    - Analytics link on admin-dashboard
  - **Z4** — Release notes v3.4
- **Verified:** All pages render, live data flows, no console errors
- **Release tag:** `v3.4-polish-and-analytics-20260923`
- **HEAD after:** `f99c42b`

### Y — Marketing polish + Admin + Blog (2026-09-23)

- **Commits:** `f427531` `4ad2219` `64649ac` `9505785` `26b8d63` `f538c08` `57df7a4` `097e429` `f1ec086`
- **What shipped:**
  - **Y1:** Enriched IELTS section metadata (`practice_url`, `content_count`, `subsections`, `available`)
  - **Y2:** Edtech-first homepage (hero + 4 feature cards + value props + business strip), new `/consulting` page, IELTS hub copy enhancements
  - **Y3:** Admin reported-questions page (list + dismiss + delete), tested end-to-end
  - **Y4:** Release notes for v3.3
  - **Y5:** Blog infrastructure
    - `blog_engine.py` — markdown loader with frontmatter parser, contract-compliant with existing routes
    - 8 posts in `blog/posts/` — 3 new IELTS + 5 recovered from git history (AI staffing, US visas, remote hiring, skill gap, escrow)
    - Fixed template rendering (safe filter + `.blog-content` styles)
    - Removed duplicate nav link + 2 orphan templates
- **Verified:**
  - Homepage shows new hero + 4 cards
  - Consulting page loads
  - Admin review page works (dismiss tested)
  - Blog loads with 8 posts across 6 categories
  - Single posts render clean HTML
- **HEAD after:** `f1ec086`

### X5 — IELTS Reading + all-4 sections Listening (2026-09-23)

- **Commits:** `d070c8f` `60b3e81` `32da091`
- **Tag:** `v3.3-ielts-complete-20260923`
- **What shipped:**
  - **Listening expansion:** All 4 sections now seeded (14 total)
    - Section 1: 3 conversations (travel, camping, language course)
    - Section 2: 3 monologues (Riverside Park, City Library, Community Center)
    - Section 3: 3 discussions (Climate Change, Education Tech, Urban Design)
    - Section 4: 5 lectures (Bioacoustics, Microbiomes x2, Microplastics x2)
    - Section selector UI added to `/ielts-listening`
    - Section IDs renamed from `IELTS-L4-*` to `IELTS-L{num}-*` (cosmetic fix)
  - **Reading section (new):**
    - DB tables: `charvak_ielts_reading_passages` + `charvak_ielts_reading_attempts`
    - Seed script: `scripts/seed_ielts_reading.py` (3 difficulty tiers)
    - 9 passages seeded: Coral Reefs, Monarch Butterfly, Honeybees / Urban Health, Urban Ecology / Technology, Tech Ethics, AI
    - Engine methods: `get_reading_passage()`, `evaluate_reading()`
    - Routes: `/ielts-reading` + `/api/ielts/reading/{passage,score}`
    - Credit keys: `ielts_reading_passage` (5), `ielts_reading_score` (10)
    - Frontend: `templates/ielts-reading.html` (276 lines)
- **Verified in prod:**
  - All 4 listening sections load and play
  - All 3 reading passages load with questions + score
  - Band scoring: 10/10 -> 9.0, 0/10 -> 2.0
- **IELTS Suite: COMPLETE** (Listening + Reading + Writing + Speaking)
- **Notes:** Listening/Reading results persist to their own attempt tables but not yet to `charvak_assessment_results` (cross-test dashboard gap)
- **HEAD after:** `32da091`
### X4 — IELTS Listening Section 4 (2026-09-23)

- **Commits:** `62d9f0d` `d9ff133`
- **What shipped:**
  - **DB tables:** `charvak_ielts_listening_sections` (10 cols) + `charvak_ielts_listening_attempts` (8 cols)
  - **Seed script:** `scripts/seed_ielts_listening.py` — generates 5 lectures via AI
    - 5 Section-4 lectures seeded (Bioacoustics, Microbiomes ×2, Microplastics ×2)
    - Each: 420-550 words, 10 MCQs, topic + title
  - **Engine methods:** `get_listening_section()`, `evaluate_listening()`, `_listening_band()`
  - **Routes:** `/ielts-listening` page + `/api/ielts/listening/{section,score}`
  - **Credit keys:** `ielts_listening_section` (5), `ielts_listening_score` (10)
  - **Frontend:** `templates/ielts-listening.html` (371 lines)
    - Audio player + timer
    - 10 MCQ questions with radio options
    - Scorecard: band + review (✓/✗ per option) + explanations
    - Transcript shown after scoring
- **Verified in prod:**
  - Full flow: Load Lecture → Play → Answer → Submit → Band score
  - Band 5.5 for 5/10 correct (scoring works)
  - TTS audio plays (ElevenLabs primary, browser fallback)
- **Notes:**
  - Sections 1-3 not yet seeded (Section 4 only, per scope decision)
  - ElevenLabs TTS handles ~3.7K chars per lecture
- **HEAD after:** `d9ff133`

---

## âœ… COMPLETED

### N1 - State exam smoke test + content quality fixes

- **Completed:** 2026-09-22 (Session N1) - commits `9a8ce83` through `00aec90`
- **Catalog:** `upsc_cse` + `neet_ug` added (136 â†’ 138 exams)
- **Question bank:** 5 state PCS exams topped to 40+ per topic; ~13,600+ rows total
- **Mock test performance:** batched bank query (3 DB calls â†’ 1); 2-4s â†’ 0.4s
- **Connection pool:** `get_pooled_connection()` + `release_pooled_connection()` in `database.py`; `exam_prep_engine` hot paths migrated; startup warmup in `main.py`
- **Language hints:** AI prompt forces correct script for 10 language sections (Bengali, Hindi, Tamil, Telugu, Marathi, Kannada, Malayalam, Gujarati, Punjabi, Urdu)
- **Practice route fix:** `/api/exam/ai-questions` redirected from legacy `ai_question_generator` to `exam_prep_engine` - was serving wrong content for state-specific topics
- **Verified in prod (Render logs):**
  - `[startup] DB connection pool warmed` âœ…
  - `bank lookup: X/Topic -> 10 rows (wanted 10)` for all 5 state PCS exams âœ…
  - Bengali content serves correctly âœ…
  - Credit deduction: 3 cr practice / 15 cr mock âœ…
- **N1.5 Legal audit:** PASSED - all 4 pages render on `www.charvakit.com` (terms, privacy, refund, cookie-policy), plus `accessibility`
- **Follow-ups:**
  - Semantic duplicate questions (near-identical wording across topics) â†’ C13
  - Two engines to consolidate (`exam_prep_engine` vs `ai_question_generator`)
  - Apex domain `charvakit.com` returns 404; optional Cloudflare redirect to `www`

---

### N2 - System-wide semantic dedup (2026-09-22)

- **Commits:** `0ed1110` `b1f6a0d` *(plus N2.5 pending)*
- **What shipped:**
  - **Prompt diversity rules:** `_generate_via_ai` now requires 8+ distinct subtopics per batch
  - **Embeddings:** `embedding vector(1536)` column + `ivfflat` index on `charvak_exam_question_bank`
  - **Backfill:** 13,720 questions embedded via OpenAI `text-embedding-3-small` (~11 min, ~$0.02)
  - **Read-time filter:** `_fetch_bank_questions` + `_fetch_bank_multi` filter by cosine distance < 0.15
  - **Write-time dedup:** seed script's `seed_one` runs `dedup_bank()` after each generation
  - **One-time cleanup:** deleted 1,069 semantic near-dupes (7.8% of bank)
- **Verified:**
  - Bank: 13,720 â†’ 12,651
  - All 10 sampled questions unique per topic
  - Mixed mock serves diverse content
- **Follow-ups:**
  - Consider embeddings for live-AI assessment flows (mock drives, company assessments)
  - Optional: curate top 5 exams manually for extra polish
- **HEAD after:** *(pending commit)*
- **Next:** Session N3 (IELTS Speaking or Onboarding)

### C13 — Curated question banks (pragmatic automated approach)

- **Completed:** 2026-09-23 (partial-complete, pragmatic scope)
- **Commits:** `02a21a4` `92390d4` `eadfb4f`
- **What shipped:**
  - **Layer 1 — `scripts/validate_questions.py`:** deterministic structural validator
    - Checks: option count == 4, correct_index in range, no dup options, no empty options, question text length ≥ 15, explanation present, prefix consistency
    - Deleted **126 truly-broken questions** (69 option_count_8, 33 truncated, 21 dup-options, 3 malformed)
    - **31 false positives eliminated** — smarter `has_prefix` avoids flagging Indian names like "B. R. Ambedkar"
    - Bank: **12,647 → 12,521 valid** (99.86% structurally clean)
    - **Cost: $0, time: 10 seconds**
  - **Layer 2 — `scripts/ai_verify_questions.py` (built but NOT USED):**
    - Batch AI verification via gpt-4o-mini
    - **Test sample:** 2 flags raised, both false positives (100% error rate)
    - Decision: **skip AI content verification** — LLMs unreliable for factual MCQ correctness
  - **Layer 3 — User report system:**
    - Schema: `reported`, `reported_at`, `reported_by`, `report_reason` columns
    - Endpoint: `POST /api/questions/report`
    - UI: "⚠ Report" link next to each question in `exam-prep.html`
    - Verified end-to-end (report → DB row confirmed)
  - **CLI extension — `scripts/review_questions.py`:**
    - Interactive approve/reject/edit/skip/back/quit workflow
    - `--reported` flag for triaging user-reported questions
    - `--exam`, `--topic`, `--limit`, `--random` filters
  - **`.gitignore` housekeeping:** whitelisted C13 scripts (`validate_questions.py`, `review_questions.py`, `ai_verify_questions.py`)
- **Not in scope (deferred):**
  - Full manual review of all 138 exams (diminishing returns; user reports drive ongoing curation)
  - Layer 2 AI verification (unreliable at `gpt-4o-mini`; `gpt-4o` cost-benefit unclear)
  - Admin review UI page (CLI is sufficient for current volume)
- **Verdict:** DEFERRED completion; infrastructure shipped; curation is ongoing via user reports
- **HEAD after:** `eadfb4f`

### W4 — Cross-test results dashboard (2026-09-23)

- **Commits:** `a79555b` `3ff3586`
- **What shipped:**
  - **New page** `templates/my-results.html` (208 lines):
    - Teal gradient hero
    - 4 stat cards: Tests Taken, Average Score, Passed, Needs Practice
    - Filter buttons by assessment_type (dynamic)
    - Result cards: name, score, pass/fail badge, date, "View Details"
    - Details modal with recursive flattening of `details_json`
    - Empty state ("No results yet")
    - Loading + error states
  - **Route:** `GET /my-results` (page)
  - **Nav:** "My Results" button added to logged-in user dropdown
  - **Backend:** No changes — reused existing `/api/results/user/{email}`
- **Verified:**
  - Page loads with 4 stat cards
  - Cards render for `versant` results
  - View Details modal shows sub-bands + feedback
  - Filter buttons work
  - Nav link visible + works
- **HEAD after:** `3ff3586`
- **Notes:** Ready for ielts_speaking + ielts_writing results (already persisted via N4 fixes)

### W1-W2 — Currency detection: two-layer country resolution (2026-09-23)

- **Commits:** `692a0f1` `8b28468` `325cf86` `0830b97`
- **What shipped:**
  - **Root cause fixed:** `detect_user_region` had language→currency map with `"en": "USD"` — every English browser got USD, including Indian users.
  - **Two-layer detection in `ip_detection.py`:**
    - Layer 1: Cloudflare `CF-IPCountry` header (primary — auto-updated weekly by CF)
    - Layer 2: Self-hosted GeoLite2 City MMDB (fallback — lazy refresh if >7 days old)
    - Layer 3: Default `IN` (last resort)
    - Rejects CF invalid codes: `XX` (unknown), `T1` (Tor)
  - **GeoLite2 integration:**
    - `scripts/update_geoip.py` downloads from jsDelivr (no MaxMind license key needed)
    - Build command: `pip install -r requirements.txt && python scripts/update_geoip.py`
    - DB path: `data/GeoLite2-City.mmdb` (~63 MB, gitignored)
    - `data/.gitkeep` committed to preserve the directory
  - **Lazy in-process refresh:** if DB age >7 days, triggers a background re-download + hot-swap on next lookup
  - **Route update:** `/api/region` now uses `ip_detector.detect_from_request(request)` which handles CF header + IP + default in one call
  - **Scripts tracked:** added explicit `.gitignore` exceptions for all production scripts
- **Verified in prod:**
  - Browser console: `{country: 'IN', currency: 'INR', source: 'cf_header'}`
  - Render logs: `GeoLite2 loaded: data/GeoLite2-City.mmdb`
  - Render logs: `IP Location Detector ready (GeoLite2: ENABLED, CF header: enabled)`
- **Why no cron:** Render cron jobs are ephemeral containers with no access to the web service's filesystem. They cannot update the running service's DB. Lazy refresh handles it in-process instead.
- **HEAD after:** `0830b97`

### V — Full Versant rebuild (2026-09-23)

- **Commits:** `62a8d7e` `75386ee` `5038332` `96066c4` `56715e0`
- **What shipped:**
  - **DB schema:** `charvak_versant_sessions` + `charvak_versant_answers`
  - **Engine:** `cbt_versant.py` fully DB-backed (in-memory → Postgres)
    - Kept: 6 section designs (Read Aloud, Repeats, Sentence Builds, Conversations, Story Retelling, Summary & Opinion)
    - New: `create_session`, `get_session`, `save_text_answer`, `save_audio_answer`, `complete_session`
    - Whisper transcription + AI scoring on 5 Versant criteria (20-80 scale)
  - **Routes:** `/api/versant/{start-session, record-audio, submit-text, complete, session/{id}, sections}`
  - **Frontend:** full rewrite of `versant.html` (425 lines)
    - Landing → one-question flow → section transitions → complete → scorecard
    - Progress bar, timer, transcript display
  - **Nav:** Assessments dropdown now links to IELTS Speaking, Versant, Advanced
  - **Whisper hardening:** hallucination filter, language=en, tiny-audio skip
- **Verified:**
  - Session with 30 real answers → score 50.0
  - Transcripts are real English (no hallucination)
  - Cross-persisted to `charvak_assessment_results`
- **Bugs fixed during build:**
  - `get_session` duplicate `status` key → `complete_session` short-circuited
  - Whisper hallucinating Japanese/spam captions on short/silent audio
  - Frontend swallowing real error messages
  - Broken `/ielts` nav link (route doesn't exist)
- **HEAD after:** `56715e0`
- **Next:** IELTS Writing/Listening/Reading landing page (currently API-only)
### N3 — Onboarding + GA4 + welcome email sequence (2026-09-22)

- **Commits:** `9dc76c4`, `bad2ad9`
- **What shipped:**
  - **GA4 funnel events:** `charvakTrack` helper + `sign_up`, `first_assessment_start`, `notify_me_click`, `onboarding_viewed`
  - **`/welcome` onboarding page:** 3 CTA cards + 50-credit banner; new users land here after register
  - **Register redirect:** `/login` → `/welcome`
  - **Welcome email:** `enhanced_email.send_welcome()` called on register
  - **Email queue:** `charvak_email_queue` table + `email_queue.py` module
  - **Delayed emails:** `nudge_first_assessment` (24h) + `cta_credits_expire` (72h)
  - **Cron endpoint:** `/api/cron/send-queued-emails` (X-Cron-Secret auth)
  - **Render cron:** every 15 min
- **Verified:**
  - Signup → welcome email delivered
  - 2 queue rows per signup (24h + 72h)
  - Cron endpoint returns `sent:4, failed:0` on due emails
  - DB confirms `sent_at` + `status='sent'`
  - GA4 events fire (console shows `[GA4] sign_up`, `[GA4] onboarding_viewed`)
- **Follow-ups:**
  - localStorage `userEmail`/`userName` not set on register (minor UX)
  - Currency auto-detected as USD for some users (region detection issue)
  - Mojibake in register.html (`âœ…` vs `✅`, `â€”` vs `—`) — cosmetic
- **HEAD after:** `bad2ad9`

### C1 - Assessment AI for global languages

- **Completed:** 2026-09-21 (Session G1) - commit `c3dc68a`
- **Discovered:** 2026-09-20 (audit was wrong; corrected 2026-09-20)
- **Reality:** `global_config.LANGUAGES` has 34 languages âœ… (config complete)
- **Real gap fixed:** `indian_language_ai._generate_questions` only handled 12 Indian languages.
  Spanish, French, German, Japanese, etc. users got English/Hinglish assessment questions.
- **What shipped:**
  - `LANG_NAME_FOR_PROMPT` (36 languages) for AI prompt naming
  - `LANG_META()` resolver: INDIAN_LANGUAGES â†’ global_config.LANGUAGES â†’ fallback
  - Silent-Hindi bug fixed in BOTH `create_assessment` AND `translate_job_ad`
  - Static fallback guard: non-Indian returns `[]` instead of Hinglish default
  - `_generate_questions_via_ai` now serves all 34 languages
- **Verified:** live OpenAI smoke test - es/fr/ja/ar/zh/hi/te/ta/ko/de all
  returned native-script questions (5 each)
- **Note:** `_generate_questions_static` deliberately still covers only 12 Indian
  languages. Non-Indian + AI failure returns `[]`, so caller falls back explicitly.

---

### C4 - Adaptive difficulty

- **Completed:** 2026-09-21 (Session G2) - commit `15193f9`
- **What shipped:**
  - New `charvak_user_ability` table (migration + engine self-init)
  - New `ability_engine.py` - Elo math, `get_ability`,
    `update_from_assessment`, `get_recommended_difficulty`, `recommend_difficulty`
  - `results_system.record_assessment_result` accepts optional `skill=`;
    when set, updates ability post-insert (non-fatal on failure)
  - `complete_mock_drive.complete_mock` passes `skill=mock_{company_id}`
  - `enhanced_assessment_engine.create_custom_assessment` and
    `generate_topic_questions` accept `email=` and use ability-recommended
    difficulty when caller omits it
  - `main.py` routes `/api/enhanced/*` forward `difficulty` + `email`
- **Verified:**
  - Local Elo math (8/10 â†’ +7.2, 2/10 â†’ âˆ’7.45)
  - Prod table exists with all columns + PK `(email, skill)` + 2 indexes
- **Not in scope (Phase 2):** mock drives still generate at fixed difficulty.
  Ability only read by `/api/enhanced/*` today.
- **Backwards compatible:** existing callers see no behavior change.


### C5 - Curated question banks

- **Completed:** 2026-09-21 (Session G3) - commit `f4a3fd3` + local seed run
- **What shipped:**
  - New `scripts/seed_exam_question_bank.py` - idempotent, resumable,
    throttled batch generator for `charvak_exam_question_bank`
  - Phases: `--phase 1` (top 10 exams, ~35 pairs), `--phase 2`
    (all 67 Indian exams, 207 pairs)
  - `--resume` skips pairs already at target count
  - Runs through `exam_prep_engine.generate_questions` - same path
    users hit, no parallel write paths
- **Verified (local):**
  - Phase 2: **207/207 pairs succeeded** in 5281s (88 min)
  - Bank now: **12,892 rows** across 67 exams, 43 distinct topics
  - **207/207 pairs cache-eligible** (â‰¥30 questions)
  - Average 62 questions/pair (target 50; OpenAI variance + top-up)
- **Known limitations:**
  - `jssc/Math` had 30 stub rows from OpenAI timeout during batch;
    re-generated to 42 real questions.
  - `global_exams_engine` excluded (no `generate_questions` method yet)
  - Runtime 88 min vs 33 min estimate - OpenAI averaged ~25s/call
- **Backwards compatible:** no user-facing code changes.

---


### C6 - Assessment UI translations

- **Completed:** 2026-09-21 (Session G5) - commits `fa83917` through `acd450e`
- **What shipped:**
  - **`static/js/i18n.js`** - client-side loader (~5.5 KB)
    - Language priority: localStorage â†’ `window.CHARVAK_LANG` â†’ Accept-Language â†’ `en`
    - Replaces `[data-i18n]`, `[data-i18n-placeholder]`, `[data-i18n-title]`
    - Exposes `window.changeLanguage()` + `window.t()` for programmatic use
    - Graceful fallback: missing keys render English
  - **`static/locales/en.json`** - 278 source strings across 16 groups
  - **17 language files** - hi, te, ta, kn, ml, mr, bn, gu, pa (Indian);
    es, fr, ar, zh, de, pt, ru, ja (Global)
  - **`scripts/translate_ui.py`** - batch translator (OpenAI gpt-4o-mini, temp 0.2)
  - **~197 data-i18n attributes** across 7 templates:
    - `base.html` - 90 (nav, footer, topbar, user menu)
    - 6 assessment templates - ~107 (reports, advanced-assessment,
      assessments, custom-assessment, mcq, exam-prep)
- **Fixed as part of G5:** base.html had double-encoded UTF-8 in 17
  language <option> values. Replaced from `global_config.LANGUAGES`.
- **Scope boundary:** static HTML only. JS-injected strings (innerHTML,
  template literals) deferred to a follow-up session.
- **Backwards compatible:** pages render English by default.


### C7-AA4a — Events paid tier (2026-09-24)

- **Commits:** `3de2d13` `96177f7` `2684720` `fc46ac7` `5e19057` `d9c197f`
- **What shipped:**
  - **Schema:** `charvak_events.price_inr`; `charvak_event_rsvps.tier`, `paid`, `payment_id`
  - **Engine:** `events_engine.rsvp_paid()` (idempotent, verifies `price_inr > 0`, writes RSVP with payment_id)
  - **Route:** `POST /api/events/rsvp-paid`
  - **Frontend:** tier selector (Free / ₹499 Pro), Razorpay modal integration, real user data from localStorage
  - **Currency:** local conversion using `CharvakCurrency` helper (INR → USD/EUR/GBP/...)
  - **Symbols:** fixed mojibake in `currency-utils.js`
- **Verified:** India shows ₹499, USD shows $5.99, upgrade opens Razorpay modal
- **C7 progress:** 1 of 18 templates complete (events.html)
- **Next:** AA4b (ats.html), AA4c (reports.html)

### RESOLVED — C7 — Build 13 Category-B feature backends (post-G6) (2026-09-28)

**Resolved 2026-09-28.** All 13 backends verified working via batch API test. 12 tool frontends wired end-to-end. 12 paid add-ons converted to notifyMe (commits ab1901f, e5e3cca). Paid fulfillment pipeline deferred as separate track. background-verification.html already correct. 5 Pydantic models tightened.

- **Discovered:** 2026-09-21 (Session G6 revenue audit)
- **Issue:** 13 templates have `processCharvakPayment` UI + callback
  but NO backend endpoint. Currently take payment intent but deliver
  no actual feature.
- **Affected templates:**
  1. `agency-twin.html` - â‚¹2,999 Agency-Twin Pro
  2. `agent-ready.html` - â‚¹399 Agent-Ready Wrapper
  3. `ai-internship.html` - variable (weeks Ã— program)
  4. `ai-slop-quarantine.html` - â‚¹149 AI-Slop Clean
  5. `auditbot.html` - â‚¹299 Fix + â‚¹999 Subscription (2 features)
  6. `design-token-sentinel.html` - â‚¹299 Design-Token Pro
  7. `developer-entropy.html` - â‚¹299 Monitoring
  8. `geo-compliance.html` - â‚¹199 Contract Gen + â‚¹999 Global Hiring (2)
  9. `legacy-shift.html` - â‚¹4,999 Migration
  10. `lock-in-breaker.html` - â‚¹4,999 + â‚¹4,999 (2)
  11. `marketing-ai.html` - â‚¹299
  12. `micro-squads.html` - â‚¹49,999 Assembly
  13. `reports.html` - â‚¹299 Premium Report
  14. `skill-twin.html` - â‚¹499 Verification
  15. `team-dashboard.html` - â‚¹1,999 Pro
  16. `skill-twin` variants
- **Temporary handling (G6):** replace payment button with
  "Notify Me" CTA. Captures intent, no fraud risk.
- **Future work per feature:**
  - Build backend engine + endpoint
  - Add `FEATURE_CREDITS` key
- Added 2026-09-28: `internship_custom_program: 50` (AI curriculum design)
  - Guard with `require_credits_from_data`
  - Wire frontend to credit purchase flow
- **Est:** 3-5 hr per feature Ã— 15 features = **~45-75 hr total**
- **Priority:** Medium - tackle top 3 by market demand first
- **Verdict:** DEFERRED (post-G6, iterative)**

- **Expanded (2026-09-21, Session G6 revenue audit):** 5 additional
  templates confirmed to have the same problem - dead
  `processCharvakPayment` callbacks + working free paths with no gate:
  1. `events.html` - RSVP works free; â‚¹499 button was dead
  2. `ats.html` - no form exists; â‚¹999 button was dead
  3. `lms.html` - no real enroll endpoint; â‚¹999 button was dead
  4. `micro-internship.html` - form on `/post-micro-project` ignores
     the `?payment_id=` redirect; â‚¹2,000 bypassed
  5. `university.html` - no form exists; â‚¹4,999 button was dead

  **G6 handling:** All 5 buttons replaced with `notifyMe()` (matches
  the pattern used across 13 other templates). No working flow was
  removed - the free paths remain intact for now.

  **Future work per template:**
  - Build proper form (events needs RSVP confirmation page; ats
    needs provider/api_key inputs; university needs registration form)
  - Add backend endpoint guard where one exists
  - Wire frontend to `notifyMe()` â†’ real "Buy Credits" flow when
    the feature ships

- **Total C7 scope:** **18 templates** (~25 features across them)
- **Est (updated):** ~60-90 hr total, iterative by priority


### C9 - Catalog expansion: 12 missing exams

- **Completed:** 2026-09-22 (Session L) - commit `f15464f`, merged on main
- **Discovered:** 2026-09-21 (CBT/CAT audit against the master exam list)
- **Issue:** Catalog held 67 exams / 8 categories - missing key Indian CBT exams
  (JEE Advanced, SRMJEEE, MET, COMEDK UGET, MAT, ATMA, MAH MBA CET, IIT JAM, NIMCET)
  and had zero global exams.
- **What shipped:**
  - `engineering` +4: `jee_advanced`, `srmjeee`, `met_manipal`, `comedk_uget`
  - `management` +3: `mat`, `atma`, `mah_mba_cet`
  - `university` +2: `iit_jam`, `nimcet`
  - **NEW category `international`** +3: `gmat_focus` (Section-Adaptive CAT),
    `gre_general` (Section-Adaptive), `toefl_ibt` (CBT)
  - Single-file change: `exam_prep_engine.py`
  - Docstring updated: `67 exams, 8 categories` â†’ `79 exams, 9 categories`
- **Verified:**
  - Local + prod: `total_categories: 9`, `total_exams: 79`
  - All 12 new exam IDs resolve via `get_exam_details`
  - Question generation works end-to-end (real AI)
  - Non-ASCII = 0
- **Follow-ups:**
  - IELTS Academic deferred - needs AI writing/speaking scoring path
  - RRB ALP CBAT (Computer-Based Aptitude Test) module - different question type
  - Adaptive engine (IRT) for GMAT/GRE/NMAT/BITSAT - longer roadmap
  - Re-seed `charvak_exam_question_bank` for the 12 new exams (currently on-demand)

---

### C8 - Revenue enablement (G6)

- **Completed:** 2026-09-21 (Session G6) - commits `0dcf2a8` through `92ce054`
- **What shipped:**
  - **`credit_guard.py`** - reusable `require_credits_from_data(data, feature)`
    + `require_credits_dep` dependency factory; 401 for missing email,
    402 for insufficient credits
  - **Pricing (repriced):** Starter â‚¹199/300cr, Pro â‚¹499/1000cr,
    Premium â‚¹999/2500cr, Enterprise â‚¹4999/15000cr
  - **8 new feature keys** in `FEATURE_CREDITS` (mock_test repriced 20â†’15)
  - **10 routes guarded** across exam / assessment / mock drive
  - **`exam-prep.html` rewritten** - 4 credit packages + balance banner;
    fake subscription system (subscribeExam, planLimits, canPractice,
    showUpgradeModal) removed; demo@ fallback removed
  - **`main.js` 401/402 handler** - global fetch wrapper dispatches
    `charvak:401` / `charvak:402` events
  - **`indian-language-ai.html`** - migrated to credits (2 routes guarded)
  - **18 dead payment buttons** replaced with `notifyMe()` (interest capture);
    `/api/features/notify` + `charvak_feature_interest` table added
  - **`payment-helper.js`** - region-aware modal (India â†’ Razorpay first,
    Intl â†’ PayPal first) with "RECOMMENDED" badge
- **Bugs found in Phase 9 testing & fixed:**
  - Free-plan credit farming (click "Start Free" repeatedly â†’ +50 each):
    `purchase_credits` now rejects repeat free claims; UI hides Free
    card for users with credits
  - `charvak_feature_interest` table creation moved to `_ensure_tables`
- **Not in scope (deferred to C7):**
  - 13 Category-B templates still need real feature backends
  - 5 more templates (events, ats, lms, micro-internship, university)
    have working endpoints but need proper form UX
- **Backwards compatible:** pages render English by default; existing
  users unaffected

- **Batches 1-5 (final audit):** All revenue-generating routes now guarded:
  - Batch 1: Voice + AI tools (14 routes)
  - Batch 2: Marketing + Outreach (7 routes)
  - Batch 3: Student + FYP + Interview + Bridge + Tutor (14 routes)
  - Batch 4: Products + Company + AI-Course + Versant + LMS (39 routes)
  - Batch 5: Background verification + Roles + Content + Internship (5 routes)
  - **System total: 92 routes guarded**
  - **Audit result:** only auth / payment-flow / credits meta / admin /
    mid-session routes remain free (by design).
  - **Nothing AI-powered or feature-unlocking is free.**


### M-1 - IELTS Academic (Listening/Reading/Writing)

- **Completed:** 2026-09-22 - commit `3c7e664` (merge of `15482f6`)
- **What shipped:**
  - `ielts_academic` added to `exam_prep_engine` catalog (80 exams, 9 categories)
  - NEW `ielts_engine.py` (~311 lines) - stateless orchestration:
    - AI prompt generation (Task 1 + Task 2, JSON-mode)
    - AI band scoring on 4 official IELTS criteria
    - Persists to `charvak_assessment_results` (assessment_type='ielts_writing')
  - 3 new routes in `main.py`:
    - `GET  /api/ielts/sections`
    - `POST /api/ielts/writing/generate`
    - `POST /api/ielts/writing/evaluate`
  - 2 new credit keys: `ielts_writing_eval` (15cr), `ielts_writing_prompt` (3cr)
- **Verified E2E:** 117-word Task 2 essay scored 5.5 overall with correct
  Task Response cap (5.0) for word-count violation; persisted with all
  4 sub-bands in details_json.
- **Deferred to M-2:** IELTS Speaking (needs audio recording + Whisper).


### M-2 - RRB ALP CBAT

- **Completed:** 2026-09-22 - commit `<hash>`
- **What shipped:**
  - NEW `cbat_engine.py` (~594 lines) - DB-backed engine
    for 6 sub-tests: Analogies, Decision Making, Numerical Ability,
    Memory (Short/Long), Following Directions
  - NEW migration `20260922_cbat.sql` - 2 tables
    (`charvak_cbat_sessions`, `charvak_cbat_answers`)
  - NEW `templates/cbat.html` - timed question delivery, SVG rendering,
    no back-navigation, per-question countdown
  - 5 new routes: `/api/cbat/sub-tests`, `/start`, `/submit-answer`,
    `/complete`, `/status/{id}`
  - `cbat_session` credit key (25cr)
  - `rrb_alp_cbat` catalog entry (81 exams total)
- **Verified E2E:**
  - 6 sub-tests with per-question timing metadata
  - AI-generated 20 unique Analogies questions
  - Idempotent answer submission (UNIQUE constraint)
  - Session score 5.0% for 1/20 correct
  - All data persisted across 3 tables
  - 25 credits deducted correctly
- **Future (M-3):** Seed curated CBAT questions into a cache
  (currently AI-generated per session)
  - Delivery: image-based (SVG inline), strict per-question timing,
    no back-navigation (UNIQUE constraint on answers table)


### M-3 - State Government Exam Coverage

- **Completed:** 2026-09-22 - commits `f471b67`, `1c0d161` (merged via `2a91239`, `1da969e`)
- **What shipped:**
  - **3 new categories** in `exam_prep_engine`:
    - `state_pcs` (20 exams): UPPSC, MPSC Rajyaseva, RPSC RAS, WBCS,
      TNPSC Group 1 & 2, KPSC KAS, MPPSC SSE, GPSC, OPSC, APSC,
      CGPSC, JPSC, UKPSC, HPSC, PPSC, Kerala PSC, Manipur PSC,
      JKPSC, TPSC
    - `state_police` (18 exams): UP, Bihar, Rajasthan, Delhi, Haryana,
      MP, Maharashtra, Punjab, Kerala, Karnataka, TN, Telangana, AP,
      Gujarat, WB, Odisha, Jharkhand, Chhattisgarh
    - `state_tet` (17 exams): UPTET, REET, MAHA TET, TNTET, KARTET,
      UTET, WBTET, MPTET, JTET, OTET, PSTET, HPTET, APTET, TSTET,
      KTET, Assam TET, Bihar TET
  - **Catalog: 81 â†’ 136 exams, 9 â†’ 12 categories**
  - Zero new engines, tables, routes, or templates - all reuse
    existing infrastructure
  - AI question generation works for every new exam
- **Verified:**
  - Prod shows 136 exams / 12 categories
  - AI generation confirmed for new exams
- **Coverage:** all major Indian states across PCS / Police / TET


### M-3.5 - Prompt hardening + difficulty calibration

- **Completed:** 2026-09-22 - commit `43bc281` (merge of `43c20d2`)
- **What shipped:**
  - AI prompt rewritten with STRICT RULES:
    - Enforce EXACTLY 4 options per question
    - Require unique questions (no duplicates)
    - Verify correct answer appears in options
    - Self-regenerate on invalid output
  - `difficulty` field added to all 136 exams
  - `_get_exam_difficulty()` helper added
  - Prompt passes `Difficulty: {level}` context
- **Distribution:** Easy 49, Medium 68, Hard 19
- **Verified:**
  - ssc_cgl/Reasoning (Medium): 5 unique, 4-opts-each
  - up_police/GK (Easy): basic state GK
  - cat/VARC (Hard): complex reasoning
- **Discovered but NOT fixed:** see C13.

### C13 - Curated question banks (Session M-4)

- **Discovered:** 2026-09-22 (content quality audit on SSC CGL Reasoning)
- **Issue:** Prompt hardening reduces but does not eliminate logical
  errors in AI questions (missing correct answer in options, subtle
  math errors). Content quality is user-visible.
- **Solution:** Pre-generate questions once, manually review, seed
  into `charvak_exam_question_bank`. Cache-first, live-AI fallback.
- **Scope:**
  - Top 20 exams x 5 topics x 30 questions = 3,000 curated questions
  - Manual review process
  - Seed script (reuse Session G3 pattern)
  - Extend `_load_from_bank` to prefer seeded questions
- **Est:** 2-3 hr per batch
- **Priority:** Medium-High

## ðŸ”´ CRITICAL - Must Fix

### C2 - `voice_to_web_engine.py` persistence

- **Discovered:** 2026-09-20 (was flagged as B-2, never executed)
- **Issue:** 5 in-memory stores (`websites`, `domains`, `updates`, `support_tickets`, `seo_configs`)
- **Action:** Design tables + migration + refactor + test
- **Est:** ~1 hr
- **Target:** Session B-2
- **Status:** SKIPPED on 2026-09-21 in favor of C1. Re-schedule per priority.

### C3 - RTL UI support - DEFERRED 2026-09-21

- **Discovered:** 2026-09-20 (`base.html` has `<html lang="en">` hardcoded)
- **Original issue:** Arabic users see LTR layout despite `dir="rtl"` in config
- **Why deferred:** Only 1 of 34 languages is RTL (`ar`). No evidence of an
  Arabic-speaking user base in any project doc. RTL-layout-with-English-text
  is worse UX than clean LTR - the right sequence is C6 (content i18n) FIRST,
  then C3.
- **Escalation trigger (any of):**
  1. A real Arabic-speaking user or customer appears
  2. Sales/marketing targets MENA region
  3. C6 (assessment UI translations) ships - then C3 makes sense as follow-up
- **When triggered:** ~2 hr (dynamic `lang`/`dir`, bootstrap RTL swap,
  cookie picker, ~2 CSS overrides in `static/css/style.css`)
- **Verdict:** DEFERRED (product decision - no current user base)

---

## ðŸ” NEEDS VERIFICATION

### V1 - Doc sprawl

- **Check:** List all .md files in root
- **Concern:** Duplicates may exist (KNOWN-ISSUES vs FINAL-STATUS, etc.)
- **Action:** Verify next audit

### V2 - whatsapp_bot.py JSON mode - FALSE ALARM

- **Discovered:** Line 60 uses `response_format="text"` - but this is
  `audio.transcriptions.create` (Whisper), NOT chat completions.
  Text format is correct for Whisper.
- **Line 89** (the only LLM call) uses JSON mode correctly.
- **Verdict:** âœ… No bug. No action needed.

### V3 - 34-language claim vs delivered

- **Check:** Count actual supported languages
- **Concern:** Site copy says 34; actual may be less
- **Status:** âœ… RESOLVED 2026-09-21 - `global_config.LANGUAGES` has 34 languages,
  and as of Session G1 `indian_language_ai._generate_questions` serves all of them
  via AI. Copy claim is now accurate for the assessment flow.

---


### V4 - Dev and prod share one Render Postgres

- **Discovered:** 2026-09-21 (Session G3)
- **Reality:** `.env` `DATABASE_URL` connects to
  `dpg-d9m92j0ae00c73blvoq0-a.singapore-postgres.render.com/vouchai`.
  Every local script run writes to prod. No dev/staging isolation.
- **Evidence:**
  - Local `charvak_exam_question_bank` count (12,892) exactly matches
    prod count verified via Render Shell
  - `charvak_user_ability` table appeared in prod immediately after
    local `ability_engine._ensure_tables()` ran during G2
  - No log file at `/tmp/g3_seed.log` in Render Shell despite local
    seed script having run - because the script never ran in Render's
    container; it ran on the local machine talking to the shared DB
- **Implication:**
  - All local experiments are prod operations
  - Any destructive query (`DROP`, `DELETE` without `WHERE`, bulk
    `UPDATE`) affects real users immediately
  - No safe sandbox for testing
  - Backups capture prod state, not a dev clone
- **Action (deferred):** Set up local Postgres 15 for dev (Postgres 15
  is already installed per `MASTER-REFERENCE.md` at
  `C:\Program Files\PostgreSQL\15`) OR provision a separate Render
  staging database.
  - **Option A (local):** Point `.env.local` at
    `postgresql://postgres:dev@localhost:5432/charvak_dev`, run
    migrations + seed scripts against it.
  - **Option B (Render staging):** New Render Postgres resource;
    copy prod â†’ staging periodically for realistic tests.
- **Escalation trigger:** Any of the following:
  1. Any destructive operation planned (DROP, DELETE without WHERE,
     bulk UPDATE)
  2. Onboarding a second developer
  3. Adding a feature that requires iterative testing against scratch
     data
- **Verdict:** DEFERRED (works today; revisit when risk grows)


### V5 - Local shell env var overrides .env DATABASE_URL

- **Discovered:** 2026-09-22 (Session M-2 verification)
- **Reality:** `.env` points to Render prod DB. But setting
  `$env:DATABASE_URL` in PowerShell to a local Postgres URL makes
  Python's `load_dotenv()` a no-op - the shell value wins.
- **Consequence:** During a single session, browser tests hit PROD
  (`charvakit.com`) while shell curl/cleanup scripts hit LOCAL.
- **Rule:** Never override `DATABASE_URL` in the shell unless
  working with local. `.env` = prod source of truth.
- **Fix for cleanup scripts:** read from `.env`:
  ```powershell
  $env:DATABASE_URL = ((Get-Content .env | Where-Object { $_ -match '^DATABASE_URL=' }) -replace '^DATABASE_URL=', '').Trim()

## âœ… CONFIRMED BY DESIGN (no action)

| # | Item | Verified |
|---|---|---|
| D1 | `dynamic_role_engine.create_dynamic_training_plan` stateless | 2026-09-20 |
| D2 | ~~`ai_internship_engine.submit_work` random score placeholder~~ **RESOLVED 2026-09-28** | 2026-09-20 |
| D3 | `role_manager` + `dynamic_role_engine` parallel by design | 2026-09-20 |
| D4 | `record_survey_response` counter-only | 2026-09-20 |
| D5 | `admin_role_manager` used in main.py:6131 | 2026-09-20 |

---

## ðŸ“… SCHEDULED

| # | Item | When |
|---|---|---|
| #53 | Delete charvakit-new-OLD folder | 2026-09-22 |

---

## ðŸ”’ BLOCKED

| # | Item | Blocker |
|---|---|---|
| #65 | whatsapp_bot.py full fix | Meta registration |

---

## ðŸ“‹ EXECUTION ORDER (revised 2026-09-21)

1. ~~**Session B-2**~~ - voice_to_web persistence (C2)  [SKIPPED, re-schedule later]
2. ~~**Session G1**~~ - Assessment AI for 34 languages (C1)  âœ… DONE 2026-09-21
3. ~~**Session G4**~~ - RTL UI (C3)  [DEFERRED 2026-09-21 - no Arabic user base]
4. ~~**Session G2**~~ - Adaptive difficulty (C4)  âœ… DONE 2026-09-21 (commit `15193f9`)
5. ~~**Session G3**~~ - Question banks (C5)  âœ… DONE 2026-09-21 (commit `f4a3fd3`)
6. ~~**Session G5**~~ - Assessment i18n (C6)  âœ… DONE 2026-09-21

**All CRITICAL items resolved.** Remaining: C2 (parked), C3 (deferred).
**Dead code cleanup completed 2026-09-21 (Session G2-pre):**
- Deleted `assessment_complete.py` (in-memory stub, zero frontend callers)
- Removed 5 orphaned `/api/assessment/*` routes from `main.py`
- Commits: `bdf32fa`, `8951c9b`
---

## ðŸ§  PROCESS LESSONS LEARNED

### L1 - PowerShell + Python file patching is fragile (Session G1, 2026-09-21)

Three automated patch attempts failed before a manual edit succeeded:

- `Out-File -Encoding UTF8` (PowerShell 5.x) prepends a BOM, which broke
  byte-level string anchors in the patcher script
- `Measure-Object -Line` and `Out-String` fold/wrap UTF-8 content at console
  width, producing wrong line/char counts (reported 354 lines when the file
  had 390; reported 17,575 chars when the file was 19,806 bytes)
- Manually pasted here-string payloads silently lost leading whitespace and
  trailing commas, producing `IndentationError` and `SyntaxError`
- Hand-typed base64 payload introduced typos (`LANGUAGESS`) and dropped commas

**Reliable path forward:**
- For source edits containing non-ASCII (Devanagari, Tamil, etc.), use
  **Notepad (manual edit)** - verified working in Session G1
- For file-state questions, trust **`git diff --exit-code`** over any
  PowerShell string measurement
- Always `git diff` before commit and `git push` after - git is the durable backup

### L2 - Pager stalls in terminal scripts

`git diff` without `--no-pager` opens `less` and blocks non-interactive scripts.
Recommended: `git config --global core.pager ""` on Windows.

### L3 - Preserve `.bak` files until AFTER the commit is pushed

Session G1 deleted all `.bak` backups before the final commit.
Nothing was lost because git tracked the change, but the safety margin was thin.
**Rule: delete `.bak` files only after `git push` succeeds.**

### L4 - `git rm <file>` does not stage other working-tree changes

`git rm assessment_complete.py` stages only that file's deletion. Any other
modified files (`main.py` in this case) need explicit `git add`. Always check
`git status --short` before committing - files marked ` M` in the second
column are modified but NOT staged.

`git commit` without `-a` only commits staged changes. Verify with
`git show --stat HEAD` after each commit that the expected files landed.

### L5 - `ast.parse()` is stricter than Python's real import

`ast.parse(open(path).read())` fails on files with UTF-8 BOM (`EF BB BF`),
raising `SyntaxError: invalid non-printable character U+FEFF`. But
`import module_name` succeeds - Python accepts BOM at start of source files.

**Rule:** use `python -c "import X"` for syntax validation. Reserve
`ast.parse` for cases where the string doesn't have a BOM, or strip the
BOM first.

**Note:** `results_system.py` has a pre-existing BOM (unrelated to G2).
No action taken; if a future housekeeping session wants a repo-wide BOM
sweep, grep files whose first 3 bytes are `EF BB BF`.

### L6 - Multi-insert patchers must go strictly bottom-up

When a patch inserts lines at multiple positions in the same file, apply
edits in **strictly descending index order** (highest first). An insert at
index 49 shifts every subsequent index - so an "insert at 48" that follows
it lands 2 lines off and can break the file.

**Session G2 evidence:** the first Batch-3 patcher for
`enhanced_assessment_engine.py` failed exactly this way (`'{' was never
closed`). Rolled back cleanly with `git checkout --`. The corrected patcher
applied ops in reverse index order and worked first try.


### L7 - Real OpenAI latency is 3-4x the nominal estimate

Session G3: batch seeding 207 pairs took 88 min, not the estimated
33 min. Root cause: OpenAI chat completions averaged ~25s per call in
practice, not the ~7.5s assumed from single-call timings.

**Rule:** for batch OpenAI work, estimate at **25-30s per call** unless
you have measured recent latency. Add 2-3s throttle on top.

### L8 - Engine fallback masks OpenAI failures as success

`exam_prep_engine._generate_via_ai` catches exceptions and returns
`_stub_questions()` on failure, but the outer `generate_questions`
still returns `status: success`. The seed script therefore reports OK
on fallback content.

**G3 evidence:** `jssc/Math` (pair 198) - OpenAI timed out at 45s, stub
content (30 trivial arithmetic questions) was written to the bank.
Fixed by deleting stub rows (LENGTH heuristic) and re-generating.

**Rule:** for content-quality-sensitive batches, verify question content
sample, not just count. Consider adding a `source` column to the bank
to distinguish AI-generated from stub.

**Rule:** for multi-edit patchers, iterate indices in descending order,
or operate on string matches rather than line indices.


### L9 - Double-encoded UTF-8 in template dropdown values

Session G5 found `base.html`'s language dropdown had 17 `<option>`
values that were double-encoded (UTF-8 bytes reinterpreted as Latin-1,
then re-encoded). `à¤¹à¤¿à¤¨à¥à¤¦à¥€` was stored as `Ã Â¤Â¹Ã Â¤Â¿Ã Â¤Â¨Ã Â¥Ã Â¤Â¦Ã Â¥â‚¬`.

**Fix:** rewrite `<option value="XX">ANYTHING</option>` from
`global_config.LANGUAGES` (which was clean).

**Rule:** when pasting non-ASCII into files, verify bytes with
`[System.IO.File]::ReadAllBytes()`. If the first bytes of a Devanagari
character are `C3 A0` instead of `E0 A4`, it's double-encoded.

**Search for hidden instances:** grep for `Ã Â¤`, `Ã Â®`, `Ã Â²`, `Ã˜Â§`, `Ã¤Â¸`,
`Ã `, etc. across all templates.

---

## PROCESS COMMITMENT

**To prevent future slips:**

1. **Every session is documented** before starting (in this file)
2. **After every session**, status is updated here
3. **Never let a promised item silently disappear** - flag it in this file immediately
4. **Verification audits** every N sessions to catch gaps
5. **Session-CONTEXT.md** links here for fresh chats

---
**Last updated:** 2026-09-29 (Session B - flags #2, #4, #5, #6 closed; #3 deferred to dedicated test session). HEAD: `7c679f1`



---

## Session 2026-09-27 — 11-Product Frontend Sprint

**Time:** single session, ~3 hours
**Commits:** `1fc5b06` through `37df5b1` (13 commits)

### Completed

All 11 AI Products now have real forms wired to their auth-gated,
credit-gated backend routes. Every one verified E2E: form → auth → credits
→ AI → render.

| # | Product | Credits | Commit |
|---|---|---|---|
| 1 | AuditBot | 25 | 7f178b9 |
| 2 | Lock-In Breaker | 20 | d07a8ba |
| 3 | Reverse Staffing | 20 | 6505695 |
| 4 | AI Slop Quarantine | 10 | 1fc5b06 |
| 5 | Geo Compliance | 15 | 31e4080 |
| 6 | Design Token Sentinel | 15 | 372f810 |
| 7 | Agency Twin | 20 | 88756b2 |
| 8 | Skill Twin | 15 | e1d138e |
| 9 | Silent Killer | 15 | 91463bf |
| 10 | Developer Entropy | 15 | f39b71f |
| 11 | Micro Squads | 25 | 37df5b1 |

### Bugs found & fixed during the sprint

1. **Silent Killer `status` field collision** — engine set `status: "active"`,
   overwriting the route wrapper's `status: "success"`. Frontend showed
   "Setup failed" despite the API working. Fixed by renaming to
   `monitor_status`.
2. **Agency Twin roadmap** — AI returned roadmap as objects; frontend
   rendered `[object Object]`. Fixed with defensive `_renderList` helper.
3. **Credit text mismatches** — 3 templates (`lock-in-breaker`,
   `reverse-staffing`, `ai-slop-quarantine`) displayed "15 credits" while
   backend charged 20/20/10. Fixed by reading actual `FEATURE_CREDITS`.
4. **Reverse Staffing field reset** — `value="3"` on the experience input
   reset the field after submit. Fixed with `placeholder="e.g. 3"`.
5. **`premium-upsell.html`** — every product's "Unlock Full Report" button
   called undefined `processToolPayment`. Fixed with `notifyMe` fallback.

### Credit verification

DB log confirmed every product charged the correct amount per call.
Final balance after all E2E tests: 385 credits remaining.

### Process lesson

WatchFiles on Windows can hold a file lock during uvicorn reload, silently
reverting a Python write. **Fix:** stop uvicorn → write → verify with grep
→ restart. Hit this twice (`products_engine.py`, `developer-entropy.html`).

### Newly identified — not in original sprint scope

- **`agent-ready.html`** — C7 template (₹399 dead payment button)
- **`ai_service.py` tools without frontends:**
  - Neural Wireframe (`neural_wireframe_to_code`)
  - Globalize.ai (`localize_website`)
  - Legacy-Shift (`analyze_legacy_code`)
  - Agent-Ready (`generate_agent_schema`)
  - These were verified to return real AI output tonight, but no page
    calls them. Backend is ready; frontend wiring needed.

**Last updated:** 2026-09-29 (Session B - flags #2, #4, #5, #6 closed; #3 deferred to dedicated test session). HEAD: `7c679f1`


---

### RESOLVED — 4 unlisted AI tools need frontend wiring + auth (2026-09-28)

**Resolved 2026-09-28.** All 4 tools (Neural Wireframe, Globalize.ai, Legacy-Shift, Agent-Ready) rebuilt with real forms + auth headers + credits + JSON renderers. Commits: da15ef6, 05bf57f, 6b18873, a7080cd. Backend auth in 6b22d61.

Discovered after the 11-product sprint. These 4 tools have:
- ✅ Page route registered
- ✅ Template file exists
- ✅ Backend API route
- ✅ Credit-gating via require_credits_from_data
- ❌ No require_auth_for_email
- ❌ Frontend never calls the AI route

| Tool | Page | API route | Credit key |
|---|---|---|---|
| Neural Wireframe | /neural-wireframe | /api/ai/neural-wireframe | ai_neural_wireframe |
| Globalize.ai | /globalize | /api/ai/localize | ai_localize |
| Legacy-Shift | /legacy-shift | /api/ai/analyze-legacy | ai_analyze_legacy |
| Agent-Ready | /agent-ready | /api/ai/generate-schema | ai_generate_schema |

**Special case:** neural-wireframe.html has a Razorpay flow that charges but
never calls the AI route. Needs replacement with credits-based form.

**Also without backend routes (marketing-only pages):**
- /napkin-challenge
- /revenue-leak-detector
- /time-machine-checker
- /ai-commerce-scorecard

**Est:** ~1.5 hrs total for the 4 tools.

**Verdict:** SCHEDULED — next session

**Last updated:** 2026-09-29 (Session B - flags #2, #4, #5, #6 closed; #3 deferred to dedicated test session). HEAD: `7c679f1`


---

## Next session scope (2026-09-27)

Queue of remaining work, roughly in priority order.

| # | Item | Effort | Type |
|---|---|---|---|
| 1 | **4 unlisted AI tools** — Neural Wireframe, Globalize.ai, Legacy-Shift, Agent-Ready | ~1.5 hrs | Same pattern as 11-product sprint |
| 2 | **MCQ** — /mcq page: keep free library, add AI-generate button → /api/assessment/mcq/generate (already auth+credit, 5cr) | ~30-45 min | Frontend add + verify |
| 3 | **AI Internship** — add require_auth_for_email to 5 routes (enroll has credits but no auth; scenario/complete/submit/progress have neither); engine submit_work uses random score (KNOWN-ISSUES #9) | ~45-60 min | IDOR fix + optional AI eval |
| 4 | **C7 — 14 templates with dead payment buttons** | 4-6 hrs | Per-template product decisions |
| 5 | **4 templates with processToolPayment** (background-verification, bounty-swap, ref-swap, ghost-tracker) | 45 min | Same fix as premium-upsell.html |
| 6 | **FYP feature roadmap** (7 logged features) | 1 hr each | Product decisions |
| 7 | **Dead /api/assessment/* routes** | 20 min | Hygiene — legacy-marked, cleanup candidate |

### Notes

- Item 1 is mechanical (same pattern used 11x tonight) — highest confidence of clean success.
- Items 2-3 need discovery greps first: does the backend exist? Is it auth+credit gated? Does the frontend call it?
- Item 4 requires product decisions per template (ship real feature vs keep notify-me).
- Item 5 is quick and formulaic.
- Item 6 is the FYP roadmap already logged: Viva Answers, Per-Chapter Expand, Milestone Roadmap, Refine Section, Humanize, Citations, Viva Simulator.
- Item 7 can be either deleted or left with the legacy banner we added.

**Suggested session structure:**
- Session A (~2 hrs): Items 1 + 5 (mechanical fixes, quick wins)
- Session B (~30 min): Items 2 + 3 (MCQ + AI Internship audit)
- Session C (~4-6 hrs): Item 4 (C7 template sweep)
- Session D (open): Item 6 (FYP features by user demand)
- Optional: Item 7 whenever there is appetite

**Last updated:** 2026-09-29 (Session B - flags #2, #4, #5, #6 closed; #3 deferred to dedicated test session). HEAD: `7c679f1`


---

**MCQ strategy decision (2026-09-27): Option A — Free library + paid AI generate**

**Rationale:** The curated `mcq_bank` remains free as a lead magnet (SEO, user
acquisition). The existing AI-generation route (`/api/assessment/mcq/generate`)
becomes the paid tier at 5 credits per call. This matches the freemium pattern
used across the rest of the product suite.

**Implementation for next session:**
- `/mcq` page keeps the current "From Library" browse as-is (free)
- Add "AI Generate" button on the same page -> POST /api/assessment/mcq/generate
  with JSON body containing email, category, topic, count + Authorization header
- Display "5 credits" on the button
- Handle 401 (redirect to login) and 402 (redirect to pricing)
- Response shape: status + questions array -- render like the library view

**Not doing (rejected alternatives):**
- Option B: charging for library access too -- removes the free lead magnet
- Option C: deprecating the library, everything via AI -- slower + always costs

**Verdict:** Decided, scope locked, awaiting implementation in next session

**Last updated:** 2026-09-29 (Session B - flags #2, #4, #5, #6 closed; #3 deferred to dedicated test session). HEAD: `7c679f1`


---

## Session 2026-09-27 (evening, part 2) — MCQ + internship resume + cleanup

**HEAD after:** `61ad294`

### Completed this session

- **MCQ (Item 2)** — paid AI generate tier
  - `templates/mcq.html` — "AI Generate" button + inline form (topic / category / count), wired to `POST /api/assessment/mcq/generate` (existing route, 5 credits, auth+credit-gated)
  - XSS hardening — added `esc()` helper and wrapped all `innerHTML` interpolations in `renderQuestions`
  - Commits: `0a0ee21` (feature), `61ad294` (DBMS rename)
- **MCQ DBMS/SQL -> DBMS & SQL rename** — 4 files updated
  - `mcq_bank.py:158`, `advanced_assessment_engine.py:99`, `market_standard.py:102`, `templates/mcq.html:110`
  - Fixes `GET /api/mcq/questions/technical/DBMS%2FSQL` -> 404 (FastAPI decodes `%2F` before route matching)
- **CharvakCurrency utility** — added `detectLocation`, `format`, `getName` to `static/js/currency-utils.js`
  - Fixed 3 pre-existing JS errors that were blocking `/ai-internship` from rendering at all
- **Cross-device internship resume**
  - `ai_internship_engine.get_my_enrollments(email)` + `record_day_viewed(enrollment_id, day)`
  - `GET /api/internship/my-enrollments?email=` (auth-gated)
  - Resume banner in `ai-internship.html` with "Resume" button
  - `get_daily_scenario` now bumps `charvak_ai_internship_enrollments.current_day` on every load
  - Commit: `8c53cc4`
- **Repo cleanup** — deleted 6 stale `_*.py` dev scripts from 2026-09-19/21

### Verified

- Library free path — no deduction
- `DBMS & SQL` tab loads (200 OK)
- AI Generate — 5 credits deducted (`assessment_mcq`), 10 questions returned in ~5-10s
- 402 redirects to `/ai-credits-pricing` on insufficient credits
- XSS — `<img src=x onerror=alert(1)>` in topic does not fire (escaped)
- Resume banner renders for users with active enrollments; if localStorage is cleared, banner recovers

---

### RESOLVED — `mcq_bank.get_topic_questions` no longer calls OpenAI (2026-09-28, commit 819cb3f)

**Resolved 2026-09-28.** Removed the `_generate_ai_questions` fallback from
the free library path entirely. `get_topic_questions` now returns only what
the curated bank holds — the paid `/api/assessment/mcq/generate` route
(5 credits) is the only path that calls OpenAI. Verified: library click shows
no OpenAI activity in uvicorn log; paid AI generate still charges correctly.

The library endpoint `GET /api/mcq/questions/{category}/{topic}` accepts `count` (default 10). When `len(questions) < count`, it calls `_generate_ai_questions()` — an **ungated OpenAI call**. Users clicking a topic tab can trigger a free AI call.

**Fix (recommended):** remove the AI fallback from the library endpoint — return only what the bank has. The paid AI tier at `/api/assessment/mcq/generate` now covers on-demand generation.

**Est:** ~10 min. **Verdict:** SCHEDULED — small correctness fix.

---

### RESOLVED — MCQ sections/topics are hardcoded in 3 places with no single source of truth (2026-09-27)

**Resolved 2026-09-28.** Fixed 2026-09-28 (`54bd78a`). Template now fetches `/api/mcq/topics` on load; hardcoded dict becomes fallback only.


Topics live in:
1. `mcq_bank._initialize_question_bank()` — actual bank (source of truth for lookups)
2. `templates/mcq.html` `topics` dict — hardcoded tab list
3. `mcq_bank.get_all_topics()` — derived, not consumed by the frontend

Adding a topic today requires editing (1) and (2) by hand. Silent drift is possible.

**Fix:** fetch `/api/mcq/topics` at page load, build tabs dynamically, remove the hardcoded dict.

**Est:** ~45 min. **Verdict:** SCHEDULED — architectural cleanup, not urgent.

---

### Still SCHEDULED (unchanged)

- **Internship enrollment cleanup** (~45 min) — auto-abandon prior active per `(email, program_id)` on new enroll; banner dropdown when user has >1 active across programs; `POST /api/internship/abandon/{enrollment_id}` + Dismiss button
### RESOLVED — Internship Phase 3: AI-designed custom programs (2026-09-28, commit f57af58)

**Shipped 2026-09-28 (commit `f57af58`).** AI-designed custom internship programs.
Users type any role (e.g. "Underwater Robotics Engineer") and OpenAI generates a full
curriculum: name, category, 4-6 skills, 3-4 deliverables, week-by-week outline.

- Backend: `ai_internship_engine.create_custom_program()` + `_resolve_program()` helper;
  `get_programs(email)` merges user's custom programs into the grid; `enroll()` now
  resolves custom program IDs (previously only static `self.programs` dict)
- Route: `POST /api/internship/custom-program` — auth-gated + credits-gated
- Frontend: search-bar card above the program grid; custom programs render with a blue
  "Custom" badge; `loadPrograms()` sends `?email=` so users see their own
- Storage: `charvak_ai_internship_custom_programs` table (schema existed, was dormant)
- Per-user scoping via `requested_by` column; `is_public=0` for now

**Verified E2E:** created "Underwater Robotics Engineer" → real AI curriculum (5 skills,
4 deliverables, category Engineering) → persisted to DB → re-fetched via API with
`is_custom: true`. 50 credits deducted correctly.
- **Internship Phase 4 — tier UI + top-up-then-enroll** (~60 min) — tier selector, credits-needed computation, Razorpay top-up modal, switch `internship_enroll` from flat 100 cr to tier-based
- ~~**`ai_internship_engine.submit_work` real AI eval** (KNOWN-ISSUES #9)~~ — **RESOLVED 2026-09-28, commit `16c5d97`.** Real OpenAI mentor eval now live; random stub only used as fallback if the AI call fails. Submit Work UI added to `templates/ai-internship.html`. Verified E2E: scored 8/10 with contextual strengths/improvements.


### RESOLVED — Internship Phase 4: tier-based INR enrollment via Razorpay (2026-09-28)

**Shipped 2026-09-28.** Replaces the flat 100-credit `internship_enroll` with 8 priced tiers
(Sprint 2wk Rs1,299 → Capstone 16wk Rs8,499). Users pick a plan in a modal, pay via
Razorpay, and get an enrollment record + confirmation email.

**Pricing:** +25% raise from the old display prices. Sprint Rs1,299 / Standard Rs2,499 /
Extended Rs3,499 / Immersive Rs4,499 / Semester Lite Rs5,499 / Semester Rs6,499 /
Semester Plus Rs7,499 / Capstone Rs8,499. Bundled AI mentor (20 free questions, 5cr each
after).

**Backend:**
- `ai_internship_engine.enroll_paid()` + `find_enrollment_by_payment()` idempotency check
- `_get_tier_by_key()` helper reads from `charvak_ai_internship_tiers`
- New columns on enrollments: `mentor_asks_used`, `amount_paid_inr`, `razorpay_payment_id`
- New route `POST /api/internship/enroll-paid` — verifies Razorpay API capture + exact amount
- Webhook `notes.tool == 'internship_enroll'` branch (idempotent, same pattern as courses)
- `enhanced_email.send_internship_enrollment()` — confirmation with next steps

**Frontend:**
- Modal with 8 tier cards, populates from `/api/internship/tiers` (cached)
- Razorpay SDK loaded lazily (`ensureRazorpayLoaded()`) — not on every page load
- `verifyAndEnroll()` handles signature verification + calls the enroll route
- Success toast + auto-scroll + auto-load Day 1 scenario

**Critical fix — modal must escape `<main>` stacking context:**
The modal was initially rendered inside `{% block content %}`, which `base.html`
wraps in `<main>`. `<main>` has `position: relative; z-index: 1`, creating a stacking
context that trapped the modal behind its own backdrop regardless of z-index.
**Fix:** added `{% block modal %}{% endblock %}` in `base.html` right after `</main>`.
Any template that needs a modal puts it in the modal block instead of the content block.
**Reusable pattern** — all future modals must use `{% block modal %}`.

**Verified E2E:**
- Razorpay SDK loads, order created via API, checkout modal opens with card form
- Enrolled 4-week Data Engineer program, all 8 tiers render in the picker
- Order IDs recorded in log: `order_ThGLR1j0dKRjLP`, `order_ThGLw0ZLuAcn6w`,
  `order_ThGOsbUDYQosVj`
- Fake payment rejected with 402 (verified against real Razorpay API)
- Legacy `/api/internship/enroll` route kept for backward compat (unused by new UI)

### AUDITED — modal stacking-context sweep (2026-09-28)

Grep of `templates/*.html` for `class="modal fade"` returned exactly **one** match:
`templates/ai-internship.html` (the Phase 4 tier modal, already fixed by moving it to
`{% block modal %}`). No other templates have modals trapped in `<main>`.

**Going forward:** any new modal goes in `{% block modal %}` in `base.html`
(declared right after `</main>`), never in `{% block content %}`.

### Cleanup pending

- **devtest orphan enrollments** — ~8 active rows from testing. Delete + refund or leave. Do at end of internship work.

**Last updated:** 2026-09-29 (Session B - flags #2, #4, #5, #6 closed; #3 deferred to dedicated test session). HEAD: `7c679f1`


---

## Session 2026-09-28 — PayPal credits for non-INR (backend verified)

**HEAD before block:** `8c96e68` + follow-up commits

### Completed this session

- **PayPal credits purchase for non-INR users** — full flow
  - `payment_engine.create_paypal_order()` now calls `POST https://api-m.paypal.com/v2/checkout/orders` and returns the real PayPal order ID (17-char alphanumeric, e.g. `7JU25615UU6203421`). Previously it returned an invented `PAYPAL_xxx` id that PayPal rejected with `INVALID_RESOURCE_ID`.
  - `payment_engine.fetch_paypal_order(paypal_order_id)` — new method. Fetches order from PayPal's API, returns `{status, status_field, amount, currency, email, paypal_order_id}`.
  - `payment_engine.verify_paypal_payment()` — test-mode bypass removed. Previous behavior returned `{"verified": True}` unconditionally when `PAYMENT_MODE=test`, which would have granted credits for any fabricated order id. Now returns `{"verified": False, "message": "refused in test mode"}`.
  - `/api/credits/purchase` — now branches on `payment_id` prefix:
    - `pay_xxxxx` (Razorpay, INR, paise): unchanged
    - `paypal:<CURRENCY>:<PAY-xxx>`: fetch from PayPal, check `status == COMPLETED`, verify currency matches, verify amount matches `INR_RATES[currency] * plan.price` within 2% FX tolerance, then grant credits.
  - `templates/ai_credits_pricing.html` — `processSubscription()` refactored. INR → Razorpay (unchanged). Non-INR → provider picker with **Pay with PayPal (USD)** and **Pay with Razorpay (INR)** buttons. Provider picker shows the approximate local-currency amount.
  - `static/js/payment-helper.js` — added `ensurePayPalLoaded()` helper that fetches the client_id from `/api/payment/status` and injects the SDK on demand. Fixed a syntax bug (`await` inside non-async `.then()` callback). Replaced the `YOUR_PAYPAL_CLIENT_ID` placeholder that would have loaded a broken SDK.
  - `payment_engine.is_ready()` — now returns `razorpay_key_id` and `paypal_client_id` (public-safe halves only; secrets never exposed). Required for the lazy SDK load.
  - `templates/base.html` — removed the unconditional PayPal SDK load on every page (saves ~1 MB per page load on non-payment pages).

### Verified

- **Backend verified against live PayPal API, no charge.** Test script created real order `7JU25615UU6203421`, fetched it, parsed status `CREATED`, amount `2.39 USD` matching `round(199 * INR_RATES["USD"], 2)`. `verify_paypal_payment` correctly returned `{verified: False}` for the uncaptured order.
- Order `7JU25615UU6203421` was never captured; it auto-expires ~3 hours from creation. No money moved.
- INR path unchanged — Razorpay modal still opens with correct amount.
- `/api/credits/purchase` correctly rejects fake PayPal order ids with a 404 from the PayPal API.

### FLAGGED — PayPal credits: browser capture step not yet tested end-to-end

The `paypal.Buttons({ createOrder, onApprove })` chain — specifically `actions.order.capture()` returning to `/api/credits/purchase` — has not been exercised with a live capture. Every other piece of the chain is verified:
- `create_paypal_order` reaches PayPal and returns a real ID ✅
- `fetch_paypal_order` retrieves and parses it ✅
- amount math matches within tolerance ✅
- `/api/credits/purchase` correctly branches on the `paypal:` prefix and validates server-side ✅
- `paypal.Buttons` is standard SDK usage ✅

**Test:** make one real $2.39 payment via the picker, verify credits granted, then refund in the PayPal dashboard. ~5 min, $0 net cost.

**Verdict:** FLAGGED — needs one live capture to close.

### RESOLVED — `CachedStaticFiles` + hardcoded `?v=` query strings

`main.py` sets `Cache-Control: public, max-age=31536000, immutable` on all `/static/*` files. Templates reference them with a fixed `?v=2.1`/`?v=2.2`/`?v=2.3` query string. Any code change to a cached JS/CSS file requires manually bumping the `?v=` reference in every template that includes it.

This caused today's PayPal debugging: `payment-helper.js` was updated in `8c96e68`, but the browser ran a stale cached copy for ~10 minutes because the URL was unchanged. Diagnosed by comparing `document.querySelectorAll('script[src*="payment-helper"]')` output to the on-disk file.

**Fix:** inject a build hash (`RENDER_GIT_COMMIT`, or a startup timestamp) into templates as `STATIC_VERSION` and reference assets as `/static/js/payment-helper.js?v={{ STATIC_VERSION }}`. ~30 min. Medium priority — every future JS/CSS edit will hit this footgun until fixed.

### FLAGGED — `ai_courses_payments` PayPal path may have the same stub

`payment_engine.create_paypal_order` was a stub until today. If `ai_courses_payments.py` (or any other engine) has its own PayPal order-creation path, it may share the same bug. Worth a quick audit: `grep -rn "create_paypal_order\|PAYPAL_" --include="*.py" | grep -v "payment_engine.py"`. ~15 min.

### FLAGGED — PayPal credits has no webhook safety net

If the browser closes after the PayPal SDK captures the payment but before the frontend POSTs to `/api/credits/purchase`, the user's money is taken but credits are never granted. `/webhook/paypal` exists but only handles AI course payments.

**Fix:** extend the webhook to detect credits purchases (via `purchase_units[0].custom_id` starting with `credits|`) and call `purchase_credits` idempotently. ~30 min. Real user-impact risk — a browser crash between capture and callback = lost payment.

### Not changed (deliberately)

- Razorpay flow on `/ai-credits-pricing` — unchanged, still INR-only.
- INR users still see only Razorpay.
- `PAYMENT_MODE=test` behavior for Razorpay `order_test_*` fake orders — untouched. (Separate flag; not PayPal-related.)

**Last updated:** 2026-09-29 (Session B - flags #2, #4, #5, #6 closed; #3 deferred to dedicated test session). HEAD: `7c679f1`

---

## Session 2026-09-28 (evening, part 3) — Item 4 shipped

### RESOLVED — requirements.txt missing razorpay (2026-09-28)

`payment_engine.py` imports `razorpay` but it was never listed in
`requirements.txt`. Local dev on a fresh venv failed at
`python -c "import fastapi, psycopg2, openai, razorpay"`.

**Resolved 2026-09-28.** Added `razorpay>=1.4.0` to requirements.txt.
Prod likely worked because Render's build cache had it installed from
an earlier state — worth confirming on next deploy.

### RESOLVED — lazy-import-inside-pool deadlock class (2026-09-28)

**Resolved 2026-09-28.** Swept all indented engine imports inside functions using DB connections. 16 candidates: 12 direct-connection (safe), 2 tests, 2 pooled but released before import. Zero remaining real deadlock sites.

Any code that holds a `db.get_pooled_connection()` and then triggers an
`from X import Y` where module X does DB work at import time will deadlock.
`ai_internship_engine` is a known offender — it runs `_ensure_tables()` on
import, so a lazy `from ai_internship_engine import ...` inside a function
that already holds a pool connection blocks forever on pool reacquire.

Fixed one instance 2026-09-28 in `admin_internship_metrics.py` (hoisted the
import to module level).

**Sweep candidates:** grep for lazy imports of DB-touching modules inside
functions that hold pool connections:

    Select-String -Path "*.py" -Pattern "^    from .*_engine import"
    Select-String -Path "*.py" -Pattern "^        from .*_engine import"

Each is a latent deadlock if the caller holds a pool connection.

**Verdict:** FLAGGED — sweep on next cleanup session.

### RESOLVED — FYP roadmap item #2 (Per-Chapter Expand) — browser verified (2026-09-28)

Shipped in `a9a6a04`; browser-verified 2026-09-28 against the 3.11.9 venv.

- `final_year_project_engine.expand_chapter_ai()` + `_fallback_expand()`
- `POST /api/fyp/expand-chapter` (auth + 10 cr via `fyp_expand_chapter`)
- Frontend: per-chapter Expand button + collapsible content div
- DOM-cached — second click toggles visibility, no re-fetch, no re-charge

**Server log evidence:** 4 expand clicks across 2 test runs → exactly 4 POST
requests to /api/fyp/expand-chapter, each returning 200 and calling OpenAI.
Zero extra requests on toggle clicks, proving the DOM cache works.

**Credit note:** verified against admin (`hr@charvakit.com`), which bypasses
deduction via `check_and_deduct()`. The route hits the credit guard
correctly; the bypass just skips the actual decrement. Non-admin charge path
is covered by every other gated route in the app.

**Verdict:** ✅ DONE

---

## Session 2026-09-28 (evening, part 4) — System audit + security sweep

**HEAD after:** 3f71788

### RESOLVED — 20 unguarded /api routes (commit 3f71788)
Admin-only: delete-user, escrow/release, escrow/resolve, kyc/review, enterprise/resume/pending, enterprise/resume/review, referral/pay
User-scoped: messaging/inbox, messaging/conversation, kyc/initiate, training/enroll, training/create-plan, training/update-progress, enroll/payment, enroll/check-access, career/alert, career/save-job, career/offer, career/salary

### RESOLVED — dead fetch to /api/notifications/send

**Resolved 2026-09-28.** Removed from templates/lock-in-breaker-pricing.html. Commit 03903a2.
File: templates/lock-in-breaker-pricing.html:155. Est: 5 min.

### RESOLVED — duplicate /api/payment/history route

**Resolved 2026-09-28.** Duplicate registration removed in commit 03903a2.
Registered twice in main.py. Est: 15 min.

### RESOLVED — /api/na/* auth review
20 routes with candidate PII. Est: 30 min.

### Completed — System audit
Produced SYSTEM-AUDIT-2026-09-28.md. 745 routes, 116 root Python files, 178 templates, 0 orphan engines, 20 routes fixed today.

---

## Session 2026-09-28 (evening, part 5) — Small-item sweep + lazy-import audit

**HEAD after:** 03903a2

### RESOLVED — dead /api/notifications/send fetch (commit 03903a2)
Removed from lock-in-breaker-pricing.html.

### RESOLVED — duplicate /api/payment/history route (commit 03903a2)
Two identical registrations at main.py:2877 and 2882. Removed the duplicate.

### RESOLVED — lazy-import-in-pool deadlock sweep
Swept all indented engine imports inside functions using DB connections.
Found 16 candidates; 12 were direct-connection (not pooled) so no deadlock risk,
2 were tests, and the 2 pooled candidates both release the connection before
the import. Key insight in database.py:30-38 — get_connection() returns a fresh
direct psycopg2 connection per call, so holding one during an import does NOT
block the pool. Only get_pooled_connection() shares state and can deadlock.

**Verdict:** zero remaining real deadlock sites. Sweep closed.

---

## Session 2026-09-28 (evening, part 6) — Session C: 4 unlisted AI tools shipped

**HEAD after:** (next commit)

### RESOLVED — 4 unlisted AI tools frontend wiring (4 commits)
All 4 tools had working backends (credit-gated) but the frontends were
marketing pages that either called notifyMe() or linked elsewhere.

- Neural Wireframe: rebuilt as real form (sketch description textarea
  + Generate button, 25 cr). Removed broken Razorpay Pro-flow that
  posted to /api/payment/create-order with wrong schema.
- Globalize.ai: rebuilt as URL + language form (15 cr). Removed
  localStorage-only 'Growth plan' flow.
- Legacy-Shift: rebuilt as code textarea (20 cr). Replaced notifyMe()
  placeholder.
- Agent-Ready: rebuilt as URL form (15 cr). Replaced notifyMe()
  placeholder.

All 4 use the same pattern as the 11-product sprint (2026-09-27):
form + auth header + 401/402 handling + recursive JSON renderer for
the AI's arbitrary nested response.

**Backend auth:** all 4 routes had require_credits_from_data already;
added require_auth_for_email in 6b22d61. Re-raise fix (a8e1275) made
the guards actually fire by re-raising HTTPException through the
broad except. Verified live: /api/ai/neural-wireframe without auth
-> 401.

**Verified E2E:**
- Neural Wireframe: pricing-page description -> real React+Tailwind JSX
- Globalize.ai: example.com -> Spanish translations + cultural adaptations
  + LOPDGDD compliance notes
- Legacy-Shift: legacy PHP snippet -> SQL injection + XSS + deprecated
  MySQL flagged; migration steps returned
- Agent-Ready: example.com -> JSON-LD schema + 2 micro-API definitions
  + product catalog structure

---

## Session 2026-09-28 close-out (Session C + full docs sync)

**HEAD:** e28c781 (ai-slop) / f58e63f (auth + cache)

### Final state

18 commits today. Two features shipped. Four AI tools rebuilt. Twenty-four security guards made live. Full docs sync. Complete backup.

### Commit chain (today)

```
7a40e95  docs: full sync to da15ef6 after Session C
da15ef6  feat(neural-wireframe): rebuild UI with real form + credits flow
10358ad  docs: Session C complete - 4 unlisted AI tools shipped
a7080cd  feat(agent-ready): rebuild UI with real URL form + credits flow
6b18873  feat(legacy-shift): rebuild UI with real code textarea + credits flow
05bf57f  feat(globalize): rebuild UI with real form + credits flow
9158f27  docs(dev-setup): curl.exe + PowerShell JSON-body gotcha
a8e1275  fix(security): re-raise HTTPException before broad except in 147 routes
83dc08a  docs: close small-item sweep - 3 flags resolved
03903a2  chore(cleanup): remove dead /api/notifications/send fetch + dup route
2cdba0e  docs: system audit 2026-09-28 + tracker sync
3f71788  fix(security): add auth guards to 20 unguarded /api routes
6b22d61  fix(auth): require_auth_for_email on 4 AI tool routes
ab6eba5  docs: FYP per-chapter expand verified E2E
75ce15f  refactor(admin): compact tiers + paginated table
1068809  docs: Item 4 tracker update
c4fb2a5  feat(admin): internship enrollments dashboard
a9a6a04  feat(fyp): per-chapter expand
```

### Shipped (features)

- FYP Per-Chapter Expand - 10 cr per chapter, DOM-cached, browser-verified
- Internship admin dashboard - /admin/internship-enrollments with KPIs, doughnut, CSV, filters, pagination

### Shipped (products)

- Neural Wireframe - sketch description -> React+Tailwind JSX (25 cr)
- Globalize.ai - URL + language -> nested localization report (15 cr)
- Legacy-Shift - code snippet -> vulnerabilities + migration plan (20 cr)
- Agent-Ready - URL -> JSON-LD + micro-APIs + product schema (15 cr)

All 4 replaced marketing stubs with real forms, auth headers, 401/402 handling, and recursive JSON renderers.

### Security wins

- 20 unguarded /api routes secured (3f71788)
- 4 AI tool routes now require email-match auth (6b22d61)
- **147 HTTPException re-raise clauses** (a8e1275) - the critical fix that made the 24 guards actually fire. Before this, the guards were dead code: broad except Exception swallowed HTTPException and returned HTTP 200.
- Lazy-import-in-pool deadlock sweep - zero remaining sites

### Cleanup

- Dead /api/notifications/send fetch removed from lock-in-breaker-pricing.html
- Duplicate /api/payment/history route removed

### Docs shipped

- SYSTEM-AUDIT-2026-09-28.md - full structural audit + Session C addendum
- MASTER-REFERENCE.md - synced to HEAD + v3.5-session-C-20260928
- ARCHITECTURE.md - added HTTPException re-raise pattern section
- KNOWN-ISSUES.md - 5 new fix rows
- OUTSTANDING-WORK-INVENTORY.md - Session C closures
- SESSION-CONTEXT.md - fresh resume pointer
- STATUS.md - Session 2026-09-28 summary
- DEV-SETUP.md - curl.exe JSON-body gotcha

### Backup

C:\\projects\\Charvak_Complete_Backup_20260928_230130.zip (50.56 MB)
- 562 source files
- 1368 .git history files
- 152 charvak_* tables (5.1 MB SQL dump)
- .env + .env.local included (secrets - do not share)
- embedding column excluded from charvak_exam_question_bank (regenerate with scripts/backfill_question_embeddings.py)

### Open flags (carried forward) - updated 2026-09-28

**Genuinely open (6):**

1. Premium Report product - product decision, 8-12 hrs
2. uvicorn reload invalidates browser tokens - dev-only defer
3. PayPal credits capture test - 5 min (Session B)
4. CachedStaticFiles ?v= - 30 min (Session B)
5. ai_courses_payments PayPal stub audit - 15 min (Session B)
6. PayPal credits webhook safety net - 30 min (Session B)

**Resolved since this list was first written (2026-09-28):**
- Voice-to-Web Option 2 (45ec344, a8c066e)
- /api/na/* auth review (18 routes admin-gated)
- AI-Slop Report Card detector (real fetch to products backend)
- Dead /api/notifications/send fetch (03903a2)
- Duplicate /api/payment/history route (03903a2)
- 4 unlisted AI tools frontend wiring (4 commits)

### Recommended next session

**Session B - PayPal hardening (~1 hr)** closes flags 5, 6, 7, 8.

---

## RESOLVED - C7 paid-tier sweep (2026-10-02, `abd653d`)

17 of 17 C7 templates now shipped. Sessions 3-8 closed the entire gap.
Every product page that advertised a paid tier now has either:

- A real credits-based purchase flow (AuditBot, Lock-In Breaker,
  Bridge, Marketing AI, Team Dashboard, Background Verification,
  Geo-Compliance, Reverse Staffing, Design-Token, Agency-Twin,
  LMS, Skill-Twin, University, Legacy-Shift, Micro-Squads lead form), or
- A notify-me interest capture (Silent-Killer, honesty-rewritten)

### C7 completion by session

| Session | Templates |
|---|---|
| 3 | AuditBot (2 tiers) |
| 4 | Lock-In Breaker (2 tiers) |
| 5 | Micro-Squads (sales-lead flow) |
| 6 | Developer Entropy, AI-Slop, Design-Token, Geo-Compliance (2), Agency-Twin, Reverse Staffing, Bridge, Marketing AI, Team Dashboard, Background Verification |
| 7 | Silent-Killer (honesty rewrite), Skill-Twin AA4d, LMS, Hosted booking page |
| 8 | University (3 tiers), Legacy-Shift (migration tier) |

### Credit design principle (applied throughout)

Ship paid tiers as credits, not separate Razorpay charges. Reuses
FEATURE_CREDITS, check_and_deduct, and charvak_credit_usage_history.
One-time credit purchase already works (Fix A/B/C from 2026-09-12).
No new payment paths = no new webhook signature bugs.

Only exception: Micro-Squads (Rs 49,999) uses a sales-lead flow, not
self-serve checkout.

### New tables added during the sweep (17)

charvak_auditbot_fixes, charvak_auditbot_subscriptions,
charvak_lock_in_engagements, charvak_micro_squad_leads,
charvak_bridge_premium_reports, charvak_marketing_booking_kits,
charvak_team_subscriptions, charvak_geo_compliance_contracts,
charvak_geo_compliance_hiring, charvak_reverse_staffing_subscriptions,
charvak_booking_requests, charvak_skill_twin_results,
charvak_skill_twin_badges, charvak_university_subscriptions,
charvak_legacy_shift_reports, charvak_course_enrollments (LMS),
plus supporting subscription/index tables

### Verified

Every tier was E2E-tested with `test-register-2026-09-24@example.com`:
form -> auth -> credits -> AI/output -> persisted row -> balance
deduction. Sample verifications:

- AuditBot: SCAN-9F09F99A, FIX-88A2A1FA2C5D
- Lock-In Breaker: LIE-A746A84F9CEF, LIE-5C94EAF47EFD
- Micro-Squads: LEAD-2356D884840F (0 credits, lead-only)
- Skill-Twin: real badge purchase, idempotent, verified at /badge/{id}
- University: UNI-EA076ACA, tier=starter, 20000 -> 16000
- Legacy-Shift: LS-225427023418, 16000 -> 14975

No further C7 work remains.


---

### FLAGGED — /ai-assessment renders ai-bridge.html (URL/content mismatch) (2026-10-02)

GET /ai-assessment (main.py:6540) renders i-bridge.html with the
title "AI Career Assessment - Charvak IT Consulting". But ai-bridge.html
is the AI Bridge product template — no career-assessment flow exists.

**Fix:** Session 10 (Phase 1 of CAREER-ASSESSMENT-PLAN.md) — create
	emplates/ai-assessment.html and update the route to render it.

**Est:** tracked in the plan doc.

**Verdict:** SCHEDULED — Session 10


### FLAGGED — Silent-Killer continuous monitoring (cron + alerts) (2026-10-02)

Session 9a shipped on-demand scanning + watch dashboard. The "Notify Me
When Continuous Monitoring Ships" button remains on
/silent-killer for the automatic-scheduled-scan feature.

**Fix:** Session 9b — enhanced_email.send_silent_killer_alert(),
POST /api/cron/silent-killer-scan (X-Cron-Secret auth), Render cron
job (manual dashboard config), frontend alert timeline.

**Est:** ~3-4 hrs. Requires Render dashboard access.

**Verdict:** SCHEDULED — Session 9b


### FLAGGED — Session 9 quick wins (2026-10-02)

Three deferred items, ~1.5 hrs total:

1. #3 PayPal live capture test (~5-10 min, \.39 charge + refund)
2. ARCHITECTURE.md static-assets section still says immutable,
   max-age=1y — needs max-age=3600, must-revalidate
3. scripts/_*.py cleanup (~30 min — 20+ one-off dev scripts)
4. Doc pass on 4 trackers (~30 min)

**Verdict:** SCHEDULED — any session


### FLAGGED — Python module escape sequences to check (2026-10-02)

During Session 9a, noticed products_engine.py had \u2014 appearing
inside normal string literals that were being written through a Python
script. The behavior was correct on this run (the em-dash landed as a
real U+2014), but the mechanism (Python string escaping through a
PowerShell here-string into a Python script) is fragile and produced
two misses earlier in the session (B2 stub anchor, Patch D JS).

**Fix:** standardize on [System.IO.File]::WriteAllText(...) for any
future multi-line doc or code write, or keep patches under 100 lines
each. Already documented in this session's workflow.

**Verdict:** documented, no code change needed

---

### FLAGGED — Indian Language AI: assessment questions are generated but never shown (2026-10-02)

Session C fixed the authToken ReferenceError in templates/indian-language-ai.html.
Both forms now reach the backend. But the Language Assessment flow stops
at "Assessment Created!"

**The gap:**
- Backend /api/indian-languages/assessment generates N questions, stores
  them in charvak_lang_ai_assessments.questions (JSONB), returns only a
  summary (native_name, total_questions, skill, difficulty).
- Frontend shows the summary and never renders the questions, never
  collects answers, never calls /api/indian-languages/submit.
- The user sees "5 questions created" and no way to answer them.

**The fix:**
1. Backend: either return questions in the create response, or add
   GET /api/indian-languages/assessment/{assessment_id}/questions
   (auth-gated, email match)
2. Frontend: render questions below the summary
   - MCQ questions: radio buttons
   - Free-text questions: textarea
3. Add "Submit Answers" button that POSTs to /api/indian-languages/submit
4. Display score + pass/fail badge

**Est:** 30-60 min. Self-contained.

**Verdict:** SCHEDULED — next cleanup session


### FLAGGED — Indian Language AI vs Career Assessment: relationship TBD (2026-10-02)

/indian-language-ai and /ai-assessment (the Career Assessment product
planned in CAREER-ASSESSMENT-PLAN.md) overlap. Both produce skill
assessments. Questions:

- Should Indian Language AI stay a lightweight translation + quick-
  assessment tool, separate from the Career Assessment product?
- Or should Indian Language AI become the "Indian language flavor" of
  Career Assessment (same engine, different locale)?
- Or should Career Assessment support all 34 languages via the existing
  i18n system, making Indian Language AI redundant?

**Recommendation for now:** keep separate. Career Assessment (Session 10)
uses /api/career-assessment/* with its own UI. Indian Language AI is its
own thing and just needs its question-display gap closed.

**Revisit:** after Career Assessment Phase 1 ships. If overlap becomes
painful, consolidate in Session 12+.

**Verdict:** DEFERRED — product decision, revisit after Session 10

---

### RESOLVED — Indian Language AI: real MCQ scoring + varied answer positions (2026-10-02, 96535c0 + 4385008)

The flag from earlier tonight ("questions generated but never shown")
is closed. The full fix shipped:

- Real MCQ scoring (deterministic correctness, not "count answers")
- Question display (radio buttons with 4 options)
- Submit flow wired to /api/indian-languages/submit
- Auth on /submit (was IDOR — commit 4385008)
- correct_index stripped from frontend response (cheat prevention)
- Server-side option shuffle (bulletproof against lazy AI)
- 10/15/20 question selector
- Static mojibake fallback replaced with clean English MCQ templates

Verified E2E: junk answers = 0%, real answers = 100%.

The other flag — "Indian Language AI vs Career Assessment relationship"
— remains DEFERRED. Revisit after Session 10.

---

### RESOLVED — /ai-assessment renders ai-bridge.html (URL/content mismatch) (2026-10-02, 5946ec3)

The flag from earlier tonight is closed. /ai-assessment now renders
templates/ai-assessment.html - a real 3-step career readiness wizard
calibrated to (role x industry x level).

Session 10 Phase 1 shipped:
- career_assessment_engine.py (new, 760 lines)
- 6 routes under /api/career-assessment/*
- 3 new credit keys (15/25/35)
- New 3-step wizard template (443 lines)
- 106 roles, 66 industries, 7 levels, 3 sizes
- Real MCQ generation via OpenAI (role-calibrated prompts)
- Deterministic scoring + persisted to /my-results
- Verified E2E + prod endpoints live

Session 11 (Phase 2) will add all non-MCQ formats.
Full plan in CAREER-ASSESSMENT-PLAN.md.

Verdict: RESOLVED

---

### FLAGGED — Session 13 exclusions (2026-10-03)

Phase 3 of Career Assessment ships WITHOUT these features, deliberately:

1. Retake comparison charts — nice-to-have
2. Certificates / badges — Phase 4
3. Live adaptive mid-assessment — deferred indefinitely (see plan doc
   for rationale)
4. Peer benchmarking — Phase 4

These are not bugs, not omissions. They are scope boundaries.
Session 13 delivers: topic tagging, skill gap, cross-assessment
adaptation, ability update, learning path.

Verdict: DOCUMENTED — no action needed

---

### FLAGGED — difficulty-aware ability update (2026-10-03)

`ability_engine.update_from_assessment` supports a `difficulty=` kwarg
but nothing passes it. Result: a 100% on an "intern" assessment and a
100% on an "executive" assessment produce the same Elo delta (~12
points with K=25). Real difficulty should scale the update.

Fix: map career level_key to a difficulty_value (intern=600, junior=800,
mid=1000, senior=1200, staff=1400, manager=1500, executive=1600) and
pass it through from complete_assessment. Est: ~30 min.

Verdict: SCHEDULED — Session 14

---

### RESOLVED — PayPal credits capture test (Session 9 quick win) (2026-10-03, db9e2a1)

The Session B flag (#3 PayPal live capture test) is closed. Full
sandbox flow verified end-to-end with a US sandbox buyer + US sandbox
merchant:

- Order created: 1WH95310FS6736459, $5.99 USD
- Buyer approved via sandbox checkout
- Server captured: 9WF9133469670842D, status COMPLETED
- /api/credits/purchase granted 1000 credits for the Pro plan
- Second call: already_credited=true (idempotency verified)
- Balance: 500 -> 1500

Code changes required to enable sandbox testing (now committed):
- payment_engine.py: new PAYPAL_MODE env var + _paypal_base() helper.
  Defaults to "live" so prod is unchanged. Sandbox mode routes PayPal
  API calls to api-m.sandbox.paypal.com.
- main.py: /api/region accepts ?country= / ?currency= dev override
- static/js/currency-utils.js: passes ?country= from the URL through
  to /api/region

Verified prod is unaffected:
- Render still uses live PayPal (client_id prefix "Aaj...")
- Local .env has sandbox creds (prefix "BAAP...")
- .env is gitignored; never reaches Render

Follow-up (1 min, requires Render dashboard access):
- Add PAYPAL_MODE=live explicitly to Render's env vars for clarity

Verdict: RESOLVED

---

### RESOLVED — PayPal credits capture test (Session 9 quick win) (2026-10-03, db9e2a1)

The Session B flag (#3 PayPal live capture test) is closed. Full
sandbox flow verified end-to-end with a US sandbox buyer + US sandbox
merchant:

- Order created: 1WH95310FS6736459, $5.99 USD
- Buyer approved via sandbox checkout
- Server captured: 9WF9133469670842D, status COMPLETED
- /api/credits/purchase granted 1000 credits for the Pro plan
- Second call: already_credited=true (idempotency verified)
- Balance: 500 -> 1500

Code changes required to enable sandbox testing (now committed):
- payment_engine.py: new PAYPAL_MODE env var + _paypal_base() helper.
  Defaults to "live" so prod is unchanged. Sandbox mode routes PayPal
  API calls to api-m.sandbox.paypal.com.
- main.py: /api/region accepts ?country= / ?currency= dev override
- static/js/currency-utils.js: passes ?country= from the URL through
  to /api/region

Verified prod is unaffected:
- Render still uses live PayPal (client_id prefix "Aaj...")
- Local .env has sandbox creds (prefix "BAAP...")
- .env is gitignored; never reaches Render

Follow-up (1 min, requires Render dashboard access):
- Add PAYPAL_MODE=live explicitly to Render's env vars for clarity

Verdict: RESOLVED

---

### RESOLVED — difficulty-aware ability update (2026-10-03, 36a400f)

The COMMITMENT.md flag is closed. ability_engine.update_from_assessment
now receives difficulty based on the career level:

- ability_engine.DIFFICULTY_VALUE extended with career level keys:
  intern=600, junior=800, mid=1000, senior=1200, staff=1400,
  manager=1500, executive=1600
- results_system.record_assessment_result accepts difficulty= and
  forwards it (was hardcoded 'medium')
- career_assessment_engine.complete_assessment passes difficulty=level

Verified: 100% on intern -> +2.18 Elo; 100% on executive -> +23.26 Elo
(was +12.00 for both before the fix).

Also stripped a pre-existing UTF-8 BOM from results_system.py — the
real cause of a phantom "invalid non-printable character U+FEFF"
ast.parse error during patching.

Verdict: RESOLVED

---

### FLAGGED — LMS progress ownership check (2026-10-03, Session 14 security sweep)

`/api/lms/progress/{enrollment_id}` was fully open (any caller could
read any enrollment's progress). Session 14 added `require_auth(request)`
so it now requires a logged-in user.

**Still missing:** ownership check. Any logged-in user can read any
enrollment's progress by ID. The enrollment_id may not be guessable in
practice, and the data returned is minimal (percentage only), so this
is Medium priority.

**Fix:** add ownership verification. Requires `lms_engine.get_progress`
to expose the enrollment's owner email, OR a new helper
`lms_engine.get_enrollment_owner(enrollment_id)`. Then:

    require_auth_for_request(request)  # returns caller
    owner = lms_engine.get_enrollment_owner(enrollment_id)
    if owner != caller_email and not is_admin:
        return 403

**Est:** ~30 min (engine change + route change + E2E)

**Verdict:** SCHEDULED — Session 15 or 16

---

### RESOLVED — Rotated PayPal client secret (2026-10-03)

Session 15 follow-up. The PayPal client secret was displayed in a chat
during Session 12 and flagged for rotation. Rotated the LIVE secret in
the PayPal Developer Dashboard.

- Generated new secret via PayPal Dashboard -> Apps & Credentials
  -> Live API Credentials -> Generate New Secret
- Updated PAYPAL_CLIENT_SECRET in Render env vars (prod)
- Updated PAYPAL_CLIENT_SECRET in local .env
- Verified prod /api/payment/status still returns paypal: true
- Verified sandbox auth still returns 200 with the new secret
- Old secret deleted from the PayPal dashboard after verification

Not related to this: SYNC_API_KEY / SYNC_API_SECRET were flagged
separately as hardcoded defaults in the public repo. Those still need
rotation — see "Rotate PayPal + SYNC keys" in the Session 16 queue.

Verdict: RESOLVED

---

### RESOLVED — Rotated SYNC_API_KEY + SYNC_API_SECRET, stripped fallbacks (2026-10-04, 30f9bf3)

Session 12 backlog item. The SYNC_API_KEY and SYNC_API_SECRET had
hardcoded fallback defaults in api_sync.py, visible in the public repo:

  API_SECRET = os.getenv("SYNC_API_SECRET", "charvak-doketsrb-sync-secret-2024")
  API_KEY    = os.getenv("SYNC_API_KEY",    "cvk_sync_key_2024")

If Render env vars were missing, the app would silently accept these
public defaults.

What was done:
- Rotated both values on Charvak (Render env vars)
- Updated local .env with the new values
- Updated DoketsRB (Vercel) env vars with the same values
- Patched api_sync.py: removed fallbacks, added startup warning guard
- Verified: prod /api/sync/health + /api/sync/jobs return 200 with
  the new key
- Module test: API_SECRET and API_KEY are empty strings when env vars
  are cleared (no fallback)

Monitoring:
- Charvak Render logs show no 401s on /api/sync/*
- Will confirm DoketsRB alignment on the next sync trigger from Vercel

Verdict: RESOLVED

## FLAGGED — DoketsRB bidirectional sync (Session 38+)

**The infrastructure is real, the wiring is pending.**

`api_sync.py` is a complete, secured sync module with six endpoints:
- POST /api/sync/resume       (DoketsRB -> Charvak)
- POST /api/sync/application  (DoketsRB -> Charvak)
- GET  /api/sync/jobs         (Charvak -> DoketsRB, for their tracker)
- POST /api/sync/skills       (DoketsRB -> Charvak, gap analysis)
- GET  /api/sync/status/{user_id}
- GET  /api/sync/health

Security is enforced (SYNC_API_KEY + HMAC signature, fail-closed).
Tables exist: charvak_synced_users, charvak_synced_applications,
charvak_ats_sync_log, charvak_doketsrb_score_tokens,
charvak_doketsrb_score_events, charvak_doketsrb_bundle_subs.

**Current state:** 0 rows in the sync tables. The endpoints are
ready to receive, but nothing is sending yet.

**What to build:**

1. **DoketsRB-side alignment** (external, non-code)
   - Verify SYNC_API_KEY and SYNC_API_SECRET match on both Vercel
     and Render (rotated in Session 15)
   - DoketsRB calls /api/sync/resume on profile save
   - DoketsRB calls /api/sync/application on tracker update
   - DoketsRB calls /api/sync/skills after ATS scan
   - Estimated: coordination effort, minimal code

2. **Charvak-side UX** (Session 38+)
   - "Sync now" button on /job-board -> pulls latest from DoketsRB
   - Sync status indicator on /career-center panel
   - Show "Last synced: 2 min ago" for user confidence
   - `/api/sync/pull` route (user-triggered) that calls DoketsRB's
     public endpoints and returns the merged state
   - Estimated: ~1 session

3. **The full picture for users** (Session 39+)
   - Onboarding flow: "Connect your DoketsRB account" with OAuth-like link
   - Auto-sync on page load when user is linked
   - Real-time status: "Your DoketsRB resume is in sync as of [time]"
   - Estimated: ~1 session

**Why this matters:**
The DoketsRB sync is the bridge between resume-building (DoketsRB)
and job-matching (Charvak). It's how a user's resume ends up matched
to roles they can actually apply for. Without it, the two platforms
are separate products. With it, they're one pipeline.

**Trigger to start:** DoketsRB-side readiness to call the six endpoints.
Could start with just #1 + #2 for a v1 sync status.

**Verdict:** FLAGGED — Session 38+.
