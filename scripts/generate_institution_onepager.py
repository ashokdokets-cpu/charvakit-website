"""
Generate Charvak Institution One-Pager PDF (2 pages).
Run: python scripts/generate_institution_onepager.py
Output: ~/Desktop/Charvak_Institution_OnePager.pdf
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
    draw_cta_strip, draw_numbered_step, draw_page_footer,
    draw_section_divider,
)


def build_pdf():
    pdf = CharvakReportPDF(
        report_title="The Placement Operating System for Institutions",
        user_email=None,
    )
    pdf.set_auto_page_break(auto=False, margin=15)

    # ==================== PAGE 1 ====================
    pdf.add_page()
    draw_brand_header(pdf, title_text="FOR UNIVERSITIES  ·  www.charvakit.com")

    # Title + subtitle — get Y position for stat row
    after_title_y = draw_title(
        pdf,
        title="The Placement Operating System for Universities and Colleges",
        subtitle="Prove placement readiness to your Dean in 4 weeks.\n"
                 "Dean-ready reports, HMAC-verifiable certificates, and cohort dashboards.",
        y=36,
    )

    # Stat row — 6mm below subtitle end
    stat_y = after_title_y + 6
    draw_stat_row(pdf, [
        ("138 exams", "company patterns"),
        ("34 languages", "incl. all Indian"),
        ("6 jurisdictions", "DPDP · GDPR · NYC · EU AI"),
    ], y=stat_y)

    features = [
        ("📊", "Dean-ready readiness reports",
         "Cohort score, department heatmap, 3-month trend, % certified, % certs viewed\n"
         "by employers. Signed PDF + live dashboard. The artifact your Dean actually reads."),
        ("🔐", "HMAC-verifiable certificates",
         "Every qualified student gets a cryptographic cert. Employers verify the score\n"
         "in 5 seconds at a public URL. Defensible in placement audits, board reviews."),
        ("💻", "Code execution in 4 languages",
         "Python, JavaScript, Java, TypeScript. Tested against deterministic test cases.\n"
         "43 task classes across 5 formats. SQL (SQLite) honestly labeled."),
        ("🔥", "Engagement dashboards",
         "Streaks, badges, cohort leaderboards. SMS/WhatsApp push hooks ready.\n"
         "Measurable 5-day habit adoption across your batch."),
        ("🆓", "Free 4-week pilot",
         "100-500 students per department. No contract, no cost.\n"
         "Your CDC director sees real dashboards in 48 hours. Your Dean sees the\n"
         "first readiness report by Week 2. Zero risk."),
    ]

    # Feature blocks start 10mm below stat row
    y = stat_y + 25
    for icon, title, desc in features:
        draw_feature_block(pdf, icon, title, desc, y=y)
        y += 22

    draw_cta_strip(
        pdf,
        main_text="See it live in 30 seconds — no login required",
        url_text="https://www.charvakit.com/demo  ·  Free 4-week pilot · No contract · No cost",
        y=H - 45,
    )

    draw_page_footer(pdf, page_label="Page 1", total_pages=2)

    # ==================== PAGE 2 ====================
    pdf.add_page()
    draw_brand_header(pdf, title_text="THE PILOT  ·  www.charvakit.com")

    draw_title(
        pdf,
        title="The 4-week free pilot",
        subtitle="Pick a batch. Get a signed readiness report your Dean can defend.\n"
                 "No contract, no cost, no login from your side.",
        y=36,
    )

    # Section divider
    draw_section_divider(pdf, y=70)
    
    # Week timeline
    pdf.set_xy(20, 76)
    pdf.set_font("DejaVu", "B", size=12)
    pdf.set_text_color(*INK)
    pdf.cell(W - 40, 6, "Timeline", align="L")

    weeks = [
        (1, "Week 1 — Provision + onboard",
         "Portal provisioned in 24 hours. Batch invited. First assessments start.\n"
         "Zero friction: students log in with their college email."),
        (2, "Week 2 — First Dean report",
         "Cohort readiness score, department heatmap, top 10 students.\n"
         "Delivered as a signed PDF. Your Dean reviews it while pilot is still running."),
        (3, "Week 3 — First certifications",
         "Top scorers earn HMAC-verifiable certs. Employers begin verifying.\n"
         "Engagement dashboard shows streak %, drill completions, cohort leaderboard."),
        (4, "Week 4 — Full readiness report",
         "3-month trend, % certified, % certs viewed by employers, top 10 placement-ready.\n"
         "Full pilot report + placement readiness scorecard for the board."),
    ]

    y = 86
    for num, title, desc in weeks:
        draw_numbered_step(pdf, num, title, desc, y=y)
        y += 22

    # What you get box
    pdf.set_fill_color(*GREEN_LIGHT)
    pdf.set_draw_color(*GREEN_BORDER)
    pdf.set_line_width(0.3)
    pdf.rect(20, 178, W - 40, 38, style="DF")

    pdf.set_xy(24, 181)
    pdf.set_font("DejaVu", "B", size=10)
    pdf.set_text_color(*GREEN_TEXT)
    pdf.cell(W - 48, 5, "WHAT YOU GET (in 4 weeks, zero cost)", align="L")

    pdf.set_xy(24, 188)
    pdf.set_font("DejaVu", size=9)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W - 48, 4.5,
        "✓ Dean-ready signed PDF (cohort score, dept heatmap, 3-month trend)\n"
        "✓ Live cohort dashboard (real-time engagement + readiness)\n"
        "✓ HMAC-verifiable certifications for qualified students\n"
        "✓ 100% visibility into what your Dean will see before committing\n"
        "✓ A template for future batches (renewable, not a one-time artifact)",
    )

    # Contact CTA
    draw_cta_strip(
        pdf,
        main_text="Reply with your batch size and graduation year",
        url_text="hr@charvakit.com  ·  +91 799 7871 701  ·  https://www.charvakit.com/demo",
        y=H - 45,
    )

    draw_page_footer(pdf, page_label="Page 2", total_pages=2)

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    out_path = os.path.join(desktop, "Charvak_Institution_OnePager.pdf")
    pdf.output(out_path)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"✓ PDF saved: {out_path}")
    print(f"  Size: {size_kb:.1f} KB")
    return out_path


if __name__ == "__main__":
    path = build_pdf()
    print(f"\nOpen it: start \"{path}\"")