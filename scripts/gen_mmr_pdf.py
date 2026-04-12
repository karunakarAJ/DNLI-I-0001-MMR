
"""
Convert I-0001-Medical-Monitoring-Report-2026FEB25-AI.html to PDF
using ReportLab Platypus.
"""
import re, base64, io, sys
from bs4 import BeautifulSoup, NavigableString, Tag

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HTML_PATH = '/sessions/fervent-busy-euler/mnt/MMR/I-0001-Medical-Monitoring-Report-2026FEB25-AI.html'
PDF_PATH  = '/sessions/fervent-busy-euler/mnt/MMR/I-0001-Medical-Monitoring-Report-2026FEB25-AI.pdf'

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm

print("Parsing HTML...")
with open(HTML_PATH, encoding='utf-8') as f:
    raw = f.read()
soup = BeautifulSoup(raw, 'lxml')

# ─── STYLES ──────────────────────────────────────────────────────────────────
SS = getSampleStyleSheet()

def s(name, **kw):
    base = SS[name] if name in SS else SS['Normal']
    return ParagraphStyle(name + '_custom_' + str(id(kw)), parent=base, **kw)

STYLES = {
    'cover_title':  s('Title',    fontSize=22, leading=28, textColor=colors.HexColor('#1F4E79'),
                      spaceAfter=12, alignment=TA_CENTER),
    'cover_sub':    s('Normal',   fontSize=13, leading=17, textColor=colors.HexColor('#2E75B6'),
                      spaceAfter=6,  alignment=TA_CENTER),
    'cover_meta':   s('Normal',   fontSize=9,  leading=13, textColor=colors.grey,
                      alignment=TA_CENTER),
    'diff_banner':  s('Normal',   fontSize=9,  leading=13,
                      backColor=colors.HexColor('#FFF9C4'),
                      textColor=colors.HexColor('#7B4F00'),
                      borderPadding=6, spaceAfter=8),
    'h2':           s('Heading2', fontSize=13, leading=17, textColor=colors.HexColor('#1F4E79'),
                      spaceBefore=14, spaceAfter=4,
                      borderPadding=(0,0,2,0)),
    'h3':           s('Heading3', fontSize=11, leading=15, textColor=colors.HexColor('#2E75B6'),
                      spaceBefore=10, spaceAfter=3),
    'h4':           s('Heading4', fontSize=10, leading=14, textColor=colors.HexColor('#375623'),
                      spaceBefore=8,  spaceAfter=2),
    'body':         s('Normal',   fontSize=8.5, leading=12, spaceAfter=4),
    'body_small':   s('Normal',   fontSize=7.5, leading=11, spaceAfter=3),
    'callout':      s('Normal',   fontSize=8.5, leading=12,
                      backColor=colors.HexColor('#FFF3CD'),
                      textColor=colors.HexColor('#664D03'),
                      borderPadding=5, spaceAfter=6),
    'callout_red':  s('Normal',   fontSize=8.5, leading=12,
                      backColor=colors.HexColor('#FDECEA'),
                      textColor=colors.HexColor('#721C24'),
                      borderPadding=5, spaceAfter=6),
    'fig_caption':  s('Normal',   fontSize=7.5, leading=11,
                      textColor=colors.grey, alignment=TA_CENTER,
                      spaceAfter=8, spaceBefore=2),
    'table_header': s('Normal',   fontSize=7.5, leading=10, fontName='Helvetica-Bold',
                      alignment=TA_CENTER),
    'table_cell':   s('Normal',   fontSize=7.5, leading=10),
    'footer':       s('Normal',   fontSize=7, textColor=colors.grey, alignment=TA_CENTER),
}

# table alternating row colors
ROW_EVEN = colors.HexColor('#EBF5FF')
ROW_ODD  = colors.white
HDR_BG   = colors.HexColor('#1F4E79')
HDR_FG   = colors.white

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def clean(text):
    """Sanitize text for ReportLab Paragraph (escape < > &)."""
    if text is None:
        return ''
    text = str(text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'<[^>]+>', ' ', text)   # strip any remaining tags
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def html_para(html_str, style):
    """Build a Paragraph from an HTML fragment, handling <strong><em> etc."""
    # convert common inline tags to ReportLab markup
    text = str(html_str)
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'<b>\1</b>', text, flags=re.S)
    text = re.sub(r'<em[^>]*>(.*?)</em>',         r'<i>\1</i>', text, flags=re.S)
    text = re.sub(r'<b[^>]*>(.*?)</b>',            r'<b>\1</b>', text, flags=re.S)
    text = re.sub(r'<i[^>]*>(.*?)</i>',            r'<i>\1</i>', text, flags=re.S)
    text = re.sub(r'<br\s*/?>', ' ', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&', '&amp;').replace('\u2019',"'").replace('\u2018',"'")
    text = text.replace('\u2013', '-').replace('\u2014', '--')
    text = text.replace('\u00d7', 'x').replace('\u2265', '>=').replace('\u2264', '<=')
    text = text.replace('\u00b0', 'deg').replace('\u2082', '2').replace('\u2084', '4')
    text = text.replace('\u207f', 'n').replace('\u00b9', '1').replace('\u00b2', '2')
    text = text.replace('\u2190', '<-').replace('\u2192', '->').replace('\u2193', 'v')
    text = text.replace('\u2605', '*').replace('\u26a0', '!')
    text = text.replace('\u00e9', 'e').replace('\u00ea', 'e').replace('\u00eb', 'e')
    # Remove any unbalanced tags or leftovers
    text = re.sub(r'\s+', ' ', text).strip()
    try:
        return Paragraph(text, style)
    except Exception:
        return Paragraph(clean(text), style)

def b64_to_image(b64_data, max_w, max_h):
    """Convert base64 PNG to ReportLab Image."""
    try:
        img_bytes = base64.b64decode(b64_data)
        buf = io.BytesIO(img_bytes)
        img = Image(buf)
        # scale to fit page width, preserving aspect
        iw, ih = img.drawWidth, img.drawHeight
        ratio = ih / iw if iw > 0 else 1
        w = min(max_w, iw)
        h = w * ratio
        if h > max_h:
            h = max_h
            w = h / ratio
        img.drawWidth  = w
        img.drawHeight = h
        return img
    except Exception as e:
        return Paragraph(f'[Figure — image load error: {e}]', STYLES['body_small'])

def build_html_table(tbl_tag):
    """Convert an HTML <table> to a ReportLab Table."""
    rows_data = []
    col_spans = {}   # track span positions
    html_rows = tbl_tag.find_all('tr')

    for ri, tr in enumerate(html_rows):
        cells = tr.find_all(['th', 'td'])
        row = []
        ci = 0
        for cell in cells:
            while (ri, ci) in col_spans:
                row.append('')
                ci += 1
            txt = clean(cell.get_text(separator=' ', strip=True))
            is_header = (cell.name == 'th' or
                        'header' in cell.get('class', []) or
                        ri == 0)
            style = STYLES['table_header'] if is_header else STYLES['table_cell']
            row.append(Paragraph(txt, style))
            
            colspan = int(cell.get('colspan', 1))
            rowspan = int(cell.get('rowspan', 1))
            for rs in range(1, rowspan):
                for cs in range(colspan):
                    col_spans[(ri + rs, ci + cs)] = True
            for cs in range(1, colspan):
                row.append('')
            ci += colspan
        rows_data.append(row)

    if not rows_data:
        return None

    # Determine column count
    ncols = max(len(r) for r in rows_data)
    # Pad rows
    for r in rows_data:
        while len(r) < ncols:
            r.append('')

    avail_w = PAGE_W - 2 * MARGIN
    col_w = avail_w / ncols

    tbl = Table(rows_data, colWidths=[col_w] * ncols, repeatRows=1)

    style_cmds = [
        ('BACKGROUND',  (0,0), (-1,0), HDR_BG),
        ('TEXTCOLOR',   (0,0), (-1,0), HDR_FG),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 7.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [ROW_ODD, ROW_EVEN]),
        ('GRID',        (0,0), (-1,-1), 0.3, colors.HexColor('#CCCCCC')),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING',(0,0), (-1,-1), 4),
        ('TOPPADDING',  (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
        ('WORDWRAP',    (0,0), (-1,-1), True),
    ]
    tbl.setStyle(TableStyle(style_cmds))
    return tbl

# ─── PAGE TEMPLATE (header + footer) ─────────────────────────────────────────
class MMRDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.page_num = 0

    def handle_pageBegin(self):
        super().handle_pageBegin()
        self.page_num += 1

    def afterPage(self):
        canvas = self.canv
        canvas.saveState()
        # Header bar
        canvas.setFillColor(colors.HexColor('#1F4E79'))
        canvas.rect(MARGIN, PAGE_H - MARGIN * 0.65, PAGE_W - 2*MARGIN, 1, fill=1, stroke=0)
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.grey)
        canvas.drawString(MARGIN, PAGE_H - MARGIN * 0.9,
                         'DNLI-I-0001 | DNL126 | Medical Monitoring Report | FEB 2026 | CONFIDENTIAL')
        # Footer
        canvas.setFillColor(colors.HexColor('#1F4E79'))
        canvas.rect(MARGIN, MARGIN * 0.35, PAGE_W - 2*MARGIN, 1, fill=1, stroke=0)
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.grey)
        canvas.drawString(MARGIN, MARGIN * 0.15, 'Denali Therapeutics | AI-Generated | For Review Only')
        canvas.drawRightString(PAGE_W - MARGIN, MARGIN * 0.15, f'Page {self.page_num}')
        canvas.restoreState()

# ─── CONTENT BUILDER ─────────────────────────────────────────────────────────
print("Building PDF content...")
story = []
avail_w = PAGE_W - 2 * MARGIN
avail_h = PAGE_H - 2 * MARGIN

# ── COVER PAGE ──────────────────────────────────────────────────────────────
story.append(Spacer(1, 2.5*cm))
story.append(Paragraph('MEDICAL MONITORING REPORT', STYLES['cover_title']))
story.append(Paragraph('DNL126  [DNLI-I-0001]', STYLES['cover_sub']))
story.append(Spacer(1, 0.8*cm))
story.append(HRFlowable(width=avail_w, thickness=2, color=colors.HexColor('#1F4E79')))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph('[FEB 2026]', STYLES['cover_sub']))
story.append(Spacer(1, 0.6*cm))
meta_lines = [
    'EDC Data Cut:  2026-02-25',
    'Safety Lab (MLM):  2026-02-13',
    'ADA (Bioagilytix):  2026-02-20',
    'IRT/PROD:  2026-02-01',
    'Biomarkers (Frontage):  2025-07-18',
    'Clinical Outcomes (WCG):  2026-02-10',
]
for ml in meta_lines:
    story.append(Paragraph(ml, STYLES['cover_meta']))
story.append(Spacer(1, 1.0*cm))
story.append(HRFlowable(width=avail_w, thickness=1, color=colors.HexColor('#2E75B6')))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph('Confidential — For Internal Review Only', STYLES['cover_meta']))
story.append(Paragraph('AI-Generated from raw data package | Denali Therapeutics', STYLES['cover_meta']))
story.append(PageBreak())

# ── PARSE HTML BODY ──────────────────────────────────────────────────────────
body = soup.find('body') or soup
main = body.find('div', class_='container') or body

IMG_MAX_W = avail_w
IMG_MAX_H = 17 * cm

def process_node(node):
    """Recursively convert HTML nodes to ReportLab flowables."""
    items = []

    if isinstance(node, NavigableString):
        txt = str(node).strip()
        if txt:
            items.append(Paragraph(clean(txt), STYLES['body']))
        return items

    tag = node.name
    if tag is None:
        return items

    css_class = ' '.join(node.get('class', []))

    # Skip script/style
    if tag in ('script', 'style', 'head'):
        return items

    # Difference banner
    if 'diff-banner' in css_class or ('callout' in css_class and 'yellow' in css_class.lower()):
        txt = node.get_text(separator=' ', strip=True)
        items.append(Paragraph(clean(txt), STYLES['callout']))
        return items

    if 'callout' in css_class and ('red' in css_class or 'orange' in css_class):
        txt = node.get_text(separator=' ', strip=True)
        items.append(Paragraph(clean(txt), STYLES['callout_red']))
        return items

    # Headings
    if tag == 'h1':
        items.append(PageBreak())
        items.append(Paragraph(clean(node.get_text()), STYLES['h2']))
        items.append(HRFlowable(width=avail_w, thickness=1.5,
                               color=colors.HexColor('#1F4E79')))
        return items

    if tag == 'h2':
        items.append(PageBreak())
        txt = clean(node.get_text())
        items.append(Paragraph(txt, STYLES['h2']))
        items.append(HRFlowable(width=avail_w, thickness=1.5,
                               color=colors.HexColor('#1F4E79')))
        return items

    if tag == 'h3':
        txt = clean(node.get_text())
        items.append(Spacer(1, 0.15*cm))
        items.append(Paragraph(txt, STYLES['h3']))
        return items

    if tag == 'h4':
        txt = clean(node.get_text())
        items.append(Paragraph(txt, STYLES['h4']))
        return items

    # Paragraph
    if tag == 'p':
        txt = node.get_text(separator=' ', strip=True)
        if txt.strip():
            items.append(html_para(str(node), STYLES['body']))
        return items

    # Figure with embedded image
    if tag == 'figure':
        img_tag_el = node.find('img')
        cap_el     = node.find('figcaption')
        caption    = clean(cap_el.get_text()) if cap_el else ''

        if img_tag_el:
            src = img_tag_el.get('src', '')
            m = re.match(r'data:image/[^;]+;base64,(.+)', src, re.S)
            if m:
                b64 = m.group(1).strip()
                img = b64_to_image(b64, IMG_MAX_W, IMG_MAX_H)
                items.append(Spacer(1, 0.2*cm))
                items.append(img)
                if caption:
                    items.append(Paragraph(caption, STYLES['fig_caption']))
                items.append(Spacer(1, 0.3*cm))
        return items

    # Table
    if tag == 'table':
        tbl = build_html_table(node)
        if tbl:
            items.append(Spacer(1, 0.2*cm))
            items.append(tbl)
            items.append(Spacer(1, 0.25*cm))
        return items

    # List items
    if tag in ('ul', 'ol'):
        for li in node.find_all('li', recursive=False):
            txt = li.get_text(separator=' ', strip=True)
            items.append(Paragraph(f'• {clean(txt)}', STYLES['body']))
        return items

    # HR
    if tag == 'hr':
        items.append(HRFlowable(width=avail_w, thickness=0.5, color=colors.lightgrey))
        return items

    # Generic containers: recurse
    if tag in ('div', 'section', 'article', 'main', 'header', 'body'):
        for child in node.children:
            items.extend(process_node(child))
        return items

    # Span and other inline — treat as paragraph if has text
    txt = node.get_text(separator=' ', strip=True)
    if txt:
        items.append(html_para(str(node), STYLES['body']))
    return items


# Process main content
for child in main.children:
    story.extend(process_node(child))

# ─── BUILD PDF ───────────────────────────────────────────────────────────────
print(f"Building PDF with {len(story)} flowables...")
doc = MMRDocTemplate(
    PDF_PATH,
    pagesize=A4,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    topMargin=MARGIN,
    bottomMargin=MARGIN,
    title='DNLI-I-0001 Medical Monitoring Report — FEB 2026',
    author='Denali Therapeutics (AI-Generated)',
    subject='Medical Monitoring Report DNL126',
)

doc.build(story)
import os
size_mb = os.path.getsize(PDF_PATH) / 1e6
print(f"\n✓ PDF written: {PDF_PATH}")
print(f"  Size: {size_mb:.1f} MB")
