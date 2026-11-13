"""Link capability declarations to real source symbols and current execution evidence."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import ast
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.capabilities import VERSION, FEATURES, AGENTS


def main():
    rows = []
    for feature in FEATURES:
        item = dict(feature)
        if feature['implemented']:
            path = ROOT/feature['source']['path']
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for name in feature['source']['symbol'].split('.'):
                matches = [node for node in ast.walk(tree)
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name]
                if not matches:
                    raise ValueError(f"Missing source symbol: {feature['id']} / {name}")
                tree = matches[0]
            item['source'] = {**feature['source'], 'line': tree.lineno,
                              'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        rows.append(item)
    cases = json.loads((ROOT/'results/agent-upgrade-cases.json').read_text(encoding='utf-8'))
    result = {'system_version': VERSION,
        'exported_at': datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
        'features': rows, 'agent_contracts': AGENTS,
        'executed_examples': [{'case_id': item['case_id'],
            'feature_usage': item['response']['feature_usage']} for item in cases['cases']],
        'note': 'Source declarations prove implementation; per-request feature_usage proves execution. '
                'Configured/live backends require their own verification.'}
    path = ROOT/'results/technology-map.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'source_symbols_verified': sum(f['implemented'] for f in FEATURES),
                      'features': len(FEATURES), 'examples': len(cases['cases'])}))


if __name__ == '__main__':
    main()
