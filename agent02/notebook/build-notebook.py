"""Consolidate all assignment code into a portable, fully executed notebook."""
from pathlib import Path
import ast
import sys
import tempfile
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager
from nbconvert import HTMLExporter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STEM = 'agent02_CT_04_hieugm'
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = []


def section(title, description, source):
    cells.extend([md('## ' + title + '\n\n' + description), code(source)])


def definitions(filename, names):
    text = (ROOT / 'code' / filename).read_text(encoding='utf-8')
    lines = text.splitlines()
    result = []
    for node in ast.parse(text).body:
        if getattr(node, 'name', '') in names:
            start = min([node.lineno] + [d.lineno for d in getattr(node, 'decorator_list', [])])
            result.append('\n'.join(lines[start-1:node.end_lineno]))
    assert len(result) == len(names)
    return '\n\n\n'.join(result)


cells.append(md('# Agent 02 Q learning và agent theo luật\n\n'
    '**Giáp Minh Hiếu — B23DCCN299**\n\n'
    'Notebook này chứa toàn bộ mã làm bài, tự chạy độc lập trên Jupyter hoặc Colab. '
    'Không cần thư mục code, file Python, dữ liệu JSON hay hình từ bên ngoài. '
    'Chọn **Restart Kernel and Run All** để chạy đủ 31 lượt: mỗi lượt '
    '5.000 episode × 20 bước huấn luyện và 500 × 20 bước đánh giá. '
    'Thời gian tham khảo khoảng 12 phút trên máy đã kiểm chứng.\n\n'
    'Cần NumPy và Matplotlib. Nếu chưa có, chạy `%pip install numpy matplotlib` '
    'trong một ô riêng. Kết quả CSV, JSON và PNG được chương trình tự tạo '
    'trong thư mục agent02_results cạnh thư mục làm việc. '
    'Mã phát triển từ agent02_code.tex do giảng viên cung cấp.'))
section('1 Thư viện và thư mục kết quả', 'Chỉ dùng thư viện chuẩn, NumPy, Matplotlib và công cụ hiển thị Jupyter.',
    'from dataclasses import dataclass, asdict, replace\nfrom pathlib import Path\n'
    'import csv, json, platform, sys, time\nimport numpy as np\n'
    'import matplotlib\nmatplotlib.use("Agg")\nimport matplotlib.pyplot as plt\n'
    'from IPython.display import display, Image, HTML\n'
    'OUT = Path.cwd() / "agent02_results"\nOUT.mkdir(parents=True, exist_ok=True)\n'
    'print("Output directory:", OUT.resolve())\n'
    'print("Python:", platform.python_version(), "NumPy:", np.__version__)')
section('2 Cấu hình thực nghiệm', 'Giữ nguyên ngân sách và các tham số của đề.',
    definitions('reference_core.py', ['Config']))
section('3 Môi trường thương mại điện tử',
    'Hai agent chọn đồng thời. Chuyển đổi theo đề, doanh số Binomial, reward là lợi nhuận.',
    definitions('reference_core.py', ['ECommerceEnvironment']))
section('4 Agent Q learning', 'Q có kích thước (2,2,2); epsilon-greedy, random tie và terminal target.',
    definitions('reference_core.py', ['QLearningAgent']))
section('5 Agent theo luật', 'Không học từ reward, không tự khởi phát giảm giá từ lịch sử 00.',
    definitions('reference_core.py', ['RuleBasedAgent']))
section('6 Huấn luyện một RL với đối thủ luật', 'Chỉ RL cập nhật Q. Ghi reward và số hành động từng episode.',
    definitions('reference_core.py', ['train_rl_against_rule']))
section('7 Đánh giá riêng và đóng băng policy',
    'Cùng demand và uniforms khách hàng giữa các trận riêng. Không cập nhật Q, không exploration.',
    definitions('evaluation.py', ['make_tape', 'evaluate']))
section('8 Ghi dữ liệu và thống kê', 'SD mẫu giữa năm seed dùng ddof=1, khác SD giữa episode.',
    definitions('results_io.py', ['write_json', 'write_csv', 'training_stats', 'aggregate']))
section('9 Biểu đồ', 'Reward cửa sổ 100 episode, so sánh alpha/epsilon, độ nhạy và reward tích lũy.',
    definitions('results_io.py', ['plot_curves']))
source = (ROOT / 'code/agent02_experiment.py').read_text(encoding='utf-8')
constants = source[source.index('SEEDS ='):source.index('\n\ndef one_run')].strip()
section('10 Sáu cấu hình và chạy một seed',
    'Baseline, alpha 0.01/0.50, epsilon cố định 0.05/0.30 và giảm giá 5%. '
    'Baseline transfer sang mức giảm 5% được đo riêng với huấn luyện lại.',
    constants + '\n\n' + definitions('agent02_experiment.py', ['one_run']))
section('11 Điều phối toàn bộ bài thực nghiệm',
    'Baseline thêm seed42; sáu cấu hình đều có seeds11/22/33/44/55, tổng31 lượt.',
    definitions('agent02_experiment.py', ['main']))
section('12 Kiểm chứng phép cập nhật và luật',
    'Câu3: target10.5, hiệu TD6.5, Q mới4.65; terminal không bootstrap.',
    'check_agent = QLearningAgent(alpha=.1, gamma=.9, seed=42)\n'
    'check_agent.q[0, 0, 0] = 4\ncheck_agent.q[1, 0] = [5, 2]\n'
    'check_agent.learn((0, 0), 0, 6, (1, 0))\n'
    'assert np.isclose(check_agent.q[0, 0, 0], 4.65)\n'
    'check_agent.q[0, 0, 0] = 4\n'
    'check_agent.learn((0, 0), 0, 6, (1, 0), terminal=True)\n'
    'assert np.isclose(check_agent.q[0, 0, 0], 4.2)\n'
    'assert [RuleBasedAgent().act((d, c)) for d in range(2) for c in range(2)] == [0, 0, 0, 1]\n'
    'print("Q update, terminal target and rule truth table: PASS")')
section('13 Chạy đầy đủ 31 lượt',
    'Ô này huấn luyện và đánh giá thật, không nạp kết quả đã tính từ trước. '
    'Chờ thông báo Completed trước khi chạy các ô phân tích bên dưới.', 'main()')
section('14 Bảng kết quả tổng hợp', 'Số đo do ô phía trên vừa tạo. Không cần file kết quả đi kèm notebook.',
    'summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))\n'
    'table_rows = [["Cấu hình", "Agent", "N", "Reward mean", "SD mẫu", "Tỷ lệ giảm giá"]]\n'
    'for r in summary["aggregate"]:\n'
    '    table_rows.append([r["configuration"], r["strategy"], r["n"], '
    'f"{r[\'mean_reward\']:.4f}", f"{r[\'sample_sd\']:.4f}", '
    'f"{100*r[\'mean_discount_rate\']:.2f}%"])\n'
    'display(HTML("<table>" + "".join("<tr>" + "".join("<td>"+str(x)+"</td>" '
    'for x in row)+"</tr>" for row in table_rows) + "</table>"))')
section('15 Baseline Q table và số hành động', 'Phân biệt policy trên bảng với những trạng thái thật sự được thăm.',
    'baseline = json.loads((OUT / "baseline-seed-42.json").read_text(encoding="utf-8"))\n'
    'print("Q table:\\n", np.array(baseline["q_table"]))\n'
    'print("Greedy policy:", baseline["policy"])\n'
    'print("Training:", baseline["training_stats"])\n'
    'for name in ["rl_evaluation", "rule_evaluation"]:\n'
    '    print(name, {k:v for k,v in baseline[name].items() if k != "episodes"})')
section('16 Kiểm tra toàn bộ kết quả',
    'Đếm đủ lượt/episode/bước, tổng reward và hành động, Q đóng băng và tổng hợp 5 seed.',
    'run_files = sorted(OUT.glob("*-seed-*.json"))\nassert len(run_files) == 31\n'
    'for path in run_files:\n'
    '    run = json.loads(path.read_text(encoding="utf-8"))\n'
    '    assert len(run["training_rows"]) == 5000\n'
    '    for name in ["rl_evaluation", "rule_evaluation"]:\n'
    '        ev = run[name]\n        assert ev["steps"] == 10000\n'
    '        assert all(sum(c) == 10000 for c in ev["action_counts"])\n'
    '        assert ev["total_rewards"] == [sum(e[k] for e in ev["episodes"]) '
    'for k in ["focal_reward", "opponent_reward"]]\n'
    '    assert run["rl_evaluation"]["q_unchanged"]\n'
    'assert all(r["n"] == 5 for r in summary["aggregate"])\n'
    'print("All 31 full runs and 12 summary rows: PASS")')
section('17 Biểu đồ và độ nhạy', 'Các ảnh được nhúng trực tiếp trong notebook để đọc cả khi không có thư mục PNG.',
    'for name in ["baseline", "baseline-cumulative", "learning-rate", "exploration", "robustness"]:\n'
    '    display(Image(filename=str(OUT / (name + ".png"))))\n'
    'print("Frozen baseline transfer at 5% discount:")\n'
    'for row in summary["robustness_transfer"]:\n    print(row)')
cells.append(md('## Giới hạn và kết luận\n\n'
    'Mô hình chuyển đổi minh họa, không phải dữ liệu thị trường thực. '
    'Quan sát thiếu hành động trước của chính agent và thời gian còn lại. '
    'Không đo hai RL cùng học. Tách transfer và retrain; không khẳng định RL luôn hơn luật. '
    'Giảm20% cho biên lợi nhuận3, giảm5% cho biên4.5. '
    'Các số trên được tính trong lần thực thi notebook này.'))
nb = nbf.v4.new_notebook(cells=cells, metadata={
    'kernelspec': {'display_name':'Python 3','language':'python','name':'python3'},
    'language_info': {'name':'python'}, 'standalone': True})
nbf.write(nb, HERE / (STEM + '.ipynb'))
work = Path(tempfile.mkdtemp(prefix='notebook-standalone-', dir=ROOT / 'report/preview'))
assert not list(work.iterdir()), 'Validation requires an empty execution directory'
ksm = KernelSpecManager()
spec = ksm.get_kernel_spec('python3')
spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
ksm.get_kernel_spec = lambda name: spec


class ProgressClient(NotebookClient):
    def process_message(self, msg, *args, **kwargs):
        if msg['msg_type'] == 'stream':
            print(msg['content']['text'], end='', flush=True)
        return super().process_message(msg, *args, **kwargs)


client = ProgressClient(nb, timeout=1800, kernel_name='python3',
    resources={'metadata': {'path':str(work)}})
client.km = client.create_kernel_manager()
client.km.kernel_spec_manager = ksm
client.execute()
nbf.write(nb, HERE / (STEM + '.ipynb'))
body, _ = HTMLExporter().from_notebook_node(nb)
(HERE / (STEM + '.html')).write_text(body, encoding='utf-8')
print('Standalone notebook complete:', len([c for c in nb.cells if c.cell_type=='code']), 'code cells')
