"""Run the new SQL benchmark without overwriting legacy CDC/Hospital artifacts."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.ml.benchmark import run_benchmark


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['full', 'smoke'], default='full')
    parser.add_argument('--seeds', type=int, nargs='+', default=[42, 43, 44])
    parser.add_argument('--reuse-prepared-db', action='store_true')
    parser.add_argument('--resume', action='store_true', help='Verify hashes/labels of completed runs before reuse')
    args = parser.parse_args()
    result = run_benchmark(ROOT, args.mode, tuple(args.seeds), prepare=not args.reuse_prepared_db, resume=args.resume)
    print({k: result[k] for k in ['dataset_count', 'model_type_count', 'dataset_model_combinations',
                                 'run_count', 'elapsed_seconds']})


if __name__ == '__main__':
    main()
