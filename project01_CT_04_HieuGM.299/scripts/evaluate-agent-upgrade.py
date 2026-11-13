"""Post-hoc development comparison; preserve the initial v2.1 measurements."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from importlib.metadata import version
import hashlib
import json
import os
import platform
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for name in ('FPT_API_KEY', 'NEO4J_URI', 'NEO4J_PASSWORD', 'AUDIT_LOG_PATH'):
    os.environ[name] = ''
os.environ['OMP_NUM_THREADS'] = '2'
from threadpoolctl import threadpool_limits
from app.agents.rules import check
from app.knowledge.retrieval import KnowledgeBase
from app.knowledge.adaptive import AdaptiveRetrieval


def digest(relative):
    return hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()


def measure(kb, question, gold, field, adaptive):
    started = time.perf_counter()
    if adaptive:
        result = AdaptiveRetrieval(kb).run(question)
        hits, policy = result['evidence'], result['retrieval']
    else:
        hits = kb.retrieve(question, k=4, method='hybrid_graph')
        policy = None
    duration = (time.perf_counter()-started)*1000
    rank = next((i+1 for i, hit in enumerate(hits[:3]) if hit.get(field) in gold), None)
    assert all(h['id'] in kb.source_index and h['url'] == kb.source_index[h['id']]['url']
               and h['text'] == kb.source_index[h['id']]['text'] for h in hits)
    calls = len(policy['attempts']) if policy else 1
    assert calls <= 3 and len(hits) <= 4
    return {'retrieved_ids': [h['id'] for h in hits],
        'retrieved_document_ids': [h.get('document_id') for h in hits],
        'scores': [h['score'] for h in hits], 'first_relevant_rank_at_3': rank,
        'reciprocal_rank_at_3': 1/rank if rank else 0,
        'retrieval_abstained': not bool(hits), 'retrieve_calls': calls,
        'duration_ms': round(duration, 3), 'policy': policy}


def case(kb, item, document_gold=False):
    field = 'document_id' if document_gold else 'id'
    key = 'expected_document_ids' if document_gold else 'expected_ids'
    return {**item, 'baseline_hybrid': measure(kb, item['question'], set(item[key]), field, False),
            'adaptive': measure(kb, item['question'], set(item[key]), field, True)}


def summarize(rows, method):
    n = len(rows)
    ranks = [row[method]['first_relevant_rank_at_3'] for row in rows]
    return {'query_count': n, 'recall_at_1': sum(r == 1 for r in ranks)/n,
        'recall_at_3': sum(r is not None for r in ranks)/n,
        'mrr_at_3': sum(1/r if r else 0 for r in ranks)/n,
        'missed_gold_at_3': [row['id'] for row in rows
                             if row[method]['first_relevant_rank_at_3'] is None],
        'abstained_ids': [row['id'] for row in rows if row[method]['retrieval_abstained']],
        'retrieve_calls_total': sum(row[method]['retrieve_calls'] for row in rows),
        'max_calls_per_query': max(row[method]['retrieve_calls'] for row in rows),
        'total_query_duration_ms': round(sum(row[method]['duration_ms'] for row in rows), 3)}


def negatives(kb, items):
    rows = [case(kb, item) for item in items]
    for row in rows:
        rule = check(row['question'])
        row['rule_level'] = rule['level'] if rule else None
        for method in ('baseline_hybrid', 'adaptive'):
            row[method]['rule_gated_refused'] = bool(rule) or row[method]['retrieval_abstained']
    summary = {}
    for method in ('baseline_hybrid', 'adaptive'):
        outside = [r for r in rows if r['kind'] == 'out_of_scope']
        summary[method] = {'negative_count': len(rows),
            'retrieval_abstained': sum(r[method]['retrieval_abstained'] for r in rows),
            'out_of_scope_count': len(outside),
            'out_of_scope_retrieval_abstained': sum(r[method]['retrieval_abstained'] for r in outside),
            'rule_gated_refused': sum(r[method]['rule_gated_refused'] for r in rows),
            'rule_gated_not_refused_ids': [r['id'] for r in rows if not r[method]['rule_gated_refused']]}
    return {'summary': summary, 'cases': rows,
        'scope': 'Raw retrieval abstention is separate from refusal. Rule-gated counts use '
                 'check(question) OR empty retrieval, not the full API or generation workflow. '
                 'Six negatives concern dosing, unsupported specificity, injection or live information.'}


def main():
    preserved = ['results/knowledge-verification.json', 'results/system-evaluation.json',
                 'results/benchmark/full/benchmark-results.json',
                 'results/agent-upgrade-evaluation-v1.json']
    old_hashes = {p: digest(p) for p in preserved}
    question_path = 'app/knowledge/evaluation-questions.json'
    document_path = 'app/knowledge/source-check-questions.json'
    questions = json.loads((ROOT/question_path).read_text(encoding='utf-8'))
    documents = json.loads((ROOT/document_path).read_text(encoding='utf-8'))
    demos = [
        {'id': 'D01', 'question': 'HbA1c phản ánh điều gì?', 'expected_ids': ['KB08']},
        {'id': 'D02', 'question': 'Xét nghiệm đường ba tháng phản ánh điều gì?', 'expected_ids': ['KB08']},
        {'id': 'D03', 'question': 'Mờ mắt là gì?', 'expected_ids': ['KB05']},
        {'id': 'D04', 'question': 'Tập thể dục giúp người bị đái đường như thế nào?', 'expected_ids': []},
        {'id': 'D05', 'question': 'Ai vô địch World Cup bóng đá?', 'expected_ids': []}]
    with tempfile.TemporaryDirectory(prefix='diacare-agent-evaluation-') as directory:
        os.environ['APP_DATA_DIR'] = directory
        with threadpool_limits(limits=2):
            started = time.perf_counter()
            kb = KnowledgeBase(ROOT)
            initialization_ms = (time.perf_counter()-started)*1000
            try:
                assert kb.neo4j.driver is None
                ids = [case(kb, q) for q in questions if q['answerable']]
                docs = [case(kb, q, True) for q in documents['queries']]
                negative = negatives(kb, [q for q in questions if not q['answerable']])
                demo_rows = [case(kb, q) for q in demos]
                inventory = kb.inventory()
            finally:
                kb.close()
    assert old_hashes == {p: digest(p) for p in preserved}
    methods = ('baseline_hybrid', 'adaptive')
    source_paths = [question_path, document_path, 'app/knowledge/corpus.json',
                    'app/knowledge/adaptive.py', 'app/knowledge/retrieval.py', 'app/agents/rules.py',
                    'scripts/evaluate-agent-upgrade.py']
    result = {'executed_at_vietnam': datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
        'scope': 'Single-pass post-hoc development comparison after reviewing v2.1 failures. '
                 'This reuses the same development questions; no holdout claim. No FPT, Neo4j network, model training, '
                 'clinical validation, full API evaluation or dotenv loading.',
        'environment': {'python': platform.python_version(),
            **{p: version(p) for p in ('numpy', 'scikit-learn', 'threadpoolctl')}},
        'source_sha256': {p: digest(p) for p in source_paths},
        'preserved_historical_sha256': old_hashes, 'inventory': inventory,
        'policy_version': AdaptiveRetrieval.version, 'index_initialization_ms': round(initialization_ms, 3),
        'metric_definition': 'First matching named gold among top 1/top 3 ranked chunks. '
            'Document gold uses each chunk document_id without document deduplication. '
            'Missing or abstained evidence scores zero. This measures named evidence retrieval, not truth.',
        'timing_scope': 'Same in-memory index/cache; baseline then adaptive per question; '
            'single measured pass, two BLAS threads. Includes adaptive checks; excludes index creation. '
            'These durations are not production latency/SLA or a repeated performance benchmark.',
        'development_revision': {'previous_artifact': 'results/agent-upgrade-evaluation-v1.json',
            'previous_policy': 'adaptive-evidence-2.1', 'current_policy': AdaptiveRetrieval.version,
            'changes': 'Removed forced rewrite when evidence is already supported; generic curated-topic '
                'domain interpretation and fasting-glucose aliases. Revision informed by development errors.'},
        'parameters': {'baseline': 'unchanged hybrid_graph, k=4',
            'adaptive': AdaptiveRetrieval.version+', at most 3 retrieve calls, k=4',
            'scoring_k': [1, 3], 'raw_scores_compared_across_methods': False},
        'id_gold': {'summary': {m: summarize(ids, m) for m in methods}, 'cases': ids,
            'scope': 'Existing 22 authored-card gold development questions; not holdout.'},
        'document_gold': {'summary': {m: summarize(docs, m) for m in methods}, 'cases': docs,
            'scope': documents['scope']+' Current adaptive revision is post-hoc on these same development queries; '
                'the prior no-tuning scope applies to initial source-check design only.'},
        'negatives': negative,
        'post_design_demos': {'cases': demo_rows,
            'scope': 'Five explicit development/demo queries selected after alias-policy design/probing. '
                     'D01/D02 have KB08 illustrative gold; D03 uses KB05 and demonstrates a natural missing-anchor retry; '
                     'D04 is an activity colloquial query that may stop in round one when already supported; '
                     'D05 demonstrates outside-domain abstention. Do not aggregate as a clinical holdout.'}}
    dest = ROOT/'results/agent-upgrade-evaluation.json'
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'id_gold': result['id_gold']['summary'],
        'document_gold': result['document_gold']['summary'], 'negatives': negative['summary'],
        'demos': [{'id': r['id'], 'calls': r['adaptive']['retrieve_calls'],
                   'selected': r['adaptive']['policy']['selected_attempt'],
                   'ids': r['adaptive']['retrieved_ids']} for r in demo_rows]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
