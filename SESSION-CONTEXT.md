# Session Context - Charvak

**HEAD:** aadb13d
**Live:** https://www.charvakit.com
**Updated:** 2026-10-25 (Session 82 extended - G6 closed + W1 shipped)

---

## Session 83 — F1 Scorecard Artifact SHIPPED (2026-10-26)

**F1 of 8 enterprise features from ENTERPRISE-ROADMAP-FLAG.md — LIVE on prod.**

### 3 demo scorecards live:
- https://www.charvakit.com/scorecard/SC-2780FC46D5E0 (87/100, Senior Backend Engineer)
- https://www.charvakit.com/scorecard/SC-07CF13C2A0F6 (78/100, Full-Stack Engineer)
- https://www.charvakit.com/scorecard/SC-AE61E212BFE2 (72/100, Data Scientist)

### Shipped
- scorecard_engine.py (466 lines)
- 5 routes (/scorecard/{id}, /api/scorecard/{id}, /api/scorecard/create, /api/scorecard/{id}/share, /api/scorecard/list/{email})
- templates/scorecard.html (206 lines)
- migrations/20261026_scorecards.sql
- "Create Shareable Scorecard" button on /ai-assessment result page

### Beats VIVA360
- HMAC-verifiable credential vs their "explainable"
- Full skill breakdown vs their 6 axes
- Integrity status shown
- Public JSON API
- No login required

### Debugging lessons
1. .env.local OVERRIDES .env — must disable for prod seeding
2. Verify data via deployed /api endpoints, not just local script

### Follow-ups (not blocking)
- Add charvak_career_certifications migration to prod
- Document .env.local disable pattern in DEV-SETUP.md

### Next in roadmap
- F2 Compliance Page (~30 min, writing only)
- F3 Screen Agent (2 sessions)

---

## Session 82 Extended - G6 + W1 + 401 Fix CLOSED (2026-10-25)

Three major deliverables shipped and verified on prod.

### 1. G6 - Google OAuth - FULLY SHIPPED

- users.google_oauth_id + users.auth_provider columns deployed
- google_oauth_engine.py (full OAuth 2.0 flow) deployed
- 3 routes: /api/auth/google/start, /callback, /unlink
- Sign in with Google button on /login + /register
- charvak_auth_token cookie for ALL users (30-day, HttpOnly, Secure, SameSite=Lax)
- checkLoginState() cookie-session fallback
- verified=TRUE on Google account linking
- Google Cloud consent screen compliant (2024+ policy)
- End-to-end verified on prod

Prod user record verified:
    charvakit@gmail.com: auth_provider=google, verified=True, google_oauth_id set

Bugs fixed (6 auth bugs):
1. require_auth() didn't read charvak_auth_token cookie
2. /api/auth/login only set cookie for admins
3. checkLoginState() only read localStorage
4. find_or_create_user didn't set verified=TRUE on link
5. Google consent screen missing 2024+ required fields
6. Stale browser cookies from pre-fix sessions

### 2. W1 - Homepage Reframe - SHIPPED

- Placement OS positioning strip above hero
- 'The Placement Operating System for Indian Colleges' + 'Assess -> Prove -> Place'
- More from Charvak section below 3 pillars (4 cards)
- Live on prod: https://www.charvakit.com/

### 3. 401 Redirect Fix - SHIPPED

- base.html 401 handler skips redirect when URL contains /api/auth/me
- Before: anonymous visitors auto-redirected to /login
- After: homepage reachable to new visitors
- Verified on prod

### Commits Pushed

- aec9c96 - feat(auth): Google OAuth sign-in (G6)
- c793fed - fix(auth): cookie sessions work end-to-end
- 59caf2c - chore: gitignore Session 82 debug artifacts
- 208f9bb - chore(migrations): formalize users table legacy columns
- aadb13d - feat(homepage): W1 + 401 redirect fix

### Local Environment

- Local DB: synced with prod (98/99 migrations, 11 users columns)
- New migration: 20261025_users_legacy_columns.sql

### IMMEDIATE NEXT SESSION — Two Features Queued

**See NEXT-SESSION-PLAN.md for full details.**

Build in this order:
1. **Email Mismatch Auto-Link Flow** (~2 hrs) — unblocks DoketsRB sync UX
2. **Coding/SQL Certifications** (~3.5 hrs) — closes Tier 2 gap

Both unblocked. Diagnostics in the plan file.

### Next Session Priorities (Monday Oct 26)

1. Send 5 university one-pagers (drafts ready in chat)
   - Design Partner: IIT Madras CDC, VIT Vellore CDC, NIT Trichy CDC
   - Outreach: BITS Pilani CDC, PSG Coimbatore CDC
   - Attach: Charvak_Enterprise_Package.pdf
2. Render Postgres password rotation (2 min - Session 19 flag)
3. Send Amrita follow-up #1 (Wed Oct 28 scheduled)

### Pending Flags

- Render password rotation (Session 19, oldest carried flag)
- /api/sync/* should skip 401 redirect (10 min)
- require_auth() cookie fallback chain (5 min)
- Migration ordering warning (employer_accounts before employer_referrals)
- Dean Report Frontend (deferred - see DEAN_REPORT_FRONTEND_FLAG.md)
- A4 LMS Bridge (deferred - trigger: institution asks)

### Git State

- HEAD: aadb13d
- Working tree: clean
- Prod: 200, all features live

---

## Sessions 79-81 (reference)

- S79-S80: Amrita email sent Oct 23 19:54 (3 PDFs), GPT-5.4 env flip verified, 5 enterprise one-pagers, 3-pillar homepage (707996c)
- S81: Phase A products - A1 Employer Network v0.3, A2 Proof Dashboard backend, A3 Engagement Dashboard v1.0, 6 new tables

---