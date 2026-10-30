# CHARVAK ATS EXTENSION — FLAGGED FOR LATER BUILD

**Flagged:** 2026-10-31 (Session 106 close)
**Status:** NOT STARTED — demand-triggered
**Effort:** 3 sessions (~3 weeks calendar time)
**Trigger:** First employer asks "we'll drop [ATS name] and use Charvak as our only ATS if you build X"

---

## THE STRATEGIC POSITION

**Do NOT build a full ATS speculatively.**

Charvak already has ~70% of what an ATS does — and 100% of what makes it unique:
- Candidate database (190+ candidates, 48 columns)
- Job/requisition management (real CBREX roles)
- Application tracking (status pipeline)
- Recruiter dashboard (117 KB HTML, live)
- AI screening agent (F3 Screen Agent)
- JD-to-Shortlist (parse → rank → match)
- Verified skill certificates (HMAC)
- 518-skill calibration
- Hire tracking (avg CTC, time-to-hire)
- Micro-internships (12 live projects)
- Bulk certificate verification API

**What's missing** is the commodity 30% that Greenhouse, Lever, and Workable already do well:
- Email inbox integration
- Calendar sync
- Offer letter generation
- Background check integration
- Payroll handoff
- Kanban drag-drop UI
- Boolean search
- Team collaboration features

**The moat is the verification layer, not the ATS.** No competitor has both.

---

## WHY NOT BUILD SPECULATIVELY

1. **Greenhouse/Lever/Workable have 10+ years of engineering** on the commodity ATS features
2. **Every enterprise buyer already has an ATS** — they don't want another one
3. **Building it costs 3 sessions** that could go to close actual customers
4. **The pitch is "keep your ATS, add Charvak as verification layer"** — not "replace your ATS"
5. **No customer has asked for it yet** — no paying customer has said "we need you to be our only ATS"

**Trigger only when a paying customer explicitly asks.**

---

## THE TRIGGER (DO NOT BUILD UNTIL THESE FIRE)

Build ONLY when ANY of these happen:

1. **First paying enterprise customer says** "we'll drop our ATS and use Charvak as our only ATS if you build [specific feature]"
2. **Deal in negotiation > ₹10L ARR** requires Charvak to be the primary ATS (not just verification layer)
3. **First candidate actively loses an opportunity** because Charvak can't send emails/schedule interviews
4. **5+ employers explicitly ask** "can I manage my entire hiring pipeline in Charvak?"

**Until any of these, Charvak = verification layer that complements their ATS. Not replacement.**

---

## SESSION 108 — Email + Calendar Integration

**Effort:** 1 session (~6-8 hours)
**Priority:** Highest (unblocks the most workflows)

### What It Builds

**Email Integration:**
- Send emails from within Charvak (reuse `email_engine.py` + SendGrid)
- Templates: interview invitation, offer, rejection, follow-up
- Merge fields: candidate_name, role_title, company, interview_date, custom_fields
- Send from recruiter's own email (SendGrid verified sender)
- Full email thread visible in the candidate's ATS profile
- Inbox view (received replies) — via SendGrid inbound parse webhook
- Attachments supported (offer letters, JD, comp info)

**Calendar Integration:**
- Google Calendar OAuth (Schedule interviews)
- Outlook/Microsoft 365 OAuth (for enterprise buyers)
- Availability slot proposal — candidate picks from recruiter's free slots
- Auto-generate Google Meet or Teams link
- Interview reminders: 24h + 1h before
- Auto-update candidate pipeline stage on interview scheduled

### API / Files

- `email_engine.py` — extend with template + merge field methods
- `calendar_engine.py` (new) — Google + Outlook OAuth + slot management
- `charvak_email_threads` table (new) — thread tracking per candidate
- `charvak_interview_schedules` table (new) — calendar events + reminders
- `templates/recruiter/inbox.html` — inbox view
- `templates/recruiter/candidate-email.html` — thread view
- `templates/recruiter/schedule-interview.html` — slot picker
- `POST /api/email/send` — send with template
- `GET /api/email/threads/{candidate_id}` — thread list
- `POST /api/calendar/slots` — create interview slots
- `POST /api/calendar/book` — candidate books slot
- `POST /webhook/sendgrid-inbound` — parse replies into threads
- `GET /api/calendar/sync` — sync from Google/Outlook

### Dependencies

- `SENDGRID_API_KEY` (already set)
- `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` (need to add to Render env)
- `MICROSOFT_CLIENT_ID` + `MICROSOFT_CLIENT_SECRET` (need to add for Outlook)
- SendGrid Inbound Parse setup (5-min dashboard config)

---

## SESSION 109 — Offer Letters + Background Checks

**Effort:** 1 session (~6-8 hours)
**Priority:** Medium (needed for end-to-end ATS replacement)

### What It Builds

**Offer Letters:**
- Template management (per role, per level)
- Merge fields: candidate_name, role_title, level, CTC, joining_date, benefits
- PDF generation (reuse `pdf_engine.py`)
- E-sign workflow — DocuSign lite or HelloSign
- Auto-track status: sent, viewed, signed, declined
- Version history (revised offers)
- Auto-notify HR + candidate on signing

**Background Checks:**
- Checkr API integration (or similar India-friendly vendor like AuthBridge)
- Pre-employment check packages: identity, education, employment, criminal
- Consent capture before check (DPDP compliance)
- Result callback + auto-update application status
- Manual review queue for failed checks

### API / Files

- `offer_letter_engine.py` (new) — template + merge + PDF
- `esign_engine.py` (new) — DocuSign/HelloSign adapter
- `bgv_engine.py` (new) — Checkr/AuthBridge adapter
- `charvak_offers` table (new) — offer lifecycle
- `charvak_offer_templates` table (new) — template library
- `charvak_bgv_requests` table (new) — background check tracking
- `templates/recruiter/offer-builder.html` — offer creation UI
- `templates/recruiter/offer-tracking.html` — offer status dashboard
- `POST /api/offers/create` — generate offer
- `POST /api/offers/{offer_id}/send` — send for e-sign
- `POST /webhook/esign` — e-sign callback
- `POST /api/bgv/initiate` — start background check
- `POST /webhook/bgv` — background check result callback

### Dependencies

- DocuSign or HelloSign account (~₹2K/month + per-signature cost)
- Checkr or AuthBridge account (~₹500-2000 per check)
- Legal review for DPDP consent (India biometric/background data)
- Legal review for NYC Law 144 (US jurisdiction)

---

## SESSION 110 — Advanced Pipeline UI

**Effort:** 1 session (~6-8 hours)
**Priority:** Lowest (nicety for power users)

### What It Builds

**Kanban Board:**
- Drag-drop between pipeline stages
- Stage columns: Applied → Screening → Interview → Offer → Hired → Rejected
- Multi-role board (grouped by role)
- Bulk select + bulk move
- Undo on drag (10-second window)
- Filters: role, source, score range, integrity status, date range

**Boolean Search:**
- Query language: `python AND (react OR vue) AND score>75 AND NOT rust`
- Search across candidate profile, verified skills, certificates, custom fields
- Saved searches (per recruiter, per role)
- Search result sorting: relevance, score, recency

**Custom Fields per Role:**
- Each role defines its own fields (e.g., "notice_period", "current_ctc", "relocation_ok")
- Field types: text, number, date, boolean, choice, multichoice
- Field values stored per application (not per candidate)
- Admin UI to add/remove/reorder fields per role
- Validation rules (required, min/max, regex)

**Team Collaboration:**
- Assign candidates to specific recruiters
- @mention recruiters in candidate notes
- Real-time notifications (WebSocket or polling)
- Activity feed: who did what, when
- Permission levels: owner, admin, member, viewer

### API / Files

- `pipeline_engine.py` (new) — kanban + stage management
- `search_engine.py` (new) — boolean query parser + execution
- `custom_fields_engine.py` (new) — per-role field schema
- `collaboration_engine.py` (new) — assignments + mentions
- `charvak_pipeline_stages` table (new)
- `charvak_role_custom_fields` table (new)
- `charvak_field_values` table (new)
- `charvak_candidate_assignments` table (new)
- `charvak_mentions` table (new)
- `charvak_activity_feed` table (new)
- `templates/recruiter/pipeline-kanban.html` — kanban view
- `templates/recruiter/search-advanced.html` — boolean search
- `templates/recruiter/role-fields-editor.html` — custom fields
- `GET /api/pipeline/{role_id}` — kanban data
- `POST /api/pipeline/move` — move candidate between stages
- `POST /api/search/advanced` — boolean search
- `POST /api/roles/{role_id}/fields` — add custom field
- `POST /api/candidates/{candidate_id}/assign` — assign to recruiter
- `POST /api/candidates/{candidate_id}/mention` — @mention

### Dependencies

- `chart.js` (already loaded)
- SortableJS for drag-drop (add via CDN or npm)
- WebSocket support (optional; can use polling initially)

---

## TOTAL EFFORT IF BUILT

| Session | Est. Hours | Est. Value |
|---|---|---|
| 108 — Email + Calendar | 6-8 hrs | Unblocks end-to-end workflow |
| 109 — Offers + BGV | 6-8 hrs | Enables full hiring lifecycle |
| 110 — Advanced Pipeline UI | 6-8 hrs | Improves UX for power users |
| **Total** | **18-24 hrs** | **Can be primary ATS for enterprise** |

**Trigger:** Only when a paying customer says "we'll drop our ATS if you build X."

---

## WHAT THE PITCH LOOKS LIKE AT EACH STAGE

### Today (before Sessions 108-110)
> "Keep using your ATS. Charvak plugs into it and adds verified skill data to every candidate. Your ATS is your pipeline. Charvak is your trust layer."

### After Session 108 (email + calendar)
> "Charvak can now handle the entire hiring workflow from JD to offer. Your ATS is optional — Charvak does 80% of what it does, plus verified skills."

### After Session 109 (offers + BGV)
> "Charvak is now a complete hiring solution. Sign offers, run background checks, all in one place. If you want to keep your ATS, we still plug in. If you want to drop it, we're ready."

### After Session 110 (advanced pipeline)
> "Charvak is the only ATS with verified skill intelligence built in. Greenhouse can't do what we do. We can do what Greenhouse does."

---

## THE RISK REGISTER

| Risk | Mitigation |
|---|---|
| Building 108-110 speculatively wastes 3 sessions | Only build when trigger fires (paying customer asks) |
| DocuSign + Checkr costs ~₹15K/month | Pass to customer as add-on, not built-in cost |
| Legal review for BGV (DPDP) takes weeks | Start legal review 1 month before Session 109 |
| Customer's ATS may have custom workflows not replicable | Position as "Charvak-native ATS for new roles" not "replace existing" |
| Kanban UI complexity in vanilla JS | Use SortableJS library (battle-tested) |

---

## THE COMPETITIVE LANDSCAPE

| Competitor | Has ATS? | Has Verified Skills? | Charvak's Advantage |
|---|---|---|---|
| **Greenhouse** | Full ATS | ❌ No | Verified skill certs + HMAC + 518 calibration |
| **Lever** | Full ATS | ❌ No | Same + micro-internships |
| **Workable** | Full ATS | ❌ No | Same + FYP + candidate side |
| **HackerRank** | Assessment only | ✅ Assessment | No ATS — Charvak has both |
| **TestGorilla** | Assessment only | ✅ Test library | No ATS — Charvak has both |
| **VIVA360** | AI screening | ⚠️ Explainable only | Not HMAC-verifiable |
| **Charvak** | Verified layer + partial ATS | ✅ HMAC + 518 skills | **Category-of-one** |

**Every competitor is either ATS-without-verification or verification-without-ATS. Charvak can be both. That's the moat.**

---

## THE DECISION CRITERIA

**Build Sessions 108-110 IF AND ONLY IF:**

- [ ] 1 paying customer explicitly asks for full ATS functionality
- [ ] That customer has a contract value > ₹10L ARR
- [ ] They've committed to dropping their current ATS
- [ ] They've agreed to a 3-month rollout timeline
- [ ] Legal review is scoped (for BGV/DPDP)
- [ ] DocuSign/Checkr vendor selection is done
- [ ] You have 3 sessions of engineering time available

**Otherwise, stay as the verification layer. It's a bigger moat with less engineering.**

---

## RELATED FLAGS

- `INVERTED-MARKETPLACE-FLAG.md` — Candidate dashboard + JD-to-shortlist + notifications (3 sessions)
- `SESSION-102-CANDIDATE-DASHBOARD-FLAG.md` — Candidate-side dashboard
- `DEAN_REPORT_FRONTEND_FLAG.md` — University dean frontend (2-3 sessions)
- `A4_LMS_BRIDGE_FLAG.md` — Moodle/Canvas integration (5 sessions)

**All demand-triggered. None built until a paying customer asks.**

---

**Last updated:** 2026-10-31 (Session 106 close)
**Next review:** 2026-12-01 (30 days) OR immediately if trigger fires
**Owner:** Bhavya M