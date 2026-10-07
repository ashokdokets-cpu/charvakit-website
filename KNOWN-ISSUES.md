# Charvak — Known Issues Registry

**Created:** 2026-09-18
**Last updated:** 2026-09-28 (Session C)
**Purpose:** Central registry for bugs, dead code, and design issues found during the persistence project. Every session appends to this file. Session I resolves what's still open.

**Legend:** 🔴 data integrity | 🟠 feature gap | 🟡 cosmetic | 🟢 hygiene

---

### V4-adjacent gap — scripts with `load_dotenv()` silently target prod (2026-09-26)

- **Discovered during:** Voice-to-Web Option 2 E2E testing.
- **Reality:** `.env.local` gets renamed `.env.local.off` when testing against prod.
  Any dev script run during that window that calls plain `load_dotenv()` (no args)
  will load `.env` → **prod**. Not dev.
- **Consequence:** the dev user's verification row was inserted into prod while the
  server was pointed at dev — leading to a 30-minute 403 debugging rabbit hole that
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
| 2026-09-18 | G/4 | `na_module/resume_engine.py` | PII phone regex had a capture group → `re.findall` returned empty strings → `replace('', ...)` inserted redaction marker between every character (86 chars → 1529 chars) | Non-capturing group `(?:...)` |
| 2026-09-18 | G/2 | `na_module/vms_connector.py` | `job_id = f"NA-JOB-{hash(str(raw_data))}"` — `hash()` randomized per process, IDs changed on every restart | `secrets.token_hex(4).upper()` |
| 2026-09-18 | G/4 | `na_module/resume_engine.py` | `vendor_id = f"VEN-{hash(...)}"` — same bug | `secrets.token_hex(4).upper()` |
| 2026-09-18 | E/4 | `final_year_project_engine.py` | AI methods called `json.loads(response.choices[0].message.content)` without `response_format`; GPT-4o-mini returned prose + markdown fences → `Expecting value: line 1 column 1` | `response_format={"type": "json_object"}` + defensive fence strip |
| 2026-09-18 | J/6 | `ai_question_generator.py` | `generate_with_openai` had no `response_format` (same AI JSON bug class) | Added `response_format={"type": "json_object"}` + defensive fence strip + regex fallback |
| 2026-09-18 | J/3 | `indian_language_ai.py` | Mojibake emoji in `translate_job_ad` ad string (rocket, pin, arrow) | Converted to `\U` escapes; real Hindi/Tamil/Telugu content preserved as raw UTF-8 |
| 2026-09-18 | J/2 | `content_generator.py` | `_deduplicate` crashed on `sentence_builds` items (dict with list `words` value — unhashable) | Stringify non-string keys via `str()` |
| 2026-09-18 | J/2 | `content_generator.py` | `_generate_with_ai` had no `response_format` + no timeout (same AI JSON bug class) | Added `response_format={"type": "json_object"}` + timeout + defensive fence strip |
| 2026-09-18 | H/8 | `advanced_assessment_engine.py` | `_generate_mcq_with_openai` AI JSON parsing without `response_format` + no timeout + fragile regex-only extraction | Added `response_format={"type": "json_object"}` + timeout + defensive fence strip + regex fallback |
| 2026-09-18 | H/8 | `advanced_assessment_engine.py` | Dead `user_scores` field (declared, never written) | Removed; no table created |
| 2026-09-18 | H/6 | `ai_bridge_engine.py` | Two AI JSON parsing calls without `response_format` (question generation + report evaluation) | Added `_ai_json()` helper with `response_format={"type": "json_object"}` + defensive fence strip |
| 2026-09-18 | H/5 | `training_mapping_engine.py` | `get_job_market_insights` avg_salary mojibake stripped to bare `",000 - ,000"` (both ranges empty). Restored to sensible `Rs.8L - Rs.30L` style | Manual restoration |
| 2026-09-18 | H/2 | `enhanced_assessment_engine.py` | Dead `question_cache` field + missing `response_format` on AI call | Removed dead field; added `response_format` + timeout + defensive fence strip |
| 2026-09-18 | TierE | `payment_engine.py` | `self.payments` in-memory list backed admin endpoints (`get_all_payments`, `get_payment_status`); all reset on restart | Persist to `charvak_payment_log` with `raw_data JSONB` |
| 2026-09-18 | D/2 | `brand_engine.py` | `promote_job` used `timedelta` without importing it — every call would `NameError` | Added `from datetime import timedelta` |
| 2026-09-18 | D/1 | `badge_engine.py` | `share_text` had mojibake `ðŸ†` instead of 🏆 | `\U0001F3C6` unicode escape |
| 2026-09-18 | F/3 | `marketing_ai_engine.py` | Mojibake in templates — `ðŸš€` instead of 🚀 in every generated job ad / social post | `\U0001F680` unicode escapes (source stays ASCII) |
| 2026-09-18 | F/4 | `dynamic_role_engine.py` | `recommend_custom_role` mutated in-memory `role_database` — custom roles lost on every restart | Persist to `charvak_dynamic_custom_roles`, merge into `get_all_roles()` |
| 2026-09-17 | C | `main.py` | `GET /api/exam/progress` shadowed by `/api/exam/{exam_id}` catch-all | Routes inserted before catch-all |
| 2026-09-17 | C/3 | `exam_prep_engine.py` | Docstring said "83 exams" but actual catalog is 67 | Updated to 67 |

---

## Open — data integrity 🔴
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
| 1 | `na_module/revenue_engine.py` | `create_subscription` | Re-subscribe re-adds `monthly_fee` to `transactions` without adding a new subscription row. Revenue inflates silently on tier changes | TBD — product decision |
| 2 | `na_module/resume_engine.py` | `SubVendorManager.track_submission` | Duplicate `(vendor, candidate, job)` bumps `active_candidates` counter even though the row is deduped via `ON CONFLICT DO NOTHING` | TBD |
| 3 | `na_module/charvak_vms.py` | `approve_timecard` | Repeated approvals grow `approval_history` and overwrite `payment_reference` (no guard for already-approved state) | TBD |
| 4 | `migrations/20260916_course_payments.sql` | Foreign key | References `charvak_enrollments` which no migration creates. Fresh-clone / DR restore fails | Session I |
| 5a | `payment_engine.py` | `is_ready()` | `/api/payment/status` publicly returns `razorpay_key_id` + `paypal_client_id` — should trim to just bool flags. (Secret values NOT leaked — key_id is the public half.) | Security audit |
| 5 | `main.py` | `/api/exam/progress`, `/api/exam/history`, `/api/exam/study-plan` | No auth check — anyone can query any email's data | Security audit |
| 6 | `whatsapp_bot.py` | ~line 92 | AI JSON parsing bug (same as fixed in E/4) | When WhatsApp unblocks (external) |
| 6a | `badge_engine.py` | `self.certifications` | Dead field — declared but never written to, no table created | Session I or future work |
| 6b | `profile_network_engine.py` | `self.referral_matches` | Dead field — computed inline but never stored in list, no table created | Session I |
| 6c | `profile_network_engine.py` | `candidate_data` in master_profiles | Snapshot at create time — goes stale after candidate updates their own profile | Product decision |
| 6d | `university_engine.py` | `student_count` | Denormalized counter — only increments (no `remove_student` method exists) | Product decision |
| 6e | `messaging_engine.py` | `get_stats.unread_messages` | Counts only `sent`+`delivered` — excludes `replied` | Product decision |
| 26 | `ai_bridge_engine.py` | `get_premium_report` |
| 27 | `enterprise_engine.py` | `review_resume` | Typo in response: `f"Resume {decision}d"` → "Resume rejectd" for reject | Cosmetic / Session K |
| 28 | `enterprise_engine.py` | `record_survey_response` / `kiosk_check_in` | Increment counters but don't store respondent/student data (matches original) | Product decision |
| 30 | `content_generator.py` |
| 31 | `indian_language_ai.py` | `self.translations` | Dead field — declared but never written, `get_stats.total_translations` always 0 | Session K or later |
| 32 | `indian_language_ai.py` |
| 33 | `role_manager.py` + `dynamic_role_engine.py` | Custom roles | Two parallel custom-role stores (`charvak_role_manager_custom_roles` + `charvak_dynamic_custom_roles`). `role_manager.get_all_roles()` merges both via `dynamic_role_engine.get_all_roles()` + own table. Consolidation is a future refactor | Session K or I |
| 34 | `monitor_service.py` | `SiteMonitor.check_site` | `requests.Session(timeout=10)` is invalid - Session takes no `timeout` kwarg. Every check fails with TypeError, but the error is captured in `issues` (matches original behavior) | Session K or I |
| 35 | `monitor_service.py` |
| 36 | `ai_question_generator.py` | `self.used_questions` | Dead field - declared but never written or read | Session K or later |
 module-level state | Original used module-level `monitored_sites = {}` and `alert_history = []`. Now DB-backed; dummy `monitor = SiteMonitor("", "")` kept for backwards-compat | Done (this session) |
 `submit_assessment` | Score not persisted back to assessment record (matches original) | Product decision |
 `self.content_cache` | Dead field — declared but never written to, no table created | Session K or later |
| 29 | `voice_to_web_engine.py` | (not audited yet) | Persistence deferred to Session B-2 | Session B-2 |
 Not idempotent - calling twice for same session creates 2 premium rows + doubles revenue | Product decision / bug fix |
| 25 | `chatbot_engine.py` | `_match_faq` | Keyword keys don't match FAQ question text - some FAQs unreachable (e.g. "pricing" keyword vs "cost" in question text). Falls back to AI. | Product decision / bug fix |
| 7 | `ai_bridge_engine.py` | `_generate_ai_questions` + `_generate_report` | AI JSON parsing bug (missing `response_format`, both places) | FIXED in H/6 |
| 5b | `outreach_engine.py` | `subscribe_premium`, `connect_gmail` | No UNIQUE constraint — multiple subscriptions and Gmail syncs allowed per email (matches original behavior) | Product decision |
| 5c | `dynamic_role_engine.py` | `recommend_custom_role` | Anyone can add a global custom role — no auth, no per-user scoping | Security audit |
| 5d | `dynamic_role_engine.py` | `create_dynamic_training_plan` | Stateless — plan returned but not stored (matches original) | Product decision |

---

## Open — feature gaps 🟠

| # | File | Issue | Fix in session |
|---|---|---|---|
| 8 | `final_year_project_engine.py` | `total_projects` always returns 0 — `self.projects` was a dead field | Future feature work |
| 9 | `ai_internship_engine.py` | `submit_work` uses `random.randint(7,10)` for score | Product decision |
| 10 | `exam_prep_engine.py` | Icons changed from emoji to ASCII IDs — needs frontend mapping | When UI is built |
| 11 | `main.py` | Exam prep frontend mock-test UI doesn't exist (backend + routes live) | Dedicated UI session |
| 12 | `na_module/charvak_vms.py` | `vendor_performance` dead field — never written to | Future feature work |
| 13 | `student_suite_engine.py` | `assist_assignment` / `assist_research` return stubs — no real AI | Feature work |
| 26 | `advanced_assessment_engine.py` | `_generate_versant_questions` | Declared question counts (e.g. repeats=16) exceed available static prompts (4) — questions limited by prompt count | Feature gap |
| 14 | `na_module/vector_matcher.py` | `SKILL_EMBEDDINGS` is a small static dict; comment says "in production, use pgvector/Pinecone" | Future scaling |
| 15 | Analytics Dashboards | Never audited; page exists but no data source verified | Dedicated audit |

---

## Open — cosmetic 🟡

| # | File | Issue |
|---|---|---|
| 15a | `notification_engine.py` | Mojibake in email subject (`âš ï¸` instead of warning emoji) — fix in Session H |
| 15b | `products_engine.py` | Mojibake in log message (`âœ…`) — fix in Session H |
| 16 | Multiple engines | Heading order on remaining pages (accessibility) |
| 17 | Site-wide | TBT ~1,900ms mobile — needs conditional script loading |
| 18 | `na_module/vector_matcher.py`, `work_auth.py`, etc. | Emoji icons in some docstrings — clean up during Session I |

---

## Open — hygiene / process 🟢

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

1. **Every session appends to it** — if you preserve a bug, note it here.
2. **Fixed items move to "Fixed"** with date + fix reference.
3. **Session K** is the dedicated bug-cleanup session. **Session I** does the final capstone + tag.
4. **Keep it in git** so it survives across machines and sessions.

### Open — pattern: frontend handlers reference undefined variables (2026-10-02)

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


### Open — Indian Language AI: questions generated but not displayed (2026-10-02)

Full detail in COMMITMENT.md. The Language Assessment flow shows a
summary ("5 questions created") and never renders the questions, never
collects answers, never calls /submit.

Fix: 30-60 min. Backend returns questions or new GET endpoint +
frontend renders them + wires /submit + shows score.

Verdict: SCHEDULED - next cleanup session

---

### Open — PowerShell process-kill leaves stale workers (2026-10-03)

Hit this multiple times during Sessions 9-13:

- `Stop-Process -Name python` runs but a "python" process remains
- Subsequent curl hits the OLD code even after a "restart"
- `taskkill /PID X /F` fails with "Process not found" moments later
- Port 8000 has no listener even though `Get-Process` shows python

Root cause: `--reload` spawns a supervisor + worker. Killing the
supervisor leaves the worker holding the port. Some windows the
`Get-Process` snapshot is also stale (process exited between commands).

Fix — always verify after kill:

    Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Get-Process | Where-Object { $_.ProcessName -eq "python" } | Select-Object Id, ProcessName, Path

If a process remains, kill it explicitly by PID. If it says "not found"
but still shows, wait 2 seconds and re-check. Never assume the kill
worked — verify.

Verdict: DOCUMENTED — apply the verify pattern


### Open — PowerShell Get-Content displays correct UTF-8 as mojibake (2026-10-03)

Two false alarms during Sessions 13-14 (COMMITMENT.md, CAREER-ASSESSMENT-PLAN.md):

Files displayed as `â€"` (mojibake) in PowerShell's `Get-Content` output,
but the bytes on disk were clean UTF-8 em-dashes.

Root cause: Windows PowerShell 5.x `Get-Content` uses the console code page
for output. `[System.IO.File]::ReadAllBytes()` and `ReadAllLines(path, UTF8)`
show the truth.

Fix — always verify with:

    [System.IO.File]::ReadAllLines("path", [System.Text.Encoding]::UTF8)

Never "fix" apparent mojibake without this check first. The earlier
em-dash fix attempts might have been display-only, not real disk bugs.

Verdict: DOCUMENTED — never fix mojibake without the byte check


### RESOLVED — PayPal credits capture test (2026-10-03, db9e2a1)

The Session B flag (#3 PayPal live capture test) is closed. Full
sandbox flow verified end-to-end with a US sandbox buyer + US sandbox
merchant. See COMMITMENT.md for details.

Verdict: RESOLVED


### FLAGGED — PAYPAL_MODE should be explicit on Render (2026-10-03)

The new `PAYPAL_MODE` env var defaults to "live" when unset, so Render
works correctly today. But an explicit value is clearer for ops and
prevents accidental sandbox routing on production.

Fix: add `PAYPAL_MODE=live` to Render's Environment tab.
Est: 1 min. Verdict: SCHEDULED — next Render dashboard session



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

### RESOLVED — Anti-Cheating Layer A (2026-10-06, 1124a38 + 91e1b1f)

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


### RESOLVED — Admin UI for integrity events + public Trust Score badge (2026-10-07, 33cb2f6)

Session 27 shipped the integrity engine (event capture). Session 38
shipped the surfaces that make it useful:

- `/admin/integrity-events` — list of all assessments with integrity
  events, sorted by risk level, filterable by risk and email/ID
- `/admin/integrity-events/{aid}` — full event timeline with metadata
  card and per-type filters
- `/api/admin/integrity-events` — new admin list endpoint
- `GET /api/readiness/{cert_id}/integrity` — public endpoint returning
  only {risk_level, verified, total_events, message}
- `integrity_engine.get_public_summary()` — strips per-type counts and
  timestamps so the public badge can't leak assessment detail
- Trust Score badge on `/readiness/{id}` — 4 states, explainer collapse,
  silent-fail

**Verified:** 21 assessments in the list, 87-event detail renders all
five event types, clean + elevated badge states both confirmed on the
certificate. Reverted after the elevated test — cert back to clean.

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
- Admin list shows "English Assessment · versant"
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