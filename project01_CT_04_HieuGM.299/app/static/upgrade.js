// Academic inspection tools: render server-provided decisions, never calculate scores here.
const reviewNames = {passed:'Đạt các kiểm tra đã định nghĩa',revised:'Đã sửa sang trích xuất',
  abstained:'Từ chối vì chưa đủ điều kiện',safety_override:'Ưu tiên luật an toàn',error:'Kiểm duyệt gặp lỗi'};

function renderUpgrade(result, target) {
  const r = result.report, box = text('div'), retrieval = r.retrieval || {}, quality = r.quality || {};
  box.append(text('h4', 'Quyết định truy xuất'), text('p',
    `${retrieval.sufficient ? 'Đủ theo tiêu chí kỹ thuật' : 'Chưa đủ / đã bỏ qua'} · ${retrieval.reason || '—'}`, 'muted'));
  const attempts = text('ul');
  (retrieval.attempts || []).forEach(a => attempts.append(text('li',
    `Lượt ${a.attempt}: ${a.method} · ${a.query_strategy} · ${a.supported_count}/${a.candidate_count} đoạn hợp lệ · ${a.reason}`)));
  box.append(attempts, text('p', 'Độ đủ bằng chứng là heuristic để điều khiển truy xuất, không phải xác suất câu trả lời đúng.', 'hint'));
  box.append(text('h4', 'Kiểm duyệt sau khi sinh'), text('p', reviewNames[quality.status] || 'Chưa có kết quả'));
  box.append(text('p', `Lượt sửa: ${quality.revision_count || 0}/${quality.max_revisions ?? 1} · bản nháp đầu ${quality.initial_passed ? 'đạt' : 'chưa đạt / không áp dụng'}`, 'muted'));
  const checks = text('ul');
  (quality.attempts || []).forEach((a,i) => checks.append(text('li',
    `Lần kiểm ${i+1}: ${a.passed ? 'đạt' : 'chưa đạt'} · ${(a.issue_codes || []).join(', ') || 'không phát hiện lỗi trong phạm vi kiểm'}`)));
  box.append(checks, text('p', quality.scope || 'Các kiểm tra này chưa xác thực lâm sàng.', 'hint'));
  const usage = result.feature_usage || {};
  box.append(text('h4', 'Đã dùng trong yêu cầu này'), text('p',
    `DL: ${usage.deep_learning ? 'có' : 'không'} · retrieval: ${usage.retrieval_attempts || 0} lượt · graph: ${usage.graph_backend || 'không dùng'} · FPT đã gọi: ${usage.fpt_called ? 'có' : 'không'} · kết quả: ${usage.final_generation || '—'}`, 'muted'));
  target.append(reportSection('6. Quyết định và kiểm duyệt', box));
}
window.renderUpgrade = renderUpgrade;

window.addEventListener('DOMContentLoaded', async () => {
  try {
    const result = await request('/api/capabilities');
    $('technology-version').textContent = result.system_version;
    result.features.forEach(f => {
      const card = text('article');
      card.append(text('p', f.implemented ? 'ĐÃ TRIỂN KHAI' : 'CHƯA TRIỂN KHAI', 'eyebrow'),
        text('h3', f.name), text('p', f.scope), text('p', `Vai trò: ${f.agent}`, 'muted'));
      if (f.implemented) {
        const details = document.createElement('details'); details.append(text('summary', 'Mã nguồn và cách kiểm tra'),
          text('p', `${f.source.path} → ${f.source.symbol}`, 'muted'), text('p', `Điểm vào: ${f.endpoint}`, 'muted'),
          text('p', `Demo: ${f.demo}`)); card.append(details);
      }
      $('technology-list').append(card);
    });
  } catch (error) { showError($('technology-list'), error); }
});
