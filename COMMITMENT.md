# Charvak — Commitment Tracker

**Purpose:** Track every planned-but-not-completed item. Nothing gets lost again.
**Created:** 2026-09-20
**Last updated:** 2026-09-25
**HEAD:** c2c67d7

### FLAGGED — /api/assessment/* routes appear to be dead code (2026-09-26)

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



### FLAGGED — Mock Drives + Versant routes lack auth (2026-09-26)

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

### FLAGGED — lms.html minified JS needs manual auth wiring (2026-09-27)

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

### FLAGGED — bridge.html premium flow broken (2026-09-27)

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

### FLAGGED — auth wiring status by cluster (2026-09-27)

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

### FLAGGED — 11 product templates: frontend wiring required (2026-09-26)

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

### FLAGGED — AI feature verification sweep — full list (2026-09-26)

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


### FLAGGED — student_suite auth gap (2026-09-26)

`/api/student/assignment` and `/api/student/research` now call
`require_auth_for_email` (fixed in Phase 3 of tonight's session).

Still missing: `/api/student/subscribe` has NO auth check. Anyone can create a
subscription row for any email. Same IDOR pattern.

Also `/api/student/stats` has NO auth — leaks global subscription/usage counts.

Fix: add `require_auth_for_email(request, email)` to subscribe, and
`require_admin(request)` to stats. ~5 min.

Verdict: FLAGGED — small follow-up

### FLAGGED — uvicorn reload invalidates browser tokens (2026-09-26)

`auth.active_tokens` is in-memory. Every `uvicorn --reload` restart wipes it.
Browser localStorage keeps the stale token, causing 401/403 on every API call
until the user clears localStorage and logs in again. Confusing during dev.
In production (long-running process) this only happens on deploy.

Possible fixes (future):
- Persist tokens to DB with expiry
- Add a frontend handler that auto-clears localStorage on repeated 401
- Dev-only: warn on reload that tokens are invalidated

Verdict: DEFERRED — low priority for prod, annoying for dev.

### FLAGGED — ai_service/generate_* functions still unverified (2026-09-26)

Already in tracker from earlier tonight. 5 functions routed through
ai_service.call_openai() have not been E2E-tested since the fix:
- neural_wireframe_to_code
- localize_website
- generate_legal_contract
- analyze_legacy_code
- generate_assessment_questions

Verdict: SCHEDULED — own session

### FLAGGED — 11 AI Products need same audit as tools (2026-09-26)

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

### FLAGGED — Post-ai_service-fix verification sweep (2026-09-26)

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

### FLAGGED — Voice-to-Web hardcodes USD in generated prices (2026-09-26)

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

### FLAGGED — `email_verification.is_verified()` bare except (2026-09-26)

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

### FLAGGED — Voice-to-Web Option 2 — auto-deploy infrastructure (2026-09-25)

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

### FLAGGED — Anti-bot for /contact (2026-09-25)

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

### N1 â€” State exam smoke test + content quality fixes

- **Completed:** 2026-09-22 (Session N1) â€” commits `9a8ce83` through `00aec90`
- **Catalog:** `upsc_cse` + `neet_ug` added (136 â†’ 138 exams)
- **Question bank:** 5 state PCS exams topped to 40+ per topic; ~13,600+ rows total
- **Mock test performance:** batched bank query (3 DB calls â†’ 1); 2-4s â†’ 0.4s
- **Connection pool:** `get_pooled_connection()` + `release_pooled_connection()` in `database.py`; `exam_prep_engine` hot paths migrated; startup warmup in `main.py`
- **Language hints:** AI prompt forces correct script for 10 language sections (Bengali, Hindi, Tamil, Telugu, Marathi, Kannada, Malayalam, Gujarati, Punjabi, Urdu)
- **Practice route fix:** `/api/exam/ai-questions` redirected from legacy `ai_question_generator` to `exam_prep_engine` â€” was serving wrong content for state-specific topics
- **Verified in prod (Render logs):**
  - `[startup] DB connection pool warmed` âœ…
  - `bank lookup: X/Topic -> 10 rows (wanted 10)` for all 5 state PCS exams âœ…
  - Bengali content serves correctly âœ…
  - Credit deduction: 3 cr practice / 15 cr mock âœ…
- **N1.5 Legal audit:** PASSED â€” all 4 pages render on `www.charvakit.com` (terms, privacy, refund, cookie-policy), plus `accessibility`
- **Follow-ups:**
  - Semantic duplicate questions (near-identical wording across topics) â†’ C13
  - Two engines to consolidate (`exam_prep_engine` vs `ai_question_generator`)
  - Apex domain `charvakit.com` returns 404; optional Cloudflare redirect to `www`

---

### N2 â€” System-wide semantic dedup (2026-09-22)

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

### C1 â€” Assessment AI for global languages

- **Completed:** 2026-09-21 (Session G1) â€” commit `c3dc68a`
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
- **Verified:** live OpenAI smoke test â€” es/fr/ja/ar/zh/hi/te/ta/ko/de all
  returned native-script questions (5 each)
- **Note:** `_generate_questions_static` deliberately still covers only 12 Indian
  languages. Non-Indian + AI failure returns `[]`, so caller falls back explicitly.

---

### C4 â€” Adaptive difficulty

- **Completed:** 2026-09-21 (Session G2) â€” commit `15193f9`
- **What shipped:**
  - New `charvak_user_ability` table (migration + engine self-init)
  - New `ability_engine.py` â€” Elo math, `get_ability`,
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


### C5 â€” Curated question banks

- **Completed:** 2026-09-21 (Session G3) â€” commit `f4a3fd3` + local seed run
- **What shipped:**
  - New `scripts/seed_exam_question_bank.py` â€” idempotent, resumable,
    throttled batch generator for `charvak_exam_question_bank`
  - Phases: `--phase 1` (top 10 exams, ~35 pairs), `--phase 2`
    (all 67 Indian exams, 207 pairs)
  - `--resume` skips pairs already at target count
  - Runs through `exam_prep_engine.generate_questions` â€” same path
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
  - Runtime 88 min vs 33 min estimate â€” OpenAI averaged ~25s/call
- **Backwards compatible:** no user-facing code changes.

---


### C6 â€” Assessment UI translations

- **Completed:** 2026-09-21 (Session G5) â€” commits `fa83917` through `acd450e`
- **What shipped:**
  - **`static/js/i18n.js`** â€” client-side loader (~5.5 KB)
    - Language priority: localStorage â†’ `window.CHARVAK_LANG` â†’ Accept-Language â†’ `en`
    - Replaces `[data-i18n]`, `[data-i18n-placeholder]`, `[data-i18n-title]`
    - Exposes `window.changeLanguage()` + `window.t()` for programmatic use
    - Graceful fallback: missing keys render English
  - **`static/locales/en.json`** â€” 278 source strings across 16 groups
  - **17 language files** â€” hi, te, ta, kn, ml, mr, bn, gu, pa (Indian);
    es, fr, ar, zh, de, pt, ru, ja (Global)
  - **`scripts/translate_ui.py`** â€” batch translator (OpenAI gpt-4o-mini, temp 0.2)
  - **~197 data-i18n attributes** across 7 templates:
    - `base.html` â€” 90 (nav, footer, topbar, user menu)
    - 6 assessment templates â€” ~107 (reports, advanced-assessment,
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

### C7 â€” Build 13 Category-B feature backends (post-G6)

- **Discovered:** 2026-09-21 (Session G6 revenue audit)
- **Issue:** 13 templates have `processCharvakPayment` UI + callback
  but NO backend endpoint. Currently take payment intent but deliver
  no actual feature.
- **Affected templates:**
  1. `agency-twin.html` â€” â‚¹2,999 Agency-Twin Pro
  2. `agent-ready.html` â€” â‚¹399 Agent-Ready Wrapper
  3. `ai-internship.html` â€” variable (weeks Ã— program)
  4. `ai-slop-quarantine.html` â€” â‚¹149 AI-Slop Clean
  5. `auditbot.html` â€” â‚¹299 Fix + â‚¹999 Subscription (2 features)
  6. `design-token-sentinel.html` â€” â‚¹299 Design-Token Pro
  7. `developer-entropy.html` â€” â‚¹299 Monitoring
  8. `geo-compliance.html` â€” â‚¹199 Contract Gen + â‚¹999 Global Hiring (2)
  9. `legacy-shift.html` â€” â‚¹4,999 Migration
  10. `lock-in-breaker.html` â€” â‚¹4,999 + â‚¹4,999 (2)
  11. `marketing-ai.html` â€” â‚¹299
  12. `micro-squads.html` â€” â‚¹49,999 Assembly
  13. `reports.html` â€” â‚¹299 Premium Report
  14. `skill-twin.html` â€” â‚¹499 Verification
  15. `team-dashboard.html` â€” â‚¹1,999 Pro
  16. `skill-twin` variants
- **Temporary handling (G6):** replace payment button with
  "Notify Me" CTA. Captures intent, no fraud risk.
- **Future work per feature:**
  - Build backend engine + endpoint
  - Add `FEATURE_CREDITS` key
  - Guard with `require_credits_from_data`
  - Wire frontend to credit purchase flow
- **Est:** 3-5 hr per feature Ã— 15 features = **~45-75 hr total**
- **Priority:** Medium â€” tackle top 3 by market demand first
- **Verdict:** DEFERRED (post-G6, iterative)**

- **Expanded (2026-09-21, Session G6 revenue audit):** 5 additional
  templates confirmed to have the same problem â€” dead
  `processCharvakPayment` callbacks + working free paths with no gate:
  1. `events.html` â€” RSVP works free; â‚¹499 button was dead
  2. `ats.html` â€” no form exists; â‚¹999 button was dead
  3. `lms.html` â€” no real enroll endpoint; â‚¹999 button was dead
  4. `micro-internship.html` â€” form on `/post-micro-project` ignores
     the `?payment_id=` redirect; â‚¹2,000 bypassed
  5. `university.html` â€” no form exists; â‚¹4,999 button was dead

  **G6 handling:** All 5 buttons replaced with `notifyMe()` (matches
  the pattern used across 13 other templates). No working flow was
  removed â€” the free paths remain intact for now.

  **Future work per template:**
  - Build proper form (events needs RSVP confirmation page; ats
    needs provider/api_key inputs; university needs registration form)
  - Add backend endpoint guard where one exists
  - Wire frontend to `notifyMe()` â†’ real "Buy Credits" flow when
    the feature ships

- **Total C7 scope:** **18 templates** (~25 features across them)
- **Est (updated):** ~60-90 hr total, iterative by priority


### C9 â€” Catalog expansion: 12 missing exams

- **Completed:** 2026-09-22 (Session L) â€” commit `f15464f`, merged on main
- **Discovered:** 2026-09-21 (CBT/CAT audit against the master exam list)
- **Issue:** Catalog held 67 exams / 8 categories â€” missing key Indian CBT exams
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
  - IELTS Academic deferred â€” needs AI writing/speaking scoring path
  - RRB ALP CBAT (Computer-Based Aptitude Test) module â€” different question type
  - Adaptive engine (IRT) for GMAT/GRE/NMAT/BITSAT â€” longer roadmap
  - Re-seed `charvak_exam_question_bank` for the 12 new exams (currently on-demand)

---

### C8 â€” Revenue enablement (G6)

- **Completed:** 2026-09-21 (Session G6) â€” commits `0dcf2a8` through `92ce054`
- **What shipped:**
  - **`credit_guard.py`** â€” reusable `require_credits_from_data(data, feature)`
    + `require_credits_dep` dependency factory; 401 for missing email,
    402 for insufficient credits
  - **Pricing (repriced):** Starter â‚¹199/300cr, Pro â‚¹499/1000cr,
    Premium â‚¹999/2500cr, Enterprise â‚¹4999/15000cr
  - **8 new feature keys** in `FEATURE_CREDITS` (mock_test repriced 20â†’15)
  - **10 routes guarded** across exam / assessment / mock drive
  - **`exam-prep.html` rewritten** â€” 4 credit packages + balance banner;
    fake subscription system (subscribeExam, planLimits, canPractice,
    showUpgradeModal) removed; demo@ fallback removed
  - **`main.js` 401/402 handler** â€” global fetch wrapper dispatches
    `charvak:401` / `charvak:402` events
  - **`indian-language-ai.html`** â€” migrated to credits (2 routes guarded)
  - **18 dead payment buttons** replaced with `notifyMe()` (interest capture);
    `/api/features/notify` + `charvak_feature_interest` table added
  - **`payment-helper.js`** â€” region-aware modal (India â†’ Razorpay first,
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


### M-1 â€” IELTS Academic (Listening/Reading/Writing)

- **Completed:** 2026-09-22 â€” commit `3c7e664` (merge of `15482f6`)
- **What shipped:**
  - `ielts_academic` added to `exam_prep_engine` catalog (80 exams, 9 categories)
  - NEW `ielts_engine.py` (~311 lines) â€” stateless orchestration:
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


### M-2 â€” RRB ALP CBAT

- **Completed:** 2026-09-22 â€” commit `<hash>`
- **What shipped:**
  - NEW `cbat_engine.py` (~594 lines) â€” DB-backed engine
    for 6 sub-tests: Analogies, Decision Making, Numerical Ability,
    Memory (Short/Long), Following Directions
  - NEW migration `20260922_cbat.sql` â€” 2 tables
    (`charvak_cbat_sessions`, `charvak_cbat_answers`)
  - NEW `templates/cbat.html` â€” timed question delivery, SVG rendering,
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


### M-3 â€” State Government Exam Coverage

- **Completed:** 2026-09-22 â€” commits `f471b67`, `1c0d161` (merged via `2a91239`, `1da969e`)
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
  - Zero new engines, tables, routes, or templates â€” all reuse
    existing infrastructure
  - AI question generation works for every new exam
- **Verified:**
  - Prod shows 136 exams / 12 categories
  - AI generation confirmed for new exams
- **Coverage:** all major Indian states across PCS / Police / TET


### M-3.5 â€” Prompt hardening + difficulty calibration

- **Completed:** 2026-09-22 â€” commit `43bc281` (merge of `43c20d2`)
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

### C13 â€” Curated question banks (Session M-4)

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

## ðŸ”´ CRITICAL â€” Must Fix

### C2 â€” `voice_to_web_engine.py` persistence

- **Discovered:** 2026-09-20 (was flagged as B-2, never executed)
- **Issue:** 5 in-memory stores (`websites`, `domains`, `updates`, `support_tickets`, `seo_configs`)
- **Action:** Design tables + migration + refactor + test
- **Est:** ~1 hr
- **Target:** Session B-2
- **Status:** SKIPPED on 2026-09-21 in favor of C1. Re-schedule per priority.

### C3 â€” RTL UI support â€” DEFERRED 2026-09-21

- **Discovered:** 2026-09-20 (`base.html` has `<html lang="en">` hardcoded)
- **Original issue:** Arabic users see LTR layout despite `dir="rtl"` in config
- **Why deferred:** Only 1 of 34 languages is RTL (`ar`). No evidence of an
  Arabic-speaking user base in any project doc. RTL-layout-with-English-text
  is worse UX than clean LTR â€” the right sequence is C6 (content i18n) FIRST,
  then C3.
- **Escalation trigger (any of):**
  1. A real Arabic-speaking user or customer appears
  2. Sales/marketing targets MENA region
  3. C6 (assessment UI translations) ships â€” then C3 makes sense as follow-up
- **When triggered:** ~2 hr (dynamic `lang`/`dir`, bootstrap RTL swap,
  cookie picker, ~2 CSS overrides in `static/css/style.css`)
- **Verdict:** DEFERRED (product decision â€” no current user base)

---

## ðŸ” NEEDS VERIFICATION

### V1 â€” Doc sprawl

- **Check:** List all .md files in root
- **Concern:** Duplicates may exist (KNOWN-ISSUES vs FINAL-STATUS, etc.)
- **Action:** Verify next audit

### V2 â€” whatsapp_bot.py JSON mode â€” FALSE ALARM

- **Discovered:** Line 60 uses `response_format="text"` â€” but this is
  `audio.transcriptions.create` (Whisper), NOT chat completions.
  Text format is correct for Whisper.
- **Line 89** (the only LLM call) uses JSON mode correctly.
- **Verdict:** âœ… No bug. No action needed.

### V3 â€” 34-language claim vs delivered

- **Check:** Count actual supported languages
- **Concern:** Site copy says 34; actual may be less
- **Status:** âœ… RESOLVED 2026-09-21 â€” `global_config.LANGUAGES` has 34 languages,
  and as of Session G1 `indian_language_ai._generate_questions` serves all of them
  via AI. Copy claim is now accurate for the assessment flow.

---


### V4 â€” Dev and prod share one Render Postgres

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
    seed script having run â€” because the script never ran in Render's
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


### V5 â€” Local shell env var overrides .env DATABASE_URL

- **Discovered:** 2026-09-22 (Session M-2 verification)
- **Reality:** `.env` points to Render prod DB. But setting
  `$env:DATABASE_URL` in PowerShell to a local Postgres URL makes
  Python's `load_dotenv()` a no-op â€” the shell value wins.
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
| D2 | `ai_internship_engine.submit_work` random score placeholder | 2026-09-20 |
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

1. ~~**Session B-2**~~ â€” voice_to_web persistence (C2)  [SKIPPED, re-schedule later]
2. ~~**Session G1**~~ â€” Assessment AI for 34 languages (C1)  âœ… DONE 2026-09-21
3. ~~**Session G4**~~ â€” RTL UI (C3)  [DEFERRED 2026-09-21 â€” no Arabic user base]
4. ~~**Session G2**~~ â€” Adaptive difficulty (C4)  âœ… DONE 2026-09-21 (commit `15193f9`)
5. ~~**Session G3**~~ â€” Question banks (C5)  âœ… DONE 2026-09-21 (commit `f4a3fd3`)
6. ~~**Session G5**~~ â€” Assessment i18n (C6)  âœ… DONE 2026-09-21

**All CRITICAL items resolved.** Remaining: C2 (parked), C3 (deferred).
**Dead code cleanup completed 2026-09-21 (Session G2-pre):**
- Deleted `assessment_complete.py` (in-memory stub, zero frontend callers)
- Removed 5 orphaned `/api/assessment/*` routes from `main.py`
- Commits: `bdf32fa`, `8951c9b`
---

## ðŸ§  PROCESS LESSONS LEARNED

### L1 â€” PowerShell + Python file patching is fragile (Session G1, 2026-09-21)

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
  **Notepad (manual edit)** â€” verified working in Session G1
- For file-state questions, trust **`git diff --exit-code`** over any
  PowerShell string measurement
- Always `git diff` before commit and `git push` after â€” git is the durable backup

### L2 â€” Pager stalls in terminal scripts

`git diff` without `--no-pager` opens `less` and blocks non-interactive scripts.
Recommended: `git config --global core.pager ""` on Windows.

### L3 â€” Preserve `.bak` files until AFTER the commit is pushed

Session G1 deleted all `.bak` backups before the final commit.
Nothing was lost because git tracked the change, but the safety margin was thin.
**Rule: delete `.bak` files only after `git push` succeeds.**

### L4 â€” `git rm <file>` does not stage other working-tree changes

`git rm assessment_complete.py` stages only that file's deletion. Any other
modified files (`main.py` in this case) need explicit `git add`. Always check
`git status --short` before committing â€” files marked ` M` in the second
column are modified but NOT staged.

`git commit` without `-a` only commits staged changes. Verify with
`git show --stat HEAD` after each commit that the expected files landed.

### L5 â€” `ast.parse()` is stricter than Python's real import

`ast.parse(open(path).read())` fails on files with UTF-8 BOM (`EF BB BF`),
raising `SyntaxError: invalid non-printable character U+FEFF`. But
`import module_name` succeeds â€” Python accepts BOM at start of source files.

**Rule:** use `python -c "import X"` for syntax validation. Reserve
`ast.parse` for cases where the string doesn't have a BOM, or strip the
BOM first.

**Note:** `results_system.py` has a pre-existing BOM (unrelated to G2).
No action taken; if a future housekeeping session wants a repo-wide BOM
sweep, grep files whose first 3 bytes are `EF BB BF`.

### L6 â€” Multi-insert patchers must go strictly bottom-up

When a patch inserts lines at multiple positions in the same file, apply
edits in **strictly descending index order** (highest first). An insert at
index 49 shifts every subsequent index â€” so an "insert at 48" that follows
it lands 2 lines off and can break the file.

**Session G2 evidence:** the first Batch-3 patcher for
`enhanced_assessment_engine.py` failed exactly this way (`'{' was never
closed`). Rolled back cleanly with `git checkout --`. The corrected patcher
applied ops in reverse index order and worked first try.


### L7 â€” Real OpenAI latency is 3-4x the nominal estimate

Session G3: batch seeding 207 pairs took 88 min, not the estimated
33 min. Root cause: OpenAI chat completions averaged ~25s per call in
practice, not the ~7.5s assumed from single-call timings.

**Rule:** for batch OpenAI work, estimate at **25-30s per call** unless
you have measured recent latency. Add 2-3s throttle on top.

### L8 â€” Engine fallback masks OpenAI failures as success

`exam_prep_engine._generate_via_ai` catches exceptions and returns
`_stub_questions()` on failure, but the outer `generate_questions`
still returns `status: success`. The seed script therefore reports OK
on fallback content.

**G3 evidence:** `jssc/Math` (pair 198) â€” OpenAI timed out at 45s, stub
content (30 trivial arithmetic questions) was written to the bank.
Fixed by deleting stub rows (LENGTH heuristic) and re-generating.

**Rule:** for content-quality-sensitive batches, verify question content
sample, not just count. Consider adding a `source` column to the bank
to distinguish AI-generated from stub.

**Rule:** for multi-edit patchers, iterate indices in descending order,
or operate on string matches rather than line indices.


### L9 â€” Double-encoded UTF-8 in template dropdown values

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
3. **Never let a promised item silently disappear** â€” flag it in this file immediately
4. **Verification audits** every N sessions to catch gaps
5. **Session-CONTEXT.md** links here for fresh chats

---
**Last updated:** 2026-09-24
**Next update:** after C13 or Session C2
