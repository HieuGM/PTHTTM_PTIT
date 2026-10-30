"""Validate required report evidence and rendered text bounds before packaging."""
from pathlib import Path
import json
import re
import pymupdf
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STEM = 'agent02_CT_04_hieugm'
checks = {}
source = (HERE / (STEM + '.md')).read_text(encoding='utf-8')
pdf = pymupdf.open(HERE / (STEM + '.pdf'))
text = '\n'.join(p.get_text() for p in pdf)
checks['all_ten_questions'] = all(re.search(rf'Câu {i}\s', text) for i in range(1,11))
checks['no_unfilled_placeholders'] = '{{' not in source and '}}' not in source
checks['identity'] = all(s in text for s in ['Giáp Minh Hiếu','B23DCCN299','agent02_CT_04_hieugm'])
cover = pdf[0].get_text().replace('\u00a0', ' ')
checks['cover_identity'] = 'Giáp Minh Hiếu' in cover and 'B23DCCN299' in cover
checks['cover_assignment'] = 'ASSIGNMENT 02' in cover
checks['cover_no_template_student'] = 'Phạm Mai Linh' not in cover and 'B23DCCN488' not in cover
checks['figures'] = source.count('![') == 3
checks['source_files'] = all((ROOT / f).is_file() for f in [
    'code/agent02_experiment.py','code/reference_core.py','code/evaluation.py',
    'code/test-experiment.py','reference/agent02_code.tex',
    'notebook/agent02_CT_04_hieugm.ipynb','notebook/agent02_CT_04_hieugm.html'])
checks['no_replacement_glyph'] = '\ufffd' not in text
outliers = []
for i, page in enumerate(pdf):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            x0,y0,x1,y1 = line['bbox']
            if x0 < 42 or x1 > page.rect.width-42 or y0 < 34 or y1 > page.rect.height-21:
                outliers.append({'page':i+1,'bbox':[x0,y0,x1,y1],
                                 'text':''.join(s['text'] for s in line['spans'])})
checks['text_within_page_margins'] = not outliers
checks['page_count'] = len(pdf) == 14
baseline = json.loads((ROOT/'results/baseline-seed-42.json').read_text(encoding='utf-8'))
checks['baseline_rewards'] = baseline['rl_evaluation']['mean_rewards'][0] == 34.9185
checks['training_total'] = baseline['training_stats']['rl_total_reward'] == 3345548
nb = json.loads((ROOT/'notebook'/f'{STEM}.ipynb').read_text(encoding='utf-8'))
codes = [c for c in nb['cells'] if c['cell_type']=='code']
checks['notebook_executed'] = all(c['execution_count'] is not None for c in codes)
checks['notebook_no_errors'] = not any(o['output_type']=='error' for c in codes for o in c['outputs'])
tests = json.loads((ROOT/'results/test-results.json').read_text(encoding='utf-8'))
checks['numerical_tests'] = tests['passed'] == 6
summary = json.loads((ROOT/'results/summary.json').read_text(encoding='utf-8'))
checks['full_seed_groups'] = len(summary['aggregate'])==12 and all(r['n']==5 for r in summary['aggregate'])
audit = {'pages':len(pdf),'checks':checks,'all_passed':all(checks.values()),'outliers':outliers,
         'visual_review':'PNG inspection required separately'}
(HERE/'preview/audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False,indent=2))
assert audit['all_passed']
