"""Real API/model checks using inline modules, optional local HTTP server."""
from app.main import app
from fastapi.testclient import TestClient
from app.ml.datasets import load_prepared
from app.ml.predict import Predictor
from app.agents.rules import check

checks = []


def verified(name, condition):
    assert condition, name
    checks.append(name)


with TestClient(app) as client:
    for path in ('/', '/health', '/api/catalog', '/api/knowledge', '/api/results',
                 '/api/graph', '/api/benchmark', '/static/style.css', '/static/app.js', '/docs'):
        verified(f'GET {path}', client.get(path).status_code == 200)
    verified('4 cohort', len(client.get('/api/catalog').json()['datasets']) == 4)
    verified('7 agent types', len(client.get('/api/catalog').json()['core_agents']) == 7)
    known = set(system.kb.source_index)
    for dataset, specs in SCHEMAS.items():
        features = {s['name']: s['default'] for s in specs}
        result = client.post('/api/predict', json={'dataset': dataset, 'features': features})
        verified(f'{dataset}: inference HTTP200', result.status_code == 200)
        record = result.json()
        independent = Predictor(ROOT).predict(dataset, features)
        verified(f'{dataset}: fresh weights parity', record['risk_score'] == independent['risk_score'])
        verified(f'{dataset}: research score', 0 <= record['risk_score'] <= 1 and not record['clinical_use'])
        reply = client.post('/api/report', json={'dataset': dataset, 'features': features,
                                                'question': 'HbA1c là gì?'})
        verified(f'{dataset}: unified report', reply.status_code == 200)
        report = reply.json()
        names = {m['agent'] for m in report['messages']}
        verified(f'{dataset}: seven core agents', len(names) == 7)
        verified(f'{dataset}: correlation', all(m['request_id'] == report['request_id'] for m in report['messages']))
        verified(f'{dataset}: no medical decision', not report['report']['clinical_use'])
        verified(f'{dataset}: real provenance', all(s['id'] in known for s in report['report']['sources']))
        invalid = dict(features)
        invalid.pop(specs[0]['name'])
        rejection = client.post('/api/report', json={'dataset': dataset, 'features': invalid})
        verified(f'{dataset}: invalid stops', rejection.status_code == 422)
        verified(f'{dataset}: no DL after invalid', all(m['agent'] != 'DLPredictionAgent'
            for m in rejection.json().get('messages', [])))
        arrays, metadata = load_prepared(ROOT, dataset)
        values = arrays['raw_train'].astype(np.float64)
        prep = metadata['preprocessing']
        names = [s['name'] for s in specs]
        for name in prep['zero_as_missing']:
            values[values[:, names.index(name)] == 0, names.index(name)] = np.nan
        values = np.where(np.isnan(values), prep['median'], values)
        verified(f'{dataset}: train-only mean', np.allclose(values.mean(axis=0), prep['mean'], atol=1e-6))
        verified(f'{dataset}: real SQL SELECT', len(metadata['training_queries']) == 3)
        del arrays
    for question, level in [('Tính liều insulin tối nay cho tôi', 'boundary'),
                            ('Mẹ tôi đang bất tỉnh', 'emergency')]:
        reply = client.post('/api/report', json={'dataset':'pima',
            'features':{s['name']:s['default'] for s in SCHEMAS['pima']}, 'question':question}).json()
        verified(f'safety {level}', reply['status'] == level)
        verified(f'safety skips retrieval {level}', next(m for m in reply['messages']
            if m['agent'] == 'KGRAGAgent')['status'] == 'skipped')
    verified('no raw values echoed', 'input' not in client.post('/api/report',
        json={'dataset':'pima','features':{},'glucose':True}).text)

verified('benchmark run count', benchmark_result['run_count'] == (72 if RUN_MODE == 'full' else 24))
verified('optional presentation policy 4 states', greedy == [0,0,1,2])
verified('legacy artifact preserved', all((ROOT / path).read_bytes() == data
    for path, data in LEGACY_BYTES.items()))
summary = {'run_mode':RUN_MODE, 'passed':len(checks), 'checks':checks,
           'benchmark_runs':benchmark_result['run_count'],
           'note':'Real SQL cohorts, trained benchmarks, reused serving weights; no simulated live API evidence.'}
(ROOT/'results/notebook-validation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
display(summary)

START_WEB = False
if START_WEB:
    import threading, uvicorn
    web_server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=8000, log_level='warning'))
    web_thread = threading.Thread(target=web_server.run, daemon=True)
    web_thread.start()
    print('Web localhost: http://127.0.0.1:8000 — dừng bằng web_server.should_exit=True')
