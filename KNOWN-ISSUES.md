# Charvak — Known Issues Registry

**Created:** 2026-09-18
**Purpose:** Central registry for bugs, dead code, and design issues found during the persistence project. Every session appends to this file. Session I resolves what's still open.

**Legend:** 🔴 data integrity | 🟠 feature gap | 🟡 cosmetic | 🟢 hygiene

---

## Fixed (this project)

| Date | Session | File | Issue | Fix |
|---|---|---|---|---|
| 2026-09-18 | G/4 | `na_module/resume_engine.py` | PII phone regex had a capture group → `re.findall` returned empty strings → `replace('', ...)` inserted redaction marker between every character (86 chars → 1529 chars) | Non-capturing group `(?:...)` |
| 2026-09-18 | G/2 | `na_module/vms_connector.py` | `job_id = f"NA-JOB-{hash(str(raw_data))}"` — `hash()` randomized per process, IDs changed on every restart | `secrets.token_hex(4).upper()` |
| 2026-09-18 | G/4 | `na_module/resume_engine.py` | `vendor_id = f"VEN-{hash(...)}"` — same bug | `secrets.token_hex(4).upper()` |
| 2026-09-18 | E/4 | `final_year_project_engine.py` | AI methods called `json.loads(response.choices[0].message.content)` without `response_format`; GPT-4o-mini returned prose + markdown fences → `Expecting value: line 1 column 1` | `response_format={"type": "json_object"}` + defensive fence strip |
| 2026-09-17 | C | `main.py` | `GET /api/exam/progress` shadowed by `/api/exam/{exam_id}` catch-all | Routes inserted before catch-all |
| 2026-09-17 | C/3 | `exam_prep_engine.py` | Docstring said "83 exams" but actual catalog is 67 | Updated to 67 |

---

## Open — data integrity 🔴

| # | File | Line / Area | Issue | Fix in session |
|---|---|---|---|---|
| 1 | `na_module/revenue_engine.py` | `create_subscription` | Re-subscribe re-adds `monthly_fee` to `transactions` without adding a new subscription row. Revenue inflates silently on tier changes | TBD — product decision |
| 2 | `na_module/resume_engine.py` | `SubVendorManager.track_submission` | Duplicate `(vendor, candidate, job)` bumps `active_candidates` counter even though the row is deduped via `ON CONFLICT DO NOTHING` | TBD |
| 3 | `na_module/charvak_vms.py` | `approve_timecard` | Repeated approvals grow `approval_history` and overwrite `payment_reference` (no guard for already-approved state) | TBD |
| 4 | `migrations/20260916_course_payments.sql` | Foreign key | References `charvak_enrollments` which no migration creates. Fresh-clone / DR restore fails | Session I |
| 5 | `main.py` | `/api/exam/progress`, `/api/exam/history`, `/api/exam/study-plan` | No auth check — anyone can query any email's data | Security audit |
| 6 | `whatsapp_bot.py` | ~line 92 | AI JSON parsing bug (same as fixed in E/4) | When WhatsApp unblocks (external) |
| 7 | `ai_bridge_engine.py` | ~line 164 | AI JSON parsing bug (same as fixed in E/4) | Session H |

---

## Open — feature gaps 🟠

| # | File | Issue | Fix in session |
|---|---|---|---|
| 8 | `final_year_project_engine.py` | `total_projects` always returns 0 — `self.projects` was a dead field | Future feature work |
| 9 | `ai_internship_engine.py` | `submit_work` uses `random.randint(7,10)` for score | Product decision |
| 10 | `exam_prep_engine.py` | Icons changed from emoji to ASCII IDs — needs frontend mapping | When UI is built |
| 11 | `main.py` | Exam prep frontend mock-test UI doesn't exist (backend + routes live) | Dedicated UI session |
| 12 | `na_module/charvak_vms.py` | `vendor_performance` dead field — never written to | Future feature work |
| 13 | `student_suite_engine.py` | `assist_assignment` / `assist_research` return stubs — no real AI | Feature work |
| 14 | `na_module/vector_matcher.py` | `SKILL_EMBEDDINGS` is a small static dict; comment says "in production, use pgvector/Pinecone" | Future scaling |
| 15 | Analytics Dashboards | Never audited; page exists but no data source verified | Dedicated audit |

---

## Open — cosmetic 🟡

| # | File | Issue |
|---|---|---|
| 16 | Multiple engines | Heading order on remaining pages (accessibility) |
| 17 | Site-wide | TBT ~1,900ms mobile — needs conditional script loading |
| 18 | `na_module/vector_matcher.py`, `work_auth.py`, etc. | Emoji icons in some docstrings — clean up during Session I |

---

## Open — hygiene / process 🟢

| # | Item | Notes |
|---|---|---|
| 19 | Demo env vars must stay unset on prod | `CHARVAK_LOAD_DEMO_JOBS`, `CHARVAK_LOAD_DEMO_REVENUE`, `CHARVAK_LOAD_DEMO_VMS`. Add to deployment checklist |
| 20 | `na_module/` has no `__init__.py` | Works as namespace package but implicit. Consider adding |
| 21 | No migration runner | Engines use `_ensure_tables()` on import. Acceptable, but a real runner would be cleaner |
| 22 | `Out-File -Encoding utf8` writes BOM | Documented in DEV-SETUP.md; scripts strip it manually |
| 23 | PowerShell `python -c` + quotes | Documented in DEV-SETUP.md; always use temp `.py` files |
| 24 | PowerShell `curl.exe` + JSON body | Documented in DEV-SETUP.md; always use `--data-binary @file.json` |

---

## Rules for this file

1. **Every session appends to it** — if you preserve a bug, note it here.
2. **Fixed items move to "Fixed"** with date + fix reference.
3. **Session I sweeps it** and resolves open items or formally defers them.
4. **Keep it in git** so it survives across machines and sessions.
