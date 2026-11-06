"""Refresh report figures, measured benchmark tables, references and Markdown."""
from pathlib import Path
import csv
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STEM = ROOT.name

def architecture():
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set(xlim=(0, 11), ylim=(0, 6.5)); ax.axis('off')
    boxes = [(.25,5.35,3.0,'Web UI / API\nFeatures + optional question'),
        (4.0,5.35,3.0,'Coordinator Agent\nValidate order / aggregate / errors'),
        (.25,3.9,3.0,'Patient Data Agent\nStrict schema / early stop'),
        (4.0,3.9,3.0,'DL Prediction Agent\nReuse serving weights + metadata'),
        (7.75,3.9,3.0,'Rule-Based Agent\nSafety + review flags'),
        (.25,2.4,3.0,'KG/RAG Agent\nEntities / graph / chunks / sources'),
        (4.0,2.4,3.0,'Explanation Agent\nFPT API or labelled template'),
        (7.75,2.4,3.0,'Monitoring Agent\nRequest / version / metadata only'),
        (.25,.65,4.5,'Model + data layer\n4 SQL cohorts / 6 types / 72 benchmark runs'),
        (6.25,.65,4.5,'Knowledge layer\nNeo4j / Web + PDF / SQLite evidence cache')]
    for x,y,w,label in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,.78,boxstyle='round,pad=.06',
            facecolor='#edf5f4',edgecolor='#337b76',linewidth=1.2))
        ax.text(x+w/2,y+.39,label,ha='center',va='center',fontsize=10.8,color='#183b49')
    arrows=[((3.3,5.74),(3.9,5.74)),((4.6,5.27),(1.75,4.77)),
        ((3.3,4.29),(3.9,4.29)),((7.05,4.29),(7.65,4.29)),
        ((9.25,3.82),(1.75,3.28)),((3.3,2.79),(3.9,2.79)),
        ((7.05,2.79),(7.65,2.79)),((2.5,1.49),(5.0,3.82)),
        ((8.5,1.49),(1.75,2.32))]
    for start,end in arrows:
        ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':'#698e90','lw':1.2})
    ax.text(5.5,.15,'Seven core agents; optional RL simulation is outside the clinical workflow',
        ha='center',fontsize=10,color='#384d59')
    fig.tight_layout(pad=.3)
    (HERE/'figures').mkdir(exist_ok=True)
    fig.savefig(HERE/'figures/architecture.png',dpi=180,bbox_inches='tight');plt.close(fig)

def number(value):
    return f'{float(value):.4f}'.replace('.',',')

def benchmark_tables():
    rows=list(csv.DictReader((ROOT/'results/benchmark/full/summary.csv').open(encoding='utf-8-sig')))
    names={'cdc':'CDC BRFSS','hospital':'Hospital','pima':'Pima','early':'Early Stage'}
    names_short={'logistic':'Logistic','random_forest':'Random Forest',
        'hist_gradient_boosting':'HGB','mlp2':'MLP2','mlp3':'MLP3','resmlp':'ResMLP'}
    parts=[]
    for index,dataset in enumerate(['cdc','hospital','pima','early'],4):
        parts.append('<!-- pagebreak -->')
        parts.append(f'## 4.{index}. Kết quả {names[dataset]}')
        parts.append('Các giá trị là test mean ± SD ba seed; ngưỡng từng run chọn trên validation.')
        lines=['| Model | ROC-AUC | AP | F1 | Brier |','|---|---:|---:|---:|---:|']
        for row in [r for r in rows if r['dataset']==dataset]:
            cells=[names_short[row['model_id']]]
            for metric in ['roc_auc','average_precision','f1','brier']:
                cells.append(number(row[metric+'_mean'])+' ± '+number(row[metric+'_std']))
            lines.append('| '+' | '.join(cells)+' |')
        parts.append('\n'.join(lines))
        parts.append(f'![So sánh metric trong cohort {names[dataset]}, error bar là SD ba seed](../results/benchmark/full/figures/{dataset}-benchmark.png)')
    path=HERE/'sections/04-deep-learning.md'
    value=path.read_text(encoding='utf-8-sig')
    generated='<!-- BENCHMARK_START -->\n\n'+'\n\n'.join(parts)+'\n\n<!-- BENCHMARK_END -->'
    if '<!-- BENCHMARK_TABLES -->' in value:
        value=value.replace('<!-- BENCHMARK_TABLES -->',generated)
    else:
        value=re.sub(r'<!-- BENCHMARK_START -->.*?<!-- BENCHMARK_END -->',lambda _:generated,value,flags=re.S)
    path.write_text(value,encoding='utf-8')

def references():
    corpus=json.loads((ROOT/'app/knowledge/corpus.json').read_text(encoding='utf-8'))
    sources={d['url']:d['title'] for d in corpus['documents'] if d['ingestion']=='downloaded'}
    extra={
      'https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators':'UCI891. CDC Diabetes Health Indicators.',
      'https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset':'Alex Teboul. Binary BRFSS2015; nguồn khai báo CC0.',
      'https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008':'UCI296. Diabetes130-US Hospitals; DOI10.24432/C5230J; CC BY4.0.',
      'https://doi.org/10.1155/2014/781670':'Strack và cộng sự (2014). Impact of HbA1c Measurement on Hospital Readmission Rates.',
      'https://www.openml.org/d/37':'OpenML37. Pima; metadata licence Public, không tự gán CC0.',
      'https://api.openml.org/api/v1/json/data/37':'OpenML. Metadata và MD5 ARFF của dataset37.',
      'https://archive.ics.uci.edu/dataset/529/early+stage+diabetes+risk+prediction+dataset':'UCI529. Early Stage Diabetes Risk Prediction; DOI10.24432/C5VG8H; CC BY4.0.',
      'https://arxiv.org/abs/2005.11401':'Lewis và cộng sự (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.',
      'https://www.cs.rhul.ac.uk/~mike/pubs/ker95.pdf':'Wooldridge và Jennings (1995). Intelligent Agents: Theory and Practice.',
      'http://incompleteideas.net/book/the-book-2nd.html':'Sutton và Barto (2018). Reinforcement Learning: An Introduction.',
      'https://docs.pytorch.org/docs/stable/index.html':'PyTorch. Tài liệu chính thức tensor, neural network, state_dict.',
      'https://scikit-learn.org/stable/modules/model_evaluation.html':'scikit-learn. Model evaluation, Average Precision và ROC-AUC.',
      'https://neo4j.com/docs/python-manual/current/':'Neo4j. Python Driver Manual.',
      'https://ai-docs.fptcloud.com/api-reference/ai-marketplace/api-reference/api-integration-multimodal-model-text-md':'FPT Cloud AI Marketplace. API integration, gateway mkp-api.fptcloud.com và /chat/completions.',
      'https://fastapi.tiangolo.com/deployment/docker/':'FastAPI. FastAPI in Containers - Docker.',
      'https://render.com/docs/blueprint-spec':'Render. Blueprint YAML Reference.',
      'https://render.com/docs/deploys':'Render. Deploy lifecycle and manual deploys for public Git repository URLs.'}
    sources.update(extra)
    text='# TÀI LIỆU THAM KHẢO\n\nTài liệu kiến trúc do giảng viên cung cấp: project_architecture_multiagent_diabet_v1.pdf (11 trang,11/2026). Đây là đặc tả được đối chiếu, không là kết quả đo của project.\n\nNguồn Web/PDF được kiểm tra trong quá trình thực hiện; ngày tải/hash/note cụ thể lưu trong corpus và knowledge-ingestion.json. PDF Việt 2020 là nguồn lịch sử. Số liệu mô hình được tính bằng mã và dữ liệu của bài, không chép số liệu báo cáo mẫu.\n\n'
    text+='\n\n'.join(f'{i}. [{title}]({url})' for i,(url,title) in enumerate(sources.items(),1))
    (HERE/'sections/09-references.md').write_text(text+'\n',encoding='utf-8')
    return len(sources)

def main():
    architecture();benchmark_tables();count=references()
    order=sorted(p.name for p in (HERE/'sections').glob('*.md'))
    (HERE/'section-order.json').write_text(json.dumps(order,indent=2),encoding='utf-8')
    text='# PROJECT01 - HỆ ĐA AGENT HỖ TRỢ BỆNH ĐÁI THÁO ĐƯỜNG\n\nGiáp Minh Hiếu - B23DCCN299 - CT01 - Nhóm04\n\n'
    text+='\n\n'.join((HERE/'sections'/name).read_text(encoding='utf-8-sig') for name in order)
    (HERE/(STEM+'.md')).write_text(text,encoding='utf-8')
    print('Prepared',len(order),'sections;',count,'references')

if __name__=='__main__':
    main()
