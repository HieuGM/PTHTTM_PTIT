"""Inspect provenance, optionally refresh documents/import actual Neo4j, export Cypher."""
from datetime import datetime, timezone
from app.knowledge.ingestion import ingest_sources, add_curated_cards
from app.knowledge.graph_builder import build_graph, cypher_seed
from app.knowledge.neo4j_backend import Neo4jGraph
from app.knowledge.retrieval import KnowledgeBase

if REFRESH_WEB:
    documents, chunks, failures = ingest_sources(ROOT, ROOT/'data/documents/raw', refresh=True)
    if not any(item['type'] == 'pdf' for item in documents):
        raise RuntimeError('Chưa tải được PDF thật; xem lỗi nguồn trước khi tiếp tục.')
    add_curated_cards(ROOT, documents, chunks)
    CORPUS = {'version':'diacare-notebook-refreshed-2.0',
        'generated_at':datetime.now(timezone.utc).isoformat(),
        'documents':documents, 'chunks':chunks, 'graph':build_graph(ROOT, documents, chunks),
        'ingestion_failures':failures, 'evidence_policy':'Actual downloads or explicit curated cards.'}
    (ROOT/'app/knowledge/corpus.json').write_text(json.dumps(CORPUS, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT/'DB_diabet.cypher').write_text(cypher_seed(CORPUS), encoding='utf-8')
document_table = pd.DataFrame(CORPUS['documents'])
display(document_table[[c for c in ['id','title','url','ingestion','sha256','page_count'] if c in document_table]])
display({'downloaded':sum(d['ingestion']=='downloaded' for d in CORPUS['documents']),
    'reference_only':sum(d['ingestion']!='downloaded' for d in CORPUS['documents']),
    'chunks':len(CORPUS['chunks']), 'concepts':len(CORPUS['graph']['concepts']),
    'clinical_relations':len(CORPUS['graph']['relations']),
    'ingestion_failures':CORPUS.get('ingestion_failures', [])})

graph = Neo4jGraph()
try:
    if INITIALIZE_NEO4J:
        counts = graph.initialize(CORPUS)
        live_evidence = graph.evidence(['a1c','type2'])
        display({'backend':graph.backend, 'counts':counts,
                 'actual_query_chunks':len(live_evidence['chunk_ids'])})
    else:
        display({'graph_backend':graph.backend, 'connection_status':graph.status,
                 'initialization':'skipped; set INITIALIZE_NEO4J=True only for dedicated database'})
finally:
    graph.close()

