let benchmarkData;
const number = (value, digits=3) => Number(value).toFixed(digits);
function renderBenchmark() {
  const key = $('benchmark-dataset').value;
  $('benchmark-description').textContent = catalog.datasets[key].label_semantics || catalog.datasets[key].task;
  const table = text('table'), head = text('tr');
  ['Mô hình','ROC-AUC','AP','F1','Sensitivity','Specificity','Brier ↓'].forEach(v => head.append(text('th', v)));
  const thead = text('thead'); thead.append(head); table.append(thead); const body = text('tbody');
  benchmarkData.summary.filter(r => r.dataset === key).forEach(row => {
    const tr = text('tr'); tr.append(text('td', row.model_name));
    ['roc_auc','average_precision','f1','sensitivity','specificity','brier'].forEach(metric => tr.append(text('td', `${number(row[metric+'_mean'])} ± ${number(row[metric+'_std'])}`)));
    body.append(tr);
  }); table.append(body); $('benchmark-table').replaceChildren(table);
  $('benchmark-detail').textContent = 'Mean ± SD trên 3 seed mô hình, cùng split. SD bằng 0 có thể xảy ra với thuật toán xác định; đây không phải khoảng tin cậy. Ngưỡng F1 và checkpoint chỉ chọn trên validation.';
}
async function loadBenchmark() {
  benchmarkData = await request('/api/benchmark');
  if (!benchmarkData.summary) { $('benchmark-table').textContent = 'Chưa có kết quả thực nghiệm.'; return; }
  const rows = benchmarkData.summary;
  $('model-count').textContent = new Set(rows.map(r => r.model_id)).size;
  $('run-count').textContent = benchmarkData.run_count ?? benchmarkData.runs?.length ?? 0;
  [...new Set(rows.map(r => r.dataset))].forEach(key => { const opt = text('option', names[key] || key); opt.value = key; $('benchmark-dataset').append(opt); });
  $('benchmark-dataset').onchange = renderBenchmark; renderBenchmark();
}
async function loadGraph() {
  const graph = await request('/api/graph');
  $('graph-backend').textContent = graph.backend || graph.graph_backend || catalog.knowledge.graph_backend;
  const nodes = graph.nodes || graph.concepts || [], edges = graph.edges || graph.relations || [];
  $('graph-stats').textContent = `${nodes.length} thực thể · ${edges.length} quan hệ có nguồn · MENTIONS được thống kê riêng trong kho tri thức.`;
  const svg = $('knowledge-graph'), ns = 'http://www.w3.org/2000/svg', positions = {};
  const make = (tag, attrs) => { const e = document.createElementNS(ns, tag); Object.entries(attrs).forEach(([k,v]) => e.setAttribute(k,v)); return e; };
  nodes.forEach((node,i) => { const a = i*2*Math.PI/nodes.length; positions[node.id] = {x:500+330*Math.cos(a),y:310+240*Math.sin(a)}; });
  edges.forEach(edge => { const a=positions[edge.source], b=positions[edge.target]; if (!a || !b) return; const line=make('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:'#b6cac3','stroke-width':2}); const title=make('title',{}); title.textContent=edge.predicate; line.append(title); svg.append(line); });
  nodes.forEach(node => { const p=positions[node.id],g=make('g',{}); g.append(make('circle',{cx:p.x,cy:p.y,r:7,fill:'#17735b'})); const label=make('text',{x:p.x+(p.x<500?-12:12),y:p.y+4,'text-anchor':p.x<500?'end':'start',fill:'#173f34','font-size':11}); label.textContent=node.label || node.name || node.id; g.append(label); svg.append(g); });
  const list = text('ul', '', 'relation-list'); edges.forEach(edge => { const li=text('li'); li.append(text('b', `${edge.source} → ${edge.predicate} → ${edge.target}`)); li.append(text('span', ` · ${edge.evidence_chunk_id || ''}${edge.page ? ' · trang '+edge.page : ''} `)); if (edge.url) li.append(linkTo({title:'Xem nguồn ↗',url:edge.url})); list.append(li); });
  $('graph-relations').replaceChildren(list);
}
