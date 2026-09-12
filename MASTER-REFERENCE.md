# CHARVAKIT.COM — MASTER REFERENCE
## Charvak IT Consulting Pvt Ltd
### Last updated: September 13, 2026

**Live:** https://www.charvakit.com
**Version:** v1.1-stable-20260913

---

## SYSTEM OVERVIEW

- Engines: 29+
- Templates: 180+
- APIs: 160+
- Languages: 34 global + 12 Indian
- Visa Types: 17
- Security: 7 layers
- Payments: LIVE (Razorpay + PayPal + UPI)
- AI Credits: DB-backed, persisted (Fix B — 2026-09-12)
- Webhook safety net: LIVE (Fix C — 2026-09-13)

---

## COMPANY

- **Location:** #301, Sri Padmavati Towers, 3rd Lane, Seetaram Nagar, Guntur 522001, Andhra Pradesh, India
- **Email:** hr@charvakit.com
- **Phone:** +91 799 7871 701

**Two products share one Render Postgres database:**
1. **Charvak** (this project) — AI tools, exams, credits, career engine
2. **Dokets VouchAI** — AI escrow platform (dokets.com)

---

## INFRASTRUCTURE

| Service | Identifier | Notes |
|---|---|---|
| Render (Charvak) | `srv-d9hhljd8nd3s73d2hoeg` | Python 3.11.9, Singapore |
| Render (VouchAI) | `srv-d9nque942hec7386q3mg` | Node, Singapore |
| Render Postgres | `dpg-d9m92j0ae00c73blvoq0-a` | DB: `vouchai` (shared) |
| GitHub | `ashokdokets-cpu/charvakit-website` | main branch |
| Cloudflare | www.charvakit.com | CDN + DNS |
| Razorpay | LIVE | INR payments + webhook |
| PayPal | LIVE | 16 currencies |
| SendGrid | LIVE | Transactional email |
| OpenAI | GPT-4o-mini | AI features |
| ElevenLabs | LIVE | Voice features |

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
| Templates | Jinja2 (180+) |
| Database | PostgreSQL via psycopg2 |
| Frontend | Bootstrap 5, vanilla JS, Chart.js |
| Hosting | Render (Singapore) |
| CDN | Cloudflare |
| CI/CD | GitHub push → Render auto-deploy |

---

## ENGINES (29)

payment, kyc, escrow, referral, badge, blog, chatbot, sso,
micro_internship, training, interview_prep, job_board,
products, candidate, email, messaging, events, brand, team,
ats, university, enterprise, invoice, tools,
marketing_ai, indian_language_ai, lms, career_v2

Plus newer: `ai_credit_engine` (DB-backed), `email_verification` (DB-backed)

---

## FEATURES

- 16 AI Products + 12 AI Tools
- NA Module (17 visas, 6 files)
- Career Center (alerts, saved jobs, interviews, offers)
- LMS (ratings, quizzes, certificates, lessons, payouts)
- Marketing AI (job ads, social posts)
- Indian Language AI (12 languages)
- Enterprise (Teams, ATS, University, Enterprise)
- **AI Credits** (purchase, daily bonus, usage history — persisted)
- **Exam Prep** (122 exams, Indian + global)

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

### VouchAI-owned tables (shared DB, do not touch)

`Contract`, `Dispute`, `Milestone`, `Payment`, `User`, `UserAchievement`, `jobs`, `applications`

---

## API ENDPOINTS (key)

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login` — email verification check + admin bypass
- `POST /api/auth/logout`, `/api/auth/logout-all`
- `GET /api/auth/me`

### Credits
- `GET /api/credits/plans`
- `GET /api/credits/{email}`
- `POST /api/credits/check`
- `POST /api/credits/purchase` — **Fix A: requires verified payment for paid plans**
- `POST /api/credits/daily-bonus`
- `GET /api/credits/expiry/{email}`, `/api/credits/usage/{email}`
- `GET /api/credits/admin/stats`

### Payments
- `POST /api/payment/create-order` — creates Razorpay/PayPal order
- `POST /api/payment/verify` — client-side callback verification
- `GET /api/payment/history`
- **`POST /webhook/razorpay`** — server-to-server webhook (Fix C)

### Admin
- `/admin-login`, `/admin-control`
- All `/admin*` routes protected by middleware

---

## PAYMENT FLOW (post Fix A/B/C)
User selects plan
→ POST /api/payment/create-order
→ payment_engine.create_razorpay_order()
→ order notes: {plan, email, tool, amount_inr}

Razorpay modal opens; user pays

Client callback fires (in browser):
→ POST /api/payment/verify (HMAC signature check)
→ POST /api/credits/purchase {email, plan, payment_id}
→ purchase_credits() verifies payment via Razorpay API
→ credits granted + plan upgraded

Webhook fires (server-to-server, parallel):
→ POST /webhook/razorpay (HMAC with RAZORPAY_WEBHOOK_SECRET)
→ extracts plan/email from payment.notes
→ calls purchase_credits() — idempotent, no double-credit

text

**Idempotency:** `payment_id` UNIQUE in `charvak_credit_purchases`. Second call returns `already_credited: true`.

**Admin bypass:** admins skip verification and credit checks.

---

## ADMIN ACCOUNTS

| Email | Role |
|---|---|
| charvakit@gmail.com | Admin |
| hr@charvakit.com | Admin |

**Rotate password:** `python scripts\rotate_admin_password.py`

---

## PROJECT STRUCTURE
charvakit-new/
├── main.py # FastAPI app (~4500 lines)
├── auth.py # Register, login, tokens
├── database.py # DB connection + user CRUD
├── payment_engine.py # Razorpay + PayPal + webhook sig verify
├── ai_credit_engine.py # DB-backed credits
├── email_verification.py # DB-backed verification
├── password_reset.py
├── email_engine.py # SendGrid
├── admin_access.py, admin_role_manager.py
├── [40+ other engines]
├── templates/ # 180+ Jinja2 pages
├── static/ # css, js, images, fonts
├── na_module/ # North America modules
├── scripts/ # Dev/ops scripts
├── requirements.txt, runtime.txt
├── .env # Never committed
├── STATUS.md # Session continuity
├── MASTER-REFERENCE.md # ← this file
├── ARCHITECTURE.md
├── PAGES-INVENTORY.md

text

---

## OPERATING COMMANDS

```powershell
# Local dev
uvicorn main:app --reload --port 8000

# Backup (creates Desktop folder + ZIP)
python scripts\full_backup.py

# Rotate admin password
python scripts\rotate_admin_password.py

# Tag a stable release
git tag -a "vX.Y-stable-YYYYMMDD" -m "description"
git push --tags

# Push code
git add .
git commit -m "message"
git push origin main
BACKUPS
Latest: Charvak_Complete_Backup_20260913_024908.zip (24.75 MB, 4,597 entries)

Includes:

All source code, templates, static assets

.env (with secrets)

.git (full history)

scripts/

_MANIFEST.txt, _README.txt

Security note: backup ZIPs contain .env secrets — do not email or share publicly.

KNOWN ISSUES / TODO
□ Heading order on index.html (h4→h3 skip)
□ TBT ~1,900ms mobile — needs conditional script loading
□ Mojibake scan of remaining templates
□ Real abandoned-checkout webhook test
EXTERNAL DASHBOARDS
Render: https://dashboard.render.com

GitHub: https://github.com/ashokdokets-cpu/charvakit-website

Razorpay: https://dashboard.razorpay.com

SendGrid: https://app.sendgrid.com

OpenAI: https://platform.openai.com

Cloudflare: https://dash.cloudflare.com

Keep this file updated after major changes.

text

**Save with Ctrl+S.** Close Notepad.

### Step 4 — Verify

```powershell
Get-ChildItem MASTER-REFERENCE.md* | Select-Object Name, Length
Expected:

MASTER-REFERENCE.md — ~7000 bytes (new comprehensive version)

MASTER-REFERENCE.md.pre-20260913 — 874 bytes (old preserved)