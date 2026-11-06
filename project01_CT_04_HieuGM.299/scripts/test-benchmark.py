"""Check every real benchmark score/checkpoint and all four serving models."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.ml.verification import verify_benchmark

if __name__ == '__main__':
    result = verify_benchmark(ROOT)
    print({'status': result['status'], 'checks': result['checks_count'], 'runs': result['run_count']})
