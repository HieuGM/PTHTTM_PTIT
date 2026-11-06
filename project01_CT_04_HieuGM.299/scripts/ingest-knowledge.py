"""Fetch real HTML/PDF and build evidence cache + Neo4j initialization file."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.knowledge.ingestion import ingest_sources, add_curated_cards
from app.knowledge.graph_builder import build_graph, cypher_seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, default=ROOT/'data/documents/raw')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    documents, chunks, failures = ingest_sources(ROOT, args.cache, args.refresh)
    if not any(item['type'] == 'pdf' for item in documents):
        raise RuntimeError('No genuine PDF ingested; cannot claim PDF pipeline completed')
    if len(documents) < 3:
        raise RuntimeError('Too few downloaded primary documents')
    add_curated_cards(ROOT, documents, chunks)
    corpus = {'version': 'diacare-kg-rag-2.0', 'generated_at': datetime.now(timezone.utc).isoformat(),
        'documents': documents, 'chunks': chunks, 'graph': build_graph(ROOT, documents, chunks),
        'ingestion_failures': failures, 'evidence_policy': 'Downloaded page text or explicitly authored source-linked card; no synthetic documents.'}
    target = ROOT/'app/knowledge/corpus.json'
    target.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT/'DB_diabet.cypher').write_text(cypher_seed(corpus), encoding='utf-8')
    result = {'corpus_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'ingested_documents': [d for d in documents if d['ingestion'] == 'downloaded'],
        'reference_only_documents': sum(d['ingestion'] != 'downloaded' for d in documents),
        'chunks': len(chunks), 'concepts': len(corpus['graph']['concepts']),
        'mentions': len(corpus['graph']['mentions']), 'medical_relations': len(corpus['graph']['relations']),
        'failures': failures, 'raw_cache_distributed': False}
    (ROOT/'results/knowledge-ingestion.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'ingested_documents'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
