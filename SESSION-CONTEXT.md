# Session Context - Charvak

**HEAD:** `0f6c5c1`
**Last updated:** 2026-09-29 (Session B - 4 of 5 payment flags closed; #3 deferred)
**Version:** `v3.5-session-B-20260929`

---

## Where we are

This session closed 4 of the 5 closable flags from the original plan.

**Commits this session:**
- `f58e63f` fix(auth): persist auth tokens to Postgres (survives reloads)
  + Cache-Control: `immutable, max-age=1y` -> `must-revalidate, max-age=1h`
- `e28c781` fix(ai-slop): real /api/products/ai-slop/scan instead of Math.random()
- `7c94b7f` docs: session B close-out
- `9130b8f` fix(paypal): webhook safety net for credits purchases
- `7c679f1` fix(paypal): signature verification + purchase_credits import

### Flags closed

| # | Flag | Commit | Evidence |
|---|---|---|---|
| #2 | uvicorn tokens | `f58e63f` | log in -> restart uvicorn -> same cookie 200 |
| #4 | CachedStaticFiles ?v= | `f58e63f` | Cache-Control now `max-age=3600, must-revalidate` |
| #5 | ai_courses_payments PayPal stub | audit only | no duplicate stub; all create_paypal_order calls go through payment_engine |
| #6 | PayPal credits webhook safety net | `9130b8f` + `7c679f1` | forged prod webhook -> 401; attacker@evil.com has 0 rows |

### Flag deferred

**#3 — PayPal credits capture test (live $2.39)**

Code is ready and locally verified. Not tested end-to-end with a real
capture yet. This is a **live-money** test and deserves a dedicated
session where we can watch the full flow: browser -> PayPal -> frontend
POST -> credits granted -> webhook fires -> idempotent no-op -> refund.

**Prep for next session:**
- Test user: `test-register-2026-09-24@example.com`
- Confirm current balance and plan before starting
- Confirm `/api/payment/status` returns `paypal_ready: true`
- Force non-INR region (localStorage override or VPN)
- PayPal dashboard + Render logs open before clicking "Pay"

**The one thing to watch for:** the webhook log line must show
`already=True`. If it shows `already=False`, the browser path and webhook
path computed different `payment_id` strings and we have a double-grant
bug to fix before the refund.

---

## Security wins this session

- `/webhook/paypal` no longer accepts unauthenticated payloads. The
  docstring claimed signature verification but no code existed — an
  unauthenticated POST with a forged custom_id could grant credits to
  any email. Now forwards to PayPal's
  `/v1/notifications/verify-webhook-signature` and returns 401 on failure.
- `purchase_credits` import bug fixed — the webhook's credits safety net
  was silently failing since commit `9130b8f` because it tried to import
  an instance method as a module-level function.
- Webhook safety net now covers credits purchases: if the browser closes
  after PayPal captures but before the frontend POSTs, the webhook grants
  credits idempotently. `charvak_credit_purchases.payment_id` UNIQUE
  prevents double-grants.

---

## Environment

- HEAD: `7c679f1`
- Local Python: 3.11.9 venv (matches prod)
- Local DB: Postgres 15 at localhost:5432
- Dev server: `uvicorn main:app --reload --port 8000`
- Prod: https://www.charvakit.com (Render auto-deploy on push to main)
- Render service: `srv-d9hhljd8nd3s73d2hoeg`
- Backup: C:\projects\Charvak_Complete_Backup_20260928_230130.zip

---

## Recommended next session

**Session B continued — live PayPal capture test (~30 min)**

Full checklist in COMMITMENT.md under "DEFERRED — PayPal credits
capture test". Everything else from Session B is closed; this is the
last piece.

Alternative (small, low-risk):
- Update ARCHITECTURE.md static-assets section (still references the
  old `immutable` Cache-Control)
- Sweep `scripts/_*.py` files from root — there are 20+ one-off dev
  scripts left over from earlier work

---

## Session 2026-09-29 - AI Tools Suite E2E complete

**Commit:** `8bb21a5`

### Shipped

All 12 AI Tools rebuilt as real, safe, working frontends.

**Problems found:**
- 3 templates (bounty-swap, ghost-tracker, ref-swap) were stubs:
  clicking the button just revealed a pre-baked result card, no API
  call, no credits deducted.
- 1 template (micro-trial) called the wrong endpoint
  (/api/tools/ghost-bounty instead of /api/tools/micro-trial).
- The other 8 had:
  * a fake Math.random() fallback that fabricated a result on
    fetch failure
  * innerHTML with AI output -> XSS hole
  * no 401/402 handling

**Fix:** Canonical template pattern applied to all 12:
- Correct /api/tools/<name> endpoint
- Real form inputs matching the backend's Pydantic model
- No fake fallback - failures surface
- esc() + recursive renderValue() - no innerHTML from AI
- 401 -> /login, 402 -> /ai-credits-pricing
- maxlength matching every Pydantic Field constraint
- Credit cost badge in the hero

**Also fixed:**
- pydantic ValidationError was being swallowed by the routes' broad
  except Exception, returned as HTTP 200 with a generic message.
  Now: imported, re-raised in the 8 tool routes, global 422 handler.
  422 responses carry the exact field name and actual constraint.

### Verified

All 12 tools smoke-tested end-to-end against a real test user:

| Tool | Status | Credits |
|---|---|---|
| resume-roast | 200 | 5 |
| ghost-bounty | 200 | 10 |
| ref-check | 200 | 10 |
| role-mirror | 200 | 5 |
| bounty-swap | 200 | 10 |
| micro-trial | 200 | 10 |
| offer-matcher | 200 | 5 |
| ghost-job-shield | 200 | 10 |
| counter-offer | 200 | 5 |
| ref-swap | 200 | 10 |
| ghost-tracker | 200 | 5 |
| pitch-roast | 200 | 5 |

Total: 90 credits deducted (500 -> 410). 12 usage-history rows.
Real AI output on every call. Elapsed: 39 seconds for all 12.

### Still open (from this session)

- Phase 4: persistence of tool results (charvak_tool_results table +
  /my-tools history page) - next
- #3 live PayPal capture test - deferred

---

## Session 2026-09-29 (continued) - AI Tools persistence shipped

**Commit:** `0f6c5c1`

### Shipped

Phase 4: every AI tool run is now persisted to `charvak_tool_results`.
Users can view their history at `/my-tools`.

New files:
- `migrations/20260929_tool_results.sql` - table + 3 indexes
- `tool_results.py` - record_tool_result() + get_tool_history()
- `templates/my-tools.html` - history view

Changes:
- main.py: 13 routes call record_tool_result, 2 new routes
- base.html: My Tools History nav link in AI Tools dropdown

Design:
- Non-fatal - tools work even if the table doesn't exist
- Indexed on (email, created_at DESC) for fast history
- 100-row limit per user (no pagination yet)

### Full AI Tools Suite status

12 tools, all end-to-end complete:
- Backend route + auth + credits + real AI call
- Frontend form with correct endpoint + safe rendering
- 401/402/422 handling
- Persistence + history view

Verified E2E: 4 tool runs persisted and rendered on /my-tools
(Counter-Offer 5cr, Micro-Trial 10cr, Role-Mirror 5cr, GhostBounty 10cr).

### Still open

- #3 PayPal live capture test (deferred to dedicated session)
- Premium Report product (~8-12 hrs, product decision)
- C7 remaining templates (~10-12 with dead paid tiers)
- Rotate PayPal secret / SYNC keys (external dashboards)
