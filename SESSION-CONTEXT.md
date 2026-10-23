# Session Context - Charvak

**HEAD:** 707996c
**Live:** https://www.charvakit.com
**Updated:** 2026-10-24 (Sessions 79-80 closed)

---

## Latest State

**Sessions 76-80 shipped in 24 hours (2026-10-24):**

- **S76** (`e6af6b0`): Nav Phase 2 — 14 flat items → 5 story-driven dropdowns
- **S77** (`cea4e69`): 12px gap between Global Platform strip and main nav
- **S78** (`db6978b`): Email gate on /readiness cert page for anonymous visitors
- **S79** (`6c95809`, `2dad2ed`): Flag 1+3 closed, Amrita email sent, GPT-5.4 verified
- **S80** (`707996c`): 3-pillar homepage + 5 enterprise one-pagers

### Flags Status
| Flag | Status |
|---|---|
| Flag 1 — Amrita email | ✅ Sent Oct 23, 19:54 (3 PDFs attached) |
| Flag 2 — Render password | 📅 **Monday** (2 min) |
| Flag 3 — GPT-4o env flip | ✅ Verified 7/7 tests |
| Flag B — 5 enterprise one-pagers | ✅ Done (Desktop folder) |
| Flag D — 3-pillar homepage | ✅ Live on prod |

### Amrita Follow-Up Schedule
- Wed Oct 28: follow-up #1
- Fri Nov 1: final nudge
- Nov 15: re-engage (if new angle)

Scripts saved in `_amrita_followups.txt`

### Next Session (Monday)
1. Rotate Render Postgres password (2 min)
2. Verify homepage 200
3. Then: send 5 one-pagers to 5 universities (outbound)

### Head State
- HEAD: `707996c`
- Working tree: clean
- Prod: 200, all features live

---

---

## Latest State

**Session 74 extended (2026-10-22):**

### Shipped to Prod
- Certificate page conversion CTAs (Retake, See courses) — `b4616f8`
- Fixed pre-existing backtick syntax bug in renderCertificate
- Verified Razorpay live payment flow works end-to-end
- Confirmed Resume Roast page functional (76% dropoff = user behavior, not bug)

### Key Commits
- `b4616f8` fix(readiness): repair backtick escape + add conversion CTAs
- `1573fc5` fix(css): restore .dropdown-menu display:none (broken header)
- `04b583b` docs(session-74): close-out
- `51deff2` chore: gitignore backups/

### Business Assets Live
- Azure role: https://www.charvakit.com/open-roles/ROLE-7B9405A1
- 12 screening questions configured
- Certificate page now has 2 monetization CTAs

### Still Pending (Session 75)
- Fix #3: Homepage CTA to /ai-assessment (20 min)
- Fix #4: Email capture before cert download (60 min)
- Nav Phase 2: 5 story-driven dropdowns (2 hrs, VS Code direct edit)
- One remaining minor JS block issue (cosmetic, non-blocking)

### GA4 Data Context
- 674 users last 30 days
- 316 hit /readiness-check (46%)
- 23 complete (3.4%)
- 262 cert page views/month
- Zero revenue — now with 2 CTAs to change that

### Session 75 Priorities
1. Homepage Career Assessment CTA
2. Email capture before cert download
3. Nav Phase 2 (fresh approach, VS Code)
---

## Institutional Expansion (New — 2026-10-24)

See `INSTITUTIONAL-ROADMAP.md` for the complete Phase A/B/C roadmap.

**TL;DR:** Four TPO objections must be solved before Charvak sells
to institutions:
1. "We have an LMS" → A4 LMS Bridge (5 sessions)
2. "Students are lazy" → A3 Engagement Engine (5 sessions)
3. "Where are the placements?" → A1 Employer Network (6 sessions)
4. "How do I prove ROI to my Dean?" → A2 Proof Dashboard (5 sessions)

**Phase A total:** 21 sessions. Ships Charvak from "assessment tool" to
"placement operating system."

**Recommended first build:** A2 — Proof Dashboard (5 sessions).
Unblocks every TPO conversation.

**Do not skip Phase A.** Phase B and C are blocked on Phase A capability.
