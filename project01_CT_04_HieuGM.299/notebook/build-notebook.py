"""Build one readable notebook: inline module source, artifacts are data only."""
import base64
import hashlib
import json
import pprint
from pathlib import Path
import nbformat as nbf

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
cells = []
manifest = {}


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(text):
    source = text.strip()
    compile(source.split('\n', 1)[1] if source.startswith('%%diacare_module ') else source,
            '<notebook-cell>', 'exec')
    cells.append(nbf.v4.new_code_cell(source))


def helper(name):
    code((HERE/name).read_text(encoding='utf-8'))


def module(name):
    relative = name.replace('.', '/')+'.py'
    source = (PROJECT/relative).read_text(encoding='utf-8')
    manifest[relative] = hashlib.sha256(source.encode()).hexdigest()
    code('%%diacare_module '+name+'\n'+source)


def json_data(relative, variable):
    value = json.loads((PROJECT/relative).read_text(encoding='utf-8'))
    code(variable+' = '+pprint.pformat(value, width=110, sort_dicts=False)+
         f'\n(ROOT / {relative!r}).parent.mkdir(parents=True, exist_ok=True)\n'+
         f'(ROOT / {relative!r}).write_text(json.dumps({variable}, ensure_ascii=False, indent=2), encoding="utf-8")')
    if variable == 'CORPUS':
        cells[-1].metadata.update(tags=['data-artifact'], jupyter={'source_hidden':True})


md('''# Project01 — DiaCare Hybrid Multi-Agent System
**Giáp Minh Hiếu · B23DCCN299 · CT01 · Nhóm 04**  
Giảng viên: **PGS.TS. Trần Đình Quế**

Một notebook tự đủ mã thực thi: **4 tập dữ liệu độc lập, 6 loại mô hình, 3 seed = 72 lượt**;
SQLite → Deep Learning; Web/PDF → Knowledge Graph/RAG; **7 agent cốt lõi** → báo cáo.
Mở Jupyter/VS Code/Colab, chọn Python3.12, Run All. Cần Internet lần đầu để cài thư viện/tải4nguồn.
`RUN_MODE="full"` chạy72lượt; `smoke` chạy24lượt (1seed,2epochDL,10cây/iteration), cùng toàn bộ split.
Smoke kiểm luồng; không dùng số smoke thay kết quả full.

Mã nằm trực tiếp trong các ô. Magic `%%diacare_module` chỉ tạo namespace trong bộ nhớ,
để các hàm trùng tên không ghi đè nhau; **không ghi/import tệp `.py` cục bộ**.
JSON tri thức và4trọng số phục vụ được nhúng như **dữ liệu**, không giấu source code.
Ô corpus lớn và tensor được gập mặc định trong JupyterLab; bấm mở ô để xem dữ liệu.
CDC/Hospital tái sử dụng trọng số cũ; benchmark lưu riêng. Pima/Early được chọn bằng validation.
API FPT/Neo4j là tùy chọn cần credentials; mặc định template và graph cache có nhãn.
Điểm nghiên cứu chưa hiệu chuẩn; không chẩn đoán/kê đơn. Không có dữ liệu bệnh nhân Việt Nam.
Nguồn Vinmec/WHO/NIDDK/PDF phục vụ **tri thức**, không phải4cohort có nhãn để train.''')
helper('notebook-setup.py')
helper('notebook-config.py')
helper('notebook-runtime.py')
md('''## 1. Schema và dữ liệu từ Database
CDC khảo sát binary; Hospital tái nhập viện<30ngày; Pima diabetes; Early-stage triệu chứng.
Không xếp hạng chéo AUC giữa nhiệm vụ/quần thể. Nguồn/giấy phép nằm trong `SOURCE_URLS/LICENSES`.
Pima lấy OpenML37 (metadata license Public); UCI34 là bộ khác. Early-stage520dòng →251vector
độc nhất sau dedup. Chia trước khi fit imputer/scaler; Hospital tách theo patient_nbr, ID không vào X.
CSV thật → SQLite raw/prepared tables → SELECT train/val/test. SQL raw có ID: chỉ giữ cục bộ.''')
for name in ('schema', 'database', 'datasets', 'network', 'metrics', 'training', 'benchmark', 'plotting', 'predict', 'verification'):
    module('app.ml.'+name)
md('''## 2. Tái sử dụng mô hình đã có
Bốn state_dict được nhúng có SHA-256; torch.load(weights_only=True). CDC/Hospital giữ nguyên.
Hai mô hình mới là artifact đã chọn bằng validation ở lần full trước; full bên dưới sẽ tái chọn
Pima/Early bằng validation của lần này. Smoke giữ artifact phục vụ, train benchmark riêng.
Các byte base64 dưới đây chỉ là trọng số tensor; thuật toán mạng nằm ở ô `network` phía trên.''')
weights = {}
for dataset in ('cdc', 'hospital', 'pima', 'early'):
    relative = f'models/{dataset}/model.pt'
    raw = (PROJECT/relative).read_bytes()
    weights[relative] = {'base64':base64.b64encode(raw).decode(), 'sha256':hashlib.sha256(raw).hexdigest()}
    json_data(f'models/{dataset}/metadata.json', 'MODEL_METADATA_'+dataset.upper())
code('MODEL_WEIGHTS = '+pprint.pformat(weights, width=100, sort_dicts=False)+'\n'+
     'LEGACY_BYTES = {}\nfor path, item in MODEL_WEIGHTS.items():\n'+
     '    data = base64.b64decode(item["base64"])\n'+
     '    assert hashlib.sha256(data).hexdigest() == item["sha256"]\n'+
     '    target = ROOT/path\n    target.parent.mkdir(parents=True, exist_ok=True)\n    target.write_bytes(data)\n'+
     '    if "/cdc/" in path or "/hospital/" in path:\n        LEGACY_BYTES[path] = data\n'+
     '        meta_path = str(Path(path).with_name("metadata.json"))\n        LEGACY_BYTES[meta_path] = (ROOT/meta_path).read_bytes()\n'+
     'print("4 bộ trọng số có hash; 2 model cũ được giữ nguyên.")')
cells[-1].metadata.update(tags=['data-artifact'], jupyter={'source_hidden':True})
md('''## 3. Benchmark thật: 4×6×3
LR, RF, Histogram Gradient Boosting; MLP64–32, MLP64–32–16, ResidualMLP.
Checkpoint valROC-AUC; ngưỡng valF1; test chỉ đánh giá sau khi đóng băng. Split cố định seed42;
seed42/43/44 thay khởi tạo mô hình, không phải3tập dữ liệu hay6×3loại kiến trúc.
SD ba seed không bao gồm bất định lấy mẫu/dịch miền. Tree weights không phát hành; giữ config/score.
Thời gian dưới đây là lần chạy thật trên máy bạn; download/SQL có thể lâu hơn fit.''')
code('''from app.ml.benchmark import run_benchmark
from app.ml.plotting import plot_benchmark
from app.ml.database import connect_database
from app.ml.verification import verify_benchmark
seeds = (42,43,44) if RUN_MODE == 'full' else (42,)
benchmark_started = time.perf_counter()
benchmark_result = run_benchmark(ROOT, mode=RUN_MODE, seeds=seeds)
benchmark_wall_seconds = time.perf_counter()-benchmark_started
model_verification = verify_benchmark(ROOT, RUN_MODE)
display({'mode':RUN_MODE, 'dataset_count':4, 'model_types':6,
         'runs':benchmark_result['run_count'], 'wall_seconds':benchmark_wall_seconds,
         'independent_checks':model_verification['checks_count']})
display(pd.read_csv(ROOT/f'results/benchmark/{RUN_MODE}/summary.csv'))
for figure in plot_benchmark(ROOT, RUN_MODE):
    display(Image(filename=str(figure)))
with connect_database(ROOT) as db:
    display(pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", db))''')
md('''## 4. Nguồn Web/PDF, Knowledge Graph và RAG
Corpus nhúng là kết quả tải thật có URL/hash/ngày/page, phân biệt downloaded và curated_reference.
Các đoạn PDF có số trang. Quan hệ chuyên môn có chunk dẫn chứng; MENTIONS chỉ là nhận diện thực thể.
PDF tiếng Việt là bản lịch sử năm2020 qua kho chính thức Đồng Nai, không được gọi là hướng dẫn mới nhất.
Truy xuất: wordTF-IDF + charTF-IDF + LSA32 + graph boost; LSA không phải neural embedding.
Có đủ source ingestion để tùy chọn tải lại; mặc định dùng snapshot tái lập, không tải toàn bộ Web khi startup.''')
for name in ('cards', 'sources', 'ontology', 'corpus', 'evaluation-questions', 'source-check-questions'):
    json_data('app/knowledge/'+name+'.json', name.upper().replace('-','_'))
for name in ('rules', 'contracts', 'policy'):
    module('app.agents.'+name)
md('''### Phần tùy chọn: Q-learning cách trình bày
4 trạng thái ×3 hành động,4000episode; reward do tác giả định nghĩa cho hình thức trả lời.
Đây là contextual bandit mô phỏng một bước, không học kết quả bệnh nhân/điều trị.
Không thuộc7agent cốt lõi và không được dùng để tăng số mô hình dự đoán trong benchmark.''')
policy_source = (PROJECT/'scripts/train-policy.py').read_text(encoding='utf-8')
policy_source = policy_source.replace('ROOT = Path(__file__).resolve().parents[1]', '')
code(policy_source)
for name in ('ingestion', 'graph_builder', 'store', 'neo4j_backend', 'retrieval', 'generation'):
    module('app.knowledge.'+name)
helper('notebook-knowledge.py')
md('''## 5. Bảy agent và hợp đồng thông điệp
Data → DL Prediction → Rule-Based → KG/RAG → Coordinator tổng hợp → Explanation → Monitoring.
Mỗi message có request_id/agent/status/payload/evidence/model_version. Input sai dừng trước DL.
Luật an toàn ưu tiên; report tách score/luật/bằng chứng/bất định/xung đột/hạn chế.
Monitoring chỉ metadata, không lưu feature/câu hỏi/key. FPT khi USE_FPT=True và bạn nhập khóa riêng.
Q-learning trình bày của API chat cũ chỉ là phần mở rộng tùy chọn, không chọn điều trị.''')
for name in ('roles', 'reporting', 'workflow', 'coordinator'):
    module('app.agents.'+name)
helper('notebook-demos.py')
md('''## 6. So sánh truy xuất trên bộ câu hỏi phát triển
Ba phương pháp trên cùng câu hỏi đã xây dựng; không gọi đây là kiểm định ngoài miền.
Giữ từng ca sai. Citation đúng ID không tự chứng minh mọi mệnh đề đúng y khoa.
Không gọi API LLM hàng loạt trong phần đánh giá mặc định.''')
helper('notebook-evaluation.py')
md('''## 7. API và toàn bộ giao diện
Source FastAPI, HTML/CSS/JavaScript nằm ngay dưới. TestClient chạy model thật từ4artifact.
Tab benchmark API hiển thị lần full trong thư mục output; smoke được lưu riêng và có thể chưa có tab full.
START_WEB=True mở localhost:8000 trên máy cá nhân. Colab có thể hạn chế cổng.
Docker/Render sử dụng cùng source; không chạy Jupyter trên production.''')
for path in sorted((PROJECT/'app/static').glob('*')):
    if path.is_file() and path.suffix in {'.js','.css','.html'}:
        value = path.read_text(encoding='utf-8')
        if "'''" not in value:
            literal = "r'''"+value+"'''"
        elif '"""' not in value:
            literal = 'r"""'+value+'"""'
        else:
            literal = repr(value)
        code('STATIC_SOURCE = '+literal+f'\n(ROOT/"app/static/{path.name}").write_text(STATIC_SOURCE, encoding="utf-8")')
module('app.api_models')
module('app.main')
helper('notebook-api-checks.py')
code('INLINE_SOURCE_SHA256 = '+pprint.pformat(manifest, width=110)+'\n'+
     '(ROOT/"results/inline-source-manifest.json").write_text(json.dumps(INLINE_SOURCE_SHA256, indent=2), encoding="utf-8")\n'+
     'print("Đã hoàn tất:", ROOT)')
md('''## Cách bảo vệ và giới hạn
Trả lời số lượng:4cohort,6loại mô hình,24cặp dataset–model,72lượt khi full;3DL+3ML.
Không cộng3seed thành18loại. Không gộp bài toán Hospital với chẩn đoán diabetes.
Vinmec/WHO/NIDDK và PDF là dữ liệu tri thức; dữ liệu bảng có nhãn đến từ các nguồn đã nêu.
Neo4j có credentials mới truy vấn graph thật; SQLite cache có nhãn degraded. Template không gọi là LLM.
Chưa kiểm định trên bệnh nhân Việt Nam; không hiệu chuẩn lâm sàng/đưa khuyến nghị điều trị.
Đầu ra nằm riêng trong diacare-notebook-output, gồm raw/SQL cục bộ không nên đưa lên GitHub.
Không gửi khóa vào chat, không lưu notebook với output có secrets; dùng getpass/environment.''')
notebook = nbf.v4.new_notebook(cells=cells, metadata={
    'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
    'language_info':{'name':'python','version':'3.12.9'}, 'diacare':{'version':'2.0','inline_source_sha256':manifest}})
nbf.validate(notebook)
nbf.write(notebook, HERE/'project01-diacare.ipynb')
print(f'Wrote {len(cells)} readable cells; Python source compiles.')
