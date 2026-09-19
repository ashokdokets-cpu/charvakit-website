# Charvak — Complete Outstanding Work Inventory

**State at time of writing:** HEAD b346012, reconciliation scan complete
**Engine count:** 59 total (54 root + 6 na_module - 1 dup in scripts/one-off)
**DB-backed:** ~46 confirmed via scan (49 claimed in docs, delta likely na_module + top-level modules)
**Pulled from:** KNOWN-ISSUES.md, TODO-MASTER.md, TIER3-PERSISTENCE-PROJECT.md, master docs
**Filed:** 2026-09-19
**Total line items:** ~77

---

## 🟡 PERSISTENCE — remaining engines

| # | Engine | Session | Est. | Notes |
|---|---|---|---|---|
| 1 | voice_to_web_engine.py | B-2 | ~1 hr | Last Tier A engine. Needs audit first — never read since 2026-09-17 audit (7.5 KB then) |
| 2 | whatsapp_bot.py | External block | — | Awaits Meta number registration. Also has AI JSON bug |

**Total:** 1 persistable + 1 external-blocked.

---

## 🔴 SECURITY

| # | Item | Session | Risk |
|---|---|---|---|
| 3 | ~~Auth check missing on /api/exam/progress, /api/exam/history, /api/exam/study-plan~~ **FIXED 2026-09-19** | K/1 | ~~High~~ DONE |
| 4 | ~~/api/payment/status returns razorpay_key_id + paypal_client_id + mode~~ **FIXED 2026-09-19** | K/2 | ~~Medium~~ DONE |
| 5 | ~~dynamic_role_engine.recommend_custom_role — anyone can add a global custom role~~ **FIXED 2026-09-19** | K/3 | ~~Medium~~ DONE |

---

## 🟠 DATA INTEGRITY

| # | File | Issue | Session |
|---|---|---|---|
| 6 | ~~revenue_engine.create_subscription re-subscribe inflates revenue~~ **FIXED 2026-09-19** | K/4 | DONE |
| 7 | ~~resume_engine.SubVendorManager.track_submission duplicate bumps counter~~ **FIXED 2026-09-19** | K/5 | DONE |
| 8 | ~~charvak_vms.approve_timecard repeat approvals grow history + overwrite payment_reference~~ **FIXED 2026-09-19** | K/6 | DONE |
| 9 | ~~outreach_engine.subscribe_premium / connect_gmail no UNIQUE — duplicates allowed~~ **FIXED 2026-09-19** | K/7 | DONE |
| 10 | ~~messaging_engine.get_stats.unread_messages excludes replied~~ **FIXED 2026-09-19** | K/8 | DONE |

---

## 🟢 FORMAL DEFERRALS

| # | File | Issue |
|---|---|---|
| 11 | ~~dynamic_role_engine.create_dynamic_training_plan~~ **[DEFERRED - see DEFERRALS.md]** | By design |
| 12 | ~~profile_network_engine.candidate_data~~ **[DEFERRED - see DEFERRALS.md]** | By design |
| 13 | ~~university_engine.student_count~~ **[DEFERRED - see DEFERRALS.md]** | By design |
| 14 | ~~ai_internship_engine.submit_work~~ **[DEFERRED - see DEFERRALS.md]** | Placeholder |

---

## 🟠 TIER 3 — genuinely outstanding

| # | Item | Session | Notes |
|---|---|---|---|
| 15 | Analytics Dashboards audit | Dedicated | Never scoped |
| 16 | University Portal FEATURE completeness | Dedicated | Feature gap |
| 17 | Exam prep frontend mock-test UI | Dedicated UI | Backend done |
| 18 | WhatsApp bot E2E | External block | — |
| 19 | ~~Backfill missing migrations/20260916_charvak_enrollments.sql~~ **FIXED 2026-09-19** - migration created (index ordering was the real issue, no FK) | DONE |
| 20 | ~~Fix 20260916_course_payments.sql FK ordering~~ **[STALE - no FK constraints in migration; original issue no longer exists]** | DONE |
| 21 | Session I capstone bundle | Session I | — |
| 22 | Tag v3.0-tier3-complete-YYYYMMDD | Session I | Release marker |
| 23 | Final backup | Session I | Durability |

---

## 🟡 DEAD FIELDS / COSMETIC BUGS

| # | File | Issue |
|---|---|---|
| 24 | ~~badge_engine.certifications~~ **[ALREADY RESOLVED - field no longer exists]** | No-op |
| 25 | ~~profile_network.referral_matches~~ **FIXED 2026-09-19** - placeholder stat removed | DONE |
| 26 | ~~content_generator.content_cache~~ **[ALREADY RESOLVED - field no longer exists]** | No-op |
| 27 | ~~ai_question_generator.used_questions~~ **[ALREADY RESOLVED - field no longer exists]** | No-op |
| 28 | ~~indian_language_ai.translations~~ **RECLASSIFIED** - translations dict is live; removed only unused total_translations placeholder | DONE |
| 29 | ~~indian_language_ai.submit_assessment~~ **FIXED 2026-09-19** - persists to charvak_lang_ai_submissions | DONE |
| 30 | ~~role_manager + dynamic_role_engine~~ **[DEFERRED - by design, see DEFERRALS.md]** | DONE |
| 31 | ~~monitor_service.SiteMonitor.check_site~~ **FIXED 2026-09-19** - switched to httpx.AsyncClient | DONE |
| 32 | ~~chatbot_engine._match_faq~~ **FIXED 2026-09-19** - key normalization | DONE |
| 33 | ~~ai_bridge_engine.get_premium_report~~ **FIXED 2026-09-19** - idempotency guard | DONE |
| 34 | ~~bridge_engine.update_progress~~ **[STALE - method does not exist; submit_answer merges correctly]** | No-op |
| 35 | ~~advanced_assessment_engine._generate_versant_questions~~ **[DEFERRED - content gap, see DEFERRALS.md]** | DONE |
| 36 | ~~enterprise_engine.review_resume~~ **FIXED 2026-09-19** - verb lookup replaces typo | DONE |
| 37 | ~~enterprise_engine.record_survey_response~~ **[DEFERRED - by design]**; ~~kiosk_check_in~~ **FIXED 2026-09-19** - logs to kiosk_events | DONE |
| 38 | ~~enterprise_engine.get_salary_benchmarks~~ **FIXED 2026-09-19** - proper median | DONE |
| 39 | ~~ats_engine asymmetric returns~~ **FIXED 2026-09-19** - standardized on jobs_count | DONE |

---

## 🟡 FEATURE GAPS

| # | File | Issue |
|---|---|---|
| 40 | ~~final_year_project_engine.total_projects returns 0~~ **FIXED 2026-09-20** - removed dead field (no live consumers) | DONE |
| 41 | student_suite_engine.assist_assignment / assist_research | Stubs |
| 42 | na_module/vector_matcher.SKILL_EMBEDDINGS | Static dict |
| 43 | advanced_assessment_engine._generate_versant_questions | Same as #35 |
| 44 | ~~exam_prep_engine emoji icons -> ASCII~~ **[ALREADY RESOLVED 2026-09-20 - icons are already ASCII slugs]** | DONE |

---

## 🟡 COSMETIC / A11Y

| # | Item |
|---|---|
| 45 | ~~Fix heading order on remaining pages~~ **COMPLETE 2026-09-19** - A-1 (20) + A-1.2 (73) + A-1.3 (24) = 117/165 templates fixed. Remaining ~48 excluded (admin/blog/tools/includes + shared layout + inline labels). | DONE |
| 46 | ~~TBT ~1,900ms mobile~~ **COMPLETE 2026-09-20** - actual TBT was 110ms (inventory stale). Session A-2 fixed: polling loop, 18 image dimensions, mobile navbar min-height + aspect-ratio. Results: Mobile CLS 0.135 -> 0, Desktop CLS 0 -> 0.009, Desktop Perf 92 -> 93. | DONE |
| 47 | ~~Emoji icons in docstrings~~ **[ALREADY RESOLVED - na_module files 100% ASCII; remaining emoji are user-facing/logger/icon-data]** | DONE |
| 48 | ~~Mojibake in notification_engine.py subject~~ **[ALREADY RESOLVED - emoji are real UTF-8]** | DONE |
| 49 | ~~Mojibake in products_engine.py log~~ **[ALREADY RESOLVED - emoji are real UTF-8]** | DONE |

---

## 🟢 HOUSEKEEPING

| # | Item |
|---|---|
| 50 | ~~Delete GitHub branches~~ **[ALREADY RESOLVED - no feat-* branches remain]** | DONE |
| 51 | ~~Delete local feat-micro-internship-escrow~~ **[ALREADY RESOLVED - not present]** | DONE |
| 52 | ~~Rename old folder to charvakit-new-OLD~~ **DONE 2026-09-19** - renamed from OneDrive/Desktop/charvakit-new | DONE |
| 53 | Delete old location (charvakit-new-OLD) after 2026-09-22 verification | SCHEDULED |
| 54 | ~~pip install sendgrid locally~~ **[DONE 2026-09-19 - sendgrid 6.12.5 installed]** | DONE |
| 55 | ~~Document full charvak_* schema in MASTER-REFERENCE.md~~ **FIXED 2026-09-19** - SCHEMA.md (128 tables auto-generated) + generator script + MASTER-REFERENCE link | DONE |
| 56 | Root directory final reorg |
| 57 | ~~Delete wget.exe if reappeared~~ **[ALREADY RESOLVED - not present]** | DONE |
| 58 | ~~Add git status check to session start~~ **FIXED 2026-09-19** - added to DEV-SETUP.md | DONE |

---

## 🔵 OPTIONAL / FUTURE

- **#88** ~~job_service.py persistence~~ **[RESOLVED 2026-09-19 - verified dead code; file deleted + import removed]**


- **#86** Product audit trail (deferred feature) — products_engine is stateless; if business wants an audit trail, needs: table `charvak_product_results`, INSERT in 11 methods, read endpoint `/api/products/results`, filter UI. Est ~3 hr.
- **#87** ~~Notification retention policy~~ **[FIXED 2026-09-20 - scripts/cleanup_notifications.py; Render cron pending]**


| # | Item |
|---|---|
| 59 | RazorpayX integration |
| 60 | AI Products real integrations (2–3 flagships) |
| 61 | Enterprise Option B — public engine pages |
| 62 | Per-level curriculum quality verification |
| 63 | International EMI via PayPal invoicing |
| 64 | ~~Verify /mock-test route~~ **[ALREADY RESOLVED 2026-09-20 - /mock-drive is canonical; /mock-test was never planned as a page]** | DONE |
| 65 | whatsapp_bot.py AI JSON bug (when unblocked) |
| 66 | indian_language_ai.py questions for 8 languages missing |
| 67 | ai_question_generator.used_questions — implement dedup |

---

## 🟣 PROCESS / HYGIENE

| # | Item |
|---|---|
| 68 | ~~Update STATUS.md at end of every session~~ **FIXED 2026-09-19** - refreshed to Session K status | DONE |
| 69 | ~~Keep TIER3-PERSISTENCE-PROJECT.md in sync~~ **FIXED 2026-09-19** - updated with B-3/B-4 status | DONE |
| 70 | Add markdown-emoji hygiene rule to DEV-SETUP.md |
| 71 | Add smoke-test safety gate to DEV-SETUP.md |
| 72 | ~~Consolidate doc sprawl~~ **FIXED 2026-09-19** - 6 docs archived to docs/archive/, DEPLOY_TRIGGER.md removed, root reduced 21 -> 14 | DONE |

---

## 🟠 AUDIT / VERIFICATION NEEDED

| # | Item |
|---|---|
| 73 | Reconciliation scan — precise remaining engine count |
| 74 | ~~Formalize the "verified skip" list in TIER3-PERSISTENCE-PROJECT.md~~ **FIXED 2026-09-19** - full section added with 5 categories + re-eval triggers | DONE |
| 75 | Verify voice_to_web_engine.py unchanged since 2026-09-17 |
| 76 | Check other unclassified engines post-Session-J |
| 77 | admin_role_manager.py add_role_as_admin actually used? |

---

## 🆕 SCAN FINDINGS

- [x] **H-2** templates/base.html — mojibake fixed 2026-09-19
 (added 2026-09-19 post-reconciliation)

| # | New Item | Priority | Notes |
|---|---|---|---|
| 78 | notification_engine.py ~~in-memory, 6 main.py refs~~ **FIXED 2026-09-19 (B-3)** - persisted to charvak_notifications | DONE |
| 79 | ~~products_engine.py~~ **[B-4 CLOSED 2026-09-19 - verified stateless]** | DONE |
| 80 | tools_engine.py -- in-memory, scope unclear | Low | Audit needed |
| 81 | job_service.py -- in-memory, 1 main.py ref | Low | Likely thin wrapper |
| 82 | scripts/one-off/resume_engine.py -- dead duplicate | Trivial | Delete |
| 83 | enhanced_assessment_engine.py -- 0 DB signals | Low | Verify legacy vs active |
| 84 | chatbot_engine.py -- AI JSON mode missing | Medium | Confirm real bug or false positive |

### Resolved by scan (updates audit bucket #71-75)

- #71 -- DONE: reconciliation scan ran 2026-09-19
- #73 -- DONE: voice_to_web_engine.py unchanged since Aug 27 2026
- #74 -- DONE: found 4 new in-memory + 9 unclear
- #75 -- DONE: admin_role_manager IS used (main.py:6088-6093)
- #72 -- PARTIAL: unclear files now identified, formalize in Session I

---

## Summary counts

| Bucket | Count |
|---|---|
| 🔴 Security | 3 |
| 🟠 Data integrity | 5 |
| 🟢 Formal deferrals | 4 |
| 🟠 Tier 3 outstanding | 9 |
| 🟡 Dead fields / cosmetic bugs | 16 |
| 🟡 Feature gaps | 5 |
| 🟡 Cosmetic / a11y | 5 |
| 🟢 Housekeeping | 9 |
| 🔵 Optional / future | 9 |
| 🟣 Process | 5 |
| 🟠 Audit/verify | 5 |
| 🟡 Persistence engines remaining | 2 (+4 new from scan) |
| **TOTAL** | **~84** (after scan additions) |

---

## Recommended session bundling

| Session | Scope | Items | Est. |
|---|---|---|---|
| Audit | Reconciliation + verification scans | 5 | ~30 min |
| B-2 | voice_to_web_engine persistence | 1 | ~1 hr |
| K | Security + data integrity + formal deferrals + dead fields + cosmetic | 33 | 3–4 hr |
| I | Capstone: backfill, reorg, consolidation, tag, backup | 10+ | 1–2 hr |
| Post-I | Feature gaps, optional, a11y | 14+ | open-ended |
| External | WhatsApp / Meta | 1 | blocked |

**Path to "done":** B-2 → K → I = ~5–7 hr to close everything actionable.

---

## Execution order (agreed)

1. **Reconciliation scan** (~30 min) — cleans items #73–77, exact counts
2. **Session B-2** (~1 hr) — closes Tier A
3. **Session K** (~3–4 hr) — security first, then data integrity, dead fields, cosmetic
4. **Session I** (~1–2 hr) — capstone + tag + backup
5. **Post-I features** — pick what matters

**Keep this file in sync after every session.** It is the master backlog.

## Session A-1.3 — JS-Templated Templates (filed 2026-09-19)

**Scope:** 26 templates using JS template literals where headings live inside `<script>` blocks. Cannot be safely bulk-fixed.

**Files:**
ai-bridge, ai-generate-stack, ai-internship, ai_credits_pricing, application-dashboard, bridge, client-dashboard, company-detail, credit_dashboard, doketsrb, exam-prep, inbox, indian-language-ai, interview-dashboard, interview-results, marketing-ai, my-courses, na-bench-staffing, napkin-challenge, referral-dashboard, skill-check, staff-augmentation-proposal, student-suite, submit-referral, testimonials, web-design-proposal

**Approach:**
1. Open each file, find heading patterns inside JS strings
2. Update the heading tag inside the template literal
3. Update any JS that queries by tag name (rare but check)
4. Test rendered output in browser
5. Commit per batch of 5 files

**Estimated:** 2-3 hr.

