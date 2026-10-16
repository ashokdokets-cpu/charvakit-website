# Session 44-A3 — Localized Exam Funnels Plan

**Created:** 2026-10-16
**Status:** In progress
**Effort estimate:** ~5 hrs (accelerated from 7 by reusing A1.5 + 44-B infra)

---

## What this is

Ten SEO-optimized public landing pages, one per high-traffic state-PSC exam.
Each shows a free 15-question mock (no login), then offers a Rs 49
currency-aware unlock for the full 100-question mock.

**SEO target:** "{exam name} free mock test" + "{exam name} online
practice" + "{exam name} mock test in {language}".

## The 10 exams

| # | exam_id | Name | State | Language |
|---|---|---|---|---|
| 1 | uppsc_pcs | UPPSC PCS | UP | Hindi |
| 2 | mpsc_rajyaseva | MPSC Rajyaseva | Maharashtra | Marathi |
| 3 | rpsc_ras | RPSC RAS | Rajasthan | Hindi |
| 4 | wbpsc_wbcs | WBCS | West Bengal | Bengali |
| 5 | tnpsc_group1 | TNPSC Group 1 | Tamil Nadu | Tamil |
| 6 | kpsc_kas | KPSC KAS | Karnataka | Kannada |
| 7 | mppsc_sse | MPPSC SSE | MP | Hindi |
| 8 | gpsc_class12 | GPSC Class 1 & 2 | Gujarat | Gujarati |
| 9 | apsc_cce | APSC CCE | Assam | Assamese |
| 10 | kpsc_kerala | Kerala PSC KAS | Kerala | Malayalam |

## Free tier flow

1. Anonymous user lands on /free-mock/{exam_id}
2. Clicks "Start free mock - no login"
3. Backend creates anon token (anonymous_sessions.create_session)
4. Serves 15 questions (5 per section, 3 sections per exam)
5. User answers, submits
6. Backend scores, shows result + "Rs 49 for the full 100-question mock" CTA
7. Cert-share-link (uses A1.8 charvakShareUrl helper)

## Paid tier flow

1. Click "Unlock full mock - Rs 49"
2. POST /api/exam/free-mock/{exam_id}/unlock-order
3. Backend calls payment_engine.resolve_public_price("state_psc_full_mock", country)
4. Returns {amount_local, currency, gateway, razorpay_paise|paypal_amount, order_id}
5. Frontend opens Razorpay (INR) or PayPal (else)
6. Client confirms → POST /api/exam/free-mock/{exam_id}/unlock-run
7. Backend verifies payment, unlocks the full mock (100+ questions)
8. User takes the full mock in the same UI

## Files to touch

| File | Change |
|---|---|
| payment_engine.py | Add `state_psc_full_mock` to PUBLIC_PRICE_TABLE |
| exam_prep_engine.py | New `get_free_mock_questions(exam_id, sections=3, per_section=5)` |
| main.py | 4 new routes (page + 3 API) |
| templates/free-mock.html | New page template |
| templates/exam-prep.html | Add "Try free mock" CTA at top |
| sitemap.xml | Add 10 entries |
| migrations/ | New table `charvak_free_mock_results` |

## Reused infrastructure

- `anonymous_sessions.py` (A1.5) — no-login flow
- `payment_engine.resolve_public_price()` (44-B) — currency-aware pricing
- `charvakShareUrl()` (44-A1.8) — share tracking
- `exam_prep_engine._fetch_bank_questions()` — question source

## Success metrics

- 100 free mocks completed in first 30 days
- 10 Rs 49 unlocks in first 30 days
- 5% landing → free-mock-start conversion
- 10% free-mock → unlock conversion

## Not in scope

- Non-PSC state exams (police, TET) — Phase 2
- Voice-mode mocks — never
- Live proctoring — never

---

**Keep this doc in sync. It's the reference for the batch.**