# Charvak — Release Notes v3.4

**Release date:** 2026-09-23
**Previous release:** `v3.3-ielts-complete-20260923`

---

## 🎉 Highlights

This release focuses on **product polish, admin tooling, and content marketing**. The IELTS suite from v3.3 is now complemented by a unified blog, a real analytics dashboard, admin moderation tools, and an edtech-first marketing homepage.

---

## ✨ What's New

### Marketing & Positioning

- **New edtech-first homepage** — hero leads with "Practice smarter. Score higher." and 3 clear CTAs (Take a free IELTS test / Practice 138 exams / See pricing)
- **New `/consulting` page** — IT staffing and consulting moved to its own focused page; homepage retains a compact business strip
- **IELTS hub copy** — dual-column info block explaining section specifics and what users get per session

### Blog & Content (SEO foundation)

- **New markdown-based blog** at `/blog` with 8 published posts:
  - **3 edtech (IELTS)**: IELTS vs TOEFL, IELTS Speaking with AI, Writing Task 2 structure
  - **5 consulting (recovered)**: AI in IT staffing, US work visas for Indian developers, remote hiring best practices, bridging skill gaps, escrow payments
- **Full infrastructure**:
  - `blog_engine.py` — markdown frontmatter parser + HTML renderer
  - `/blog/rss.xml` — RSS feed
  - `/api/blog/posts`, `/api/blog/{slug}` — JSON endpoints
  - Canonical templates under `templates/blog/`

### Admin Analytics Dashboard

- **New page** at `/admin/analytics` with real, DB-backed metrics:
  - **6 KPI cards**: Total Users, Verified, Active 7d, Revenue, Credits Sold, Tests Taken
  - **User funnel visualization**: Registered → Verified → Took Test → Purchased, with conversion rates
  - **IELTS usage breakdown** by section (Listening, Reading, Writing, Speaking) with bar chart
  - **Top assessments by usage** table
  - **Question bank health**: total, reviewed, reported with review percentage
- **6 new API endpoints** under `/api/admin/metrics/*`
- **Link from main admin-dashboard** to the new analytics page
- **Retry logic** for transient pool issues in query execution

### Admin Moderation

- **New reported-questions page** at `/admin/reported-questions`:
  - Lists all user-reported questions with reporter, reason, timestamp
  - Actions: **Dismiss** (clears the flag) or **Delete** (removes from bank)
  - Tested end-to-end in production

### IELTS Page Polish

- **`/ielts-writing`** — richer intro with 4 criteria cards, updated Task toggle labels
- **`/ielts-listening`** — section tabs now show question counts; each section shows a description that updates on click
- **`/ielts-reading`** — 3 difficulty-tier cards, exam strategy list, tab counts
- **Richer section metadata** in `/api/ielts/sections`: `content_type`, `total_questions_available`, and accurate counts

---

## 🐛 Bug Fixes

- **Blog post rendering** — HTML content was showing as raw text; fixed with `|safe` filter and proper blog-content styles
- **Blog consolidation** — removed duplicate nav link and 2 orphan templates
- **Recovered 5 blog posts** that had been stored as hardcoded data in an earlier `blog_engine.py` and lost when the file was refactored

---

## 🔧 Infrastructure

- **New script**: `admin_metrics_engine.py` (176 lines) — DB-backed analytics
- **Whitelisted scripts** in `.gitignore`: `seed_ielts_listening.py`, `seed_ielts_reading.py`, `review_questions.py`, `validate_questions.py`, `ai_verify_questions.py`
- **BOM handling**: consistent UTF-8 no-BOM writes across new files

---

## 📊 By the Numbers

| Metric | Value |
|---|---|
| Blog posts | 8 |
| IELTS sections | 4 (Listening, Reading, Writing, Speaking) |
| IELTS Listening sections seeded | 14 |
| IELTS Reading passages seeded | 9 |
| Question bank size | 12,518 questions |
| Admin analytics KPIs | 6 |

---

## 🔮 Coming Next

- More blog posts (targeting 20+ for full SEO footprint)
- Real backends for the 18 Category-B feature templates
- IELTS General Training variant
- Advanced user-cohort analytics
- Chart.js visualizations on the analytics dashboard

---

*Charvak — AI-powered exam practice, IELTS preparation, and IT consulting.*
