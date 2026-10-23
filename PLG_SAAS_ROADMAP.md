# PLG SAAS TRANSFORMATION — MASTER ROADMAP

**Flagged:** 2026-10-24 (Session 81 close)
**Status:** FLAGGED — ready to execute when trigger fires
**Purpose:** Full strategic analysis + phased execution plan to convert
Charvakit from a hybrid consulting business into a self-driven,
product-led growth SaaS platform.

**TL;DR:** Platform is 60% ready. Missing pieces are ~20 sessions of work.
Focus on B2B University SaaS (10-20x better ROI than B2C). 
Do NOT try to build all three streams simultaneously.

---

## THE HONEST CURRENT STATE (as of 2026-10-24)

### What's Ready (60%)
- Credit system (live)
- One-time payment infra (Razorpay + PayPal live)
- Employer network v0.3 (public page, referral, signup, admin approval)
- University admin approval portal
- Proof Dashboard backend (aggregated cohort data, Dean PDF)
- Engagement Dashboard (streaks, badges, leaderboard)
- All AI engines (IELTS, Versant, Career Assessment, etc.)
- 3-pillar homepage positioning

### What's Missing (40%)
| Gap | Criticality | Effort |
|---|---|---|
| Marketing engine (no traffic) | **CATASTROPHIC** | Ongoing |
| Recurring billing (no Razorpay Subscriptions) | **CRITICAL** | 5 sessions |
| Google OAuth / SSO | HIGH | 2 sessions |
| Auto-topup + trial-to-paid | HIGH | 3 sessions |
| Self-serve college signup | HIGH | 3 sessions |
| Dynamic paywalls | MEDIUM | 3 sessions |
| Programmatic SEO | MEDIUM | 3-4 sessions |
| API monetization | LOW | Skip |
| Affiliate network | LOW | Skip |
| Campus ambassadors | MEDIUM (sales, not code) | Manual |

**Total missing:** ~20 sessions

---

## THREE REVENUE STREAMS — HONEST ASSESSMENT

### A. B2C Micro-Transactions (Pay-As-You-Go)

**What it is:** Auto-recurring ₹199-499/mo credit packs + ₹499-999 instant certification fees

**What's missing:** UPI Autopay, auto-charge logic, certification payment gate

**Effort:** 5-6 sessions

**Revenue reality:**
- Theoretical: ₹1L/mo at 500 paying users
- **You have 674 monthly users total**
- Requires 7x user growth (2-3 years) before meaningful revenue
- **Ceiling at current traffic: ₹5-10K/mo**

**Verdict:** Risk. Build later.

### B. B2B SaaS Subscription (Colleges + Employers) ⭐ BEST

**What it is:** 
- University subscriptions (₹25K-2L/yr × 10-50 universities)
- Employer subscriptions ($49-199/mo × 20-50 employers)

**What's missing:** Self-serve college signup, recurring billing, tier enforcement, proof dashboard UI, employer paid tier

**Effort:** 8 sessions

**Revenue reality:**
- 10 universities × ₹50K/yr = **₹5L/year**
- 20 employers × ₹5K/mo × 12 = **₹10L/year**
- Combined realistic: **₹15L/year** with 3-6 months of sales

**Verdict:** ⭐ **Best ROI. Build first.**

### C. Developer & Institutional APIs

**What it is:** White-label IELTS/Versant AI scoring API, $0.10/evaluation

**What's missing:** Public API endpoints, API key management, per-call billing, developer docs portal, sandbox

**Effort:** 9 sessions

**Revenue reality:**
- No existing customers
- 6-12 months of developer marketing required
- $1K/mo at 1 paying customer

**Verdict:** Low priority. Skip until 50+ paying customers ask.

---

## THE CRITICAL INSIGHT: MARKETING ENGINE

**The document's biggest assumption:** Users exist. **They don't.**

Current traffic: ~674 monthly users. To reach 5,000 paying B2C users requires 7x growth. At current organic growth rate (100-200/mo), that's 24-36 months away.

**Options:**
1. **Build B2B instead** (10 university sales = ₹5L vs 5,000 B2C sales = ₹10L, but B2B takes 3 months not 2 years)
2. **Invest in marketing** (~₹20-50K/mo for ads + content + SEO) — requires capital
3. **Both** — focus B2B, seed B2C marketing in parallel

**Reality:** If you don't have ₹20-50K/mo marketing budget, B2C is off the table.

---

## RECOMMENDED 90-DAY PLAN

### Month 1: Foundation (8 sessions)
1. **Google OAuth** (~2 sessions) — instant signup reduces friction
2. **Razorpay Subscriptions + auto-topup** (~3 sessions) — infrastructure for all recurring revenue
3. **Auto-topup flow** (~2 sessions) — trigger charge when credits hit 0
4. **Tier enforcement** (~1 session) — real access control per plan

### Month 2: B2B Deals (10 sessions)
5. **Self-serve college signup + instant payment** (~3 sessions)
6. **Proof Dashboard UI** (~3 sessions) — the artifact TPO shows Dean
7. **Employer paid tier** (~2 sessions) — charge for candidate access
8. **Referral tracking UI** (~2 sessions) — TPO referral status pipeline

**In parallel — Sales:**
- Close Amrita
- Reach out to 20 more universities
- Close 3-5 more

### Month 3: Marketing + First Paying Customers
9. **Programmatic SEO** for top 20 exam pages (~2 sessions)
10. **Dynamic paywalls** on IELTS/Versant (~2 sessions)
11. **Referral bonus program** (~2 sessions)

**In parallel — Sales:**
- Sign 5-10 university contracts
- Sign 10-20 employer accounts
- **Target: ₹5L-15L ARR**

**Total:** ~20 sessions of build + intense sales.

---

## WHAT I'D ACTUALLY BUILD FIRST (Concrete)

If we start today:

**Session 82:** Google OAuth — Sign in with Google
- Google Cloud project setup
- OAuth2 flow
- `/login` page with "Sign in with Google" button
- Account linking for existing users

**Session 83:** Razorpay Subscriptions
- `charvak_subscriptions` table
- Subscribe endpoint (`/api/subscriptions/create`)
- Cancel/upgrade endpoints
- Subscription status webhook

**Session 84:** Auto-topup + trial management
- `charvak_trial_state` table
- Auto-charge trigger (cron)
- Trial expiry → conversion flow
- Dunning email sequence

**Session 85:** Self-serve college signup
- `/college/signup` public form
- Instant payment + access
- College admin dashboard

**Session 86-88:** Proof Dashboard UI
- Client-facing dashboard (auth-gated)
- Dean PDF on-demand
- Weekly auto-email

**Session 89-90:** Employer paid tier
- `charvak_employer_subscriptions` table
- Candidate access enforcement
- Employer dashboard with paid gating

**Session 91:** Referral tracking UI
- TPO referral status updates
- Candidate notification emails
- Status dashboard

**Session 92:** Email onboarding sequence
- Welcome → Day 3 → Day 7 → Day 14
- Trial expiry reminders
- Reactivation emails

**Session 93:** Referral bonus program
- ₹100 per signup (from existing `charvak_referrals`)
- Automated payout flow

**Then: STOP BUILDING. START SELLING.**

---

## WHAT TO SKIP FOR NOW

### Skip until triggered:
- **API monetization** (skip until 50+ paying customers ask)
- **Affiliate network** (skip until 10K+ users)
- **Campus ambassadors** (skip until 3+ colleges signed)
- **B2C auto-topup** (skip until 2K+ users)
- **Programmatic SEO** (skip until 3 paying customers)
- **Dynamic paywalls** (skip until 1K+ users)

### Why? Each is 3-9 sessions of work with zero revenue impact until user base grows.

---

## THE 4 QUESTIONS I ASKED (still unanswered)

These determine the whole plan. When you're ready to execute, answer:

1. **Which path to build first?** (Google OAuth / Razorpay Subscriptions / Self-serve B2B / Proof Dashboard UI)

2. **Do you have budget for marketing?** (~₹20-50K/month for ads)

3. **Are you willing to do 20+ sales calls in 90 days?** (university outreach)

4. **What's your realistic runway?** (months of cash on hand)

**Based on answers:**
- **Budget + runway + sales willing:** Go full 90-day plan above
- **No budget + short runway:** Focus 100% on B2B (15 sessions, 3 sales)
- **Budget + no runway:** B2C marketing first, monetize later

---

## WHEN TO UNFREEZE THIS FLAG

**Trigger conditions (any of these):**

1. **Amrita signs** paid pilot → Start B2B infrastructure immediately
2. **5+ paying customers** using employer/university features → Scale up
3. **You have ₹50K+ budget** for 3 months → B2C + B2B parallel
4. **6+ months of runway** → Build full 90-day plan
5. **Sales team or partner** available → Focus on sales, we build
6. **First 3 college contracts signed** → Add employer subscriptions

**Do NOT start** until at least one trigger fires. Building without demand wastes sessions.

---

## WHAT TO DO WHILE WAITING

**Immediate (this week):**
- Rotate Render password (2 min)
- Send Amrita follow-up (5 min)
- Reach out to 3 more universities (30 min)

**Ongoing (weekly):**
- Post 2 LinkedIn posts about Charvak features
- Add 5 university contacts to outreach list
- Send 5 cold emails to potential employers

**Before unfreezing:**
- Get 3 more demos on calendar
- Have 1 college in paid negotiation
- Confirm ₹20K marketing budget OR commit to 20 sales calls

---

## PROGRESS TRACKING

**Status as of 2026-10-24:**
- [x] Analysis complete (this document)
- [x] Three revenue paths assessed
- [x] 90-day plan drafted
- [x] Skip list defined
- [x] Trigger conditions established
- [ ] Marketing budget confirmed
- [ ] Sales willingness confirmed
- [ ] Runway confirmed
- [ ] First trigger fires
- [ ] Build begins (Session 82)

---

## RELATED FLAGS

- `INSTITUTIONAL-ROADMAP.md` — Phase A/B/C (currently 3/4 Phase A items shipped)
- `A4_LMS_BRIDGE_FLAG.md` — Deferred until institution asks
- `DEAN_REPORT_FRONTEND_FLAG.md` — Deferred until 1 paying client
- `COMMITMENT.md` — Full session history

---

## FINAL NOTE

**This is a strategic roadmap, not a task list.** Read it when:

1. You have a paying client and want to know "what next?"
2. You're considering a big feature and want to check alignment
3. You've hit a trigger and want the exact plan
4. You're pitching to investors and need the roadmap

**Don't read this to decide what to build tomorrow.** Read it to decide what to build **when you have demand**.

The best plan now: **Ship what's already built. Get first paying customer. Then execute this roadmap.**

---

**Last updated:** 2026-10-24
**Next review:** When trigger fires (Amrita signs OR 5+ paying customers OR 6 months of runway)