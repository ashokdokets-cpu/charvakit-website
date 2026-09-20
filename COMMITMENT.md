# Charvak — Commitment Tracker

**Purpose:** Track every planned-but-not-completed item. Nothing gets lost again.
**Created:** 2026-09-20
**Last updated:** 2026-09-21
**HEAD:** `c3dc68a`

---

## ✅ COMPLETED

### C1 — Assessment AI for global languages

- **Completed:** 2026-09-21 (Session G1) — commit `c3dc68a`
- **Discovered:** 2026-09-20 (audit was wrong; corrected 2026-09-20)
- **Reality:** `global_config.LANGUAGES` has 34 languages ✅ (config complete)
- **Real gap fixed:** `indian_language_ai._generate_questions` only handled 12 Indian languages.
  Spanish, French, German, Japanese, etc. users got English/Hinglish assessment questions.
- **What shipped:**
  - `LANG_NAME_FOR_PROMPT` (36 languages) for AI prompt naming
  - `LANG_META()` resolver: INDIAN_LANGUAGES → global_config.LANGUAGES → fallback
  - Silent-Hindi bug fixed in BOTH `create_assessment` AND `translate_job_ad`
  - Static fallback guard: non-Indian returns `[]` instead of Hinglish default
  - `_generate_questions_via_ai` now serves all 34 languages
- **Verified:** live OpenAI smoke test — es/fr/ja/ar/zh/hi/te/ta/ko/de all
  returned native-script questions (5 each)
- **Note:** `_generate_questions_static` deliberately still covers only 12 Indian
  languages. Non-Indian + AI failure returns `[]`, so caller falls back explicitly.

---

## 🔴 CRITICAL — Must Fix

### C2 — `voice_to_web_engine.py` persistence

- **Discovered:** 2026-09-20 (was flagged as B-2, never executed)
- **Issue:** 5 in-memory stores (`websites`, `domains`, `updates`, `support_tickets`, `seo_configs`)
- **Action:** Design tables + migration + refactor + test
- **Est:** ~1 hr
- **Target:** Session B-2
- **Status:** SKIPPED on 2026-09-21 in favor of C1. Re-schedule per priority.

### C3 — RTL UI support

- **Discovered:** 2026-09-20 (base.html has `<html lang="en">` hardcoded)
- **Issue:** Arabic users see LTR layout despite `dir="rtl"` in language config
- **Action:** Add dynamic `dir` attribute + RTL CSS
- **Est:** ~1.5 hr
- **Target:** Session G4  ← NEXT

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
- **Status:** ✅ RESOLVED 2026-09-21 — `global_config.LANGUAGES` has 34 languages,
  and as of Session G1 `indian_language_ai._generate_questions` serves all of them
  via AI. Copy claim is now accurate for the assessment flow.

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

## 📋 EXECUTION ORDER (revised 2026-09-21)

1. ~~**Session B-2**~~ — voice_to_web persistence (C2) ~1 hr  [SKIPPED — user chose G1 first]
2. ~~**Session G1**~~ — Assessment AI for 34 languages (C1) ~1.5 hr  ✅ DONE 2026-09-21
3. **Session G4** — RTL UI (C3) ~1.5 hr  ← START HERE
4. **Session G2** — Adaptive difficulty (C4) ~2 hr
5. **Session G3** — Question banks (C5) ~2-3 hr
6. **Session G5** — Assessment i18n (C6) ~1.5 hr

**Remaining: ~8.5-9 hr across 5 sessions** (C2 still pending, not in this sequence)

---

## 🧠 PROCESS LESSONS LEARNED

### L1 — PowerShell + Python file patching is fragile (Session G1, 2026-09-21)

Three automated patch attempts failed before a manual edit succeeded:

- `Out-File -Encoding UTF8` (PowerShell 5.x) prepends a BOM, which broke
  byte-level string anchors in the patcher script
- `Measure-Object -Line` and `Out-String` fold/wrap UTF-8 content at console
  width, producing wrong line/char counts (reported 354 lines when the file
  had 390; reported 17,575 chars when the file was 19,806 bytes)
- Manually pasted here-string payloads silently lost leading whitespace and
  trailing commas, producing `IndentationError` and `SyntaxError`
- Hand-typed base64 payload introduced typos (`LANGUAGESS`) and dropped commas

**Reliable path forward:**
- For source edits containing non-ASCII (Devanagari, Tamil, etc.), use
  **Notepad (manual edit)** — verified working in Session G1
- For file-state questions, trust **`git diff --exit-code`** over any
  PowerShell string measurement
- Always `git diff` before commit and `git push` after — git is the durable backup

### L2 — Pager stalls in terminal scripts

`git diff` without `--no-pager` opens `less` and blocks non-interactive scripts.
Recommended: `git config --global core.pager ""` on Windows.

### L3 — Preserve `.bak` files until AFTER the commit is pushed

Session G1 deleted all `.bak` backups before the final commit.
Nothing was lost because git tracked the change, but the safety margin was thin.
**Rule: delete `.bak` files only after `git push` succeeds.**

---

## PROCESS COMMITMENT

**To prevent future slips:**

1. **Every session is documented** before starting (in this file)
2. **After every session**, status is updated here
3. **Never let a promised item silently disappear** — flag it in this file immediately
4. **Verification audits** every N sessions to catch gaps
5. **Session-CONTEXT.md** links here for fresh chats

---

**Last updated:** 2026-09-21
**Next update:** after Session G4