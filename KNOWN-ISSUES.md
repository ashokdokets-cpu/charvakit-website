# Charvak - Known Issues Registry

### RESOLVED - Passport is_public defaults to TRUE (2026-10-30, a859b21)

Every new passport was created with is_public=TRUE by DB default.
Users who took a readiness check had no UI to control visibility -
their score + cert count + display name appeared in recruiter search
without their knowledge.

Fix (Session 101):
- Migration flips DB default TRUE -> FALSE
- POST /api/passport/visibility toggle endpoint (auth-gated)
- templates/passport.html shows toggle to passport owner only
- Owner bypass: private passports visible to owner via direct URL
- Strangers get 404 on private passport (correct privacy behavior)

Verification:
- Local: default=false, nullable=NO
- Existing public @hr-c97e preserved is_public=TRUE
- New @charvak-admin-0b61 created is_public=FALSE
- Prod API health check: 200/401/200 (all passing)

Verdict: RESOLVED.

---

### RESOLVED - Staff Augmentation card shown with hardcoded $4,000 (2026-10-30)

The Staff Augmentation card on the homepage showed From $4,000/month
hardcoded - wrong currency for Indian viewers, wrong price for the
product (Rs 4,000 is intern rate, not staff aug rate).

Fix:
- Removed hardcoded price
- Replaced with 3 value claims: Shortlist in 48 hours. Verified by
  real code execution. See pricing.
- Removed nested <a> tag that was breaking layout

Verdict: RESOLVED.

---

### RESOLVED - Exam-prep categories shown as raw DB keys (2026-10-30)

/exam-prep categories rendered as central_govt, manage ment,
state_exams with mid-word wrapping. Frontend fetched API returning
raw keys, not display names.

Fix: Backend get_all_categories() now returns display names + icons
via CATEGORY_DISPLAY dict. Frontend uses API values directly.

Verdict: RESOLVED. All 18 categories (12 Indian + 6 global) render
with clean names + icons. 138 + 55 = 193 exams all visible.

---



**Last updated:** 2026-10-24 (Sessions 79-80 closed)

### RESOLVED - Homepage positioning was exam-prep-only (2026-10-24, 707996c)

The homepage hero read "Practice smarter. Score higher." — positioning
Charvak as a B2C exam-prep app. Enterprise buyers (universities, employers)
had no entry path from the homepage.

**Fix:** Full 3-pillar rewrite. Hero: "The AI Verification Layer for Global
Talent." Three pillar cards: For Learners / For Universities / For Employers.
Each with 5 feature bullets + 2 CTAs. Proof bar + featured products added.

**Verified on prod:** all 7 structural markers present.

---

### RESOLVED - Softened 48-hour placement claim (2026-10-24, 707996c)

The homepage claimed "Hire verified. Deploy in 48 hours." — an aggressive
SLA we couldn't guarantee without 20+ engineers ready to interview.

**Fix:** Softened 4 locations:
- "Hire verified. Deploy in 48 hours." → "Hire verified. Match in 48 hours."
- "48-hour engineer placement SLA" → "48-hour candidate shortlist"
- "AI-verified remote engineers placed in 48 hours" → "...shortlisted in 48 hours"

**Rationale:** What we can defend is 3 candidates within 48 hours, not a
guaranteed start date. Match is achievable; deploy requires the candidate
to accept an offer, resign, and start — outside our control.

---

### RESOLVED - GPT-4o model retirement (Jan 14, 2027) (2026-10-23)

GPT-4o-mini and GPT-4o were being retired Jan 14, 2027. The migration
plan (Phase 1-3b) completed in Session 54, but the Render env vars were
never set. The code was still defaulting to `gpt-4o-mini` (retiring).

**Fix (Session 79):**
- Set `OPENAI_MODEL=gpt-5.4-nano` on Render
- Set `OPENAI_MODEL_CHEAP=gpt-5.4-nano`
- Set `OPENAI_MODEL_SMART=gpt-5.4-mini`
- Verified 7/7 tests: JD parse (8 skills extracted), auth gate (401), 6 endpoints

**Deadline eliminated.**

---


# Charvak - Known Issues Registry

**Last updated:** 2026-10-23 (Sessions 76/77/78 closed)

### RESOLVED - Email gate modal trapped in hidden parent (2026-10-23, db6978b)

The Session 78 email gate modal was placed inside `#rdContent`, which is
`display:none` until the cert renders. Since the gate fires BEFORE cert
renders, the modal was trapped inside a hidden parent and never appeared.

Additionally, `renderCertificate` was defined in IIFE #2 but called from
IIFE #1 via the modal's submit/skip handlers. Different scopes =
ReferenceError after capture.

**Fixes:**
1. Moved modal HTML out of `#rdContent` (now sibling inside `.rd-wrap`)
2. Exposed `window.renderCertificate = renderCertificate`

**Verified:** anonymous gate shows, capture works, skip works, authed
users bypass.

---

### RESOLVED - Nav gap between strip and main nav (2026-10-23, cea4e69)

Global Platform strip and main nav were visually merged. Nav was pinned
at `top: 32px` while strip rendered 0-39px, so nav overlapped strip's
bottom 9px.

**Fix:** nav at `top: 53px` (12px gap), removed redundant body padding-top.

---

# Charvak â Known Issues Registry



**Created:** 2026-09-18

**Last updated:** 2026-10-16 (Session 44-B â multi-currency)

**Purpose:** Central registry for bugs, dead code, and design issues.



---



### RESOLVED - Razorpay webhook plan guard rejects orders without `plan` key (2026-10-16, 48298e1)



Discovered during 44-A1 (AI Slop Checker) launch. The Razorpay

webhook has an initial guard:



    if not payment_id or not plan or not email:

        return {'status': 'ignored', 'message': 'missing data'}



Our `ai_slop_report` orders were not setting `plan` in their notes,

so the webhook silently rejected every delivery. The 44-A1 order

was paid (Razorpay captured the charge), but credits/report were

never generated.



**Fix (commit 48298e1):** add `"plan": "ai_slop_report"` to the

notes dict at order creation.



**Verified:** SLOP-CDE1EB71 -> PR-34DF3743E6EE2C25 -> PDF 47,619 bytes

delivered via email.



**Lesson for future paid products:**



Any new paid product that goes through the Razorpay webhook MUST

set a `plan` key in notes, even if the product already has a

different `tool` identifier. The guard checks `plan`, not `tool`.



Pattern to copy from 44-A2 (Band Guesser) and 44-B follow-ups:



    notes = {

        "plan": "<product_key>",   # REQUIRED for webhook guard

        "tool": "<product_key>",   # used for the tool-specific branch

        "email": email,

        ...

    }



---

# Charvak Ã¢â¬â Known Issues Registry



**Created:** 2026-09-18

**Last updated:** 2026-10-12

**Purpose:** Central registry for bugs, dead code, and design issues.



**Active roadmap:** See TRACK-A-B-PLAN.md for the full Track A (B2C)

and Track B (CSR) sequencing.

**Created:** 2026-09-18

**Last updated:** 2026-09-28 (Session C)

**Purpose:** Central registry for bugs, dead code, and design issues found during the persistence project. Every session appends to this file. Session I resolves what's still open.



### RESOLVED - IELTS writing + speaking topical relevance (2026-10-08, b3fd1f6 + 0f17fe9)



Session 40c flagged that the IELTS writing + speaking AI scoring

did not enforce topical relevance. Off-topic submissions could

receive a normal band score; on-topic partial submissions could

score 0.



Session 41 fixes both:



1. Prompt hardening in `evaluate_writing` and `evaluate_speaking`:

   the AI is now instructed to verify the response addresses the

   prompt. Off-topic responses cap Task Achievement / Task Response

   (or all sub-bands, for speaking) at 3.0 and set

   `topical_relevance=false` + `relevance_note`.



2. Speaking prompt explicitly tells the AI which parts were

   answered, and instructs it NOT to cap the band for missing

   parts. This closes the "partial scored 0" regression.



3. Frontend red banner above the yellow partial banner when

   `topical_relevance === false`, showing the AI's

   `relevance_note`.



4. Root-cause fix: the writing evaluate route read

   `data.get("prompt_text", "")` while the frontend sends

   `{prompt: ...}`. The prompt never reached the engine.

   Every IELTS writing evaluation since the feature shipped was

   scored without the prompt. Now reads `prompt` with a

   `prompt_text` fallback.



Verified:

- scripts/test_ielts_relevance.py: 14/14 (6 canned cases)

- Browser off-topic writing: red + yellow banners, TR 3.0,

  overall 4.5, feedback notes the mismatch

- Browser on-topic writing: no banners, all bands 8.0

- Browser off-topic speaking: red banner with the AI's note

- Browser on-topic partial speaking: yellow partial banner only



Verdict: RESOLVED.





**Legend:** [RED] data integrity | [WHITE] feature gap | [YELLOW] cosmetic | [GREEN] hygiene



---



### V4-adjacent gap Ã¢â¬â scripts with `load_dotenv()` silently target prod (2026-09-26)



- **Discovered during:** Voice-to-Web Option 2 E2E testing.

- **Reality:** `.env.local` gets renamed `.env.local.off` when testing against prod.

  Any dev script run during that window that calls plain `load_dotenv()` (no args)

  will load `.env` Ã¢â â **prod**. Not dev.

- **Consequence:** the dev user's verification row was inserted into prod while the

  server was pointed at dev Ã¢â¬â leading to a 30-minute 403 debugging rabbit hole that

  looked like a code bug but was a state mismatch.

- **Rule:** any script that intends dev MUST call

  `load_dotenv(".env.local", override=True)` explicitly, not `load_dotenv()`.

  Add to `DEV-SETUP.md` as a hard rule.

- **Alternative:** rename `.env.local` less often; use script-local env override

  instead of the rename dance.



## Fixed (this project)



| Date | Session | File | Issue | Fix |

|---|---|---|---|---|

| 2026-09-29 | Auth | `auth.py` + `main.py` | In-memory `active_tokens` wiped on every uvicorn reload / Render restart -> every browser 401 | DB-backed `charvak_auth_tokens` table; verify_token falls back to DB - `f58e63f` |

| 2026-09-29 | Perf | `main.py` | `CachedStaticFiles` set `immutable, max-age=1y` -> every JS/CSS edit required manual `?v=` bump | Changed to `max-age=3600, must-revalidate` - `f58e63f` |

| 2026-09-29 | Fix | `templates/ai-contamination-detector.html` | Fabricated numbers via `Math.random()` | Real fetch to `/api/products/ai-slop/scan` - `e28c781` || 2026-09-28 | Sec | main.py | 20 unguarded /api routes (escrow, kyc, enterprise, referral, lifecycle, messaging, career, training, enroll) | require_admin or require_auth_for_email added - 3f71788 |

| 2026-09-28 | Sec | main.py | 4 AI tool routes missing email-match auth | require_auth_for_email added - 6b22d61 |

| 2026-09-28 | Sec | main.py | 147 routes swallowed HTTPException via broad except Exception (guards never fired) | except HTTPException: raise inserted - a8e1275 |

| 2026-09-28 | Fix | templates/lock-in-breaker-pricing.html | Dead fetch to /api/notifications/send | Removed - 03903a2 |

| 2026-09-28 | Fix | main.py | Duplicate /api/payment/history route | Removed duplicate - 03903a2 |

| 2026-09-18 | G/4 | `na_module/resume_engine.py` | PII phone regex had a capture group Ã¢â â `re.findall` returned empty strings Ã¢â â `replace('', ...)` inserted redaction marker between every character (86 chars Ã¢â â 1529 chars) | Non-capturing group `(?:...)` |

| 2026-09-18 | G/2 | `na_module/vms_connector.py` | `job_id = f"NA-JOB-{hash(str(raw_data))}"` Ã¢â¬â `hash()` randomized per process, IDs changed on every restart | `secrets.token_hex(4).upper()` |

| 2026-09-18 | G/4 | `na_module/resume_engine.py` | `vendor_id = f"VEN-{hash(...)}"` Ã¢â¬â same bug | `secrets.token_hex(4).upper()` |

| 2026-09-18 | E/4 | `final_year_project_engine.py` | AI methods called `json.loads(response.choices[0].message.content)` without `response_format`; GPT-4o-mini returned prose + markdown fences Ã¢â â `Expecting value: line 1 column 1` | `response_format={"type": "json_object"}` + defensive fence strip |

| 2026-09-18 | J/6 | `ai_question_generator.py` | `generate_with_openai` had no `response_format` (same AI JSON bug class) | Added `response_format={"type": "json_object"}` + defensive fence strip + regex fallback |

| 2026-09-18 | J/3 | `indian_language_ai.py` | Mojibake emoji in `translate_job_ad` ad string (rocket, pin, arrow) | Converted to `\U` escapes; real Hindi/Tamil/Telugu content preserved as raw UTF-8 |

| 2026-09-18 | J/2 | `content_generator.py` | `_deduplicate` crashed on `sentence_builds` items (dict with list `words` value Ã¢â¬â unhashable) | Stringify non-string keys via `str()` |

| 2026-09-18 | J/2 | `content_generator.py` | `_generate_with_ai` had no `response_format` + no timeout (same AI JSON bug class) | Added `response_format={"type": "json_object"}` + timeout + defensive fence strip |

| 2026-09-18 | H/8 | `advanced_assessment_engine.py` | `_generate_mcq_with_openai` AI JSON parsing without `response_format` + no timeout + fragile regex-only extraction | Added `response_format={"type": "json_object"}` + timeout + defensive fence strip + regex fallback |

| 2026-09-18 | H/8 | `advanced_assessment_engine.py` | Dead `user_scores` field (declared, never written) | Removed; no table created |

| 2026-09-18 | H/6 | `ai_bridge_engine.py` | Two AI JSON parsing calls without `response_format` (question generation + report evaluation) | Added `_ai_json()` helper with `response_format={"type": "json_object"}` + defensive fence strip |

| 2026-09-18 | H/5 | `training_mapping_engine.py` | `get_job_market_insights` avg_salary mojibake stripped to bare `",000 - ,000"` (both ranges empty). Restored to sensible `Rs.8L - Rs.30L` style | Manual restoration |

| 2026-09-18 | H/2 | `enhanced_assessment_engine.py` | Dead `question_cache` field + missing `response_format` on AI call | Removed dead field; added `response_format` + timeout + defensive fence strip |

| 2026-09-18 | TierE | `payment_engine.py` | `self.payments` in-memory list backed admin endpoints (`get_all_payments`, `get_payment_status`); all reset on restart | Persist to `charvak_payment_log` with `raw_data JSONB` |

| 2026-09-18 | D/2 | `brand_engine.py` | `promote_job` used `timedelta` without importing it Ã¢â¬â every call would `NameError` | Added `from datetime import timedelta` |

| 2026-09-18 | D/1 | `badge_engine.py` | `share_text` had mojibake `[PIN]` instead of [FLAG] | `\U0001F3C6` unicode escape |

| 2026-09-18 | F/3 | `marketing_ai_engine.py` | Mojibake in templates Ã¢â¬â `[LAUNCH]` instead of [LAUNCH] in every generated job ad / social post | `\U0001F680` unicode escapes (source stays ASCII) |

| 2026-09-18 | F/4 | `dynamic_role_engine.py` | `recommend_custom_role` mutated in-memory `role_database` Ã¢â¬â custom roles lost on every restart | Persist to `charvak_dynamic_custom_roles`, merge into `get_all_roles()` |

| 2026-09-17 | C | `main.py` | `GET /api/exam/progress` shadowed by `/api/exam/{exam_id}` catch-all | Routes inserted before catch-all |

| 2026-09-17 | C/3 | `exam_prep_engine.py` | Docstring said "83 exams" but actual catalog is 67 | Updated to 67 |



---



## Open Ã¢â¬â data integrity [RED]

### FLAGGED - IELTS writing + speaking AI scoring does not enforce topical relevance (2026-10-08)



Discovered during Session 40c testing. Two related observations:



1. Pasting text from a DIFFERENT topic into a writing or speaking

   response can still return a non-zero band score. The AI grades

   fluency / lexical resource / grammar, but does not reliably check

   whether the answer actually addresses the prompt.



2. Conversely, a partial-but-on-topic submission (e.g. parts 1+2 of

   speaking answered correctly) returned band 0 with feedback about

   "missing responses." The AI overcorrected for incompleteness.



**Impact:** HIGH. This directly undermines the trust-pipeline story.

An employer viewing a certificate needs confidence that the band

reflects on-topic ability. Off-topic submissions scoring points is

the kind of gap that loses enterprise deals.



**Root cause:** The prompts in `evaluate_writing` and

`evaluate_speaking` (ielts_engine.py) do not include a

topical-relevance criterion. The AI is asked to score the 4 official

IELTS criteria (Task Achievement / Coherence / Lexical / Grammar)

but Task Achievement specifically is under-specified for

off-topic detection.



**Suggested fix (its own session, ~2 hrs):**

1. Add an explicit top-of-prompt instruction:

   - "If the response does not address the prompt topic, cap Task

     Achievement at 3.0 and note the topical mismatch in feedback."

2. Add a pre-scoring sanity check on the backend:

   - Compute a lightweight topical-similarity score between prompt

     keywords and response text (keyword overlap is sufficient for

     a first pass; embeddings would be stronger).

   - If similarity is below a threshold, route to a specific

     "response does not address the prompt" band.

3. Build a regression test harness with 5 known cases:

   - On-topic full response -> normal score

   - On-topic partial response -> band + partial flag

   - Off-topic full response -> capped / flagged

   - Off-topic short response -> capped / flagged

   - Empty / near-empty response -> band 0, no error



**Verdict:** SCHEDULED - Session 41 candidate A.





| # | File | Line / Area | Issue | Fix in session |

|---|---|---|---|---|

| 1 | `na_module/revenue_engine.py` | `create_subscription` | Re-subscribe re-adds `monthly_fee` to `transactions` without adding a new subscription row. Revenue inflates silently on tier changes | TBD Ã¢â¬â product decision |

| 2 | `na_module/resume_engine.py` | `SubVendorManager.track_submission` | Duplicate `(vendor, candidate, job)` bumps `active_candidates` counter even though the row is deduped via `ON CONFLICT DO NOTHING` | TBD |

| 3 | `na_module/charvak_vms.py` | `approve_timecard` | Repeated approvals grow `approval_history` and overwrite `payment_reference` (no guard for already-approved state) | TBD |

| 4 | `migrations/20260916_course_payments.sql` | Foreign key | References `charvak_enrollments` which no migration creates. Fresh-clone / DR restore fails | Session I |

| 5a | `payment_engine.py` | `is_ready()` | `/api/payment/status` publicly returns `razorpay_key_id` + `paypal_client_id` Ã¢â¬â should trim to just bool flags. (Secret values NOT leaked Ã¢â¬â key_id is the public half.) | Security audit |

| 5 | `main.py` | `/api/exam/progress`, `/api/exam/history`, `/api/exam/study-plan` | No auth check Ã¢â¬â anyone can query any email's data | Security audit |

| 6 | `whatsapp_bot.py` | ~line 92 | AI JSON parsing bug (same as fixed in E/4) | When WhatsApp unblocks (external) |

| 6a | `badge_engine.py` | `self.certifications` | Dead field Ã¢â¬â declared but never written to, no table created | Session I or future work |

| 6b | `profile_network_engine.py` | `self.referral_matches` | Dead field Ã¢â¬â computed inline but never stored in list, no table created | Session I |

| 6c | `profile_network_engine.py` | `candidate_data` in master_profiles | Snapshot at create time Ã¢â¬â goes stale after candidate updates their own profile | Product decision |

| 6d | `university_engine.py` | `student_count` | Denormalized counter Ã¢â¬â only increments (no `remove_student` method exists) | Product decision |

| 6e | `messaging_engine.py` | `get_stats.unread_messages` | Counts only `sent`+`delivered` Ã¢â¬â excludes `replied` | Product decision |

| 26 | `ai_bridge_engine.py` | `get_premium_report` |

| 27 | `enterprise_engine.py` | `review_resume` | Typo in response: `f"Resume {decision}d"` Ã¢â â "Resume rejectd" for reject | Cosmetic / Session K |

| 28 | `enterprise_engine.py` | `record_survey_response` / `kiosk_check_in` | Increment counters but don't store respondent/student data (matches original) | Product decision |

| 30 | `content_generator.py` |

| 31 | `indian_language_ai.py` | `self.translations` | Dead field Ã¢â¬â declared but never written, `get_stats.total_translations` always 0 | Session K or later |

| 32 | `indian_language_ai.py` |

| 33 | `role_manager.py` + `dynamic_role_engine.py` | Custom roles | Two parallel custom-role stores (`charvak_role_manager_custom_roles` + `charvak_dynamic_custom_roles`). `role_manager.get_all_roles()` merges both via `dynamic_role_engine.get_all_roles()` + own table. Consolidation is a future refactor | Session K or I |

| 34 | `monitor_service.py` | `SiteMonitor.check_site` | `requests.Session(timeout=10)` is invalid - Session takes no `timeout` kwarg. Every check fails with TypeError, but the error is captured in `issues` (matches original behavior) | Session K or I |

| 35 | `monitor_service.py` |

| 36 | `ai_question_generator.py` | `self.used_questions` | Dead field - declared but never written or read | Session K or later |

 module-level state | Original used module-level `monitored_sites = {}` and `alert_history = []`. Now DB-backed; dummy `monitor = SiteMonitor("", "")` kept for backwards-compat | Done (this session) |

 `submit_assessment` | Score not persisted back to assessment record (matches original) | Product decision |

 `self.content_cache` | Dead field Ã¢â¬â declared but never written to, no table created | Session K or later |

| 29 | `voice_to_web_engine.py` | (not audited yet) | Persistence deferred to Session B-2 | Session B-2 |

 Not idempotent - calling twice for same session creates 2 premium rows + doubles revenue | Product decision / bug fix |

| 25 | `chatbot_engine.py` | `_match_faq` | Keyword keys don't match FAQ question text - some FAQs unreachable (e.g. "pricing" keyword vs "cost" in question text). Falls back to AI. | Product decision / bug fix |

| 7 | `ai_bridge_engine.py` | `_generate_ai_questions` + `_generate_report` | AI JSON parsing bug (missing `response_format`, both places) | FIXED in H/6 |

| 5b | `outreach_engine.py` | `subscribe_premium`, `connect_gmail` | No UNIQUE constraint Ã¢â¬â multiple subscriptions and Gmail syncs allowed per email (matches original behavior) | Product decision |

| 5c | `dynamic_role_engine.py` | `recommend_custom_role` | Anyone can add a global custom role Ã¢â¬â no auth, no per-user scoping | Security audit |

| 5d | `dynamic_role_engine.py` | `create_dynamic_training_plan` | Stateless Ã¢â¬â plan returned but not stored (matches original) | Product decision |



---



## Open Ã¢â¬â feature gaps [WHITE]



| # | File | Issue | Fix in session |

|---|---|---|---|

| 8 | `final_year_project_engine.py` | `total_projects` always returns 0 Ã¢â¬â `self.projects` was a dead field | Future feature work |

| 9 | `ai_internship_engine.py` | `submit_work` uses `random.randint(7,10)` for score | Product decision |

| 10 | `exam_prep_engine.py` | Icons changed from emoji to ASCII IDs Ã¢â¬â needs frontend mapping | When UI is built |

| 11 | `main.py` | Exam prep frontend mock-test UI doesn't exist (backend + routes live) | Dedicated UI session |

| 12 | `na_module/charvak_vms.py` | `vendor_performance` dead field Ã¢â¬â never written to | Future feature work |

| 13 | `student_suite_engine.py` | `assist_assignment` / `assist_research` return stubs Ã¢â¬â no real AI | Feature work |

| 26 | `advanced_assessment_engine.py` | `_generate_versant_questions` | Declared question counts (e.g. repeats=16) exceed available static prompts (4) Ã¢â¬â questions limited by prompt count | Feature gap |

| 14 | `na_module/vector_matcher.py` | `SKILL_EMBEDDINGS` is a small static dict; comment says "in production, use pgvector/Pinecone" | Future scaling |

| 15 | Analytics Dashboards | Never audited; page exists but no data source verified | Dedicated audit |



---



## Open Ã¢â¬â cosmetic [YELLOW]



| # | File | Issue |

|---|---|---|

| 15a | `notification_engine.py` | Mojibake in email subject (`[WARN] ` instead of warning emoji) Ã¢â¬â fix in Session H |

| 15b | `products_engine.py` | Mojibake in log message (`[OK]`) Ã¢â¬â fix in Session H |

| 16 | Multiple engines | Heading order on remaining pages (accessibility) |

| 17 | Site-wide | TBT ~1,900ms mobile Ã¢â¬â needs conditional script loading |

| 18 | `na_module/vector_matcher.py`, `work_auth.py`, etc. | Emoji icons in some docstrings Ã¢â¬â clean up during Session I |



---



## Open Ã¢â¬â hygiene / process [GREEN]



| # | Item | Notes |

|---|---|---|

| 19 | Demo env vars must stay unset on prod | `CHARVAK_LOAD_DEMO_JOBS`, `CHARVAK_LOAD_DEMO_REVENUE`, `CHARVAK_LOAD_DEMO_VMS`. Add to deployment checklist |

| 20 | `na_module/` has no `__init__.py` | Works as namespace package but implicit. Consider adding |

| 21 | No migration runner | Engines use `_ensure_tables()` on import. Acceptable, but a real runner would be cleaner |

| 22 | `Out-File -Encoding utf8` writes BOM | Documented in DEV-SETUP.md; scripts strip it manually |

| 23 | PowerShell `python -c` + quotes | Documented in DEV-SETUP.md; always use temp `.py` files |

| 24 | PowerShell `curl.exe` + JSON body | Documented in DEV-SETUP.md; always use `--data-binary @file.json` |

| 24b | Markdown files | Never use emoji or em-dash in `.md` sources. Use ASCII markers `[OK]`, `[WAIT]`, `[RED]`, etc. Emoji cause non-ASCII byte creep that breaks normalizer checks. | Session K or I |



---



## Rules for this file



1. **Every session appends to it** Ã¢â¬â if you preserve a bug, note it here.

2. **Fixed items move to "Fixed"** with date + fix reference.

3. **Session K** is the dedicated bug-cleanup session. **Session I** does the final capstone + tag.

4. **Keep it in git** so it survives across machines and sessions.



### Open Ã¢â¬â pattern: frontend handlers reference undefined variables (2026-10-02)



Second instance of this class: 'authToken is not defined' in

templates/indian-language-ai.html (both createAssessment and

translateJobAd). Fixed 2026-10-02.



First instance was C7's processToolPayment (fixed 2026-09-27).



Root cause: templates don't share an auth helper, so each form handler

declares its own email + authToken. Some forgot.



Systemic fix (future session): add a shared getAuthContext() helper in

base.html that returns {email, token}. Every handler calls it, so a

ReferenceError can't happen. Grep templates for 'authToken' and 'Bearer'

to find all call sites.



Verdict: FLAGGED - cleanup candidate





### Open Ã¢â¬â Indian Language AI: questions generated but not displayed (2026-10-02)



Full detail in COMMITMENT.md. The Language Assessment flow shows a

summary ("5 questions created") and never renders the questions, never

collects answers, never calls /submit.



Fix: 30-60 min. Backend returns questions or new GET endpoint +

frontend renders them + wires /submit + shows score.



Verdict: SCHEDULED - next cleanup session



---



### Open Ã¢â¬â PowerShell process-kill leaves stale workers (2026-10-03)



Hit this multiple times during Sessions 9-13:



- `Stop-Process -Name python` runs but a "python" process remains

- Subsequent curl hits the OLD code even after a "restart"

- `taskkill /PID X /F` fails with "Process not found" moments later

- Port 8000 has no listener even though `Get-Process` shows python



Root cause: `--reload` spawns a supervisor + worker. Killing the

supervisor leaves the worker holding the port. Some windows the

`Get-Process` snapshot is also stale (process exited between commands).



Fix Ã¢â¬â always verify after kill:



    Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force -ErrorAction SilentlyContinue

    Start-Sleep -Seconds 2

    Get-Process | Where-Object { $_.ProcessName -eq "python" } | Select-Object Id, ProcessName, Path



If a process remains, kill it explicitly by PID. If it says "not found"

but still shows, wait 2 seconds and re-check. Never assume the kill

worked Ã¢â¬â verify.



Verdict: DOCUMENTED Ã¢â¬â apply the verify pattern





### Open Ã¢â¬â PowerShell Get-Content displays correct UTF-8 as mojibake (2026-10-03)



Two false alarms during Sessions 13-14 (COMMITMENT.md, CAREER-ASSESSMENT-PLAN.md):



Files displayed as `Ã¢â¬â"` (mojibake) in PowerShell's `Get-Content` output,

but the bytes on disk were clean UTF-8 em-dashes.



Root cause: Windows PowerShell 5.x `Get-Content` uses the console code page

for output. `[System.IO.File]::ReadAllBytes()` and `ReadAllLines(path, UTF8)`

show the truth.



Fix Ã¢â¬â always verify with:



    [System.IO.File]::ReadAllLines("path", [System.Text.Encoding]::UTF8)



Never "fix" apparent mojibake without this check first. The earlier

em-dash fix attempts might have been display-only, not real disk bugs.



Verdict: DOCUMENTED Ã¢â¬â never fix mojibake without the byte check





### RESOLVED Ã¢â¬â PayPal credits capture test (2026-10-03, db9e2a1)



The Session B flag (#3 PayPal live capture test) is closed. Full

sandbox flow verified end-to-end with a US sandbox buyer + US sandbox

merchant. See COMMITMENT.md for details.



Verdict: RESOLVED





### FLAGGED Ã¢â¬â PAYPAL_MODE should be explicit on Render (2026-10-03)



The new `PAYPAL_MODE` env var defaults to "live" when unset, so Render

works correctly today. But an explicit value is clearer for ops and

prevents accidental sandbox routing on production.



Fix: add `PAYPAL_MODE=live` to Render's Environment tab.

Est: 1 min. Verdict: SCHEDULED Ã¢â¬â next Render dashboard session







### RESOLVED - Modal trapped in <main> stacking context (2026-10-05, 37f978f)



The admin client-role detail page had a modal that appeared faded

and unclickable. Root cause: modal HTML was inside the content block,

which `base.html` wraps in `<main>`. `<main>` has `position: relative;

z-index: 1`, creating a stacking context that trapped the modal behind

its own backdrop.



**Fix:** moved modal HTML to the `{% block modal %}` slot (rendered as

a direct child of `<body>`, immediately after `</main>`). Same pattern

applied to `open-role-detail.html` in Session 22c.2.



**Verification:** `document.getElementById('applicantModal').parentElement.tagName`

should be `BODY`, not `MAIN`.



**Rule for future sessions:** any modal must go in the modal block slot,

never in the content block.





### RESOLVED - Jinja parsing template tags inside a JS comment (2026-10-05, 37f978f)



The detail template had a JS comment containing a literal template tag

for the modal block - Jinja treated it as a real tag, opening an extra

block inside the JS. This caused:

`TemplateSyntaxError: Unexpected end of template. Jinja was looking for: 'endblock'`



**Fix:** reworded the comment to not include template tag syntax.



**Rule:** never write `{%` or `%}` inside a `.html` template's JS or CSS,

even in comments or string literals. Jinja has no context awareness.





### RESOLVED - Click delegation handler missing (2026-10-05, 37f978f)



After several reorganization patches, the `document.addEventListener("click", ...)`

block that handles `data-action` buttons was silently removed. The page's

`window.openApplicant` and `window.downloadPackage` were still defined,

but the delegation that called them was gone.



**Diagnosis technique (keep this):**



    getEventListeners(document).click.forEach(function(l, i) {

        var src = (l.listener && l.listener.toString) ? l.listener.toString() : '';

        if (src.indexOf('data-action') !== -1) console.log('FOUND at', i);

    });



If no listener contains `data-action`, the delegation isn't attached.



**Fix:** re-added the delegation listener before the `DOMContentLoaded` block.





### Process lesson - inline onclick calls IIFE-scoped functions



Both admin pages have buttons with `onclick="loadRoles()"` /

`onclick="loadAll()"`. Inline handlers execute in **global scope**, but

`loadRoles` / `loadAll` are defined **inside an IIFE**, so the inline

handler can't find them unless they're explicitly assigned to `window`.



**Fix:** `window.loadRoles = loadRoles;` / `window.loadAll = loadAll;`

right before the IIFE closes.



**Long-term rule:** prefer `data-action` + event delegation for all

button handlers. Inline onclick to IIFE functions is a footgun.



### RESOLVED Ã¢â¬â Anti-Cheating Layer A (2026-10-06, 1124a38 + 91e1b1f)



Gap 3 from COMPETITIVE-STRATEGY.md is partially closed. Layer A

(deterministic environment signals) is live on Career Assessments:

paste, tab_switch, contextmenu, focus_out, rapid_input. Recorded to

charvak_assessment_integrity_events, rolled up to

charvak_career_assessments.integrity_summary.



Layer B (question design) is an ongoing habit; Layer C (behavioral

analytics) is still future work.



**Commits:** 1124a38 (backend) + 91e1b1f (frontend)

**Engine:** integrity_engine.py

**Routes:** POST /api/integrity/event, GET /api/admin/career-assessment/{aid}/integrity

**Verification:** 8-scenario curl matrix + engine unit test + browser E2E.





### RESOLVED Ã¢â¬â Admin UI for integrity events + public Trust Score badge (2026-10-07, 33cb2f6)



Session 27 shipped the integrity engine (event capture). Session 38

shipped the surfaces that make it useful:



- `/admin/integrity-events` Ã¢â¬â list of all assessments with integrity

  events, sorted by risk level, filterable by risk and email/ID

- `/admin/integrity-events/{aid}` Ã¢â¬â full event timeline with metadata

  card and per-type filters

- `/api/admin/integrity-events` Ã¢â¬â new admin list endpoint

- `GET /api/readiness/{cert_id}/integrity` Ã¢â¬â public endpoint returning

  only {risk_level, verified, total_events, message}

- `integrity_engine.get_public_summary()` Ã¢â¬â strips per-type counts and

  timestamps so the public badge can't leak assessment detail

- Trust Score badge on `/readiness/{id}` Ã¢â¬â 4 states, explainer collapse,

  silent-fail



**Verified:** 21 assessments in the list, 87-event detail renders all

five event types, clean + elevated badge states both confirmed on the

certificate. Reverted after the elevated test Ã¢â¬â cert back to clean.



**Rule going forward:** any new assessment format (Versant, Mock Drives,

CBAT, IELTS) that wants a trust artifact reuses this exact pattern.

Engine and route are assessment-type-agnostic; only the frontend

wiring differs.



### RESOLVED - Integrity roll-out to Mock + CBAT (2026-10-07, 5ed18f4)



Session 38 shipped the integrity admin UI + public badge for Career

Assessments only. Session 39 extends the same pattern to Mock Drives

and CBAT.



**What shipped:**

- `_integrity_lookup_owner()` in main.py - prefix-based table routing

  (CAR/MK/MOCK/CBAT)

- `/api/integrity/public/{assessment_id}` - public endpoint for any

  assessment type (extends the Session 38 cert-scoped endpoint)

- `CharvakIntegrity.renderBadge()` in static/js/integrity-capture.js -

  shared badge renderer with self-injecting CSS

- Admin list + detail endpoints now show real metadata for MK/CBAT rows

- Mock + CBAT result screens render the trust badge



**Two pre-existing bugs fixed along the way:**



1. **CBAT page route was never registered.** Session M-2 shipped

   `cbat_engine.py`, five `/api/cbat/*` routes, and `templates/cbat.html`

   - but `@app.get("/cbat")` was missing. The page was unreachable for

   weeks. Fixed in 39-5b.



2. **`cbat.html` called `window.charvakFetch()` at 3 sites but the

   function was never defined.** Same class of bug as `processToolPayment`

   (Session C) and `authToken` (Session 21). Fixed in 39-5c.



**Patterns established for future assessment roll-outs:**



- Adding a new assessment type = one entry in the prefix map +

  a getter function in the template. ~15 lines total per assessment.

- The badge renders via `CharvakIntegrity.renderBadge({slotId,

  assessmentId})`. One call site, self-contained.



**Patcher discipline:** the session's patcher for 39-8b uses

preview-then-assert-then-write. Three asserts fire before any write:

1. Expected anchor line matches

2. No unclosed docstring above the replacement block (the specific

   bug that broke the first 39-8 attempt)

3. Exact block boundaries match expectation



Both gates would have aborted the patcher before writing if the file

shape had changed. main.py was never at risk.



**Follow-up flagged:**

- Systemic `charvakFetch` belongs in base.html. Three templates now

  duplicate a ~12-line helper. One-line addition to base would let

  every template share it.



### RESOLVED - Versant persistence + integrity roll-out (2026-10-07, e25598e)



Versant had been dead-on-arrival for weeks. cbt_versant.py was

refactored to persist to Postgres, but the migration was never

added and no self-healing DDL was in place. Every create_session()

call hit a try/except and returned "could not create session",

silently failing.



**What shipped (7 commits):**



1. `charvak_versant_sessions` + `charvak_versant_answers` migration

   + self-healing DDL in cbt_versant.py.__init__



2. VERSANT prefix in _integrity_lookup_owner's table_map



3. List endpoint LEFT JOINs versant + COALESCEs role/format



4. Detail endpoint gains a VERSANT metadata branch



5. versant.html wired to CharvakIntegrity.init() via

   window.VS.sessionId



6. Trust badge on the Versant scorecard via the shared

   CharvakIntegrity.renderBadge()



7. Graceful partial-credit handling: the engine now computes

   partial = (answered_count < total_count), tells the AI in the

   prompt, tags the response, persists the metadata, and the

   frontend shows a yellow warning banner.



**Verified E2E:**

- Full session completes (was broken)

- 10 events captured live

- Admin list shows "English Assessment ÃÂ· versant"

- Detail page metadata populated

- Partial submission shows banner + DB records partial=True

- Full submission: no banner



**Patcher discipline lesson (worth keeping):**

The 40a-9 v1 patcher broke cbt_versant.py by stopping its

_score_versant replacement at the last quoted string, leaving the

original closing `)` as an orphan (SyntaxError: unmatched ')'). v2

fixed it by:

  1. Asserting lines[promptEndIdx + 1].Trim() == ')' BEFORE writing

  2. Including the `)` line in the replacement range

  3. Post-write ast.parse with automatic restore-from-backup on

     failure



Rule: when replacing a Python statement whose closing paren is on

its own line, the paren is part of the boundary. Assert it. Replace

it. And add a post-write AST check that restores on failure so the

file is never left broken.



**Follow-up flagged:**

- Versant schema has no `passed` column. Add it and populate in

  complete_session (score >= threshold).



### RESOLVED - IELTS persistence + integrity roll-out (2026-10-08, c65b696)



IELTS had the same class of pre-existing bugs as Versant (40a): the

engine code referenced tables and columns that no migration ever

created. Every affected route failed silently.



**What shipped (9 commits):**



1. `charvak_ielts_sessions` table + migration + self-healing DDL

2. `create_session` / `complete_session` on `ielts_engine.py`

3. 4 start routes create sessions and return session_id

4. 4 complete routes close sessions on evaluate/score

5. 4 templates propagate session_id in the payload

6. `_integrity_lookup_owner` gains 4 IELTS prefixes + two-segment

   fallback for multi-dash prefixes

7. Admin list endpoint JOINs IELTS sessions

8. Admin detail endpoint gains IELTS metadata branch

9. Trust badge + capture wired into all 4 templates

10. Partial-credit tracking for reading + listening



**Pre-existing bugs fixed (7):**



- 4 missing tables: reading_passages, listening_sections,

  reading_attempts, listening_attempts

- `last_used_at` column missing from 2 tables

- Migration file had `#` SQL comment syntax (invalid)

- Seed scripts load `.env` (prod) instead of `.env.local`

- 3 missing commas after `session_id:` in template payloads

- 1 missing comma before `session_id:` in writing template

- `$host` and `$pid` reserved PowerShell variable collisions



**Two-segment prefix pattern (new):**



`_integrity_lookup_owner` now tries single-segment prefixes first

(CAR, CBAT, VERSANT), then falls back to two-segment (IELTS-W, IELTS-R)

when the map misses and the ID has 2+ segments. Future prefixes

following the two-segment shape plug in with a single map entry.



**Comma preservation rule (new):**



When patching a JS object literal by inserting a field, verify that

the field before the insertion ends with a comma (if anything follows)

and that the new field ends with a comma (if anything follows it).

A missing comma produces a "Unexpected identifier" syntax error in

the browser, easy to catch with a hard refresh.



**Trust pipeline coverage: 5 of 5 assessment types.**



Career, Mock, CBAT, Versant, IELTS all carry the full trust artifact

now: capture events, admin visibility, badge on scorecard, and

(honest) partial-credit handling where applicable.



**Follow-ups flagged:**

- `charvakFetch` belongs in `base.html` (still pending from Session 39)

- Seed scripts should load `.env.local` (pattern documented in

  `DEV-SETUP.md`, still needs applying to the IELTS seeds)

- Versant `passed` boolean column (from Session 40a)

- Partial-credit handling for IELTS writing + speaking (deferred to

  Session 40c)



### RESOLVED - Session 42 fixes (2026-10-09, 9d2aced)



Four bugs fixed across Session 42:



1. **Empty signature block on the readiness PDF certificate** (2026-10-09, b1a0668)

   The certificate printed "Authorized Signatory" over an empty line.

   Fixed: signatory name + title added above the line, with an

   optional hook for a handwritten signature.png.



2. **Pattern selection on /mock-drive generated the wrong questions**

   (2026-10-09, 83d0a81). Previously, clicking any of a company's

   patterns started the same default pattern. The frontend passed

   pattern_id, but start_mock_drive ignored it. Fixed by threading

   pattern_id through /api/mock/start-complete -> start_mock_drive,

   which now looks up the pattern in multi_pattern_company.



3. **Login dead-end on any page using ?next=** (2026-10-09, 9d2aced)

   login.html read ?redirect= (legacy) instead of ?next= (used

   everywhere else). Users landed on "/" instead of the page they

   came from. Fixed: honor ?next= OR ?redirect= with sanitization

   (same-origin paths only).



4. **Register flow ignored ?next=** (2026-10-09, 9d2aced)

   register.html had no ?next= handling at all - new users always

   went to /welcome. The Register link on login.html also dropped

   ?next=. Fixed: register.html honors ?next=, login.html's Register

   link carries it through.



**Session 42 also closed four carry-forward flags:**

- charvakFetch moved to base.html (Session 39 flag)

- Seed scripts load .env.local (Session 40b flag)

- Versant passed column added (Session 40a flag)

- .gitignore duplicate cleanup (Session 41 flag)





### RESOLVED - A1.6 tools route uses raw ip_detector (2026-10-13 -> resolved 2026-10-13)



**Resolved 2026-10-13 in commit 5573b13** ("fix(payments): A1.6 country

code + PayPal server-side capture"). The fix was applied the same day the

flag was filed, but the tracker was never updated.



**Verified 2026-10-16** at main.py:2971-2992:

- Uses improved_ip_detector (returns ISO codes)

- Has a name-to-ISO fallback map for edge cases

- Passes normalized country_code into tool_payment_engine.create_order()



**Verdict:** RESOLVED - docs-only close-out.





### RESOLVED - A1.7 PayPal capture route (2026-10-19, verified)



**Verified 2026-10-19.** Fully implemented in Session 43-A1.7:

- Route: `main.py:15136` - `@app.post("/api/payment/paypal/capture")`

- Handler: `api_paypal_capture` at `main.py:15138`

- Engine: `payment_engine.py:799` - `capture_paypal_order()` (78 lines, full impl, idempotent)

- Frontend callers: `static/js/ielts-deep-report.js:323`, `static/js/tool-pay.js:263`



**Verdict:** RESOLVED - docs-only close-out. No code change needed.



### FLAGGED - deploy.yml uses Python 3.9 while prod is 3.11 (2026-10-19)



**Discovered:** 2026-10-19 during Session 52 flag cleanup.



`.github/workflows/deploy.yml` sets `python-version: '3.9'` while

`.github/workflows/test.yml` and `runtime.txt` both use 3.11. Production

uses 3.11 (per `runtime.txt` and Render's build config).



**Current impact:** zero. The `deploy.yml` "Run tests" step is a

placeholder (`python -m pytest || echo "No tests yet"`) that doesn't

run anything meaningful. Render's own build (`pip install -r

requirements.txt` + `uvicorn main:app`) is the actual deploy path.



**Real risk if unaddressed:** if `deploy.yml` ever gains real pre-deploy

tests, they'd run on 3.9 and could pass while prod (3.11) fails - masking

Python 3.10/3.11-only syntax issues.



**Fix:** bump `python-version: '3.9'` -> `'3.11'` in `deploy.yml` (line 15).



**Effort:** 5 seconds. **Priority:** low (cosmetic until deploy.yml gets

real tests).



**Verdict:** FLAGGED - fix opportunistically when deploy.yml gets real

pre-deploy validation.



### RESOLVED - admin-cas-keys.html patch corruption (2026-10-20, 2cff7e2)



**Incident:** During Session 64b first attempt, a 6-part mega-patch

corrupted `templates/admin-cas-keys.html`. The file ended up with

`renderRow`'s return template spliced inside `loadKeys`, an orphan

`<div></div>` inside `deactivateKey`, and an `else` clause attached to

nothing. Browser console showed:

- `Uncaught SyntaxError: Unexpected token 'catch'`

- `Uncaught ReferenceError: loadKeys is not defined`



**Root cause:** The patch anchored on `window.loadKeys = async function()`.

That string does NOT exist in the clean file. The functions use bare

declarations (`async function loadKeys()`) with `window.loadKeys = loadKeys`

exports at the bottom of the IIFE. My grep matched `fetch('/api/admin/cas-keys/list'`

as a substring â which occurs in both `loadKeys` AND `approveKey` â and the

insert landed in the wrong function.



**Fix applied in the retry (Session 64b successful run):**

- Restored from clean backup (225 lines)

- Applied 6 gated patches (P1-P6)

- Each patch: Jinja render + `node --check` on the extracted inline

  `<script>` + auto-revert on failure

- Line-range anchors + unique full-line string matches (verified via

  occurrence count before edit)



**Zero corruption on the retry.** All 6 patches passed their gates.



**Process rules for future template patches:**



1. **Dump the exact structure first.** A 30-second `ReadAllLines` +

   line-number walk eliminates hours of debugging.



2. **Anchor on full lines, not substrings.** `fetch('/api/admin/cas-keys/list'`

   matches twice. `const r = await fetch('/api/admin/cas-keys/list', {headers: authHeaders()});`

   matches once.



3. **Verify occurrence count before every edit.** If > 1, use brace-balance

   or line-range scope, never the substring.



4. **Gate every patch with `node --check`.** Static checks (grep for element

   presence, Jinja render) do NOT catch JS syntax errors inside template

   literals. Only a real parser does.



5. **Auto-revert on gate failure.** Per-patch backups (`p1.bak` through

   `pN.bak`) + `Copy-Item $path.bak $path` on failure. Zero time lost.



6. **Split multi-part patches.** A 6-part mega-patch ran in bottom-up order

   but each step re-searched the file for its anchor â after step N, the

   line numbers had shifted, so step N+1's anchor pointed at a different

   location. Split into 6 separate patches, verify each, then proceed.



**Verdict:** RESOLVED. Session 64b shipped cleanly with the corrected

methodology. Rules documented above.



## RESOLVED - Career Certification f-string + branding bugs (2026-10-20, 766fb6b)



**Bugs fixed during Session 69:**



1. **Python 3.11 f-string backslash restriction** - f-string expressions

   cannot include backslash-escaped quotes. Python <3.12 behavior. Fix:

   extract dict value to local var first, then interpolate the local.



2. **PowerShell inline JS escaping** - writing JS with escaped quotes in a

   PowerShell single-quoted string breaks the parser. Fix: use a

   single-quoted here-string for any JS block containing quotes or `<`.



3. **SECRET_KEY import from global_config doesn't exist** - assumed

   `global_config.SECRET_KEY` existed. It doesn't. Existing pattern (from

   `_generate_certificate_hash`) is:

   `os.getenv("READINESS_HMAC_KEY") or os.getenv("SECRET_KEY") or "dev-only-not-secret"`.



4. **Auto-revert gate only checks ast.parse** - silent runtime bugs like

   `NameError: sig is not defined` pass syntax check. Fix: add runtime smoke

   test after every function patch (2-second check catches 80% of silent bugs).



5. **PDF verify URL hardcoded** - `render_readiness_certificate_pdf` had

   the verify URL path hardcoded to /api/readiness/verify/. Added

   `verify_url_path` param (defaults to /api/readiness/verify/) so career

   certs can pass /api/career-certification/verify/.



6. **PDF issued date showed N/A** - renderer reads `created_at` from cert

   dict, but the dict had only `issued_at`. Fix: add both fields.



7. **PDF branding said "Role Readiness"** - parameterized `report_type` on

   `render_readiness_certificate_pdf` with "readiness" (default) and

   "career_certification" options.



## PROCESS RULES ADDED (2026-10-20)



**Rule 1 - Runtime smoke tests after every function patch.**

`ast.parse` catches syntax. It does NOT catch missing variables, wrong

returns, or runtime NameErrors. Add a `python -c "call_function(...)"` call

as mandatory second gate. 2 seconds, catches 80% of silent bugs.



**Rule 2 - Python 3.11 f-string limitation.**

Cannot use backslash-escaped quotes inside `{...}`. Extract dict values

to local variables before interpolation. Python 3.12+ (PEP 701) removes

this restriction, but production is 3.11.



**Rule 3 - PowerShell JS escaping.**

Use a single-quoted here-string for any block containing escaped quotes,

`<`, or template literals. Never embed JS in single-quoted PowerShell

strings - the parser sees escaped quote as string-terminate and `<` as

comparison operator.



**Rule 4 - Docstring-aware patches.**

When inserting code after a function docstring, count triple-quotes. The

first `"""` is opening. The SECOND on its own line is close. Inserting

between them puts code inside the docstring where Python treats it as

text (never executed). This caused the branding block to be invisible

in Session 69 fix 7.



## RESOLVED - AI Tutor frontend nav overlap (Session 70, a016814)

7 bugs found and fixed during S67b build. All related to CSS/JS
integration of the tutor panel into my-course.html.

### Bug 1 - _token() undefined
Chat tried to call _token() but that function only existed in
interview-session.html (from S65), not my-course.html.
Fix: added _token() helper (5 lines).

### Bug 2 - visibility toggle broke slide-in
Panel used visibility hidden to visible toggle in .open class, but
visibility is not transitionable. Result: panel became visible while
still at translateX(100%) (off-screen), appearing to flash and
disappear. Fix: removed visibility toggle, use pointer-events none
to auto instead.

### Bug 3 - !important specificity conflict
Base #tutorPanel transform !important won over #tutorPanel.open
transform without !important. Fix: removed !important from base
transform; specificity handles it correctly (110 > 100).

### Bug 4 - Panel rendered inline (not fixed)
Panel was rendering as a normal block element at bottom of page
instead of a fixed right-side drawer. Fix: forced position fixed
important on the div.

### Bug 5 - Close button invisible
The close X was rendered but visually hard to spot. Fix: forced
36x36 circle, white background, teal X, box shadow.

### Bug 6 - Panel overlapped by site nav
Panel at top 0 placed the close button at y 8, inside the site nav
fixed zone (y 32-98). The nav currency selector covered the close
button. Fix: moved panel to top 100px, height calc(100vh - 100px).

### Bug 7 - Currency selector stacked on close button
Both the currency selector and close button had z-index 9999.
Clicks landed on the currency dropdown instead of the close button.
Fix: reduced panel z-index to 1050, header to 100.

### The Debugging Pattern (worth remembering)

SYMPTOM: button exists in DOM but clicking does nothing

DIAGNOSTIC: In browser console, run elementFromPoint at the button
center coordinates. If it returns a different element, that element
is the true blocker.

    var btn = document.querySelector('.target-button');
    var rect = btn.getBoundingClientRect();
    var elementAt = document.elementFromPoint(
        rect.x + rect.width/2,
        rect.y + rect.height/2
    );
    console.log('Same?', btn === elementAt);

If Same? is false, the returned element is what is receiving clicks.
For this bug, elementFromPoint returned the currency select element,
revealing the z-index overlap immediately.

This is faster than inspecting CSS cascade or DevTools positioning
because it tells you what the click will ACTUALLY hit.

### Rule added to process memory

When a button exists but appears non-interactive:
1. First check document.elementFromPoint(x, y) at its center
2. If a different element is returned, that is the true blocker
3. Common culprits: fixed nav bars, sticky headers, overlays
4. Fix is usually a z-index + position adjustment, not CSS rewrite
## RESOLVED - AI Tutor frontend nav overlap (Session 70, a016814)



7 bugs found and fixed during S67b. All CSS/JS integration issues.



### Bug 1 - _token() undefined

_token() only existed in interview-session.html, not my-course.html.

Fix: added _token() helper.



### Bug 2 - visibility toggle broke slide-in

visibility is not transitionable. Fix: removed visibility, use

pointer-events none to auto.



### Bug 3 - !important specificity conflict

Fix: removed !important from base transform.



### Bug 4 - Panel rendered inline

Fix: position fixed important on div.



### Bug 5 - Close button invisible

Fix: 36x36 circle, white bg, teal X.



### Bug 6 - Panel overlapped by site nav

Fix: moved panel to top 100px, height calc(100vh - 100px).



### Bug 7 - Currency selector stacked on close

Fix: reduced panel z-index 9999 to 1050.



### Debugging Pattern

For invisible buttons: run document.elementFromPoint(x, y) at button

center. If it returns a different element, that is the true blocker.

For this bug, it returned the currency SELECT element.


### RESOLVED - /api/sync/skills returns 422 with List[str] payload (2026-10-21, bcccee1)

DoketsRB was sending skill_gaps as ["Python","AWS"] but SkillGapSync
required List[dict]. Every call returned 422 with 2 validation errors.

Fix: skill_gaps -> List[Any]. Handler normalizes strings to
{topic: str} before INSERT. Also added tolerant extras.

Verified: original DoketsRB payload returns 200, gaps_count=2.

---

### RESOLVED - Early .env load in api_sync.py (2026-10-21, bcccee1)

api_sync.py was imported by main.py (line 31) before database.py
(line 37) loaded .env. API_KEY and API_SECRET evaluated as empty
strings at import time. All auth failed on local uvicorn --reload.

Fix: Added load_dotenv() directly in api_sync.py right after import os.
Module now self-sufficient regardless of import order.

Verified: no startup warning. All tests return 200 locally.

---

### RESOLVED - /api/sync/pull route missing (2026-10-21, 7fa6f89)

DoketsRB built their pull endpoints in Session 72. Charvak had no
route to call them.

Fix: New handle_pull(user_id, request) + POST /api/sync/pull/{user_id}.
Idempotent via ON CONFLICT DO UPDATE.

Verified: HTTP 200 on prod with bb864eb3,
{profile_synced:true, applications_synced:1, errors:[]}.

---

### FLAGGED - Sync Now button on /career-center (2026-10-21)

Button was inserted into career-v2.html but reverted because it
called two missing endpoints:
- /api/sync/user-info?email=X (never built)
- /api/sync/pull/{user_id} (exists but requires HMAC; browser cannot
  compute HMAC without exposing SYNC_API_SECRET)

To build properly:
1. Add /api/sync/user-info?email=X endpoint (10 lines)
2. Add signed-pull-for-browser route (Bearer auth, skip HMAC, 15 lines)
3. Insert button + JS in career-v2.html (30 lines)

Total: ~1 hr. Defer until user demand.

Verdict: FLAGGED - non-blocking, backend API is complete.

### RESOLVED - authToken missing from localStorage (2026-10-21, c4ae9c1)

Login stored token as auth_token and charvak_token, but button read
authToken (camelCase). Result: token always null. Button fell back to
cookie auth, which failed for non-admin users.

Fix: fallback chain authToken -> auth_token -> charvak_token -> empty.
Verified: Sync Now button works end-to-end on prod.

---

### RESOLVED - require_auth rejected cookie auth (2026-10-21, ac5647a)

require_auth only checked Authorization: Bearer. Cookie-based sessions
failed with 401 even when logged in.

Fix: try Bearer first, fall back to charvak_admin_token / auth_token
cookies. Verified: works with either auth method.

---

### RESOLVED - Duplicate doketsrb_id rows (2026-10-21)

Production DB had two rows for contact@dokets.com with different
doketsrb_id values. user-info endpoint used LIMIT 1, returned wrong one.

Fix: deleted stale 4c792e8d row + added UNIQUE constraint on email.
Verified: user-info now returns correct bb864eb3 doketsrb_id.

---

### RESOLVED - info/pull parse statements missing (2026-10-21, 78fbc4e)

Earlier patch overwrote var info = await infoResp.json() and
var pull = await pullResp.json(). Button threw ReferenceError.

Fix: restored both parse statements after fetch calls.
Verified: JS syntax OK via node --check, button works on prod.

---

### FLAGGED - Coding/SQL certificates missing (2026-10-22)

Career Assessment supports 8 formats (mcq, coding, sql, short_answer,
numeracy, SJT, behavioral, system_design, debugging, case_study). But
certifications only issue for MCQ and AI-scored formats. Coding and sql
CTA is hidden in ai-assessment.html.

Fix: Session 73+. Schema migration + task class catalog + engine changes
+ template renderer + PDF renderer. ~4.25 hrs across 2 sessions.

Verdict: FLAGGED - buildable now, deferred pending 3 flags.

---

### FLAGGED - base.html 401 redirect affects sync endpoints (2026-10-22)

base.html line 926 redirects to /login on any 401. If /api/sync/*
returns 401 (e.g., user session expired), page redirects instead of
showing sync error.

Fix: exclude /api/sync/* from the global 401 handler.
Verdict: FLAGGED - 10 min fix, non-urgent.

### RESOLVED - ?country= query param ignored in resume-roast (2026-10-22, d1b5b8c)

The fetch call was:
    fetch("/api/public/price/resume_roast_teaser", { credentials: "include" })
Missing the query string. So ?country=US on the page URL never reached
the API. API fell back to IP detection -> IN default -> INR 99 for
everyone.

Fix: one-line
    fetch("/api/public/price/resume_roast_teaser" + window.location.search, { ... })

**Debugging lesson:** the MutationObserver hotfix (14f0368) accidentally
stripped this during the IIFE rewrite. The bug was masked by our
diagnostic:

    html.includes("MutationObserver") -> true

which matched the WORD inside a comment ("// No MutationObserver...").
Not a real observer. We chased the phantom for ~30 min.

**Verification method (best):**

In DevTools Console, run BOTH:
    fetch("/api/public/price/resume_roast_teaser").then(r=>r.json()).then(d=>console.log(d))
    fetch("/api/public/price/resume_roast_teaser" + window.location.search).then(r=>r.json()).then(d=>console.log(d))

If they return different countries -> bug is in fetch URL, not API.

### RESOLVED - MutationObserver + textContent infinite loop (2026-10-22, 14f0368)

Never use MutationObserver with { childList: true, subtree: true } on
document.body when the callback calls .textContent = value. The
textContent write removes + adds a text node, which IS a childList
mutation, which retriggers the observer -> infinite loop.

Fix: don't use MutationObserver for state that can be computed at render
time. Update the target element directly once, or bake values into
template strings at render time.

### RESOLVED - Dynamic currency display in resume-roast (2026-10-22, 1c1707c + d1b5b8c)

Resume Roast now fetches local price on page load:
    fetch("/api/public/price/resume_roast_teaser" + window.location.search)

Renders hero (#rrHeroPrice) + unlock button (#rrUnlockPrice) in the
visitor's currency. Verified on prod:
    IN -> Rs 99
    US -> \.99
    GB -> Rs 2.99
    AE -> AED 14
    JP -> JPY 500
    (all 13 currencies via payment_engine.PUBLIC_PRICE_TABLE)




## Session 74 (2026-10-22) - Production CSS bug + revenue CTAs + Azure role

### RESOLVED - Missing .dropdown-menu display:none broke entire site (1573fc5)

The .dropdown-menu { display: none } rule was missing from style.css in
commit 07ae7fc. Without it, every nav dropdown rendered open by default,
expanding the header across the entire page. Fixed in 1573fc5 by adding
the base rule + .dropdown-menu.show { display: block }.

Lesson: when deleting CSS during refactors, verify foundational Bootstrap
rules survive. Always test in fresh Incognito after CSS changes.

### RESOLVED - Backtick-n literal in renderCertificate broke JS block (b4616f8)

Line 937 of readiness.html had literal backtick-n (from PowerShell here-string
escape) instead of an actual newline. This started a template literal that
never closed, causing "Unexpected end of input" parse error. Fixed in b4616f8
by replacing the backtick-n with a proper newline.

Lesson: when patching templates via PowerShell scripts, here-string escapes
can leak into the file. Always verify the final output visually after
patch scripts run.

### RESOLVED - Certificate page missing monetization CTAs (b4616f8)

262 cert page views/month had zero next-step CTAs before this fix. Added 2
HTML-only CTAs below the existing 'what next?' funnel:
- Retake with role focus -> /ai-assessment (25 credits)
- See recommended courses -> /ai-courses
Both are pure a href links with zero JS dependency.

Expected: 262 views/month x 5-10% click = 13-26 clicks, converting to
Rs 150-500/month initial from existing traffic.

### RESOLVED - New Azure & Hybrid Infrastructure Engineer role created

Created ROLE-7B9405A1 for financial services client:
- Title: Senior Azure and Hybrid Infrastructure Engineer
- Location: US-based, remote, Eastern Time (DC/MD/NoVA preferred)
- Rate: $60-65/hr, 6-month contract
- 12 screening questions (8 candidate, 4 admin verification)
- Public URL: https://www.charvakit.com/open-roles/ROLE-7B9405A1
- Admin URL: https://www.charvakit.com/admin/client-roles/ROLE-7B9405A1

Ready for LinkedIn + CBREX submission.

### VERIFIED - Razorpay live payment flow works end-to-end

Tested order creation on prod with live keys:
- Created order_Tr2J19L8pVnyeW for Rs 99 (9900 paise)
- Currency: INR
- Live key prefix: rzp_live_T...

Confirmed: Razorpay is NOT the blocker for zero revenue. The issue is
conversion (users don't click "buy"). Certificate CTAs aim to fix this.


---

### RESOLVED - G6 Google OAuth end-to-end (2026-10-25, c793fed + aadb13d)

Google OAuth now works end-to-end on prod. Six auth bugs found and fixed plus one 401 redirect bug.

Bugs fixed:
1. require_auth() didn't read charvak_auth_token cookie
2. /api/auth/login only set cookie for admins
3. checkLoginState() only read localStorage
4. find_or_create_user didn't set verified=TRUE on link
5. Google consent screen missing 2024+ required fields
6. Stale browser cookies masking state
7. 401 handler redirecting homepage visitors

Fix summary:
- require_auth() reads charvak_auth_token
- /api/auth/login sets charvak_auth_token for all users
- checkLoginState() falls back to /api/auth/me with credentials:include
- find_or_create_user sets verified=TRUE on link
- Google consent screen fully configured
- 401 handler skips redirect for /api/auth/me

Verified on prod: password login works, Google OAuth works, user record shows auth_provider=google + verified=True + google_oauth_id set, homepage accessible to anonymous visitors.

Verdict: RESOLVED.

---

### RESOLVED - W1 homepage Placement OS reframe (2026-10-25, aadb13d)

Homepage now positions Charvak as 'The Placement Operating System for Indian Colleges' via a green strip above the existing hero. Full product suite has a home in the More from Charvak section below the 3 pillars.

Closes W1 from GAPS_AND_WEAKNESSES_MASTER.md.