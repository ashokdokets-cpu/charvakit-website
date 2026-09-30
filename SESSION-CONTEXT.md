# Session Context - Charvak

**HEAD:** `5b9d1c5`
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

---

## NEXT SESSIONS - C7 paid-tier backlog (queued 2026-09-29)

The AI Tools Suite is done. Next work is closing the C7 gap: every
product page still has 1-3 dead paid-tier buttons wired to notifyMe()
instead of a real purchase flow.

### Session 3 (~3 hrs) - AuditBot paid tiers

Highest-value per tracker. Product page: /auditbot
Backend already exists: POST /api/products/auditbot/scan (25 cr).

Two dead buttons to ship:
1. "Fix" - Rs 299 - takes the scan result and generates an AI fix patch
2. "Subscription" - Rs 999/mo - ongoing monitoring + alerts

Design decision: credits-based, not separate Razorpay.
- auditbot_fix: 50 credits (=~Rs 299 at current pricing)
- auditbot_monthly: 150 credits

Deliverables:
- 2 new routes: POST /api/products/auditbot/fix, POST /api/products/auditbot/subscribe
- New tables: charvak_auditbot_fixes, charvak_auditbot_subscriptions
- Frontend: replace 2 notifyMe calls with real forms
- Webhook for subscription renewals (or manual renew for now)

### Session 4 (~4 hrs) - Lock-In Breaker paid tiers

Product page: /lock-in-breaker (also /lock-in-breaker-pricing)
Backend exists: POST /api/products/lock-in-breaker/audit (25 cr).

Two dead buttons:
1. "Migration" - Rs 4,999 - full migration plan
2. "Continuous Protection" - Rs 4,999 - ongoing lock-in watch

Deliverables:
- 2 new routes: .../migration-plan, .../protection
- New table: charvak_lock_in_engagements
- Credit keys: lockin_migration (800 cr), lockin_protection (800 cr)
- Frontend: replace notifyMe buttons

Note: Rs 4,999 self-serve vs book-a-call is a product decision.
Recommend: self-serve at these price points, since the engine already
produces value at scan time.

### Session 5 (~6 hrs) - Micro-Squads

Product page: /micro-squads
Backend exists: POST /api/products/micro-squads/assemble (25 cr).

One dead button: "Assembly" - Rs 49,999.

This is NOT a self-serve click-to-pay product. Rs 49,999 needs a
sales conversation. Recommend: replace notifyMe with a calendar booking
form (or a Calendly-style embed). Store the lead in
charvak_micro_squad_leads.

Deliverables:
- POST /api/products/micro-squads/lead - captures booking request
- New table: charvak_micro_squad_leads
- Frontend: replace notifyMe with booking form + confirmation email

### Session 6+ - Remaining C7 (batch by complexity)

Small (< 1 hr each):
- Marketing AI (Rs 299) - single tier
- Background Verification (variable) - single tier
- Bridge (Rs ~) - premium calc
- Developer Entropy (Rs 299) - monitoring tier
- AI-Slop Quarantine (Rs 149) - cleanup tier

Medium (1-2 hrs each):
- Design-Token (Rs 299 Pro)
- Geo-Compliance (Rs 199 + Rs 999) - 2 tiers
- Agency-Twin (Rs 2,999 Pro)
- Team Dashboard (Rs 1,999 Pro)
- Reverse Staffing (subscription)
- LMS (Rs 999 enroll)
- University (Rs 4,999)

Large (2-4 hrs each):
- Legacy-Shift (Rs 4,999 migration)
- Skill-Twin (Rs 499 verify) - also needs persistence (AA4d deferred)

### Design principle for all of the above

Ship as CREDITS, not separate Razorpay charges.

Rationale:
- One-time credit purchase already works (Fix A/B/C from 2026-09-12)
- Existing infra: FEATURE_CREDITS dict, check_and_deduct,
  charvak_credit_usage_history
- No new payment paths = no new webhook signature bugs
- Users top up once, spend across products
- Refunds/chargebacks handled centrally

Only exception: Micro-Squads (Rs 49,999) which needs a sales-lead
flow, not self-serve checkout.

### Per-template checklist (for each C7 session)

1. Add credit key to FEATURE_CREDITS in ai_credit_engine.py
2. Add the backend route with require_auth_for_email + require_credits_from_data
3. Add DB table if the result needs to persist
4. Replace notifyMe() in the template with a real form + fetch
5. Add 401/402/422 handling (copy from tools templates)
6. Record the run (if it makes sense) - reuse tool_results.py pattern
7. Test E2E: form -> credit deduction -> real output -> render

---

## Session 3 (2026-09-30) - AuditBot paid tiers shipped

**Commit:** `52fc994`

AuditBot is now complete end-to-end. Both paid tiers replace the
Session G6 notifyMe placeholders with real credits-based flows.

### One-Time Fix (600 credits)
- Route: POST /api/products/auditbot/fix
- Engine: products_engine.auditbot_fix(data)
- Consumes last scan findings, calls OpenAI for a structured guide
- Persists to charvak_auditbot_fixes
- Frontend: "Get Fixed" button now POSTs and renders the guide inline

### Continuous Monitoring (400 credits for 30 days)
- Route: POST /api/products/auditbot/subscribe
- Engine: products_engine.auditbot_subscribe(data)
- UPSERT into charvak_auditbot_subscriptions (30-day expiry)
- Frontend: "Subscribe" button now POSTs and renders confirmation

### Design decisions
- Credits-based, not separate Razorpay. Reuses existing infra.
- 1 credit = Rs 0.50 (Pro plan rate)
  - Rs 2,999 One-Time Fix = 600 credits
  - Rs 1,999 Continuous = 400 credits
- No cron for "real" 24/7 monitoring yet. Subscription unlocks
  unlimited ad-hoc scans for 30 days. Scheduled scans = future feature
  when there is demand.
- Removed a stray trailing 'F' character after the Subscribe button

### Verified E2E with test-register-2026-09-24@example.com
- Scan: 200, 25 credits, SCAN-9F09F99A
- Fix: 200, 600 credits, FIX-88A2A1FA2C5D, 7-step AI guide persisted
- Subscribe: 200, 400 credits, continuous tier, 30-day expiry persisted
- 402 correctly blocks Subscribe on insufficient credits
- Browser flow works via /auditbot

### Session 4 next - Lock-In Breaker paid tiers
Two dead tiers (Rs 4,999 x 2). Same pattern:
- Migration: charvak_lock_in_engagements table
- Credit keys: lockin_migration, lockin_protection (suggest 1000 each)
- Routes: /api/products/lock-in-breaker/migration-plan, .../protection
- Frontend: replace 2 notifyMe calls in lock-in-breaker.html

---

## Session 4 (2026-09-30) - Lock-In Breaker paid tiers shipped

**Commit:** `24c9955`

Both paid tiers now work end-to-end as credits-based flows. Was: one
live notifyMe plus one fake Razorpay flow that never persisted a
server-side record (latent money bug — Razorpay charge with no
backend record).

### One-Time Migration (1000 credits, ~Rs 4,999)
- Route: POST /api/products/lock-in-breaker/migration-plan
- Engine: products_engine.lock_in_migration_plan(data)
- Real AI plan: 5 phases, service mapping, cutover, criteria, team
- Persists to charvak_lock_in_engagements (tier='migration')

### Continuous Protection (1000 credits for 30 days, ~Rs 4,999/mo)
- Route: POST /api/products/lock-in-breaker/protection
- Engine: products_engine.lock_in_protection(data)
- 30-day engagement with expires_at
- Persists to charvak_lock_in_engagements (tier='protection')

### Frontend
- lock-in-breaker.html: real handlers, esc() helper, Start Migration
  button added next to existing Get Continuous Protection
- lock-in-breaker-pricing.html: fake Razorpay flow stripped; page is
  now reference-only, both buttons redirect to /lock-in-breaker
- Copy: Rs 4,999 -> 1000 credits

### Verified E2E
- Audit: 20 cr, AUDIT-AFB077CA, HIGH complexity
- Migration: 1000 cr, LIE-A746A84F9CEF, 5-phase AI plan
- Protection: 1000 cr, LIE-5C94EAF47EFD, 30-day expiry
- Balance 3000 -> 980 exactly
- 2 rows in charvak_lock_in_engagements with correct tiers
- 3 usage-history rows

### Session 5 next - Micro-Squads (Rs 49,999)
Different shape: sales-lead flow, not self-serve checkout.
Plan:
- New table: charvak_micro_squad_leads
- Route: POST /api/products/micro-squads/lead
- Frontend: replace notifyMe with a booking form + confirmation email
- SendGrid notification to sales on new lead

### Remaining C7 (~10 templates) after Micro-Squads
Small (< 1 hr): Marketing AI, Background Verification, Bridge,
Developer Entropy, AI-Slop
Medium (1-2 hrs): Design-Token, Geo-Compliance, Agency-Twin,
Team Dashboard, Reverse Staffing, LMS, University
Large (2-4 hrs): Legacy-Shift, Skill-Twin (also needs persistence)

---

## Session 5 (2026-09-30) - Micro-Squads lead capture shipped

**Micro-Squads Rs 49,999 tier is now a real sales-lead flow, not a
notifyMe placeholder.** Different shape from AuditBot / Lock-In Breaker
because Rs 49,999 is a sales conversation, not self-serve checkout.

### Backend
- Route: POST /api/products/micro-squads/lead
- No credit deduction (lead, not paid feature)
- Auth-gated (require_auth_for_email) so leads tie to real accounts
- Validates name (>=2), email, requirement (20-5000 chars)
- Persists to charvak_micro_squad_leads with status='new' + squad_id
- Sends HR notification to HR_EMAIL
- Sends confirmation email to the user
- Returns lead_id

### Frontend
- templates/micro-squads.html: dead assembleSquad() removed
- Added openLeadForm() + submitLead()
- Added squadLeadModal with form fields + XSS-safe esc()
- renderSquadResult saves window.lastSquadResult and appends
  "Request Squad Assembly - Talk to Sales" CTA after the free scan

### Verified E2E
- Free scan: 25 cr, SQUAD-6ADC4107
- Lead: 0 cr, LEAD-2356D884840F, 200
- Balance 980 -> 955 (only the scan deducted)
- Lead row correct in charvak_micro_squad_leads
- HR email received at hr@charvakit.com

### C7 progress
- Session 3: AuditBot (2 tiers) ✅
- Session 4: Lock-In Breaker (2 tiers) ✅
- Session 5: Micro-Squads (1 lead flow) ✅
- Session 6: small/medium C7 batch (~10 templates)
  Small: Marketing AI, Background Verification, Bridge,
         Developer Entropy, AI-Slop
  Medium: Design-Token, Geo-Compliance, Agency-Twin,
          Team Dashboard, Reverse Staffing, LMS, University
- Session 7: Legacy-Shift + Skill-Twin (also needs persistence)

---

## Session 6 progress (2026-09-30) - Batch 1 + 2a + 2b-1 shipped

### Batch 1 (`3e0cbb5`) - 6 templates wired to existing routes
- developer-entropy.html
- ai-slop-quarantine.html
- design-token-sentinel.html
- geo-compliance.html (2 tiers)
- agency-twin.html
- reverse-staffing.html

Frontend-only. All had working backend, just dead notifyMe buttons.

### Batch 2a (`b616466`) - 3 new routes for existing templates
- POST /api/products/geo-compliance/contract (400 cr)
- POST /api/products/geo-compliance/hiring   (2000 cr)
- POST /api/products/reverse-staffing/subscribe (1000 cr)

3 new tables, 3 new engine methods, 3 new credit keys.

### Batch 2b-1 (`d1d21df`) - bridge.html full stack
- POST /api/bridge/premium (1000 cr)
- Engine: bridge_engine.bridge_premium_calculator()
- Table: charvak_bridge_premium_reports
- Real 5-year projection + sensitivity + board recs + white-label spec

### Batch 2b remaining (3 templates)
- marketing-ai.html (Rs 299)
- team-dashboard.html (Rs 1,999)
- background-verification.html (variable)

Each needs full stack: migration + credit key + engine + route + frontend.

### Progress: 10 of ~17 C7 templates shipped this session

### Deferred to Session 7
- lms.html
- silent-killer.html
- skill-twin.html (needs persistence - AA4d)
- university.html
- legacy-shift.html

### External (deferred)
- #3 PayPal live capture test
- Rotate PayPal + SYNC keys
- scripts/_*.py cleanup
- ARCHITECTURE.md static section refresh

---

## Session 7 queue (2026-09-30)

### Headline item: hosted booking page

The Marketing AI Outreach Kit generates a `booking_link` that currently
points at `https://www.charvakit.com/contact?ref={slug}` — a dead-end
because the contact page doesn't read the `ref` param. The link has no
product behind it yet.

Build the real hosted page:

**Public route:** `GET /booking/{slug}` — no auth required.
- Reads charvak_marketing_booking_kits by slug
- Renders: "You are booking a {meeting_type} with {host_name} from
  {business_name}", agenda preview, and a request form
- Form fields: prospect name, email, preferred time (text for now),
  notes

**Request endpoint:** `POST /api/booking/{slug}/request`
- Saves to new table `charvak_booking_requests`
  (request_id, slug, kit_id, host_email, prospect_name, prospect_email,
   preferred_time, notes, status, created_at)
- Sends host notification email (host email = the kit's email)
- Sends prospect confirmation email
- Returns {status, request_id}

**Template:** `templates/booking.html` — clean, minimal, mobile-first.
- Reads kit data server-side
- 404 if slug doesn't exist
- Handles "already requested" gracefully

**Scope decision:** no calendar integration in Session 7. The host
emails the prospect back with a time. Real slot-picking is Session 8
if the product needs it.

**Est: 2-3 hrs.**

### Also in Session 7

Complete the remaining C7 templates:
- team-dashboard.html (Rs 1,999 Pro)
- background-verification.html (variable)
- lms.html
- silent-killer.html
- skill-twin.html (needs persistence — AA4d)
- university.html
- legacy-shift.html

### Deferred indefinitely (external)

- #3 PayPal live capture test
- Rotate PayPal + SYNC keys
- scripts/_*.py cleanup
- ARCHITECTURE.md static-assets section refresh

---

## Session 6 COMPLETE (2026-09-30)

Batch 2b-4 shipped (background-verification). Session 6 fully closed.

### Total C7 progress: 13 of ~17 templates

**Session 6 alone shipped 10 templates + 3 supporting backends:**

Batch 1 (`3e0cbb5`):
- developer-entropy, ai-slop, design-token, geo-compliance, agency-twin, reverse-staffing

Batch 2a (`b616466`):
- Backends: geo contract, geo hiring, reverse-staffing subscribe

Batch 2b-1 (`d1d21df`): bridge
Batch 2b-2 (`e06ed30`): marketing-ai
Batch 2b-3 (`9330804`): team-dashboard
Batch 2b-4 (pending): background-verification

### New tables (9 total this session)

- charvak_bridge_premium_reports
- charvak_marketing_booking_kits
- charvak_team_subscriptions
- charvak_geo_compliance_contracts
- charvak_geo_compliance_hiring
- charvak_reverse_staffing_subscriptions
- charvak_auditbot_fixes (session 3)
- charvak_auditbot_subscriptions (session 3)
- charvak_lock_in_engagements (session 4)

### New credit keys (26+)

bgv_identity, bgv_education, bgv_employment, bgv_credit, bgv_criminal,
bgv_complete, bridge_premium, marketing_booking_kit, team_pro_subscription,
geo_contract, geo_hiring, reverse_staffing_subscription, auditbot_fix,
auditbot_continuous, lockin_migration, lockin_protection...

### Security fixes

- 3 team routes gated (create/invite/get)
- 1 background-verification route gated
- Bug fixed: /api/team/invite collision (email was auth + member email)

### Frontend bugs fixed

- marketing-ai: 2 broken free tools (undefined authToken/email)
- team-dashboard: 2 broken free tools (undefined authToken)
- team-dashboard: dead upgradeTeam() handler removed
- background-verification: dead startVerification() replaced with real
- All C7 templates now have XSS-safe esc() rendering

### What's left (Session 7)

**Headline:** hosted booking page (see Session 7 queue earlier)

**Remaining C7 templates (~4-5):**
- lms.html
- silent-killer.html
- skill-twin.html (needs persistence)
- university.html
- legacy-shift.html

**External:**
- #3 PayPal live test
- rotate PayPal + SYNC keys
- scripts/_*.py cleanup

### Files touched this session: ~40

---

## Session 7 COMPLETE (2026-09-30) - Booking page + C7 cleanup

### Shipped

**1. Hosted booking page (Session 7 headline)** - `6399d2f`
- Public GET /booking/{slug} renders a page for any Marketing AI
  outreach kit
- POST /api/booking/{slug}/request captures prospect requests
- Emails host + prospect on request
- New table charvak_booking_requests
- Marketing AI kit now returns a real booking link (was a dead-end)
- Host dashboard on marketing-ai.html shows incoming requests

**2. Silent-Killer honesty rewrite** - `5919305`
- Removed 3 misleading product claims ("24/7 monitoring",
  "Instant alerts", "Auto-hotfix") that didn't have backend support
- Added a real "Notify Me When Continuous Monitoring Ships" button
- Free on-demand scan still works unchanged
- Session 8 will build the real scheduler

**3. Skill-Twin AA4d - full badge system** - `d875705`
- Phase A: skill-twin results now persist to charvak_skill_twin_results
- Phase B: real badge purchase (100 credits), idempotent, no double-charge
- Phase C: public verify page /badge/{badge_id} + API
- Phase D: rewired skill-twin.html + skill-check.html + badge.html
- SECURITY: /api/badge/issue was completely open; now admin-only
- Fixed a money bug: idempotency check swallowed exceptions and charged
  anyway. Now fails closed.

**4. LMS course enrollment** - (this commit)
- Reuses charvak_courses catalog (25 courses)
- Real enroll flow, tier-based credits (200 standard / 1000 premium)
- Public catalog dropdown + "Your Enrollments" list
- Idempotent, no double-charge

### What's left of the whole system

**C7 templates:** 15 of ~17 done across sessions 3-7.
Remaining: university.html, legacy-shift.html

**Session 8 queue:**
1. Silent-Killer continuous monitoring (cron + alerts) - ~4-6 hrs
2. University.html paid tier - ~2 hrs
3. Legacy-Shift.html migration tier - ~2 hrs
4. Full doc pass on 4 trackers - ~30 min
5. Hygiene: scripts/_*.py cleanup, git gc, ARCHITECTURE.md refresh
6. #3 PayPal live test - ~30 min

**Deferred / external:**
- Rotate PayPal + SYNC keys
- Premium Report product (8-12 hrs, product decision)
- FYP feature roadmap (7 items, ~8 hrs)
- Response object references in main.py that could be Response classes
  (spotted during Silent-Killer; not fixed)
