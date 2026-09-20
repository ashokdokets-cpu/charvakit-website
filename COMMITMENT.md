# Charvak — Commitment Tracker

**Purpose:** Track every planned-but-not-completed item. Nothing gets lost again.
**Created:** 2026-09-20
**HEAD at creation:** `600e295`

---

## 🔴 CRITICAL — Must Fix

### C1 — Assessment AI for global languages

- **Discovered:** 2026-09-20 (audit was wrong; corrected 2026-09-20)
- **Reality:** `global_config.LANGUAGES` has **34 languages** ✅ (config is complete)
- **Real gap:** `indian_language_ai._generate_questions` only handles 12 Indian languages
  - Spanish, French, German, Japanese, etc. users get English assessment questions
- **Action:** Extend `_generate_questions` to handle all 34 languages via AI
- **Est:** ~1.5 hr
- **Target:** Session G1

### C2 — `voice_to_web_engine.py` persistence

- **Discovered:** 2026-09-20 (was flagged as B-2, never executed)
- **Issue:** 5 in-memory stores (`websites`, `domains`, `updates`, `support_tickets`, `seo_configs`)
- **Action:** Design tables + migration + refactor + test
- **Est:** ~1 hr
- **Target:** Session B-2

### C3 — RTL UI support

- **Discovered:** 2026-09-20 (base.html has `<html lang="en">` hardcoded)
- **Issue:** Arabic users see LTR layout despite `dir="rtl"` in language config
- **Action:** Add dynamic `dir` attribute + RTL CSS
- **Est:** ~1.5 hr
- **Target:** Session G4

### C4 — Adaptive difficulty

- **Discovered:** 2026-09-20 (no `user_ability` table)
- **Issue:** Marketing claims "adaptive learning" but every user gets same difficulty
- **Action:** Add `charvak_user_ability` table + Elo-style logic
- **Est:** ~2 hr
- **Target:** Session G2

### C5 — Curated question banks

- **Discovered:** 2026-09-20 (`charvak_aiqg_question_cache` has 0 rows)
- **Issue:** Assessments depend entirely on live OpenAI calls
- **Action:** Pre-generate 200 questions per top 5 exams
- **Est:** ~2-3 hr
- **Target:** Session G3

### C6 — Assessment UI translations

- **Discovered:** 2026-09-20 (no i18n framework)
- **Issue:** Assessment pages show English regardless of user language
- **Action:** Add i18n framework + translate assessment UI
- **Est:** ~1.5 hr
- **Target:** Session G5

---

## 🔍 NEEDS VERIFICATION

### V1 — Doc sprawl
- **Check:** List all .md files in root
- **Concern:** Duplicates may exist (KNOWN-ISSUES vs FINAL-STATUS, etc.)
- **Action:** Verify next audit

### V2 — whatsapp_bot.py JSON mode — FALSE ALARM

- **Discovered:** Line 60 uses `response_format="text"` — but this is
  `audio.transcriptions.create` (Whisper), NOT chat completions.
  Text format is correct for Whisper.
- **Line 89** (the only LLM call) uses JSON mode correctly.
- **Verdict:** ✅ No bug. No action needed.

### V3 — 34-language claim vs delivered
- **Check:** Count actual supported languages
- **Concern:** Site copy says 34; actual may be less
- **Action:** Either add languages (G1) or fix copy

---

## ✅ CONFIRMED BY DESIGN (no action)

| # | Item | Verified |
|---|---|---|
| D1 | `dynamic_role_engine.create_dynamic_training_plan` stateless | 2026-09-20 |
| D2 | `ai_internship_engine.submit_work` random score placeholder | 2026-09-20 |
| D3 | `role_manager` + `dynamic_role_engine` parallel by design | 2026-09-20 |
| D4 | `record_survey_response` counter-only | 2026-09-20 |
| D5 | `admin_role_manager` used in main.py:6131 | 2026-09-20 |

---

## 📅 SCHEDULED

| # | Item | When |
|---|---|---|
| #53 | Delete charvakit-new-OLD folder | 2026-09-22 |

---

## 🔒 BLOCKED

| # | Item | Blocker |
|---|---|---|
| #65 | whatsapp_bot.py full fix | Meta registration |

---

## 📋 EXECUTION ORDER (revised 2026-09-20)

1. **Session B-2** — voice_to_web persistence (C2) ~1 hr  ← START HERE (closes persistence)
2. **Session G1** — Assessment AI for 34 languages (C1) ~1.5 hr
3. **Session G4** — RTL UI (C3) ~1.5 hr
4. **Session G2** — Adaptive difficulty (C4) ~2 hr
5. **Session G3** — Question banks (C5) ~2-3 hr
6. **Session G5** — Assessment i18n (C6) ~1.5 hr

**Total: ~9.5-10.5 hr across 6 sessions**

---

## PROCESS COMMITMENT

**To prevent future slips:**

1. **Every session is documented** before starting (in this file)
2. **After every session**, status is updated here
3. **Never let a promised item silently disappear** — flag it in this file immediately
4. **Verification audits** every N sessions to catch gaps
5. **Session-CONTEXT.md** links here for fresh chats

---

**Last updated:** 2026-09-20
**Next update:** after Session G1
