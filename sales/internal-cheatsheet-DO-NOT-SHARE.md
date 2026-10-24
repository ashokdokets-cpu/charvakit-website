
# INTERNAL CHEATSHEET — DO NOT SHARE WITH CLIENTS

**Owner:** Bhavya only. Sales team training ONLY.
**Never share this file with any client, partner, or prospect.**

---

## 1. What Charvak Actually Is (Technical Truth)

For your own understanding. NEVER quoted to clients.

- Stack: FastAPI + Postgres (Render), Cloudflare CDN
- 62 Python engines, 192 Postgres tables
- 106 roles × 66 industries × 7 levels = ~49,000 assessment combinations
- Judge0 CE for code execution (Python, JavaScript, Java, Go, C++)
- HMAC-SHA256 for certificate signing (uses SECRET_KEY env var)
- 5 integrity signals: paste, tab_switch, contextmenu, focus_out, rapid_input
- Elo-based adaptive difficulty (ability_engine.py)
- Dokets VouchAI escrow for micro-internship (10% intern-side fee)

---

## 2. Sales Talk Track — What To Say When Asked

### Client: 'How exactly do you test candidates?'
**Say:** 'We run role-calibrated assessments that mix multiple-choice questions with real code submissions. Candidates write and run code in a controlled environment — not explain it verbally. Their performance produces a professional skill profile with per-topic breakdown.'

**DON'T say:** 'We use Judge0 running in Docker containers with HMAC signature verification.'

### Client: 'What is your certificate?'
**Say:** 'Each shortlisted candidate carries a cryptographically signed credential. You can independently verify it at a public URL — no login required — so you are not taking our word for their score.'

**DON'T say:** 'It uses HMAC-SHA256 with a shared secret stored in an environment variable.'

### Client: 'How do you prevent cheating?'
**Say:** 'Our platform records environmental signals during the assessment that indicate whether the submission is the candidate's own work. If concerns are recorded, we flag the candidate. Otherwise, we say the report is clean and you can trust it.'

**DON'T say:** 'We record paste events, tab switches, context menu opens, focus out events, and rapid input patterns.'

### Client: 'What is your tech stack?'
**Say:** 'We built our own assessment platform specifically for the Indian hiring market. It runs live — you can see it at charvakit.com.'

**DON'T say:** 'We use FastAPI, Postgres, Judge0, HMAC, OpenAI GPT-5.4-nano, Razorpay, PayPal, ElevenLabs, and Cloudflare.'

### Client: 'How is this different from HackerRank / TestGorilla / Keka?'

**Say:** 'Those are assessment libraries. Charvak is a full placement operating system — we handle assessment, shortlisting, and end-to-end placement with the micro-internship trial that de-risks the hire. Our credibility is the outcome, not just the score.'

**Internal note:** HackerRank/TestGorilla don't do placement. Keka is HRIS. Charvak is the only one doing assessment + trial + placement as one pipeline.

### Client: 'How do you compare to Naukri / iimjobs?'
**Say:** 'Naukri is a job board. We do curated placement with vetted candidates. If you use Naukri, you're screening 200 CVs. If you use Charvak, you're interviewing 3.'

### Client: 'Why should I pay 8.33% when Naukri is free?'
**Say:** 'Naukri is free because they don't guarantee candidates. We do. Our fee is comparable to industry standard — Belong, Xpheno, ABC Consultants all charge similar. What is different is: verified candidates, escrow-protected trial, 90-day replacement guarantee.'

---

