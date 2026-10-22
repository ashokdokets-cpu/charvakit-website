# Session Context - Charvak

**HEAD:** 51deff2
**Live:** https://www.charvakit.com
**Updated:** 2026-10-22 (Session 74 closed — production CSS bug fixed)

---

## Session 74 CLOSED (2026-10-22) — Production CSS Bug Fixed

**Commits:**
- `07ae7fc` feat(nav): Phase 1 - auth CTAs to top bar
- `1573fc5` fix(css): restore .dropdown-menu display:none (broken header)
- `51deff2` chore: gitignore backups/ directory

### What Shipped to Prod

- Phase 1 nav: auth CTAs moved to top bar (Sign In, Get Started →)
- Auth dropdown removed from main nav (14 items instead of 15)
- **Critical fix**: Restored missing `.dropdown-menu { display: none }` rule
- Added `?v=` cache-bust to style.css link
- backups/ directory gitignored

### Bug Fixed (Production Critical)

The `.dropdown-menu { display: none }` rule was accidentally missing from
style.css in commit `07ae7fc`. Without it, ALL nav dropdowns rendered
open by default — header occupied full page, nav items appeared mid-page,
site completely broken for every user.

**Fixed in `1573fc5`.** Site fully operational. Verified on prod.

### Deferred to Session 75

- Nav Phase 2 (5 story-driven dropdowns) — redo with VS Code direct edit
- Design system polish — inline style block in base.html
- Resume Roast Patches 3-4 (live activity ticker, Dokets CTA)
- Dashboard flags (Render password, Amrita email, GPT-4o flip)

### Lessons Learned

1. Never run `uvicorn --reload` twice. Zombie processes serve stale
   cached responses. Kill by port ownership, not process name.
2. PowerShell $str.Length truncates multi-line `curl.exe -s` output.
   Use `curl.exe -o file` + `(Get-Item).Length` for reliable file size.
3. `Get-Process.Path` for venv python reports system python path
   because venv python.exe is a stub. Verify via sys.executable.
4. Browser cache needs ?v= version bump or full browser restart.
5. `$content.Replace()` on templates can match the wrong context.

### Prod Verification (2026-10-22, post-deploy)

- Homepage: HTTP 200
- CSS served: 26,129 bytes (correct, complete)
- Dropdown hide rule: present
- .dropdown-menu.show rule: present
- All 5 nav dropdowns: open/close correctly
- 14/14 IELTS regression: passed

### Next Session (75) — Fresh Start

**Priority 1**: Nav Phase 2 redo (2 hrs)
- Open VS Code, edit base.html directly
- Replace navbar-nav block
- Add mega-menu CSS inline in base.html style block
- One edit, one commit, no PowerShell scripts

**Priority 2**: Resume Roast patches 3-4 (60 min)
- Live activity ticker
- Dokets "Build a Better One" CTA

**Priority 3**: Dashboard flags (15 min)
- Rotate Render Postgres password
- Send Amrita email to Prof. Raj
- Phase 3c GPT-4o-mini env flip (Nov 3 target)