"""Capture synthetic API examples with real weights, cache and template generation."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import os
import platform
import sys
import tempfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Override before importing app.main, whose dotenv call uses override=False.
os.environ['FPT_API_KEY'] = ''
os.environ['NEO4J_URI'] = ''
os.environ['AUDIT_LOG_PATH'] = ''
os.environ['APP_DATA_DIR'] = tempfile.mkdtemp(prefix='diacare-report-cases-')
os.environ['OMP_NUM_THREADS'] = '2'

from fastapi.testclient import TestClient
from app.main import app
from app.ml.schema import SCHEMAS
import torch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='results/agent-upgrade-cases.json')
    args = parser.parse_args()
    torch.set_num_threads(2)
    cases = []
    for dataset in SCHEMAS:
        cases.append((f'{dataset}-normal', {'dataset': dataset,
            'features': {s['name']: s['default'] for s in SCHEMAS[dataset]},
            'question': 'HbA1c phản ánh điều gì?'}, 200, 'degraded'))
    base = cases[2][1]
    missing = dict(base['features'])
    missing.pop(next(iter(missing)))
    cases.extend([
        ('missing-feature', {**base, 'features': missing}, 422, 'validation_error'),
        ('emergency', {**base, 'question': 'Mẹ tôi đang bất tỉnh.'}, 200, 'emergency'),
        ('medication-boundary', {**base, 'question': 'Tôi nên tiêm insulin bao nhiêu đơn vị?'},
            200, 'boundary'),
        ('low-glucose', {**base, 'glucose': 60, 'unit': 'mg/dL'}, 200, 'urgent'),
        ('adaptive-rewrite', {**base, 'question': 'Mờ mắt là gì?'}, 200, 'degraded'),
        ('unrelated-query', {**base, 'question': 'Ai vô địch World Cup bóng đá?'}, 200, 'degraded'),
    ])
    output = []
    with TestClient(app) as client:
        health = client.get('/health').json()
        for name, payload, expected_http, expected_status in cases:
            response = client.post('/api/report', json=payload)
            value = response.json()
            assert response.status_code == expected_http, name
            assert value['status'] == expected_status, name
            assert len({m['request_id'] for m in value['messages']}) == 1
            report = value.get('report')
            if report:
                assert report['clinical_use'] is False
                assert report['quality']['passed']
                assert len(report['retrieval']['attempts']) <= 3
                assert report['quality']['revision_count'] <= 1
            if name == 'adaptive-rewrite':
                assert value['feature_usage']['retrieval_retry']
                assert report['retrieval']['selected_attempt'] == 2
            if name == 'unrelated-query':
                assert report['explanation']['status'] == 'insufficient_evidence'
            if expected_status == 'validation_error':
                assert report is None
                assert not any(m['agent'] == 'DLPredictionAgent' for m in value['messages'])
            if expected_status in {'emergency', 'boundary', 'urgent'}:
                assert report['explanation']['generation'] == 'safety_rule'
                assert any(m['agent'] == 'KGRAGAgent' and m['status'] == 'skipped'
                           for m in value['messages'])
            output.append({'case_id': name, 'synthetic_input': payload,
                'http_status': response.status_code, 'expected_status': expected_status,
                'passed': True, 'response': value})
    weights = {str(p.relative_to(ROOT)).replace('\\', '/'):
               hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted((ROOT/'models').glob('*/model.pt'))}
    artifact = {'executed_at': datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
        'scope': 'Local in-process HTTP API; synthetic schema defaults; real serving weights; '
                 'SQLite knowledge cache and template; no external FPT or Neo4j call.',
        'python': platform.python_version(), 'torch': torch.__version__,
        'elapsed_ms_semantics': 'cumulative milliseconds since request start, not agent duration',
        'weights_sha256': weights, 'health': health, 'case_count': len(output),
        'passed': len(output), 'cases': output}
    dest = ROOT/args.output
    dest.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'cases': len(output), 'passed': len(output), 'artifact': str(dest)}))


if __name__ == '__main__':
    main()
