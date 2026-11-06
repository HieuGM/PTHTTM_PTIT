"""Render per-cohort figures from the completed SQL benchmark."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.ml.plotting import plot_benchmark

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['full', 'smoke'], default='full')
    arguments = parser.parse_args()
    for path in plot_benchmark(ROOT, arguments.mode):
        print(path)
