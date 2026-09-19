# Charvak Doc & Source Style Guide

**Purpose:** Small set of rules to keep our code and docs consistent.
**Companion files:** DEV-SETUP.md (local workflow), KNOWN-ISSUES.md (bug registry).

---

## Emoji Policy (in .py source files)

We had 105 emoji occurrences in .py files as of 2026-09-19. Not all are bad.
Here's the rule:

### OK to keep

- **User-facing strings** — email subjects, WhatsApp messages, HTML content,
  anything a customer will read. Emoji are intentional UX.
- **Logger messages** — `logger.info("✅ Engine ready")`. Helps scan logs visually.
- **Data dicts with `"icon"` keys** — `{"icon": "🎓"}` — frontend renders them.
- **Standalone print() in one-off scripts under scripts/one-off/** — these are
  scratch tools, not production.

### Not OK

- **Docstrings** — `"""✅ Foo"""` — no benefit; pollutes `help()` output.
- **Source identifiers** — variable/function names must be ASCII.
- **Comments** — plain ASCII preferred; use `->` not `→`, `[OK]` not `✅`.
- **Markdown files** (`.md`) — use plain ASCII markers like `[OK]`, `[WAIT]`,
  `[DONE]` instead of ✅/🟡.

### Why

1. Fonts render emoji inconsistently across terminals/editors.
2. Emoji inflate file size (multi-byte UTF-8 for one glyph).
3. Mojibake risk when files cross encoding boundaries.
4. `grep` on emoji is awkward vs `[OK]`.

---

## Line Endings

- LF (`\n`) in all source files (enforced by `.gitattributes`).
- CRLF only for PowerShell/`.bat` if needed.

---

## Versioning

- **vX.Y.Z** for major/minor/patch.
- Session tags: `vX.Y-session-LETTER-YYYYMMDD` (e.g., `v3.2-session-K-complete-20260919`).

---

## Commits

- Prefix: `feat(...)`, `fix(...)`, `chore(...)`, `docs(...)`, `test(...)`.
- One logical change per commit.
- Body explains **why** more than **what** (the diff shows what).

---

## File naming

- `*_engine.py` — business logic
- `*_service.py` — supporting service (cron, monitor)
- `*_manager.py` — CRUD manager
- `scripts/one-off/*.py` — scratch scripts, not imported by main.py
- `migrations/YYYYMMDD_name.sql` — idempotent SQL migrations

---

## Migrations

- Always `CREATE TABLE IF NOT EXISTS`.
- Always `CREATE INDEX IF NOT EXISTS`.
- Clean up duplicates before adding UNIQUE constraints.
- Apply locally first, verify, then apply to prod via Render Shell.