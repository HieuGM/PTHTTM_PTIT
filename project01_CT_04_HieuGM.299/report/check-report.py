"""Audit the upgraded report and render every page for separate visual review."""
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
    'toc_present': 'MỤC LỤC' in text and len(toc) >= 35,
    'four_real_cohorts': all(x in text for x in ['226.342','101.763','768','251']),
    'six_models_three_seeds_72_runs': all(x in normalized for x in ['72','24','Residual','Logistic']),
    'actual_benchmark_metrics': all(x in text for x in ['0,8277','0,6348','0,8653','0,9615']),
    'legacy_reuse': '11 artifact' in normalized and 'legacy-1.0' in text,
    'sql_training': 'SELECT' in text and 'SQLite' in text,
    'knowledge_provenance': all(x in normalized for x in ['Vinmec','340','2160','77','MENTIONS']),
    'graph_real_and_fallback': '400' in text and '2545' in text and 'sqlite_cache' in text,
    'llm_and_citation_limit': 'mkp-api.fptcloud.com' in text and 'citation_ids' in text and 'ngữ nghĩa' in text,
    'seven_agent_contract': all(x in text for x in ['request_id','model_version','Monitoring','Patient Data']),
    'rl_simulation_scope': 'contextual bandit' in text and '4.000' in text and 'gamma=0' in text,
    'retrieval_failures_retained': 'Q22' in text and '0,9091' in text and '0,8750' in text,
    'time_accounting_honest': all(x in text for x in ['145,588','23,449','resume']),
    'upgraded_public_proof': all(x in text for x in ['1d08d9ba7bc1d757ee856268f671ca035399a7b8', '30/30', '29/30', '14:40:42']),
    'public_status_scoped': 'diacare-mas-hieugm299.onrender.com' in text and 'phiên bản' in text,
    'no_replacement_glyph': '\ufffd' not in text and '\u25a0' not in text,
    'identifiers_preserved': not any(x in text for x in ['Neo 4 j', 'B 23 DCCN', 'project 01_CT_', 'srv-dbm 5', '6 eb 79']),
    'no_placeholders': '<!-- BENCHMARK_TABLES -->' not in text and 'TODO' not in text}
overflow=[]
for index,page in enumerate(doc):
    for word in page.get_text('words'):
        if word[0]<28 or word[2]>page.rect.width-28 or word[1]<10 or word[3]>page.rect.height-12:
            overflow.append({'page':index+1,'word':word[4]})
checks['no_text_outside_page']=not overflow
if args.render_dir:
    target=Path(args.render_dir);target.mkdir(parents=True,exist_ok=True)
    for index,page in enumerate(doc):
        page.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(target/f'page-{index+1:03}.png')
report={'pdf':path.name,'pages':len(doc),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'checks':checks,'passed':sum(checks.values()),'total':len(checks),'overflow':overflow,
    'chapter_outline':[x for x in toc if x[0]==1],
    'visual_review':'Separate all-page PNG inspection required; semantic checks do not prove layout.'}
(HERE/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(doc),'passed':report['passed'],'total':len(checks),
    'failed':[k for k,v in checks.items() if not v]}))
if not all(checks.values()):
    raise SystemExit(1)
