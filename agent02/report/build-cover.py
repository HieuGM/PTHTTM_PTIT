"""Retain the supplied cover's ornament, PTIT logo and typography."""
from pathlib import Path
import pymupdf

HERE = Path(__file__).resolve().parent


def build_cover():
    doc = pymupdf.open(HERE.parent / 'reference/cover-template.pdf')
    page = doc[0]
    replacements = {
        'ASSIGNMENT 01': 'ASSIGNMENT 02 – INTELLIGENT ',
        'Sinh viên thực hiện': 'Sinh viên thực hiện :  Giáp Minh Hiếu ',
        'Mã sinh viên': 'Mã sinh viên :  B23DCCN299 ',
    }
    changes = []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                for prefix, replacement in replacements.items():
                    if span['text'].startswith(prefix):
                        changes.append((span, replacement))
    assert len(changes) == 3
    for span, _ in changes:
        page.add_redact_annot(span['bbox'], fill=(1, 1, 1))
    # Preserve both image assets, including the page-sized ornament.
    page.apply_redactions(images=0, graphics=0)
    page.insert_font(fontname='CoverTimesBold', fontfile='C:/Windows/Fonts/timesbd.ttf')
    for span, replacement in changes:
        page.insert_text(span['origin'], replacement, fontname='CoverTimesBold',
                         fontsize=span['size'], color=(0, 0, 0))
    text = page.get_text().replace('\u00a0', ' ')
    assert 'Giáp Minh Hiếu' in text and 'B23DCCN299' in text
    assert 'B23DCCN488' not in text and 'Phạm Mai Linh' not in text
    return doc
