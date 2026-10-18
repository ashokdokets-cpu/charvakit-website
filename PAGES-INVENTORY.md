# Charvak — Pages Inventory

**Last updated:** 2026-10-19
**Version:** v3.5-session-52-20261019
**Delta section:** see "Recent Additions & Updates" at the bottom for the Sessions 8-15 changes.

Every template in `templates/`. Grouped by purpose.

---

## Root Templates

| Template | Route | Purpose | Auth? |
|---|---|---|---|
| `base.html` | (layout) | Master layout — nav, footer, scripts | — |
| `index.html` | `/` | Homepage — hero, features, products, testimonials | No |
| `about.html` | `/about` | About Charvak | No |
| `services.html` | `/services` | Services overview | No |
| `web-design.html` | `/services/web-design` | Web design service page | No |
| `web-design-proposal.html` | `/services/web-design/proposal` | Proposal request | No |
| `staff-augmentation.html` | `/services/staff-augmentation` | Staff augmentation service | No |
| `staff-augmentation-proposal.html` | `/staff-augmentation/proposal` | Staffing proposal | No |
| `products.html` | `/products/dokets-vouchai` | Product detail page | No |
| `products-list.html` | `/products` | All products listing | No |
| `team.html` | `/team` | Team page | No |
| `careers.html` | `/careers` | Careers page | No |
| `contact.html` | `/contact` | Contact form | No |
| `register.html` | `/register` | Registration page | No |
| `login.html` | `/login` | Unified login (email + SSO) | No |
| `forgot-password.html` | `/forgot-password` | Password reset request | No |
| `reset-password.html` | `/reset-password` | Password reset form | No |
| `verify-email.html` | `/verify-email` | Email verification landing | No |
| `roadmap.html` | `/roadmap` | Product roadmap | No |
| `how-it-works.html` | `/how-it-works` | How Charvak works | No |
| `for-candidates.html` | `/for-candidates` | Candidate landing | No |
| `for-employers.html` | `/for-employers` | Employer landing (also `/demo`) | No |
| `hire-talent.html` | `/hire-talent` | Hire vetted talent | No |
| `developer-signup.html` | `/developer-signup` | Developer pool signup | No |
| `demos.html` | `/demos` | Product demo videos | No |
| `pricing.html` | `/pricing` | Pricing overview | No |
| `payments.html` | `/payments` | Payments info page | No |
| `assessments.html` | `/assessments` | Assessments hub | No |
| `training.html` | `/training` | Training programs hub | No |
| `roles.html` | `/roles` | Career roles catalog | No |
| `ai_credits_pricing.html` | `/ai-credits-pricing` | AI credits pricing | No |
| `credit_dashboard.html` | `/credit-dashboard` | Credit dashboard | Yes |

---

## Auth

| Template | Route | Purpose |
|---|---|---|
| `register.html` | `/register` | Registration |
| `login.html` | `/login` | Login (with SSO options) |
| `forgot-password.html` | `/forgot-password` | Forgot password |
| `reset-password.html` | `/reset-password` | Reset password |
| `verify-email.html` | `/verify-email` | Email verification |
| `sso-success.html` | (SAML ACS) | SSO success page |
| `sso-error.html` | (SAML ACS) | SSO error page |

---

## AI Tools (12 viral + more)

| Template | Route | Purpose | Credits |
|---|---|---|---|
| `tools/index.html` | `/tools` | AI tools suite index | — |
| `tools/resume-roast.html` | `/tools/resume-roast` | Resume critique | 5 |
| `tools/ghost-bounty.html` | `/tools/ghost-bounty` | Ghost job detection | 10 |
| `tools/ref-check.html` | `/tools/ref-check` | Reference check | 10 |
| `tools/role-mirror.html` | `/tools/role-mirror` | Role match | 5 |
| `tools/bounty-swap.html` | `/tools/bounty-swap` | Referral bounty swap | 10 |
| `tools/micro-trial.html` | `/tools/micro-trial` | Micro-trial brief | 10 |
| `tools/offer-matcher.html` | `/tools/offer-matcher` | Offer comparison | 5 |
| `tools/ghost-job-shield.html` | `/tools/ghost-job-shield` | Ghost job shield | 10 |
| `tools/counter-offer.html` | `/tools/counter-offer` | Counter-offer analysis | 5 |
| `tools/ref-swap.html` | `/tools/ref-swap` | Reference swap | 10 |
| `tools/ghost-tracker.html` | `/tools/ghost-tracker` | Ghosted applications tracker | 5 |
| `tools/pitch-roast.html` | `/tools/pitch-roast` | Recruiter pitch roast | 5 |

---

## AI Products

| Template | Route | Purpose |
|---|---|---|
| `voice-to-web.html` | `/voice-to-web` | Voice → website |
| `cloud-waste-calculator.html` | `/cloud-waste-calculator` | Cloud waste calculator |
| `lock-in-breaker.html` | `/lock-in-breaker` | Vendor lock-in breaker |
| `lock-in-breaker-pricing.html` | `/lock-in-breaker-pricing` | Lock-In Breaker plans |
| `reverse-staffing.html` | `/reverse-staffing` | Reverse staffing |
| `code-quality-checker.html` | `/code-quality-checker` | Code quality checker |
| `auditbot.html` | `/auditbot` | AI security scanner |
| `digital-health-checker.html` | `/digital-health-checker` | Digital health checker |
| `neural-wireframe.html` | `/neural-wireframe` | Sketch → code |
| `napkin-challenge.html` | `/napkin-challenge` | Napkin to live challenge |
| `skill-twin.html` | `/skill-twin` | AI skill twin |
| `skill-check.html` | `/skill-check` | Free skill check |
| `globalize.html` | `/globalize` | Website localization |
| `revenue-leak-detector.html` | `/revenue-leak-detector` | Revenue leak detector |
| `micro-squads.html` | `/micro-squads` | Micro-squads |
| `scope-simulator.html` | `/scope-simulator` | Scope simulator |
| `agency-twin.html` | `/agency-twin` | AI agency twin |
| `burnout-calculator.html` | `/burnout-calculator` | Burnout calculator |
| `geo-compliance.html` | `/geo-compliance` | Geo-compliance shield |
| `contract-risk-radar.html` | `/contract-risk-radar` | Contract risk radar |
| `design-token-sentinel.html` | `/design-token-sentinel` | Design token sync |
| `brand-drift-inspector.html` | `/brand-drift-inspector` | Brand drift inspector |
| `legacy-shift.html` | `/legacy-shift` | Legacy modernization |
| `time-machine-checker.html` | `/time-machine-checker` | Time machine checker |
| `agent-ready.html` | `/agent-ready` | Agent-ready wrapper |
| `ai-commerce-scorecard.html` | `/ai-commerce-scorecard` | AI commerce scorecard |
| `silent-killer.html` | `/silent-killer` | Silent killer sentinel |
| `dead-link-auditor.html` | `/dead-link-auditor` | Dead link auditor |
| `ai-slop-quarantine.html` | `/ai-slop-quarantine` | AI-slop quarantine |
| `ai-contamination-detector.html` | `/ai-contamination-detector` | AI contamination detector |
| `developer-entropy.html` | `/developer-entropy` | Developer entropy |
| `team-entropy-scorecard.html` | `/team-entropy-scorecard` | Team entropy scorecard |

---

## Exam Prep

| Template | Route | Purpose |
|---|---|---|
| `exam-prep.html` | `/exam-prep` | Global exam prep (122 exams, has built-in mock test UI) |
| `mcq.html` | `/mcq` | MCQ assessment |
| `versant.html` | `/versant` | Versant English assessment |
| `companies.html` | `/company-patterns` | Company patterns (mock drive UI) |
| `advanced-assessment.html` | `/advanced-assessment` | Advanced assessment suite |
| `custom-assessment.html` | `/custom-assessment` | Custom assessment |
| `ai-generate-stack.html` | `/ai-generate-stack` | AI stack generator |
| `assessments.html` | `/assessments` | Unified assessments hub |

---

## Career Engine

| Template | Route | Purpose |
|---|---|---|
| `career-engine.html` | `/career-engine` | Career engine hub |
| `interview-prep.html` | `/interview-prep` | Interview prep landing |
| `interview-session.html` | `/interview-session/{session_id}` | Live interview session |
| `interview-results.html` | `/interview-results/{session_id}` | Interview results |
| `interview-dashboard.html` | `/interview-dashboard` | Interview history |
| `post-job.html` | `/post-job` | Post a job |
| `job-board.html` | `/job-board` | Job board listing |
| `track-application.html` | `/track-application` | Application tracking |
| `application-dashboard.html` | `/application-dashboard` | User's applications |
| `submit-referral.html` | `/submit-referral` | Submit a referral |
| `referral-dashboard.html` | `/referral-dashboard` | Referral stats |
| `training-engine.html` | `/training-engine` | Training engine |
| `online-classroom.html` | `/online-classroom` | Online classroom |
| `background-verification.html` | `/background-verification` | Background check |
| `career-v2.html` | `/career-center` | Career center v2 |
| `micro-internship.html` | `/micro-internship` | Micro-internships |
| `post-micro-project.html` | `/post-micro-project` | Post a micro-project |
| `ai-internship.html` | `/ai-internship` | AI internship program |
| `client-dashboard.html` | `/client-dashboard` | Client dashboard |
| `badge.html` | `/badge` | Verified badge |
| `candidate-signup.html` | `/candidate-signup` | Candidate pool signup |
| `profile-network.html` | `/profile-network` | Profile & network |
| `outreach.html` | `/outreach` | Outreach tools |
| `final-year-project.html` | `/final-year-project` | Final year project assistant |

---

## Training / Courses / LMS

| Template | Route | Purpose |
|---|---|---|
| `ai-courses.html` | `/ai-courses` | AI courses catalog (updated copy for EMI) |
| `trainers.html` | `/trainers` | Trainers listing |
| `post-course.html` | `/post-course` | Post a course |
| `request-training.html` | `/request-training` | Request training |
| `training.html` | `/training` | Training hub |
| `course-detail.html` | `/course/{course_name}` | Course detail + level selector + EMI |
| `my-course.html` | `/my-course/{enrollment_id}` | Lesson player + Pay-to-Unlock card |
| `my-courses.html` | `/my-courses` | User's enrolled courses |
| `certificate.html` | `/certificate/{certificate_id}` | Certificate view |
| `lms.html` | `/lms` | LMS hub |
| `student-suite.html` | `/student-suite` | AI student suite |
| `skill-check.html` | `/skill-check` | Skill check (also `/ai-generate-stack`) |

---

## Products

| Template | Route | Purpose |
|---|---|---|
| `products.html` | `/products/dokets-vouchai` | Product detail |
| `products-list.html` | `/products` | Products listing |
| `doketsrb.html` | `/doketsrb` | DoketsRB Suite |

---

## Free Tools & Calculators

| Template | Route | Purpose |
|---|---|---|
| `tools/index.html` | `/tools` | Tools index |
| All `tools/*.html` | (see AI Tools) | — |

---

## Assessments

| Template | Route | Purpose |
|---|---|---|
| `assessments.html` | `/assessments` | Assessments hub |
| `advanced-assessment.html` | `/advanced-assessment` | Advanced assessment |
| `custom-assessment.html` | `/custom-assessment` | Custom assessment |
| `reports.html` | `/reports` | Assessment reports |
| `skill-check.html` | `/skill-check` | Skill check |
| `skill-twin.html` | `/skill-twin` | Skill twin |
| `ai-bridge.html` | `/ai-assessment` | AI bridge assessment |
| `bridge.html` | `/bridge` | Bridge journey |

---

## Mock Drives (v2.2)

| Template | Route | Purpose | Notes |
|---|---|---|---|
| `companies.html` | `/mock-drive` | Company mock drives (18 companies) | Jinja template with base.html (v2.2) |
| `companies.html` | `/company-patterns` | (alias) | Same template |
| `companies.html` | `/companies` | (alias) | Same template — will be repurposed as brand directory in future |

---

## NA (North America) Module

| Template | Route | Purpose |
|---|---|---|
| `na-bench-staffing.html` | `/na-bench-staffing` | NA bench staffing |
| `na-client-signup.html` | `/na-client-signup` | NA client signup |

---

## Admin

| Template | Route | Purpose |
|---|---|---|
| `admin-login.html` | `/admin-login` | Admin login |
| `admin-unified.html` | `/admin-control`, `/admin-dashboard` | Admin control center |
| `admin-invoices.html` | `/admin-invoices` | Invoice management |
| `admin-cleanup-users.html` | `/admin/cleanup-users` | User cleanup |
| `admin-testimonials.html` | `/admin/testimonials` | Testimonials moderation |
| `admin-roles.html` | `/admin-roles` | Role management |

---

## Legal

| Template | Route | Purpose |
|---|---|---|
| `terms.html` | `/terms` | Terms & Conditions |
| `privacy.html` | `/privacy` | Privacy Policy |
| `refund.html` | `/refund` | Refund policy |
| `cookie-policy.html` | `/cookie-policy` | Cookie policy |
| `accessibility.html` | `/accessibility` | Accessibility statement |
| `sla.html` | `/sla` | SLA & uptime |
| `help.html` | `/help` | Help center |

---

## Blog / Content

| Template | Route | Purpose |
|---|---|---|
| `blog/index.html` | `/blog` | Blog listing |
| `blog/post.html` | `/blog/{slug}` | Blog post |
| `case-studies.html` | `/case-studies` | Case studies |
| `testimonials.html` | `/testimonials` | Client testimonials |

---

## Payments / Billing

| Template | Route | Purpose |
|---|---|---|
| `payments.html` | `/payments` | Payment methods info |
| `pricing.html` | `/pricing` | Pricing tiers |
| `ai_credits_pricing.html` | `/ai-credits-pricing` | AI credits plans |
| `credit_dashboard.html` | `/credit-dashboard` | User credit dashboard |
| `invoice.html` | `/invoice` | Invoice generator |
| `agreement.html` | `/agreement` | Agreement signing |

---

## Includes (reusable partials)

| Template | Purpose |
|---|---|
| `includes/*.html` | Header, footer, nav, modals, shared components |

---

## Templates with Payment Integration

| Template | Payment type |
|---|---|
| `pricing.html` | Razorpay (credits) |
| `ai_credits_pricing.html` | Razorpay (credits) |
| `course-detail.html` | Razorpay (course fee / EMI first installment) |
| `my-course.html` | Razorpay (EMI pay-to-unlock) |
| `payments.html` | Info page only |

---

## Layout Notes

- All templates extend `base.html` except legacy standalone pages
- `base.html` provides nav (with Mock Drives link), footer, GA4, scripts block
- Page-specific CSS goes in a `<style>` block at the top of `{% block content %}`
- Page-specific JS goes in `{% block scripts %}`
- Dark/light theme handled by CSS variables in `base.html`

---

*Keep in sync with MASTER-REFERENCE.md.*

---

## Recent Additions & Updates (Sessions 8-15, 2026-10-03)

This delta tracks templates added or materially updated since 2026-09-17.
When the main sections below drift too far, fold this back in.

### Added Since Last Update

| Template | Route | Purpose | Auth? |
|---|---|---|---|
| `booking.html` | `/booking/{slug}` | Public hosted booking page for Marketing AI outreach kits | No |
| `my-results.html` | `/my-results` | Cross-test results dashboard (feeds IELTS, Career Assessment, Mock Drives) | Yes |
| `my-tools.html` | `/my-tools` | History of AI Tool runs (persisted via tool_results.py) | Yes |
| `cbat.html` | `/cbat` | RRB ALP CBAT sub-tests (Session M-2) | Yes |
| `ai-assessment.html` | `/ai-assessment` | Career Assessment — 3-step wizard, 8 formats, adaptive, learning paths | Yes |
| `silent-killer.html` | `/silent-killer` | Silent-Killer Sentinel (was stub, now real URL monitoring) | Yes |
| `advanced-assessment.html` | (advanced assessment page) | Advanced assessment variant | Yes |
| `custom-assessment.html` | (custom assessment) | Custom topic-based assessment | Yes |
| `career-v2.html` | (career v2 engine) | Career Center v2 (alerts, saved jobs, offers, salary) | Yes |

### Materially Updated

| Template | Change | Session |
|---|---|---|
| `indian-language-ai.html` | Real MCQ scoring (was free-text) + auth on submit | Session 21 |
| `silent-killer.html` | Real URL monitoring (was `notifyMe` stub) | Session 9a |
| `legacy-shift.html` | Added Rs 4,999 migration plan tier | Session 8 |
| `university.html` | Real subscription flow (3 tiers), security fix | Session 8 |
| `lock-in-breaker.html` | Real paid tiers (migration + protection) | Session 4 |
| `auditbot.html` | Real paid tiers (one-time fix + subscribe) | Session 3 |
| `micro-squads.html` | Real sales-lead form (was notifyMe) | Session 5 |
| `marketing-ai.html` | Real booking-kit generation + host dashboard | Session 6 |
| `team-dashboard.html` | Real Pro subscription tier | Session 6 |
| `background-verification.html` | Real BGV tier | Session 6 |
| `design-token-sentinel.html` | Real paid tier | Session 6 |
| `developer-entropy.html` | Real paid tier | Session 6 |
| `geo-compliance.html` | Real contract + hiring tiers | Session 6 |
| `agency-twin.html` | Real paid tier | Session 6 |
| `reverse-staffing.html` | Real subscription tier | Session 6 |
| `skill-twin.html` | Real badge system (AA4d) | Session 7 |
| `lms.html` | Real course enrollment (reuses charvak_courses) | Session 7 |
| `ai-bridge.html` / `bridge.html` | `/ai-assessment` no longer renders ai-bridge.html | Session 10 |
| `pricing.html` | Updated plan pricing (Starter Rs 199 / Pro Rs 499 / Premium Rs 999) | Session C8 |

### Deleted

None removed. `scripts/one-off/*` scripts were archived (Session 14) but that folder held Python scripts, not templates.

### Notes

- Template count went from ~180 (2026-09-17) to 182 (2026-10-03)
- Full 159-root + 23-subfolder inventory is available by running the script in the section below if added in the future



## Session 24 - Admin Client Roles (2026-10-05)

Two new admin pages added.

| Template | Route | Purpose | Auth? |
|---|---|---|---|
| `admin-client-roles.html` | `/admin/client-roles` | Client roles list with applicant counts + filters | admin_auth_guard |
| `admin-client-role-detail.html` | `/admin/client-roles/{role_id}` | Role detail + ranked applicants + view/download modal | admin_auth_guard |

### Notes

- Both pages fetch data from `/api/admin/client-roles/*` endpoints
- Detail page has a modal in the `{% block modal %}` slot
- Applicant row actions use `data-action` + event delegation
- Refresh buttons rely on `window.loadRoles` / `window.loadAll`

## Session 42 additions (2026-10-09)

| Template | Route | Purpose | Auth? |
|---|---|---|---|
| placement-prep-2026.html | /placement-prep-2026 | Campus placement landing (Nov-Dec 2026) | No |
| mock-result.html | /mock-result/{session_id} | Shareable mock drive result | No |

### Materially updated in Session 42

- readiness.html - quiet integrity badge, "Your Score" cell, CTA polish
- readiness-check.html - meta description + OG tags for social previews
- ai-courses.html - AI Course Designer card + "Your custom courses"
- companies.html - URL preselect + login gate + pattern_id passthrough
- login.html - honors ?next= with sanitization; Register link carries it
- register.html - honors ?next= after successful registration
- cbat.html - local charvakFetch removed (now in base.html)
- base.html - global charvakFetch helper

## Session 43 additions (2026-10-12)

Active roadmap for the current work: see `TRACK-A-B-PLAN.md`.

### Session 43 shipped

- Integrity fact-panel certificate redesign (facts, not verdicts)
- FYP discipline-aware topic generation (MBA/commerce support)
- 8 MBA courses generated and promoted to public catalog

### Materially updated in Session 43

- readiness.html - fact-based integrity panel (replaced verdict badge)
- final-year-project.html - MBA-calibrated topic generation
- ai-courses - 8 MBA courses added to catalog
- readiness-check.html - dynamic CTA (Session 42-6)
- ai-assessment.html - clean integrity fact panel

### Track A pending (see TRACK-A-B-PLAN.md)

- Batch A1: Small cleanup (Render password, PAYPAL_MODE, flicker, CI hook)
- Batch A2: Certificate round 3 (QR, watermark, i18n)
- Batch A3: FYP features (Citation, Milestone Roadmap, Plagiarism, Refine)
- Batch A4: Personalized training views
- Batch A5: DoketsRB bidirectional sync

### Track B pending (after A2)

- B1-B4: CSR skilling business model - see TRACK-A-B-PLAN.md

<!-- BEGIN SESSION-48 -->

## Session 48 Additions - Cohort Mode

| Template | Route | Purpose | Auth? |
|---|---|---|---|
| cohorts.html | /cohorts | Landing with create/join modals + my-cohorts list | Yes (JS-gated) |
| cohort-detail.html | /cohorts/{cohort_id} | Leaderboard + share code + refresh | Yes (JS-gated) |

### Notes

- /cohorts/join/{join_code} is a 302 redirect to /cohorts?join={code}
- The ?join= parameter auto-opens the join modal with code pre-filled
- Passport page (/passport/{handle}) has a new "My Cohorts" section
  visible only to the authenticated owner

### Nav integration

- Dropdown: "My Cohorts" between "My Career Center" and "Job Board"
- Footer: "My Cohorts" link in Quick Links section

<!-- END SESSION-48 -->

## Employer Portal (Session 51, 2026-10-19)

The B2B verification surface. Public, no auth required.

| Template | Route | Purpose | Auth? |
|---|---|---|---|
| `employer-dashboard.html` | `/employer/dashboard` | B2B portal: quick-verify input + browse public passports with tier filters + pagination | No (public) |
| `employer-verify.html` | `/employer/verify/{handle}` | Single-passport verification card: score + tier + component bars + integrity badge + hash copy + raw JSON link | No (public) |

**Backing API:**

- `GET /api/passport/public/list` - paginated public passport list (60/min, public)
  - Query: `?tier=<foundation|developing|solid|strong|elite>&limit=20&offset=0`
  - Response: `{status, passports: [...], total, page, pages, tier}`
  - No PII - aggregates only (handle, charvak_score, score_tier, display_name, score_updated_at)

**Nav integration:**

- "For Employers" link in top nav (`base.html` line 344), teal CTA
  styling matching Exam Prep / Readiness Check / Open Roles

**Engine:**

- `passport_engine.list_public_passports(tier, limit, offset)` - filters
  by `is_public = TRUE`, ordered by `charvak_score DESC`

**Verified on prod (2026-10-19):**

- `/employer/dashboard` -> 200, renders @hr-6201 (442, developing)
- `/employer/verify/hr-6201` -> 200, full card with real data
- `/api/passport/public/list` -> correct JSON shape

**Discovery funnel:**

- Employer lands on dashboard
- Quick-verify by handle OR browse public talent pool
- Click card -> full verify page with cryptographic proof
- Share verify URL with team (or open raw JSON for API integration)

## Certificate-as-a-Service (Session 52, 2026-10-19)

Bulk verification API for institutional buyers (universities, placement
cells, coaching centers). Completes Wave 2.

| Template | Route | Purpose | Auth? |
|---|---|---|---|
| `employer-cas.html` | `/employer/cas` | Landing page: hero, 4 pricing tiers, API docs, request form | No (public) |

**Backing API:**

- `POST /api/cas/verify-batch` - bulk verify up to 100 certificate hashes
  - Header: `X-CAS-Key: cas_<32-hex>`
  - Body: `{"certificate_hashes": ["hash1", "hash2", ...]}`
  - Returns: `{status, total, valid, invalid, results: [...]}`
  - Rate limit: 60/min per IP
  - Quota per tier: 500 / 5,000 / 50,000 / unlimited (monthly)

- `POST /api/cas/request-key` - university requests API key
  - Body: `{institution_name, contact_name, contact_email}`
  - Returns: `{status: "pending", key_id, message}`
  - Rate limit: 5/min per IP
  - Admin must approve before key works

**Engine (`cas_engine.py`, new):**

- `verify_certificate_by_hash(hash)` - single cert via HMAC
- `verify_batch(hashes, api_key)` - up to 100, quota-checked
- `request_api_key(institution, contact_name, contact_email)`
- `approve_api_key(key_id)` - admin action
- `check_api_key(raw_key)` - validates + rate-checks
- `list_api_keys(active_only=True)` - admin view
- SHA-256 hashed API key storage, approval-gated (is_active=FALSE default)
- Self-healing DDL for `charvak_cas_api_keys`

**Table (`charvak_cas_api_keys`):**

- key_id (TEXT PK, format `KEY-XXXXXXXXXXXXXXXX`)
- institution_name, contact_name, contact_email
- api_key_hash (SHA-256 hex, UNIQUE)
- tier (pilot / department / campus / university)
- monthly_quota (500/5000/50000/0)
- calls_this_month, last_call_at
- is_active (FALSE until admin approves)
- created_at, approved_at, expires_at

**Pricing tiers (as of Session 52):**

| Tier | Price | Verifications/year |
|---|---|---|
| Pilot | Free | 500 (1 batch) |
| Department | Rs 49,999 | 5,000 |
| Campus | Rs 1,99,999 | 50,000 |
| University | Rs 4,99,999 | Unlimited |

**Discovery funnel:**

- Employer lands on `/employer/dashboard` (Session 51)
- Sees CTA "Are you a university? Get bulk verification" (line 51)
- Lands on `/employer/cas` - sees pricing + API docs + request form
- Submits request -> `KEY-XXXX` reference shown
- Admin approves (currently via DB, Session 53 will add `/admin/cas-keys`)
- University uses API key in `POST /api/cas/verify-batch`

**Verified on prod (2026-10-19):**

- `GET /employer/cas` -> 200
- `POST /api/cas/verify-batch` (no key) -> 401
- Engine smoke test: 10/10 checks pass
- Request form submits successfully (verified locally)

**Unblocks:** Track C (Amrita CDC pilot) - Prof. Raj can request key,
admin approves, Amrita batch-verifies 500 students in one call.
