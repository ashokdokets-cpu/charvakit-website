# Security Policy -- Charvak IT Consulting

## Reporting a Vulnerability

If you discover a security issue, **do not open a public GitHub issue**.
Email **hr@charvakit.com** with:
- Description of the issue
- Steps to reproduce
- Potential impact

We aim to respond within 48 hours.

---

## Secret Management Rules

1. **Never commit secrets.** All API keys, DB passwords, and tokens live in environment variables only.
2. **Never paste secrets in chat, tickets, or docs.** Use `<REDACTED>` in any transcript.
3. **`.env` is gitignored.** Use `.env.example` as the template for required variables.
4. **Pre-commit hook is mandatory.** Every commit is scanned for secrets by `.githooks/pre_commit_scanner.py`.

## What the Pre-Commit Hook Catches

| Pattern | Provider |
|---------|----------|
| `postgresql://user:pass@` | Database connection strings |
| `sk-...` | OpenAI / Stripe |
| `xkeysib-...` | Brevo |
| `SG....` | SendGrid |
| `AIza...` | Google API |
| `AKIA...` | AWS Access Key |
| `ghp_...` | GitHub tokens |
| `xox[baprs]-...` | Slack tokens |
| `-----BEGIN ... PRIVATE KEY-----` | Private keys |

If the hook blocks your commit, **remove the secret** (use an env var) -- do not bypass with `--no-verify` unless you have reviewed the file manually.

## Incident History

### 2026-11-16 -- Leaked DB Credential (Resolved)
- **What:** `cleanup_radar_jobs.py` contained a hardcoded `postgresql://` connection string and was committed to public GitHub.
- **Detection:** Reported during code review.
- **Response:** Credential invalidated within 15 minutes. Git history rewritten to remove the blob. Force-pushed clean history. Repo shrunk 90% (489 MB to ~50 MB).
- **Impact:** No breach. Audited 44 known users; no unauthorized access.
- **Prevention:** Pre-commit hook installed. `.env.example` created. This document created.

## Environment Variables

See `.env.example` for the full list. Required in production:
- `DATABASE_URL`
- `SECRET_KEY`
- `BREVO_API_KEY` (or `SENDGRID_API_KEY`)
- `CRON_SECRET`
- `TECHMAP_API_KEY`
- `BASE_URL`

## Backup & Recovery

- Backups live in `%USERPROFILE%\Documents\charvak_backups\` (outside the repo)
- Restore procedure: see `manifest.json` inside each backup folder
- After any credential rotation, create a fresh backup before the old one is deleted

---

*Last updated: 2026-11-16*
### 2026-11-16 (post-Day4) -- pyjwt missing from requirements.txt (Resolved)
- **What:** New student-auth routes imported `auth_utils`, which imports `jwt`. `pyjwt` was installed locally but missing from `requirements.txt`. Render build did not install it, causing HTTP 500 on `/student/dashboard` and `/college/students`.
- **Detection:** Post-deploy smoke test.
- **Response:** Added `pyjwt==2.15.1` to `requirements.txt`. Redeployed with cache clear. All routes healthy.
- **Prevention:** For any new feature: (a) `pip install` locally, (b) add to `requirements.txt` in same commit, (c) `pip install --dry-run -r requirements.txt` before pushing.

