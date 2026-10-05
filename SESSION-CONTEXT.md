# Session Context - Charvak

## Sessions 19-21 CLOSED (2026-10-04) - Certificate v2

Three sessions shipped together as the certificate-v2 release.

**Session 19 — Size upgrade CTA + supersedes chain**
- supersedes / superseded_by columns on charvak_readiness_certificates
- Auto-link on upgrade (same email/role/industry/level)
- Yellow "want a more precise score?" card on below-benchmark certs
- Green "Improved from an earlier check" callout on the new cert
- 15-question Standard check CTA (25 cr)

**Session 20 — Certificate polish**
- Best Score stat card on /my-results
- "Show only latest per role" toggle
- Supersede email notification

**Session 21 — PDF download**
- render_readiness_certificate_pdf() — branded A4 layout, single page
- GET /api/readiness/{id}/download (public + token fallback)
- Frontend: real PDF download, no more window.print()

**Session 22 candidates:**
- A: Sprint B /my-jobs verified job matching (2 sessions)
- B: Certificate round 2 (QR, watermark, multi-language)
- C: Anti-cheating Layer A (1 session)

Recommendation: A.



## Session 22 CLOSED (2026-10-05) — Sprint B: Client Staffing Pipeline

The CBREX-mediated staffing pipeline is live end-to-end.
Candidates can browse open roles, apply with screening answers and
consent, and self-provision their profile inline in the apply modal.

**6 commits shipped:**
- `e23b853` schema + engine + 9 routes (Session 22a)
- `41a91a1` /open-roles + /open-roles/{id} + apply modal (Session 22b)
- `598101e` candidates_engine + /api/candidates/* (Session 22c.1)
- `b95d39d` inline profile form (Session 22c.2)
- (+ two micro-fixes: registered_at column, JSONB skills coercion)

**Live URLs (prod):**
- /open-roles             public listing
- /open-roles/{role_id}   public detail + apply

**Backend namespace:**
- /api/staffing/open                      public listing
- /api/staffing/roles/{role_id}           public detail
- /api/staffing/roles/{role_id}/apply     auth + consent
- /api/candidates/me                      auth (caller only)
- /api/candidates/upsert                  auth (create/update)
- /api/admin/client-roles/*               6 admin endpoints

**5 new tables:**
charvak_client_roles, charvak_role_screening_questions,
charvak_role_screening_answers, charvak_candidate_documents,
charvak_candidate_consents

**Verified E2E on local + prod:**
- Anonymous browse, login-gated apply, dynamic question rendering,
  consent capture, inline profile form, retry-on-profile-missing,
  green success banner, all data persisted with correct FK links.

**Still pending for Session 23+:**
- CBREX package generator (PDF + ZIP with resume/eval/certificate)
- Admin dashboard (/admin/client-roles UI)
- Nav link for /open-roles in base.html
- Candidate profile edit page (/profile)



## Session 22.5 + Role Loading CLOSED (2026-10-05)

Extended Session 22 into a full staffing pipeline launch.

**7 real roles loaded to prod:** AI Machine Learning Engineer,
AI Agent Operations Engineer, Platform Engineer, AI Engineer (all NCS,
urgent), Lead Firmware Engineer, Application Engineer (Lenze), Sr.
Mechanical Design Engineer STP (Middle East Group). 92 screening
questions across all roles.

**New features:**
- /open-roles  public role listing (works on any device)
- /open-roles/{id}  detail + apply modal
- Inline profile collection when candidate has no profile
- /profile  candidate profile edit
- /my-applications  candidate's applications list
- HR email notification on every application to
  hr@charvakit.com + charvakit@gmail.com

**CBREX name fully stripped:** client_name="via Charvak", all vendor
fields nulled, budgets hidden from public API + UI, zero CBREX
strings in DB.

**Commits:** a2620d5, 8b7831f, e97d7ef, 5fb67f2 + seed files

**Verified E2E on prod:** fresh user registration -> apply -> inline
profile -> green success banner -> email arrives at both inboxes.

**Lesson:** database.py loads .env.local with override=True — silently
overrides shell env vars. For prod data ops: rename .env.local first,
use direct psycopg2, restore after.

**Next (Session 23):** CBREX package generator
- GET /api/admin/applications/{app_id}/cbrex-package (JSON)
- .pdf (Charvak Evaluation Form via pdf_engine.py)
- .zip (resume + eval PDF + certificate PDF + consent proof)



## Session 23 CLOSED (2026-10-05) - Submission package generator

Full pipeline now works end-to-end via API. Admin can generate a
complete client-ready submission package from any application.

**Commits:**
- d35032c  Session 23 4a.1 - JSON package builder
- b6ee7e3  Session 23 4a.2 - PDF evaluation form
- 579b249  Session 23 4a.3 - ZIP bundle + CBREX de-identifier
- 5a762aa  Session 23 polish - consistent 404s for missing apps

**New endpoints (all admin-gated):**
- GET /api/admin/applications/{id}/submission-package       (JSON)
- GET /api/admin/applications/{id}/submission-package.pdf   (PDF)
- GET /api/admin/applications/{id}/submission-package.zip   (ZIP)

**ZIP contents:**
- 01_candidate_profile.json
- 02_evaluation_form.pdf (branded Charvak layout)
- 03_readiness_certificate.pdf (if cert exists)
- 04_resume.<ext>               (if uploaded or text present)
- 05_consent_proof.<ext>        (if proof file uploaded)
- README.txt                    (manifest enumerating actual contents)

**CBREX de-identifier sweep completed:**
- Renamed cbrex_pdf_engine.py -> submission_pdf_engine.py
- All 3 routes renamed /cbrex-package* -> /submission-package*
- All function names, docstrings, comments de-identified
- Consent vendor default changed CBREX -> Charvak
- Result: 0 CBREX references across the codebase

**Verified E2E on local APP-7F862AE1:**
- All 3 new routes 200 (JSON/PDF/ZIP)
- Old routes 404
- Missing app IDs 404 consistently across all three
- ZIP contents match README

**Next session (24):** admin UI for client roles + applications
- /admin/client-roles          (list + applicant counts)
- /admin/client-roles/{role_id} (detail + applicants + downloads)
- Link in admin dropdown
- All backend endpoints already exist



## Session 24 CLOSED (2026-10-05) - Client Roles admin UI

Full admin interface for the staffing pipeline. Backend endpoints
already existed from Session 22; this session added the frontend.

**Commit:** `37f978f` — feat(admin): Session 24 - client roles
list + role detail pages

**New pages:**

- `/admin/client-roles`
  - Table of all client roles with applicant counts
  - Summary strip: Total / Urgent / Applicants / Sourcing
  - Filter buttons by status (all / sourcing / shortlisting / submitted / closed)
  - Per-row: View detail, Open public page

- `/admin/client-roles/{role_id}`
  - Role info card with skills + priority badge
  - Summary strip: Total / Pending / Submitted / Shortlisted
  - Applicant list ranked by readiness
  - Per-applicant actions:
    - View modal with full profile + screening answers
    - Download submission-package.zip

**Bugs fixed during session:**

1. Modal trapped in `<main>` stacking context — moved to `{% block modal %}`
2. Modal button bindings moved inside DOMContentLoaded
3. Jinja parsed a template tag inside a JS comment — removed
4. Click delegation handler was silently lost in an earlier patch — restored
5. `loadAll` / `loadRoles` exposed on `window` for inline Refresh buttons

**Local dev admins created matching prod:**

- hr@charvakit.com
- charvakit@gmail.com
- ADMIN_EMAILS env updated in `.env.local`

**Verified E2E on local:**

- List page renders 7 roles, filters work, Refresh works
- Detail page renders 1 applicant, modal works, Download works
- No console errors

**Prod verified:**

- `/admin/client-roles` returns 302 (redirect to login = gate works)
- Old `/cbrex-package` route returns 401 (retired)

**Next session (25) candidates:**

- Status update UI in the applicant modal (shortlist / submitted / hired / etc.)
- Recruiter notes textarea
- Batch download ZIP (all applicants per role)
- Security sweep on new admin endpoints





## Session 25 CLOSED (2026-10-05) - Admin applicant actions

Three patches that close the admin workflow loop.

**Commit:** `cdc5cb3` + following (dashboard card)

**Shipped:**

- **Patch 5c.1** - Applicant status + recruiter notes UI in the
  modal on /admin/client-roles/{role_id}
  - Status dropdown (pending/shortlisted/submitted/interviewing/
    offer/hired/rejected/withdrawn)
  - Recruiter notes textarea (private, not shown to candidates)
  - Save button POSTs to /api/admin/applications/{id}/submission-status
  - Prefills current values on modal open
  - Auto-refreshes the applicant list after save

- **Patch 5c.2** - Batch download ZIP per role
  - New endpoint: GET /api/admin/client-roles/{role_id}/applicants-batch.zip
  - Returns one ZIP containing a per-applicant subfolder for every
    applicant of the role: candidate_profile.json + evaluation_form.pdf
    + README.txt + SUMMARY.txt at the root
  - New module: client_staffing_batch.py (standalone helper)
  - Frontend: 'Download All as ZIP' button next to Applicants header

- **Patch 5c.3** - Admin dashboard card
  - 'Client Roles' button added to admin-unified.html Quick Actions

**Fixed during session:**

- Schema assumption bug: charvak_applications has no candidate_name
  column. Batch query now LEFT JOINs charvak_candidates on email.

**Session 25 result:** the full admin workflow works from the
browser, no DB editing required:
  dashboard -> roles list -> role detail -> applicant modal
    -> status change + notes -> save
    -> single download or batch download

**Next session (26) candidates:**

- Security sweep on new admin endpoints (Session 14 style)
- Delete or leave legacy /api/assessment/* routes (8 remaining)
- Verify charvak_jobs legacy reference in main.py
- Anti-cheating Layer A (blocks Career Assessment Phase 2b)
- Career Assessment Phase 2b (coding + SQL via Judge0 sandbox)



## Session 26 CLOSED (2026-10-05) - Security sweep + cautious cleanup

Three items investigated; zero deletions made. The system is cleaner
than the audit implied.

**Item 1 - Security sweep on new admin endpoints (PASSED)**

Ran the 4-scenario matrix on 10 admin routes from Sessions 22-25:
- Anonymous -> 401
- Non-admin user (valid token) -> 403
- Admin -> 200 or 400
- Zero security gaps

Also confirmed: 10 pre-existing admin routes (analytics, settings,
users, purchases, testimonials x5, cleanup-users) rely on
`admin_auth_guard` middleware alone (no require_admin in body).
Verified with non-admin token: all return 403.

**Item 2 - Legacy /api/assessment/* routes (KEPT, not deleted)**

Initial audit flagged 7 routes as dead. Deep audit revealed they
must stay:
- COMMITMENT.md documents them as deliberately preserved
- Two underlying engine methods have OTHER live call sites
  (main.py:10614 and main.py:10581)
- audits/audit-routes.json catalogs all 8
- No proof exists of zero external callers

Action: tombstone comment added above the block documenting the
decision. Routes left in place.

Note: POST /api/assessment/mcq/generate IS live (used by mcq.html).

**Item 3 - charvak_jobs reference (NOT dead, no action)**

`charvak_jobs` is a LIVE table used by:
- main.py:1629 - active /api/jobs/post route
- api_sync.py - DoketsRB integration (jobs sync)
- ats_engine.py - ATS provider integration
- job_board_engine.py - the engine that owns the table
- 4 public routes verified live: /api/jobs, /search, /stats, /applications

The table serves the public job board, distinct from
`charvak_client_roles` which serves the CBREX staffing pipeline.
Both are live. Neither supersedes the other.

Action: no action. Table and routes stay.

**Process lesson:**

Simple greps miss real usage. In both cases, only cross-referencing
multiple file types + historical tracker decisions revealed the truth.

Rule for future audits: grep across ALL file types including
historical trackers and audit artifacts.

**Next session (27) candidates:**

- Anti-cheating Layer A (blocks Career Assessment Phase 2b)
- Career Assessment Phase 2b (coding + SQL via Judge0)
- AuditBot Continuous
- Rotate Render Postgres password (still pending)


---

---

---

---

## Session 18 CLOSED (2026-10-04) - Train stage resurrection

Custom-course generator (Phase 1) plus critical Train-stage bug fixes.
The lesson player went from broken to fully functional.

**Highlights:**
- Custom-course generator: users can generate a private course for any
  weak topic without a matching catalog course (50 credits each)
- Learning path is now fully self-contained (no external links)
- Fixed charvak_enrollments missing recipient_name column
- Fixed charvak_certificates missing recipient_name column
- Fixed my-course.html missing updateProgress() function
- Fixed all my-course.html POST fetches (auth headers)
- complete_week() now auto-issues a certificate on the final week

**Verified:** Course completed end-to-end, certificate CERT-9C1DBCD84B4E
issued, verify URL live.

**Session 19:** Phase 2 size upgrade CTA (10 -> 20 question upsell)
**Session 20:** Certificate enhancement (signature, HMAC, QR)
**Session 21:** Sprint B /my-jobs

---

**HEAD:** `980bbdc`
**Last updated:** 2026-10-04 (Session 16 - Premium Report product shipped)
**Version:** `v3.5-session-16-20261004`

---

## Where we are (Session 16)

Session 16 shipped the **Premium Report** product (Rs 199 / 400 credits)
end-to-end across 5 commits.

**Commits this session:**
- `aa8a279` feat(pdf): add PDF engine for Premium Report generation
- `c60a9a5` feat(premium-report): add report generator engine + routes
- `961a3dc` feat(premium-report): PDF download route + SendGrid email
- `a2537e6` feat(premium-report): frontend unlock flow + /my-reports
- `980bbdc` fix(premium-report): accept ?token= for browser/email downloads

### Shipped

**Premium Report product**
- `pdf_engine.py` — fpdf2-based PDF renderer with branded cover page,
  headers, footers, sections, severity badges, Unicode via DejaVu
- `premium_report_engine.py` — one OpenAI call produces 5 AI sections
  from the source product's free-tier scan data; persists to
  `charvak_premium_reports`; falls back to a template if AI is down
- 3 report types: `auditbot`, `lock_in_breaker`, `skill_twin`
- Credit key: `premium_product_report` (400 cr) — separate from the
  existing `premium_report` (25 cr) used by assessment reports
- SendGrid email with the PDF as a base64 attachment
- `templates/includes/premium-upsell.html` rewritten to be
  config-aware (reads `window.CHARVAK_PREMIUM`); falls back to
  notifyMe() on the 24 other pages that include it
- `/my-reports` dashboard listing the user's reports with
  Download PDF buttons

### E2E verified
- Full flow: free scan → unlock → AI generation → PDF → email → download
- Credit deduction: exact 400 per report
- 3 premium reports generated during testing
- Email delivered to test-register email
- Download works from both the inline upsell and the dashboard

### Notes
- Browser <a href> navigations don't send Authorization headers, so
  the download route accepts ?token= as a fallback. `/generate`
  includes the caller's token in the returned `download_url`.
- Fixed a latent bug: `auditbot.html` never set
  `window.lastAuditResult`, so the upsell always said "Run a scan
  first". The other two premium pages already did.

---

## Where we are

Session 15 completed Silent-Killer 9b (continuous monitoring cron +
state-change email alerts) plus several smaller items.

**Commits this session:**
- `5e64b1a` feat(payments): expose PAYPAL_MODE in /api/payment/status
- `1f1f834` docs: sync SCHEMA.md (128->164 tables) + PAGES-INVENTORY delta
- `f468c50` feat(silent-killer): continuous monitoring cron + alerts (Session 9b)

### Shipped

**Silent-Killer 9b (headline)**
- enhanced_email.send_silent_killer_alert() - SendGrid email on state change
- products_engine.silent_killer_due_watches() - due-watch selector
- POST /api/cron/silent-killer-scan - X-Cron-Secret auth
- Full frontend rewrite of the script block (previous version had 15
  lines with malformed JS strings; page rendered but nothing worked)
- "Notify Me" button retired; live badge replaces it
- Render cron job silent-killer-scan runs every 5 min, verified firing

**Observability**
- /api/payment/status now returns paypal_mode ("live" | "sandbox")
- Fixed CRON_SECRET typo in local .env (colon -> equals)
- Set PAYPAL_MODE=live on Render; confirmed via /api/payment/status
- Added CRON_SECRET to silent-killer-scan cron's environment

**Docs**
- SCHEMA.md regenerated: 128 -> 164 tables
- PAGES-INVENTORY.md header bump + Sessions 8-15 delta section

### Verified E2E

Local:
- Cron without secret -> 401
- Cron with wrong secret -> 401
- Cron with correct secret -> 200
- Due watch detection -> only due watches scanned
- fail -> ok flip -> alerted: 1, email sent to owner
- Browser: page fully functional (panel, recheck, history, delete)

Prod:
- /api/payment/status: paypal_mode = "live"
- Render cron silent-killer-scan: 200 + {"status":"success",...}
- Created a test watch directly in prod DB; Render cron picked it up
  and ran the scan within 5 minutes (confirmed scan row with 200 OK).
  Test watch was cleaned up afterward.

### Local vs Prod database

Local .env.local points at charvak_dev on localhost:5432.
Prod uses vouchai on Render Postgres.

### Flagged for Session 16

- Career Assessment Phase 2b: coding + SQL via Judge0 (2-3 days)
- Premium Report product (8-12 hrs, product decision)
- Doc pass on remaining stale files (DEFERRALS, DEV-SETUP, DOC-STYLE)
- Rotate PayPal + SYNC keys (external dashboards)

---

## Career Assessment product status

| Phase | Status |
|---|---|
| Phase 1 (MCQ) | Shipped |
| Phase 2a (7 more formats) | Shipped |
| Phase 3 (adaptive + skill gap + learning paths) | Shipped |
| Phase 2b (coding + SQL) | Session 16+ |
| Phase 4 (certs, badges) | Future |

---

## Environment

- HEAD: f468c50
- Local Python: 3.11.9 venv
- Local DB: Postgres 15 (charvak_dev)
- Prod DB: Render Postgres (vouchai)
- Prod: https://www.charvakit.com
- Render service: srv-d9hhljd8nd3s73d2hoeg
- Render cron jobs: send-emi-reminders, cleanup-notifications,
  send-queued-emails, silent-killer-scan (new)

---

## Session 17 COMPLETE — Sprint A shipped (2026-10-04)

Sprint A of the Proof Layer framework is live. The free Role Readiness
Certificate is end-to-end: landing page -> assessment -> shareable
certificate URL with HMAC verification.

**7 commits shipped:**
- 14b2bb8  feat(readiness): Sprint A backend (engine + 5 routes + benchmarks)
- 4fc158e  feat(readiness): readiness.html (public certificate page)
- 2c09632  feat(readiness): readiness-check.html + route (public landing)
- 87aa95a  feat(readiness): ai-assessment deep-link + certificate CTA
- 814db5e  fix(readiness): percentile floor 5..99, level/passing fallbacks, OG tags
- <next>   fix(readiness): move var _a out of string concat

**Live at:**
- GET /readiness-check     — public free landing
- GET /readiness/{id}      — public shareable certificate
- GET /api/readiness/{id}  — public read
- GET /api/readiness/verify/{hash}  — public verification
- POST /api/readiness/generate      — auth-gated certificate creation
- GET /api/readiness/list/{email}   — auth-gated list

**Verified E2E on local:**
- Dropdowns populate [107, 67, 8] for role/industry/level
- Free check start -> deep-link -> questions skip Step 1
- Answer -> result page (with green certificate CTA)
- Get My Certificate -> /readiness/RDC-XXXX
- Certificate renders with score, benchmark, percentile (floor 5), hash
- Verify URL returns {valid: true}
- Tampered hash returns {valid: false}

**Session 17d (2026-10-04):** Made the certificate discoverable.
/my-results now lists readiness certificates with a filter pill + stat
card. Top nav has a "Readiness Check" link. User dropdown has a
"My Certificates" button. Closes the discoverability gap on the Sprint
A certificate.

**Session 18 scope (next):**
1. Custom-course generator (replace external links with Charvak-hosted
   custom courses in learning paths)
2. Size upgrade CTA on quick-check results (10 -> 20 questions for
   below-benchmark users)
3. Sprint B kickoff: /my-jobs verified matching

---

## Session 17 priority (locked)

**Scope:** Gap 1 (Role Readiness Score) + Gap 3 (Anti-Cheating Layer A)
alongside Career Assessment Phase 2b (coding/SQL via Judge0).

**Why:** Gap 3 is a prerequisite for Phase 2b — without integrity signals,
employers will dismiss the coding/SQL assessments. Shipping 2b without
anti-cheating produces a technically complete feature that fails commercially.

**Reference:** See `COMPETITIVE-STRATEGY.md` for the full analysis, the 4 gaps,
the roadmap, and the metrics we're tracking. Re-read at the start of every
session.

**Gaps 2 and 4 (deferred, documented):**
- Gap 2: Multilingual Voice AI — Sessions 20+
- Gap 4: AuditBot Continuous Compliance — Sessions 18-19

---

## Recommended next session (Session 16)

Option A: Career Assessment Phase 2b (coding + SQL) - 2-3 days.
Option B: Premium Report product - 8-12 hrs.
Option C: Doc pass + cleanup - ~1.5 hrs.

Recommendation: A.

**Post-Session 16 update:** Premium Report shipped. Session 17 is now
open to:
- Career Assessment Phase 2b (coding + SQL via Judge0 sandbox)
- Or a doc pass on the remaining stale files
- Or a security sweep (Session 14 style)