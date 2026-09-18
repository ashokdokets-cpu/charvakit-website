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
