"""Verify source bytes, actual Neo4j/cache parity and untuned retrieval results."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.knowledge.ingestion import extract_pages, clean_text
from app.knowledge.retrieval import KnowledgeBase
from app.knowledge.store import cached_evidence
from app.knowledge.generation import validate_generated


def retrieval_metrics(kb, queries, method, document_gold=False):
    rows = []
    for query in queries:
        hits = kb.retrieve(query['question'], k=3, method=method)
        gold = set(query['expected_document_ids'] if document_gold else query['expected_ids'])
        field = 'document_id' if document_gold else 'id'
        rank = next((i+1 for i, hit in enumerate(hits) if hit[field] in gold), None)
        assert all(h['id'] in kb.source_index and h['url'].startswith('https://') for h in hits)
        rows.append({**query, 'retrieved_ids': [h['id'] for h in hits],
            'retrieved_document_ids': [h['document_id'] for h in hits],
            'scores': [h['score'] for h in hits], 'first_relevant_rank': rank})
    scored = [r for r in rows if r.get('answerable', True)]
    return {'recall_at_1': sum(r['first_relevant_rank'] == 1 for r in scored)/len(scored),
        'recall_at_3': sum(r['first_relevant_rank'] is not None for r in scored)/len(scored),
        'mrr_at_3': sum(1/r['first_relevant_rank'] if r['first_relevant_rank'] else 0 for r in scored)/len(scored),
        'queries': rows}


def verify_sources(corpus, cache):
    checks = []
    for document in corpus['documents']:
        if document['ingestion'] != 'downloaded':
            continue
        raw = (cache/(document['id']+('.pdf' if document['type'] == 'pdf' else '.html'))).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == document['sha256'], document['id']
        pages = {page: clean_text(text) for page, text in extract_pages(raw, document['type'])}
        for chunk in corpus['chunks']:
            if chunk['document_id'] == document['id'] and chunk['source_type'] != 'curated_card':
                assert chunk['text'] in pages[chunk['page']], chunk['id']
                assert hashlib.sha256(chunk['text'].encode()).hexdigest() == chunk['text_sha256']
        checks.append('source/page/hash:'+document['id'])
    index = {item['id']: item for item in corpus['chunks']}
    for relation in corpus['graph']['relations']:
        assert relation['evidence_quote'] == index[relation['evidence_chunk_id']]['text']
    checks.append('all clinical relations point to exact source passages')
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, default=ROOT/'data/documents/raw')
    parser.add_argument('--require-neo4j', action='store_true')
    args = parser.parse_args()
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env', override=False)
    corpus_path = ROOT/'app/knowledge/corpus.json'
    corpus = json.loads(corpus_path.read_text(encoding='utf-8'))
    checks = verify_sources(corpus, args.cache)
    previous = os.environ.get('APP_DATA_DIR')
    with tempfile.TemporaryDirectory(prefix='diacare-kb-verification-') as directory:
        os.environ['APP_DATA_DIR'] = directory
        kb = KnowledgeBase(ROOT)
        try:
            if args.require_neo4j:
                assert kb.neo4j.backend == 'neo4j', kb.neo4j.status
            counts = None
            if kb.neo4j.backend == 'neo4j':
                with kb.neo4j.driver.session(database=kb.neo4j.database, default_access_mode='READ') as session:
                    counts = dict(session.run('MATCH (n) WITH count(n) AS nodes '
                        'OPTIONAL MATCH ()-[r]->() RETURN nodes,count(r) AS edges').single())
                assert counts['nodes'] == len(corpus['documents'])+len(corpus['chunks'])+len(corpus['graph']['concepts'])
                for concepts in [['type2'], ['a1c'], ['type1', 'insulin'], ['symptoms']]:
                    actual = kb.graph_evidence(concepts)
                    cached = cached_evidence(kb.db_path, concepts, 150)
                    assert actual['backend'] == 'neo4j'
                    assert set(actual['chunk_ids']) == set(cached['chunk_ids'])
                    assert {r['id'] for r in actual['relations']} == {r['id'] for r in cached['relations']}
                checks.append('actual Neo4j counts and four query groups match SQLite evidence cache')
            queries = json.loads((ROOT/'app/knowledge/evaluation-questions.json').read_text(encoding='utf-8'))
            source_queries = json.loads((ROOT/'app/knowledge/source-check-questions.json').read_text(encoding='utf-8'))
            methods = ['lexical', 'semantic', 'hybrid_graph']
            comparison = {m: retrieval_metrics(kb, queries, m) for m in methods}
            source_comparison = {m: retrieval_metrics(kb, source_queries['queries'], m, True) for m in methods}
            fixture = json.dumps({'answer': 'Dữ liệu kiểm parser. [KB08]', 'citation_ids': ['KB08']})
            validate_generated(fixture, [kb.source_index['KB08']])
            try:
                validate_generated(fixture.replace('KB08', 'INVENTED'), [kb.source_index['KB08']])
                raise AssertionError('unknown citation accepted')
            except ValueError:
                pass
            checks.append('citation parser valid/invalid fixtures; not an LLM network simulation')
            result = {'status': 'passed', 'verified_at': datetime.now(timezone.utc).isoformat(),
                'corpus_sha256': hashlib.sha256(corpus_path.read_bytes()).hexdigest(),
                'inventory': kb.inventory(), 'neo4j_counts': counts, 'checks': checks,
                'retrieval_comparison': comparison, 'source_check_comparison': source_comparison,
                'legacy_scope': 'Original 30 development queries, 22 answerable; strict original authored-card gold. Relevant downloaded chunks are not automatically gold.',
                'source_check_scope': source_queries['scope'],
                'fpt_live_generation_tested': False,
                'limitations': 'Recall measures named evidence retrieval, not clinical correctness. Citation ID validity is not factual entailment. No tuning on eight new source checks.'}
            (ROOT/'results/knowledge-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({'status': result['status'], 'inventory': result['inventory'],
                'neo4j_counts': counts, 'retrieval': {m: {k: v for k, v in r.items() if k != 'queries'}
                    for m, r in comparison.items()}, 'source_checks': {m: {k: v for k, v in r.items() if k != 'queries'}
                    for m, r in source_comparison.items()}}, ensure_ascii=False))
        finally:
            kb.close()
            if previous is None:
                os.environ.pop('APP_DATA_DIR', None)
            else:
                os.environ['APP_DATA_DIR'] = previous


if __name__ == '__main__':
    main()
