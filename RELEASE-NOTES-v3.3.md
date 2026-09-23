# Charvak — Release Notes v3.3

**Release date:** 2026-09-23
**Tag:** `v3.3-ielts-complete-20260923`
**Previous release:** `v3.0-tier3-complete-20260919`

---

## 🎉 Highlights

This release completes the **IELTS Academic suite** (all 4 sections), rebuilds **Versant** as a production-grade test, and lays the foundation for **user-driven content quality** on the exam question bank.

**You can now offer:**
- Complete IELTS Academic practice (Listening, Reading, Writing, Speaking)
- Full Versant English Assessment (6 sections, 5-criteria scoring)
- Cross-test results dashboard
- 138 Indian exam practice with a 12,500+ question bank

---

## ✨ What's New

### IELTS Academic — Complete Suite

**New pages:**
- `/ielts` — Hub with all 4 sections
- `/ielts-listening` — 14 sections with real TTS audio (4 section types)
- `/ielts-reading` — 9 passages across 3 difficulty tiers
- `/ielts-writing` — Task 1 + Task 2 with band scoring
- `/ielts-speaking` — Full 3-part audio test

**Each section offers:**
- AI band scoring on the 4 official IELTS criteria
- Instant feedback with sub-band scores
- Cross-test history integration

**Credit keys added:**
- `ielts_listening_section` (5), `ielts_listening_score` (10)
- `ielts_reading_passage` (5), `ielts_reading_score` (10)
- `ielts_writing_prompt` (3), `ielts_writing_eval` (15)
- `ielts_speaking_prompt` (3), `ielts_speaking_transcribe` (5), `ielts_speaking_eval` (15)

### Versant English Assessment — Full Rebuild

- **DB-backed** (was in-memory) with 2 new tables:
  - `charvak_versant_sessions`
  - `charvak_versant_answers`
- **6 sections** (Read Aloud, Repeats, Sentence Builds, Conversations, Story Retelling, Summary)
- **Whisper transcription** for audio answers
- **AI scoring** on 5 criteria (20-80 scale)
- Full frontend rewrite with one-question-at-a-time flow

### Cross-Test Results Dashboard

- New page: `/my-results`
- Shows all assessments: IELTS, Versant, exam practice, mock drives
- Filter by assessment type
- Details modal with sub-band breakdowns

### Currency Detection — Two-Layer Fix

- **Bug:** Indian users with `en-US` browser got USD pricing
- **Fix:**
  - **Layer 1:** Cloudflare `CF-IPCountry` header (auto-updated by CF)
  - **Layer 2:** Self-hosted GeoLite2 MMDB (weekly auto-refresh)
  - **Layer 3:** Accept-Language fallback
- **Verified:** Indian users now see INR reliably

### Exam Question Bank — Quality Improvements

- **Deterministic validator** — deleted 126 structurally broken questions
- **User report system** — any user can flag a broken question
- **Admin review page** — `/admin/reported-questions` for triage
- **Semantic dedup** — pgvector embeddings + cosine-distance filtering
- **Bank size:** 12,647 → 12,521 valid questions

### Navigation

- **Assessments dropdown:** All Assessments, IELTS (All Sections), IELTS Speaking, Versant English, Advanced Assessment
- **User menu:** Added "My Results" link
- **New pages:** `/consulting`, `/ielts`, `/ielts-listening`, `/ielts-reading`, `/ielts-writing`

### Marketing

- **Edtech-first homepage** — hero leads with IELTS/exams/Versant
- **Consulting page** — IT staffing/consulting moved to `/consulting`
- **IELTS hub copy** — clearer value prop and section descriptions

---

## 🐛 Bug Fixes

- IELTS Speaking persist call — fixed signature mismatch (`record_assessment_result`)
- Versant `get_session` — fixed duplicate `status` key that broke `complete_session`
- Whisper hallucination filter — rejects `. .` and non-English spam captions
- Line corruption in `main.py` — fixed a missing newline that broke `/api/ielts/speaking/evaluate`
- Nav dropdown — re-added `/ielts` (all-sections) link now that the page exists
- `.gitignore` — whitelisted production scripts that were accidentally ignored

---

## 🔒 Infrastructure

- **Connection pool:** `database.py` now supports `get_pooled_connection()` for hot paths
- **Pool warmup:** `main.py` warms the pool on startup
- **GeoLite2 auto-update:** `scripts/update_geoip.py` runs from a Render cron
- **Scripts whitelisted:** All seed/validate/review scripts now tracked in git

---

## 📊 By the Numbers

| Metric | Value |
|---|---|
| Total exams | 138 |
| Question bank | 12,521 validated questions |
| IELTS Listening sections | 14 |
| IELTS Reading passages | 9 |
| Versant sections | 6 |
| Supported languages | 34 |
| AI scoring criteria | 4 (IELTS), 5 (Versant) |
| Countries served | 50+ |

---

## 🔮 Coming Next

- Real backends for 18 template features (currently "Notify Me")
- IELTS General Training variant
- More Listening/Reading content batches
- Analytics dashboards
- Blog content for SEO

---

## 🔗 Links

- **Product:** https://www.charvakit.com
- **IELTS hub:** https://www.charvakit.com/ielts
- **Cross-test dashboard:** https://www.charvakit.com/my-results
- **Pricing:** https://www.charvakit.com/ai-credits-pricing

---

*Charvak — AI-powered exam practice, IELTS preparation, and IT consulting.*