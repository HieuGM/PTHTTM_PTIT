"""Populate SQLite with authentic raw rows, clean splits and train-only preprocessing."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.ml.datasets import prepare_database

if __name__ == '__main__':
    prepare_database(ROOT)
