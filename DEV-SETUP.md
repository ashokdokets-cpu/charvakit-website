# Charvak — Local Dev Setup

**Purpose:** How to run local smoke tests without touching prod.
**Created:** 2026-09-17 (Session C)
**Updated:** 2026-09-19 (Session H-2) - added Session Start Checklist

---

## Session Start Checklist

Run these at the start of every session:

    cd C:\projects\charvakit-new
    .\venv\Scripts\Activate.ps1

    # 1. Working tree must be clean
    git status --short

    # 2. Confirm HEAD matches SESSION-CONTEXT.md
    git log --oneline -3

    # 3. Ensure Postgres is running
    Get-Service postgresql-x64-15

    # 4. Prod is reachable
    try { (Invoke-WebRequest -Uri "https://www.charvakit.com/api/payment/status" -UseBasicParsing -TimeoutSec 5).StatusCode } catch { $_.Exception.Message }

If any check fails:
- Dirty tree -> git stash or commit before proceeding
- HEAD mismatch -> update SESSION-CONTEXT.md
- Postgres stopped -> Start-Service postgresql-x64-15
- Prod down -> check Render dashboard

---

## Local Postgres

Installed via Chocolatey: `choco install postgresql15 --params '/Password:dev'`

- **Install:** `C:\Program Files\PostgreSQL\15`
- **Service:** `postgresql-x64-15` (Automatic start; `Start-Service postgresql-x64-15` if stopped)
- **Binaries:** `C:\Program Files\PostgreSQL\15\bin` (on machine PATH)
- **Superuser:** `postgres` / `dev`
- **Databases:** `vouchai` (dev), `vouchai_test` (spare)
- **Connection string:** `postgresql://postgres:dev@localhost:5432/vouchai`

## `.env.local`

Exists at repo root, gitignored (`.gitignore` line 3: `.env.*`). Contents:

    DATABASE_URL=postgresql://postgres:dev@localhost:5432/vouchai
    OPENAI_API_KEY=
    SECRET_KEY=dev-only-not-secret-not-used-for-prod
    ADMIN_EMAIL=admin@test.local
    HR_EMAIL=hr@test.local
    SITE_URL=http://localhost:8000

**Important:** `load_dotenv()` defaults to `override=False`, so a shell env var set
*before* Python runs wins over `.env.local`. That's why the pattern below works:

    $env:DATABASE_URL = "postgresql://postgres:dev@localhost:5432/vouchai"
    python script.py
    $env:DATABASE_URL = $null

## Applying migrations locally

    @'
    import glob, psycopg2
    conn = psycopg2.connect("postgresql://postgres:dev@localhost:5432/vouchai")
    cur = conn.cursor()
    for f in sorted(glob.glob("migrations/*.sql")):
        print("applying", f)
        with open(f, "r", encoding="utf-8-sig") as fh:
            cur.execute(fh.read().lstrip("\ufeff"))
    conn.commit(); cur.close(); conn.close()
    '@ | Out-File -FilePath _apply.py -Encoding utf8
    # strip BOM
    $b = [System.IO.File]::ReadAllBytes("_apply.py")
    if ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) {
        [System.IO.File]::WriteAllBytes("_apply.py", $b[3..($b.Length-1)])
    }
    python _apply.py
    Remove-Item _apply.py

**Known gap:** `20260916_course_payments.sql` references `charvak_enrollments`,
which no migration creates. Alphabetical apply fails there. Run the 20260917+
migrations manually in dependency order, or backfill the missing migration.

## Three pitfalls we hit (avoid these)

### 1. `Out-File -Encoding utf8` writes a BOM

Python's `json`, `ast.parse`, and psycopg2's `cur.execute` all fail on a leading
BOM. Always strip after writing:

    $b = [System.IO.File]::ReadAllBytes("script.py")
    if ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) {
        [System.IO.File]::WriteAllBytes("script.py", $b[3..($b.Length-1)])
    }

Or write with:
    [System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false)))

### 2. `python -c "..."` with nested quotes breaks in PowerShell

PowerShell mangles escaped quotes when passing to native executables. **Never use
`python -c` for anything containing `"`.** Write a temp `.py` file.

### 3. `curl.exe -d '{"key":"value"}'` silently strips inner quotes

PowerShell's native-arg parsing eats the double quotes even inside single quotes.
The server receives `{key:value}` and returns a JSON parse error.

**Always write the body to a file:**

    '{"key":"value"}' | Out-File -FilePath _body.json -Encoding ascii -NoNewline
    curl.exe -s -X POST "http://localhost:8000/api/endpoint" `
      -H "Content-Type: application/json" `
      --data-binary "@_body.json"

## Smoke test pattern (recommended)

1. Write the test as a temp `.py` file (heredoc → `Out-File`)
2. Strip BOM
3. Set `$env:DATABASE_URL` to local
4. Run the test
5. Clean up any rows the test created
6. Clear `$env:DATABASE_URL`
7. Delete the temp file

Never leave a `_*.py` or `_*.json` file in the repo root — they show as untracked
and pollute `git status`.

## Prod safety gate

Every smoke test should include this at the top:

    import os
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv("DATABASE_URL", "")
    host = url.split("@")[1].split("/")[0] if "@" in url else "unknown"
    is_prod = "render.com" in host or "singapore" in host
    if is_prod and os.getenv("CHARVAK_ALLOW_PROD") != "1":
        raise SystemExit("REFUSING prod. Set CHARVAK_ALLOW_PROD=1 to override.")

## Service commands

    # Status
    Get-Service postgresql-x64-15

    # Restart
    Restart-Service postgresql-x64-15

    # psql shell
    $env:PGPASSWORD = "dev"
    psql -U postgres -d vouchai
    $env:PGPASSWORD = $null

    # List tables
    $env:PGPASSWORD = "dev"
    psql -U postgres -d vouchai -c "\dt charvak_*"
    $env:PGPASSWORD = $null

## curl.exe on PowerShell — JSON body gotcha

curl.exe in PowerShell strips backslash-escaped quotes inside -d payloads.
A request like:
    curl.exe ... -d "{\"email\":\"a@b.com\"}"
reaches the server as:  {email:a@b.com}   (no quotes around keys/values).
The server request.json() then raises JSONDecodeError, the route outer
except Exception catches it, and the response is HTTP 200 with a generic
error payload — the auth guard never runs.

Always use --data-binary @file:
    Out-File -FilePath _body.json -Encoding ascii -NoNewline
    (then pipe the JSON string into _body.json)
    curl.exe ... --data-binary "@_body.json"
    Remove-Item _body.json

When debugging a route, always verify the request actually reached the
guard. A 200 with a generic error payload can mean either "guard did not
fire" OR "body was malformed before the guard". Check the uvicorn log —
a JSONDecodeError traceback at "data = await request.json()" confirms
the second case.


---

## Security Sweep Checklist (Session 14, 2026-10-03)

Every 4-6 sessions, run this. It catches leaks that code review alone
cannot. Learned the hard way: earlier code-pattern-only sweeps missed
4 real leaks that a live-endpoint probe would have caught instantly.

### Live test first, code scan second.

Code review sees guards. Live tests see *behaviour*. Do the live test
first.

### Step 1 - Probe suspect routes against prod

Run these curls. Note the HTTP status. 200 on user-scoped routes is a
red flag.

    # Public routes (should be 200)
    curl.exe -s -o NUL -w "GET / -> %{http_code}`n" "https://www.charvakit.com/"

    # User-scoped with email in path (should be 401/403)
    curl.exe -s -o NUL -w "GET /api/results/user/victim@example.com -> %{http_code}`n" `
        "https://www.charvakit.com/api/results/user/victim@example.com"

    # Credit-gated (should be 401 without token)
    curl.exe -s -o NUL -w "POST /api/career-assessment/start -> %{http_code}`n" `
        -X POST "https://www.charvakit.com/api/career-assessment/start" `
        -H "Content-Type: application/json" -d "{}"

    # Admin (should be 401 without token)
    curl.exe -s -o NUL -w "GET /api/admin/users -> %{http_code}`n" `
        "https://www.charvakit.com/api/admin/users"

    # PII endpoints (should be 401 without token)
    curl.exe -s -o NUL -w "GET /api/ats/candidates -> %{http_code}`n" `
        "https://www.charvakit.com/api/ats/candidates"

### Step 2 - Code scan

Scan main.py for routes and their guards. Focus on these risky patterns:

- Routes with `{email}` in path
- Routes calling `require_credits_from_data` (must have auth too)
- Routes under `/admin` or `/api/admin` (should be middleware-covered)
- Routes accepting `email` in the JSON body (POST)

    # Count guard usage
    Select-String -Path "main.py" -Pattern "require_auth_for_email\(" | Measure-Object
    Select-String -Path "main.py" -Pattern "require_admin\(" | Measure-Object

    # Find routes with {email} in path
    Select-String -Path "main.py" -Pattern '@app\.(get|post)\([^)]*\{email\}' | Select-Object LineNumber, Line

### Step 3 - Cross-reference

A route should return 401/403 if it:

- Reads or returns PII (name, email, phone, resume, address)
- Mutates user state (credits, subscriptions, progress)
- Charges credits
- Is under /admin or /api/admin

If a route that should be gated returns 200 without a token,
investigate.

### Step 4 - Session 14 findings (reference)

The 2026-10-03 sweep found 4 real leaks using this method:

| Route | Issue | Fix |
|---|---|---|
| /api/ats/candidates | Full candidate PII exposed | require_admin |
| /api/company-pattern/readiness/{email}/{company_id} | IDOR | require_auth_for_email |
| /api/analysis/gap/{email}/{target_role} | IDOR | require_auth_for_email |
| /api/lms/progress/{enrollment_id} | Any logged-in user could read any progress | require_auth + ownership check |

All four had passed earlier code-only sweeps. The live probe caught
what pattern matching missed.

### Step 5 - Known false positives (do not re-investigate)

- Routes under `/api/cron/*` - protected by X-Cron-Secret header,
  not user auth. Return 200 with no token is expected.
- `/api/contact`, `/api/questions/report`, `/api/referral/track-signup`,
  `/api/credits/check`, `/api/credits/purchase` - intentionally public.
  They validate input server-side; no PII is returned.
- Admin routes under `/admin/*` or `/api/admin/*` - covered by
  `admin_auth_guard` middleware (main.py:262). Even if a route body
  has no guard, the middleware returns 401 for the whole namespace.
- `/api/region`, `/api/payment/status`, `/api/credits/plans`,
  `/api/career-assessment/options` - public catalogs / status.
  Return 200 by design.

### Step 6 - Verify guards actually fire

For every route touched by a fix, verify in prod:

    1. Anonymous call -> 401
    2. Wrong-user call -> 403 (for email-match routes)
    3. Right-user call -> 200
    4. Admin call -> 200 (if admin bypass exists)

Do not mark a fix complete until all four scenarios pass against
prod, not localhost. Localhost can differ (see V4/V5 in KNOWN-ISSUES).

### Quick wins if the sweep finds nothing

- Re-run step 1 for any new routes added since the last sweep
- Check `.env` for new secrets not in MASTER-REFERENCE.md
- Verify prod still uses live PayPal (`paypal_client_id` starts with
  "Aaj..." not the sandbox prefix)
