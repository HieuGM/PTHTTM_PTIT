"""One live public-question check; retain verdict/usage, never keys or rejected drafts."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env', override=False)
os.environ['NEO4J_URI'] = ''
os.environ['AUDIT_LOG_PATH'] = ''
from app.agents.coordinator import Coordinator
from app.ml.schema import SCHEMAS


def main():
    with tempfile.TemporaryDirectory(prefix='diacare-provider-review-') as cache:
        os.environ['APP_DATA_DIR'] = cache
        system = Coordinator(ROOT)
        try:
            configured = system.generator.configuration()['configured']
            started = time.perf_counter()
            result = system.report('pima', {s['name']: s['default'] for s in SCHEMAS['pima']},
                                   'HbA1c phản ánh điều gì?')
            explanation = result['report']['explanation']
            review = explanation['review']
            received = review.get('original_generation') == 'fpt_cloud_llm'
            artifact = {'executed_at': datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                'system_version': result['system_version'], 'configured': configured,
                'scope': 'One real provider request with public educational question and synthetic '
                         'Pima defaults; SQLite graph cache; no clinical validation.',
                'provider_structured_response_received': received,
                'provider_attempted': review['provider_attempted'],
                'final_generation': explanation['generation'], 'final_status': explanation['status'],
                'final_review_passed': review['passed'], 'review': review,
                'usage': explanation.get('usage'), 'feature_usage': result['feature_usage'],
                'duration_ms': round((time.perf_counter()-started)*1000, 2),
                'citations': explanation.get('citations', []),
                'final_answer_characters': len(explanation['answer']),
                'error_class': explanation.get('error'),
                'no_raw_rejected_draft_saved': True, 'extra_provider_calls_for_review': 0}
            assert review['revision_count'] <= 1
            path = ROOT/'results/provider-review-verification.json'
            path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({k: artifact[k] for k in ['configured',
                'provider_structured_response_received','final_generation','final_review_passed']}))
        finally:
            system.kb.close()


if __name__ == '__main__':
    main()
