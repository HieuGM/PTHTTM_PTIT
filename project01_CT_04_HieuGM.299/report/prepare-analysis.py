"""Derive serving analysis and API walkthrough from recorded evidence, without refitting."""
from pathlib import Path
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def replace_block(section, marker, content):
    path = HERE/'sections'/section
    value = path.read_text(encoding='utf-8')
    pattern = f'<!-- {marker}_START -->.*?<!-- {marker}_END -->'
    replacement = f'<!-- {marker}_START -->\n\n{content}\n\n<!-- {marker}_END -->'
    assert re.search(pattern, value, re.S), marker
    path.write_text(re.sub(pattern, lambda _: replacement, value, flags=re.S), encoding='utf-8')


def decimal(value):
    return f'{value:.4f}'.replace('.', ',')


def serving_analysis():
    table = ['Bảng dưới lấy đúng bốn artifact phục vụ; mỗi hàng là một run, không là mean ba seed.',
        '', '| Cohort / model | TN / FP / FN / TP | Sensitivity | Specificity | F1 |',
        '|---|---|---:|---:|---:|']
    matrices = []
    for dataset in ['cdc', 'hospital', 'pima', 'early']:
        meta = load(f'models/{dataset}/metadata.json')
        if dataset in {'cdc', 'hospital'}:
            metric = load(f'results/{dataset}-training.json')['test']['mlp']
            model = 'MLP3 legacy'
        else:
            model = f"{meta['model_id']} seed {meta['seed']}"
            metric = load(f"results/benchmark/full/{dataset}/{meta['model_id']}-seed{meta['seed']}.json")['test']
        (tn, fp), (fn, tp) = metric['confusion_matrix']
        table.append(f'| {dataset} / {model} | {tn} / {fp} / {fn} / {tp} | '+
            ' | '.join(decimal(metric[k]) for k in ['sensitivity', 'specificity', 'f1'])+' |')
        matrices.append((dataset, metric['confusion_matrix']))
    fig, axes = plt.subplots(1, 4, figsize=(12, 3))
    for ax, (dataset, matrix) in zip(axes, matrices):
        ax.imshow(matrix, cmap='Blues')
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(matrix[i][j]), ha='center', va='center', fontsize=14,
                    color='white' if matrix[i][j] > max(map(max, matrix))*.55 else '#172c3b')
        ax.set(title=dataset.upper(), xticks=[0, 1], yticks=[0, 1], xlabel='Predicted', ylabel='True')
    fig.tight_layout()
    fig.savefig(HERE/'figures/serving-confusion.png', dpi=200)
    plt.close(fig)
    table.extend(['', '![Confusion matrix của bốn serving model; số đếm từ artifact đã lưu](figures/serving-confusion.png)',
        '', 'Nguồn: results/cdc-training.json, hospital-training.json và hai record benchmark '+
        'pima/mlp2-seed42.json, early/resmlp-seed42.json. CDC/Hospital là kết quả legacy; '+
        'không thay bằng run benchmark khác.'])
    replace_block('04-deep-learning.md', 'SERVING_ANALYSIS', '\n'.join(table))


def api_cases():
    evidence = ROOT/'results/agent-upgrade-cases.json'
    if not evidence.exists():
        raise FileNotFoundError('Run scripts/capture-report-cases.py first')
    data = load('results/agent-upgrade-cases.json')
    lines = [f"Lượt chạy cục bộ ghi tại {data['executed_at']}; {data['passed']}/{data['case_count']} ca đạt "+
        'kỳ vọng chức năng. Dữ liệu là giá trị mặc định minh họa theo schema, không là hồ sơ bệnh nhân. '+
        'Mô hình dùng trọng số thật; tri thức dùng SQLite cache và giải thích bằng template. '+
        'Lượt này không gọi FPT hoặc Neo4j ngoài, không đo SLA.', '',
        '| Ca | HTTP | Trạng thái | Message | Generation |', '|---|---:|---|---:|---|']
    for case in data['cases']:
        response = case['response']
        report = response.get('report')
        generation = report['explanation']['generation'] if report else 'không tạo report'
        lines.append(f"| {case['case_id']} | {case['http_status']} | {response['status']} | "+
                     f"{len(response['messages'])} | {generation} |")
    example = next(c for c in data['cases'] if c['case_id'] == 'pima-normal')
    lines.extend(['', '### 6.7.1. Một request Pima xuyên suốt', '',
        'Request sau gửi đến POST /api/report. Các tên trường giữ nguyên để có thể chạy lại:', '',
        '```json', json.dumps(example['synthetic_input'], ensure_ascii=False, indent=2), '```', ''])
    response = example['response']
    report = response['report']
    prediction = report['prediction']
    lines.extend([f"Request_id của lần ghi: `{response['request_id']}`. Score thực là "+
        f"{decimal(prediction['risk_score'])}, ngưỡng validation {decimal(prediction['threshold'])}, "+
        f"nhãn nghiên cứu {prediction['predicted_class']}; phiên bản {prediction['model_version']}. "+
        'Đây là output của vector minh họa, không là xác suất bệnh cá nhân.', '',
        '| Thứ tự / agent | Status | Mốc elapsed_ms | duration_ms riêng |', '|---|---|---:|---:|'])
    for i, message in enumerate(response['messages'], 1):
        lines.append(f"| {i}. {message['agent']} | {message['status']} | {message['elapsed_ms']} | {message['duration_ms']} |")
    lines.extend(['', '### 6.7.2. Evidence, giải thích và cờ review', '',
        'Một số evidence được trả trong đúng request trên:', '',
        '| ID | Document / page | Nguồn |', '|---|---|---|'])
    for source in report['sources'][:3]:
        lines.append(f"| {source['id']} | {source.get('document_id', '')} / "+
            f"{source.get('page') or '-'} | [{source['title']}]({source['url']}) |")
    lines.extend(['', 'Các cờ review: '+', '.join(f['rule_id'] for f in report['review_flags'])+'. '+
        'Trạng thái degraded phản ánh backend cache, không phải suy luận DL thất bại. '+
        'conflicts.status=not_assessed cho biết chưa thực hiện kiểm mâu thuẫn ngữ nghĩa tổng quát. '+
        'clinical_use=False và uncertainty.score_calibrated=False được giữ trong report.', '',
        'File results/agent-upgrade-cases.json lưu toàn bộ input minh họa, response, trace, nguồn, '+
        'hash bốn trọng số và môi trường chạy. Request_id/thời gian ở lần tái chạy sẽ khác; '+
        'cần so sánh hành vi và schema thay vì yêu cầu UUID giống nhau.', '',
        '### 6.7.3. Hai đường rẽ quan trọng', '',
        'Ca missing-feature trả HTTP 422, chỉ có Coordinator → Patient Data → Monitoring. '+
        'Không có message DL và report=null: luồng không tạo dự đoán khi vector chưa hợp lệ.', '',
        'Các ca emergency, medication-boundary và low-glucose dùng safety_rule; KG có status skipped. '+
        'DL đã chạy trước Rule theo thứ tự hiện tại, nhưng score không ghi đè cảnh báo. '+
        'Explanation dùng thông điệp luật mà không gọi LLM. Các ca này minh họa điều phối; '+
        'không là đánh giá độ nhạy/đặc hiệu lâm sàng của bộ luật.'])
    replace_block('06-rules-rl.md', 'API_CASES', '\n'.join(lines))


def workflow_figure():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set(xlim=(0, 11), ylim=(0, 7)); ax.axis('off')
    def box(x, y, w, label, color='#edf5f4'):
        ax.add_patch(FancyBboxPatch((x, y), w, .58, boxstyle='round,pad=.04',
            facecolor=color, edgecolor='#437c82'))
        ax.text(x+w/2, y+.29, label, ha='center', va='center', fontsize=11)
    labels = ['Client: POST /api/report', 'Coordinator: request_id / started',
        'Patient Data: validate schema', 'DL Prediction: real serving weights',
        'Rule: flags / safety priority', 'KG/RAG: adaptive evidence (max 3 calls)',
        'Coordinator: aggregate outputs', 'Explanation: FPT/template + review (max 1 revision)',
        'Monitoring: metadata -> response']
    for i, label in enumerate(labels):
        y = 6.25-i*.71
        box(2.7, y, 5.6, label)
        if i:
            ax.annotate('', xy=(5.5, y+.62), xytext=(5.5, y+.71), arrowprops={'arrowstyle':'->'})
    box(.05, 4.55, 2.2, 'Invalid -> HTTP 422', '#fff1e7')
    box(8.7, 3.84, 2.2, 'DL error -> HTTP 503', '#fff1e7')
    box(.05, 2.55, 2.2, 'Safety -> skip KG', '#fff1e7')
    box(8.7, 2.30, 2.2, 'Cache -> degraded', '#fff1e7')
    for start, end in [((2.7, 5.12), (2.25, 4.84)), ((8.3, 4.41), (8.7, 4.13)),
                       ((2.7, 3.70), (2.25, 2.84)), ((8.3, 2.99), (8.7, 2.59))]:
        ax.annotate('', xy=end, xytext=start, arrowprops={'arrowstyle':'->', 'color':'#986640'})
    ax.text(5.5, .18, 'Early exits also call Monitoring; elapsed_ms is cumulative from request start.',
        ha='center', fontsize=10)
    fig.tight_layout(pad=.2)
    fig.savefig(HERE/'figures/workflow-sequence.png', dpi=200)
    plt.close(fig)


def main():
    serving_analysis(); api_cases(); workflow_figure()


if __name__ == '__main__':
    main()
