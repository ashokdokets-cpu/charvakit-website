"""
Charvak System Audit
Tests every major page, API, and feature area to report what's live, partial, or broken.
Run: python scripts/system_audit.py
"""
import os
import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime

# Use localhost for full testing, or prod for external-only testing
BASE_URL = os.getenv("AUDIT_URL", "http://localhost:8000")

# Disable SSL verification for localhost
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Pages to check (public)
PAGES = [
    # Core
    "/", "/about", "/team", "/careers", "/contact", "/capabilities",
    "/services/web-design", "/services/staff-augmentation",
    "/pricing", "/ai-credits-pricing", "/credit-dashboard",
    # Auth
    "/login", "/register", "/forgot-password", "/admin-login",
    # Content
    "/privacy", "/terms", "/refund", "/cookie-policy", "/accessibility",
    "/robots.txt", "/sitemap.xml",
    # Blog
    "/blog", "/blog/rss.xml", "/case-studies", "/testimonials",
        # AI Tools
    "/tools", "/tools/resume-roast", "/tools/role-mirror",
    "/tools/ghost-bounty", "/tools/ref-check", "/tools/ghost-tracker",
    "/tools/offer-matcher", "/tools/pitch-roast", "/tools/ref-swap",
    "/tools/bounty-swap", "/tools/counter-offer", "/tools/ghost-job-shield",
    "/tools/micro-trial", "/voice-to-web", "/neural-wireframe", "/outreach",
    "/student-suite", "/indian-language-ai", "/marketing-ai",
    # Products
    "/products", "/doketsrb", "/lock-in-breaker", "/auditbot",
    "/skill-twin", "/micro-squads", "/globalize", "/agency-twin",
    # Free tools
    "/cloud-waste-calculator", "/code-quality-checker",
    "/digital-health-checker", "/skill-check", "/revenue-leak-detector",
    # Career
    "/career-engine", "/job-board", "/post-job", "/interview-prep",
    "/micro-internship", "/ai-internship", "/hire-talent",
    "/candidate-signup", "/developer-signup",
    # Education
    "/exam-prep", "/assessments", "/training", "/ai-courses", "/lms",
        # Tier 3
    "/university", "/ats",
]

# Public APIs (no auth needed)
APIS = [
    "/api/credits/plans",
    "/api/credits/demo@charvakit.com",
    "/api/testimonials",
    "/api/blog/posts",
    "/api/payment/status",
    "/api/na/revenue/total",
    "/api/security/stats",
    "/api/email/stats",
    "/api/kyc/status",
    "/api/jobs/stats",
    "/api/student/stats",
    "/api/lms/stats",
    "/api/outreach/stats",
    "/api/enterprise/stats",
    "/api/exam/categories",
]

# Admin endpoints (expect 401 without auth — that's fine, means they exist and are protected)
ADMIN_ENDPOINTS = [
    "/api/admin/users",
    "/api/admin/purchases",
    "/api/admin/testimonials",
    "/api/admin/testimonials/stats",
    "/api/admin/analytics",
    "/api/credits/admin/stats",
    "/api/admin/cleanup-users",
]


def check(url, allow_codes=(200,)):
    """Return (status, duration_ms)."""
    import time
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CharvakAudit/1.0"})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            duration = int((time.time() - start) * 1000)
            return resp.status, duration
    except urllib.error.HTTPError as e:
        duration = int((time.time() - start) * 1000)
        return e.code, duration
    except Exception as e:
        return f"ERR:{type(e).__name__}", int((time.time() - start) * 1000)


def run_audit(paths, label, expected_ok=(200,), expected_alt=()):
    print(f"\n=== {label} ({len(paths)} items) ===")
    ok_count = 0
    issues = []
    for path in paths:
        url = BASE_URL + path
        status, ms = check(url)
        if status in expected_ok:
            ok_count += 1
            print(f"  [OK]   {path} -> {status} ({ms}ms)")
        elif status in expected_alt:
            ok_count += 1
            print(f"  [OK*]  {path} -> {status} ({ms}ms) [expected alternate]")
        else:
            issues.append((path, status))
            print(f"  [FAIL] {path} -> {status} ({ms}ms)")
    print(f"  -> {ok_count}/{len(paths)} passing")
    return issues


def main():
    print(f"\n{'='*72}")
    print(f"CHARVAK SYSTEM AUDIT")
    print(f"URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"{'='*72}")

    page_issues = run_audit(PAGES, "PUBLIC PAGES")
    api_issues = run_audit(APIS, "PUBLIC APIs")
    # Admin should return 401/403 without cookie — that means the endpoint exists and is protected
    admin_issues = run_audit(ADMIN_ENDPOINTS, "ADMIN APIs (expect 401/403 unauthenticated)",
                             expected_ok=(200,), expected_alt=(401, 403))

    all_issues = page_issues + api_issues + admin_issues

    print(f"\n{'='*72}")
    print(f"SUMMARY")
    print(f"{'='*72}")
    print(f"Total checks: {len(PAGES) + len(APIS) + len(ADMIN_ENDPOINTS)}")
    print(f"Failures: {len(all_issues)}")

    if all_issues:
        print(f"\nFailed endpoints:")
        for path, status in all_issues:
            print(f"  - {path}: {status}")
        print(f"\nRecommendation: investigate these before proceeding.")
    else:
        print(f"\nAll checks passing.")


if __name__ == "__main__":
    main()