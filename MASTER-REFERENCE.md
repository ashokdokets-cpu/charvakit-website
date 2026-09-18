# CHARVAKIT.COM - MASTER REFERENCE
## Charvak IT Consulting Pvt Ltd
### Last updated: September 18, 2026 (after Session H)

**Live:** https://www.charvakit.com
**Version:** v2.8-persistence-A-C-D-E-F-G-H-20260918

---

## SYSTEM OVERVIEW

- Engines: 32+
- Templates: 203
- APIs: 180+
- Languages: 34 global + 12 Indian
- Visa Types: 17
- Security: 7 layers
- Payments: LIVE (Razorpay INR + international, PayPal multi-currency)
- AI Credits: DB-backed, persisted (Fix B - 2026-09-12)
- Course Payments + India EMI: LIVE (2026-09-16)
- Tiered Pricing (Basic/Intermediate/Advanced): LIVE (2026-09-16)
- Mock Drives: DB-backed (2026-09-17)
- Webhook safety net: LIVE (Razorpay + PayPal)

---

## COMPANY

- **Location:** #301, Sri Padmavati Towers, 3rd Lane, Seetaram Nagar, Guntur 522001, Andhra Pradesh, India
- **Email:** hr@charvakit.com
- **Phone:** +91 799 7871 701

**Two products share one Render Postgres database:**
1. **Charvak** (this project) - AI tools, exams, credits, career engine
2. **Dokets VouchAI** - AI escrow platform (dokets.com)

---

## INFRASTRUCTURE

| Service | Identifier | Notes |
|---|---|---|
| Render (Charvak) | `srv-d9hhljd8nd3s73d2hoeg` | Python 3.11.9, Singapore |
| Render (VouchAI) | `srv-d9nque942hec7386q3mg` | Node, Singapore |
| Render Cron | `send-emi-reminders` | Daily 9:00 AM IST - EMI reminder emails |
| Render Postgres | `dpg-d9m92j0ae00c73blvoq0-a` | DB: `vouchai` (shared) |
| GitHub | `ashokdokets-cpu/charvakit-website` | main branch |
| Cloudflare | www.charvakit.com | CDN + DNS |
| Razorpay | LIVE | INR + International payments + webhook |
| PayPal | LIVE | Multi-currency |
| SendGrid | LIVE | Transactional email |
| OpenAI | GPT-4o-mini | AI features |
| ElevenLabs | LIVE | Voice features |

### Local dev

- Postgres 15 installed at `C:\Program Files\PostgreSQL\15`
- Service: `postgresql-x64-15` (Automatic start)
- DB: `vouchai` at `postgresql://postgres:dev@localhost:5432/vouchai`
- `.env.local` present, not committed
- See `DEV-SETUP.md`

### Render env vars
DATABASE_URL (Render Postgres internal URL)
RAZORPAY_KEY_ID (rzp_live_...)
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET (Fix C)
PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET
SENDGRID_API_KEY
OPENAI_API_KEY
ELEVENLABS_API_KEY
SECRET_KEY (64 chars)
SITE_URL (https://www.charvakit.com)
ADMIN_EMAIL (charvakit@gmail.com)
HR_EMAIL (hr@charvakit.com)

text

---

## TECH STACK

| Layer | Technology |
|---|---|
| Backend | Python 3.11.9 + FastAPI + Uvicorn |
| Templates | Jinja2 (203) |
| Database | PostgreSQL via psycopg2 |
| Frontend | Bootstrap 5, vanilla JS, Chart.js |
| Hosting | Render (Singapore) |
| CDN | Cloudflare |
| CI/CD | GitHub push -> Render auto-deploy |

---

## ENGINES (32+)

Core: payment, kyc, escrow, referral, badge, blog, chatbot, sso,
micro_internship, training, interview_prep, job_board,
products, candidate, email, messaging, events, brand, team,
ats, university, enterprise, invoice, tools,
marketing_ai, indian_language_ai, lms, career_v2

Data-backed: `ai_credit_engine`, `email_verification`, `ai_courses`, `ai_courses_payments`, `complete_mock_drive`, `results_system`

---

## FEATURES

- 16 AI Products + 12 AI Tools
- NA Module (17 visas, 6 files)
- Career Center (alerts, saved jobs, interviews, offers)
- LMS (ratings, quizzes, certificates, lessons, payouts)
- Marketing AI (job ads, social posts)
- Indian Language AI (12 languages)
- Enterprise (Teams, ATS, University, Enterprise)
- AI Credits (purchase, daily bonus, usage history - persisted)
- Exam Prep (122 exams, Indian + global)
- **AI Courses** (catalog, lessons, certificates - persisted)
- **AI Course Fee + India EMI + Global Pricing** (v2.0)
- **Tiered Pricing** (Basic/Intermediate/Advanced - v2.1)
- **Company Mock Drives** (18 companies, AI-generated, persisted - v2.2)

---

## DATABASE SCHEMA

### Charvak-owned tables

| Table | Purpose |
|---|---|
| `users` | email, password_hash, name, phone, role |
| `email_verification_tokens` | token, email, expires_at, verified |
| `password_reset_tokens` | reset flow |
| `contacts` | contact form submissions |
| `charvak_user_credits` | email PK, plan, credits_remaining, daily_usage (JSONB), expires_at |
| `charvak_credit_usage_history` | every deduction |
| `charvak_credit_purchases` | purchase log; `payment_id` UNIQUE for idempotency |
| `charvak_courses` | 25-course catalog, price_inr source of truth |
| `charvak_enrollments` | enrollment state, user_level (beginner/intermediate/advanced) |
| `charvak_course_lessons` | weekly lessons (JSONB content) |
| `charvak_certificates` | issued certificates with recipient name |
| `charvak_course_prices` | 175 rows (25 courses x 7 Tier-1 markets) |
| `charvak_course_payments` | per-payment log; `razorpay_payment_id` UNIQUE |
| `charvak_course_installments` | India EMI schedule (milestone-block model) |
| `charvak_course_levels` | 75 rows (25 courses x 3 levels) |
| `charvak_mock_sessions` | one row per started company mock drive |
| `charvak_mock_answers` | one row per answered question |
| `charvak_assessment_results` | every assessment result |
| `charvak_interview_sessions` | Interview prep sessions |
| `charvak_interview_answers` | Interview prep answers |
| `charvak_referrals` | referral codes + referrer info |
| `charvak_referral_clicks` | click tracking |
| `charvak_referral_bounties` | bounty payments |
| `charvak_jobs` | job board postings |
| `charvak_applications` | job applications |
| `charvak_skill_gaps` | skill gap analysis |
| `charvak_synced_users` | Dokets RB sync |
| `charvak_synced_applications` | Dokets RB sync |

### VouchAI-owned tables (shared DB, do not touch)

`Contract`, `Dispute`, `Milestone`, `Payment`, `User`, `UserAchievement`

---

## API ENDPOINTS (key)

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login` - email verification check + admin bypass
- `POST /api/auth/logout`, `/api/auth/logout-all`
- `GET /api/auth/me`

### Credits
- `GET /api/credits/plans`
- `GET /api/credits/{email}`
- `POST /api/credits/check`
- `POST /api/credits/purchase`
- `POST /api/credits/daily-bonus`
- `GET /api/credits/expiry/{email}`, `/api/credits/usage/{email}`
- `GET /api/credits/admin/stats`

### Payments
- `POST /api/payment/create-order`
- `POST /api/payment/verify`
- `GET /api/payment/history`
- `POST /webhook/razorpay`
- `POST /webhook/paypal`

### AI Courses
- `GET /api/ai-course/catalog`
- `GET /api/ai-course/course/{course_name}` - returns levels[]
- `GET /api/ai-course/price/{course_name}?level=X&country=YY`
- `POST /api/ai-course/enroll` - FREE path (price 0)
- `POST /api/ai-course/create-order`
- `POST /api/ai-course/confirm-payment`
- `GET /api/ai-course/installments/{enrollment_id}`
- `GET /api/ai-course/access/{enrollment_id}/{week_num}`
- `POST /api/ai-course/complete-week`
- `POST /api/ai-course/complete`
- `GET /api/ai-course/certificate/{certificate_id}`

### Company Mock Drives
- `GET /mock-drive` - page (v2.2)
- `GET /api/company-patterns/{company_id}`
- `POST /api/mock/start-complete`
- `POST /api/mock/submit-complete`
- `POST /api/mock/complete-full`

### Results
- `POST /api/results/record`
- `GET /api/results/user/{email}`
- `GET /api/results/readiness/{email}`

### Admin
- `/admin-login`, `/admin-control`
- All `/admin*` routes protected by middleware

---

## PAYMENT FLOW

### Credit purchase
User selects plan
-> POST /api/payment/create-order
-> Razorpay order created with notes: {plan, email, tool, amount_inr}
-> Client pays, calls /api/payment/verify + /api/credits/purchase
-> Webhook /webhook/razorpay idempotent fallback

text

### Course fee + EMI (v2.0)
Student picks level (beginner/intermediate/advanced)
-> GET /api/ai-course/price/{course}?level=X&country=YY

Student clicks Enroll
-> POST /api/ai-course/create-order
India: charges first installment only
Global: charges full price

-> POST /api/ai-course/confirm-payment
Verifies, fetches gateway, records, unlocks block

-> Webhook branches on notes.tool == "ai_course"

text

### EMI milestone-block model (India only)
- 2 blocks up to 8 weeks, 3 blocks for longer
- Each paid installment unlocks its block
- Locked weeks show "Pay to Unlock" card
- 24h-throttled in-context reminder email

### Reminder emails
- Render Cron `send-emi-reminders` daily 9 AM IST
- Stages: T-3d, due-date, +1d, +3d, +7d
- Dedupe via `last_reminder_stage`

**Idempotency:** `payment_id` UNIQUE on purchases + course_payments

---

## ADMIN ACCOUNTS

| Email | Role |
|---|---|
| charvakit@gmail.com | Admin |
| hr@charvakit.com | Admin |

**Rotate password:** `python scripts/rotate_admin_password.py`

---

## PROJECT STRUCTURE
charvakit-new/
├── main.py # FastAPI app (~5900 lines)
├── auth.py # Register, login, tokens
├── database.py # DB connection + user CRUD
├── payment_engine.py # Razorpay + PayPal + webhook sig verify
├── ai_credit_engine.py # DB-backed credits
├── ai_courses.py # AI courses + certificates
├── ai_courses_payments.py # Course payments + India EMI (NEW v2.0)
├── complete_mock_drive.py # Company mock drives (DB-backed v2.2)
├── results_system.py # Assessment results (DB-backed v2.2)
├── notification_engine.py # Email notifications + EMI reminders
├── email_verification.py # DB-backed verification
├── password_reset.py
├── email_engine.py # SendGrid
├── [40+ other engines]
├── templates/ # 203 Jinja2 pages
├── static/ # css, js, images, fonts
├── na_module/ # North America modules
├── migrations/ # SQL migrations (idempotent)
├── scripts/ # Dev/ops scripts
├── requirements.txt, runtime.txt
├── .env # Never committed
├── STATUS.md
├── MASTER-REFERENCE.md # <- this file
├── ARCHITECTURE.md
├── TIER3-MASTER-PLAN.md
├── PAGES-INVENTORY.md

text

---

## OPERATING COMMANDS

```powershell
# Local dev
uvicorn main:app --reload --port 8000

# Backup
python scripts/full_backup.py

# Rotate admin password
python scripts/rotate_admin_password.py

# Send EMI reminders manually
python scripts/send_emi_reminders.py

# Tag a stable release
git tag -a "vX.Y-stable-YYYYMMDD" -m "description"
git push --tags
BACKUPS
Latest: Charvak_Complete_Backup_20260917_012029.zip (6.39 MB, 1,014 entries)

Includes source, templates, static, migrations, scripts, .env, .git/, _DB_DUMP/ (24 tables), docs.

Security note: backup ZIPs contain .env secrets - do not share publicly.

KNOWN ISSUES / TODO

See KNOWN-ISSUES.md for the full list.

- [ ] Rotate PayPal client secret (deferred)
- [ ] Fix heading order on remaining pages (accessibility)
- [ ] TBT ~1,900ms mobile - needs conditional script loading
- [ ] Session 5C (mock engine consolidation) queued
- [ ] Backfill missing migrations/20260916_charvak_enrollments.sql
- [ ] Fix 20260916_course_payments.sql FK ordering
- [ ] Persist remaining 24 engines (Sessions B, D, F, H + Tier E verify)
- [ ] Exam prep frontend mock-test UI (backend + routes are live)
- [ ] Analytics Dashboards audit

EXTERNAL DASHBOARDS
Render: https://dashboard.render.com

GitHub: https://github.com/ashokdokets-cpu/charvakit-website

Razorpay: https://dashboard.razorpay.com

SendGrid: https://app.sendgrid.com

OpenAI: https://platform.openai.com

Cloudflare: https://dash.cloudflare.com

Keep this file updated after major changes.

text

---

## Step 3 — After saving, verify

```powershell
Set-Location "C:\Users\lenovo\OneDrive\Desktop\charvakit-new"

$bytes = [System.IO.File]::ReadAllBytes("MASTER-REFERENCE.md")
Write-Host "Size: $($bytes.Length) bytes"
Write-Host "Lines: $((Get-Content MASTER-REFERENCE.md).Count)"
Write-Host "First 3 bytes: $($bytes[0]) $($bytes[1]) $($bytes[2])"

Write-Host "`nFirst 5 lines (UTF-8 aware):" -ForegroundColor Cyan
$lines = [System.IO.File]::ReadAllLines("MASTER-REFERENCE.md", [System.Text.Encoding]::UTF8)
for ($i = 0; $i -lt 5; $i++) {
    Write-Host ("{0,4}: {1}" -f ($i+1), $lines[$i])
}

Write-Host "`nMarkers:" -ForegroundColor Cyan
@("v2.2-mock-drives-20260917","charvak_course_levels","AI Course Fee") | ForEach-Object {
    $found = $false
    foreach ($l in $lines) { if ($l -match [regex]::Escape($_)) { $found = $true; break } }
    Write-Host ("  {0,-40} {1}" -f $_, $(if ($found) { 'OK' } else { 'MISSING' })) -ForegroundColor $(if ($found) { 'Green' } else { 'Red' })
}