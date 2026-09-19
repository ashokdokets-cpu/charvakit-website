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
