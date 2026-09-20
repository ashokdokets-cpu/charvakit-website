# Charvak - Session-by-Session Execution Plan

**Last updated:** 2026-09-20
**Current HEAD:** `0e62c17`
**Version:** `v3.0-tier3-complete-20260919`
**Progress:** ~99% complete (1 actionable item left)

---

## Session Status

### Foundation
| Session | Scope | Status |
|---|---|---|
| A | kyc, candidate, training, lms | ✅ |
| B (partial) | enterprise, ats | ✅ |
| C | events, career_v2, exam_prep | ✅ |
| D | messaging, profile_network, badge, university, brand | ✅ |
| E | final_year_project, student_suite, ai_internship, team | ✅ |
| F | outreach, marketing_ai, exam_analytics, dynamic_role | ✅ |
| G | 6 na_module engines | ✅ |
| H | 8 ephemeral engines | ✅ |
| I | capstone + v3.0 tag + backup | ✅ |
| J | 6 backlog engines (audit gap) | ✅ |
| Tier E | payment fix + 3 verifications | ✅ |

### Quality & Cleanup
| Session | Scope | Status |
|---|---|---|
| K (1-3) | 3 security fixes | ✅ prod-verified |
| K (4-8) | 5 data integrity fixes | ✅ prod-verified |
| K deferrals | 4 by-design decisions documented | ✅ |
| K dead fields | 16 cleanup items | ✅ |
| K features | 2 new persistence (lang_assessments, kiosk_events) | ✅ |
| B-3 | notification_engine persistence | ✅ |
| B-4 | products_engine verification | ✅ |
| H-2 | 13 items (cosmetic + housekeeping) | ✅ |
| A-1 | 20 top-traffic templates a11y | ✅ prod-verified |
| A-1.2 | 73 templates a11y (static) | ✅ prod-verified |
| A-1.3 | 24 templates a11y (JS-templated) | ✅ prod-verified |
| F1 | #41, #43, #67 | ✅ |
| F2 | #42, #66 | ✅ |
| A-2 | Polling loop, image dims, mobile CLS | ✅ prod-verified |
| Quick Wins | #40, #44, #64 | ✅ |
| #86 | Product audit trail | ✅ prod-verified |
| #87 | Notification retention + cron | ✅ live |
| #88 | Dead code cleanup | ✅ |

### AI Product Enhancements
| Session | Products | Status |
|---|---|---|
| #60-A | Lock-In Breaker | ✅ |
| #60-B | AuditBot | ✅ |
| #60-C | Design-Token Sentinel | ✅ |
| #60-D | 6 more products (Reverse Staffing, Skill Twin, Geo Compliance, AI Slop, Agency Twin, Dev Entropy) | ✅ |
| #62 | 75 course descriptions regenerated | ✅ prod-verified |

---

## Remaining Work

### Actionable (1 item, ~1 hr)
| # | Item | Est. |
|---|---|---|
| **B-2** | voice_to_web_engine.py persistence | ~1 hr |

### Product-Driven (4 items, decisions required)
| # | Item | Decision |
|---|---|---|
| #59 | RazorpayX integration | Is manual payout a pain point? |
| #61 | Enterprise public pages | Seed data decision needed |
| #63 | International EMI | Is there demand? |
| #65 | WhatsApp bot | BLOCKED — Meta registration |

### Scheduled (1 item)
| # | Item | When |
|---|---|---|
| #53 | Delete charvakit-new-OLD | 2026-09-22 |

### Won't Fix (~30 items)
- ~48 templates (admin, includes, tools, blog)
- 6 deferrals by design
- Vendored mojibake
- Inline label headings

---

## Session B-2 — Detailed Plan

**Goal:** Persist voice_to_web_engine.py (last remaining engine)

**Steps:**
1. Audit voice_to_web_engine.py (5 in-memory stores, ~7.5 KB)
2. Design 1-2 tables (voice_to_web_sessions, generated_sites)
3. Write migration + apply locally
4. Refactor engine methods to use DB
5. Test E2E
6. Commit + push
7. Apply migration on prod via Render Shell
8. Verify

**Deliverable:** Persistence project 100% complete.

---

## Infrastructure Verified (2026-09-20)

- ✅ 25 pages return 200 in prod
- ✅ 3 security fixes enforced (K/1, K/2, K/3)
- ✅ #86 audit trail auth-gated
- ✅ pgvector 0.8.1 active
- ✅ 7+ new prod tables
- ✅ 9 AI-enhanced products live
- ✅ Product audit trail logging
- ✅ Notification retention cron running

---

## Tags (10 created)

| Tag | Purpose |
|---|---|
| v3.0-tier3-complete-20260919 | Capstone release |
| a1-safety-checkpoint-20260919 | Before A-1 |
| a1-before-bulk-20260919 | Before A-1 bulk |
| a1.2-safety-checkpoint-20260919 | Before A-1.2 |
| a1.2-complete-20260919 | After A-1.2 |
| a1.3-complete-20260919 | After A-1.3 |
| a2-performance-20260920 | A-2 work |
| a2-revert-20260920 | A-2 revert |
| a2-complete-20260920 | A-2 complete |
| f1-features-20260920 | F1 features |

---

## Key Files

| File | Purpose |
|---|---|
| SESSION-PLAN.md | This file |
| SESSION-CONTEXT.md | Resume pointer |
| OUTSTANDING-WORK-INVENTORY.md | Master backlog |
| FINAL-STATUS-20260920.md | Status report |
| DEFERRALS.md | By-design decisions |
| SCHEMA.md | DB schema (128 tables) |
| KNOWN-ISSUES.md | Bug registry |
| DOC-STYLE.md | Code conventions |

---

## Next Session Priorities

1. **B-2** — voice_to_web persistence (~1 hr)
2. **Prod migration** for B-2 via Render Shell
3. **Product decisions** — #59, #61, #63
4. **#53 scheduled cleanup** — 2026-09-22

---

## Resume Opener

> Resuming Charvak work. HEAD is `0e62c17`. All sessions through #60-D, #62, F1, F2, A-1/A-1.2/A-1.3, A-2, K, H-2, I, B-3, B-4, #86, #87, #88 are complete and prod-verified. Only B-2 (voice_to_web persistence, ~1 hr) remains actionable. See SESSION-PLAN.md and FINAL-STATUS-20260920.md. Starting Session B-2.
