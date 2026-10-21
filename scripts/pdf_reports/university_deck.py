"""Generate University Partnership Deck PDF (SAMPLE) - 8 pages."""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import white as _white
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from datetime import datetime

OUTPUT = 'reports/Charvak-University-Deck-SAMPLE.pdf'
TOTAL_PAGES = 8

c = canvas.Canvas(OUTPUT, pagesize=A4)

# ============ PAGE 1: COVER ============
c.setFillColor(DARK_TEAL)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

# Decorative shapes
c.setFillColor(colors.HexColor('#2a8a75'))
c.circle(PAGE_WIDTH, PAGE_HEIGHT, 350, fill=1, stroke=0)
c.circle(0, 0, 250, fill=1, stroke=0)

# SAMPLE badge top
c.setFillColor(RED)
c.roundRect(PAGE_WIDTH - 200, PAGE_HEIGHT - 55, 160, 32, 5, fill=1, stroke=0)
c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 9)
c.drawCentredString(PAGE_WIDTH - 120, PAGE_HEIGHT - 42, 'SAMPLE PARTNERSHIP PROPOSAL')
c.setFont('Helvetica', 7)
c.drawCentredString(PAGE_WIDTH - 120, PAGE_HEIGHT - 50, 'Illustrative numbers')

# Main content centered
c.setFillColor(WHITE)
c.setFont('Helvetica', 11)
c.drawString(40, PAGE_HEIGHT - 120, 'CHARVAK IT CONSULTING')

c.setFont('Helvetica-Bold', 48)
c.drawString(40, PAGE_HEIGHT - 240, 'Career Readiness')
c.drawString(40, PAGE_HEIGHT - 295, 'Infrastructure')
c.drawString(40, PAGE_HEIGHT - 350, 'for Higher Education')

c.setFont('Helvetica', 16)
c.setFillColor(colors.HexColor('#b8e0d6'))
c.drawString(40, PAGE_HEIGHT - 400, 'A partnership proposal from Charvak')

# White card with details
draw_rounded_rect(c, 40, 180, PAGE_WIDTH - 80, 130, radius=10, fill_color=WHITE)

c.setFillColor(MID_GRAY)
c.setFont('Helvetica', 9)
c.drawString(60, 270, 'PREPARED FOR')
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 14)
c.drawString(60, 250, 'Your University (Sample)')

c.setFillColor(MID_GRAY)
c.setFont('Helvetica', 9)
c.drawString(60, 220, 'PREPARED BY')
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 11)
c.drawString(60, 205, 'Bhavya M · Founder & CEO')
c.setFont('Helvetica', 10)
c.setFillColor(MID_GRAY)
c.drawString(60, 190, 'Charvak IT Consulting Pvt Ltd')

# Footer
c.setFillColor(colors.HexColor('#b8e0d6'))
c.setFont('Helvetica', 9)
c.drawString(40, 100, f'Date: {datetime.now().strftime("%B %d, %Y")}')
c.drawString(40, 85, 'https://www.charvakit.com  ·  hr@charvakit.com  ·  +91 799 7871 701')

draw_page_number(c, 1, TOTAL_PAGES)
c.showPage()

# ============ PAGE 2: THE PROBLEM ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'THE PROBLEM', 'Why current approaches fall short')

# Big stat on left
draw_rounded_rect(c, 40, PAGE_HEIGHT - 260, 220, 150, radius=10, fill_color=TEAL)
c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 72)
c.drawCentredString(150, PAGE_HEIGHT - 190, '45%')
c.setFont('Helvetica', 10)
c.drawCentredString(150, PAGE_HEIGHT - 215, 'of Indian graduates')
c.drawCentredString(150, PAGE_HEIGHT - 228, 'are considered')
c.drawCentredString(150, PAGE_HEIGHT - 241, 'employable')

# Source note
c.setFillColor(MID_GRAY)
c.setFont('Helvetica', 8)
c.drawCentredString(150, PAGE_HEIGHT - 275, 'Source: India Skills Report')

# Right side - 3 smaller stats
right_stats = [
    ('1.5 Crore', 'students graduate every year'),
    ('55%', 'face rejection cycles of 6-18 months'),
    ('₹2.4 Lakh Cr', 'lost annual economic value from\nunemployment and under-employment'),
]

y_pos = PAGE_HEIGHT - 130
for value, label in right_stats:
    draw_rounded_rect(c, 280, y_pos - 55, PAGE_WIDTH - 320, 55, radius=8, fill_color=WHITE,
                      stroke_color=colors.HexColor('#d1fae5'))
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(295, y_pos - 25, value)
    c.setFont('Helvetica', 9)
    c.setFillColor(MID_GRAY)
    c.drawString(295, y_pos - 45, label)
    y_pos -= 65

# Bottom explanation
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 11)
c.drawString(40, 280, 'The root cause:')

c.setFont('Helvetica', 10)
c.setFillColor(MID_GRAY)
c.drawString(40, 258, 'Institutions measure aptitude and CGPA, but not actual career readiness.')
c.drawString(40, 242, 'Students discover gaps only through rejections — months after graduation')
c.drawString(40, 226, 'when it is too late to fix them.')

# Bottom callout
draw_rounded_rect(c, 40, 130, PAGE_WIDTH - 80, 65, radius=8, fill_color=colors.HexColor('#fef3c7'))
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 11)
c.drawString(55, 175, '⚠ THE OPPORTUNITY')
c.setFont('Helvetica', 10)
c.drawString(55, 155, 'Institutions that measure readiness can intervene BEFORE rejection cycles.')
c.drawString(55, 140, 'That intervention is our product.')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 2, TOTAL_PAGES)
c.showPage()

# ============ PAGE 3: WHAT WE BUILD ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'OUR PRODUCT SUITE', 'Four integrated products for institutional buyers')

# 2x2 grid of product cards
card_w = (PAGE_WIDTH - 100) / 2
card_h = 165
positions = [
    (40, PAGE_HEIGHT - 220),
    (60 + card_w, PAGE_HEIGHT - 220),
    (40, PAGE_HEIGHT - 405),
    (60 + card_w, PAGE_HEIGHT - 405),
]

products = [
    ('Career Assessment Engine', '106 roles × 66 industries × 7 levels',
     '8 assessment formats\nAI-generated questions per role'),
    ('Verified Certificates', 'Digitally signed, publicly verifiable',
     'Free for score ≥ 85\nEmployer-trusted'),
    ('Placement Dashboard', 'Aggregate readiness per batch',
     'Per-department tracking\nWeekly reports'),
    ('Bulk Verification API', 'Verify 100+ certs per call',
     'Free pilot tier: 500 verifications\nFor placement cells at scale'),
]

for (title, tagline, details), (x, y) in zip(products, positions):
    draw_card(c, x, y - card_h, card_w, card_h, bg_color=WHITE,
              border_color=colors.HexColor('#d1fae5'))

    # Icon circle
    c.setFillColor(TEAL)
    c.circle(x + 30, y - 30, 15, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(x + 30, y - 35, title[0])

    # Title
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(x + 55, y - 35, title)

    # Tagline
    c.setFillColor(MID_GRAY)
    c.setFont('Helvetica', 9)
    c.drawString(x + 15, y - 65, tagline)

    # Details
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica', 9)
    detail_y = y - 90
    for line in details.split('\n'):
        c.drawString(x + 15, detail_y, line)
        detail_y -= 14

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 3, TOTAL_PAGES)
c.showPage()

# ============ PAGE 4: HOW IT WORKS ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'HOW A PARTNERSHIP WORKS', 'From onboarding to outcomes in 8 weeks')

# 5 steps vertical timeline
steps = [
    ('WEEK 1', 'ONBOARDING', 'Bulk cohort creation\nDepartment mapping\nPlacement cell training', TEAL),
    ('WEEK 1-2', 'BASELINE ASSESSMENT', 'Students take free assessments\nPer-student diagnostic reports\nAggregate batch readiness', colors.HexColor('#2a8a75')),
    ('WEEK 3-4', 'INTERVENTION', 'AI-generated learning paths\nRecommended interventions per department', GREEN),
    ('WEEK 4-6', 'VERIFICATION', 'Students retake assessments\nEligible students get verified certificates', YELLOW),
    ('WEEK 6-8', 'OUTCOMES', 'Placement tracking\nVerified hires report\nYear-long partnership decision', colors.HexColor('#dc3545')),
]

y_pos = PAGE_HEIGHT - 130
card_h = 85
for i, (week, title, detail, color) in enumerate(steps):
    # Number circle
    c.setFillColor(color)
    c.circle(60, y_pos - card_h / 2, 20, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(60, y_pos - card_h / 2 - 5, str(i + 1))

    # Card
    draw_rounded_rect(c, 100, y_pos - card_h, PAGE_WIDTH - 140, card_h, radius=8, fill_color=WHITE)

    # Week label
    c.setFillColor(color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(120, y_pos - 20, week)

    # Title
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(120, y_pos - 40, title)

    # Details
    c.setFillColor(MID_GRAY)
    c.setFont('Helvetica', 9)
    detail_y = y_pos - 55
    for line in detail.split('\n'):
        c.drawString(120, detail_y, line)
        detail_y -= 11

    y_pos -= (card_h + 8)

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 4, TOTAL_PAGES)
c.showPage()

# ============ PAGE 5: PILOT PROPOSAL ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'THE PILOT WE PROPOSE', 'Free 4-week pilot · 100-500 students · Zero commitment')

# ========== BIG CTA BLOCK (top) ==========
draw_rounded_rect(c, 40, PAGE_HEIGHT - 200, PAGE_WIDTH - 80, 120, radius=12, fill_color=TEAL)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 28)
c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 105, 'FREE 4-WEEK PILOT')

c.setFont('Helvetica', 14)
c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 135, '100-500 students')

c.setFont('Helvetica', 11)
c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 165, 'Zero cost · Zero commitment · Zero strings')

# ========== 3 COLUMNS (middle, y=320-560) ==========
col_w = (PAGE_WIDTH - 100) / 3   # ~165px per column
col_top = PAGE_HEIGHT - 260       # 582
col_bottom = 320                  # bottom of columns
col_h = col_top - col_bottom      # 262

columns = [
    ('WHAT YOU GET', TEAL, [
        'Bulk cohort setup',
        'Free assessments',
        'Diagnostic reports',
        'Placement dashboard',
        'Weekly reports',
        'End-of-pilot report',
        'Optional co-branding',
    ]),
    ('WHAT WE GET', DARK_TEAL, [
        'Real usage data',
        'Platform feedback',
        'Case study material',
        'Employer intros',
        'Path to partnership',
    ]),
    ('WHAT IT PROVES', GREEN, [
        'Engagement rate',
        'Real skill gaps',
        'Employer trust',
        'ROI of model',
        'Placement outcomes',
    ]),
]

x = 40
for col_title, col_color, items in columns:
    # Card background
    draw_rounded_rect(c, x, col_bottom, col_w - 10, col_h, radius=10, fill_color=WHITE,
                      stroke_color=colors.HexColor('#e5e7eb'))

    # Header bar
    c.setFillColor(col_color)
    c.rect(x, col_top - 30, col_w - 10, 30, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(x + (col_w - 10) / 2, col_top - 20, col_title)

    # Items with wrapped text
    c.setFont('Helvetica', 9)
    item_y = col_top - 55
    item_max_width = col_w - 45   # padding left + checkmark space

    for item in items:
        # Checkmark
        c.setFillColor(col_color)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(x + 12, item_y, '>')

        # Item text (wrapped if long)
        c.setFillColor(CHARCOAL)
        c.setFont('Helvetica', 9)
        wrap_text(c, item, x + 24, item_y, item_max_width, 'Helvetica', 9, 11, 2)

        # Advance based on whether item wrapped
        from reportlab.pdfbase.pdfmetrics import stringWidth
        if stringWidth(item, 'Helvetica', 9) > item_max_width:
            item_y -= 28   # 2 lines + spacing
        else:
            item_y -= 20   # 1 line + spacing

    x += col_w + 5

# ========== BOTTOM PRICING CALLOUT (bottom, y=130-215) ==========
draw_rounded_rect(c, 40, 130, PAGE_WIDTH - 80, 90, radius=10, fill_color=colors.HexColor('#fef3c7'))

c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 11)
c.drawString(55, 200, '>> IF PILOT DELIVERS VALUE')

c.setFont('Helvetica', 9)
c.drawString(55, 182, 'We discuss a 12-month partnership:')
c.drawString(55, 167, 'Department (up to 500): Rs 49,999/year  ·  Campus (up to 5,000): Rs 1,99,999/year')
c.drawString(55, 152, 'University (unlimited): Rs 4,99,999/year')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 5, TOTAL_PAGES)
c.showPage()
# ============ PAGE 6: PRICING TIERS ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'PARTNERSHIP TIERS', 'Four tiers, annual contracts')

# 4 tier cards - calculated dimensions
tier_gap = 6
tier_w = (PAGE_WIDTH - 60 - (tier_gap * 3)) / 4   # (595-60-18)/4 = ~129px per card
tier_h = 420
tier_top = PAGE_HEIGHT - 110                       # 732 (below header)
tier_bottom = tier_top - tier_h                    # 312

tiers = [
    ('PILOT', 'Free', ['500 students', '4 weeks', 'Full access', 'No commit'], LIGHT_GRAY, CHARCOAL, False),
    ('DEPARTMENT', 'Rs 49,999', ['500 students', '12 months', 'Full platform', 'Dept dashboard', 'Bi-weekly reports'], WHITE, MID_GRAY, False),
    ('CAMPUS', 'Rs 1,99,999', ['5,000 students', '12 months', 'Everything in Dept', 'Multi-dept dashboard', 'Co-branded certs', 'CAS API access'], TEAL, TEAL, True),
    ('UNIVERSITY', 'Rs 4,99,999', ['Unlimited', '12 months', 'Everything in Campus', 'Multi-campus', 'SSO integration', 'Priority support'], DARK_TEAL, DARK_TEAL, False),
]

x = 30
for name, price, features, bg, border, is_recommended in tiers:
    card_x = x
    card_y = tier_bottom
    card_w = tier_w
    card_h = tier_h

    # Card background
    if is_recommended:
        draw_rounded_rect(c, card_x, card_y, card_w, card_h, radius=10, fill_color=bg)
        text_color = WHITE
        feature_color = WHITE
    else:
        draw_rounded_rect(c, card_x, card_y, card_w, card_h, radius=10,
                          fill_color=bg, stroke_color=border)
        text_color = CHARCOAL
        feature_color = CHARCOAL

    # Recommended badge (drawn over card top)
    if is_recommended:
        badge_w = card_w - 20
        badge_x = card_x + 10
        badge_y = card_y + card_h - 28
        c.setFillColor(YELLOW)
        c.roundRect(badge_x, badge_y, badge_w, 20, 4, fill=1, stroke=0)
        c.setFillColor(CHARCOAL)
        c.setFont('Helvetica-Bold', 7)
        c.drawCentredString(card_x + card_w / 2, badge_y + 6, 'RECOMMENDED')

    # Card title
    title_y = card_y + card_h - 55
    c.setFillColor(text_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(card_x + card_w / 2, title_y, name)

    # Price
    price_y = title_y - 22
    c.setFillColor(WHITE if is_recommended else CHARCOAL)
    c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(card_x + card_w / 2, price_y, price)

    # Per year note
    if price != 'Free':
        c.setFont('Helvetica', 8)
        c.setFillColor(colors.HexColor('#e0f0ec') if is_recommended else MID_GRAY)
        c.drawCentredString(card_x + card_w / 2, price_y - 13, 'per year')

    # Divider line
    div_y = price_y - 35
    c.setStrokeColor(WHITE if is_recommended else colors.HexColor('#e5e7eb'))
    c.setLineWidth(0.7)
    c.line(card_x + 12, div_y, card_x + card_w - 12, div_y)

    # Features (wrapped to fit card width)
    feature_y = div_y - 18
    feature_max_width = card_w - 30
    c.setFont('Helvetica', 8.5)

    for feature in features:
        # Checkmark
        c.setFillColor(YELLOW if is_recommended else GREEN)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(card_x + 12, feature_y, '>')

        # Feature text - wrapped
        c.setFillColor(feature_color)
        c.setFont('Helvetica', 8.5)
        lines_drawn = wrap_text(c, feature, card_x + 22, feature_y, feature_max_width,
                                'Helvetica', 8.5, 10, 2)

        feature_y -= (10 * lines_drawn + 5)

    x += tier_w + tier_gap

# Footer note
c.setFillColor(MID_GRAY)
c.setFont('Helvetica', 8)
c.drawCentredString(PAGE_WIDTH / 2, 130, '* Sample pricing. Final pricing depends on student count,')
c.drawCentredString(PAGE_WIDTH / 2, 116, 'department scope, and contract length. Discuss with our team.')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 6, TOTAL_PAGES)
c.showPage()
# ============ PAGE 7: WHY CHARVAK ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'WHY CHARVAK', 'What makes us different from EdTech incumbents')

# Left and right columns
col_w = (PAGE_WIDTH - 80) / 2

# Left column
c.setFillColor(TEAL)
c.setFont('Helvetica-Bold', 14)
c.drawString(40, PAGE_HEIGHT - 100, 'BUILT BY ENGINEERS')
c.drawString(40, PAGE_HEIGHT - 118, 'FOR EDUCATORS')

left_items = [
    ('Bootstrapped, no VC dependency', 'Every feature shipped because it works'),
    ('40+ features in 6 months', 'Continuous shipping, not roadmap slides'),
    ('Zero crashes in pilot deployments', 'Real production stability'),
    ('12,500+ question bank', 'Deep content depth, not surface coverage'),
    ('106 career roles calibrated', 'Every role validated against industry'),
]

y = PAGE_HEIGHT - 150
for title, desc in left_items:
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, y, '✓ ' + title)
    c.setFont('Helvetica', 9)
    c.setFillColor(MID_GRAY)
    c.drawString(52, y - 13, desc)
    y -= 40

# Right column
c.setFillColor(TEAL)
c.setFont('Helvetica-Bold', 14)
c.drawString(PAGE_WIDTH / 2 + 20, PAGE_HEIGHT - 100, 'PROVEN')
c.drawString(PAGE_WIDTH / 2 + 20, PAGE_HEIGHT - 118, 'INTEGRATIONS')

right_items = [
    ('DoketsRB bidirectional sync', 'Live on production'),
    ('Razorpay + PayPal', 'Live payment processing'),
    ('Employer dashboards', 'Used by HR teams'),
    ('Bulk verification API', 'Used by placement cells'),
    ('Digitally signed certificates', 'Employer-verifiable'),
]

y = PAGE_HEIGHT - 150
for title, desc in right_items:
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(PAGE_WIDTH / 2 + 20, y, '✓ ' + title)
    c.setFont('Helvetica', 9)
    c.setFillColor(MID_GRAY)
    c.drawString(PAGE_WIDTH / 2 + 32, y - 13, desc)
    y -= 40

# Bottom commitment callout
callout_y = 130
draw_rounded_rect(c, 40, callout_y, PAGE_WIDTH - 80, 100, radius=10, fill_color=TEAL)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 12)
c.drawString(55, callout_y + 78, 'COMMITMENT TO OUTCOMES')

c.setFont('Helvetica', 10)
c.drawString(55, callout_y + 58, '→ We measure students placed, not just tests taken')
c.drawString(55, callout_y + 42, '→ No paywall on certificates for score ≥ 85')
c.drawString(55, callout_y + 26, '→ Pilot is truly free — zero strings attached')
c.drawString(55, callout_y + 10, '→ Partnership is a 12-month engagement, not a one-time sale')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 7, TOTAL_PAGES)
c.showPage()

# ============ PAGE 8: NEXT STEPS ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'NEXT STEPS', 'From review to launch in 3 steps')

# ========== STEP CARDS (top section) ==========
step_w = (PAGE_WIDTH - 120) / 3
step_h = 150
step_y = PAGE_HEIGHT - 250

steps = [
    ('1', 'REVIEW', 'Read this proposal.\nSend questions to\nhr@charvakit.com', TEAL),
    ('2', 'SCHEDULE', '20-min demo call\nwith your CDC team.\nMon-Fri, 10am-6pm IST', YELLOW),
    ('3', 'LAUNCH', 'Pilot starts in 1 week.\nFirst assessment\nin week 2.', GREEN),
]

x = 40
for num, title, detail, color in steps:
    # Card
    draw_rounded_rect(c, x, step_y - step_h, step_w - 8, step_h, radius=10, fill_color=WHITE,
                      stroke_color=colors.HexColor('#e5e7eb'))

    # Number circle
    c.setFillColor(color)
    c.circle(x + step_w / 2 - 4, step_y - 35, 22, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(x + step_w / 2 - 4, step_y - 42, num)

    # Title
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(x + step_w / 2 - 4, step_y - 78, title)

    # Detail
    c.setFillColor(MID_GRAY)
    c.setFont('Helvetica', 8.5)
    detail_y = step_y - 100
    for line in detail.split('\n'):
        c.drawCentredString(x + step_w / 2 - 4, detail_y, line)
        detail_y -= 11

    x += step_w + 4

# ========== BIG CTA (middle section) ==========
cta_w = PAGE_WIDTH - 120
cta_h = 130
cta_x = 60
cta_y = 260

draw_rounded_rect(c, cta_x, cta_y, cta_w, cta_h, radius=14, fill_color=DARK_TEAL)

# CTA headline
c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 26)
c.drawCentredString(PAGE_WIDTH / 2, cta_y + 95, "Let's build this together.")

# Divider line
c.setStrokeColor(colors.HexColor('#4db8a0'))
c.setLineWidth(0.5)
c.line(cta_x + 40, cta_y + 78, cta_x + cta_w - 40, cta_y + 78)

# Who to contact
c.setFillColor(colors.HexColor('#b8e0d6'))
c.setFont('Helvetica', 10)
c.drawCentredString(PAGE_WIDTH / 2, cta_y + 60, 'To move forward, contact:')

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 14)
c.drawCentredString(PAGE_WIDTH / 2, cta_y + 38, 'Bhavya M  ·  Founder & CEO')

# ========== CONTACT INFO (bottom section) ==========
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 13)
c.drawCentredString(PAGE_WIDTH / 2, 200, 'hr@charvakit.com  ·  +91 799 7871 701')

c.setFont('Helvetica', 11)
c.setFillColor(TEAL)
c.drawCentredString(PAGE_WIDTH / 2, 178, 'https://www.charvakit.com')

# Divider
c.setStrokeColor(colors.HexColor('#e5e7eb'))
c.setLineWidth(0.5)
c.line(140, 155, PAGE_WIDTH - 140, 155)

# Address
c.setFillColor(MID_GRAY)
c.setFont('Helvetica', 9)
c.drawCentredString(PAGE_WIDTH / 2, 135, 'Charvak IT Consulting Pvt Ltd')
c.drawCentredString(PAGE_WIDTH / 2, 120, '#301, Sri Padmavati Towers, 3rd Lane')
c.drawCentredString(PAGE_WIDTH / 2, 107, 'Seetaram Nagar, Guntur 522001')
c.drawCentredString(PAGE_WIDTH / 2, 94, 'Andhra Pradesh, India')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 8, TOTAL_PAGES)
c.save()
print(f'Generated: {OUTPUT}')
print(f'Pages: {TOTAL_PAGES}')
print(f'Size: {os.path.getsize(OUTPUT)} bytes')
