"""Deterministic PDF/content audit plus page renders outside constrained C drive."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import pymupdf

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--render-dir')
args = parser.parse_args()
path = HERE / 'project01_CT_04_HieuGM.299.pdf'
doc = pymupdf.open(path)
text = '\n'.join(page.get_text() for page in doc)
normalized = re.sub(r'\s+', ' ', text)
cover = doc[0].get_text()
toc = doc.get_toc()
checks = {
    'nonempty_all_pages': all(page.get_text().strip() for page in doc),
    'correct_student': 'Giáp Minh Hiếu' in cover and 'B23DCCN299' in cover,
    'confirmed_cover': all(value in cover for value in ['Trần Đình Quế','CT01','04']),
    'no_sample_identity': 'B23DCCN465' not in text and 'Nguyễn Tự Kiên' not in text,
    'seven_chapters': len([x for x in toc if x[0] == 1 and x[1].startswith('CHƯƠNG')]) == 7,
    'toc_present': 'MỤC LỤC' in text and len(toc) >= 30,
    'fifty_five_tests': '55/55' in text and '55 trường hợp' in text,
    'two_real_datasets': '253.680' in text and '101.766' in text,
    'real_model_metrics': all(x in text for x in ['0,8274','0,6334','0,4393','0,1869']),
    'rag_limit_explicit': 'không có LLM' in normalized,
    'rl_scope_explicit': 'contextual bandit' in text and '4.000 episode' in text,
    'remaining_error_kept': 'Q22' in text and '21/22' in text,
    'cloud_deployment_evidence': all(x in normalized for x in [
        'diacare-mas-hieugm299.onrender.com', '13/13', 'trạng thái live']),
    'no_replacement_glyph': '\ufffd' not in text and '\u25a0' not in text}
overflow = []
for i, page in enumerate(doc):
    for word in page.get_text('words'):
        if word[0] < 28 or word[2] > page.rect.width-28 or word[1] < 10 or word[3] > page.rect.height-12:
            overflow.append({'page': i+1, 'word': word[4]})
checks['no_text_outside_page'] = not overflow
if args.render_dir:
    target = Path(args.render_dir)
    target.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(doc):
        page.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(target/f'page-{i+1:03}.png')
report = {'pdf': path.name, 'pages': len(doc), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
          'checks': checks, 'passed': sum(checks.values()), 'total': len(checks),
          'overflow': overflow, 'chapter_outline': [x for x in toc if x[0] == 1],
          'visual_review': 'Separate human-style PNG inspection required; not replaced by these checks.'}
(HERE / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'pages': len(doc), 'passed': report['passed'], 'total': len(checks)}))
if not all(checks.values()):
    raise SystemExit(1)
