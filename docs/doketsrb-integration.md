# Charvak <-> DoketsRB Sync Integration

**Version:** 1.0
**Last updated:** 2026-10-21
**Maintained by:** Charvak IT Consulting
**Audience:** DoketsRB engineering team

---

## Overview

Charvak exposes 6 endpoints under `/api/sync/*` for bidirectional data
sync with DoketsRB:

- **Push** (DoketsRB -> Charvak): resume, application, skills
- **Pull** (Charvak -> DoketsRB): jobs
- **Status** (both directions): per-user sync status, health check

All state persists to `charvak_synced_users`, `charvak_synced_applications`,
and `charvak_ats_sync_log` on Charvak's Postgres.

---

## Credentials

Two separate credentials are required. **They are NOT the same value.**

| Variable | Length | Header | Purpose |
|---|---|---|---|
| `SYNC_API_KEY` | 43 chars | `X-API-Key` | Identifies caller |
| `SYNC_API_SECRET` | 64 chars | (never sent) | Signs HMAC |

- `SYNC_API_KEY` is safe to store in your Vercel environment as-is.
- `SYNC_API_SECRET` must be kept server-side only. Never expose in browser
  code or client bundles.
- Get `SYNC_API_SECRET` from Charvak team via secure channel
  (1Password / Bitwarden Send / Signal). Do not request via email.

---

## Quick Test (Start Here)

**Goal:** Confirm your credentials work before writing any integration code.

### Test with curl (bash)

Run this in your terminal. Replace `<64-char-secret>` with the actual value.

- Export the two credentials as env vars
- Build a test JSON body
- Compute HMAC-SHA256 of the body using SYNC_API_SECRET
- POST to /api/sync/resume with X-API-Key and X-Signature headers

**Curl example:**

- BODY=<json string with user_id, doketsrb_id, name, email, phone, resume_data, skills, experience, education>
- SIG=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SYNC_API_SECRET" | awk '{print $2}')
- curl -X POST https://www.charvakit.com/api/sync/resume \\
    -H "Content-Type: application/json" \\
    -H "X-API-Key: $SYNC_API_KEY" \\
    -H "X-Signature: $SIG" \\
    -d "$BODY"

### Test with PowerShell

- Load SYNC_API_KEY and SYNC_API_SECRET from env or hardcode for test
- Build $body as a JSON string
- Compute HMAC using New-Object System.Security.Cryptography.HMACSHA256
- Write to temp file, POST via curl.exe --data-binary @temp.json

### Expected Response

If successful, you should see a JSON object containing:
- status: success
- message: Resume synced for user <id>
- synced_at: ISO timestamp

If you see this, your setup is correct. Move on to code integration.
If not, jump to the Troubleshooting section.

---

## Endpoint Reference

### POST /api/sync/resume

Push a user's full profile from DoketsRB to Charvak.

**Request body** (Pydantic-validated):

- user_id (string, required)
- doketsrb_id (string, required)
- name (string, required)
- email (string, required)
- phone (string, optional, default empty)
- resume_data (object, optional, default empty)
- skills (array, optional, default empty)
- experience (array, optional, default empty)
- education (array, optional, default empty)

**Response:** status=success, message, synced_at

**Behavior:** Upsert into charvak_synced_users on user_id. Idempotent - safe to call multiple times with the same data.

**When to call:** On profile save (create or update).

---

### POST /api/sync/application

Push an application event from DoketsRB to Charvak.

**Request body:**

- user_id (string, required)
- job_title (string, required)
- company (string, required)
- status (string, required - applied, interviewed, offered, rejected, etc.)
- applied_date (string, optional, ISO date)

**When to call:** On application tracker update.

---

### POST /api/sync/skills

Push skill data from a DoketsRB ATS scan.

**Request body:**

- user_id (string, required)
- skills (array, required - e.g. Python, React)
- gap_topics (array, optional, default empty)
- source (string, optional, default doketsrb)

**When to call:** After ATS scan completes.

---

### GET /api/sync/jobs

Pull current Charvak job listings for display on DoketsRB.

**Query params:**
- limit (integer, default 50, max 200)

**Response:** status=success, jobs=array of {job_id, title, company, location, type, salary_range, posted_at, detail_url}

**Auth:** X-API-Key only (no signature needed for GET).

**When to call:** Cache refresh, or on user job-search page.

---

### GET /api/sync/status/{user_id}

Check per-user sync state (last sync time, record counts).

**Response:** status=success, user_id, last_synced_at, profile_synced, applications_count, skills_synced

**Auth:** X-API-Key only.

---

### GET /api/sync/health

No auth. Returns service status. Use this for uptime monitoring.

---

### POST /api/sync/pull/{user_id}

**Charvak pulls from DoketsRB.** User-triggered sync: Charvak calls DoketsRB
public endpoints, then merges into charvak_synced_users +
charvak_synced_applications.

**Auth:** X-API-Key + X-Signature (same as push routes). Empty body
counts as the HMAC payload.

**Path parameter:** user_id - the DoketsRB user UUID

**Flow:**

1. Charvak GETs https://www.doketsrb.com/api/public?action=profile&user_id={uid}
2. Charvak GETs https://www.doketsrb.com/api/public?action=applications&user_id={uid}
3. Both calls send X-API-Key
4. Charvak upserts into charvak_synced_users + charvak_synced_applications
5. Returns per-endpoint counts

**Response:**

    {
      "status": "success",
      "user_id": "bb864eb3-...",
      "profile_synced": true,
      "applications_synced": 1,
      "errors": []
    }

**Status values:** success (both), partial (one failed, see errors[]), error (neither)

**Test with curl:**

    BODY=''
    SIG=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SYNC_API_SECRET" | awk '{print $2}')

    curl -X POST https://www.charvakit.com/api/sync/pull/bb864eb3-3232-4b09-926a-ce7baaadc93f \
      -H "X-API-Key: $SYNC_API_KEY" \
      -H "X-Signature: $SIG"

**Expected response:**

    {"status":"success","user_id":"bb864eb3-...","profile_synced":true,"applications_synced":1,"errors":[]}

**Common failures:**

| HTTP | Meaning | Fix |
|---|---|---|
| 401 | Wrong X-API-Key | Check SYNC_API_KEY both sides |
| 403 | Wrong signature | Sign EMPTY body (not {} or user_id) |
| 200, profile_synced=false | DoketsRB endpoint unreachable | Check doketsrb.com/api/public |
| 200, errors=[404] | User ID not in DoketsRB | Verify UUID exists |

**When to call:** From /career-center "Sync now" button, or scheduled cron (future).

**DoketsRB endpoints required:**

- GET https://www.doketsrb.com/api/public?action=profile&user_id=...
- GET https://www.doketsrb.com/api/public?action=applications&user_id=...

Both must use the same SYNC_API_KEY that Charvak sends.

---

## HMAC Signing Specification

**Algorithm:** HMAC-SHA256
**Key:** SYNC_API_SECRET (the 64-char secret, NOT the API key)
**Payload:** Raw request body bytes (exact string sent over the wire)
**Output:** Lowercase hex string (64 chars)

### Python Example

- Import hmac, hashlib, json, requests
- Build body dict with all required fields
- Serialize with json.dumps(body, separators=(',',':')) to match curl output
- Encode UTF-8
- HMAC-SHA256 using SYNC_API_SECRET as key
- Use .hexdigest() - lowercase hex, NOT base64
- Send via requests.post with data=body_bytes

### Node.js / TypeScript Example

- Import crypto from 'crypto'
- Build body object
- Serialize with JSON.stringify(body)
- HMAC via crypto.createHmac('sha256', process.env.SYNC_API_SECRET).update(bodyString, 'utf8').digest('hex')
- Send via fetch with the string body

---

## Common HMAC Mistakes

| Mistake | Why it fails | Fix |
|---|---|---|
| Signing with SYNC_API_KEY instead of SYNC_API_SECRET | Wrong key | Use the 64-char secret, not the 43-char API key |
| Signing the parsed JSON object instead of the raw body | Bytes do not match | Always sign exactly what you send |
| Base64 instead of hex | Wrong encoding | Use hexdigest() (Python) or .digest(''hex'') (Node) |
| Using json= instead of data= in requests | Different serialization | Use data=body_bytes in Python requests |
| Missing Content-Type: application/json | Server may reject | Add the header |
| Trailing spaces in json.dumps | Bytes differ | Use separators=('','','':'''') in Python |
| Signing after mutating the dict | Signed data != sent data | Sign the exact bytes you send |

---

## Troubleshooting

### 401 Invalid API key

**Meaning:** X-API-Key header is missing OR wrong value.

**Fix:**
1. Check SYNC_API_KEY env var is set to SvuFokOQxAFFN5ghSPvuyDWHr-x7m3x_9KMkGj2DUrs
2. Confirm the header is X-API-Key (case-insensitive, but no typos)
3. Test with curl -H "X-API-Key: SvuF..." alone (no signature) - if this works, your API key is fine

### 403 Invalid signature

**Meaning:** HMAC does not match what the server computed.

**Check in this order:**
1. Are you signing with SYNC_API_SECRET? This is the #1 cause. Not SYNC_API_KEY.
2. Is SYNC_API_SECRET exactly 64 chars? If shorter, it is the wrong value.
3. Is the signature hex, not base64? Lowercase 64-char string.
4. Is the payload the exact raw body bytes? Not the parsed dict, not the dict re-serialized.
5. Is the header name X-Signature?

### 422 Unprocessable Entity

**Meaning:** Body shape invalid (not an auth failure).

**Fix:** Include all required fields. Our ResumeSync model requires user_id, doketsrb_id, name, email.

### 5xx Server Error

**Meaning:** Charvak-side error.

**Fix:** Contact Charvak team with the exact request ID (from response headers) and timestamp.

---

## Rate Limits

| Endpoint | Limit |
|---|---|
| /api/sync/resume | 60/min per API key |
| /api/sync/application | 60/min |
| /api/sync/skills | 60/min |
| /api/sync/jobs | 120/min |
| /api/sync/status/{user_id} | 120/min |
| /api/sync/health | 300/min |

Rate-limited requests return 429 Too Many Requests with Retry-After header.

---

## Support

- Bug reports: Contact Charvak team with request ID + timestamp
- Credential rotation: Coordinate 2-week lead time before rotating
- New feature requests: Email Charvak team with use case description

**Do not send secrets via email.** Use 1Password / Bitwarden Send / Signal.

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-10-21 | Initial doc - all 6 endpoints, HMAC spec, troubleshooting |
