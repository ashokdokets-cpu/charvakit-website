## Session 2026-10-13 - A1.8 + A1.9

### Shipped

- WhatsApp/LinkedIn share instrumentation across 4 templates
- Placement-prep promotion + UTM attribution
- 2 new helper functions in base.html
- 6 new GA4 events in the funnel

### Bugs fixed

- `readiness.html` share buttons were plain anchors; tracking
  wrapped in dead `rdOpenShare()` and never fired. Fixed.

### Next

- A2 (Certificate round 3) or A3 (FYP features)
- Or cleanup pass: rdOpenShare removal, PayPal E2E for A1.6

---

## Session 2026-10-13 - Session 43-A1.7

**HEAD:** `731b70a`

### Shipped

- IELTS Deep Report micro-paywall (Rs 99)
- 9 files changed, +1,885 / -1
- 4 new routes, new engine, new frontend, new PDF renderer

### Bugs fixed mid-session

- Country detection returning full names
- fpdf2 X-drift crash on multi_cell after cell
- EmailEngine.send_email signature mismatch
- PDF header showing "Charvak Premium Report"

### Next

- A1.8 (WhatsApp loop) or A2 (Certificate round 3)
- A1.6 country-code cleanup (5 min)
- Prod smoke test after deploy

---

# Charvak IT Consulting - Project Status

**Last updated:** 2026-10-12 (Session 43 - FYP MBA calibration + integrity fact panel)
**Version:** v3.5-session-43-20261012
**Live:** https://www.charvakit.com
**Status:** Track A active. Track B flagged.

## Session 2026-10-12 - Session 43

**HEAD:** 3fd8ad7

Two commits, four real fixes, one flagship feature.

### Shipped

- Integrity fact-panel certificate redesign (facts, not verdicts)
- FYP discipline-aware topic generation (MBA/commerce support)
- 8 MBA courses generated and promoted to public catalog
- MBA role calibration verified for 5 roles

### Commits

- e6daf79 — feat(integrity): fact-based certificate panel + reweighted classifier
- 3fd8ad7 — feat(fyp): discipline-aware topic generation - MBA/commerce support

### Site health

- 182 page routes: all 200 or legit redirect
- 155 API routes: all reachable
- 0 broken buttons
- 0 hidden elements without unhide logic
- 0 HTTP 500s

### Meeting prep

- Charvak-TPO-Demo folder with 7 PDFs on Desktop
- Amrita CDC meeting pending confirmation

### Next

See TRACK-A-B-PLAN.md for the full sequence.

**Track A batches:**
- A1: Small cleanup (45 min)
- A2: Certificate round 3 (1 session)
- A3: FYP features (1 session)
- A4: Personalized training views (1 session)
- A5: DoketsRB sync (2 sessions)

**Track B stages (after A2):**
- B1: Vocational calibration proof
- B2: CSR Assessment API
- B3: Pilot with one TP
- B4: First paid contract

**Estimate:** Track A ~6-7 weeks. Track B ~4-5 months.