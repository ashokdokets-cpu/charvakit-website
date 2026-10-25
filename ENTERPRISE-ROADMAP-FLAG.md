# CHARVAK ENTERPRISE ROADMAP — FLAGGED 2026-10-26

**Strategic goal:** Beat VIVA360 + be enterprise-ready in 3-6 months

**Positioning:** Charvak = placement OS for Indian colleges + enterprises
**Advantage over VIVA360:** Placement (not just screening) + B2C funnel + micro-internship trial + India-first + HMAC credentials

---

## 8 Features to Build (Ranked)

### Tier 1 — CRITICAL (build first)

**F1 — Verified Scorecard Artifact** [1 session]
- Public, shareable, no-login candidate scorecard URL
- Structure: overall score + 5-axis skill breakdown + work sample + integrity + credential + HMAC verify link + trial recommendation
- New: scorecard_engine.py, templates/scorecard.html, charvak_scorecards table
- Beats VIVA: HMAC-verifiable (not just explainable) + ties to trial

**F2 — Enterprise Compliance Page** [0.5 session, writing only]
- /compliance route
- Content: audit trail, explainable scoring, bias audit, NYC Law 144, EU AI Act, India DPDP, GDPR, SOC 2 roadmap, data residency
- Beats VIVA: India-specific (DPDP, DigiLocker) + Aadhaar-lite

**F3 — Recruiter Screen Agent** [2 sessions]
- Recruiter pastes JD -> auto-outreach -> chat captures notice/CTC/auth -> auto-schedule
- New: recruiter_screen_engine.py, charvak_screen_sessions, charvak_screen_conversations, templates/screen-*.html
- Build on: chatbot_engine, jd_parser_engine
- Beats VIVA: uses JD parser for deeper context + 34 languages

### Tier 2 — IMPORTANT (2-3 sessions)

**F4 — Enterprise Recruiter Dashboard** [1 session]
- Single dashboard for all roles/pipelines/analytics
- Multi-level view (freshers + laterals)
- Bulk actions, CSV/PDF export
- Built on candidate_profile_engine + client_roles

**F5 — AI Communication Assessment** [1 session]
- 5-min voice assessment, AI scores fluency/clarity/structure
- Reuses cbt_versant + ielts_engine
- Feeds into scorecard
- Beats VIVA: voice-based (they're text-only)

**F6 — Advanced Integrity (Biometric)** [1-2 sessions]
- DigiLocker ID verify (India-specific)
- Liveness detection (camera-based)
- Video proctoring for coding rounds
- Requires legal review (biometric data is sensitive)
- Beats VIVA: DigiLocker integration + privacy-first (record only during question)

### Tier 3 — STRATEGIC (after first enterprise client)

**F7 — Multi-Region Data Residency** [2-3 sessions]
- EU, UK Postgres deployments
- Region-aware routing
- Trigger: first EU/UK enterprise client

**F8 — ATS Integrations (Greenhouse, Lever, Workable)** [2-3 sessions each]
- Bidirectional webhook sync
- Trigger: first enterprise client asks

---

## What NOT to Build (Don't Copy VIVA)

- Do not build VIVA Match (6-axis resume scoring) — commodity
- Do not build VIVA Source — hasn't launched
- Do not adopt 'AI Operating System' positioning — generic
- Do not lean on 'candidate dignity' — enterprise cares about compliance

---

## Strategic Differentiation (Emphasize in Enterprise Pitches)

1. We PLACE, they SCREEN — different product, different price
2. We have 674 B2C users as lead-gen, they don't
3. We are India-first (34 languages, DPDP, TDS/PF, DigiLocker)
4. We have micro-internship trial, they don't
5. We have HMAC verifiable credentials, they have explainable scores
6. We do assess -> trial -> place -> certificate, they do assess only

---

## Recommended Wave Plan

Wave 1 (2 weeks, 3-4 sessions): F1 + F2 + F3
  - After Wave 1: Credible enterprise pitch

Wave 2 (2 weeks, 2-3 sessions): F4 + F5 + optional F6
  - After Wave 2: Deeper than VIVA for Indian market

Wave 3 (triggered by client): F7 + F8
  - After Wave 3: Head-to-head with VIVA360 globally

---

## Trigger to Start Wave 1

Trigger: Any of these
  - First enterprise client says 'we need more than assessments'
  - VIVA360 name comes up in a sales conversation
  - You decide to actively target enterprises (currently B2C + college focus)

Until then: focus on 10 warm emails + first paying college client

---

**Last updated:** 2026-10-26
**Owner:** Bhavya