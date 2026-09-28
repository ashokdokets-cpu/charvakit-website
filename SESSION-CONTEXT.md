# Session Context - Charvak

**HEAD:** `e28c781`
**Last updated:** 2026-09-29 (Session B - auth persistence + cache revalidation)
**Version:** `v3.5-session-B-20260929`

---

## Where we are

Two production fixes shipped this session, closing flags #2 and #4.

**Commits:**
- `f58e63f` fix(auth): persist auth tokens to Postgres (survives reloads)
- `e28c781` fix(ai-slop): replace Math.random() demo with real scan

**What changed:**
- New table `charvak_auth_tokens` (migration 20260929). Tokens now survive
  uvicorn `--reload` restarts and Render redeploys. `auth.active_tokens`
  stays as an in-process cache, backed by the DB. On cache miss,
  `verify_token` reads from the DB and repopulates.
- `CachedStaticFiles` Cache-Control changed from
  `public, max-age=31536000, immutable` to
  `public, max-age=3600, must-revalidate`. The `?v=2.x` footgun is gone.
- `ai-contamination-detector.html` now calls the real
  `/api/products/ai-slop/scan` route instead of fabricating numbers.

**Verified:** log in via curl -> restart uvicorn -> same token returns
200 on /api/credits/hr@charvakit.com. Prod auto-deployed via push.

---

## Recommended next session

**Session B (continued) - PayPal hardening (~1.5 hr)** closes the
remaining payment flags:
1. #5 - audit `ai_courses_payments.py` for the same PayPal stub pattern
2. #6 - extend `/webhook/paypal` for credits purchases (idempotent)
3. #3 - live PayPal capture test ($2.39 + refund) — last

---

## Remaining open items

1. Premium Report product - product decision (8-12 hrs)
2. uvicorn reload invalidates browser tokens - **RESOLVED** (f58e63f)
3. CachedStaticFiles ?v= - **RESOLVED** (f58e63f)
4. AI-Slop Report Card teaser - **RESOLVED** (e28c781)
5. PayPal credits capture test - Session B
6. ai_courses_payments PayPal stub audit - Session B
7. PayPal credits webhook safety net - Session B
8. /api/na/* auth review - Session C
9. Voice-to-Web Option 2 - feature, deferred

---

## Key files

1. SESSION-CONTEXT.md (this file)
2. COMMITMENT.md - full tracker
3. SYSTEM-AUDIT-2026-09-28.md - audit findings
4. ARCHITECTURE.md - system structure
5. MASTER-REFERENCE.md - infra + API reference
6. KNOWN-ISSUES.md - bug registry

---

## Environment

- HEAD: e28c781
- Local Python: 3.11.9 venv (matches prod)
- Local DB: Postgres 15 at localhost:5432
- Dev server: uvicorn main:app --reload --port 8000
- Prod: https://www.charvakit.com (Render, auto-deploy on push to main)
- Backup: C:\projects\Charvak_Complete_Backup_20260928_230130.zip