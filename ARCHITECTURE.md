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

## Assessment Integrity Layer A (Session 27, v3.5)

Deterministic environment-signal capture on Career Assessments.
Recorded only, never enforced.

### Signal types

| Signal | Detects | Metadata |
|---|---|---|
| `paste` | User pasted into a text field | target_id, chars |
| `tab_switch` | User left the assessment tab | duration_ms |
| `contextmenu` | Right-click (paste via menu) | target_id |
| `focus_out` | Input lost focus mid-answer | target_id |
| `rapid_input` | Synthetic typing (100+ chars in <200ms) | chars, window_ms, chars_per_ms |

### Storage

- `charvak_assessment_integrity_events` — one row per event
- `charvak_career_assessments.integrity_summary` (JSONB) — per-assessment rollup

### Flow

    Browser (ai-assessment.html)
      -> document-level listeners (paste, contextmenu, visibilitychange,
         blur/focus, focusout, input)
      -> queued in memory
      -> flush every 2s via fetch (Authorization header)
      -> POST /api/integrity/event
      -> route verifies auth + ownership (assessment belongs to caller)
      -> integrity_engine.record_event(...)
      -> INSERT into events table
      -> update_parent_summary recomputes rollup + writes JSONB

    Admin (later session)
      -> GET /api/admin/career-assessment/{aid}/integrity
      -> returns events list + summary

### Risk levels

- `clean`: 0 events
- `minor`: 1-5 events
- `moderate`: 6-15 events
- `elevated`: >15 events OR (>=3 tab switches + >=2 pastes)

### Design principles

- Record only. Employers decide what to do with the signal.
- Silent-fail on the frontend: a dead backend never breaks the
  assessment.
- Self-healing DDL: no manual migration step for the tables.
- No credits charged: this is a trust feature, not a paid tool.

### Rollout

Layer A ships first on Career Assessment (this session). Versant,
Mock Drives, CBAT, and IELTS can adopt the same engine + route by
adding a small frontend block (the backend is engine-agnostic).

## Code Execution via Judge0 (Session 28, v3.5)

Coding format uses Judge0 CE for real code execution. Called from
`career_assessment_engine._score_coding_batch` at assessment completion.

### Endpoint

- Base URL: `https://ce.judge0.com` (free, no auth)
- Configurable via `JUDGE0_BASE_URL` env var (defaults to ce.judge0.com)
- Optional `JUDGE0_API_KEY` env var for RapidAPI-hosted migration
- Synchronous mode: `?base64_encoded=false&wait=true`

### Flow

    Career Assessment (format=coding)
      -> start_assessment
         -> _generate_questions -> _generate_one_batch -> OpenAI
         -> returns 10 problems with starter_code + 3 test cases
         -> _strip_answers_for_frontend removes test_cases
      -> candidate submits Python code
      -> submit_answer stores source_code as answer_text
      -> complete_assessment
         -> _dispatch_scoring -> _score_coding_batch
            -> judge0_client.run_test_cases(source, test_cases)
            -> per-case pass/fail
            -> score = passed/total*100

### Language map (ready for expansion)

- python=71 (live)
- javascript=63, java=62, cpp=54, go=60 (declared, unused)

### Cost

- ce.judge0.com is free (no auth, no rate limit for reasonable use)
- Each coding question costs 3 Judge0 submissions (one per test case)
- A 10-question quick assessment = ~30 Judge0 calls

### Design principles

- Never raises: judge0_client returns {status: 'error', ...} on any failure
- Timeouts: each submission has a 5s wall-time limit + 3s CPU limit
- Silent fail: a Judge0 outage gives the candidate a score of 0, not a 500
- Rate safety: no retries, no parallelism (sequential per question)

## Unified Candidate Profile (Session 30, v3.5)

Read-only aggregation layer that presents a candidate's activity
across all subsystems in one API call. First step of the
career-center unification arc.

### Why it exists

Charvak has 8+ candidate-related tables across different engines
(assessments, certificates, applications, staffing, micro-internships,
career engine, integrity, credits). A user navigating the site
had no single place to see their full activity. The unified profile
solves that without merging any of the underlying engines.

### Endpoint

    GET /api/candidate/{email}/unified
    GET /api/candidate/{email}/unified?include=assessments,certificates

- Auth: caller must own the email
- Rate limit: 60/min
- include filter validates against ALL_SECTIONS whitelist
- Returns 10 sections:
    identity, profile, assessments, certificates, applications,
    training, career_engine, integrity, credits, doketsrb

### Engine

`candidate_profile_engine.py` — read-only. One method:
`get_unified_profile(email, include=None) -> dict`

Each section:
- Runs its own query on its own DB connection
- Wrapped in `_safe_section` so a failure never breaks the response
- Aggregates large tables (integrity events) and enumerates small ones

### Design principles

- **Read-only.** No writes, no schema changes.
- **Section-isolated.** One failure does not affect other sections.
- **Stable shape.** Empty tables still return their section with an
  empty list/structure so the frontend can render consistently.
- **Self-view only.** No admin variant in Session 30. The admin
  variant is a separate concern.
- **One call = one screen.** The response shape is designed to render
  a dashboard in a single fetch.

### Frontend

`templates/career-v2.html` — a "Your activity" panel at the top of
`/career-center`. Fetches the endpoint on page load; renders 4 stat
cards + recent assessments. Hidden entirely when logged out. Silent-fail.

### Long-term arc

This is the "read" side of the unification. Future sessions:
- Unified jobs feed (read across job-board + staffing + micro-projects)
- Unified candidate signup (write once, land in the right table)
- Assessment-to-course loop (close the Assess -> Upskill cycle)

The underlying engines stay separate. The unified layer is a thin
read-side presentation.

## Unified Jobs Feed (Session 31, v3.5)

Read-only aggregation of three job sources into one public feed.
Second step of the career-center unification arc.

### Sources

| Source | Table | Public route |
|---|---|---|
| Job board | charvak_jobs | /job-board |
| Staffing | charvak_client_roles | /open-roles |
| Gigs | charvak_micro_projects | /micro-internship |

### Endpoint

    GET /api/jobs/unified
    GET /api/jobs/unified?source=staffing,gig
    GET /api/jobs/unified?q=engineer&limit=50

Public, rate-limited 120/min. No auth required.

### Normalized shape

    {
      "id": "ROLE-XXX" | "JOB-XXX" | "PROJ-XXX",
      "source": "staffing" | "job_board" | "micro_project",
      "source_label": "via Charvak" | "Job Board" | "Gig",
      "title": "...",
      "company": "..." or "via Charvak",
      "location": "...",
      "type": "permanent" | "contract" | "gig",
      "skills": ["..."],
      "experience": {"min_years": N, "max_years": M} or null,
      "compensation_display": "Rs.25L - Rs.30L" or null,
      "compensation_min_inr": N or null,
      "compensation_max_inr": M or null,
      "posted_at": "ISO 8601",
      "detail_url": "/open-roles/..." | "/job-board/..." | "/micro-internship/..."
    }

### Sanitization by construction

Staffing items never carry: client_name, client_type, vendor_portal,
vendor_role_ref, source, source_email_ref, created_by, budget fields.
Matches the /api/staffing/open contract from Session 22. The unified
shape simply doesn't have those fields - they cannot leak.

### Frontend

- /career-center/jobs renders the feed with filters + search
- /career-center panel header has a "View all openings" link

### Future extensions

- ?type=permanent,gig filter
- ?min_compensation=N filter
- Location filter
- Saved-searches tied to charvak_career_job_alerts

## Unified Candidate Signup (Session 32, v3.5)

Write-side unification of the career-center arc. One signup entry
point, one write path, one profile editor.

### The single write path

All candidate writes go through candidates_engine.upsert():
  - /api/candidates/upsert         (canonical)
  - /api/candidate/register        (legacy alias, delegates)
  - /profile edit form             (calls /api/candidates/upsert)
  - Inline profile form on /open-roles (same)

No more parallel INSERTs. Field whitelist (37 fields) applies to every
write. signup_source tags the origin:

  "candidate-signup"  -- via /candidate/signup (public entry)
  "developer-signup"  -- legacy /developer-signup (now redirects)
  "open-roles-inline" -- via the inline profile form on a role page
  "profile-edit"      -- via /profile (canonical editor)
  "pool-register"     -- via legacy /api/candidate/register

### The signup gate

/candidate/signup is now a marketing page with two states:
  - Anonymous: shows "Create account ->" CTA
  - Authenticated: JS redirects to /profile (single write surface)

### Route consolidation

  /candidate-signup -> 302 -> /candidate/signup
  /developer-signup -> 302 -> /candidate/signup

Both legacy URLs preserved for external links and SEO.

### The profile editor

/profile is the canonical write surface. Fields:
  identity, professional, education, links, preferences
  (16 user-editable fields)

Prefills from candidates_engine.get_me() on load.
Writes via /api/candidates/upsert with signup_source="profile-edit".

### Design principles

- One write path. No parallel INSERTs.
- Field whitelist enforced at the engine boundary.
- Self-healing schema (signup_source column added on first use).
- Read/write symmetry: get_me returns every field that can be written.
- Legacy endpoints delegate - they never bypass the unified engine.

## Assess -> Upskill Loop (Session 33, v3.5)

Closes the loop from Career Assessment result to course enrollment.
Fourth and final step of the career-center unification arc.

### What it does

When a candidate completes a Career Assessment and requests their
personalized learning path, each recommended course card now shows:
  - The course name
  - A "Fills: [weak topic]" badge
  - The AI-generated reason
  - A "Start course ->" button

Clicking the button deep-links to /course/{canonical_name}, where the
existing enrollment flow (tier selection, EMI schedule, payment) runs.

### The fills_topic mapping

The AI prompt for _ai_generate_learning_path now requests a
`fills_topic` field on each `charvak_courses` entry:

    {"course_id": "...", "course_name": "...",
     "fills_topic": "<weak topic verbatim from WEAK/MIXED list>",
     "reason": "why this course addresses that topic"}

The rule: fills_topic MUST be copied verbatim from the weak topic
list, so the badge always maps back to an actual gap in the skill
gap analysis.

A defensive normalize in the sanitizer ensures fills_topic always
exists (defaults to '') so the frontend never breaks on old cached
learning paths.

### Caching

learning_path_json is lazy-generated and cached in
charvak_career_assessments. Paths generated before Session 33 have
no fills_topic; new paths do. No migration needed - the field is
optional and the renderer handles both cases.

### Design principles

- Read-only on the assessment side; write-only on the enrollment side.
- The AI's job: map each course to the specific weak topic it fixes.
- The candidate's job: click Start course.
- One click from "here's your gap" to "here's the fix."

### The full Local-to-Global journey (arc complete)

    Assess -> Prove -> Upskill -> Match -> Place
    [Career   [Readiness [AI     [Jobs    [Career
     Assess]   Cert]     Courses] Feed]    Center]

Unification arc sessions:
- 30: unified candidate profile (read view)
- 31: unified jobs feed (read view)
- 32: unified candidate signup (write path)
- 33: Assess -> Upskill loop (this session)

## AI Course Designer (Session 34, v3.5)

Closes the last dead-end in the Local-to-Global journey. When a
candidate's learning path recommends a topic with no catalog match,
the AI designs a full course on demand.

### The flow

    Career Assessment (weak topic)
      -> Learning Path generated
      -> "Custom Courses for Your Gaps" section
      -> card: "Tooling & Ecosystem  weak 0%"
              "Design this course - 50 cr"
      -> click
      -> AI generates 6-week course
         (adaptive: weak -> 6, mixed -> 4, strong -> 3)
      -> green card: "Course generated for 50 credits"
                     [Review course ->]  [My Courses]
      -> click Review course
      -> /course/{name}  (curriculum + free Enroll Now)
      -> click Enroll Now
      -> POST /api/ai-course/create-order
      -> returns {status:'exists', free:true, enrollment_id}
      -> /my-course/{enrollment_id}  (lesson player)

### Backend changes

- /api/ai-course/generate-custom: no longer auto-enrolls.
  Returns course info so the frontend can present the review step.
- /api/ai-course/create-order: free (Rs 0) courses bypass the
  gateway entirely. Returns the shape the frontend already handles
  for existing enrollments.
- Both idempotent paths (existing custom course, existing enrollment)
  return the same shape without charging credits.

### Frontend changes

- generateCustomCourse(): now takes candStatus, computes weeks from
  the candidate's gap severity.
- Confirmation card CTA: "Start Learning" -> "Review course" pointing
  at /course/{name} (not /my-course/{id}). The candidate sees the
  curriculum before enrolling.
- course-detail.html: login hint is dynamic (shows email when signed
  in, "Login required" when not).

### Cost model

- AI course design: 50 credits (custom_course_generation)
- Enrollment after generation: free (Rs 0 to the candidate)

The candidate pays once for the design; everything after is free.

### Zero dead ends principle

This is the completion of the Local-to-Global journey arc. No weak
topic is a dead end now - if a catalog course matches, the candidate
enrolls in it; if not, the AI designs one.

    Assess -> Prove -> Upskill -> Match -> Place
    [all five stages connected, zero dead ends]

## Two-Tier AI Course Unlock (Session 36, v3.5)

Restructures AI-designed courses into a freemium product. Design is
50 credits; Weeks 1-2 are free to consume; 150 credits unlock the
full course, the verified certificate, and AI tutor access.

### The pricing model

    Design     50 cr   AI generates the curriculum
    Preview    0 cr    Weeks 1-2 free to consume
    Unlock     150 cr  Weeks 3+ + certificate + AI tutor

    Total committed: 200 cr
    Total curious:   50 cr

### The gate (three layers)

Custom courses (is_custom = TRUE) gate on `charvak_enrollments.paid_unlock`:

1. Access   - check_course_access returns allowed=False for weeks 3+
2. Content  - /lesson/ and /content/ both call check_course_access
3. Certificate - complete_course refuses to issue unless paid_unlock=TRUE

The custom-course check runs BEFORE the installment lookup in
check_course_access because custom courses may have stray installment
rows from the enrollment path, and those should not be treated as real EMIs.

### The unlock flow

    User clicks Week 3
      -> check_course_access returns {allowed: false, unlock_type: 'full_course'}
      -> frontend showPaywall routes to #unlockCard
      -> user confirms (window.confirm - 150 credits is meaningful)
      -> POST /api/ai-course/unlock-full
      -> require_credits_from_data(data, 'ai_course_full_unlock')
      -> ai_courses.unlock_full_course() flips paid_unlock to TRUE
      -> page reloads, all weeks unlocked

Idempotent: a second unlock call returns already_unlocked=True without
charging again.

### Grandfather

New column: charvak_enrollments.paid_unlock BOOLEAN DEFAULT FALSE

On first run, all NULL rows flip to TRUE (one-time, self-limiting).
This ensures existing users keep full access. Subsequent runs match
zero rows.

### Credit key

ai_course_full_unlock: 150

### Files touched

- ai_courses.py         (unlock_full_course, check_unlock_status, gates)
- ai_courses_payments.py (check_access gate)
- ai_credit_engine.py   (credit key)
- main.py               (unlock-full route, lesson + content gates)
- templates/my-course.html       (#unlockCard + unlockFullCourse + completeWeek)
- templates/course-detail.html   (Start free + Unlock buttons)
- templates/ai-assessment.html   (two-tier messaging)

### Market alignment

Matches freemium course-builder pricing:
- Criterium: free tier -> €39/mo
- Oboe: free tier -> $12/mo
- Honen: subscription
- Chat2course: free tier -> ~$10/mo

Charvak's version is assessment-driven (from the skill gap) rather than
generic. That's the differentiated piece: the AI designs for YOUR gap,
not a generic topic.

## Career Engine Trio (Session 37, v3.5)

Four surfaces form the Career journey. Each has a distinct purpose.
All cross-link.

### The four surfaces

| URL | Template | Purpose | Data source |
|---|---|---|---|
| /career-engine | career-engine.html | Marketing narrative - "7 Steps" | Static |
| /career-center | career-v2.html | Logged-in dashboard | /api/candidate/{email}/unified |
| /career-center/jobs | career-jobs.html | Unified jobs feed (inside center) | /api/jobs/unified |
| /job-board | job-board.html | Public job board | /api/jobs/unified |
| /training-engine | training-engine.html | Public course catalog | /api/ai-course/catalog |

### The unified feed (Sessions 31, 37)

/api/jobs/unified merges three sources into one public feed:

  charvak_jobs           (public job board - currently empty)
  charvak_client_roles   (staffing pipeline - 7 live roles)
  charvak_micro_projects (gigs - 1 live project)

Consumed by both /job-board and /career-center/jobs.

### The training catalog (Sessions 16, 34, 36, 37)

/api/ai-course/catalog returns all active courses from
charvak_courses. 31 real courses across 6 categories (Cloud,
Custom, Data, Design, Security, Technology).

Custom courses (is_custom=TRUE) are AI-designed per user per weak
topic. They show "Free after design" in the catalog UI.

Consumed by /training-engine (Session 37 wiring) and by the
individual /course/{name} detail pages.

### Cross-links

    career-engine  ->  career-center (dashboard CTA + journey link)
    career-center  ->  career-engine (See the 7-step journey)
    career-engine  ->  job-board (Step 2 card)
    career-engine  ->  training-engine (Step 5 card)
    job-board      ->  career-center (My Career Center)
    job-board      ->  training-engine (Explore Training)
    training-engine ->  career-center (My Career Center)
    training-engine ->  career-engine (See the 7-Step Journey)

### Nav consolidation (Session 37)

The top nav's Services dropdown and the footer now expose:

    Career Engine      ->  /career-engine  (narrative)
    My Career Center   ->  /career-center  (dashboard)
    Job Board          ->  /job-board      (public)
    Training Engine    ->  /training-engine (courses)

### Session 37 flagged for future work

- Job posting as first-class feature (Session 38+)
- Personalized training views (Session 38+, needs readiness cert data)
- DoketsRB bidirectional sync (Session 38+, see COMMITMENT.md)

## Partial-Credit Handling Across the Trust Pipeline

Every assessment that can be submitted incomplete now carries an
honest partial flag. The pattern differs by scoring type:

**Deterministic scoring (reading, listening):**
- `partial = answered_count < total_count`
- `answered_count` and `partial` returned in the response
- Persisted in `details_json`
- Frontend yellow banner

**AI-scored (Versant, IELTS writing, IELTS speaking):**
- Versant: `partial = answered_count < 48`; the AI prompt is told
  the answered count and returns a `confidence` field
- IELTS writing: `partial = word_count < min_words`; min_words is
  150 for Task 1 and 250 for Task 2
- IELTS speaking: `partial = not (parts 1 and 2 and 3 present)`;
  `parts_covered` and `part_counts` returned
- All three persist the flag + supporting counts in `details_json`
- All three render a yellow banner on the result screen

**Coverage (as of Session 40c):**

| Assessment | Type | Partial handling |
|---|---|---|
| Career | deterministic | n/a (no partial state) |
| Mock | deterministic | n/a |
| CBAT | deterministic | n/a |
| Versant | AI-scored | yes |
| IELTS Reading | deterministic | yes |
| IELTS Listening | deterministic | yes |
| IELTS Writing | AI-scored | yes (Session 40c) |
| IELTS Speaking | AI-scored | yes (Session 40c) |

**Known gap (logged in KNOWN-ISSUES.md):** the AI scoring prompts
for writing and speaking do not yet enforce topical relevance. An
off-topic submission can still score points, and an on-topic partial
submission can score 0. Fix is scheduled as its own session.

## Topical-Relevance Scoring (Session 41)

Alongside partial-credit handling, IELTS writing and speaking now
carry a topical-relevance signal.

**Engine (ielts_engine.py):**
- `evaluate_writing` and `evaluate_speaking` prompts instruct
  the AI to verify the response addresses the prompt. Off-topic
  responses cap Task Achievement / Task Response (writing) or all
  sub-bands (speaking) at 3.0, and return:
    - `topical_relevance`: true | false | None
    - `relevance_note`: one-sentence explanation
- `_topical_overlap(prompt, response)` - keyword-overlap sanity
  helper, 0.0-1.0. LOG-ONLY. When overlap < 0.05 and the response
  is > 30 words, a warning is logged alongside the AI's own
  judgment. Never overrides the score.

**Frontend:**
- Red "Off-topic response" banner above the yellow partial banner,
  shown when `topical_relevance === false`. Message is the AI's
  `relevance_note`.

**Coverage:**
- Writing: yes (Session 41)
- Speaking: yes (Session 41)
- Reading / Listening: n/a (deterministic scoring)
- Versant / Career / Mock / CBAT: n/a (no off-topic category)

**Regression net:**
- scripts/test_ielts_relevance.py - 6 canned cases, 14 checks.
  Invoked manually after prompt changes. Cheap (~\.03).

## Campus Placement Funnel (Session 42-3/4/5)

A complete public-facing funnel for the Nov-Dec campus placement season.

### Public pages

- /placement-prep-2026 - landing page. 18 companies in 3 sections
  (IT services, consulting, product). Each card links to
  /mock-drive?company=<id>. Includes 3-step explainer, trust strip,
  5-item FAQ, sitemap entry, meta + OG tags.
- /mock-drive - the mock-drive engine. Reads ?company=<id> on
  load and auto-selects the card. Login-gated with an inline card that
  preserves the current URL as ?next=.
- /mock-result/{session_id} - public shareable result page. Reads
  /api/mock/result/{session_id}. Shows score + verdict + sections
  + share buttons + a "What next?" block linking to the readiness
  check (role-mapped), AI courses, and the placement-prep page.
- /ai-courses - course catalog with an AI Course Designer card.
  Design 50 credits via /api/ai-course/generate-custom.

### New API routes

- GET /api/mock/result/{session_id} - public read of a completed mock session
- GET /api/ai-course/custom-list?email=X - auth-gated list of the
  user's own custom courses

### The ?next= auth pattern

Every public page that requires login for part of its flow redirects
to /login?next=<current-path>. Both login.html and register.html now
honor this parameter with same-origin sanitization (must start with
"/", reject "//evil.com"). The Register link on login.html carries
?next= through.

This pattern was already used by the readiness check and the mock-drive
login gate; the bug fix in Session 42-5 made it actually work.

### Company -> role mapping

The mock-result page deep-links to /readiness-check?role=<role>.
The mapping (in mock-result.html) is:

- Software Engineer: TCS, Infosys, Wipro, Cognizant, HCLTech, HCL,
  Tech Mahindra, LTI, Mindtree, Capgemini, IBM, Amazon, Google, Microsoft
- Business Analyst: Deloitte, KPMG, EY, PwC
- Technology Analyst: Accenture

The readiness check's own ?role= handling pre-selects the dropdown
after page load.
