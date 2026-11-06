let catalog, dataset = 'cdc';
const $ = id => document.getElementById(id);
const text = (tag, value, cls) => { const e = document.createElement(tag); e.textContent = value ?? ''; if (cls) e.className = cls; return e; };
const names = {cdc:'CDC BRFSS', hospital:'Hospital readmission', pima:'Pima Diabetes', early:'Early-stage Diabetes'};
async function request(url, body) {
  const response = await fetch(url, body ? {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)} : {});
  const result = await response.json();
  if (!response.ok) { const error = Error(result.error?.message || (typeof result.detail === 'string' ? result.detail : 'Dữ liệu chưa hợp lệ. Hãy kiểm tra các trường đã nhập.')); error.result = result; throw error; }
  return result;
}
function linkTo(source) {
  const a = text('a', source.title || source.url);
  try { const u = new URL(source.url); if (u.protocol === 'https:') { a.href = u.href; a.target = '_blank'; a.rel = 'noopener noreferrer'; } } catch (_) {}
  return a;
}
function sourceList(sources) {
  const ul = text('ul', '', 'sources');
  sources.forEach(source => { const li = text('li'); li.append(linkTo(source)); if (source.id) li.append(text('small', ` [${source.id}]${source.page ? ' · trang '+source.page : ''}`)); ul.append(li); });
  return ul;
}
function showTrace(trace, target = $('trace')) {
  target.replaceChildren();
  trace.forEach(m => { const li = text('li'); li.append(text('b', `${m.agent || m.sender} · ${m.status || m.kind}`), text('span', m.detail || `Phiên bản: ${m.model_version || '—'} · ${m.elapsed_ms} ms`)); target.append(li); });
}
function showError(target, error) { target.replaceChildren(text('p', error.message, 'error')); }
document.querySelectorAll('[data-tab]').forEach(button => button.onclick = () => {
  document.querySelectorAll('[data-tab]').forEach(b => b.classList.toggle('active', b === button));
  document.querySelectorAll('.tab').forEach(t => t.hidden = t.id !== 'tab-' + button.dataset.tab);
});
document.querySelectorAll('[data-question]').forEach(b => b.onclick = () => { $('question').value = b.dataset.question; $('question').focus(); });
$('ask').onclick = async () => {
  $('ask').disabled = true; $('chat-output').replaceChildren(text('p', 'Đang truy xuất và tạo giải thích…', 'muted'));
  try {
    const raw = $('glucose').value;
    const result = await request('/api/chat', {question:$('question').value, glucose:raw ? Number(raw) : null, unit:$('unit').value});
    $('chat-output').replaceChildren(text('span', `${result.status} · ${result.generation || 'template'}`, 'badge'), text('div', result.answer, 'answer'), sourceList(result.sources || []));
    showTrace(result.trace);
  } catch (error) { showError($('chat-output'), error); }
  finally { $('ask').disabled = false; }
};
function buildForm() {
  const metadata = catalog.datasets[dataset];
  $('task-description').textContent = metadata.label_semantics || metadata.task;
  $('features').replaceChildren(); $('report-output').replaceChildren();
  for (const spec of metadata.feature_specs) {
    const div = text('div', '', 'field'), label = text('label', spec.label || spec.name), input = document.createElement('input');
    label.htmlFor = 'f-' + spec.name; input.id = label.htmlFor; input.name = spec.name; input.type = 'number'; input.required = true;
    input.min = spec.min; input.max = spec.max; input.step = spec.integer ? 1 : 'any'; input.value = spec.default;
    div.append(label, input, text('small', spec.coding || `Miền nhập: ${spec.min}–${spec.max}`)); $('features').append(div);
  }
}
async function initialize() {
  try {
    catalog = await request('/api/catalog'); const kb = catalog.knowledge;
    $('dataset-count').textContent = Object.keys(catalog.datasets).length;
    $('card-count').textContent = `${kb.documents} tài liệu tải thật · ${kb.cards} thẻ biên soạn`;
    $('system-mode').textContent = `${catalog.llm.configured ? 'FPT Cloud đã cấu hình' : 'Giải thích bằng mẫu'} · ${kb.graph_backend}`;
    Object.keys(catalog.datasets).forEach(key => { const option = text('option', names[key] || key); option.value = key; $('dataset-select').append(option); });
    $('dataset-select').onchange = () => { dataset = $('dataset-select').value; buildForm(); }; buildForm();
    const knowledge = await request('/api/knowledge');
    knowledge.documents.forEach(doc => { const article = text('article'); article.append(text('p', `${doc.type} · ${doc.ingestion === 'downloaded' ? 'Đã tải nội dung' : 'Nguồn tham khảo của thẻ'}`, 'eyebrow'), linkTo(doc)); if (doc.sha256) article.append(text('p', `SHA256: ${doc.sha256.slice(0,16)}…${doc.page_count ? ' · '+doc.page_count+' trang' : ''}`)); $('document-list').append(article); });
    knowledge.cards.forEach(card => { const article = text('article'); article.append(text('p', card.id, 'eyebrow'), text('h3', card.title), text('p', card.text), linkTo({title:card.source_title || 'Tài liệu gốc ↗',url:card.url})); $('knowledge-cards').append(article); });
    await Promise.all([loadBenchmark(), loadGraph()]);
  } catch (error) { showError($('report-output'), error); }
}
window.addEventListener('DOMContentLoaded', initialize);
