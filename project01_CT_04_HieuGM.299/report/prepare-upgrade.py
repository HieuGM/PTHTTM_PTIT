"""Render bounded controls and derive upgrade tables from recorded verification."""
from pathlib import Path
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load(name):
    return json.loads((ROOT/'results'/name).read_text(encoding='utf-8'))


def block(section, marker, content):
    path = HERE/'sections'/section
    value = path.read_text(encoding='utf-8')
    pattern = f'<!-- {marker}_START -->.*?<!-- {marker}_END -->'
    assert re.search(pattern, value, re.S), marker
    value = re.sub(pattern, lambda _: f'<!-- {marker}_START -->\n\n{content}\n\n<!-- {marker}_END -->', value, flags=re.S)
    path.write_text(value, encoding='utf-8')


def evaluation_table():
    data = load('agent-upgrade-evaluation.json')
    lines = ['Bảng sau đọc từ agent-upgrade-evaluation.json. Đây là phép đo phát triển sau khi '+
        'đã xem lỗi phiên bản đầu (post-hoc); không phải holdout độc lập hoặc kiểm định lâm sàng.', '',
        '| Bộ câu hỏi / phương pháp | Recall@1 | Recall@3 | MRR@3 |', '|---|---:|---:|---:|']
    for key, label in [('id_gold', '22 câu gold ID'), ('document_gold', '8 câu gold tài liệu')]:
        for method in ['baseline_hybrid', 'adaptive']:
            metric = data[key]['summary'][method]
            numbers = [f"{metric[k]:.4f}".replace('.', ',') for k in ['recall_at_1','recall_at_3','mrr_at_3']]
            lines.append('| '+label+' / '+method+' | '+' | '.join(numbers)+' |')
    lines.extend(['', 'Policy đánh giá: '+data['policy_version']+'. '+
        'Bản thử đầu được giữ tại agent-upgrade-evaluation-v1.json. '+
        'Adaptive còn bỏ sót Q21 trong bộ gold ID; phép kiểm đủ bằng chứng có thể từ chối một '+
        'câu hợp lệ về nguồn dữ liệu. Tám gold tài liệu vẫn có những lỗi của baseline. '+
        'Không kết luận nâng cấp làm tăng mọi metric.', '',
        'Ca “Mờ mắt là gì?” minh họa một nhánh bổ sung thật: lượt đầu thiếu hỗ trợ concept, '+
        'lượt sau chuẩn hóa alias thành “nhìn mờ” và lấy được KB05. '+
        'Nếu lượt đầu đã đủ, bộ điều khiển kết thúc ngay; không ép gọi thêm để trình diễn.'])
    block('05-knowledge.md', 'ADAPTIVE_EVAL', '\n'.join(lines))


def evidence_table():
    tests = load('agent-upgrade-pytest.json')
    cases = load('agent-upgrade-cases.json')
    notebook = load('notebook-agent-upgrade-verification.json')
    provider = load('provider-review-verification.json')
    lines = ['Đợt kiểm chứng mã nâng cấp hoàn tất ngày 13/11/2026. '+
        'Các kết quả dưới đây được ghi riêng với đợt bổ sung tài liệu trước đó.', '',
        '| Bằng chứng của mã nâng cấp | Kết quả | Phạm vi |', '|---|---|---|',
        f"| Pytest | {tests['passed']} đạt, {tests.get('failed', 0)} lỗi | Model thật/cache/template và ca lỗi có chủ đích |",
        f"| API minh họa | {cases['passed']}/{cases['case_count']} đạt | Bốn cohort, safety, input sai, retry và từ chối |",
        f"| Notebook | {notebook['benchmark_runs']} fit, {notebook['ml_checks_passed']} ML, {notebook['api_checks_passed']} API, {notebook['upgrade_checks_passed']} kiểm tra nâng cấp | Kernel mới; weights sandbox tách artifact phục vụ |",
        f"| FPT thật | Structured response: {provider['provider_structured_response_received']}; final generation: {provider['final_generation']} | Một câu hỏi công khai, không phải benchmark y khoa |",
        f"| Review cuối của lượt FPT | {provider['final_review_passed']} | Chỉ các điều kiện của bộ kiểm xác định |",
        '| Nguồn công nghệ | technology-map.json | Mỗi tính năng có file/hàm/dòng; phân biệt implemented và executed |', '',
        'Lượt notebook mới ghi riêng môi trường, source/hash và số kiểm tra trong verification. '+
        'Các model Pima/Early được chọn lại trong thư mục sandbox của notebook; '+
        'trọng số phục vụ trong gói nộp và số benchmark lịch sử không bị thay. '+
        'Một lượt full đã dừng khi review phát hiện lỗi xử lý xuống dòng; lượt đó không được tính là hoàn tất.', '',
        'Rà soát độc lập phát hiện bản sửa extractive có thể ghép những mảnh xuống dòng thành một '+
        'phát biểu không đạt kiểm tra. Bản cuối kiểm lại đoạn đã ghép và chuyển sang REFUSAL tin cậy '+
        'nếu candidate sau sửa vẫn bị từ chối; verdict của candidate lỗi được giữ trong metadata. '+
        'Đây là sửa lỗi trong cơ chế kiểm duyệt, không là chứng minh an toàn y tế tổng quát.']
    assert notebook, 'Missing executed notebook verification'
    block('07-verification-deploy.md', 'UPGRADE_EVIDENCE', '\n'.join(lines))


def controls_figure():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set(xlim=(0, 11), ylim=(0, 7)); ax.axis('off')
    columns = [(.25, 'KG/RAG: adaptive retrieval', [
        '1. Retrieve original query', '2. Check anchors + source provenance',
        'Sufficient -> return evidence', 'Weak -> alias rewrite / lexical fallback',
        'At most 3 calls -> evidence or abstain']),
        (5.85, 'Explanation: output review', [
        '1. FPT once or labelled template', '2. Review citations / patterns / lexical support',
        'Pass -> publish answer', 'Fail -> one extractive revision + review',
        'Still fails -> trusted refusal'])]
    for x, title, labels in columns:
        ax.text(x+2.45, 6.55, title, ha='center', fontsize=13, fontweight='bold', color='#173547')
        for i, label in enumerate(labels):
            y = 5.35-i*1.02
            ax.add_patch(FancyBboxPatch((x,y),4.9,.7,boxstyle='round,pad=.05',
                facecolor='#edf5f4' if i!=4 else '#fff1e7',edgecolor='#437c82'))
            ax.text(x+2.45,y+.35,label,ha='center',va='center',fontsize=10.5)
            if i<4:
                ax.annotate('',xy=(x+2.45,y-.23),xytext=(x+2.45,y-.03),arrowprops={'arrowstyle':'->'})
    ax.text(5.5,.25,'Internal controls within seven core roles; structured decisions are returned with each report.',
            ha='center',fontsize=10,color='#173547')
    fig.tight_layout(pad=.3)
    fig.savefig(HERE/'figures/agent-controls.png',dpi=200,bbox_inches='tight')
    plt.close(fig)


def main():
    evaluation_table(); evidence_table(); controls_figure()


if __name__ == '__main__':
    main()
