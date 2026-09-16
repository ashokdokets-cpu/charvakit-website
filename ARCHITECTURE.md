# Charvak Architecture

**Last updated:** 2026-09-17
**Version:** v2.2-mock-drives-20260917

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
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

app.mount("/static", CachedStaticFiles(directory="static"), name="static")
Script loading strategy
Razorpay, PayPal, Chart.js, Bootstrap JS → all defer (loads after DOM parse, no render-block)

Google Fonts → <link> with preconnect (not @import)

Fonts cached for 1 year

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

File Naming Conventions
*_engine.py - feature module with business logic

*_service.py - supporting service (job, monitor)

*_manager.py - CRUD manager

templates/*.html - page templates

templates/includes/*.html - reusable components

templates/tools/*.html - AI tool pages

scripts/*.py - dev/ops scripts (not imported by main.py)

migrations/*.sql - idempotent SQL migrations

Keep in sync with MASTER-REFERENCE.md.
