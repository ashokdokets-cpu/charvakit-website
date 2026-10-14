# READ THIS ONCE A MONTH - GPT-4o-mini Retirement

**Deadline: 14 January 2027**
**Flagged: 2026-10-15**

---

## Why this file exists

OpenAI is retiring GPT-4o-mini (and 3 other models) on 14 January 2027.
GPT-4o-mini powers every AI feature on Charvak.

If we miss this deadline, every AI feature silently breaks on
14 January 2027. Users see errors. Paid features fail. The platform
loses trust.

## What to do

**When you remember this file (once a month is enough):**

1. Open COMMITMENT.md and read the GPT-4o-mini retirement section.
2. Check the timeline - which phase should we be in?
3. If we're behind schedule, drop everything and start Phase 1.
4. If we're on schedule, update the timeline.

## Timeline at a glance

| Date | Phase | Status |
|---|---|---|
| Oct 20, 2026 | Phase 1: Centralize model name | Pending |
| Oct 27, 2026 | Phase 2: Evaluate successor | Pending |
| Nov 3, 2026 | Phase 3: Swap + test | Pending |
| Dec 15, 2026 | ABSOLUTE LATEST START | Deadline |
| Jan 14, 2027 | DEADLINE | Deadline |

## The 3 phases in one line each

1. **Centralize** (1 hr): Add OPENAI_MODEL to global_config.py.
   Update 34 files to import from there instead of hardcoding.
2. **Evaluate** (1-2 hrs): Test OpenAI's current flagship. Pick successor.
3. **Swap** (1 hr): Set OPENAI_MODEL env var on Render. Test E2E.

## The best thing you can do first

Centralize the model name in global_config.py:

```python
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_MODEL_CHEAP = os.getenv('OPENAI_MODEL_CHEAP', OPENAI_MODEL)
OPENAI_MODEL_SMART = os.getenv('OPENAI_MODEL_SMART', 'gpt-4o')
```

Then every engine imports from global_config. Future model changes
become a 1-line env var update, not 34 file edits.

Effort: ~1 hour. Do this before anything else.

---

**If it's after Dec 15, 2026 and Phase 3 has not started, STOP
EVERYTHING AND START IT.**
