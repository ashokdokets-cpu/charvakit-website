# Charvak — Pages Inventory

**Last updated:** 2026-09-13
**Version:** v1.1-stable-20260913

Every template in `templates/`. Grouped by purpose.

---

## Root Templates

| Template | Route | Purpose | Auth? |
|---|---|---|---|
| `base.html` | (layout) | Master layout — nav, footer, scripts | — |
| `index.html` | `/` | Homepage — hero, features, products, testimonials | No |
| `about.html` | `/about` | About Charvak | No |
| `team.html` | `/team` | Team page | No |
| `careers.html` | `/careers` | Careers listing | No |
| `contact.html` | `/contact` | Contact form + info | No |
| `capabilities.html` | `/capabilities` | Mission-driven capabilities sheet | No |
| `help.html` | `/help` | Help / FAQ | No |
| `pricing.html` | `/pricing` | Pricing page (INR + multi-currency) | No |
| `ai_credits_pricing.html` | `/ai-credits-pricing` | AI credits plans + purchase | Optional |
| `credit_dashboard.html` | `/credit-dashboard` | User's credit balance + usage | Yes |

---

## Auth

| Template | Route | Purpose |
|---|---|---|
| `login.html` | `/login` | Login form |
| `register.html` | `/register` | Registration form |
| `forgot-password.html` | `/forgot-password` | Request password reset |
| `reset-password.html` | `/reset-password?token=...` | Reset form |
| `verify-email.html` | `/verify-email?token=...` | Verification result page |
| `admin-login.html` | `/admin-login` | Admin-only login |

---

## AI Tools

| Template | Route | What it does |
|---|---|---|
| `tools.html` | `/tools` | AI Tools Suite overview |
| `resume-roast.html` | `/resume-roast` | Resume critique |
| `role-mirror.html` | `/role-mirror` | Role fit analysis |
| `ghost-bounty.html` | `/ghost-bounty` | Bounty tracking |
| `ref-check.html` | `/ref-check` | Reference checks |
| `ghost-tracker.html` | `/ghost-tracker` | Ghost job detection |
| `offer-matcher.html` | `/offer-matcher` | Offer comparison |
| `pitch-roast.html` | `/pitch-roast` | Pitch critique |
| `ref-swap.html` | `/ref-swap` | Referral matching |
| `bounty-swap.html` | `/bounty-swap` | Bounty exchange |
| `counter-offer.html` | `/counter-offer` | Counter-offer builder |
| `ghost-job-shield.html` | `/ghost-job-shield` | Job fraud detection |
| `micro-trial.html` | `/micro-trial` | Micro-trial projects |
| `voice-to-web.html` | `/voice-to-web` | Voice-to-website |
| `neural-wireframe.html` | `/neural-wireframe` | AI wireframes |
| `outreach.html` | `/outreach` | Outreach tools |
| `student-suite.html` | `/student-suite` | Student tools bundle |
| `indian-language-ai.html` | `/indian-language-ai` | 12 Indian languages |
| `marketing-ai.html` | `/marketing-ai` | Marketing content gen |

---

## Exam Prep

| Template | Route | What it does |
|---|---|---|
| `exam-prep.html` | `/exam-prep` | Exam prep hub |
| `exam-analytics.html` | `/exam-analytics` | User's performance |
| `mcq.html` | varies | MCQ practice/mock |
| `practice-test.html` | varies | Practice mode |
| `mock-test.html` | varies | Mock exam mode |
| `results.html` | varies | Result display |

---

## Career Engine

| Template | Route | What it does |
|---|---|---|
| `career-engine.html` | `/career-engine` | Career engine overview |
| `career-v2.html` | `/career-v2` | v2 career flow |
| `job-board.html` | `/job-board` | Public job listings |
| `post-job.html` | `/post-job` | Employer: post a job |
| `post-micro-project.html` | `/post-micro-project` | Post a micro-project |
| `interview-prep.html` | `/interview-prep` | Interview preparation |
| `micro-internship.html` | `/micro-internship` | Micro-internship program |
| `ai-internship.html` | `/ai-internship` | AI internship |
| `hire-talent.html` | `/hire-talent` | Employer landing |
| `candidate-signup.html` | `/candidate-signup` | Candidate signup |
| `developer-signup.html` | `/developer-signup` | Developer signup |
| `na-client-signup.html` | `/na-client-signup` | NA client signup |

---

## Training / Courses / LMS

| Template | Route | What it does |
|---|---|---|
| `training.html` | `/training` | Training hub |
| `training-engine.html` | `/training-engine` | Training engine UI |
| `ai-courses.html` | `/ai-courses` | AI courses catalog |
| `lms.html` | `/lms` | Learning management |
| `course-player.html` | varies | Lesson player |
| `monetized-training.html` | varies | Paid training |

---

## Products

| Template | Route | What it does |
|---|---|---|
| `products.html` | `/products` | All products overview |
| `dokets-vouchai.html` | `/products/dokets-vouchai` | VouchAI product page |
| `doketsrb.html` | `/doketsrb` | DoketsRB product page |
| `lock-in-breaker-pricing.html` | `/lock-in-breaker` | Lock-In Breaker |
| `auditbot.html` | `/auditbot` | AuditBot |
| `skill-twin.html` | `/skill-twin` | Skill-Twin |
| `micro-squads.html` | `/micro-squads` | Micro-Squads |
| `globalize.html` | `/globalize` | Globalize.ai |
| `agency-twin.html` | `/agency-twin` | Agency-Twin |
| `geo-compliance.html` | `/geo-compliance` | Geo-Compliance |
| `design-token-sentinel.html` | `/design-token-sentinel` | Design-Token Sentinel |
| `legacy-shift.html` | `/legacy-shift` | Legacy-Shift |
| `agent-ready.html` | `/agent-ready` | Agent-Ready |
| `silent-killer.html` | `/silent-killer` | Silent-Killer |
| `ai-slop-quarantine.html` | `/ai-slop-quarantine` | AI-Slop Quarantine |
| `developer-entropy.html` | `/developer-entropy` | Developer Entropy |

---

## Free Tools

| Template | Route | What it does |
|---|---|---|
| `cloud-waste-calculator.html` | `/cloud-waste-calculator` | Cloud cost estimator |
| `code-quality-checker.html` | `/code-quality-checker` | Code quality audit |
| `digital-health-checker.html` | `/digital-health-checker` | Digital health score |
| `skill-check.html` | `/skill-check` | Free skill assessment |
| `revenue-leak-detector.html` | `/revenue-leak-detector` | Revenue leak finder |
| `scope-simulator.html` | `/scope-simulator` | Project scope tool |
| `burnout-calculator.html` | `/burnout-calculator` | Team burnout score |
| `contract-risk-radar.html` | `/contract-risk-radar` | Contract risk scan |
| `brand-drift-inspector.html` | `/brand-drift-inspector` | Brand consistency |
| `time-machine-checker.html` | `/time-machine-checker` | Historical analysis |
| `ai-commerce-scorecard.html` | `/ai-commerce-scorecard` | E-commerce scoring |
| `dead-link-auditor.html` | `/dead-link-auditor` | Dead link scanner |
| `ai-contamination-detector.html` | `/ai-contamination-detector` | AI-slop detection |
| `team-entropy-scorecard.html` | `/team-entropy-scorecard` | Team entropy metric |

---

## Assessments

| Template | Route | What it does |
|---|---|---|
| `assessments.html` | `/assessments` | Assessment hub |
| `assessment.html` | varies | Generic assessment |
| `assessment-complete.html` | varies | Completion state |
| `advanced-assessment.html` | varies | Advanced mode |
| `company-assessment.html` | varies | Company-specific |

---

## NA (North America) Module

| Template | Route | What it does |
|---|---|---|
| `na-bench-staffing.html` | `/na-bench-staffing` | NA bench staffing |
| `reverse-staffing.html` | `/reverse-staffing` | Reverse staffing |
| `bridge.html` | `/bridge` | Bridge program |
| `final-year-project.html` | `/final-year-project` | FYP hub |

---

## Admin

| Template | Route | What it does |
|---|---|---|
| `admin-unified.html` | `/admin-control` | Unified admin dashboard |
| `admin-cleanup-users.html` | varies | User cleanup page |
| `admin-role-management.html` | varies | Role CRUD |
| `admin-invoices.html` | varies | Invoice list |
| `admin-analytics.html` | varies | Analytics charts |

---

## Legal

| Template | Route | What it does |
|---|---|---|
| `privacy.html` | `/privacy` | Privacy policy (GDPR/CCPA/LGPD/PIPEDA) |
| `terms.html` | `/terms` | Terms & conditions |
| `refund.html` | `/refund` | Refund & cancellation |
| `cookie-policy.html` | `/cookie-policy` | Cookie policy |
| `accessibility.html` | `/accessibility` | Accessibility statement |

---

## Blog / Content

| Template | Route | What it does |
|---|---|---|
| `blog.html` | `/blog` | Blog index |
| `blog-post.html` | varies | Individual post |
| `case-studies.html` | `/case-studies` | Case studies |
| `testimonials.html` | `/testimonials` | Customer testimonials |
| `events.html` | `/events` | Events listing |
| `companies.html` | `/companies` | Company directory |
| `how-it-works.html` | `/how-it-works` | Explainer page |

---

## Payments / Billing

| Template | Route | What it does |
|---|---|---|
| `payments.html` | `/payments` | Payment hub |
| `payment-success.html` | varies | Post-payment confirmation |
| `payment-failed.html` | varies | Failure page |
| `invoice.html` | varies | Invoice view |

---

## Includes (reusable partials)

| Template | Used by | What it renders |
|---|---|---|
| `includes/nav.html` | base.html | (may be inlined) |
| `includes/footer.html` | base.html | (may be inlined) |
| `includes/payment-scripts.html` | base.html | Payment SDK loaders |
| `includes/currency-updater.html` | base.html | Currency conversion |
| `includes/cookie-banner.html` | base.html | Cookie consent |
| `includes/whatsapp-widget.html` | base.html | WhatsApp float button |

---

## Templates with Payment Integration

These templates reference Razorpay/PayPal SDK directly:

- `pricing.html`
- `ai_credits_pricing.html`
- `student-suite.html`
- `voice-to-web.html`
- `neural-wireframe.html`
- `bridge.html`
- `doketsrb.html`
- `lock-in-breaker-pricing.html`
- `payments.html`
- `na-bench-staffing.html`
- `reverse-staffing.html`
- `outreach.html`
- `skill-check.html`
- `final-year-project.html`
- `indian-language-ai.html`
- `training-engine.html`
- `post-course.html`
- `post-job.html`

**Note:** SDK loading is centralized in `base.html` with `defer`. Pages don't need to add their own `<script src="razorpay...">`.

---

## Layout Notes

### `base.html` structure
- `{% block title %}` — page title
- `{% block description %}` — meta description
- `{% block content %}` — main content area
- `{% block scripts %}` — page-specific JS (runs **after** Bootstrap loads)

### Standard page template
```jinja
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block description %}Meta description{% endblock %}
{% block content %}
    <!-- page HTML -->
{% endblock %}
{% block scripts %}
<script>
    // page-specific JS that needs Bootstrap or Razorpay
</script>
{% endblock %}