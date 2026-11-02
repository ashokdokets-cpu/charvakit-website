# Employer JD Calibration - FLAGGED

**Flagged:** 2026-10-30
**Effort:** 1 session (~4 hours)
**Trigger:** Before sending the first employer Signal Email
**Status:** NOT BUILT

## The Risk

A TA lead pastes a JD with skills outside Charvak's calibrated range.
The AI generates an assessment that's inaccurate. The candidate takes
it, gets scored badly. The TA lead blames Charvak. Deal lost.

## What to Build

### 1. Calibrated Skills Whitelist (~30 min)

File: calibrated_skills.py

A curated list of ~50 skills Charvak can defend today. All other
skills are "not calibrated."

Initial list:
- Languages: python, javascript, typescript, java, cpp, go, sql
- Frameworks: react, node, django, spring
- Cloud: aws-basics, azure-basics, gcp-basics
- Data: pandas, pyspark, sql-window
- Concepts: algorithms, data-structures, oop, system-design-basics

### 2. JD Coverage Pre-Check (~1 hr)

File: jd_calibration.py

Function check_jd_coverage(jd_parsed) returns:
- status: calibrated | partial | not_calibrated
- coverage: 0-100%
- covered: [list of covered skills]
- not_covered: [list of uncovered skills]
- action: proceed | partial_assessment | decline

Wire into /recruiter/dashboard JD paste form. Show green/yellow/red
pre-flight to TA lead before running assessment.

### 3. Assessment Validator (~1 hr)

File: career_assessment_engine.py (add function)

After AI generates questions, validate that at least 80% reference
required skills. If below, regenerate once with stronger prompt.
If still failing, fall back to closest template.

### 4. Honest Fallback Messaging (~30 min)

When check_jd_coverage returns "not_calibrated", return API response:
{
    "status": "not_calibrated",
    "covered": [...],
    "not_covered": [...],
    "message": "We can verify X skills. For Y, we recommend a second-
                round screen by your team."
}

Show this message to TA lead. Offer partial assessment or waitlist.

### 5. Certificate Metadata Enhancement (~30 min)

Add skills_verified + skills_not_covered to certificate payload.
Certificate display shows "Verified: Python, SQL" not just score.

## Verification

After building:
1. Paste a calibrated JD (React Engineer) → green pre-flight
2. Paste a partial JD (React + Rust) → yellow, partial assessment offered
3. Paste an uncalibrated JD (COBOL) → red, decline with waitlist
4. Confirm assessments only run on calibrated skills
5. Confirm certificates show skill coverage

## When to Build

Trigger: 1 paying institution signed OR before first employer email.

Do NOT build before institution channel validates demand.

## Related

- EMAILS-LOCKED.md Email #7 (employer Signal) - currently leads with
  "verify my pipeline" pitch
- This flag is the missing infrastructure for that pitch to work