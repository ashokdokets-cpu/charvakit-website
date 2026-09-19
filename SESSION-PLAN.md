# CHARVAK - SESSION-BY-SESSION EXECUTION PLAN

**Last updated:** 2026-09-20
**Current HEAD:** `40985bb`
**Version:** `v3.0-tier3-complete-20260919`
**Backlog file:** `OUTSTANDING-WORK-INVENTORY.md`

---

## COMPLETED SESSIONS

| Session | Scope | Status |
|---|---|---|
| A-J | 49 engines DB-backed, 8 AI JSON bugs fixed | OK |
| Tier E | Payment engine + 3 verifications | OK |
| K | 30 items (3 sec + 5 DI + 4 deferrals + 16 cleanup + 2 features) | OK |
| B-3 | notification_engine persistence | OK |
| B-4 | products_engine stateless verification | OK |
| H-2 | 13 items (cosmetic + housekeeping + docs) | OK |
| I | Capstone + v3.0 tag + backup | OK |
| A-1 | 20 top-traffic templates a11y | OK |
| A-1.2 | 73 templates a11y (static) | OK |
| A-1.3 | 24 templates a11y (JS-templated) | OK |
| #87 | Notification retention + Render cron | OK |
| #88 | job_service.py dead code removed | OK |
| Quick Wins | #40, #44, #64 | OK |

---

## REMAINING SESSIONS

### Session B-2 - voice_to_web Persistence (~1 hr)
- [ ] Audit voice_to_web_engine.py (5 in-memory stores)
- [ ] Design 1-2 tables
- [ ] Migration + apply
- [ ] Refactor engine methods
- [ ] Test E2E
- [ ] Commit + prod migration

**Milestone:** Persistence project 100% complete.

### Session A-2 - TBT Mobile Optimization (~2-3 hr)
- [ ] Lighthouse baseline measurement
- [ ] Rewrite polling loop at base.html line 30-45
- [ ] Conditional loading for Razorpay/PayPal/Chart.js (Jinja)
- [ ] Audit ~9 inline scripts in base.html
- [ ] Move heavy inline scripts to external deferred files
- [ ] Re-measure Lighthouse
- Target: TBT < 500ms (from ~1,900ms)

### Session F1 - Feature Gaps Small (~2 hr)
- [ ] #41 student_suite_engine.assist_assignment / assist_research (AI stubs)
- [ ] #43 advanced_assessment_engine._generate_versant_questions count mismatch
- [ ] #67 ai_question_generator.used_questions implement dedup

### Session F2 - Feature Gaps Large (~2-3 hr)
- [ ] #42 na_module/vector_matcher.SKILL_EMBEDDINGS -> pgvector
- [ ] #66 indian_language_ai.py - 8 more language questions

### Session #86 - Product Audit Trail Feature (~3 hr)
- [ ] Design charvak_product_results table
- [ ] Migration + apply
- [ ] INSERT in 11 product methods
- [ ] Read endpoint /api/products/results
- [ ] Admin UI to view results
- [ ] Test + commit

**Decision required:** Is this feature wanted?

### Session Optional - Product-Driven (varies)
- [ ] #59 RazorpayX integration
- [ ] #60 AI Products real integrations
- [ ] #61 Enterprise public pages
- [ ] #62 Per-level curriculum audit
- [ ] #63 International EMI via PayPal
- [ ] #65 WhatsApp (blocked on Meta)

**Decision required:** Product priorities.

---

## NOT DOING (Documented Reasons)

### Scheduled
- #53 Delete old charvakit-new-OLD folder - 2026-09-22 (3 days after rename)

### Automatic
- #87 Cron runs weekly - no manual action

### Won't Fix
- ~48 templates (admin, includes, tools, blog, base.html)
- Inline label headings (non-structural)
- Vendored waypoints.min.js mojibake
- Emoji in log messages (documented in DOC-STYLE.md)

### Deferred By Design
See DEFERRALS.md for 8 items with rationale + escalation triggers.

### Blocked
- #65 whatsapp_bot.py AI JSON bug - awaiting Meta number registration

---

## PROGRESS TRACKER

    Total backlog (at start):     ~90 items
    Completed:                    ~84 items  (93%)
    Remaining actionable:         ~8 items   (~10-12 hr)
    Remaining product-driven:     ~15 items  (varies)
    Blocked:                       1 item
    Non-actionable:               ~30 items

    Path to "actionable complete": ~10-12 hr across 6 sessions

---

## RECOMMENDED SESSION ORDER

1. B-2 (voice_to_web)       - ~1 hr     - closes persistence project
2. A-2 (TBT)                - ~2-3 hr   - real performance win
3. F1 (feature gaps small)  - ~2 hr     - half of feature gaps
4. F2 (feature gaps large)  - ~2-3 hr   - remaining feature gaps
5. #86 (audit trail)        - ~3 hr     - new capability
6. Optional                 - product-driven

---

## KEY FILES

| File | Purpose |
|---|---|
| OUTSTANDING-WORK-INVENTORY.md | Master backlog |
| DEFERRALS.md | 8 design decisions |
| SCHEMA.md | 128 tables auto-generated |
| SESSION-CONTEXT.md | Resume pointer |
| STATUS.md | Session log |
| DOC-STYLE.md | Style guide |
| KNOWN-ISSUES.md | Bug registry |
| TIER3-PERSISTENCE-PROJECT.md | Persistence + verified skip list |
| SESSION-PLAN.md | This file |

---

## RESUME OPENER (paste into fresh chat)

> Resuming Charvak work. HEAD is <git rev-parse HEAD>. Sessions A-J, K, H-2, I, B-3, B-4, A-1/A-1.2/A-1.3, #87, #88, Quick Wins complete. See SESSION-CONTEXT.md for state, and SESSION-PLAN.md for the remaining sessions plan. Starting Session <letter>: <scope>.

---

## MILESTONES

- OK v3.0-tier3-complete-20260919 - Released 2026-09-19
- OK a1.3-complete-20260919 - Accessibility hierarchy complete
- Target v3.1-features-YYYYMMDD - After next feature sessions
