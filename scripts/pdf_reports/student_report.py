"""Generate Student Readiness Report PDF (SAMPLE)."""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import white
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUTPUT = 'reports/Charvak-Student-Report-SAMPLE.pdf'

# Sample data (replace with real data when wiring to live system)
STUDENT = {
    'name': 'Priya Sharma (Sample)',
    'role': 'Data Analyst',
    'industry': 'FinTech',
    'level': 'Mid-Level',
    'score': 72,
    'benchmark': 65,
    'skills': [
        ('SQL', 28, 68),
        ('Python', 65, 60),
        ('Statistics', 42, 55),
        ('Communication', 51, 65),
        ('Business Acumen', 78, 70),
        ('Problem Solving', 72, 70),
    ],
}

c = canvas.Canvas(OUTPUT, pagesize=A4)

# ============ PAGE 1: COVER ============
c.setFillColor(TEAL)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

# Overlay shapes
c.setFillColor(DARK_TEAL)
c.circle(PAGE_WIDTH - 50, PAGE_HEIGHT - 50, 300, fill=1, stroke=0)
c.circle(-50, 100, 200, fill=1, stroke=0)

# Top label
c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 11)
c.drawString(40, PAGE_HEIGHT - 50, 'CHARVAK')
c.setFont('Helvetica', 10)
c.drawString(40, PAGE_HEIGHT - 65, 'CAREER READINESS REPORT')

# Main title
c.setFont('Helvetica-Bold', 42)
c.drawString(40, PAGE_HEIGHT - 160, 'Your Career')
c.drawString(40, PAGE_HEIGHT - 205, 'Readiness Score')

# Big score
c.setFont('Helvetica-Bold', 96)
c.drawString(40, PAGE_HEIGHT - 340, str(STUDENT['score']))
c.setFont('Helvetica', 24)
c.drawString(220, PAGE_HEIGHT - 340, '/100')

# Above benchmark label
c.setFillColor(colors.HexColor('#e0f0ec'))
c.setFont('Helvetica-Bold', 14)
c.drawString(40, PAGE_HEIGHT - 380, '▲ Above Benchmark')
c.setFont('Helvetica', 11)
c.drawString(40, PAGE_HEIGHT - 398, f"Industry Benchmark: {STUDENT['benchmark']}/100")

# Student info
c.setFillColor(WHITE)
c.setFont('Helvetica', 10)
c.drawString(40, 220, f"STUDENT: {STUDENT['name']}")
c.drawString(40, 205, f"ROLE TARGET: {STUDENT['role']}")
c.drawString(40, 190, f"INDUSTRY: {STUDENT['industry']}")
c.drawString(40, 175, f"LEVEL: {STUDENT['level']}")

# SAMPLE badge
draw_sample_badge(c)

# Footer
c.setFont('Helvetica', 8)
c.setFillColor(colors.HexColor('#e0f0ec'))
c.drawString(40, 60, 'Charvak IT Consulting Pvt Ltd  ·  https://www.charvakit.com')

c.showPage()

# ============ PAGE 2: SKILL BREAKDOWN ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

draw_header_bar(c, 'SKILL BREAKDOWN', 'Your score vs industry benchmark')

# Intro text
c.setFillColor(CHARCOAL)
c.setFont('Helvetica', 11)
c.drawString(40, PAGE_HEIGHT - 100, f"Your score: {STUDENT['score']}/100  ·  Industry benchmark: {STUDENT['benchmark']}/100")

# Skills table
y_start = PAGE_HEIGHT - 160
row_h = 55
for i, (skill, score, benchmark) in enumerate(STUDENT['skills']):
    y = y_start - (i * row_h)
    gap = score - benchmark

    # Skill name
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, skill)

    # Bar
    bar_x = 250
    bar_w = 200
    bar_h = 14
    draw_horizontal_bar(c, bar_x, y - 4, bar_w, bar_h, score / 100,
                        fill_color=TEAL if gap >= 0 else RED)

    # Score
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(bar_x + bar_w + 15, y, f'{score}')

    # Benchmark
    c.setFillColor(MID_GRAY)
    c.setFont('Helvetica', 9)
    c.drawString(bar_x + bar_w + 45, y, f'vs {benchmark}')

    # Gap badge
    gap_text = f'{gap:+d}'
    c.setFillColor(GREEN if gap >= 0 else RED)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(bar_x + bar_w + 90, y, gap_text)

# Key insight callout
callout_y = 200
draw_rounded_rect(c, 40, callout_y, PAGE_WIDTH - 80, 100, radius=8, fill_color=colors.HexColor('#fef3c7'))

c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 12)
c.drawString(55, callout_y + 78, 'KEY INSIGHT')

c.setFont('Helvetica', 10)
c.drawString(55, callout_y + 58, 'Your biggest opportunity is SQL (-40 points).')
c.drawString(55, callout_y + 42, 'Your strongest area is Business Acumen (+8 points).')
c.drawString(55, callout_y + 26, 'Focusing on SQL first will deliver the highest impact.')

# SAMPLE badge
draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 2, 4)
c.showPage()

# ============ PAGE 3: LEARNING PATH ============
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

draw_header_bar(c, 'YOUR LEARNING PATH', 'Based on your skill gaps')

c.setFillColor(CHARCOAL)
c.setFont('Helvetica', 11)
c.drawString(40, PAGE_HEIGHT - 100, 'Follow this plan for 4-6 weeks and see measurable improvement.')

# Priority cards
cards = [
    ('PRIORITY 1 - HIGHEST IMPACT', 'SQL Mastery', 28, 68, 40,
     'Course: SQL for Data Analysts', 'Duration: 4 weeks x 5 hrs/week', RED),
    ('PRIORITY 2 - MEDIUM IMPACT', 'Communication', 51, 65, 14,
     'Course: Business Communication', 'Duration: 2 weeks x 3 hrs/week', YELLOW),
    ('PRIORITY 3 - MAINTAIN STRENGTH', 'Business Acumen', 78, 70, -8,
     'Status: Above benchmark', 'Optional: Advanced topics', GREEN),
]

y_pos = PAGE_HEIGHT - 180
for label, title, current, target, gap, line1, line2, color in cards:
    draw_card(c, 40, y_pos - 100, PAGE_WIDTH - 80, 100, left_color=color)

    c.setFillColor(color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(55, y_pos - 20, label)

    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(55, y_pos - 42, title)

    c.setFont('Helvetica', 10)
    c.drawString(55, y_pos - 58, f'Current: {current}/100  ·  Target: {target}/100  ·  Gap: {gap}')

    c.setFont('Helvetica', 9)
    c.setFillColor(MID_GRAY)
    c.drawString(55, y_pos - 75, line1)
    c.drawString(55, y_pos - 88, line2)

    y_pos -= 115

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 3, 4)
c.showPage()

# ============ PAGE 4: CERTIFICATE & NEXT STEPS ============
# Top half teal
c.setFillColor(TEAL)
c.rect(0, PAGE_HEIGHT / 2, PAGE_WIDTH, PAGE_HEIGHT / 2, fill=1, stroke=0)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 22)
c.drawString(40, PAGE_HEIGHT - 70, 'YOU QUALIFIED!')

c.setFont('Helvetica', 12)
c.drawString(40, PAGE_HEIGHT - 95, 'Eligible for Verified Certificate')
c.drawString(40, PAGE_HEIGHT - 115, f"Tier: EXPERT (score {STUDENT['score']}, benchmark {STUDENT['benchmark']})")

# Certificate preview card
cert_y = PAGE_HEIGHT / 2 + 40
cert_h = 200
draw_rounded_rect(c, 100, cert_y, PAGE_WIDTH - 200, cert_h, radius=10, fill_color=WHITE)

c.setFillColor(TEAL)
c.setFont('Helvetica-Bold', 14)
c.drawCentredString(PAGE_WIDTH / 2, cert_y + cert_h - 30, 'CHARVAK')

c.setFillColor(CHARCOAL)
c.setFont('Helvetica', 9)
c.drawCentredString(PAGE_WIDTH / 2, cert_y + cert_h - 45, 'CERTIFICATE OF EXPERTISE')

c.setFont('Helvetica-Bold', 14)
c.drawCentredString(PAGE_WIDTH / 2, cert_y + cert_h - 75, STUDENT['name'])

c.setFont('Helvetica', 9)
c.drawCentredString(PAGE_WIDTH / 2, cert_y + cert_h - 95, 'has demonstrated verified expertise in')
c.setFont('Helvetica-Bold', 11)
c.drawCentredString(PAGE_WIDTH / 2, cert_y + cert_h - 112,
                    f"{STUDENT['role']} · {STUDENT['industry']} · {STUDENT['level']}")

c.setFont('Helvetica', 10)
c.setFillColor(TEAL)
c.drawCentredString(PAGE_WIDTH / 2, cert_y + 20, f"Score: {STUDENT['score']}/100  ·  Tier: Expert")

# Bottom half cream
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT / 2, fill=1, stroke=0)

c.setFillColor(CHARCOAL)
c.setFont('Helvetica-Bold', 16)
c.drawString(40, PAGE_HEIGHT / 2 - 40, "WHAT'S NEXT")

next_steps = [
    'Retake in 30 days to track improvement',
    'Browse jobs matched to your certificate',
    'Share your certificate with recruiters',
    'Questions? hr@charvakit.com',
]
y = PAGE_HEIGHT / 2 - 80
for step in next_steps:
    c.setFillColor(TEAL)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, '→')
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica', 11)
    c.drawString(60, y, step)
    y -= 28

draw_sample_badge(c)
draw_footer(c)
draw_page_number(c, 4, 4)

c.save()
print(f'Generated: {OUTPUT}')
print(f'Pages: 4')
