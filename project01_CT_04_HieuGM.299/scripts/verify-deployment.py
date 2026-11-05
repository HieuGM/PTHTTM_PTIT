"""Exercise a running deployment over HTTP using real bundled model artifacts."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000')
parser.add_argument('--output', default='results/deployment-verification.json')
args = parser.parse_args()
url = args.url.rstrip('/')
checks = []


def record(name, passed, detail=''):
    checks.append({'name': name, 'passed': bool(passed), 'detail': detail})


response = requests.get(url + '/health', timeout=90)
record('health', response.status_code == 200 and response.json().get('status') == 'ok')
response = requests.get(url + '/', timeout=30)
record('frontend', response.status_code == 200 and 'DiaCare' in response.text)
for asset in ['app.js', 'style.css']:
    response = requests.get(url + '/static/' + asset, timeout=30)
    record('asset_' + asset, response.status_code == 200)
response = requests.get(url + '/api/catalog', timeout=30)
catalog = response.json()
record('knowledge_inventory', catalog.get('knowledge', {}).get('cards') == 24)
for dataset in ['cdc', 'hospital']:
    metadata = catalog['datasets'][dataset]
    features = {s['name']: s['default'] for s in metadata['feature_specs']}
    prediction = requests.post(url + '/api/predict', json={'dataset': dataset, 'features': features}, timeout=30)
    result = prediction.json()
    record('prediction_' + dataset, prediction.status_code == 200 and 0 <= result['risk_score'] <= 1
           and result['clinical_use'] is False and len(result['trace']) <= 8,
           f"score={result.get('risk_score')}")
    invalid = requests.post(url + '/api/predict', json={'dataset': dataset, 'features': {}}, timeout=30)
    record('missing_fields_' + dataset, invalid.status_code == 422)
answer = requests.post(url + '/api/chat', json={'question': 'HbA1c là gì?'}, timeout=30).json()
record('grounded_answer', answer.get('status') == 'grounded' and bool(answer.get('sources')))
answer = requests.post(url + '/api/chat', json={'question': 'Tôi đang khó thở và lơ mơ'}, timeout=30).json()
record('safety_priority', answer.get('status') == 'emergency' and answer.get('policy_action') == 'safety_override')
response = requests.post(url + '/api/chat', data='{"question":"Kiểm tra glucose", "glucose":NaN}',
                         headers={'Content-Type': 'application/json'}, timeout=30)
record('nonfinite_input', response.status_code == 422)
answer = requests.post(url + '/api/chat', json={'question': 'Cổ phiếu nào tăng ngày mai?'}, timeout=30).json()
record('off_topic_refusal', answer.get('status') == 'insufficient_evidence')
report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'url': url,
          'checks': checks, 'passed': sum(c['passed'] for c in checks), 'total': len(checks),
          'scope': 'Live HTTP checks, no mocked model or network response.'}
output = Path(args.output)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'passed': report['passed'], 'total': len(checks)}))
if report['passed'] != len(checks):
    raise SystemExit(1)
