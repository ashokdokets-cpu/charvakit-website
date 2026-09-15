# Charvak IT Consulting — Project Status

**Last updated:** 2026-09-13
**Version:** v1.3-accessibility-20260913
**Live:** https://www.charvakit.com
**Status:** Tier 1 complete. Production-live, real users OK.

---

## Quick Links

- **Production:** https://www.charvakit.com
- **Render (Charvak):** https://dashboard.render.com — service `srv-d9hhljd8nd3s73d2hoeg`
- **Render (VouchAI):** service `srv-d9nque942hec7386q3mg`
- **GitHub:** https://github.com/ashokdokets-cpu/charvakit-website
- **Razorpay:** https://dashboard.razorpay.com
- **SendGrid:** https://app.sendgrid.com
- **Cloudflare:** https://dash.cloudflare.com

**Full docs:**
- `MASTER-REFERENCE.md` — comprehensive technical reference
- `ARCHITECTURE.md` — system architecture, flows, schema
- `PAGES-INVENTORY.md` — every template documented

---

## Infrastructure

| Layer | Where |
|---|---|
| App | Render (Singapore) — Python 3.11.9 + FastAPI + Uvicorn |
| Database | Render Postgres `dpg-d9m92j0ae00c73blvoq0-a`, db `vouchai` (shared with Dokets VouchAI) |
| CDN | Cloudflare |
| Email | SendGrid |
| Payments | Razorpay (INR) + PayPal (multi-currency) |
| AI | OpenAI GPT-4o-mini + ElevenLabs |

---

## Git Tags

| Tag | Meaning |
|---|---|
| `v1.3-accessibility-20260913` | **Latest** — Accessibility 69→90, Performance 42→52 |
| `v1.2-tier1-complete-20260913` | Tier 1 complete |
| `v1.1-stable-20260913` | Docs milestone |
| `v1.0-stable-20260911` | Pre-session stable |
| `v1.0.1-pre-fix-b` | Before Fix B |

## Latest Backup

`C:\Users\lenovo\OneDrive\Desktop\Charvak_Complete_Backup_20260913_195932.zip` (24.92 MB)

Contains: all source, templates, static, `.env`, `.git`, `scripts/`, master docs.

---

## Session 2026-09-12/13 — Summary

### 🔒 Security (P0 fixes)
- [x] **Fix A** — `/api/credits/purchase` now requires a verified, captured Razorpay payment for paid plans
- [x] **Fix B** — Credits persisted to Postgres (`charvak_user_credits`, `charvak_credit_usage_history`, `charvak_credit_purchases`)
- [x] **Fix C** — Razorpay webhook at `/webhook/razorpay` (abandoned-checkout safety net)
- [x] Render Postgres password rotated (Charvak + VouchAI)
- [x] Admin password rotated (old `CharvakAdmin@2026!` dead)
- [x] `RAZORPAY_WEBHOOK_SECRET` set on Render + local

### ⚡ Performance
- [x] `defer` on Razorpay, PayPal, Chart.js, Bootstrap JS
- [x] Preconnect to jsdelivr + Google Fonts
- [x] Google Fonts moved from `@import` to `<link>`
- [x] 1-year cache headers on `/static/*`
- [x] Hero image 418 KB → 71 KB
- [x] 8 more images compressed
- [x] **Performance: 42 → 52** (LCP 8.3s → 4.8s)

### ♿ Accessibility
- [x] 7 `aria-label` additions (selects, social links, user menu, WhatsApp)
- [x] Heading order fixed (`index.html`, `base.html`)
- [x] `aria-label` on Learn More / Read More links
- [x] **Accessibility: 69 → 90**

### 🧹 Content cleanups
- [x] Legal pages updated to September 2026
- [x] **Full mojibake repair** — all emojis, accents, arrows, currency symbols across all templates
- [x] `exam-prep.html` BOM stripped

### 🔍 SEO
- [x] `/sitemap.xml` now supports HEAD (was 405)
- [x] `/robots.txt` added with sitemap directive
- [x] Search Console: verified + sitemap Success
- [x] GA4 already installed (`G-HVHHD3KJ9G`)

### 🏷️ Documentation
- [x] `MASTER-REFERENCE.md` — technical reference
- [x] `ARCHITECTURE.md` — system architecture
- [x] `PAGES-INVENTORY.md` — template catalog

### 💰 Real-world verification
- [x] Real ₹99 payment completed on production
- [x] Webhook fired, idempotent no-op (correct behavior)
- [x] Credits granted + persisted + shown in UI

---

## Tier 1 — ✅ COMPLETE (10/10)

| # | Task | Status |
|---|---|---|
| 1 | End-to-end user journey test | ✅ |
| 2 | Enable email verification | ✅ |
| 3 | Test email templates | ✅ |
| 4 | Verify legal pages | ✅ |
| 5 | User journey test | ✅ |
| 6 | Real ₹1 payment test | ✅ |
| 7 | Mobile responsiveness | ✅ |
| 8 | Performance audit | ✅ |
| 9 | SEO basics | ✅ |
| 10 | GA4 + Search Console | ✅ |

---

## Tier 2 — In Progress

| # | Task | Status |
|---|---|---|
| 1 | Mojibake scan of templates | ✅ Done |
| 2 | Password strength enforcement | ⏳ Next |
| 3 | Rate limiting review | ⏳ |
| 4 | Backend health audit | ⏳ |
| 5 | Admin dashboard polish | ⏳ |
| 6 | Blog / case studies | ⏳ |
| 7 | Testimonials | ⏳ |
| 8 | STATUS.md maintain | ✅ Ongoing |

---

## Tier 3 — Nice to Have

- AI courses E2E
- Interview prep flow
- Micro-internship flow
- Job board flow
- Company patterns / mock drives
- University portal
- Enterprise features
- Analytics dashboards
- Referral / bounty system
- WhatsApp bot testing

---

## Known Issues

- **Heading order** — `index.html` and `base.html` fixed; other pages may still have issues
- **Contrast** — Lighthouse flags some text/background pairs
- **Buttons without accessible names** — icon-only buttons somewhere
- **TBT ~1,900 ms mobile** — deferred scripts fire in burst; needs conditional loading (deferred — risky for payments)
- **`.env` in backup ZIPs** — treat backup archives as sensitive
- **Root directory has ~30 one-off dev scripts** — cosmetic cleanup pending
- **PayPal client ID** — hardcoded in a few places (low priority)
- **503 files have UTF-8 BOM** — harmless (only `base.html` needed stripping)
- **SYNC_API_KEY / SYNC_API_SECRET** — hardcoded defaults in public repo. 
  Dokets RB integration callable by anyone who reads the repo. 
  Needs dual-key rotation + Dokets RB env var update. 
  Risk: medium (sync endpoints not critical but not private). 
  Deferred until we confirm Dokets RB's deployment location.

---

## Environment Variables

### Required on Render + local `.env`
DATABASE_URL (Render Postgres internal URL)
RAZORPAY_KEY_ID (rzp_live_...)
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET
PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET
SENDGRID_API_KEY
OPENAI_API_KEY
ELEVENLABS_API_KEY
SECRET_KEY (64 chars)
SITE_URL=https://www.charvakit.com
ADMIN_EMAIL=charvakit@gmail.com
HR_EMAIL=hr@charvakit.com