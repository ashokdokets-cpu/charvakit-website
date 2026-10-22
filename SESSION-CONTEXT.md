# Session Context - Charvak

**HEAD:** 701d220
**Live:** https://www.charvakit.com
**Updated:** 2026-10-22 (Session 73 closed — Resume Roast premium redesign complete)

---

## Session 73 CLOSED (2026-10-22) - Resume Roast Premium Redesign

**Commits:**
- dc5b175 feat(resume-roast): add intensity selector (clean/mild/savage)
- 1c1707c feat(resume-roast): premium UI + intensity selector + dynamic currency
- 14f0368 hotfix(resume-roast): remove MutationObserver infinite loop
- d1b5b8c fix(resume-roast): forward ?country= query param to price API
- 701d220 docs: Session 73 resolutions (KNOWN-ISSUES update)

### What shipped (all live on prod)

- 3-button intensity selector (Clean/Mild/Savage) with color-shift states
- Tone-mapped AI prompts (clean=mentor, mild=friend, savage=Ramsay)
- Hero redesign (gradient bg, amber pill, "Do You?", 4-stat row, 5k+ social proof)
- External CSS static/css/resume-roast.css (487 lines, cacheable)
- Dynamic currency (13 countries via ?country= override)
- Migration: charvak_resume_teasers.intensity TEXT DEFAULT 'mild'

### Verified on prod

- Default: Rs 99 (IN, tier_1, razorpay)
- US: $3.99 (tier_3, paypal)
- GB: £2.99 (tier_3, paypal)
- JP: ¥500 (tier_3, paypal)
- All 5x page hammering: 200 OK in 0.3-0.4s
- Pre-push 14/14 IELTS regression passed on every commit

### Root causes fixed this session

1. MutationObserver infinite loop (1c1707c bug) — observer watching
   document.body with {subtree: true} re-triggered on every .textContent
   write. Fixed in 14f0368 by removing the observer entirely.
2. Missing ?country= forwarding (introduced in 14f0368) — the fetch URL
   lost `+ window.location.search` during the IIFE rewrite. Fixed in
   d1b5b8c.

### Infra learnings documented

- Windows venv .Path display quirk (Get-Process.Path shows base python,
  not venv shim — NORMAL for Windows venvs)
- MMDB refresh (data/GeoLite2-City.mmdb stale > 7 days -> slow IP detection)
- Windows localhost IPv6 preference (use 127.0.0.1 in dev browser)
- Python 3.11 f-string same-quote-inside-{} limitation

### Repo state

- Working tree clean
- HEAD = origin/main = 701d220
- Prod verified live

---

## What's Next (Session 74)

**Recommended: Resume Roast Patches 3-4 (~60 min)**

Patch 3: Live activity ticker
- New endpoint GET /api/tools/resume-roast/recent (last 10, PII-masked)
- Frontend auto-scroll ticker below hero
- Social proof -> higher trust -> higher conversion

Patch 4: "Build a Better One" CTA
- Card after free result -> https://www.doketsrb.com/#builder
- Bridges B2C roast users to Dokets paid product

**Alternative: Close 3 dashboard flags (15 min total)**
- Rotate Render Postgres password (Session 19 flag)
- Send Amrita email to Prof. Raj (draft ready)
- Phase 3c GPT-4o-mini env flip (Nov 3 target)

**Alternative: Batch A8 Coding/SQL Certificate Extension**
- 2 sessions, ~4.25 hrs
- Uniform certification story

---

## Session 73 Retrospective

**Productive time:** ~3 hours of feature work
**Debug time:** ~5 hours (half real issues, half self-inflicted)

### Rules added to avoid next time

1. Never use MutationObserver with `subtree: true` on document.body
   when the callback writes .textContent. That mutation IS a childList
   mutation — infinite loop. Use direct DOM updates instead.

2. After ANY fetch rewrite, verify what fetch actually returns:
   fetch("/api/...").then(r=>r.json()).then(d=>console.log(d))
   Not what curl returns, not what HTML contains. What the browser's
   fetch receives. This is the ground truth.

3. `html.includes("MutationObserver")` matches COMMENTS too. False
   positives. Use `html.includes("new MutationObserver")` or check for
   `observer.observe` (the actual API call).

### Net result

Despite 5 hours of debugging, the session shipped:
- One full product feature (intensity selector)
- One full UI redesign (hero + CSS system)
- One full global feature (dynamic currency)
- Two real bug fixes (with permanent lessons)

Net: positive. Intensity selector alone moves B2C conversion meaningfully.