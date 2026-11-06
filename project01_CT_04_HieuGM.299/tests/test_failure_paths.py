"""Failure injection only: missing/corrupt files and unreachable provider are real faults.

These checks do not replace normal model, Neo4j or FPT integration evidence.
"""
import json
import shutil
from pathlib import Path
import pytest
from conftest import ROOT
from app.agents.workflow import ReportWorkflow
from app.knowledge.generation import EvidenceGenerator
from app.ml.schema import SCHEMAS


def patient():
    return {s['name']: s['default'] for s in SCHEMAS['cdc']}


@pytest.mark.parametrize('kind', ['missing', 'corrupt'])
def test_artifact_failure_is_explicit_and_stops_downstream(coordinator, tmp_path, kind):
    folder = tmp_path/'models/cdc'
    folder.mkdir(parents=True)
    shutil.copyfile(ROOT/'models/cdc/metadata.json',folder/'metadata.json')
    if kind == 'corrupt':
        (folder/'model.pt').write_bytes(b'not-a-pytorch-checkpoint')
    workflow = ReportWorkflow(tmp_path, coordinator.kb, EvidenceGenerator())
    result = workflow.run('cdc', patient(), 'HbA1c là gì?')
    assert result['status'] == 'dependency_error'
    assert result['error']['code'] == 'model_unavailable'
    assert result['report'] is None
    assert [m['agent'] for m in result['messages']] == [
        'CoordinatorAgent','PatientDataAgent','DLPredictionAgent','MonitoringAgent']


def test_real_unreachable_provider_returns_labeled_template(monkeypatch):
    monkeypatch.setenv('FPT_API_KEY', 'test-failure-path-only')
    monkeypatch.setenv('FPT_MODEL', 'unreachable-test-provider')
    monkeypatch.setenv('FPT_API_URL', 'https://127.0.0.1:1/chat/completions')
    generator = EvidenceGenerator()
    result = generator.generate('HbA1c là gì?', [{'id':'A','title':'Test evidence',
        'text':'Đây là đoạn bằng chứng cho đường kiểm tra lỗi kết nối.','url':'https://example.org'}])
    assert result['status'] == 'llm_unavailable'
    assert result['generation'] == 'template'
    assert result['model'] is None and result['error']
    assert '[A]' in result['answer']
    assert 'test-failure-path-only' not in json.dumps(result)


def test_opt_in_audit_contains_metadata_only(coordinator, tmp_path, monkeypatch):
    path = tmp_path/'audit.jsonl'
    monkeypatch.setenv('AUDIT_LOG_PATH', str(path))
    marker = 'PRIVATE_QUESTION_DO_NOT_SAVE'
    result = coordinator.report('cdc', patient(), marker+' HbA1c là gì?')
    audit = json.loads(path.read_text())
    assert audit['request_id'] == result['request_id']
    assert marker not in path.read_text()
    assert not {'question','features','api_key'}.intersection(audit)
    assert audit['records_patient_features'] is False


def test_unwritable_audit_does_not_discard_completed_report(coordinator, tmp_path, monkeypatch):
    # A directory is a genuine invalid file target on all supported platforms.
    monkeypatch.setenv('AUDIT_LOG_PATH', str(tmp_path))
    result = coordinator.report('cdc', patient(), 'HbA1c là gì?')
    assert result['report']['prediction']['dataset'] == 'cdc'
    assert result['status'] == 'degraded'
    assert result['audit']['write_status'] == 'failed'
    assert result['audit']['error_code']


def test_near_threshold_flag_matches_uncertainty_schema():
    from app.agents.roles import RuleBasedAgent
    from app.agents.reporting import structured_report
    prediction = {'risk_score': .51,'threshold': .5,'predicted_class': 1,'limitations':[]}
    rules = RuleBasedAgent().run('HbA1c là gì?', prediction)
    report = structured_report(prediction,rules,[],{'generation':'template'},'ok')
    assert report['uncertainty']['near_model_threshold'] is True


def test_huge_integer_is_a_validation_error_not_overflow(client):
    values = patient()
    values[next(iter(values))] = 10**1000
    response = client.post('/api/report', json={'dataset':'cdc','features':values})
    assert response.status_code == 422
    assert response.json()['status'] == 'validation_error'


@pytest.mark.parametrize('malformed', ['[]','null','42','"string"', None, 42])
def test_non_object_provider_json_is_rejected_cleanly(malformed):
    from app.knowledge.generation import validate_generated
    with pytest.raises(ValueError):
        validate_generated(malformed, [{'id':'A'}])
