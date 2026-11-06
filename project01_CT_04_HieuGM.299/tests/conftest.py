"""Integration fixtures use the actual local KB, policy and trained models."""
import os
import sys
from pathlib import Path
import pytest

# Unit/integration suite uses the real template path; paid provider is checked separately.
os.environ['FPT_API_KEY'] = ''
os.environ['NEO4J_URI'] = ''

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def coordinator(tmp_path_factory):
    from app.agents.coordinator import Coordinator
    previous = os.environ.get("APP_DATA_DIR")
    os.environ["APP_DATA_DIR"] = str(tmp_path_factory.mktemp("knowledge"))
    item = Coordinator(ROOT)
    yield item
    if previous is None:
        os.environ.pop("APP_DATA_DIR", None)
    else:
        os.environ["APP_DATA_DIR"] = previous


@pytest.fixture(scope="session")
def client(coordinator):
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as instance:
        yield instance


@pytest.fixture(params=["cdc", "hospital", "pima", "early"])
def model_case(request):
    from app.ml.predict import Predictor
    predictor = Predictor(ROOT)
    meta = predictor.metadata(request.param)
    features = {item["name"]: item["default"] for item in meta["feature_specs"]}
    return request.param, predictor, meta, features
