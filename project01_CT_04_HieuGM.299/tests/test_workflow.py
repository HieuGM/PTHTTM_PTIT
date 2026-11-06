"""Real models, SQL evidence cache and template generation exercise the seven roles."""
import json
import pytest
from app.knowledge.generation import validate_generated
from app.ml.schema import SCHEMAS


def features(dataset):
    return {s['name']: s['default'] for s in SCHEMAS[dataset]}


@pytest.mark.parametrize('dataset', list(SCHEMAS))
def test_report_contract_models_and_provenance(client, dataset):
    response = client.post('/api/report', json={'dataset': dataset,
        'features': features(dataset), 'question': 'HbA1c phản ánh điều gì?'})
    assert response.status_code == 200
    result = response.json()
    messages = result['messages']
    agents = [m['agent'] for m in messages]
    assert agents == ['CoordinatorAgent', 'PatientDataAgent', 'DLPredictionAgent',
        'RuleBasedAgent', 'KGRAGAgent', 'CoordinatorAgent', 'ExplanationAgent', 'MonitoringAgent']
    assert messages[5]['status'] == 'aggregated'
    assert len({m['request_id'] for m in messages}) == 1
    assert all({'status','payload','evidence','model_version','elapsed_ms'} <= set(m) for m in messages)
    report = result['report']
    assert report['prediction']['artifact_reused'] == (dataset in {'cdc','hospital'})
    assert report['explanation']['generation'] == 'template'
    assert {'uncertainty','conflicts','limitations','rule_results','sources'} <= set(report)
    assert report['uncertainty']['score_calibrated'] is False
    assert report['clinical_use'] is False
    assert result['audit']['records_patient_features'] is False
    assert all(s['url'].startswith('https://') for s in report['sources'])


@pytest.mark.parametrize('alteration', ['missing','extra','boolean','string','range'])
def test_invalid_report_stops_before_prediction(client, alteration):
    values = features('cdc'); name = next(iter(values))
    if alteration == 'missing':
        values.pop(name)
    elif alteration == 'extra':
        values['unexpected'] = 1
    else:
        values[name] = {'boolean': True, 'string': '1', 'range': 999}[alteration]
    response = client.post('/api/report', json={'dataset':'cdc','features': values})
    assert response.status_code == 422
    result = response.json()
    assert result['status'] == 'validation_error'
    assert [m['agent'] for m in result['messages']] == ['CoordinatorAgent','PatientDataAgent','MonitoringAgent']
    assert result['report'] is None


def test_invalid_http_envelope_does_not_echo_private_inputs(client):
    marker = 'PRIVATE_PATIENT_MARKER_DO_NOT_STORE'
    response = client.post('/api/report', json={'dataset':'cdc','features':{},'private_name':marker})
    assert response.status_code == 422
    assert marker not in response.text
    assert response.json()['request_id']


def test_report_safety_override_skips_kg_and_llm(client):
    response = client.post('/api/report', json={'dataset':'cdc','features':features('cdc'),
        'question':'Mẹ tôi đang bất tỉnh.'}).json()
    assert response['status'] == 'emergency'
    assert response['report']['explanation']['generation'] == 'safety_rule'
    assert response['report']['conflicts']['items'][0]['type'] == 'safety_override'
    kg = next(m for m in response['messages'] if m['agent'] == 'KGRAGAgent')
    assert kg['status'] == 'skipped'


def test_graph_and_benchmark_api_have_real_records(client):
    graph = client.get('/api/graph').json()
    assert len(graph['nodes']) >= 30 and len(graph['edges']) >= 15
    assert all(edge['evidence_chunk_id'] and edge['url'].startswith('https://') for edge in graph['edges'])
    result = client.get('/api/benchmark').json()
    assert result['run_count'] == len(result['runs']) == 72
    assert result['dataset_count'] == 4 and result['model_type_count'] == 6
    assert len(result['summary']) == 24


@pytest.mark.parametrize('value', [
    {'answer':'Không có trích dẫn','citation_ids':['A']},
    {'answer':'Một câu giả nguồn [B]','citation_ids':['B']},
    {'answer':'Liên kết mới https://example.com [A]','citation_ids':['A']},
    {'answer':'Tham chiếu không khớp [A]','citation_ids':['B']},
])
def test_generated_citation_validator_rejects_invalid_structure(value):
    with pytest.raises(ValueError):
        validate_generated(json.dumps(value), [{'id':'A'}])
