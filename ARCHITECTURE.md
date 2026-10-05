# Charvak Architecture

**Last updated:** 2026-10-03
**Version:** v3.5-session-13-20261003

---

## High-Level System
┌──────────────────┐
│ Cloudflare │
│ (CDN + WAF) │
└────────┬─────────┘
│
▼
┌──────────────────┐
│ Render (SG) │
│ FastAPI/Uvicorn │
│ srv-d9hhljd8... │
└────────┬─────────┘
│
┌────┼────┬───────────┐
│ │ │ │
▼ ▼ ▼ ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│Render │ │Razorpay│ │ SendGrid │ │ OpenAI + │
│Postgres│ │+ PayPal│ │ + GA4 │ │ElevenLabs│
│vouchai │ │LIVE │ │ │ │ │
└────────┘ └────────┘ └──────────┘ └──────────┘

text

---

## Request Lifecycle
Browser → Cloudflare → Render (uvicorn) → FastAPI app
│
┌─────────────────────────────────┼──────────────────────┐
│ │ │
▼ ▼ ▼
Static middleware SecurityHeaders Route handler
(CachedStaticFiles) middleware (main.py)
│
▼
Engine call
(ai_credit_engine,
payment_engine,
ai_courses,
complete_mock_drive,
results_system, etc.)
│
▼
database.py
│
▼
Render Postgres

text

**Middleware stack (in order):**
1. `SecurityHeadersMiddleware` - CSP, HSTS, X-Frame-Options, etc.
2. `MaxBodySizeMiddleware` - request size limits
3. `CORSMiddleware` - cross-origin rules
4. Rate limiting (slowapi `@limiter.limit`)
5. Admin auth guard - protects `/admin*` and `/api/admin*`

---

### DoketsRB Integration (v3.5, 2026-09-24)

- **Deep-link bridge** — `doketsrb_integration.request_score_link(candidate_id)` returns a signed
  URL pointing at `https://www.doketsrb.com/#ats-scanner`
- **Manual score entry** — after the user runs the free ATS check, Charvak prompts for the score
  and writes via `record_external_score()` → `charvak_candidates.skill_score`
- **Callback flow scaffolded** — `consume_score_callback()` and `/api/ats/score-callback` are in place
  for when DoketsRB adds a server-side `/ats-check` route that supports `return_url`
- **Tables:** `charvak_doketsrb_score_tokens`, `charvak_doketsrb_score_events`
- **Credit key:** `ats_jd_score` (5 cr, only when `target_role` is provided)


### HTTPException re-raise pattern (2026-09-28)

Every guarded route in main.py wraps its body in a try/except Exception block
that returns a friendly JSON error via handle_error(). If a guard
(require_auth_for_email, require_admin, require_credits_from_data) raises
HTTPException(401/403/402), that broad except catches it and returns HTTP 200
with an error payload - the guard never fires.

**Fix (applied to 147 routes on 2026-09-28, commit a8e1275):**

    try:
        ...
        require_auth_for_email(request, email)   # raises HTTPException
        ...
    except HTTPException:
        raise                                    # <-- propagate to FastAPI
    except Exception as e:
        return handle_error(e, ...)

FastAPI built-in handler converts the re-raised exception into the correct
status code (401/403/402).

**Rule for new routes:** any route that calls a guard inside a try/except with
a broad except Exception MUST include "except HTTPException: raise" as the
first except clause.

**Test-tooling caveat:** curl.exe on PowerShell strips backslash-escaped
quotes inside -d payloads. Use --data-binary @file with a JSON file to
avoid malformed-JSON artifacts that look like guard failures. Details in
DEV-SETUP.md.


## Authentication Flow

### Registration
POST /api/auth/register
→ auth.register_user(email, password, name)
→ database.create_user() inserts into users
→ email_verification.generate_token() → email_verification_tokens
→ email_engine.send_email() → SendGrid
→ user must click link before login

text

### Login
POST /api/auth/login
→ api_login (main.py ~line 1041)
→ if email in ADMIN_EMAILS: skip verification
→ else: email_verification.is_verified(email) - queries tokens table
→ if not verified: 403 "verify first"
→ auth.login_user() checks password hash
→ if admin: set charvak_admin_token cookie (HttpOnly, Secure, SameSite=Lax)
→ returns user + token

text

### Session
- Frontend stores `auth_token`, `userEmail`, `userName` in localStorage
- Admin session uses HTTPOnly cookie `charvak_admin_token`
- `require_admin()` checks the cookie

---

## Credits System (post Fix B)

### Storage
- **Postgres table:** `charvak_user_credits` (email PK)
- No more in-memory - survived a real fix on 2026-09-12
- `daily_usage` is JSONB: `{"2026-09-13": {"calls": 3, "credits": 15}}`

### Plans
| Key | Name | Price (INR) | Credits | Validity |
|---|---|---|---|---|
| free | Free Trial | 0 | 50 | 7 days |
| starter | Starter | 99 | 500 | 30 days |
| pro | Pro | 299 | 2000 | 30 days |
| premium | Premium | 999 | 10000 | 90 days |
| enterprise | Enterprise | 4999 | 50000 | 365 days |

### Feature costs (per AI tool call)
Stored in `FEATURE_CREDITS` dict in `ai_credit_engine.py`:
- `chatbot_query` - 2
- `resume_roast` - 5
- `fyp_documentation` - 30
- `default` - 10

### Admin bypass
`check_and_deduct()` returns immediately for admin emails with `credits_remaining: 999999999`.

---

## Payment Flow (post Fix A/B/C + v2.0 course payments)

### Credit purchase - order creation
POST /api/payment/create-order {amount, plan, email, name}
→ payment_engine.create_razorpay_order(
amount_inr = amount*100,
receipt = rcpt_YYYYMMDDHHMMSS_XXXX,
notes = {plan, email, tool, amount_inr}
)
→ Razorpay API creates order
→ returns {order_id, key_id, amount, currency}

text

### Client-side verify (happy path)
Browser: user pays → Razorpay returns signature
→ POST /api/payment/verify {payment_id, order_id, signature}
→ payment_engine.verify_razorpay_payment() - HMAC check
→ if verified: POST /api/credits/purchase {email, plan, payment_id}

text

### /api/credits/purchase (Fix A)
Read email, plan, payment_id

If plan == "free" → grant directly (no payment needed)

If plan is paid:
a. require payment_id (else 402)
b. payment_engine.fetch_razorpay_payment(payment_id)
c. check status_field == "captured"
d. check amount matches plan price
e. call ai_credit_engine.purchase_credits(email, plan, payment_id)

text

### Webhook (Fix C)
Razorpay → POST /webhook/razorpay
X-Razorpay-Signature: <hex>
Body: {"event": "payment.captured", "payload": {...}}

Read raw_body, signature

payment_engine.verify_webhook_signature(raw_body, signature)
→ HMAC-SHA256 with RAZORPAY_WEBHOOK_SECRET

Parse JSON

Extract: payment_id, notes.plan, notes.email

If event not in (payment.captured, order.paid) → ignore

Call purchase_credits() - same idempotent path

Return 200 (even on error - prevents Razorpay retry storms)

text

### Idempotency
- `charvak_credit_purchases.payment_id` has UNIQUE constraint
- Second call with same payment_id → `{already_credited: true, credits_added: 0}`

---

## Course Fee + EMI Flow (v2.0)

### Order creation (India vs Global)
Student lands on /course/{course_name}
│
▼
GET /api/ai-course/price/{course}?level=X&country=YY
│
▼
resolve_price(course_name, country_code, level)
│
├── country=IN → read charvak_course_levels.price_inr
│ return {currency: INR, amount, emi_eligible: true,
│ schedule: {num_installments, blocks}}
│
├── Tier-1 (US/GB/EU/AE/SG/AU) → read charvak_course_prices.amount_local
│ apply LEVEL_MULTIPLIERS (0.6/1.0/1.6)
│ round to X.99
│
└── Rest of world → convert level-specific INR via payment_engine.INR_RATES

text

### Enrollment + payment
Student clicks Enroll
│
▼
POST /api/ai-course/create-order {email, course_name, country_code, level}
│
▼
ai_courses.enroll_student_paid(email, course_name, country_code, level)
│
▼
ai_course_payments.create_enrollment_paid(...)
│
├── INSERT charvak_enrollments (status='pending_payment', user_level=level)
├── if country=IN: compute_emi_schedule(price_inr, level_weeks)
│ INSERT charvak_course_installments (N rows)
│
▼
payment_engine.create_razorpay_order(...)
notes = {tool:'ai_course', email, course_name, enrollment_id,
payment_type, installment_num, gateway, level}
│
▼
Razorpay modal opens; student pays
│
├── Client callback: POST /api/ai-course/confirm-payment
│ verify sig → fetch_razorpay_payment → check captured + amount
│ → ai_courses.record_course_payment(...)
│ → UPDATE charvak_course_installments SET status='paid'
│
└── Webhook (parallel): POST /webhook/razorpay
branch on notes.tool == 'ai_course'
same record_course_payment path (idempotent)

text

### Access gate
Student opens /my-course/{enrollment_id}
│
▼
GET /api/ai-course/access/{enrollment_id}/{week_num}
│
▼
ai_courses.check_course_access(...)
│
├── allowed: true → render lesson
└── allowed: false → return unlock offer:
{week_num, installment: {num, of}, amount_inr,
unlocks_weeks, due_date, days_until_due,
pay_url, message}

fire in-context reminder email (24h throttle)

text

### EMI milestone-block model (India only)

- 2 blocks for courses up to 8 weeks
- 3 blocks for longer
- Block boundaries computed from level-specific duration
- Each paid installment unlocks its block of weeks
- Earlier blocks are smallest (never front-load content)
- Earlier installments round UP (student pays more to unlock sooner)

### Reminder emails (cron)

- Render Cron `send-emi-reminders` runs daily 9:00 AM IST
- Stages: T-3d, due-date, +1d, +3d, +7d
- Dedupe via `last_reminder_stage` column
- In-context reminder: fires when student hits a locked week (24h throttle)

---

## Mock Drives Flow (v2.2)

### Session start
Student on /mock-drive
│
▼
GET /api/company-patterns/{company_id} → list of patterns
│
▼
Student clicks Start
│
▼
POST /api/mock/start-complete {email, company_id}
│
▼
complete_mock.start_mock_drive(email, company_id)
│
├── get_company_config(company_id) → exact question counts
├── for each section, generate_ai_questions(topic, count)
│ OpenAI call with prompt specifying 0-based INDEX for correct
│ _sanitize_questions(...) → ensure correct is int 0..N-1
│
├── INSERT charvak_mock_sessions (sections_json JSONB, status='in_progress')
│
▼
Return full session with questions to frontend

text

### Answer submission
Student clicks option
│
▼
POST /api/mock/submit-complete {session_id, section_name, question_id, selected_option}
│
▼
complete_mock.submit_answer(...)
│
├── defensive int(selected_option)
├── INSERT INTO charvak_mock_answers
ON CONFLICT (session_id, section_name, question_id)
DO UPDATE SET selected = EXCLUDED.selected
(idempotent per question)

text

### Scoring + result recording
Student clicks Submit
│
▼
POST /api/mock/complete-full {session_id}
│
▼
complete_mock.complete_mock(session_id)
│
├── SELECT sections_json, total_questions FROM charvak_mock_sessions
├── SELECT all answers FROM charvak_mock_answers
├── compute score = correct/total * 100
├── UPDATE charvak_mock_sessions
SET status='completed', score, correct_count, passed
├── results_system.record_assessment_result(...)
INSERT charvak_assessment_results
│
▼
Return results to frontend

text

---

## Static Assets (post-performance fixes)

### CachedStaticFiles
Custom subclass of Starlette's `StaticFiles` in `main.py`:
```python
class CachedStaticFiles(StarletteStaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            # Session B (f58e63f): revalidate hourly instead of immutable
            # to fix the ?v= bump footgun. Every JS/CSS edit required
            # manually bumping ?v= in every template before this change.
            response.headers["Cache-Control"] = "public, max-age=3600, must-revalidate"
        return response

app.mount("/static", CachedStaticFiles(directory="static"), name="static")
Script loading strategy
Razorpay, PayPal, Chart.js, Bootstrap JS → all defer (loads after DOM parse, no render-block)

Google Fonts → <link> with preconnect (not @import)

Fonts cached for 1 year (font files are immutable; JS/CSS revalidate hourly)

Deployment
Auto-deploy
text
git push origin main
→ GitHub webhook → Render detects change
→ Render builds (pip install -r requirements.txt)
→ Render starts (uvicorn main:app --host 0.0.0.0 --port $PORT)
→ ~2 min total
Rollback
bash
# Immediate rollback to previous stable tag
git checkout v1.1-stable-20260913
git checkout -b rollback
# or force-reset main if needed
git reset --hard <previous-commit>
git push origin main --force-with-lease
Environment
Python: 3.11.9 (from runtime.txt)

Build command: pip install -r requirements.txt

Start command: uvicorn main:app --host 0.0.0.0 --port $PORT

Health check: / returns 200

Backup & Restore
Backup
powershell
python scripts\full_backup.py
Creates:

Folder: Desktop/Charvak_Complete_Backup_YYYYMMDD_HHMMSS/

ZIP: same name + .zip

Includes: source, templates, static, migrations, scripts, .env, .git/, _DB_DUMP/ (all charvak_* tables), manifest, README

Restore on new machine
Unzip archive

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

.env is already present (contains secrets)

Optional DB restore: psql $env:DATABASE_URL -f _DB_DUMP\_charvak_all_tables.sql

uvicorn main:app --reload --port 8000

Data Model
users
text
user_id (PK)      TEXT
email (UNIQUE)    TEXT
password_hash     TEXT
name              TEXT
phone             TEXT
role              TEXT (default: 'candidate')
created_at        TIMESTAMP
charvak_user_credits
text
email (PK)        TEXT
plan              TEXT
credits_remaining INTEGER
total_credits_used INTEGER
total_ai_calls    INTEGER
daily_usage       JSONB
last_daily_bonus  DATE
expires_at        TIMESTAMP
created_at        TIMESTAMP
updated_at        TIMESTAMP
charvak_credit_purchases
text
purchase_id (PK)  TEXT
email             TEXT
plan              TEXT
price             INTEGER
credits_added     INTEGER
payment_id        TEXT UNIQUE
status            TEXT ('completed')
created_at        TIMESTAMP
charvak_credit_usage_history
text
usage_id (PK)     TEXT
email             TEXT
feature           TEXT
credits_used      INTEGER
created_at        TIMESTAMP
Charvak course + tier + mock tables (v2.0 - v2.2)
text
charvak_course_prices
  course_name, country_code, currency, amount_local, razorpay_paise
  PRIMARY KEY (course_name, country_code)

charvak_course_payments
  payment_id PK, enrollment_id, email, course_name, country_code,
  currency, amount_local, amount_inr, payment_type, installment_num,
  razorpay_payment_id UNIQUE, razorpay_order_id, paypal_order_id,
  gateway, status, created_at

charvak_course_installments
  installment_id PK, enrollment_id, email, installment_num,
  total_installments, amount_inr, unlocks_from_week, unlocks_to_week,
  due_week, due_date, status, paid_at, payment_id,
  last_reminder_stage, last_access_reminder_at,
  UNIQUE(enrollment_id, installment_num)

charvak_course_levels
  course_name, level, price_inr, duration_weeks, description, status
  PRIMARY KEY (course_name, level)

charvak_mock_sessions
  session_id PK, email, company_id, company_name, pattern,
  sections_json JSONB, total_questions, started_at, completed_at,
  status, score, correct_count, passed

charvak_mock_answers
  answer_id PK, session_id, section_name, question_id, selected,
  submitted_at, UNIQUE(session_id, section_name, question_id)

charvak_assessment_results
  result_id PK, email, assessment_type, assessment_name, score,
  total_questions, correct_answers, percentage, passed,
  details_json JSONB, completed_at
Security Layers
Cloudflare - DDoS, WAF, SSL termination

CSP - restrictive content-security-policy header

HSTS - 1-year strict transport security

Rate limiting - slowapi on all public endpoints

Admin middleware - charvak_admin_token cookie required

HMAC verification - Razorpay + PayPal webhook signatures

Parameterized SQL - no string concatenation in queries

Known weakness: CSP allows unsafe-inline and unsafe-eval (Bootstrap requirement). Hardening would break the site without a refactor.

## University Subscriptions (Session 8, v3.5)

Universities purchase portal access via a credit-based subscription.
Three tiers, all 365-day validity.

### Tiers

| Tier | Credits | Rupee equivalent |
|---|---|---|
| `university_starter` | 4000 | ~Rs 19,999/yr |
| `university_growth` | 10000 | ~Rs 49,999/yr |
| `university_enterprise` | 20000 | ~Rs 99,999/yr |

(1 credit ~= Rs 5, matching the Pro plan rate.)

### Tables

- `charvak_university_subscriptions` (university_id PK, admin_email,
  tier, price_inr, credits_used, started_at, expires_at)

### Routes

- `POST /api/university/register` - auth-gated (was open before Session 8)
- `POST /api/university/subscribe` - auth + credits

### Frontend

- `templates/university.html` - 3 tier buttons wired to `chooseTier()`
- Registers the university first (if new), then subscribes
- Fix in Session 8: removed a shadowing `notifyMe` script block that
  hijacked `registerUniversity` in an older template version

### Security note

Session 8 closed an open IDOR: `/api/university/register` accepted any
`admin_email` with no auth. Now forces `admin_email = caller's email`
after `require_auth_for_email`.

---

## Legacy-Shift Migration Tier (Session 8, v3.5)

The Legacy-Shift product has two tiers:
- **Free analysis** (25 cr) - AI identifies vulnerabilities, deps,
  recommended stack, and migration steps for a code snippet
- **Full migration plan** (1000 cr, ~Rs 4,999) - file-by-file plan with
  data migration steps, test plan, rollback strategy, and post-launch
  checklist

### Table

- `charvak_legacy_shift_reports` (report_id PK, email, code_preview,
  analysis_json, plan_json, credits_used, created_at)

### Routes

- `POST /api/ai/analyze-legacy` - 25 cr (existing)
- `POST /api/ai/legacy-shift-migration-plan` - 1000 cr (Session 8)

### Credit key

- `legacy_shift_migration: 1000`

### Frontend

- `templates/legacy-shift.html`
- The migration CTA appears only after a successful free analysis
- Renders the plan with the same recursive JSON viewer as the free tier

---

## Silent-Killer Sentinel (Session 9a, v3.5)

Real URL monitoring. Before Session 9a, `products_engine.silent_killer_monitor`
returned a fake monitor_id and never touched the URL. Session 9a makes
the free-tier scan real: fetch the URL, record the result, persist a
watch + a scan history.

### Tables

- `charvak_silent_killer_watches` (watch_id PK, email, url, name,
  interval_minutes, active, last_scan_at, last_status,
  last_status_code, last_error, alert_count, created_at)
- `charvak_silent_killer_scans` (scan_id PK, watch_id, email, url,
  status_code, response_ms, ok, error, checked_at)

### Engine methods (products_engine.py)

- `_ensure_silent_killer_tables()` - self-healing DDL
- `_check_url(url)` - requests.get with timeout=10, allow_redirects=True.
  Never raises. 4xx/5xx = ok=False, connection errors = ok=False with
  error string.
- `silent_killer_monitor(data)` - creates watch + first scan
- `silent_killer_recheck(data)` - re-check by watch_id
- `silent_killer_list_watches(email)` - dashboard
- `silent_killer_history(watch_id, email, limit)` - scan log
- `silent_killer_delete_watch(watch_id, email)` - removes watch + scans
- `silent_killer_run_watch(watch_id)` - cron-facing (used in Session 9b)

### Routes

- `POST /api/products/silent-killer/monitor` - 15 cr (setup)
- `POST /api/products/silent-killer/recheck` - 5 cr
- `GET /api/products/silent-killer/watches/{email}` - auth
- `GET /api/products/silent-killer/history/{watch_id}` - auth
- `DELETE /api/products/silent-killer/watch/{watch_id}` - auth

### Credit keys

- `product_silent_killer: 15`
- `silent_killer_recheck: 5`

### Frontend

- `templates/silent-killer.html` - hero badge now says "Live - On-Demand
  Scans Working"
- "Your Monitors" panel below the setup form, loads on DOMContentLoaded
- `loadWatches` / `recheckWatch` / `toggleHistory` / `deleteWatch`
- XSS-safe rendering via `_skEsc()`

### Still pending (Session 9b)

- Render cron that runs checks on schedule
- Email alerts on state change
- The "Notify Me When Continuous Monitoring Ships" button is still there

---

## Indian Language AI - real MCQ scoring (Sessions 20-21, v3.5)

The Language Assessment flow on `/indian-language-ai` used to be
half-built: the backend generated questions and stored them, but the
frontend only showed a summary. Session 20-21 made it a real product.

### What changed

- Free-text questions -> MCQ with 4 options and a correct index
- Real deterministic scoring (compare user's pick to correct_index)
- 10/15/20 question selector
- `correct_index` stripped from the frontend response (cheat prevention)
- Server-side option shuffle: even if the AI always put the right
  answer at index 0, users see varied positions
- Auth + email-match on `/api/indian-languages/submit` (was open)
- Static fallback replaced: old catalog had mojibake in 12 languages

### Credit key

- `indian_language_assessment: 10`

### Frontend

- `templates/indian-language-ai.html`
- Radio buttons per question, per-question progress badge
- Score + correct_count display

### One lesson

The old scoring was `len(answers) * 30 + 10` - it counted answers,
not correctness. Submitting junk gave 100%. Fixed in Session 21.

---

## Career Assessment (Sessions 10-13, v3.5)

A dedicated career readiness product at `/ai-assessment`. Calibrated
to (role x industry x level). Ships as 8 formats across 3 phases.

### Phase 1 (Session 10, MCQ only)

- New engine: `career_assessment_engine.py`
- Catalog: 106 roles x 66 industries x 7 levels
- Tables:
  - `charvak_career_assessments` (assessment_id PK, email, role,
    industry, level, format, size, num_questions, questions_json,
    status, score, passed, correct_count, learning_path_json,
    started_at, completed_at)
  - `charvak_career_assessment_answers` (answer_id PK, assessment_id,
    question_index, selected_index, is_correct, answer_text, ai_score,
    ai_feedback, answered_at, UNIQUE(assessment_id, question_index))
- 6 routes under `/api/career-assessment/*`
- `/ai-assessment` now renders `templates/ai-assessment.html`
  (was rendering `ai-bridge.html` - the URL/content mismatch flagged
  in Session 9)

### Phase 2a (Session 11, 7 more formats)

- 8 total formats: mcq, short_answer, numeracy, situational_judgment,
  behavioral, system_design, debugging, case_study
- 2 more (coding, sql) are shown but disabled - they need a real
  execution sandbox (Judge0/Piston), planned for Session 14
- Per-format prompt builders, normalizers, and scoring:
  - Deterministic: mcq, numeracy, SJT, short_answer (keyword match)
  - AI batch-scored: behavioral, system_design, debugging, case_study
- AI batch scoring: ONE OpenAI call handles all answers of one
  AI-scored format (~$0.005 per assessment)
- Credit keys (2 sets):
  - Deterministic: `career_assessment_quick: 15`, `_standard: 25`,
    `_full: 35`
  - AI-scored: `career_assessment_ai_quick: 20`, `_standard: 30`,
    `_full: 40`
- Frontend: format picker, per-format rendering (radio / textarea /
  number / best-worst pairs / code block), per-question breakdown

### Phase 3 (Session 13, adaptive + skill gap + learning paths)

- **Topic tagging**: 7 role categories x 8 topics each
  (`TOPIC_VOCABULARY`). AI tags every question with 1-2 topics from
  the vocabulary at generation time.
- **Skill gap**: `_aggregate_skill_gap(questions, scored)` groups by
  topic. Blended score = (binary_correct_pct + avg_ai_score_pct) / 2.
  Status: strong (>=80), mixed (55-79), weak (<55). Weakest-first.
- **Cross-assessment adaptive baseline**: `_baseline_hint(email, role,
  industry, fmt)` reads `ability_engine.get_ability`. Elo bands:
  <950 foundation-first, 950-1050 standard, >=1050 challenge. Injected
  into the prompt via `_context_header` ADAPTIVE HINT block.
  Response includes `baseline_used` / `ability_before` / `prior_attempts`.
- **Ability update on complete**: `results_system.record_assessment_result`
  with `skill=f"career_{fmt}"` triggers the internal
  `ability_engine.update_from_assessment` call. First real use of
  ability_engine since Session C4.
- **AI-generated learning path**: lazy + cached in
  `learning_path_json`. `_ai_generate_learning_path` matches
  `charvak_courses` from the 25-course catalog, curates external
  resources, generates a 2-4 week plan.

### Route: learning path

- `GET /api/career-assessment/learning-path/{assessment_id}` - auth,
  free (bonus value; no credits charged). Cached after first generation.

### Scope boundaries (Phase 3 deliberately does NOT include)

- Retake comparison charts
- Certificates / badges (Phase 4)
- Live mid-assessment adaptation (deferred indefinitely)
- Peer benchmarking (Phase 4)

### Still pending (Session 14)

- Phase 2b: coding + SQL via Judge0 sandbox
- Difficulty-aware ability update (pass `difficulty=` to
  `ability_engine.update_from_assessment` based on `level_key`)
- Catalog coverage for niche roles (no frontend System Design course
  exists in `charvak_courses`)

### Reference

Full plan in `CAREER-ASSESSMENT-PLAN.md`.

---

## File Naming Conventions

### Python modules

- `*_engine.py` - feature module with business logic
  - Notables: `career_assessment_engine.py`, `products_engine.py`,
    `ai_credit_engine.py`, `indian_language_ai.py`, `payment_engine.py`
- `*_service.py` - supporting service (job, monitor)
- `*_manager.py` - CRUD manager
- `main.py` - FastAPI app (~10,000 lines; all routes)
- `auth.py` - registration, login, tokens
- `database.py` - DB connection + user CRUD
- `ability_engine.py` - Elo-based adaptive difficulty (career assessment)
- `results_system.py` - cross-product results feed (feeds `/my-results`)

### Templates

- `templates/*.html` - page templates
- `templates/includes/*.html` - reusable components
- `templates/tools/*.html` - AI tool pages

### Scripts and migrations

- `scripts/*.py` - dev/ops scripts (not imported by `main.py`)
- `migrations/*.sql` - idempotent SQL migrations

---

## Environment Variables (production, Render)

Required on Render and in local `.env`:

| Var | Purpose |
|---|---|
| `DATABASE_URL` | Render Postgres internal URL |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | Razorpay live credentials |
| `RAZORPAY_WEBHOOK_SECRET` | HMAC for `/webhook/razorpay` |
| `PAYPAL_CLIENT_ID` / `PAYPAL_CLIENT_SECRET` | PayPal live credentials |
| `PAYPAL_WEBHOOK_ID` | Signature verification for `/webhook/paypal` |
| `PAYPAL_MODE` | `live` (default) or `sandbox`. Added Session 9; defaults to `live` when unset |
| `SENDGRID_API_KEY` | Transactional email |
| `OPENAI_API_KEY` | All AI features |
| `ELEVENLABS_API_KEY` | Voice features (Versant, TTS) |
| `SECRET_KEY` | Session/CSRF, 64 chars |
| `SITE_URL` | `https://www.charvakit.com` |
| `ADMIN_EMAIL` / `HR_EMAIL` | Admin account emails |

### Dev overrides (added Session 9)

- `/api/region?country=US` - force region for a request
  (e.g. to test PayPal on a local dev machine with an India IP)
- `/api/region?currency=USD` - force currency only
- Frontend `currency-utils.js` reads `?country=` from the page URL and
  passes it through, so `http://localhost:8000/ai-credits-pricing?country=US`
  works end-to-end

### Sandbox testing note

To test the PayPal flow locally without real money:
1. Set `PAYPAL_MODE=sandbox` in `.env`
2. Set `PAYPAL_CLIENT_ID` + `PAYPAL_CLIENT_SECRET` to a sandbox app's
   credentials (US merchant recommended for USD transactions)
3. Log in with a sandbox buyer account at
   `https://www.sandbox.paypal.com`
4. Prod is unaffected: Render has its own env vars; the local `.env`
   is gitignored

---

Keep in sync with MASTER-REFERENCE.md.

## Client Staffing Pipeline (Session 22, v3.5)

Public-facing candidate pipeline for CBREX-mediated client roles.

### Data flow

    Client email / admin input
        |
        v
    charvak_client_roles (ROLE-xxxx)
        |
        +-- charvak_role_screening_questions (QST-xxxx, per role)
        |
        v
    Candidate -> /open-roles -> /open-roles/{role_id}
        |
        v
    POST /api/staffing/roles/{role_id}/apply
        |
        +-- charvak_applications (APP-xxxx, status='applied')
        +-- charvak_role_screening_answers (7 rows per apply)
        +-- charvak_candidate_consents (in_app, IP + UA)
        |
        v
    If candidate row missing:
        POST /api/candidates/upsert (inline profile form)
        -> retry apply

### Public sanitization

Public API responses (`/api/staffing/open` and
`/api/staffing/roles/{id}`) null out client_name, client_type,
vendor_portal, vendor_role_ref, source, source_email_ref, and
created_by. Public label is always "via Charvak".

### Admin namespace

`/api/admin/client-roles/*` (6 routes, protected by
admin_auth_guard middleware + require_admin in route bodies).

### Engine

`client_staffing_engine.py`:
- create_role, list_roles, get_role, set_screening_questions
- apply_to_role, list_applications_for_role, update_submission_status

`candidates_engine.py`:
- get_me(email)
- upsert(data) -- whitelist-guarded, JSONB-coerces list-shaped fields

### Question types supported

text, multiline, yes_no, choice_single, choice_multi, number

### Fill source per question

candidate (default) or charvak (admin reviews/overrides)



## Admin UI for Client Staffing (Session 24, v3.5)

Two admin pages on top of the Session 22 backend endpoints.

### Routes

- `GET /admin/client-roles` - list page (protected by admin_auth_guard)
- `GET /admin/client-roles/{role_id}` - detail page

Both are protected by the `admin_auth_guard` middleware; no per-route
`require_admin` needed in the route body. The middleware redirects
unauthenticated page requests to `/admin-login`.

### Frontend patterns

- Templates: `templates/admin-client-roles.html`,
  `templates/admin-client-role-detail.html`
- Both extend `base.html` and use the `{% block modal %}` slot for
  any modals (to escape the `<main>` stacking context)
- Row actions use `data-action` + event delegation (no inline onclick
  with string concat, which breaks on PowerShell quote-stripping)
- Refresh buttons use inline `onclick="loadRoles()"` /
  `onclick="loadAll()"`; the functions are exposed via
  `window.loadRoles` / `window.loadAll` because the inline handler
  runs in global scope

### Data flow

List page:

    GET /admin/client-roles
      -> admin_client_roles_page (route)
      -> templates/admin-client-roles.html
      -> JS fetches /api/admin/client-roles (with Authorization header)
      -> renders table

Detail page:

    GET /admin/client-roles/{role_id}
      -> admin_client_role_detail_page (route)
      -> templates/admin-client-role-detail.html
      -> JS fetches /api/admin/client-roles/{role_id}
         AND /api/admin/client-roles/{role_id}/applications
      -> renders role info + applicant list

View modal:

      -> JS fetches /api/admin/applications/{app_id}/submission-package
      -> renders profile + screening answers

Download Package:

      -> JS fetches /api/admin/applications/{app_id}/submission-package.zip
      -> triggers browser download

### Jinja gotchas to remember

- Jinja parses template tags ANYWHERE - including in JS comments.
  Never write a template tag syntax inside a JS comment or string.
- Modals must live in the `{% block modal %}` slot so they render as
  direct children of `<body>`; otherwise they're trapped in `<main>`'s
  stacking context and appear faded/unclickable.
