# DEAN REPORT FRONTEND — FLAGGED FOR LATER BUILD

**Flagged:** 2026-10-24
**Status:** NOT BUILT (backend complete, frontend deferred)
**Trigger to build:** First paying client who needs self-serve access

---

## What's Already Done (Backend — Live on Prod)

### APIs
- `GET /api/proof-dashboard/{university_id}` — returns full JSON (cohort, depts, trend, cert views, peer benchmark)
- `GET /api/proof-dashboard/{university_id}/pdf` — returns 4-page Dean PDF
- `POST /api/certificate/{cert_id}/track-view` — records every cert view

### Data
- `charvak_certificate_views` table (live)
- `charvak_universities` + `charvak_university_students` (seeded)
- `charvak_readiness_certificates` (linked via email)
- 3 seeded institutions: Amrita, VIT, NIT Trichy
- 150 students, 222 certs, 207 views

### Engine
- `university_engine.get_proof_dashboard(university_id)` — full aggregation
- `university_engine.record_cert_view()` — idempotent tracking
- `pdf_engine.render_dean_report_pdf(data)` — 4-page branded PDF

### Verified Working
- Local: YES
- Prod: YES (`https://www.charvakit.com/api/proof-dashboard/UNI-AMRITA-001/pdf` returns 5.9 KB PDF)
- 3 Dean reports downloaded to Desktop (Amrita, VIT, NIT Trichy)

---

## What's NOT Built (Frontend)

| Component | Status | Effort |
|---|---|---|
| HTML dashboard page (`/admin/proof-dashboard/{id}`) | ❌ Not built | 1 session |
| Charts (bar chart for departments, line chart for trend) | ❌ Not built | Included |
| "Download PDF" button | ❌ Not built | Included |
| Login page for university admins | ❌ Not built | 1 session |
| Session management (cookies/JWT) | ❌ Not built | Included |
| Auth middleware on `/admin/proof-dashboard/*` | ❌ Not built | Included |
| Signed URL route (`/report/{hmac-token}`) | ⏸ Code written, reverted | 0.5 session |
| Email delivery of signed links | ❌ Not built | 0.5 session |
| Admin UI to generate signed links | ❌ Not built | Included |
| Client self-regenerate report | ❌ Not built | Included |

**Total estimated effort:** 2-3 sessions (~6-8 hours)

---

## When to Build This

### Trigger Conditions (build when ANY of these happen)

1. **First paying client says:** "I want to see this every month without asking you"
2. **You land 3+ paying universities** — manual email doesn't scale
3. **A client asks:** "Can my Dean see this himself?"
4. **Amrita converts from pilot to paid** (₹49,999+/year)

### Don't Build When
- 0-2 clients (manual PDF email works fine)
- Pilot stage (all parties are experimenting)
- Pitch/demo stage (PDFs are sufficient)

---

## The Full Frontend Build Plan (When Triggered)

### Phase 1: Public Signed URLs (0.5 session)

**What:** Generate shareable, expiring, HMAC-signed URLs.

**Files:**
- `report_token_engine.py` (engine — already written, needs committing)
- Route: `GET /report/{token}` (verify HMAC, return PDF inline)
- Route: `POST /api/admin/generate-report-link/{university_id}` (admin generates link)
- Lock down `/api/proof-dashboard/*` to require admin auth

**Flow:**
1. Admin (you) calls `/api/admin/generate-report-link/UNI-AMRITA-001`
2. Get back URL like `https://www.charvakit.com/report/a1b2c3d4...`
3. Email that URL to client
4. Client clicks → sees branded PDF (valid 30 days)
5. Link expires automatically

**Use case:** Client wants to see report but doesn't need login.

---

### Phase 2: Authenticated Dashboard (1.5 sessions)

**What:** Login + web UI dashboard per university admin.

**New tables:**
- `charvak_university_admins` (email, password_hash, university_id, role, created_at)
- (Or: reuse `users` table with a role='university_admin' + university_id column)

**New routes:**
- `GET /university/login` — login page
- `POST /api/university/login` — authenticate
- `GET /admin/proof-dashboard/{university_id}` — dashboard page (auth-gated)
- `POST /admin/proof-dashboard/{university_id}/refresh` — regenerate report
- `POST /api/university/send-report-email` — email the PDF to any address

**New templates:**
- `templates/university-login.html`
- `templates/admin-proof-dashboard.html`
  - KPI cards (cohort, certified, avg score, peer percentile)
  - Bar chart (departments) — use Chart.js
  - Line chart (trend) — use Chart.js
  - Top 10 students table
  - Cert view stats
  - "Download PDF" button
  - "Email this report" input

**Flow:**
1. Client logs in with email + password
2. Sees ONLY their university's dashboard
3. Can download PDF anytime
4. Can email PDF to Dean with 1 click

**Onboarding:**
- You (admin) create university admin account via `/admin/university-admins` page
- Send credentials to client via email
- Client logs in, sees dashboard

---

### Phase 3: Automate Delivery (1 session)

**What:** Monthly auto-email with signed link.

**What to build:**
- Render cron job (1st of each month):
  - For each paying client: generate signed URL, send email "Your monthly readiness report is ready"
- Admin UI to configure frequency (monthly, quarterly)
- Track email opens (SendGrid webhook)

**Tables:**
- `charvak_report_subscriptions` (university_id, frequency, last_sent_at, email_address)
- `charvak_report_deliveries` (delivery_id, university_id, sent_at, opened_at, email)

---

## The Decision We Made (2026-10-24)

**For now:**
- Backend APIs live
- PDFs generated per request
- Delivered by manual email
- No frontend UI
- No auth required on APIs (URLs are guessable but nobody knows them)

**Why:**
- 0 paying clients
- Amrita pilot not signed yet
- PDFs by email are the right delivery for demo stage

**Reference:** See `DEAN_REPORT_DECISION.md` (committed at `489ed68`)

---

## Trigger Checklist (Re-read This Each Month)

- [ ] Have any paying university clients? (count: ___)
- [ ] Has any client asked for self-serve access?
- [ ] Have we sent 5+ Dean reports this month?
- [ ] Is manual email delivery taking >1 hour/week?

**If any "yes" → BUILD THE FRONTEND. Start with Phase 1 (signed URLs).**

**If all "no" → keep manual email. Revisit next month.**

---

## Files to Keep Safe (for when we build this)

- `pdf_engine.py::render_dean_report_pdf()` — working
- `university_engine.py::get_proof_dashboard()` — working
- `scripts/seed_proof_dashboard.py` — test data generator
- `migrations/20261024_proof_dashboard.sql` — schema
- `DEAN_REPORT_DECISION.md` — original decision

**When ready to build:** `grep -r "proof-dashboard" .` in repo, then start with Phase 1.

---

**Last updated:** 2026-10-24 (Session 80 close)
**Owner:** Bhavya M
**Next review:** 2026-11-24 (or immediately if a paying client asks)