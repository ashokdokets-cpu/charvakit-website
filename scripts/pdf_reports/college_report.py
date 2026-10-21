"""Generate College Placement Report PDF (SAMPLE) - 6 pages."""
from reportlab.pdfgen import canvas
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from datetime import datetime

OUTPUT = 'reports/Charvak-College-Report-SAMPLE.pdf'

COLLEGE = {
    'name': 'Sample College of Engineering',
    'total_students': 247,
    'assessed': 231,
    'above_benchmark': 138,
    'below_benchmark': 93,
    'departments': [
        ('CSE', 62, 48, 14, 78),
        ('IT', 48, 34, 14, 74),
        ('ECE', 51, 29, 22, 68),
        ('Mechanical', 42, 20, 22, 62),
        ('Civil', 28, 7, 21, 55),
    ],
    'gaps': [
        ('Communication', 178, 77, RED),
        ('SQL', 156, 68, RED),
        ('System Design', 121, 52, YELLOW),
        ('Debugging', 98, 42, YELLOW),
    ],
    'roles': [
        ('Software Engineer', 48, 71, 'up'),
        ('Data Analyst', 32, 68, 'at'),
        ('Product Manager', 18, 74, 'up'),
        ('Business Analyst', 45, 69, 'at'),
        ('Sales Engineer', 24, 62, 'at'),
        ('Teaching Fellow', 12, 78, 'up'),
        ('Marketing Manager', 22, 65, 'at'),
        ('Finance Analyst', 30, 63, 'at'),
    ],
}

TOTAL_PAGES = 6
c = canvas.Canvas(OUTPUT, pagesize=A4)

# ============ PAGE 1: COVER ============
c.setFillColor(DARK_TEAL)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

c.setFillColor(colors.HexColor('#2a8a75'))
c.circle(PAGE_WIDTH + 100, PAGE_HEIGHT + 50, 400, fill=1, stroke=0)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 11)
c.drawString(40, PAGE_HEIGHT - 50, 'CSE DEPARTMENT PILOT REPORT')

c.setFont('Helvetica-Bold', 42)
c.drawString(40, PAGE_HEIGHT - 180, 'Placement Readiness')
c.drawString(40, PAGE_HEIGHT - 225, 'Report')

c.setFont('Helvetica', 16)
c.drawString(40, PAGE_HEIGHT - 265, COLLEGE['name'])
c.drawString(40, PAGE_HEIGHT - 290, 'Week 3 of 4-Week Pilot')

# Stats card
stats_y = 320
draw_rounded_rect(c, 40, stats_y, PAGE_WIDTH - 80, 180, radius=10, fill_color=WHITE)

stats = [
    ('Total Students', str(COLLEGE['total_students'])),
    ('Assessed', f"{COLLEGE['assessed']} (93%)"),
    ('Above Benchmark', f"{COLLEGE['above_benchmark']} (60%)"),
    ('Below Benchmark', f"{COLLEGE['below_benchmark']} (40%)"),
]
for i, (label, value) in enumerate(stats):
    col = i % 2
    row = i // 2
    x = 60 + col * 250
    y = stats_y + 140 - row * 70
    c.setFillColor(MID_GRAY)
    c.setFont('Helvetica', 9)
    c.drawString(x, y + 18, label)
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 18)
    c.drawString(x, y, str(value))

c.setFillColor(colors.HexColor('#b8e0d6'))
c.setFont('Helvetica', 10)
c.drawString(40, 120, f"Generated: {datetime.now().strftime('%B %d, %Y')}")
c.drawString(40, 105, 'Prepared by Charvak IT Consulting')
c.drawString(40, 90, 'https://www.charvakit.com  ·  hr@charvakit.com')

draw_sample_badge(c)
c.showPage()

# ============ PAGE 2: EXECUTIVE SUMMARY ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'EXECUTIVE SUMMARY', 'Sample College of Engineering · Week 3 Pilot Report')

# Left column - narrative
c.setFillColor(CHARCOAL)
c.setFont('Helvetica', 10)
lines = [
    f"The 4-week pilot with {COLLEGE['name']} assessed",
    f"{COLLEGE['assessed']} students across 5 departments.",
    "",
    "60% of students are at or above industry readiness",
    "benchmark — 15 points above the national average of 45%.",
    "",
    "Biggest gaps:",
    "  - Communication: 178 students below benchmark",
    "  - SQL: 156 students below benchmark",
    "  - System Design: 121 students below benchmark",
    "",
    "Top department: CSE (avg 78/100)",
    "Needs attention: Civil (avg 55/100)",
    "",
    "Recommended for Week 4:",
    "  1. Communication workshop (178 students)",
    "  2. SQL bridge course (156 students)",
    "  3. System Design seminar (121 students)",
]
y = PAGE_HEIGHT - 100
for line in lines:
    c.drawString(40, y, line)
    y -= 15

# Right column - 4 stat cards
card_x = PAGE_WIDTH - 195
cards = [
    ('60%', 'Above Benchmark', '+15% vs national'),
    ('231', 'Students Assessed', '93% completion'),
    ('40', 'Certificates Issued', 'Score ≥ 85'),
    ('5', 'Departments', '3 above benchmark'),
]
card_y = PAGE_HEIGHT - 90
for value, label, sub in cards:
    draw_stat_card(c, card_x, card_y - 70, 160, 65, value, label, sub)
    card_y -= 85

# Sample note
draw_rounded_rect(c, 40, 60, PAGE_WIDTH - 80, 55, radius=8, fill_color=colors.HexColor('#fef3c7'))
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 10)
c.drawString(55, 92, '⚠ SAMPLE REPORT')
c.setFont('Helvetica', 9)
c.drawString(55, 76, 'Numbers shown are fictional for demonstration. Your report uses your actual data.')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 2, TOTAL_PAGES)
c.showPage()

# ============ PAGE 3: DEPARTMENT BREAKDOWN ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'READINESS BY DEPARTMENT', 'Comparing each department to the national average of 65')

y_start = PAGE_HEIGHT - 120
for i, (dept, students, above, below, avg) in enumerate(COLLEGE['departments']):
    y = y_start - (i * 60)

    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, dept)

    fill_color = GREEN if avg >= 65 else YELLOW if avg >= 60 else RED
    draw_horizontal_bar(c, 160, y - 4, 320, 14, avg / 100, fill_color=fill_color)

    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(495, y, f'{avg}')

    c.setFillColor(MID_GRAY)
    c.setFont('Helvetica', 8)
    c.drawString(160, y - 20, f'{students} students · {above} above · {below} below')

# National avg reference
n_avg_y = y_start - (len(COLLEGE['departments']) * 60) - 5
c.setStrokeColor(MID_GRAY)
c.setLineWidth(1)
c.setDash([3, 3])
c.line(160, n_avg_y, 480, n_avg_y)
c.setDash([])

c.setFillColor(MID_GRAY)
c.setFont('Helvetica', 9)
c.drawString(40, n_avg_y - 5, 'National Avg: 65')

# Focus callout
callout_y = 120
draw_rounded_rect(c, 40, callout_y, PAGE_WIDTH - 80, 70, radius=8, fill_color=colors.HexColor('#fef3c7'))
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 11)
c.drawString(55, callout_y + 50, '⚠ FOCUS AREA')
c.setFont('Helvetica', 10)
c.drawString(55, callout_y + 30, 'Civil department needs intervention.')
c.drawString(55, callout_y + 15, '21 of 28 students are below benchmark.')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 3, TOTAL_PAGES)
c.showPage()

# ============ PAGE 4: SKILL GAPS ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'MOST COMMON SKILL GAPS', 'Across the entire batch of 231 assessed students')

# 2x2 grid of gap cards
card_w = (PAGE_WIDTH - 100) / 2
card_h = 150
positions = [
    (40, PAGE_HEIGHT - 180),
    (60 + card_w, PAGE_HEIGHT - 180),
    (40, PAGE_HEIGHT - 350),
    (60 + card_w, PAGE_HEIGHT - 350),
]

for (skill, count, pct, color), (x, y) in zip(COLLEGE['gaps'], positions):
    draw_card(c, x, y - card_h + 20, card_w, card_h, left_color=color)

    c.setFillColor(color)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(x + 20, y, skill)

    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 32)
    c.drawString(x + 20, y - 40, str(count))

    c.setFont('Helvetica', 11)
    c.setFillColor(MID_GRAY)
    c.drawString(x + 20, y - 60, 'students below benchmark')
    c.drawString(x + 20, y - 78, f'({pct}% of batch)')

# Bottom callout
c.setFillColor(CHARCOAL)
c.setFont('Helvetica', 10)
c.drawString(40, 110, 'Each gap represents a targeted intervention opportunity in Week 4.')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 4, TOTAL_PAGES)
c.showPage()

# ============ PAGE 5: ROLE READINESS ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'READINESS BY TARGET ROLE', 'How students targeting specific roles are performing')

y_start = PAGE_HEIGHT - 130
row_h = 40
for i, (role, students, avg, status) in enumerate(COLLEGE['roles']):
    y = y_start - (i * row_h)

    if i % 2 == 0:
        c.setFillColor(WHITE)
        c.rect(40, y - 10, PAGE_WIDTH - 80, 35, fill=1, stroke=0)

    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica', 11)
    c.drawString(55, y, role)

    c.setFont('Helvetica', 10)
    c.setFillColor(MID_GRAY)
    c.drawString(280, y, f'{students} students')

    # Score bar
    bar_color = GREEN if avg >= 65 else YELLOW if avg >= 60 else RED
    draw_horizontal_bar(c, 380, y - 2, 100, 10, avg / 100, fill_color=bar_color)

    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(495, y, f'{avg}')

# Legend
legend_y = 130
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 10)
c.drawString(40, legend_y, 'Legend:')
c.setFillColor(GREEN)
c.setFont('Helvetica', 9)
c.drawString(105, legend_y, '✓ Above benchmark (≥65)')
c.setFillColor(YELLOW)
c.drawString(255, legend_y, '→ At benchmark (60-64)')
c.setFillColor(RED)
c.drawString(395, legend_y, '⚠ Below benchmark (<60)')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 5, TOTAL_PAGES)
c.showPage()

# ============ PAGE 6: NEXT STEPS ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header_bar(c, 'RECOMMENDED NEXT STEPS', 'What to prioritize in Week 4 and beyond')

# Two column headers
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 14)
c.drawString(40, PAGE_HEIGHT - 100, 'THIS WEEK (Week 4)')
c.drawString(PAGE_WIDTH / 2 + 20, PAGE_HEIGHT - 100, 'NEXT 30 DAYS')

# Left column - this week
this_week = [
    ('☐', 'Launch Communication Workshop', '178 students · 4 sessions'),
    ('☐', 'Start SQL Bridge Course', '156 students · Self-paced'),
    ('☐', 'Review Certificate Eligibility', '40 students currently eligible'),
    ('☐', 'Weekly Progress Report', 'Due: [date + 7 days]'),
]

y = PAGE_HEIGHT - 140
for checkbox, title, detail in this_week:
    c.setFillColor(TEAL)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, checkbox)
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(58, y, title)
    c.setFont('Helvetica', 9)
    c.setFillColor(MID_GRAY)
    c.drawString(58, y - 14, detail)
    y -= 40

# Right column - next 30 days
next_30 = [
    ('Phase 1', 'Continue skill building', '4 weeks, self-paced'),
    ('Phase 2', 'Mid-program assessment', 'Week 4 retake'),
    ('Phase 3', 'Track placement outcomes', 'Week 5-8'),
    ('Phase 4', 'Decide on year-long partnership', 'Review pilot outcomes'),
]

y = PAGE_HEIGHT - 140
for phase, title, detail in next_30:
    c.setFillColor(TEAL)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(PAGE_WIDTH / 2 + 20, y + 5, phase.upper())
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(PAGE_WIDTH / 2 + 20, y - 10, title)
    c.setFont('Helvetica', 9)
    c.setFillColor(MID_GRAY)
    c.drawString(PAGE_WIDTH / 2 + 20, y - 24, detail)
    y -= 40

# Bottom callout - outcomes
callout_y = 130
draw_rounded_rect(c, 40, callout_y, PAGE_WIDTH - 80, 90, radius=10, fill_color=TEAL)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 12)
c.drawString(55, callout_y + 70, 'WHAT THIS PILOT PROVES')

c.setFont('Helvetica', 10)
c.drawString(55, callout_y + 50, '✓ 93% student participation — high engagement')
c.drawString(55, callout_y + 34, '✓ 40 verified certificates issued — trust-building')
c.drawString(55, callout_y + 18, '✓ 60% above benchmark — better than national avg')
c.drawString(55, callout_y + 2, '✓ Clear skill gaps identified for targeted intervention')

# Call to action at bottom
c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 11)
c.drawCentredString(PAGE_WIDTH / 2, 90, 'Ready for a year-long partnership?')
c.setFont('Helvetica', 10)
c.setFillColor(TEAL)
c.drawCentredString(PAGE_WIDTH / 2, 75, 'Contact: hr@charvakit.com')

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 6, TOTAL_PAGES)

c.save()
print(f'Generated: {OUTPUT}')
print(f'Pages: {TOTAL_PAGES}')
print(f'Size: {os.path.getsize(OUTPUT)} bytes')
