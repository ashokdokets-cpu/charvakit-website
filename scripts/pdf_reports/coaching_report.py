"""Generate Coaching Center Progress Report PDF (SAMPLE) - 4 pages."""
from reportlab.pdfgen import canvas
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from datetime import datetime

OUTPUT = 'reports/Charvak-Coaching-Report-SAMPLE.pdf'
TOTAL_PAGES = 4

BATCH = {
    'center': 'Sample Coaching Center',
    'batch': 'JEE 2027 Batch',
    'total_students': 100,
    'active': 96,
    'avg_w3': 62,
    'avg_w1': 50,
    'improvement': 12,
    'top_performers': [
        ('Student A', 88, 18),
        ('Student B', 85, 15),
        ('Student C', 84, 22),
        ('Student D', 82, 10),
        ('Student E', 81, 14),
    ],
    'struggling': [
        ('Student F', 32, 45),
        ('Student G', 35, 38),
        ('Student H', 38, 42),
        ('Student I', 39, 40),
        ('Student J', 40, 35),
        ('Student K', 41, 44),
    ],
    'weekly_trend': [(1, 50), (2, 56), (3, 62)],
}

c = canvas.Canvas(OUTPUT, pagesize=A4)

# ============ PAGE 1: COVER ============
# Split diagonal
c.setFillColor(TEAL)
c.rect(0, PAGE_HEIGHT / 2, PAGE_WIDTH, PAGE_HEIGHT / 2, fill=1, stroke=0)

c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT / 2, fill=1, stroke=0)

# Diagonal accent
c.setFillColor(DARK_TEAL)
c.circle(PAGE_WIDTH + 100, PAGE_HEIGHT - 100, 200, fill=1, stroke=0)

# Top-left text
c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 10)
c.drawString(40, PAGE_HEIGHT - 50, 'WEEK 3 PROGRESS REPORT')

c.setFont('Helvetica', 9)
c.drawString(40, PAGE_HEIGHT - 68, f"{BATCH['batch']}  ·  {BATCH['center']}")

# Big improvement number
c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 96)
c.drawString(40, PAGE_HEIGHT - 220, f"+{BATCH['improvement']}")

c.setFont('Helvetica', 18)
c.drawString(240, PAGE_HEIGHT - 220, 'avg. score improvement')

c.setFont('Helvetica', 12)
c.drawString(40, PAGE_HEIGHT - 260, f"From {BATCH['avg_w1']}/100 to {BATCH['avg_w3']}/100 in 3 weeks")

c.setFont('Helvetica', 10)
c.setFillColor(colors.HexColor('#b8e0d6'))
c.drawString(40, PAGE_HEIGHT - 290, f"Sample size: {BATCH['total_students']} students  ·  {BATCH['active']} active")

# Bottom - SAMPLE note
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 11)
c.drawString(40, 220, 'SAMPLE REPORT')
c.setFont('Helvetica', 9)
c.setFillColor(MID_GRAY)
c.drawString(40, 200, 'Fictional data for demonstration. Your report')
c.drawString(40, 185, 'uses your batch\'s actual performance data.')
c.drawString(40, 170, 'Delivered weekly during your 4-week pilot.')

# Bottom-right - Charvak
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 14)
c.drawString(PAGE_WIDTH - 200, 220, 'Charvak')
c.setFillColor(MID_GRAY)
c.setFont('Helvetica', 9)
c.drawString(PAGE_WIDTH - 200, 205, 'https://www.charvakit.com')
c.drawString(PAGE_WIDTH - 200, 190, 'hr@charvakit.com')
c.drawString(PAGE_WIDTH - 200, 175, f"Generated: {datetime.now().strftime('%B %d, %Y')}")

draw_sample_badge(c)
c.showPage()

# ============ PAGE 2: BATCH OVERVIEW ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'BATCH OVERVIEW', 'Week-over-week performance across your batch')

# 4 stat cards
card_w = (PAGE_WIDTH - 100) / 4
card_y = PAGE_HEIGHT - 240
stats = [
    (str(BATCH['total_students']), 'Total Students', '100% enrolled'),
    (f"{BATCH['active']}", 'Active Assessed', '96% engagement'),
    (f"{BATCH['avg_w3']}/100", 'Avg Score (W3)', 'Current'),
    (f"+{BATCH['improvement']}", 'Improvement', 'W1 to W3'),
]

x = 40
for value, label, sub in stats:
    draw_stat_card(c, x, card_y, card_w - 10, 100, value, label, sub)
    x += card_w

# Weekly trend chart
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 14)
c.drawString(40, PAGE_HEIGHT - 310, 'Weekly Score Trend')

# Chart area - constrain to safe bounds
chart_x = 80
chart_y = 320
chart_w = PAGE_WIDTH - 200   # wider margin right for 4 bars
chart_h = 180

# Grid
c.setStrokeColor(colors.HexColor('#e5e7eb'))
c.setLineWidth(0.5)
for i in range(5):
    y_line = chart_y + (i * chart_h / 4)
    c.line(chart_x, y_line, chart_x + chart_w, y_line)

# Draw bars
bar_width = 60
bar_spacing = chart_w / (len(BATCH['weekly_trend']) + 1)   # +1 for Week 4 pending
max_score = 100

for i, (week, score) in enumerate(BATCH['weekly_trend']):
    bar_x = chart_x + i * bar_spacing + (bar_spacing - bar_width) / 2
    bar_height = (score / max_score) * chart_h

    # Bar with gradient effect (draw 3 shades of teal)
    c.setFillColor(TEAL)
    c.roundRect(bar_x, chart_y, bar_width, bar_height, 4, fill=1, stroke=0)

    # Score label on bar
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(bar_x + bar_width / 2, chart_y + bar_height - 22, str(score))

    # Week label below
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(bar_x + bar_width / 2, chart_y - 15, f'Week {week}')

# Week 4 pending
pending_x = chart_x + 3 * bar_spacing + (bar_spacing - bar_width) / 2
c.setStrokeColor(MID_GRAY)
c.setLineWidth(1)
c.setDash([3, 3])
c.rect(pending_x, chart_y, bar_width, chart_h, fill=0, stroke=1)
c.setDash([])

c.setFillColor(MID_GRAY)
c.setFont('Helvetica-Bold', 10)
c.drawCentredString(pending_x + bar_width / 2, chart_y + chart_h / 2, 'Week 4')
c.setFont('Helvetica', 9)
c.drawCentredString(pending_x + bar_width / 2, chart_y + chart_h / 2 - 15, 'pending')

# Callout below chart
draw_rounded_rect(c, 40, 130, PAGE_WIDTH - 80, 130, radius=10, fill_color=LIGHT_TEAL)

c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 14)
c.drawString(55, 225, f"+{BATCH['improvement']} point improvement in 3 weeks.")

c.setFont('Helvetica', 10)
c.drawString(55, 200, 'Your batch is on track for top-quartile performance in JEE 2027.')
c.drawString(55, 180, 'The weekly cadence is producing measurable gains — students')
c.drawString(55, 160, 'who engaged with all 3 assessments improved 3x faster.')
c.drawString(55, 140, 'Continue the momentum through Week 4.')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 2, TOTAL_PAGES)
c.showPage()

# ============ PAGE 3: TOP + STRUGGLING ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'INDIVIDUAL HIGHLIGHTS', 'Top performers and students needing attention')

# Two columns
col_w = (PAGE_WIDTH - 100) / 2

# Left - Top performers
c.setFillColor(GREEN)
c.setFont('Helvetica-Bold', 14)
c.drawString(40, PAGE_HEIGHT - 110, 'TOP 5 PERFORMERS')

y = PAGE_HEIGHT - 145
for i, (name, score, improvement) in enumerate(BATCH['top_performers'], 1):
    # Row card
    draw_rounded_rect(c, 40, y - 40, col_w - 10, 35, radius=6, fill_color=WHITE,
                      stroke_color=colors.HexColor('#d1fae5'))

    # Rank
    c.setFillColor(GREEN)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(50, y - 20, f'#{i}')

    # Name
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(75, y - 20, name)

    # Score
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(220, y - 20, f'{score}/100')

    # Improvement badge
    c.setFillColor(GREEN)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(285, y - 20, f'+{improvement}')

    y -= 42

# Right - Struggling
c.setFillColor(RED)
c.setFont('Helvetica-Bold', 14)
c.drawString(PAGE_WIDTH / 2 + 10, PAGE_HEIGHT - 110, '! NEEDS INTERVENTION')

y = PAGE_HEIGHT - 145
for name, current, previous in BATCH['struggling']:
    # Row card
    draw_rounded_rect(c, PAGE_WIDTH / 2 + 10, y - 40, col_w - 10, 35, radius=6,
                      fill_color=WHITE, stroke_color=colors.HexColor('#fecaca'))

    # Name
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(PAGE_WIDTH / 2 + 25, y - 20, name)

    # Score change
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica', 10)
    c.drawString(PAGE_WIDTH / 2 + 130, y - 20, f'{previous} → {current}')

    # Direction indicator
    color = RED if current < previous else GREEN
    c.setFillColor(color)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(PAGE_WIDTH / 2 + 220, y - 20, '↓' if current < previous else '↑')

    y -= 42

# Bottom callout
draw_rounded_rect(c, 40, 130, PAGE_WIDTH - 80, 90, radius=10, fill_color=colors.HexColor('#fef3c7'))

c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 11)
c.drawString(55, 195, '> RECOMMENDED INTERVENTION')

c.setFont('Helvetica', 10)
c.drawString(55, 175, '6 students need focused attention. Recommend:')
c.drawString(55, 158, 'small group tutoring, parent consultation, additional practice.')
c.drawString(55, 141, 'Expected impact: +8 to +15 points if started this week.')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 3, TOTAL_PAGES)
c.showPage()

# ============ PAGE 4: RECOMMENDATIONS ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'RECOMMENDED ACTIONS', 'Targeted interventions for each group')

# 3 columns
col_w = (PAGE_WIDTH - 100) / 3

columns = [
    ('TOP PERFORMERS', GREEN, [
        'Provide advanced problems',
        'Consider competitive mock tests',
        'Recommend peer tutoring role',
        'Parent update: positive trend',
    ]),
    ('MIDDLE PERFORMERS', YELLOW, [
        'Focus on weak topics',
        'Increase practice frequency',
        'Weekly progress check',
        'Consider topic sessions',
    ]),
    ('STRUGGLING STUDENTS', RED, [
        'Schedule 1-on-1 sessions',
        'Parent call this week',
        'Reduce scope, fundamentals',
        'Consider counseling referral',
    ]),
]

x = 40
col_y = PAGE_HEIGHT - 120
col_h = 280

for col_title, col_color, items in columns:
    # Card
    draw_rounded_rect(c, x, col_y - col_h, col_w - 10, col_h, radius=10, fill_color=WHITE,
                      stroke_color=colors.HexColor('#e5e7eb'))

    # Header
    c.setFillColor(col_color)
    c.rect(x, col_y - 35, col_w - 10, 35, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(x + (col_w - 10) / 2, col_y - 23, col_title)

    # Items
    item_y = col_y - 60
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica', 9)

    for item in items:
        # Bullet
        c.setFillColor(col_color)
        c.drawString(x + 12, item_y, '>')
        c.setFillColor(CHARCOAL)
        wrap_text(c, item, x + 22, item_y, col_w - 35, 'Helvetica', 9, 12, 2)
        item_y -= 32

    x += col_w + 5

# Bottom callout - ROI
callout_y = 130
draw_rounded_rect(c, 40, callout_y, PAGE_WIDTH - 80, 110, radius=10, fill_color=TEAL)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 12)
c.drawString(55, callout_y + 85, 'YOUR ROI THIS WEEK')

c.setFont('Helvetica', 10)
c.drawString(55, callout_y + 62, '> Time saved on manual tracking: ~8 hours')
c.drawString(55, callout_y + 45, '> Students flagged for intervention: 6')
c.drawString(55, callout_y + 28, '> Parents informed via portal: 96')
c.drawString(55, callout_y + 11, '> Certificates pending (score ≥ 85): 3')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 4, TOTAL_PAGES)

c.save()
print(f'Generated: {OUTPUT}')
print(f'Pages: {TOTAL_PAGES}')
print(f'Size: {os.path.getsize(OUTPUT)} bytes')
