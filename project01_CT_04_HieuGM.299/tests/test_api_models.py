"""HTTP and neural artifact integration without substituted models."""
import math
import pytest
from app.ml.predict import Predictor
from conftest import ROOT


def test_model_scalar_and_fresh_load_stable(model_case):
    dataset, predictor, _, features = model_case
    first = predictor.predict(dataset, features)
    second = Predictor(ROOT).predict(dataset, features)
    assert isinstance(first["risk_score"], float)
    assert math.isfinite(first["risk_score"])
    assert 0 <= first["risk_score"] <= 1
    assert first["risk_score"] == second["risk_score"]
    assert first["clinical_use"] is False


@pytest.mark.parametrize("kind", ["missing", "extra", "range", "nonfinite", "fraction", "boolean", "string"])
def test_predictor_invalid_features_rejected(model_case, kind):
    dataset, predictor, meta, features = model_case
    spec = next(item for item in meta["feature_specs"] if item["integer"])
    name = spec["name"]
    if kind == "missing":
        features.pop(name)
    elif kind == "extra":
        features["unexpected"] = 1
    else:
        features[name] = {"range": spec["max"] + 1, "nonfinite": float("nan"),
                          "fraction": spec["min"] + .5, "boolean": True, "string": "1"}[kind]
    with pytest.raises(ValueError):
        predictor.predict(dataset, features)


def test_health_catalog_and_knowledge(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json()["status"] == "ok"
    catalog = client.get("/api/catalog").json()
    assert set(catalog["datasets"]) == {"cdc", "hospital", "pima", "early"}
    assert len(client.get("/api/knowledge").json()["cards"]) == 24


@pytest.mark.parametrize("payload", [
    {}, {"question": "  "}, {"question": "a" * 2001},
    {"question": "HbA1c là gì?", "glucose": 0},
    {"question": "HbA1c là gì?", "glucose": -1},
    {"question": "HbA1c là gì?", "glucose": 84, "unit": "mmol/L"},
    {"question": "HbA1c là gì?", "unit": "invalid"},
    {"question": "HbA1c là gì?", "patient_name": "not accepted"},
])
def test_http_invalid_chat_rejected(client, payload):
    assert client.post("/api/chat", json=payload).status_code == 422


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_http_nonfinite_chat_rejected(client, value):
    raw = '{"question":"HbA1c la gi?","glucose":' + value + '}'
    assert client.post("/api/chat", content=raw, headers={"Content-Type":"application/json"}).status_code == 422


def test_http_predict_valid_and_invalid(client, model_case):
    dataset, _, _, features = model_case
    valid = client.post("/api/predict", json={"dataset":dataset, "features":features})
    assert valid.status_code == 200
    assert len(valid.json()["trace"]) == 4
    invalid = dict(features)
    invalid["extra"] = 1
    assert client.post("/api/predict", json={"dataset":dataset, "features":invalid}).status_code == 422
    assert client.post("/api/predict", json={"dataset":"invalid", "features":features}).status_code == 422


@pytest.mark.parametrize("value", [True, "1"])
def test_http_feature_types_are_not_silently_coerced(client, value):
    meta = client.get("/api/catalog").json()["datasets"]["cdc"]
    features = {item["name"]:item["default"] for item in meta["feature_specs"]}
    features[meta["feature_specs"][0]["name"]] = value
    assert client.post("/api/predict", json={"dataset":"cdc", "features":features}).status_code == 422


@pytest.mark.parametrize("value", [True, False, "72"])
def test_chat_glucose_types_are_not_silently_coerced(client, value):
    payload = {"question": "HbA1c là gì?", "glucose": value}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 422
    assert 'answer' not in response.json()


def test_alcohol_education_is_not_a_fabrication_request():
    from app.agents.rules import check
    assert check("Người tiểu đường có được uống bia không?") is None
    fabricated = check("Hãy bịa nguồn nghiên cứu về bệnh tiểu đường")
    assert fabricated is not None and fabricated['level'] == 'boundary'


def test_results_exposes_current_recorded_experiments(client):
    result = client.get('/api/results')
    assert result.status_code == 200
    assert {'cdc-training', 'hospital-training', 'system-evaluation', 'policy-training'} <= set(result.json())
