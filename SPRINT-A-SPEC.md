# Sprint A Spec — Free Role Readiness Certificate

**Created:** 2026-10-04
**Target sessions:** 2-3
**Status:** Ready to execute
**Depends on:** Nothing — can ship immediately
**Reference:** `COMPETITIVE-STRATEGY.md` for the strategic context.

---

## Deliverable

Any user completes a Career Assessment and receives a **free, shareable, verifiable
Role Readiness Certificate** at a public URL. No premium gate. No payment.

The certificate is the acquisition artifact. Every share puts `charvakit.com/readiness/...`
in front of an audience. It is the top of the funnel for Premium Reports,
matched jobs (Sprint B), and employer outreach (Sprint C).

## Success Criteria

- A user can complete the flow from `/readiness-check` to certificate in under 6 minutes
- The certificate URL is public, cacheable, and shareable on LinkedIn / WhatsApp
- Each certificate has a short verification hash that employers can check
- `charvak_readiness_certificates` fills with rows on every completion
- The certificate uses the same PDF engine as Premium Reports (consistent branding)

---

## Readiness Score Formula

Weighted blend of five components:

| Component | Weight | Source |
|---|---|---|
| Binary correct % | 30% | `charvak_career_assessment_answers.is_correct` |
| AI-scored continuous avg | 25% | `ai_score` field, AI-scored formats only |
| Skill-gap closure | 20% | Phase 3 `_aggregate_skill_gap` (strong=100, mixed=70, weak=40) |
| Ability baseline percentile | 15% | `ability_engine.get_ability` vs cohort seed |
| Difficulty adjustment | 10% | Level-aware (intern 0.85 to executive 1.15) |

Final score = round(sum of weighted components), clamped to 0-100.

### Percentile computation

Percentile is computed against the benchmark set for (role x industry x level).
Benchmarks come from `benchmarks/role_readiness.json` — a curated file with
~200 entries covering the most common role/level combinations. Default fallback
is 65 if no benchmark exists for the specific combo.

### Benchmark file structure

```json
{
  "default": 65,
  "benchmarks": [
    {"role": "Data Scientist", "industry": "HealthTech", "level": "mid", "benchmark": 72},
    {"role": "Data Scientist", "industry": "*", "level": "mid", "benchmark": 70},
    {"role": "*", "industry": "*", "level": "mid", "benchmark": 68}
  ]
}
```

Resolution order: exact match -> wildcard industry -> wildcard role -> global default.

---

## Database Table

New table `charvak_readiness_certificates`. Migration:
`migrations/20261005_readiness_certificates.sql`.

```sql
CREATE TABLE IF NOT EXISTS charvak_readiness_certificates (
    certificate_id    TEXT PRIMARY KEY,
    assessment_id     TEXT NOT NULL,
    email             TEXT NOT NULL,
    display_name      TEXT,
    role              TEXT NOT NULL,
    industry          TEXT NOT NULL,
    level             TEXT NOT NULL,
    readiness_score   INTEGER NOT NULL,
    percentile        INTEGER,
    benchmark_score   INTEGER,
    verdict           TEXT,
    payload_json      JSONB,
    certificate_hash  TEXT NOT NULL,
    source            TEXT NOT NULL DEFAULT 'written',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_rdc_email ON charvak_readiness_certificates (email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rdc_hash ON charvak_readiness_certificates (certificate_hash);
CREATE INDEX IF NOT EXISTS idx_rdc_assessment ON charvak_readiness_certificates (assessment_id);
```

### Field notes

- `certificate_id` — format `RDC-<12 hex uppercase>`, URL-safe
- `assessment_id` — references `charvak_career_assessments.assessment_id`
- `display_name` — optional; falls back to first name + last initial derived from email
- `payload_json` — full snapshot: skill_gap, per-topic scores, answered count, time taken
- `certificate_hash` — HMAC-SHA256 of `certificate_id + email + readiness_score + created_at`, using `SECRET_KEY`. Truncated to 16 chars for readability. Used by `/verify/{hash}` for employer-side verification.
- `source` — `written` (Sprint A) or `voice` (Sprint D). Same table, different origin.

---

## API Contract

### POST /api/readiness/generate

**Auth:** `require_auth_for_email(request, email)`

**Request body:**
```json
{
  "email": "user@example.com",
  "assessment_id": "CA-XXXX-XXXX",
  "display_name": "Priya S."
}
```

**Response (success):**
```json
{
  "status": "success",
  "certificate_id": "RDC-A1B2C3D4E5F6",
  "certificate_url": "/readiness/RDC-A1B2C3D4E5F6",
  "certificate_hash": "a3f9b21c4e8d0f12",
  "readiness_score": 78,
  "percentile": 72,
  "benchmark": 70,
  "verdict": "Above benchmark - job ready"
}
```

**Errors:**
- `401` — missing auth
- `403` — assessment does not belong to caller
- `404` — assessment not found or not completed
- `409` — certificate already exists for this assessment (returns the existing one)

**Idempotency:** One certificate per `assessment_id`. Second call returns the existing certificate.

### GET /api/readiness/{certificate_id}

**Auth:** None (public)

**Response:** full certificate payload including `payload_json`. Used by the
public `readiness.html` page.

**Rate limit:** `60/minute` per IP.

### GET /api/readiness/verify/{certificate_hash}

**Auth:** None (public)

**Response:**
```json
{
  "valid": true,
  "certificate_id": "RDC-A1B2C3D4E5F6",
  "role": "Data Scientist",
  "level": "mid",
  "readiness_score": 78,
  "issued_at": "2026-10-04T15:30:00",
  "candidate_display": "Priya S."
}
```

Used by employers who want to verify a certificate they received in an email.
Returns only non-PII fields (candidate display name is truncated).

### GET /api/readiness/list/{email}

**Auth:** `require_auth_for_email(request, email)`

**Response:** list of the user's certificates (without `payload_json` for size).

---

## Frontend Pages

### /readiness-check — Public Free Landing

New template: `templates/readiness-check.html`

**Structure:**
- Hero: "Get your Verified Role Readiness Score in 5 minutes"
- 3-step visual: Pick role -> Answer 10 questions -> Share your certificate
- Form: role dropdown, industry dropdown, level dropdown
- "Start Free Check" button
- No login required to view this page

**On submit:**
- Login gate: if no auth token, redirect to `/login?next=/readiness-check`
- After login, POST to `/api/career-assessment/start` with size=`quick`, format=`mcq`
- Question flow: identical to `ai-assessment.html` Step 2
- On completion: POST to `/api/readiness/generate`, then redirect to `/readiness/{id}`

**Reuse:** Most of the assessment UI already exists in `ai-assessment.html`. The
public landing is a lighter wrapper — smaller hero, no format picker, no size picker.

### /readiness/{certificate_id} — Public Certificate

New template: `templates/readiness.html`

**Structure:**
1. Header: Charvak logo, "Verified Role Readiness"
2. Hero card: candidate display name, role x industry x level
3. Big score: 78 out of 100, with percentile ring
4. Benchmark comparison bar: "You: 78, Benchmark: 70, Percentile: 72"
5. Skill gap chart: Chart.js horizontal bar of per-topic scores
6. Verdict band: "Above benchmark - job ready" (color-coded)
7. Verification footer:
   - Certificate ID: RDC-A1B2C3D4E5F6
   - Verification hash: a3f9b21c4e8d0f12 (copy button)
   - Verify URL: charvakit.com/api/readiness/verify/a3f9b21c...
   - QR code (SVG, generated inline — no external service)
8. Action buttons:
   - "Download PDF" — reuses `pdf_engine.render_simple_pdf`
   - "Add to LinkedIn" — linkedin.com/profile/add?startTask=CERTIFICATION_NAME
   - "Share on WhatsApp" — wa.me/?text=...
   - "Retake" — links to /readiness-check
9. Footer CTA: "Take your own free readiness check" -> /readiness-check

**Design principles:**
- The page is a public artifact. Treat it like a marketing page, not a dashboard.
- Above-the-fold score is the hero. Everything else is supporting detail.
- Include Charvak branding but not heavy navigation — this page will be seen by people who have never heard of Charvak.
- The `readiness-check` CTA at the bottom is the acquisition loop.

### Frontend changes to existing pages

**templates/ai-assessment.html:**
- After completion (Step 3 result), add a green button: "Get your Verified Readiness Certificate"
- Links to `/api/readiness/generate` (POST from JS), then redirects to `/readiness/{id}`

**templates/my-results.html:**
- Add a new filter pill: "Readiness"
- Fetch readiness certificates alongside other results
- Show certificate cards (role, score, download button, view certificate link)

**templates/base.html:**
- Add "Readiness Check" to the top nav (between "Assessments" and "Training")
- Public-facing — visible when logged out too

---

## Engine Method — compute_role_readiness

New method in `career_assessment_engine.py`:

```python
def compute_role_readiness(self, assessment_id: str, email: str) -> Dict:
    """
    Compute the Role Readiness Score for a completed assessment.
    Returns {status, readiness_score, percentile, benchmark, ...}.
    Idempotent: returns existing certificate if one exists.
    """
    # 1. Load assessment, verify ownership + completed status
    # 2. Load answers from charvak_career_assessment_answers
    # 3. Compute binary_correct_pct
    # 4. Compute ai_scored_avg (only AI-scored formats)
    # 5. Call _aggregate_skill_gap -> closure_pct
    # 6. Call ability_engine.get_ability(email, skill) -> percentile
    # 7. Look up benchmark from benchmarks/role_readiness.json
    # 8. Blend with weights [0.30, 0.25, 0.20, 0.15, 0.10]
    # 9. Generate certificate_id + certificate_hash
    # 10. Persist to charvak_readiness_certificates
    # 11. Return the certificate dict
```

Edge cases:
- Assessment is `in_progress` -> return `{status: error, message: "Assessment not completed"}`
- Fewer than 5 answers -> require minimum for statistical validity
- AI-scored formats with 0 AI scores -> reweight to binary-only
- Missing benchmark -> fall back to global default 65

---

## Test Plan

Eight checks, all run against the test-register user:

### T1 — Public landing renders
Load `/readiness-check` in an incognito window. No auth needed.
Confirm: role/industry/level dropdowns populate from `/api/career-assessment/options`.

### T2 — Free assessment starts
Select Data Scientist x HealthTech x Mid-Level. Click "Start Free Check".
Redirects to `/login` (because not authenticated). Login. Land back on the flow.
POST `/api/career-assessment/start` returns an assessment_id.

### T3 — Assessment completes
Answer 10 MCQ questions. Submit. Assessment status becomes `completed`.
Existing `/api/career-assessment/complete` route handles this — no change needed.

### T4 — Certificate generates
Click "Get your Verified Readiness Certificate".
POST `/api/readiness/generate` returns `status: success` with `certificate_id` + score.
Verify in DB: `SELECT * FROM charvak_readiness_certificates WHERE assessment_id = X`.

### T5 — Certificate page renders
Navigate to `/readiness/{certificate_id}`. Confirm:
- Score displayed (large, correct value from T4)
- Percentile + benchmark bars render
- Skill gap chart renders (Chart.js)
- QR code renders (SVG)
- Download PDF button works (generates a valid PDF)

### T6 — Verification works
GET `/api/readiness/verify/{certificate_hash}` returns `{valid: true, ...}`.
GET with a tampered hash returns `{valid: false}`.

### T7 — Idempotency
POST `/api/readiness/generate` a second time for the same assessment_id.
Returns the SAME certificate_id. No duplicate row in DB.

### T8 — Auth enforcement
POST `/api/readiness/generate` with a different user's email -> 403.
GET `/api/readiness/list/{other_email}` -> 403.
GET `/api/readiness/{certificate_id}` with no auth -> 200 (public read is fine).

---

## Risks + Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Benchmark data too sparse for niche roles | Medium | Global default 65 covers all missing cases; expand the JSON file over time |
| Percentile meaningless at low sample sizes | Medium | Show "provisional" label when < 50 certificates exist for the cohort |
| Public certificate URL leaks email | Low | Only expose display_name (first name + last initial); email is never in the public response |
| HMAC secret rotation invalidates old hashes | Low | Store certificate_hash at generation time; never regenerate |
| Idempotency race (two concurrent generate calls) | Low | UNIQUE constraint on assessment_id in the table prevents duplicates |
| Users game the score by retaking | Medium | One certificate per assessment_id; retakes create new assessments, which is fine (shows improvement) |

---

## Execution Checklist

### Session 17a — Engine + Table + Routes

- [ ] Migration `20261005_readiness_certificates.sql`
- [ ] Self-healing DDL in `career_assessment_engine._ensure_tables`
- [ ] `compute_role_readiness()` method
- [ ] `benchmarks/role_readiness.json` (seed 20 roles)
- [ ] `_resolve_benchmark()` helper
- [ ] `_generate_certificate_hash()` helper (HMAC via SECRET_KEY)
- [ ] POST `/api/readiness/generate` route
- [ ] GET `/api/readiness/{certificate_id}` route (public)
- [ ] GET `/api/readiness/verify/{certificate_hash}` route (public)
- [ ] GET `/api/readiness/list/{email}` route
- [ ] E2E test with test-register user: T2, T4, T6, T7, T8

### Session 17b — Frontend

- [ ] `templates/readiness-check.html` (public landing)
- [ ] `templates/readiness.html` (public certificate)
- [ ] Chart.js skill-gap chart in readiness.html
- [ ] Inline QR SVG generator (no external deps)
- [ ] PDF download wired to `pdf_engine.render_simple_pdf`
- [ ] "Add to LinkedIn" + "Share on WhatsApp" buttons
- [ ] `ai-assessment.html` — "Get Certificate" CTA after completion
- [ ] `my-results.html` — Readiness filter + cards
- [ ] `base.html` — Readiness Check nav link
- [ ] E2E browser test: T1, T3, T5

### Session 17c — Verify + Ship

- [ ] All 8 test cases pass
- [ ] Prod smoke test on charvakit.com
- [ ] Commit + push
- [ ] Update SESSION-CONTEXT with Sprint A complete
- [ ] Update COMPETITIVE-STRATEGY roadmap to mark Sprint A done

---

## Post-Sprint-A Follow-ups (do not do in this sprint)

- Employer-side certificate search (Sprint C preparation)
- Embed the certificate on the candidate profile page in `/career-center`
- Auto-email the certificate to the user after generation
- Print-friendly CSS for the certificate page
- Multi-language certificate render (Hindi/Telugu variants)

These are Sprint B and C concerns. Keep Sprint A focused.

---

## Success metric

Within 30 days of shipping:
- 100 certificates generated
- 30 certificates shared on LinkedIn or WhatsApp
- 5 employers reference a Charvak certificate in an email

If any of these are zero, revisit the frontend framing (Sprint A spec assumes the
artifact is share-worthy).

---

Keep this spec in sync as the sprint evolves.

