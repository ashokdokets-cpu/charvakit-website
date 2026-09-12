# Charvak Architecture

**Last updated:** 2026-09-13
**Version:** v1.1-stable-20260913

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
┌───────────────────┼───────────────────┐
│ │ │
▼ ▼ ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Render Postgres│ │ Razorpay + │ │ SendGrid + │
│ (vouchai DB) │ │ PayPal │ │ OpenAI + │
│ shared w/VouchAI│ │ LIVE mode │ │ ElevenLabs │
└────────────────┘ └────────────────┘ └────────────────┘

text

---

## Request Lifecycle
Browser → Cloudflare → Render (uvicorn) → FastAPI app
│
┌─────────────────────────────┼──────────────────────────────┐
│ │ │
▼ ▼ ▼
Static middleware SecurityHeaders Route handler
(CachedStaticFiles) middleware (main.py)
│
▼
Engine call
(ai_credit_engine,
payment_engine, etc.)
│
▼
database.py
│
▼
Render Postgres

text

**Middleware stack (in order):**
1. `SecurityHeadersMiddleware` — CSP, HSTS, X-Frame-Options, etc.
2. `MaxBodySizeMiddleware` — request size limits
3. `CORSMiddleware` — cross-origin rules
4. Rate limiting (slowapi `@limiter.limit`)
5. Admin auth guard — protects `/admin*` and `/api/admin*`

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
→ else: email_verification.is_verified(email) — queries tokens table
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
- **No more in-memory** — survived a real fix on 2026-09-12
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
Stored in `FEATURE_CREDITS` dict in `ai_credit_engine.py`. Examples:
- `chatbot_query` — 2
- `resume_roast` — 5
- `fyp_documentation` — 30
- `default` — 10

### Admin bypass
`check_and_deduct()` returns immediately for admin emails with `credits_remaining: 999999999`.

---

## Payment Flow (post Fix A/B/C)

### Order creation
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
→ payment_engine.verify_razorpay_payment() — HMAC check
→ if verified: POST /api/credits/purchase {email, plan, payment_id}

text

### `/api/credits/purchase` (Fix A)
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

Call purchase_credits() — same idempotent path

Return 200 (even on error — prevents Razorpay retry storms)

text

### Idempotency
- `charvak_credit_purchases.payment_id` has UNIQUE constraint
- Second call with same payment_id → `{already_credited: true, credits_added: 0}`

---

## Data Flow: Credit Purchase (end-to-end)
User clicks "Subscribe" on Starter plan

Frontend: POST /api/payment/create-order
Backend: payment_engine → Razorpay API → order_id

Razorpay checkout modal opens in browser

User completes payment

Razorpay redirects back → frontend handler fires

┌─────────────┐
│ Browser │
└──────┬──────┘
│ POST /api/payment/verify
│ POST /api/credits/purchase
▼
┌─────────────┐ ┌─────────────┐
│ FastAPI │◄────────│ Razorpay │
│ /purchase │ verify │ API │
└──────┬──────┘ payment└─────────────┘
│
▼
┌─────────────┐
│ Postgres │
│ credits │
└─────────────┘

(in parallel)
┌─────────────┐
│ Razorpay │──── webhook ────► POST /webhook/razorpay
│ servers │ → idempotent no-op
└─────────────┘

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
git push origin main

GitHub webhook → Render detects change

Render builds (pip install -r requirements.txt)

Render starts (uvicorn main:app --host 0.0.0.0 --port $PORT)

~2 min total

Rollback
text
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

Includes: source, templates, static, .env, .git, scripts/, manifest, README

Restore on new machine
Unzip archive

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

.env is already present (contains secrets)

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
Security Layers
Cloudflare — DDoS, WAF, SSL termination

CSP — restrictive content-security-policy header

HSTS — 1-year strict transport security

Rate limiting — slowapi on all public endpoints

Admin middleware — charvak_admin_token cookie required

HMAC verification — Razorpay + webhook signatures

Parameterized SQL — no string concatenation in queries

Known weakness: CSP allows unsafe-inline and unsafe-eval (Bootstrap requirement). Hardening would break the site without a refactor.

File Naming Conventions
*_engine.py — feature module with business logic

*_service.py — supporting service (job, monitor)

*_manager.py — CRUD manager

templates/*.html — page templates

templates/includes/*.html — reusable components

templates/tools/*.html — AI tool pages

scripts/*.py — dev/ops scripts (not imported by main.py)

Keep in sync with MASTER-REFERENCE.md

text

**Save with Ctrl+S.** Close Notepad.

## Verify

```powershell
Get-ChildItem ARCHITECTURE.md* | Select-Object Name, Length
Expected: ARCHITECTURE.md — should now be ~7000-8000 bytes (was 523).