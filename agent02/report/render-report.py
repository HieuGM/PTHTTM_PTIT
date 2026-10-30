"""Render the editable Markdown report to a Unicode PDF, then PNGs for review."""
from pathlib import Path
import re
import html
import runpy
import pymupdf
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                               Table, TableStyle, Image, Preformatted, KeepTogether)
from reportlab.lib.pagesizes import A4

HERE = Path(__file__).resolve().parent
STEM = 'agent02_CT_04_hieugm'
for name, file in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf'),
                   ('Arial-Italic', 'ariali.ttf'), ('Mono', 'consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + file))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic')
styles = {
    'body': ParagraphStyle('body', fontName='Arial', fontSize=10.5, leading=15.2,
                           spaceAfter=8),
    'title': ParagraphStyle('title', fontName='Arial-Bold', fontSize=23, leading=31,
                            spaceAfter=20, textColor=colors.black),
    'h1': ParagraphStyle('h1', fontName='Arial-Bold', fontSize=16, leading=22,
                         spaceAfter=13, textColor=colors.HexColor('#17384e')),
    'h2': ParagraphStyle('h2', fontName='Arial-Bold', fontSize=11.6, leading=16,
                         spaceBefore=7, spaceAfter=7),
    'cell': ParagraphStyle('cell', fontName='Arial', fontSize=9, leading=12),
    'caption': ParagraphStyle('caption', fontName='Arial-Italic', fontSize=9,
                              leading=12, spaceAfter=10, alignment=TA_CENTER),
    'code': ParagraphStyle('code', fontName='Mono', fontSize=7.4, leading=10,
                           spaceAfter=10, backColor=colors.HexColor('#f1f4f6'),
                           borderPadding=7),
}


def para(text, style='body'):
    safe = html.escape(text)
    safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe)
    safe = re.sub(r'`(.+?)`', r'<font name="Mono">\1</font>', safe)
    return Paragraph(safe, styles[style])


def table(lines):
    rows = [x.strip().strip('|').split('|') for x in lines
            if not re.match(r'^\|[\s:|\-]+\|$', x.strip())]
    data = [[para(c.strip(), 'cell') for c in row] for row in rows]
    width = A4[0] - 100
    # Long labels receive a wider first column.
    ratios = [1.6] + [1] * (len(data[0]) - 1)
    t = Table(data, colWidths=[width * x / sum(ratios) for x in ratios], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e7eff4')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), .35, colors.HexColor('#bdcbd4')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f6f8fa')]),
    ]))
    return t


def parse(text):
    lines = text.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == '<!-- pagebreak -->':
            out.append(PageBreak())
        elif line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            out.append(Preformatted('\n'.join(code), styles['code']))
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i])
                i += 1
            out.extend([table(rows), Spacer(1, 10)])
            continue
        elif line.startswith('!['):
            match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            path = HERE / match[2]
            image = Image(str(path))
            max_height = 210 if any(s in str(path) for s in ['learning-rate', 'exploration']) else 290
            scale = min((A4[0] - 100) / image.imageWidth, max_height / image.imageHeight)
            image.drawWidth = image.imageWidth * scale
            image.drawHeight = image.imageHeight * scale
            out.append(KeepTogether([image, Spacer(1, 6), para(match[1], 'caption')]))
        elif line.startswith('# '):
            out.append(para(line[2:], 'title'))
        elif line.startswith('## '):
            out.append(para(line[3:], 'h1'))
        elif line.startswith('### '):
            out.append(para(line[4:], 'h2'))
        else:
            out.append(para(line))
        i += 1
    return out


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Arial', 8)
    canvas.setFillColor(colors.HexColor('#587083'))
    canvas.drawString(50, 30, 'AGENT02 | Giáp Minh Hiếu | B23DCCN299')
    canvas.drawRightString(A4[0] - 50, 30, str(doc.page))
    canvas.restoreState()


if __name__ == '__main__':
    doc = SimpleDocTemplate(str(HERE / f'{STEM}.pdf'), pagesize=A4,
                            leftMargin=50, rightMargin=50, topMargin=47,
                            bottomMargin=48, title='Agent 02 Q learning và agent theo luật',
                            author='Giáp Minh Hiếu')
    content = (HERE / f'{STEM}.md').read_text(encoding='utf-8')
    body = content.split('<!-- pagebreak -->', 1)[1]
    doc.build([Spacer(1, 1), PageBreak()] + parse(body), onLaterPages=footer)
    old = pymupdf.open(HERE / f'{STEM}.pdf')
    cover = runpy.run_path(str(HERE / 'build-cover.py'))['build_cover']()
    combined = pymupdf.open()
    combined.insert_pdf(cover)
    combined.insert_pdf(old, from_page=1)
    combined.set_metadata(old.metadata)
    data = combined.tobytes(garbage=4, deflate=True)
    old.close()
    cover.close()
    combined.close()
    (HERE / f'{STEM}.pdf').write_bytes(data)
    preview = HERE / 'preview'
    preview.mkdir(exist_ok=True)
    pdf = pymupdf.open(HERE / f'{STEM}.pdf')
    for index, page in enumerate(pdf):
        page.get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4)).save(preview / f'page-{index+1:02}.png')
    print('Rendered', len(pdf), 'pages')
