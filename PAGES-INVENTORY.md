# Charvak — Pages Inventory

**Last updated:** 2026-09-17
**Version:** v2.2-mock-drives-20260917

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