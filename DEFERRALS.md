# Charvak — Formal Deferrals (Session K)

**Purpose:** Document items that are intentional design decisions, not bugs.
**Policy:** Items listed here are acknowledged as "won't fix." If business requirements change, revisit using the noted "escalation trigger."
**Filed:** 2026-09-19 (Session K)
**Maintained by:** Update when any deferred item is revisited or resolved.

---
## #11 — dynamic_role_engine.create_dynamic_training_plan (stateless)

**File:** `dynamic_role_engine.py` line 236
**Filed as:** Training plan is returned but not persisted.

**Why it is by design:**
The method's own docstring states "stateless - plan is returned, not stored."
A training plan is a *recommendation* generated on demand. Persisting every
generated plan would bloat the database with throwaway output and create
stale plans whenever role definitions change.

**Behavior:**
Caller invokes with (email, role_id, weeks). Response contains the plan phases
and activities. Nothing is written to the DB. Caller decides what to do next.

**Escalation trigger:**
If product decides users should "enroll" in a plan and track completion
progress over time, a new feature is required:
- New table: `charvak_user_training_enrollments`
- New methods: `enroll(email, plan_id)`, `update_progress(enrollment_id, phase, status)`
This is a *feature*, not a bug fix. Do not silently add persistence to the
existing method.

**Verdict:** DEFERRED (by design)

---

## #12 — profile_network_engine.candidate_data (snapshot)

**File:** `profile_network_engine.py` line 93
**Filed as:** Candidate data is captured at network-creation time and goes stale
after profile updates.

**Why it is by design:**
The stored `candidate_data` is a point-in-time snapshot — analogous to a
business card collected at a conference. It is *intentional* that later
profile edits do not rewrite historical network entries. Live data would
require a JOIN at read time (slower, and semantically different).

**Behavior:**
When a network connection is created, the current candidate profile is
serialized into `candidate_data`. Future reads return the snapshot.
No auto-refresh exists.

**Escalation trigger:**
If product requires network contacts to always see the latest title/company,
two options:
- (a) Switch to a JOIN at read time: `SELECT c.* FROM candidates c JOIN network n`
- (b) Add an explicit refresh method that re-snapshots on demand

**Verdict:** DEFERRED (by design)

---
## #13 — university_engine.student_count (denormalized)

**File:** `university_engine.py` (CREATE TABLE line 34; increment line 165)
**Filed as:** student_count only increments; no decrement path exists.

**Why it is by design:**
There is no "remove student" flow in the product. Until that flow exists,
the counter is always accurate. Denormalization is deliberate — the counter
is read frequently (dashboards, listings) and a live COUNT(*) on a large
students table would be slower.

**Behavior:**
- On university creation: `student_count = 0`
- On student add: `SET student_count = student_count + 1`
- No decrement on any code path

**Escalation trigger:**
When a `remove_student` (or equivalent) method is added, it MUST include a
paired decrement:
UPDATE charvak_universities SET student_count = student_count - 1 WHERE ...
Alternatively, migrate to SELECT COUNT(*) FROM students WHERE university_id = %s
at read time. Pick one approach and use it consistently.

**Verdict:** DEFERRED (by design, contingent on no remove flow)

---

## #14 — ai_internship_engine.submit_work (random score)

**File:** `ai_internship_engine.py` line 287
**Filed as:** Submission score uses random.randint(7, 10) instead of real AI evaluation.

**Why it is by design:**
This is a placeholder awaiting real AI integration. The surrounding code
is fully DB-backed (enrollment lookup, INSERT with ON CONFLICT, etc.),
so the only stub is the score generation.

**Behavior:**
Every submission gets a random score in [7, 10]. Strengths/improvements
are static strings. No call to any AI provider.

**Escalation trigger:**
When AI evaluation budget is allocated, replace with an OpenAI call:
resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Evaluate this submission"}], response_format={"type": "json_object"})
feedback = json.loads(resp.choices[0].message.content)
The JSON output should have the same keys (score, strengths, improvements,
next_steps) so the calling code needs no changes.

**Verdict:** DEFERRED (placeholder for future AI integration)

---

## Summary

| # | Item | Verdict | Escalation Trigger |
|---|---|---|---|
| 11 | dynamic_role_engine stateless plan | DEFERRED | Product adds "enroll in plan" feature |
| 12 | profile_network candidate_data snapshot | DEFERRED | Product requires live title updates |
| 13 | university student_count denormalized | DEFERRED | remove_student method added |
| 14 | ai_internship random score | DEFERRED | AI evaluation budget allocated |

All 4 items are **intentional design decisions**. None are bugs. Documenting
here so the inventory can be cleaned up and future devs understand the why.

---## #30 — role_manager vs dynamic_role_engine (parallel custom-role stores)

**Files:** `role_manager.py`, `dynamic_role_engine.py`
**Filed as:** Two parallel custom-role stores, no consolidation.

**Why it is by design:**
These serve two distinct interfaces to the same underlying data:

- `role_manager.py` — **admin tooling**: `add_new_role`, `add_role_with_ai`,
  `get_role_details`. Lets administrators define new roles.
- `dynamic_role_engine.py` — **user-facing**: `analyze_skills_and_recommend`,
  `create_dynamic_training_plan`. Lets users discover roles matching their skills.

Both read from `charvak_dynamic_custom_roles`. The split is intentional — different
audiences, different validation, different UI routes.

**Escalation trigger:**
If the two engines start drifting (e.g., `role_manager` adds a role that
`dynamic_role_engine` can't see), THAT is a bug. Revisit if any inconsistency
appears between the two read paths.

**Verdict:** DEFERRED (by design - intentional separation of concerns)

---

## #35 — advanced_assessment_engine._generate_versant_questions (count mismatch)

**File:** `advanced_assessment_engine.py` line ~276
**Filed as:** Declared counts (e.g., 16) exceed static prompt lists (4).

**Why it is by design:**
The method caps iterating at `min(section["questions"], len(section_prompts))`.
If the section declares 16 questions but the static prompt list has 4, the loop
runs 4 times — safely. No error, no overflow.

The result is fewer questions than declared. This is a **content gap, not a
code bug** — the fix requires either:

- (a) A content writer adding more prompt items per section (to reach declared counts)
- (b) Lowering the declared count in the section config to match available prompts

**Escalation trigger:**
If product requires full question counts (e.g., 16 per section), assign content
writer to expand prompts. No code change needed.

**Verdict:** DEFERRED (content gap, not code bug)

---

## #37a — enterprise_engine.record_survey_response (counter-only)

**File:** `enterprise_engine.py` line ~622
**Filed as:** Increments counter but doesn't store respondent data.

**Why it is by design:**
The docstring says "matches original" — this behavior is intentional preservation
from an earlier in-memory version. The counter (`responses = responses + 1`)
is the requirement. Storing per-response data would need a new table and API.

**Escalation trigger:**
If product wants per-response data (analytics, filtering, export), add:
- New table: `charvak_enterprise_survey_responses`
- New column: `respondent_data JSONB`
- Modify `record_survey_response` to INSERT in addition to increment

**Verdict:** DEFERRED (by design - counter is the requirement)

---

## #37b — enterprise_engine.kiosk_check_in (dead parameter)

**File:** `enterprise_engine.py` line 678
**Filed as:** Accepts `student_id` but doesn't store it.

**Why this IS a real bug:**
Unlike 37a, `kiosk_check_in` receives `student_id` from the caller (`main.py:4032`
passes `data.get("student_id")`) but the engine never uses it. The response
message claims "Student {student_id} checked in!" but no record of the student
exists in the database — only the session's `check_ins` counter increments.

This means there is no audit trail of WHO checked in, only HOW MANY.

**Fix (scheduled with K/29 migration batch):**
- New table: `charvak_enterprise_kiosk_events`
  - `event_id TEXT PRIMARY KEY`
  - `kiosk_id TEXT NOT NULL`
  - `student_id TEXT NOT NULL`
  - `checked_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- Patch `kiosk_check_in` to INSERT an event row before incrementing the counter
- Keep the counter (for fast reads)
- Add index on `(kiosk_id, checked_in_at)` for reporting

**Escalation status:** SCHEDULED (not deferred indefinitely)

**Verdict:** DEFERRED to Session K-2 migration batch (real bug, needs table)

---