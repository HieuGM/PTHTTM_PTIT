"""Verify feature inventory, observable decisions and bounded controls on the real API."""
import ast
import json
import shutil
import pytest
from pathlib import Path
from app.ml.schema import SCHEMAS

ROOT = Path(__file__).resolve().parents[1]


def payload(question):
    return {'dataset': 'pima', 'features': {s['name']: s['default'] for s in SCHEMAS['pima']},
            'question': question}


def test_capability_inventory_points_to_existing_source_symbols(client):
    response = client.get('/api/capabilities')
    assert response.status_code == 200
    result = response.json()
    assert result['system_version'] == 'hybrid-mas-2.1'
    assert result['budgets']['extra_llm_calls_for_revision'] == 0
    assert len({f['id'] for f in result['features']}) == len(result['features'])
    for feature in result['features']:
        if feature['implemented']:
            source = ROOT/feature['source']['path']
            tree = ast.parse(source.read_text(encoding='utf-8'))
            names = feature['source']['symbol'].split('.')
            for name in names:
                found = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                         and n.name == name]
                assert found, (feature['id'], name)
                tree = found[0]
    implemented = {f['id']: f['implemented'] for f in result['features']}
    assert implemented['output_review'] and implemented['adaptive_retrieval']
    assert not any(implemented[f] for f in ['neural_embedding','langgraph','streaming'])


def test_report_measures_duration_separately_and_records_actual_usage(client):
    result = client.post('/api/report', json=payload('HbA1c phản ánh điều gì?')).json()
    assert result['system_version'] == 'hybrid-mas-2.1'
    assert len(result['messages']) == 8 and len(result['decision_trace']) == 8
    assert all(m['duration_ms'] >= 0 and m['duration_ms'] <= m['elapsed_ms']+.2
               for m in result['messages'])
    times = [m['elapsed_ms'] for m in result['messages']]
    assert times == sorted(times)
    usage = result['feature_usage']
    assert usage['deep_learning'] and usage['output_review'] and usage['adaptive_retrieval']
    assert usage['retrieval_attempts'] == 1 and not usage['retrieval_retry']
    assert not usage['fpt_called'] and not usage['rl_policy']
    assert usage['graph_backend'] == 'sqlite_cache'
    report = result['report']
    assert report['quality']['initial_passed'] and report['quality']['revision_count'] == 0
    assert report['retrieval']['sufficient']


def test_real_rewrite_has_trace_budget_and_provenance(client):
    result = client.post('/api/report', json=payload('Mờ mắt là gì?')).json()
    retrieval = result['report']['retrieval']
    assert retrieval['sufficient'] and retrieval['selected_attempt'] == 2
    assert 1 < len(retrieval['attempts']) <= retrieval['max_attempts'] == 3
    assert retrieval['attempts'][1]['query_strategy'] == 'alias_rewrite'
    assert result['feature_usage']['retrieval_retry']
    assert any(s['id'] == 'KB05' for s in result['report']['sources'])


def test_off_topic_abstains_with_valid_score_and_without_false_llm_usage(client):
    result = client.post('/api/report', json=payload('Ai vô địch World Cup bóng đá?')).json()
    report = result['report']
    assert report['prediction']['dataset'] == 'pima'
    assert report['retrieval']['reason'] == 'no_domain_anchor'
    assert report['retrieved_evidence'] == []
    assert report['explanation']['status'] == 'insufficient_evidence'
    assert report['quality']['passed'] and not result['feature_usage']['fpt_called']


def test_safety_and_invalid_input_skip_optional_controls(client):
    safety = client.post('/api/report', json=payload('Mẹ tôi đang bất tỉnh.')).json()
    assert safety['report']['quality']['status'] == 'safety_override'
    assert not safety['feature_usage']['adaptive_retrieval']
    assert not safety['feature_usage']['output_review'] and not safety['feature_usage']['fpt_called']
    invalid = payload('HbA1c là gì?'); invalid['features'].pop('Age')
    result = client.post('/api/report', json=invalid).json()
    assert not result['feature_usage']['deep_learning'] and result['report'] is None


def test_metadata_audit_has_durations_but_not_question_or_feature_values(client, tmp_path, monkeypatch):
    target = tmp_path/'audit.jsonl'
    monkeypatch.setenv('AUDIT_LOG_PATH', str(target))
    marker = 'PRIVATE_MARKER_NOT_FOR_AUDIT'
    result = client.post('/api/report', json=payload(marker+' HbA1c là gì?')).json()
    audit = json.loads(target.read_text(encoding='utf-8'))
    assert all('duration_ms' in a for a in audit['agents'])
    assert marker not in target.read_text(encoding='utf-8')
    assert 'features' not in audit and 'decision_trace' not in audit
    assert result['feature_usage']['deep_learning']


def test_mismatched_model_feature_order_is_rejected_before_inference(tmp_path):
    from app.ml.predict import Predictor
    folder = tmp_path/'models/pima'; folder.mkdir(parents=True)
    metadata = json.loads((ROOT/'models/pima/metadata.json').read_text(encoding='utf-8'))
    metadata['feature_specs'].reverse()
    (folder/'metadata.json').write_text(json.dumps(metadata), encoding='utf-8')
    shutil.copyfile(ROOT/'models/pima/model.pt', folder/'model.pt')
    with pytest.raises(ValueError, match='metadata'):
        Predictor(tmp_path).predict('pima', payload('')['features'])
