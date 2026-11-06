function reportSection(title, content) {
  const section = text('section', '', 'report-section'); section.append(text('h3', title));
  section.append(typeof content === 'string' ? text('p', content) : content); return section;
}
function renderReport(result) {
  const target = $('report-output'); target.replaceChildren(text('p', `${result.status} · mã ${result.request_id}`, 'muted'));
  showTrace(result.messages || result.trace || [], $('report-trace'));
  const r = result.report; if (!r) { target.append(text('p', result.error?.message || 'Chưa tạo được báo cáo.', 'error')); return; }
  const p = r.prediction, box = text('div');
  box.append(text('div', Number(p.risk_score).toFixed(3), 'score'), text('p', `Điểm mô hình · ngưỡng validation ${Number(p.threshold).toFixed(3)} · nhãn ${p.predicted_class}`), text('p', p.label_semantics || p.task, 'muted'), text('small', `Phiên bản ${p.model_version} · ${p.artifact_reused ? 'tái sử dụng trọng số gốc' : 'mô hình chọn theo validation'}`));
  target.append(reportSection('1. Dự đoán mô hình nghiên cứu', box));
  const rules = text('ul'); (r.rule_results.flags || []).forEach(flag => rules.append(text('li', `${flag.rule_id}: ${flag.reason}`)));
  if (!rules.childNodes.length) rules.append(text('li', 'Không có quy tắc cảnh báo được kích hoạt; điều này không xác nhận an toàn y khoa.'));
  target.append(reportSection('2. Kết quả quy tắc', rules));
  const explanation = text('div'); explanation.append(text('span', `${r.explanation.generation} · ${r.explanation.status}`, 'badge'), text('div', r.explanation.answer, 'answer'));
  target.append(reportSection('3. Giải thích có bằng chứng', explanation), reportSection('4. Nguồn truy xuất', sourceList(r.sources)));
  const limits = text('ul'); r.limitations.forEach(item => limits.append(text('li', item)));
  limits.append(text('li', r.uncertainty.interpretation), text('li', r.conflicts.limitation));
  target.append(reportSection('5. Bất định và giới hạn', limits));
}
$('report-form').onsubmit = async event => {
  event.preventDefault(); $('create-report').disabled = true;
  $('report-output').replaceChildren(text('p', 'Các Agent đang phối hợp tạo báo cáo…', 'muted'));
  try {
    const features = Object.fromEntries([...$('features').querySelectorAll('input')].map(i => [i.name, Number(i.value)]));
    const raw = $('report-glucose').value;
    renderReport(await request('/api/report', {dataset, features, question:$('report-question').value, glucose:raw ? Number(raw) : null, unit:$('report-unit').value}));
  } catch (error) { if (error.result?.messages) renderReport(error.result); else showError($('report-output'), error); }
  finally { $('create-report').disabled = false; }
};
