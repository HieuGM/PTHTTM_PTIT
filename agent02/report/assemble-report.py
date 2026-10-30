"""Fill report tables directly from the completed full benchmark artifacts."""
from pathlib import Path
import ast
import json
import platform
import importlib.metadata
import textwrap
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / 'results'


def fmt(value, digits=4):
    return f'{value:.{digits}f}'.replace('.', ',')


def mean_sd(values):
    return f'{fmt(np.mean(values))} ± {fmt(np.std(values, ddof=1))}'


def extract(file, name, method=None):
    text = (ROOT / 'code' / file).read_text(encoding='utf-8')
    node = next(x for x in ast.parse(text).body if getattr(x, 'name', '') == name)
    if method:
        node = next(x for x in node.body if getattr(x, 'name', '') == method)
    lines = text.splitlines()[node.lineno-1:node.end_lineno]
    return textwrap.dedent('\n'.join(lines))


def build():
    summary = json.loads((RESULTS / 'summary.json').read_text(encoding='utf-8'))
    runs = [json.loads(f.read_text(encoding='utf-8'))
            for f in RESULTS.glob('*-seed-*.json')]
    assert len(runs) == 31, 'Full experiment suite is required before report assembly'
    baseline = next(r for r in runs if r['name'] == 'baseline' and r['train_seed'] == 42)

    def chosen(name):
        return [r for r in runs if r['name'] == name and r['train_seed'] != 42]

    def row(name, strategy='rl'):
        return next(r for r in summary['aggregate']
                    if r['configuration'] == name and r['strategy'] == strategy)

    def compare(names):
        lines = ['| Cấu hình | Train | SD cuối | Eval mean ± SD | Giảm giá eval |',
                 '|---|---|---|---|---|']
        for name, label in names:
            selected = chosen(name)
            training = np.mean([r['training_stats']['rl_mean_reward'] for r in selected])
            noise = np.mean([r['training_stats']['rl_last1000_std'] for r in selected])
            s = row(name)
            lines.append(f'| {label} | {fmt(training)} | {fmt(noise)} | '
                         f'{fmt(s["mean_reward"])} ± {fmt(s["sample_sd"])} | '
                         f'{fmt(100*s["mean_discount_rate"], 2)}% |')
        rule = row('baseline', 'rule')
        lines.append(f'| Luật đánh giá riêng | Không học | — | '
                     f'{fmt(rule["mean_reward"])} ± {fmt(rule["sample_sd"])} | 0,00% |')
        return '\n'.join(lines)

    q_rows = ['| Trạng thái (d,c) | Q không giảm | Q giảm | Greedy |', '|---|---|---|---|']
    q = baseline['q_table']
    for d in range(2):
        for c in range(2):
            q_rows.append(f'| ({d},{c}) | {fmt(q[d][c][0])} | {fmt(q[d][c][1])} | '
                          f'{np.argmax(q[d][c])} |')
    alpha = [(n, row(n)['mean_reward']) for n in ['alpha-0.01', 'baseline', 'alpha-0.50']]
    epsilon = [(n, row(n)['mean_reward']) for n in ['baseline', 'epsilon-0.05', 'epsilon-0.30']]
    transfers = summary['robustness_transfer']
    robust = ['| Policy và môi trường | Eval mean ± SD | Tỷ lệ giảm giá |', '|---|---|---|']
    for label, values, rates in [
        ('RL baseline tại 20%', [r['rl_evaluation']['mean_rewards'][0] for r in chosen('baseline')],
         [r['rl_evaluation']['discount_rates'][0] for r in chosen('baseline')]),
        ('RL transfer 20% sang 5%', [r['transfer_reward'] for r in transfers],
         [r['transfer_discount_rate'] for r in transfers]),
        ('RL retrain tại 5%', [r['rl_evaluation']['mean_rewards'][0] for r in chosen('discount-0.05')],
         [r['rl_evaluation']['discount_rates'][0] for r in chosen('discount-0.05')]),
        ('Luật tại 5% đánh giá riêng', [r['rule_reward'] for r in transfers], [0]*5),
    ]:
        robust.append(f'| {label} | {mean_sd(values)} | {fmt(100*np.mean(rates),2)}% |')
    base, retrain = row('baseline'), row('discount-0.05')
    difference = retrain['mean_reward'] - np.mean([r['transfer_reward'] for r in transfers])
    mapping = {
        'Q_TABLE': '\n'.join(q_rows),
        'ALPHA_TABLE': compare([('alpha-0.01','alpha 0,01'),('baseline','alpha 0,10'),('alpha-0.50','alpha 0,50')]),
        'EPSILON_TABLE': compare([('baseline','Lịch chuẩn'),('epsilon-0.05','Cố định 0,05'),('epsilon-0.30','Cố định 0,30')]),
        'ROBUSTNESS_TABLE': '\n'.join(robust),
        'ALPHA_DISCUSSION': 'Reward đánh giá lần lượt là ' + '; '.join(
            f'{name}: {fmt(value)}' for name,value in alpha) +
            f'. Alpha 0,50 có SD giữa seed {fmt(row("alpha-0.50")["sample_sd"])} '
            f'so với {fmt(base["sample_sd"])} ở alpha 0,10; mean thấp hơn '
            f'{fmt(base["mean_reward"]-row("alpha-0.50")["mean_reward"])}. '
            'Hai trong năm seed alpha 0,50 chọn giảm giá khi nhu cầu thấp và mất lợi nhuận '
            'so với luật cùng seed. Đây là dấu hiệu nhạy với seed ở cấu hình này, '
            'không chứng minh mọi learning rate lớn đều kém.',
        'EPSILON_DISCUSSION': 'Reward đánh giá ba cấu hình lần lượt là ' + '; '.join(
            f'{name}: {fmt(value)}' for name,value in epsilon) +
            f'. Epsilon cố định 0,30 thấp hơn baseline '
            f'{fmt(base["mean_reward"]-row("epsilon-0.30")["mean_reward"])} reward/bước '
            'trong đánh giá greedy. Tắt exploration sau huấn luyện không bảo đảm sửa được '
            'policy cuối kém: agent vẫn hành động theo Q đã học. Sự khác biệt reward '
            'training bao gồm chi phí thử hành động và phản ứng của đối thủ.',
        'ROBUSTNESS_DISCUSSION': f'Ở mức giảm 5%, RL huấn luyện lại đạt '
            f'{fmt(retrain["mean_reward"])} ± {fmt(retrain["sample_sd"])}. '
            f'Chênh lệch trung bình so với policy baseline chuyển sang cùng môi trường là '
            f'{fmt(difference)} reward/bước. Đây là độ nhạy đã đo với thay đổi reward margin, '
            'không phải bằng chứng agent baseline tự thích nghi sau khi đóng băng.',
        'CONCLUSION': f'Ở giảm giá 20%, RL baseline và luật đánh giá riêng đều đạt '
            f'{fmt(base["mean_reward"])} ± {fmt(base["sample_sd"])} reward/bước trên 5 seed. '
            f'Khi giảm giá 5% và huấn luyện lại, RL đạt {fmt(retrain["mean_reward"])} ± '
            f'{fmt(retrain["sample_sd"])}. Vì vậy việc chọn hành động phụ thuộc mạnh vào '
            'biên lợi nhuận và hành vi đối thủ; cần kiểm tra cả thay đổi mô hình lẫn quy trình đo.',
        'ACT_CODE': extract('reference_core.py', 'QLearningAgent', 'act'),
        'LEARN_CODE': extract('reference_core.py', 'QLearningAgent', 'learn'),
        'RULE_CODE': extract('reference_core.py', 'RuleBasedAgent', 'act'),
        'TAPE_CODE': extract('evaluation.py', 'make_tape'),
        'PYTHON_VERSION': platform.python_version(),
        'NUMPY_VERSION': np.__version__,
    }
    source = (ROOT / 'code/reference_core.py').read_text(encoding='utf-8').splitlines()
    first = next(i for i, line in enumerate(source) if line.strip().startswith('conversion ='))
    last = next(i for i in range(first,len(source)) if 'rewards.append' in source[i])
    mapping['REWARD_CODE'] = textwrap.dedent('\n'.join(source[first:last+1]))
    sections = []
    for path in sorted((HERE / 'sections').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        for key, value in mapping.items():
            text = text.replace('{{'+key+'}}', value)
        assert '{{' not in text, path
        sections.append(text.strip())
    (HERE / 'agent02_CT_04_hieugm.md').write_text('\n\n<!-- pagebreak -->\n\n'.join(sections)+'\n',encoding='utf-8')
    packages = ['numpy','matplotlib','nbformat','nbclient','nbconvert','ipykernel','reportlab','PyMuPDF']
    environment = {'python':platform.python_version(), 'platform':platform.platform(),
                   'packages':{p:importlib.metadata.version(p) for p in packages}}
    (RESULTS / 'environment.json').write_text(json.dumps(environment, indent=2),encoding='utf-8')
    print('Assembled', len(sections), 'report sections from', len(runs), 'full runs')


if __name__ == '__main__':
    build()
