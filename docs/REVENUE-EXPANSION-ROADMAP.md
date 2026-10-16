# Revenue Expansion Roadmap

**Created:** 2026-10-17
**Status:** Flagged, sequential build
**Estimated impact:** Rs 4-6L/month within 6 months

---

## Executive Summary

15 revenue streams assessed. 4 recommended for immediate build.
Each reuses 60-80% of existing Charvak infrastructure.

---

## Tier 1 - Build Next (Sessions 45-49)

### Session 46 - Institutional Credit Bundles

**What:** Coaching centers buy bulk credits as branded vouchers for their students.

**Reuses:** `charvak_user_credits`, Razorpay/PayPal, `resolve_public_price`.

**New:**
- `charvak_bulk_credit_purchases` table
- `charvak_voucher_codes` table
- Redeem endpoint
- Partner dashboard

**Effort:** 1 session (~5 hrs)
**Revenue ceiling:** Rs 1.5L/mo at 10 active partners

---

### Session 47 - Verified Work Certificate

**What:** After completing a paid micro-internship, students pay Rs 149 for a
cryptographically signed "Verified Work Certificate" for LinkedIn.

**Reuses:** Micro-internship engine, escrow, certificate pattern, LinkedIn share.

**New:**
- Certificate type: "verified_work"
- Public verify URL
- Rs 149 checkout flow

**Effort:** 2 sessions
**Revenue ceiling:** Rs 75K/mo at 500 certs/mo

---

### Session 48 - Telegram Micro-Assessment Bot

**What:** Users send voice notes / essays to a Telegram bot. Bot responds with
IELTS Band / Versant Score in <30s. Rs 99/week subscription.

**Reuses:** `ielts_engine`, `cbt_versant`, Whisper, payment rails.

**New:**
- `python-telegram-bot` integration
- Webhook route `/telegram/webhook`
- `charvak_telegram_sessions` table
- Subscription billing

**Effort:** 2 sessions
**Revenue ceiling:** Rs 20K/mo at 200 subscribers

---

### Session 49 - Voice-to-Web Website Bundles

**What:** Fixed $299-799 price for "speak → 48hr live site" service.

**Reuses:** `voice_to_web_engine`, `neural_wireframe`.

**New:**
- Order table `charvak_website_orders`
- Team notification flow
- Client progress portal

**Effort:** 2 sessions + designer partner
**Revenue ceiling:** Rs 2.3L/mo at 10 sites/mo

---

## Tier 2 - Build When Justified

### Continuous Compliance Subscriptions
- **Trigger:** 3+ potential customers verbally commit
- **Effort:** 4 sessions
- **Revenue:** Rs 80K/mo at 20 customers

### Pay-per-Interview Screening
- **Trigger:** 3+ employers ask for AI pre-screening
- **Effort:** 5 sessions
- **Revenue:** Rs 42K/mo at 10 employers

### Campus Readiness Stakes
- **Trigger:** Legal review green-lights
- **Effort:** 3 sessions
- **Revenue:** Rs 4L/year
- **Risk:** Regulatory (gambling rules) - needs legal opinion

### Mock Drive Battlegrounds
- **Trigger:** 1,000+ active mock users
- **Effort:** 5 sessions
- **Revenue:** Rs 6K/mo at 100 matches/day

### University Talent Index
- **Trigger:** Amrita pilot converts
- **Effort:** 5 sessions (Track C)
- **Revenue:** Rs 5L/year

---

## Tier 3 - Multi-Month or Blocked

- **EaaS White-Label API** (needs partner)
- **WhatsApp Bot** (Meta approval)
- **Employer ATS-lite** (out of scope)
- **AI Career Twin** (legal risk - job board ToS)
- **Human Expert Marketplace** (services business, not SaaS)

---

## The Strategic Insight

Charvak's competitive advantage is **breadth of existing infrastructure**.
Every high-priority stream reuses 60-80% of what already exists.

The bottleneck is not engineering. It's **distribution**:
- Coaching centers need to be found and sold to
- Employers need to be cold-outreached
- Students need to be reached via social or SEO

**Recommendation:** Ship the 4 Tier-1 streams, then hire/partner a
partnerships person to handle the distribution side.

---

**Keep this doc in sync as streams ship.**
