# VENDOR INFLOW SETUP — Session 108A

**Purpose:** Configure automated job/JD email inflow so Feature 1-5 (Bench-Placement Agent) receives jobs passively.

**Owner:** Bhavya M
**Created:** 2026-11-08
**Status:** ACTIVE — user completes subscriptions manually

---

## WHY THIS EXISTS

Bench-Placement Agent already has:
- Email parser (jd-parser@charvakit.com)
- AI field extraction (11 fields per JD)
- Auto-match to bench candidates (Feature 5)
- One-click submit with resume PDF + cert URL

What it does NOT have: **job inflow**. Currently you only get JDs from vendors who happen to email you.

This guide unblocks **6-8 automated subscription channels** so 50-200 JDs/day flow into the parser. Zero manual paste.

**Note:** CBREX is already configured separately (Sessions 22-24). Do NOT duplicate.

---

## CHANNEL 1 — ARDENT (Vendor Network)

**What it is:** US staffing marketplace. Vendor-to-vendor JD exchange.

**Signup:** https://www.ardentstaffing.com/vendors

**Cost:** Free

**What arrives:** Daily email digest with 20-50 contract JDs (mostly US tech, H1B-friendly)

**Filter recommendation:**
- Roles: Developer, Engineer, Analyst, DevOps, Cloud
- Location: USA
- Type: Contract / C2C / W2

**Setup steps:**
1. Click 'Sign up as Vendor'
2. Complete profile (use hr@charvakit.com)
3. Enable 'Daily JD Digest' notifications
4. Set alert filters as above
5. Save

**Forwarding:** Every email from *@ardentstaffing.com -> forward to jd-parser@charvakit.com

---

## CHANNEL 2 — TALENTIFY (Vendor Network)

**What it is:** Bench-sales-focused vendor network. H1B/OPT-heavy.

**Signup:** https://www.talentify.io/vendors

**Cost:** Free

**What arrives:** 30-80 contract JDs/day

**Setup steps:**
1. Sign up at signup URL
2. Verify email
3. Enable 'Vendor Notifications' in preferences
4. Create saved searches for: Kubernetes, DevOps, Data Engineer

**Forwarding:** *@talentify.io -> jd-parser@charvakit.com

---

## CHANNEL 3 — TECHFETCH (Bench-Specific Board)

**What it is:** The original H1B/bench board. Most relevant to your candidates.

**Signup:** https://www.techfetch.com/vendor-registration

**Cost:** Free tier available

**What arrives:** 20-50 contract JDs/day, H1B-heavy

**Setup steps:**
1. Register as 'Vendor' (not candidate)
2. Enable 'Daily JD Alerts'
3. Set search: Senior Kubernetes Engineer + AWS DevOps + Data Engineer
4. Filter: US-only, contract only

**Forwarding:** *@techfetch.com -> jd-parser@charvakit.com

---

## CHANNEL 4 — DICE EMAIL ALERTS

**What it is:** Dice.com daily/weekly JD digests (not scraping — legitimate email alerts).

**Signup:** https://www.dice.com/alerts

**Cost:** Free

**What arrives:** 10-30 JDs per alert, US contract tech

**Setup steps:**
1. Log in to Dice (or create account with hr@charvakit.com)
2. Create 3 alerts:
   - Alert 1: Senior Kubernetes Engineer — Location USA — Contract
   - Alert 2: AWS DevOps — Location USA — Contract
   - Alert 3: Cloud Engineer — Location USA — Contract
3. Frequency: Daily

**Forwarding:** *@dice.com -> jd-parser@charvakit.com

---

## CHANNEL 5 — INDEED ALERTS

**What it is:** Indeed job alert emails (legitimate, no scraping).

**Signup:** https://www.indeed.com/alerts

**Cost:** Free

**What arrives:** 15-25 JDs per alert, US contract tech

**Setup steps:**
1. Create Indeed account with hr@charvakit.com
2. Create 2 alerts:
   - Alert 1: Kubernetes contract — USA only — last 7 days
   - Alert 2: DevOps contract — USA only — last 7 days
3. Frequency: Daily

**Forwarding:** *@indeed.com -> jd-parser@charvakit.com

**Do NOT scrape Indeed.** Use only the email alerts.

---

## CHANNEL 6 — LINKEDIN JOB ALERTS

**What it is:** LinkedIn job alert emails (legitimate, no scraping).

**Signup:** https://www.linkedin.com/jobs/search/

**Cost:** Free

**What arrives:** 10-20 JDs per alert, mixed quality

**Setup steps:**
1. Search: Senior Kubernetes Engineer — location United States
2. Click 'Set Alert'
3. Frequency: Daily
4. Enable 'Contract' filter
5. Repeat for DevOps

**Forwarding:** jobs-listings@linkedin.com -> jd-parser@charvakit.com

**Do NOT scrape LinkedIn.** Use only the email alerts.

---

## CHANNEL 7 — WELLFOUND (Startup Tech)

**What it is:** Startup job alerts. Contract tech roles.

**Signup:** https://wellfound.com/jobs

**Cost:** Free

**What arrives:** 5-15 JDs per alert

**Setup steps:**
1. Sign up with hr@charvakit.com
2. Search: Kubernetes — Remote (US only)
3. Subscribe to weekly digest

**Forwarding:** *@wellfound.com -> jd-parser@charvakit.com

---

## CHANNEL 8 — VENDOR NEUTRAL (Premium, Optional)

**What it is:** Premium vendor network. Higher-quality JDs, small monthly fee.

**Signup:** https://www.vendor-neutral.com/pricing

**Cost:** ~$49-99/month

**What arrives:** 50-100 JDs/day, US-only, higher client quality

**Decision:** Set this up ONLY if Channels 1-3 prove insufficient. Start with the free ones.

---

## GMAIL FORWARDING RULES

Once subscriptions arrive, configure Gmail to auto-forward all JD emails to the parser.

### Setup

1. Open Gmail settings -> 'Forwarding and POP/IMAP'
2. Add forwarding address: jd-parser@charvakit.com
3. Verify with the code Gmail sends

### Create filters

Gmail settings -> 'Filters and Blocked Addresses' -> 'Create a new filter'

**Filter 1 — Vendor networks:**
- From: ardentstaffing.com OR talentify.io OR techfetch.com OR vendor-neutral.com
- Action: Forward to jd-parser@charvakit.com
- Also: Apply label JD-Inflow

**Filter 2 — Job boards:**
- From: dice.com OR indeed.com OR wellfound.com
- Subject: job OR alert OR JD OR opportunity
- Action: Forward to jd-parser@charvakit.com
- Also: Apply label JD-Inflow

**Filter 3 — LinkedIn:**
- From: jobs-listings@linkedin.com
- Action: Forward to jd-parser@charvakit.com
- Also: Apply label JD-Inflow

**Filter 4 — CBREX (verify already setup):**
- From: cbreex.com OR cbreexglobal.com
- Action: Forward to jd-parser@charvakit.com

---

## VERIFICATION — Is It Working?

After 24 hours of subscriptions:

**Step 1 — Check parser inbox receives**
Log in to the parser account. Count emails received in last 24h.
Expected: 30-150 JDs from all channels

**Step 2 — Check DB ingestion**
SELECT COUNT(*) FROM charvak_vendor_jds WHERE parsed_at > NOW() - INTERVAL '24 hours';
Expected: Same number as emails received (or close)

**Step 3 — Check dashboard**
Open /admin/vendor-jds — new JDs should show sorted by parsed_at DESC

**Step 4 — Check auto-matches**
Open /admin/bench-matches — new JDs should auto-match to PREM/ABHINAYA/Haritha

**If any step fails:**
- Email forwarding not set up -> check Gmail filters
- Parser not receiving -> check jd-parser@charvakit.com inbox
- Ingestion failing -> check Render logs for parser errors
- Matches not computing -> check Feature 5 (auto-match on JD ingest)

---

## WEEKLY MAINTENANCE (15 min every Friday)

**Review volume:**
SELECT DATE(parsed_at) AS day, COUNT(*) FROM charvak_vendor_jds WHERE parsed_at > NOW() - INTERVAL '7 days' GROUP BY day ORDER BY day DESC;

**Review match quality:**
SELECT COUNT(*) FILTER (WHERE match_score >= 80) AS high, COUNT(*) FILTER (WHERE match_score >= 60 AND match_score < 80) AS mid FROM charvak_bench_matches WHERE computed_at > NOW() - INTERVAL '7 days';

**Decisions:**
- If JDs > 500/day with < 5 matches -> sources too noisy, filter harder or unsubscribe
- If JDs < 20/day -> add more sources or increase alert frequency
- If matches > 20 at 80+ -> excellent, tools working as intended

**Unsubscribe from:**
- Sources with 0 matches in last 2 weeks
- Sources with expired JDs (posted > 30 days ago)
- Sources sending non-US jobs

---

## EXPECTED OUTCOME

After all channels configured (24-48 hours setup):

| Metric | Target |
|---|---|
| JDs received/day | 50-200 |
| Parsed successfully | 90%+ |
| US-eligible after filter | 60-80% |
| Auto-matches 60+ | 10-30/day |
| Auto-matches 80+ | 3-8/day |

With 3-8 good matches/day and 1-click submit, you have a real staffing pipeline.

---

## ANTI-PATTERNS TO AVOID

1. Do NOT scrape any of these sites. Only use their email alert features.
2. Do NOT subscribe to paid networks before free ones work.
3. Do NOT set up all channels at once. Start with 3 (Ardent, TechFetch, Dice), verify, then add more.
4. Do NOT ignore unsubscribe. Dead channels clutter inbox and hurt signal.
5. Do NOT let the parser inbox fill. If 500+ unread, either unsubscribed or setup cleanup cron.

---

## RELATED FILES

- JOB-BOARD-EXTENSION-FLAG.md — API source roadmap (Remotive/Arbeitnow done; more in 108B)
- COMMITMENT.md — Session 108 tracking
- NEXT-SESSION-PLAN.md — Session 108 task list

---

**Owner:** Bhavya M
**Created:** 2026-11-08
**Status:** ACTIVE — user completes subscriptions manually
**Next review:** After 1 week of inflow (2026-11-15)