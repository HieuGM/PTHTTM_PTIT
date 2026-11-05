let catalog, dataset = 'cdc';
const $ = id => document.getElementById(id);
const text = (tag, value, cls) => { const e = document.createElement(tag); e.textContent = value; if (cls) e.className = cls; return e; };
async function request(url, body) {
  const response = await fetch(url, body ? {method:'POST', headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : {});
  const result = await response.json();
  if (!response.ok) throw Error(typeof result.detail === 'string' ? result.detail : 'Dữ liệu chưa hợp lệ. Hãy kiểm tra các trường đã nhập.');
  return result;
}
document.querySelectorAll('[data-tab]').forEach(button => button.onclick = () => {
  document.querySelectorAll('[data-tab]').forEach(b => b.classList.toggle('active', b === button));
  document.querySelectorAll('.tab').forEach(t => t.hidden = t.id !== 'tab-' + button.dataset.tab);
});
document.querySelectorAll('[data-question]').forEach(b => b.onclick = () => { $('question').value = b.dataset.question; $('question').focus(); });
function showTrace(trace, target = $('trace')) {
  target.replaceChildren();
  trace.forEach(message => { const li = document.createElement('li'); li.append(text('b', `${message.sender} → ${message.receiver}`), text('span', message.detail)); target.append(li); });
}
function showError(target, error) { target.replaceChildren(text('p', error.message, 'error')); }
$('ask').onclick = async () => {
  const button = $('ask'); button.disabled = true;
  $('chat-output').replaceChildren(text('p', 'Các Agent đang tìm kiếm bằng chứng…', 'muted'));
  try {
    const raw = $('glucose').value;
    const result = await request('/api/chat', {question:$('question').value, glucose:raw ? Number(raw) : null, unit:$('unit').value});
    const output = $('chat-output'); output.replaceChildren();
    const labels = {grounded:'Có bằng chứng', insufficient_evidence:'Chưa đủ bằng chứng', emergency:'Cần hỗ trợ khẩn cấp', urgent:'Cảnh báo cần chú ý', boundary:'Ngoài phạm vi hỗ trợ'};
    output.append(text('span', labels[result.status] || result.status, 'status ' + result.status), text('div', result.answer, 'answer'));
    if (result.sources.length) {
      const ul = document.createElement('ul'); ul.className = 'sources';
      result.sources.forEach(source => { const li = document.createElement('li'); const a = text('a', source.title); a.href = source.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; li.append(a); ul.append(li); }); output.append(ul);
    }
    showTrace(result.trace);
  } catch (error) { showError($('chat-output'), error); }
  finally { button.disabled = false; }
};
function buildForm() {
  const metadata = catalog.datasets[dataset];
  $('task-description').textContent = metadata.label_semantics || metadata.task || (dataset === 'cdc' ? 'Phân loại nhãn khảo sát tiền đái tháo đường hoặc đái tháo đường đã được báo cáo.' : 'Phân loại tái nhập viện trong 30 ngày sau một lượt điều trị nội trú.');
  $('features').replaceChildren(); $('predict-output').replaceChildren();
  for (const spec of metadata.feature_specs) {
    const div = document.createElement('div'); div.className = 'field';
    const label = text('label', spec.label || spec.name); label.htmlFor = 'f-' + spec.name;
    const input = document.createElement('input'); input.id = 'f-' + spec.name; input.name = spec.name; input.type = 'number'; input.required = true;
    input.min = spec.min; input.max = spec.max; input.step = spec.integer ? 1 : 'any'; input.value = spec.default;
    div.append(label, input, text('small', spec.coding || `Miền nhập: ${spec.min}–${spec.max}`)); $('features').append(div);
  }
}
document.querySelectorAll('[data-dataset]').forEach(button => button.onclick = () => { dataset = button.dataset.dataset; document.querySelectorAll('[data-dataset]').forEach(b => b.classList.toggle('active', b === button)); buildForm(); });
$('feature-form').onsubmit = async event => {
  event.preventDefault(); $('predict').disabled = true;
  try {
    const features = Object.fromEntries([...new FormData(event.target)].map(([k,v]) => [k,Number(v)]));
    const result = await request('/api/predict', {dataset, features});
    const output = $('predict-output'); output.replaceChildren(text('div', result.risk_score.toFixed(3), 'score'), text('b', 'Điểm mô hình nghiên cứu'));
    output.append(text('p', `Ngưỡng chọn trên validation: ${Number(result.threshold).toFixed(3)} · Nhãn dự đoán: ${result.predicted_class}`, 'muted'), text('p', result.label_semantics || result.task, 'muted'), text('p','Điểm này là đầu ra sigmoid của MLP, chưa được xác thực hoặc hiệu chuẩn cho quyết định lâm sàng tại Việt Nam. Hai bộ dữ liệu có nhiệm vụ khác nhau, nên không so sánh điểm giữa hai mô hình.', 'hint'));
    const ol = document.createElement('ol'); showTrace(result.trace, ol); output.append(ol);
  } catch (error) { showError($('predict-output'), error); }
  finally { $('predict').disabled = false; }
};
async function initialize() {
  try {
    catalog = await request('/api/catalog'); $('card-count').textContent = catalog.knowledge.cards; buildForm();
    const knowledge = await request('/api/knowledge');
    knowledge.cards.forEach(card => { const article = document.createElement('article'); const link = text('a', (card.source_title || 'Tài liệu gốc') + ' ↗'); link.href = card.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; article.append(text('p', card.id, 'eyebrow'), text('h3',card.title), text('p',card.text),link); $('knowledge-cards').append(article); });
  } catch (error) { showError($('chat-output'), error); }
}
initialize();
