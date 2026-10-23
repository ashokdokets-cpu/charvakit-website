# Dean Report Delivery — Decision Log (2026-10-24)

## Decision
Ship PDFs via email for now. Do NOT build the frontend UI yet.

## What's Live on Prod
- GET /api/proof-dashboard/{university_id} — JSON (works)
- GET /api/proof-dashboard/{university_id}/pdf — PDF (works)
- No auth required (URLs are guessable but nobody knows them)

## What's NOT Built
- No dashboard page (no /admin/proof-dashboard/{id})
- No signed URLs
- No client login
- No self-serve access

## Why We Skipped It
- 0 paying clients
- Amrita hasn't signed
- PDFs sent by email are the right delivery for demo stage
- Signed URLs matter only when 5+ clients need self-serve

## When to Build the Frontend
Trigger: 1 client says "I want monthly access without asking you"

Then build:
- Signed URL route (/report/{hmac-token})
- Client login page
- Auth dashboard UI
- ~2-3 sessions total

## Current Workaround
- Download 3 PDFs from /api/proof-dashboard/{id}/pdf
- Save to Desktop folder Charvak_Dean_Reports_20261024/
- Attach to emails manually

## Files Downloaded
- Amrita_Dean_Report.pdf (5.9 KB, 4 pages)
- VIT_Vellore_Dean_Report.pdf (~5.7 KB)
- NIT_Trichy_Dean_Report.pdf (~5.8 KB)

## Prod URLs (for reference)
- Amrita: https://www.charvakit.com/api/proof-dashboard/UNI-AMRITA-001/pdf
- VIT: https://www.charvakit.com/api/proof-dashboard/UNI-VIT-001/pdf
- NIT: https://www.charvakit.com/api/proof-dashboard/UNI-NITT-001/pdf

## Session Close
- Phase A2 (Proof Dashboard) — BACKEND COMPLETE
- Frontend — DEFERRED until first paying client
- Next Phase A item: A1 (Employer Network)