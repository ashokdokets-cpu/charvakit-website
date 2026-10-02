# Session Context - Charvak

**HEAD:** 585f21
**Last updated:** 2026-10-03 (Session 13 - Career Assessment Phase 3 shipped)
**Version:** 3.5-session-13-20261003

---

## Where we are

Session 13 shipped Career Assessment Phase 3: adaptive difficulty,
skill gap analysis, and AI-generated learning paths. The product is
now a real career coaching tool, not just a quiz.

**Commits this session:**
- `482d653` docs: Session 13 plan + scope boundary
- `fbc5852` docs: flag difficulty-aware ability update for Session 14
- `a585f21` feat(career-assessment): Session 13 Phase 3

### Shipped

**1. Topic tagging (7 role categories x 8 topics each):**
- Every question tagged with 1-2 topics at generation time
- Topics flow from prompt -> AI -> normalizer -> API response -> frontend

**2. Skill gap aggregation:**
- `_aggregate_skill_gap` groups answers by topic
- Blended score: (binary_correct_pct + avg_ai_score_pct) / 2
- Status: strong (>=80), mixed (55-79), weak (<55)
- Weakest-first sort in the response

**3. Cross-assessment adaptive baseline:**
- `_baseline_hint` reads ability_engine on /start
- Elo bands: <950 foundation-first, 950-1050 standard, >=1050 challenge
- Hint injected into prompt via _context_header ADAPTIVE HINT block
- Response includes baseline_used / ability_before / prior_attempts
- Frontend shows a badge when baseline_used != "baseline"

**4. Ability engine integration (first real use since C4):**
- `results_system.record_assessment_result(skill=f"career_{fmt}")` triggers
  the internal ability_engine.update_from_assessment call
- Row created on first /complete

**5. AI-generated learning path:**
- Lazy-loaded, cached in `charvak_career_assessments.learning_path_json`
- One OpenAI call: matches charvak_courses from the 25-course catalog,
  curates external resources, generates 2-4 week plan
- Route: GET /api/career-assessment/learning-path/{assessment_id}
- Free (bonus value; no credits charged)

### Verified E2E

Data Scientist / HealthTech / Mid, MCQ, 10 questions:
- baseline_used=baseline, topics present on every question
- 5/10 correct: score 50%, skill_gap 8 topics (6 weak/mixed, 2 strong)
- Learning path: 3 real courses (Data Science & ML, Python for Data
  Science, SQL & Database), 3 external resources (Coursera, Udacity),
  4-week plan
- Second start: baseline_used=standard, prior_attempts=1

### Scope boundaries (documented)

Phase 3 does NOT include:
- Retake comparison charts (future)
- Certificates/badges (Phase 4)
- Live mid-assessment adaptation (deferred)
- Peer benchmarking (Phase 4)

### Flagged for Session 14

1. **difficulty-aware ability update** - ability_engine supports
   difficulty= kwarg but nothing passes it. Fix: map level_key to
   difficulty_value (intern=600, mid=1000, senior=1400...).
   Est ~30 min.
2. **catalog coverage for niche roles** - no frontend System Design
   course exists in charvak_courses. Fix: expand catalog or refine
   matching. Est varies.

---

## Recommended next session (Session 14)

Three options:

**Option A - Session 14: Career Assessment Phase 2b (coding + SQL)**
Judge0 integration. Biggest remaining feature. Requires Judge0 API key.
~1-2 sessions.

**Option B - Session 9 quick wins** (~1.5 hrs):
- PayPal live capture test (.39 + refund) - deferred since Session B
- ARCHITECTURE.md static-assets refresh
- Doc pass on 4 trackers
- KNOWN-ISSUES: PowerShell process-kill + CRLF gotchas

**Option C - Close-out Session 13 fully + backup, then pick A or B later**

Recommendation: Option B first (clears nagging flags), then Session 14
(Phase 2b) with full attention.

---

## Career Assessment product status

| Phase | Status |
|---|---|
| Phase 1 (MCQ + catalog + persistence) | Shipped 2026-10-02 |
| Phase 2a (7 more formats) | Shipped 2026-10-02 |
| Phase 3 (adaptive + skill gap + learning paths) | Shipped 2026-10-03 |
| Phase 2b (coding + SQL via Judge0) | Session 14 |
| Phase 4 (certs, badges, benchmarking) | Future |

Full plan in CAREER-ASSESSMENT-PLAN.md.

---

## Environment

- HEAD: `a585f21`
- Local Python: 3.11.9 venv
- Local DB: Postgres 15 at localhost:5432
- Dev server: `uvicorn main:app --reload --port 8000`
- Prod: https://www.charvakit.com
- Render service: `srv-d9hhljd8nd3s73d2hoeg`