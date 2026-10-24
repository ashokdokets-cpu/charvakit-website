# NEXT SESSION PLAN - Charvak

**Created:** 2026-10-25 (Session 82 extended close)
**HEAD at creation:** 74feb96
**Priority:** Immediate next session

---

## Two Features to Build — IN THIS ORDER

### Feature 2 (BUILD FIRST) — Email Mismatch Auto-Link Flow

**Effort:** ~2 hrs
**Why first:** Smaller, self-contained, unblocks real DoketsRB sync UX
**Flag source:** COMMITMENT.md - 'Additional flags identified 2026-10-22 (deep audit)'

**Current problem:**
- User logs into Charvak with email A
- They also have DoketsRB account with email B
- Auto-sync between Charvak and DoketsRB fails silently on email mismatch
- No way to reconcile 'the same person has two emails'

**What to build:**
1. New table: charvak_email_link_requests (request_id, charvak_email,
   doketsrb_email, doketsrb_user_id, status, created_at, resolved_at)
2. Charvak-side endpoint: POST /api/sync/request-email-link
3. Charvak-side endpoint: POST /api/sync/confirm-email-link
4. Frontend UI in /career-center: banner showing 'Found DoketsRB account
   with different email X - is this you?' with Yes/No buttons
5. Update handle_pull to detect email mismatch and return
   {status: 'email_mismatch', next_action: 'confirm_link'}
6. E2E test: Charvak charvakit@gmail.com + DoketsRB contact@dokets.com
   -> trigger pull -> see banner -> confirm -> both linked

**Self-contained:** No DoketsRB-side changes required for MVP.
Future: DoketsRB can add /api/public?action=lookup-email for full auto-detect.

**Diagnostic to run first:**
  - Show current api_sync.py routes
  - Show current charvak_synced_users schema
  - Show current handle_pull implementation

---

### Feature 1 (BUILD SECOND) — Coding/SQL Certifications

**Effort:** ~3.5 hrs
**Why second:** Bigger, needs more testing, closes Tier 2 gap permanently
**Flag source:** CAREER-ASSESSMENT-PLAN.md 'Phase 4 Addition' + COMMITMENT.md 'Session 73 FLAGGED'
**Previous blocker:** Waited for 3 flags (Postgres rotation, Amrita email, GPT-4o env flip).
All 3 are now closed. Build is unblocked.

**Current problem:**
- 8 Career Assessment formats work (mcq, coding, sql, short_answer,
  numeracy, situational_judgment, behavioral, system_design, debugging, case_study)
- Career Certifications issue for MCQ and AI-scored formats
- Coding and SQL 'Get Certified' button is HIDDEN in ai-assessment.html

**What to build (Phase A - v1):**
1. Schema migration: add format, language, database_name, task_classes,
   runtime_info columns to charvak_career_certifications
2. New table: charvak_cert_task_classes (map format+language/database -> task classes)
3. Seed 30+ coding classes + 20+ SQL classes
4. Engine: _compute_task_classes() + _compute_runtime_info()
5. Update issue_certification() to accept format/language/database
6. Frontend: unhide Get Certified CTA for coding/sql
7. Certificate template: format-specific sections
   - Coding: 'Language: Python 3.11 | Runtime: Judge0 CE | Task classes: ...'
   - SQL: 'Environment: SQLite (approximate) | Task classes: ...'
7. PDF renderer: format-specific layout
8. API responses: include new fields
9. E2E test: coding cert + sql cert end-to-end

**Environment honesty:**
- v1 SQL is SQLite-based (Judge0 limitation)
- PostgreSQL/MySQL/MSSQL labeled 'SQLite-approximate' (honest disclosure)
- Languages supported in v1: Python, JavaScript, Java, Go, C++ (Judge0 CE)
- Languages to add: TypeScript, Ruby, PHP (deferred to v2)

**Diagnostic to run first:**
  - Show charvak_career_certifications schema
  - Show current 'Get Certified' CTA logic in ai-assessment.html
  - Show issue_certification signature in career_assessment_engine.py

---

## Order of Operations

1. Read this file first
2. Run diagnostic for Feature 2 (email mismatch)
3. Build Feature 2 (~2 hrs)
4. Commit + push Feature 2
5. Run diagnostic for Feature 1 (coding/sql certs)
6. Build Feature 1 (~3.5 hrs)
7. Commit + push Feature 1

**Total: ~5.5 hrs across one long session OR two sessions**

---

## Prompt for next session

Copy-paste this into the first message of the next chat:

    Resuming Charvak at HEAD 74feb96.
    Read NEXT-SESSION-PLAN.md - two features queued:
      1. Email Mismatch Auto-Link Flow (~2 hrs)
      2. Coding/SQL Certifications (~3.5 hrs)
    Run diagnostics for Feature 2 first, then build.

---