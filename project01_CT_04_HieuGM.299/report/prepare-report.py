"""Assemble editable report, source list and architecture from actual assets."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STEM = ROOT.name
fig, ax = plt.subplots(figsize=(11, 6))
ax.set(xlim=(0, 11), ylim=(0, 6)); ax.axis('off')
boxes = {
    'ui': (4.2, 5.1, 'Vietnamese web UI\nChat / Models / KB'),
    'api': (4.2, 3.9, 'FastAPI + Coordinator\nValidation / bounded trace'),
    'safe': (.3, 3.9, 'Safety rules\nPriority override'),
    'ml': (.3, 2.3, 'Data + Prediction agents\nCDC MLP / Hospital MLP'),
    'kb': (8.1, 2.3, 'Retrieval agent\nSQLite KB + TF-IDF'),
    'policy': (4.2, 2.3, 'Policy + Education agents\nQ-table / extractive answer'),
    'critic': (4.2, .7, 'Critic agent\nCitation / score semantics')}
for x, y, label in boxes.values():
    ax.add_patch(FancyBboxPatch((x, y), 2.6, .72, boxstyle='round,pad=.08',
                              facecolor='#edf5f4', edgecolor='#337b76', linewidth=1.2))
    ax.text(x+1.3, y+.36, label, ha='center', va='center', fontsize=13.5, color='#183b49')
arrows=[((5.5,5.02),(5.5,4.7)),((4.12,4.26),(2.98,4.26)),
        ((4.5,3.82),(1.6,3.1)),((6.5,3.82),(9.4,3.1)),
        ((8.02,2.66),(6.88,2.66)),((5.5,2.22),(5.5,1.5)),
        ((1.6,2.22),(4.12,1.06))]
for start,end in arrows:
    ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':'#698e90','lw':1.4})
fig.tight_layout(pad=.3)
fig.savefig(HERE/'figures/architecture.png',dpi=180,bbox_inches='tight')
plt.close(fig)

cards=json.loads((ROOT/'app/knowledge/cards.json').read_text(encoding='utf-8'))
sources={card['url']:card['source_title'] for card in cards}
extra={
 'https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators':'UCI. CDC Diabetes Health Indicators. DOI 10.24432/C53919.',
 'https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset':'Alex Teboul. Diabetes Health Indicators Dataset, BRFSS 2015; CC0.',
 'https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008':'UCI. Diabetes 130-US Hospitals 1999–2008. DOI 10.24432/C5230J; CC BY 4.0.',
 'https://extranet.who.int/ncdsmicrodata/index.php/catalog/948/study-description':'WHO. Viet Nam STEPS 2021, VNM_2021_STEPS_v01; nguồn khảo sát, chưa tải/huấn luyện trong project.',
 'https://arxiv.org/abs/2005.11401':'Lewis và cộng sự (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.',
 'https://www.cs.rhul.ac.uk/~mike/pubs/ker95.pdf':'Wooldridge và Jennings (1995). Intelligent Agents: Theory and Practice.',
 'http://incompleteideas.net/book/the-book-2nd.html':'Sutton và Barto (2018). Reinforcement Learning: An Introduction, 2nd edition.',
 'https://docs.pytorch.org/docs/stable/index.html':'PyTorch. Tài liệu chính thức về tensor, neural network và state_dict.',
 'https://scikit-learn.org/stable/modules/model_evaluation.html':'scikit-learn. Model evaluation và định nghĩa Average Precision/ROC-AUC.',
 'https://fastapi.tiangolo.com/deployment/docker/':'FastAPI. FastAPI in Containers - Docker.',
 'https://render.com/docs/blueprint-spec':'Render. Blueprint YAML Reference.'}
sources.update(extra)
references='# TÀI LIỆU THAM KHẢO\n\nCác nguồn web được kiểm tra trong quá trình thực hiện ngày 05/11/2026; từng thẻ KB giữ retrieved_at riêng. Trọng số và kết quả đo do mã project tạo, không lấy số liệu của bài mẫu.\n\n'
references+='\n\n'.join(f'{i}. [{title}]({url})' for i,(url,title) in enumerate(sources.items(),1))
(HERE/'sections/09-references.md').write_text(references+'\n',encoding='utf-8')
order=sorted(p.name for p in (HERE/'sections').glob('*.md'))
(HERE/'section-order.json').write_text(json.dumps(order,indent=2),encoding='utf-8')
text='# PROJECT 01 - HỆ ĐA AGENT HỖ TRỢ BỆNH ĐÁI THÁO ĐƯỜNG\n\nGiáp Minh Hiếu — B23DCCN299 — CT01 — Nhóm 04\n\n'
text+='\n\n'.join((HERE/'sections'/name).read_text(encoding='utf-8') for name in order)
(HERE/(STEM+'.md')).write_text(text,encoding='utf-8')
print('Prepared',len(order),'sections;',len(sources),'references')
