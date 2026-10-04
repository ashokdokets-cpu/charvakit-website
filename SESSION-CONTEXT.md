# Session Context - Charvak

**HEAD:** `980bbdc`
**Last updated:** 2026-10-04 (Session 16 - Premium Report product shipped)
**Version:** `v3.5-session-16-20261004`

---

## Where we are (Session 16)

Session 16 shipped the **Premium Report** product (Rs 199 / 400 credits)
end-to-end across 5 commits.

**Commits this session:**
- `aa8a279` feat(pdf): add PDF engine for Premium Report generation
- `c60a9a5` feat(premium-report): add report generator engine + routes
- `961a3dc` feat(premium-report): PDF download route + SendGrid email
- `a2537e6` feat(premium-report): frontend unlock flow + /my-reports
- `980bbdc` fix(premium-report): accept ?token= for browser/email downloads

### Shipped

**Premium Report product**
- `pdf_engine.py` — fpdf2-based PDF renderer with branded cover page,
  headers, footers, sections, severity badges, Unicode via DejaVu
- `premium_report_engine.py` — one OpenAI call produces 5 AI sections
  from the source product's free-tier scan data; persists to
  `charvak_premium_reports`; falls back to a template if AI is down
- 3 report types: `auditbot`, `lock_in_breaker`, `skill_twin`
- Credit key: `premium_product_report` (400 cr) — separate from the
  existing `premium_report` (25 cr) used by assessment reports
- SendGrid email with the PDF as a base64 attachment
- `templates/includes/premium-upsell.html` rewritten to be
  config-aware (reads `window.CHARVAK_PREMIUM`); falls back to
  notifyMe() on the 24 other pages that include it
- `/my-reports` dashboard listing the user's reports with
  Download PDF buttons

### E2E verified
- Full flow: free scan → unlock → AI generation → PDF → email → download
- Credit deduction: exact 400 per report
- 3 premium reports generated during testing
- Email delivered to test-register email
- Download works from both the inline upsell and the dashboard

### Notes
- Browser <a href> navigations don't send Authorization headers, so
  the download route accepts ?token= as a fallback. `/generate`
  includes the caller's token in the returned `download_url`.
- Fixed a latent bug: `auditbot.html` never set
  `window.lastAuditResult`, so the upsell always said "Run a scan
  first". The other two premium pages already did.

---

## Where we are

Session 15 completed Silent-Killer 9b (continuous monitoring cron +
state-change email alerts) plus several smaller items.

**Commits this session:**
- `5e64b1a` feat(payments): expose PAYPAL_MODE in /api/payment/status
- `1f1f834` docs: sync SCHEMA.md (128->164 tables) + PAGES-INVENTORY delta
- `f468c50` feat(silent-killer): continuous monitoring cron + alerts (Session 9b)

### Shipped

**Silent-Killer 9b (headline)**
- enhanced_email.send_silent_killer_alert() - SendGrid email on state change
- products_engine.silent_killer_due_watches() - due-watch selector
- POST /api/cron/silent-killer-scan - X-Cron-Secret auth
- Full frontend rewrite of the script block (previous version had 15
  lines with malformed JS strings; page rendered but nothing worked)
- "Notify Me" button retired; live badge replaces it
- Render cron job silent-killer-scan runs every 5 min, verified firing

**Observability**
- /api/payment/status now returns paypal_mode ("live" | "sandbox")
- Fixed CRON_SECRET typo in local .env (colon -> equals)
- Set PAYPAL_MODE=live on Render; confirmed via /api/payment/status
- Added CRON_SECRET to silent-killer-scan cron's environment

**Docs**
- SCHEMA.md regenerated: 128 -> 164 tables
- PAGES-INVENTORY.md header bump + Sessions 8-15 delta section

### Verified E2E

Local:
- Cron without secret -> 401
- Cron with wrong secret -> 401
- Cron with correct secret -> 200
- Due watch detection -> only due watches scanned
- fail -> ok flip -> alerted: 1, email sent to owner
- Browser: page fully functional (panel, recheck, history, delete)

Prod:
- /api/payment/status: paypal_mode = "live"
- Render cron silent-killer-scan: 200 + {"status":"success",...}
- Created a test watch directly in prod DB; Render cron picked it up
  and ran the scan within 5 minutes (confirmed scan row with 200 OK).
  Test watch was cleaned up afterward.

### Local vs Prod database

Local .env.local points at charvak_dev on localhost:5432.
Prod uses vouchai on Render Postgres.

### Flagged for Session 16

- Career Assessment Phase 2b: coding + SQL via Judge0 (2-3 days)
- Premium Report product (8-12 hrs, product decision)
- Doc pass on remaining stale files (DEFERRALS, DEV-SETUP, DOC-STYLE)
- Rotate PayPal + SYNC keys (external dashboards)

---

## Career Assessment product status

| Phase | Status |
|---|---|
| Phase 1 (MCQ) | Shipped |
| Phase 2a (7 more formats) | Shipped |
| Phase 3 (adaptive + skill gap + learning paths) | Shipped |
| Phase 2b (coding + SQL) | Session 16+ |
| Phase 4 (certs, badges) | Future |

---

## Environment

- HEAD: f468c50
- Local Python: 3.11.9 venv
- Local DB: Postgres 15 (charvak_dev)
- Prod DB: Render Postgres (vouchai)
- Prod: https://www.charvakit.com
- Render service: srv-d9hhljd8nd3s73d2hoeg
- Render cron jobs: send-emi-reminders, cleanup-notifications,
  send-queued-emails, silent-killer-scan (new)

---

## Session 17 COMPLETE — Sprint A shipped (2026-10-04)

Sprint A of the Proof Layer framework is live. The free Role Readiness
Certificate is end-to-end: landing page -> assessment -> shareable
certificate URL with HMAC verification.

**7 commits shipped:**
- 14b2bb8  feat(readiness): Sprint A backend (engine + 5 routes + benchmarks)
- 4fc158e  feat(readiness): readiness.html (public certificate page)
- 2c09632  feat(readiness): readiness-check.html + route (public landing)
- 87aa95a  feat(readiness): ai-assessment deep-link + certificate CTA
- 814db5e  fix(readiness): percentile floor 5..99, level/passing fallbacks, OG tags
- <next>   fix(readiness): move var _a out of string concat

**Live at:**
- GET /readiness-check     — public free landing
- GET /readiness/{id}      — public shareable certificate
- GET /api/readiness/{id}  — public read
- GET /api/readiness/verify/{hash}  — public verification
- POST /api/readiness/generate      — auth-gated certificate creation
- GET /api/readiness/list/{email}   — auth-gated list

**Verified E2E on local:**
- Dropdowns populate [107, 67, 8] for role/industry/level
- Free check start -> deep-link -> questions skip Step 1
- Answer -> result page (with green certificate CTA)
- Get My Certificate -> /readiness/RDC-XXXX
- Certificate renders with score, benchmark, percentile (floor 5), hash
- Verify URL returns {valid: true}
- Tampered hash returns {valid: false}

**Session 18 scope (next):**
1. Custom-course generator (replace external links with Charvak-hosted
   custom courses in learning paths)
2. Size upgrade CTA on quick-check results (10 -> 20 questions for
   below-benchmark users)
3. Sprint B kickoff: /my-jobs verified matching

---

## Session 17 priority (locked)

**Scope:** Gap 1 (Role Readiness Score) + Gap 3 (Anti-Cheating Layer A)
alongside Career Assessment Phase 2b (coding/SQL via Judge0).

**Why:** Gap 3 is a prerequisite for Phase 2b — without integrity signals,
employers will dismiss the coding/SQL assessments. Shipping 2b without
anti-cheating produces a technically complete feature that fails commercially.

**Reference:** See `COMPETITIVE-STRATEGY.md` for the full analysis, the 4 gaps,
the roadmap, and the metrics we're tracking. Re-read at the start of every
session.

**Gaps 2 and 4 (deferred, documented):**
- Gap 2: Multilingual Voice AI — Sessions 20+
- Gap 4: AuditBot Continuous Compliance — Sessions 18-19

---

## Recommended next session (Session 16)

Option A: Career Assessment Phase 2b (coding + SQL) - 2-3 days.
Option B: Premium Report product - 8-12 hrs.
Option C: Doc pass + cleanup - ~1.5 hrs.

Recommendation: A.

**Post-Session 16 update:** Premium Report shipped. Session 17 is now
open to:
- Career Assessment Phase 2b (coding + SQL via Judge0 sandbox)
- Or a doc pass on the remaining stale files
- Or a security sweep (Session 14 style)