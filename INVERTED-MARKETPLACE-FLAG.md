# Inverted Marketplace - FLAGGED FOR LATER

**Flagged:** 2026-10-30 (Session 101 close)
**Status:** NOT STARTED - deferred until trigger fires
**Purpose:** The two-sided companies hunt candidates marketplace.

**TL;DR:** 3 sessions of build + 1 sales motion. Do NOT start until
the trigger fires. Building this before a paying customer exists wastes
sessions on a stadium nobody is playing in.

---

## Trigger - When to Build This

Build ONLY when ANY of these happen:

1. Amrita signs a pilot (or paid contract)
2. 1+ employer signs a paid arrangement (even small)
3. 5+ universities in active pilot conversations
4. A paying customer explicitly requests the demo

Do NOT build speculatively.

---

## The 3 Sessions (When Triggered)

### Session 102 - Candidate Dashboard (/career-dashboard)

Auth-gated route. Shows candidate current state, next 3 steps,
matched open roles, recruiter activity. Rule-based (no ML).

Data contract (Python dict):

    {
        "candidate": {"email", "handle", "tier", "charvak_score",
                      "readiness_score", "cert_count", "is_public"},
        "next_steps": [{"type", "title", "impact", "action_url"}, ...],
        "matched_roles": [{"role_id", "title", "company",
                           "match_pct", "apply_url"}, ...],
        "recruiter_activity": {"views_this_week", "last_view_at"}
    }

Reuse: passport_engine, career_assessment_engine, jd_parser_engine,
charvak_client_roles.

Effort: ~1 session (3-4 hrs)

### Session 103 - JD to Shortlist (/recruiter/dashboard extension)

Paste JD -> jd_parser_engine.parse_jd -> query charvak_passports ->
score by JSON skill overlap -> return top 5 with why-they-match.

Contact button opens F3 Screen Agent with prefilled context.

Effort: ~1 session (3-4 hrs)

### Session 104 - Notification Engine (email only)

Two cron jobs:
1. Weekly candidate digest (Monday 9 AM): matched roles + recruiter views + next step
2. Daily recruiter alert (if new match): new candidates matching open JD

Reuse: email_engine + charvak_client_roles + charvak_passports + jd_parser_engine.

Effort: ~1 session (3-4 hrs)

---

## After Session 104 - STOP

Demo Sessions 102-104 to Amrita. Sell 1 paying client.

Do NOT start Session 105 until a check clears.

Do NOT build: predictive ML, advanced filters, anti-spam gate,
real-time chat, mobile app, marketplace-wide self-driven, candidate
profile v2, skills taxonomy.

Every one of these is a distraction until 10+ real placements exist.

---

## The Honest Truth

Every marketplace before the match has failed for the same reason:
built for volume before demand.

- Uber solved it by getting 100 drivers in SF first
- Airbnb solved it by getting 20 NYC apartments listed first
- Hired solved it by manually matching 50 candidates first

Charvak's 100-drivers equivalent is 5 paying customers who place
10 candidates. Not 500 candidates waiting for jobs.

Manual first. Automated second. Predictive third. Do NOT skip.

---

## Revisit Cadence

- First Monday of every month (check if trigger fired)
- When a client asks how do I find candidates in your system
- When Amrita (or any institutional buyer) says yes

Do NOT read to decide what to build when bored.

---

## The One-Line Rule

> Build Sessions 102-104 ONLY after a paying customer (or signed pilot)
> exists. Do not build the marketplace in the dark.

---

**Last updated:** 2026-10-30 (Session 101 close)
**Next review:** 2026-11-30 (first Monday of November)
**Or immediately if:** any trigger condition fires
