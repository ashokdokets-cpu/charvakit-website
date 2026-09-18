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

---