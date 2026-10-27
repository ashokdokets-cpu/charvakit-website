"""
Generate Charvak Employer One-Pager PDF (2 pages).
Run: python scripts/generate_employer_onepager.py
Output: ~/Desktop/Charvak_Employer_OnePager.pdf
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _pdf_helpers import (
    CharvakReportPDF,
    TEAL, TEAL_DARK, INK, MUTED, SOFT, WHITE, GREEN_LIGHT, GREEN_BORDER, GREEN_TEXT,
    W, H,
    draw_brand_header, draw_title, draw_stat_row, draw_feature_block,
    draw_cta_strip, draw_numbered_step, draw_pricing_table, draw_page_footer,
    draw_section_divider,
)


def build_pdf():
    pdf = CharvakReportPDF(
        report_title="The Placement Operating System for Employers",
        user_email=None,
    )
    pdf.set_auto_page_break(auto=False, margin=15)

    # ==================== PAGE 1 ====================
    pdf.add_page()
    draw_brand_header(pdf, title_text="FOR EMPLOYERS  ·  www.charvakit.com")

    # Title + subtitle — get Y position where we should place the stat row
    after_title_y = draw_title(
        pdf,
        title="The Placement Operating System for Employers",
        subtitle="Hire verified engineers in 48 hours. Every candidate's code has already been\n"
                 "executed against real test cases — not scored by AI opinions.",
        y=36,
    )

    # Stat row — placed 6mm below where subtitle ended
    stat_y = after_title_y + 6
    draw_stat_row(pdf, [
        ("4 languages", "Python · JS · Java · TS"),
        ("43 classes", "task classes tested"),
        ("48 hours", "shortlist delivered"),
    ], y=stat_y)

    # Feature blocks
    features = [
        ("🎯", "Real code execution",
         "Deterministic test cases in Python, JS, Java, TypeScript.\n"
         "Score of 85 = 85% of test cases passed. Not AI opinion."),
        ("🔐", "HMAC-verifiable certificates",
         "Every cert has a cryptographic hash. Your hiring manager\n"
         "verifies any candidate at a public URL in 5 seconds — no login."),
        ("💬", "AI screen agent",
         "Automated 2-phase chat captures notice period, current CTC,\n"
         "and work auth. Feeds candidate into pipeline automatically."),
        ("📊", "Recruiter dashboard",
         "Screen sessions + applications + referrals in one view.\n"
         "Level tabs, charts, PDF export, one-click hire tracking."),
        ("🌍", "Compliance-ready",
         "6 jurisdictions: India DPDP + GDPR + NYC 144 + EU AI Act +\n"
         "PIPL + PDPA. 4 data residency regions on request."),
    ]

    # Feature blocks start 10mm below the stat row
    y = stat_y + 25
    for icon, title, desc in features:
        draw_feature_block(pdf, icon, title, desc, y=y)
        y += 22

    # Bottom CTA
    draw_cta_strip(
        pdf,
        main_text="See it live in 30 seconds — no login required",
        url_text="https://www.charvakit.com/demo  ·  Five live demos  ·  Scorecard + cert + screen + dashboard",
        y=H - 45,
    )

    draw_page_footer(pdf, page_label="Page 1", total_pages=2)

    # ==================== PAGE 2 ====================
    pdf.add_page()
    draw_brand_header(pdf, title_text="THE PROCESS  ·  www.charvakit.com")

    draw_title(
        pdf,
        title="How to hire verified engineers in 48 hours",
        subtitle="Four steps. No new tools. No new vendors. Everything runs inside one dashboard.",
        y=36,
    )

    # Numbered steps
    steps = [
        (1, "Paste your JD",
         "AI parses the role, skills, and seniority in about 30 seconds.\n"
         "Auto-generates a screening flow calibrated to your specific job."),
        (2, "Invite candidates",
         "Automated screen chat captures notice period, CTC, and work auth.\n"
         "Candidates complete the screening in 3-5 minutes on any device."),
        (3, "Review scorecards",
         "Verified cert + HMAC hash + skill breakdown on one page.\n"
         "Your hiring manager can defend every score to a hiring committee."),
        (4, "Mark hired",
         "One-click hire tracking in your dashboard.\n"
         "Avg CTC, top company, and pipeline metrics update automatically."),
    ]

    y = 72
    for num, title, desc in steps:
        draw_numbered_step(pdf, num, title, desc, y=y)
        y += 20

    # Section divider
    draw_section_divider(pdf, y=168)
    
    # Pricing
    pdf.set_xy(20, 174)
    pdf.set_font("DejaVu", "B", size=12)
    pdf.set_text_color(*INK)
    pdf.cell(W - 40, 6, "Pricing", align="L")

    tiers = [
        ("Free", "$0", "5 verified\ncandidates/month\n\nNo credit card"),
        ("Growth", "$199/mo", "50 candidates\nUnlimited roles\nPipeline dashboard"),
        ("Enterprise", "Custom", "Unlimited\nATS integration\nSLA + priority support"),
    ]
    draw_pricing_table(pdf, tiers, y=184)

    # Bottom CTA
    draw_cta_strip(
        pdf,
        main_text="Request a 20-minute walkthrough",
        url_text="hr@charvakit.com  ·  +91 799 7871 701  ·  https://www.charvakit.com/demo",
        y=H - 45,
    )

    draw_page_footer(pdf, page_label="Page 2", total_pages=2)

    # Save to Desktop
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    out_path = os.path.join(desktop, "Charvak_Employer_OnePager.pdf")
    pdf.output(out_path)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"✓ PDF saved: {out_path}")
    print(f"  Size: {size_kb:.1f} KB")
    return out_path


if __name__ == "__main__":
    path = build_pdf()
    print(f"\nOpen it: start \"{path}\"")