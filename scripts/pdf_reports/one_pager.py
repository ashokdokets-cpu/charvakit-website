"""Generate Comparison One-Pager PDF (SAMPLE) - 1 page landscape."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

# Override page size for landscape
LAND_W, LAND_H = landscape(A4)  # 842 x 595

OUTPUT = 'reports/Charvak-One-Pager-SAMPLE.pdf'

c = canvas.Canvas(OUTPUT, pagesize=(LAND_W, LAND_H))

# ============ HEADER BAR ============
# Fixed: taller bar, explicit save/restore, larger margin, white text guarantee
c.saveState()
c.setFillColor(TEAL)
c.rect(0, LAND_H - 90, LAND_W, 90, fill=1, stroke=0)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 20)
c.drawString(40, LAND_H - 42, 'BEFORE CHARVAK  vs  WITH CHARVAK')

c.setFont('Helvetica', 10)
c.setFillColor(colors.HexColor('#e0f0ec'))
c.drawString(40, LAND_H - 65, 'Why leading institutions are replacing their assessment stack')
c.restoreState()

# ============ TWO COLUMN COMPARISON ============
col_y = 300
col_h = 220
col_w = (LAND_W - 120) / 2

# LEFT COLUMN - "Without Charvak"
draw_rounded_rect(c, 40, col_y, col_w, col_h, radius=10,
                  fill_color=colors.HexColor('#fee2e2'),
                  stroke_color=colors.HexColor('#fecaca'))

# Header
c.setFillColor(RED)
c.rect(40, col_y + col_h - 35, col_w, 35, fill=1, stroke=0)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 14)
c.drawCentredString(40 + col_w / 2, col_y + col_h - 23, 'WITHOUT CHARVAK')

# Items
without_items = [
    'Students find gaps post-graduation',
    'Placement quality unknown',
    'Employer trust requires interviews',
    'Skill gaps discovered via rejections',
    'No verified proof of readiness',
    'Parents rely on trust, not data',
    'Batch comparison is guesswork',
]

c.setFillColor(CHARCOAL)
c.setFont('Helvetica', 10)
y = col_y + col_h - 60
for item in without_items:
    c.setFillColor(RED)
    c.drawString(55, y, '✗')
    c.setFillColor(CHARCOAL)
    c.drawString(70, y, item)
    y -= 22

# RIGHT COLUMN - "With Charvak"
draw_rounded_rect(c, 60 + col_w, col_y, col_w, col_h, radius=10,
                  fill_color=colors.HexColor('#d1fae5'),
                  stroke_color=colors.HexColor('#a7f3d0'))

# Header
c.setFillColor(GREEN)
c.rect(60 + col_w, col_y + col_h - 35, col_w, 35, fill=1, stroke=0)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 14)
c.drawCentredString(60 + col_w + col_w / 2, col_y + col_h - 23, 'WITH CHARVAK')

# Items
with_items = [
    'Diagnose gaps before graduation',
    'Aggregate readiness dashboard',
    'Verified certs employers trust',
    'AI-generated fix paths',
    'Digitally signed certificates',
    'Parent-shareable progress reports',
    'Automated batch comparisons',
]

c.setFillColor(CHARCOAL)
c.setFont('Helvetica', 10)
y = col_y + col_h - 60
for item in with_items:
    c.setFillColor(GREEN)
    c.drawString(60 + col_w + 15, y, '✓')
    c.setFillColor(CHARCOAL)
    c.drawString(60 + col_w + 30, y, item)
    y -= 22

# ============ 3 COLUMN BENEFITS (middle) ============
# Fixed: full-width cards with proper gaps to prevent overlap
benefit_y = 150
benefit_h = 145
benefit_gap = 15
benefit_w = (LAND_W - 80 - (benefit_gap * 2)) / 3   # ~245px per card

benefits = [
    ('SAVE TIME', '10+ hrs/week', 'Automated tracking saves placement cell hours on manual reports', TEAL),
    ('REDUCE COST', '6 weeks vs 6 months', 'Cut rejection cycles. Students get placed faster, employers save hiring time', YELLOW),
    ('IMPROVE OUTCOMES', '60% above benchmark', '15 points higher than the 45% national average', GREEN),
]

x = 40
for title, big_value, desc, color in benefits:
    # Card full width
    card_w = benefit_w

    # Card background
    draw_rounded_rect(c, x, benefit_y, card_w, benefit_h, radius=10,
                      fill_color=WHITE,
                      stroke_color=colors.HexColor('#e5e7eb'))

    # Color accent bar top (inside card, respecting border)
    c.setFillColor(color)
    c.rect(x + 10, benefit_y + benefit_h - 10, card_w - 20, 8, fill=1, stroke=0)

    # Title
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(x + 12, benefit_y + benefit_h - 32, title)

    # Big value (auto-size to fit card width)
    from reportlab.pdfbase.pdfmetrics import stringWidth
    val_size = 18
    while stringWidth(big_value, 'Helvetica-Bold', val_size) > (card_w - 24) and val_size > 12:
        val_size -= 1

    c.setFillColor(color)
    c.setFont('Helvetica-Bold', val_size)
    c.drawString(x + 12, benefit_y + benefit_h - 62, big_value)

    # Description wrapped within card
    c.setFillColor(MID_GRAY)
    wrap_text(c, desc, x + 12, benefit_y + benefit_h - 82, card_w - 24,
              'Helvetica', 9, 12, 4)

    x += card_w + benefit_gap

# ============ BOTTOM CTA ============
cta_y = 20
cta_h = 110

draw_rounded_rect(c, 40, cta_y, LAND_W - 80, cta_h, radius=12, fill_color=DARK_TEAL)

c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 20)
c.drawString(60, cta_y + 78, 'FREE 4-WEEK PILOT')

c.setFont('Helvetica', 11)
c.setFillColor(colors.HexColor('#b8e0d6'))
c.drawString(60, cta_y + 55, '100-500 students  ·  Zero cost  ·  Zero commitment  ·  Weekly reports')

c.setFont('Helvetica-Bold', 12)
c.setFillColor(WHITE)
c.drawString(60, cta_y + 30, 'Contact:  hr@charvakit.com')

c.setFont('Helvetica', 10)
c.setFillColor(colors.HexColor('#b8e0d6'))
c.drawString(60, cta_y + 12, '+91 799 7871 701  ·  https://www.charvakit.com')

# Bottom right - brand
c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 20)
c.drawRightString(LAND_W - 60, cta_y + 78, 'Charvak')
c.setFont('Helvetica', 8)
c.setFillColor(colors.HexColor('#b8e0d6'))
c.drawRightString(LAND_W - 60, cta_y + 60, 'Career Readiness Infrastructure')
c.drawRightString(LAND_W - 60, cta_y + 48, 'for Higher Education')

# Sample badge (custom position for landscape)
c.setFillColor(RED)
c.roundRect(LAND_W - 100, LAND_H - 55, 75, 24, 4, fill=1, stroke=0)
c.setFillColor(WHITE)
c.setFont('Helvetica-Bold', 10)
c.drawCentredString(LAND_W - 62, LAND_H - 42, 'SAMPLE')

c.save()
print(f'Generated: {OUTPUT}')
print(f'Pages: 1 (landscape)')
print(f'Size: {os.path.getsize(OUTPUT)} bytes')
