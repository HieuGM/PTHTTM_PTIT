"""Assemble readable, standalone notebook cells from the reviewed application."""
import ast
import json
import pprint
from pathlib import Path
import nbformat as nbf

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    compile(text, '<notebook-cell>', 'exec')
    cells.append(nbf.v4.new_code_cell(text.strip()))


def source(relative, main=None, replacements=()):
    """Remove packaging imports/entry points; preserve actual implementation/comments."""
    text = (PROJECT / relative).read_text(encoding='utf-8')
    lines = text.splitlines()
    remove = set()
    for node in ast.walk(ast.parse(text)):
        imported = isinstance(node, ast.ImportFrom) and (
            (node.module or '').startswith(('app.', 'conftest')) or node.level)
        target = ast.get_source_segment(text, node) or ''
        packaging = isinstance(node, (ast.Assign, ast.Expr)) and (
            target.startswith(('ROOT =', 'sys.path.insert', 'module =', 'mm =', 'module.loader.')))
        entry = isinstance(node, ast.If) and '__name__' in ast.unparse(node.test)
        unused_main = isinstance(node, ast.FunctionDef) and node.name == 'main' and main is None
        if imported or packaging or entry or unused_main:
            remove.update(range(node.lineno - 1, node.end_lineno))
    text = '\n'.join(line for i, line in enumerate(lines) if i not in remove)
    if main:
        text = text.replace('def main():', f'def {main}():')
    for old, new in replacements:
        text = text.replace(old, new)
    return text.strip()


md('''# Project01 — DiaCare MAS
**Giáp Minh Hiếu · B23DCCN299 · CT01 · Nhóm 04**

Giảng viên: **PGS. TS. Trần Đình Quế**

Một notebook chứa toàn bộ mã tính toán, KB, Agent, API và giao diện. Mở bằng Jupyter,
VS Code hoặc Google Colab, chọn Python 3.12 rồi **Run All**. Không cần các tệp `.py`
hay model/JSON đính kèm. Cần Internet lần đầu để tải thư viện và hai CSV thật từ UCI.

Mặc định `RUN_MODE="full"`: hai MLP tối đa 25 epoch và hai logistic baseline.
`smoke` giữ nguyên toàn bộ dữ liệu/split nhưng chỉ train 2 epoch để kiểm tra luồng.
Đầu ra mới nằm trong `diacare-notebook-output/`, tách khỏi kết quả PDF/Render.
Các số sau khi chạy là kết quả lần chạy này; không cam kết trùng từng bit giữa phiên bản thư viện.

Luồng: môi trường → dữ liệu → MLP/baseline → biểu đồ → KB/luật/RL/MAS → demo → đánh giá → API/web.
Hai nhiệm vụ khác nhau; score chưa hiệu chuẩn lâm sàng, không dùng chẩn đoán/kê đơn.
Demo đã triển khai: https://diacare-mas-hieugm299.onrender.com .''')
code((HERE / 'notebook-setup.py').read_text(encoding='utf-8'))
code('''from pathlib import Path
import json, os, platform, time
import numpy as np, pandas as pd, torch, sklearn
from IPython.display import display, Markdown, Image
RUN_MODE = "full"  # "smoke": 2 epoch; "full": 25 epoch, patience=5
assert RUN_MODE in {"smoke", "full"}
EPOCHS = 25 if RUN_MODE == "full" else 2
ROOT = Path.cwd() / "diacare-notebook-output"
for directory in ("data/raw", "data/splits", "results", "models", "app/knowledge", "app/static"):
    (ROOT / directory).mkdir(parents=True, exist_ok=True)
os.environ["APP_DATA_DIR"] = str(ROOT / "runtime")
environment = dict(python=platform.python_version(), torch=torch.__version__,
    numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__,
    run_mode=RUN_MODE, epochs=EPOCHS, platform=platform.platform())
(ROOT / "results/environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
display(environment)''')
md('''## 1. Dữ liệu thật và schema
CDC BRFSS 2015 (nguồn gốc CC0): nhãn binary gộp diabetes/prediabetes, **không phải chẩn đoán mới**.
Hospital 1999–2008 (CC BY 4.0): tái nhập viện <30 ngày, đặc trưng chỉ đầy đủ khi ra viện.
Nguồn UCI: https://archive.ics.uci.edu/dataset/891 và https://archive.ics.uci.edu/dataset/296 .
CDC loại nhóm vector có nhãn mâu thuẫn rồi bỏ vector trùng trước chia stratified70/15/15.
Hospital chia nhóm `patient_nbr` không giao người bệnh. ID không vào X. Mean/std chỉ fit train.''')
code(source('app/ml/schema.py'))
code(source('scripts/fetch-data.py', 'fetch_data', [('ROOT.parent /', 'ROOT /')]) + '\n\nfetch_data()')
code(source('scripts/prepare-data.py', 'prepare_data') + '\n\nprepare_data()')
md('''## 2. Hai MLP và baseline
MLP n→64→32→16→1, Adam, dropout; chọn checkpoint bằng validation ROC-AUC,
ngưỡng bằng validation F1. Test chỉ dùng sau khi đóng băng. Logistic cùng split/scaler.
Các assertion kiểm tra group disjointness nằm ngay trong ô chuẩn bị dữ liệu.
Chỉ một seed; chưa có kiểm định ngoài miền hoặc hiệu chuẩn hậu nghiệm.''')
code(source('app/ml/network.py'))
code(source('scripts/model-metrics.py'))
code(source('scripts/train-models.py', replacements=[('mm.', '')]) +
     '\n\nfor dataset in ("cdc", "hospital"):\n    train(dataset, EPOCHS)')
md('## 3. Đọc kết quả và biểu đồ ROC, PR, calibration, split')
code(source('scripts/plot-model-results.py', 'plot_results', [("matplotlib.use('Agg')", "# Hiển thị ảnh sau khi lưu, phù hợp cả Colab và nbclient.")]) +
     '\n\nplot_results()\ndisplay(pd.read_csv(ROOT / "results/model-comparison.csv"))\n'
     'for name in ("cdc-evaluation", "hospital-evaluation", "dataset-splits"):\n'
     '    display(Image(filename=str(ROOT / f"results/figures/{name}.png")))')
md('''## 4. Kho tri thức có nguồn, luật và Q-learning
KB24 thẻ được nhúng bên dưới, giữ ID/URL gốc. TF-IDF trích xuất nội dung, không có LLM.
Luật an toàn đi trước policy. Q-learning là bandit một bước với reward cách trình bày
do người viết quy định; **không học điều trị hoặc kết quả sức khỏe**.''')
for name, variable in [('cards', 'KB_CARDS'), ('evaluation-questions', 'EVALUATION_QUESTIONS')]:
    payload = json.loads((PROJECT / f'app/knowledge/{name}.json').read_text(encoding='utf-8'))
    code(f'{variable} = ' + pprint.pformat(payload, width=100, sort_dicts=False) + f'\n(ROOT / "app/knowledge/{name}.json").write_text('
         f'json.dumps({variable}, ensure_ascii=False, indent=2), encoding="utf-8")')
code(source('app/agents/rules.py'))
code(source('scripts/train-policy.py') + '\ndisplay(result)')
code(source('app/agents/policy.py'))
code(source('app/agents/contracts.py'))
code(source('app/knowledge/retrieval.py'))
code(source('app/ml/predict.py') + '\n\n_default.cache_clear()')
code(source('app/agents/coordinator.py'))
md('''## 5. Demo ngay trong notebook
Sửa `QUESTION` hoặc các ô nhập, bấm nút. Các giá trị mặc định của schema chỉ để minh họa giao diện,
không phải hồ sơ bệnh nhân. Không lưu request. Tuổi CDC là **mã nhóm tuổi**.
Với câu hỏi cấp cứu, liên hệ cơ sở y tế; ứng dụng chỉ hỗ trợ giáo dục.''')
code((HERE / 'notebook-demos.py').read_text(encoding='utf-8'))
md('''## 6. Đánh giá phát triển
30 câu hỏi tác giả xây dựng và 11 ca luật, không phải benchmark độc lập/kiểm định y khoa.
Giữ từng ca sai, gồm Q22 chọn thẻ tổng quát trước thẻ kỳ vọng. Metric mô hình là ở mục3.''')
code(source('tests/evaluate-system.py') + '\n\nevaluation = evaluate()\n'
     'display(pd.DataFrame(evaluation["cases"])[["id", "first_relevant_rank", "cited_ids", "answerability_correct"]])')
md('''## 7. Toàn bộ API và giao diện web (tùy chọn)
Các ô dưới chứa source HTML/CSS/JavaScript và FastAPI. Chạy kiểm tra nội bộ bằng TestClient,
không cần mở server. `START_WEB=True` mở web localhost:8000 bằng thread nền trên máy cá nhân;
Colab có thể hạn chế truy cập cổng. Dừng bằng `web_server.should_exit=True`.
Docker/Render tiếp tục dùng source module trong gói nộp, không chạy Jupyter trên production.''')
for name, variable in [('index.html', 'INDEX_HTML'), ('style.css', 'STYLE_CSS'), ('app.js', 'APP_JS')]:
    value = (PROJECT / f'app/static/{name}').read_text(encoding='utf-8')
    assert "'''" not in value
    code(f"{variable} = r'''" + value + f"'''\n(ROOT / \"app/static/{name}\").write_text({variable}, encoding=\"utf-8\")")
code(source('app/main.py'))
code((HERE / 'notebook-api-checks.py').read_text(encoding='utf-8'))
md('''## Hoàn thành
Mọi lần chạy ghi kết quả thật vào `diacare-notebook-output/results/` và trọng số vào `models/`.
Không ghi đè metric trong báo cáo hoặc dịch vụ đang chạy. Có thể xóa thư mục đầu ra để chạy mới.
Raw CSV có ID bệnh viện chỉ nằm trong đầu ra cục bộ; không đưa raw CSV vào gói chia sẻ.
Để tái lập ngân sách báo cáo chọn `full`; phiên bản/hardware có thể làm số khác nhẹ.''')
notebook = nbf.v4.new_notebook(cells=cells, metadata={
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.12.9'}})
nbf.validate(notebook)
nbf.write(notebook, HERE / 'project01-diacare.ipynb')
print(f'Wrote {len(cells)} cells; all Python cells compile.')
