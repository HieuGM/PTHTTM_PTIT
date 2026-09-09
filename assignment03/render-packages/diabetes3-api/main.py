# -*- coding: utf-8 -*-
"""
DIABETES PREDICTION API — Assignment 03, App 1
Môn học: Intelligent System Development

POST /predict — nhận 21 chỉ số sức khỏe BRFSS → dự đoán tiểu đường bằng PyTorch MLP
(Deep Learning model đã huấn luyện trong notebook — E2 Deeper d→64→32→1).

Chạy local:  uvicorn main:app --reload --port 8011
"""
import joblib
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mlp_model import MLP

HERE = Path(__file__).parent
WEIGHTS = HERE / "model" / "diabetes_mlp.pth"
META = HERE / "model" / "diabetes_mlp_meta.joblib"
if not WEIGHTS.exists():
    WEIGHTS = HERE.parent / "model" / "diabetes_mlp.pth"
    META = HERE.parent / "model" / "diabetes_mlp_meta.joblib"

app = FastAPI(
    title="Diabetes Prediction API (Deep Learning)",
    description="Assignment 03 — Neural Networks & Representation Learning | "
                "App 1: CDC BRFSS 2015 (253,680) — PyTorch MLP d→64→32→1",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

_static = HERE / "static"
if _static.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/mobile", StaticFiles(directory=str(_static), html=True), name="mobile")

META_ART = joblib.load(META) if META.exists() else None
MODEL = None
if META_ART is not None and WEIGHTS.exists():
    MODEL = MLP(len(META_ART["feature_cols"]), tuple(META_ART["hidden"]))
    MODEL.load_state_dict(torch.load(WEIGHTS, weights_only=True, map_location="cpu"))
    MODEL.eval()

FEATURE_DESC = {
    "HighBP": "Cao huyết áp (0/1)", "HighChol": "Cao cholesterol (0/1)",
    "CholCheck": "Đã xét nghiệm cholesterol 5 năm (0/1)", "BMI": "BMI (12-98)",
    "Smoker": "Đã hút ≥100 điếu (0/1)", "Stroke": "Từng đột quỵ (0/1)",
    "HeartDiseaseorAttack": "Bệnh tim/đau tim (0/1)", "PhysActivity": "Vận động 30 ngày qua (0/1)",
    "Fruits": "Ăn trái cây ≥1 lần/ngày (0/1)", "Veggies": "Ăn rau ≥1 lần/ngày (0/1)",
    "HvyAlcoholConsump": "Uống nhiều rượu (0/1)", "AnyHealthcare": "Có bảo hiểm y tế (0/1)",
    "NoDocbcCost": "Không khám vì giá (0/1)", "GenHlth": "Sức khỏe chung 1(xấu)-5(tốt)",
    "MentHlth": "Ngày sức khỏe tinh thần kém (0-30)", "PhysHlth": "Ngày sức khỏe thể chất kém (0-30)",
    "DiffWalk": "Khó đi bộ (0/1)", "Sex": "Giới tính (0 nữ / 1 nam)",
    "Age": "Nhóm tuổi 1(18-24)-13(80+)", "Education": "Học vấn 1-6", "Income": "Thu nhập 1-8",
}


class HealthFeatures(BaseModel):
    """21 chỉ số BRFSS (đơn vị/mã hóa như khảo sát gốc)."""
    HighBP: int = Field(0, ge=0, le=1)
    HighChol: int = Field(0, ge=0, le=1)
    CholCheck: int = Field(1, ge=0, le=1)
    BMI: float = Field(27, ge=10, le=100)
    Smoker: int = Field(0, ge=0, le=1)
    Stroke: int = Field(0, ge=0, le=1)
    HeartDiseaseorAttack: int = Field(0, ge=0, le=1)
    PhysActivity: int = Field(1, ge=0, le=1)
    Fruits: int = Field(1, ge=0, le=1)
    Veggies: int = Field(1, ge=0, le=1)
    HvyAlcoholConsump: int = Field(0, ge=0, le=1)
    AnyHealthcare: int = Field(1, ge=0, le=1)
    NoDocbcCost: int = Field(0, ge=0, le=1)
    GenHlth: int = Field(3, ge=1, le=5)
    MentHlth: int = Field(0, ge=0, le=30)
    PhysHlth: int = Field(0, ge=0, le=30)
    DiffWalk: int = Field(0, ge=0, le=1)
    Sex: int = Field(0, ge=0, le=1)
    Age: int = Field(6, ge=1, le=13)
    Education: int = Field(4, ge=1, le=6)
    Income: int = Field(5, ge=1, le=8)


@app.get("/")
def root():
    return {"service": "diabetes-prediction-dl",
            "model": "PyTorch MLP 21→64→32→1 (learned representation)",
            "usage": "POST /predict với JSON 21 trường — xem /docs"}


@app.get("/health")
def health():
    if MODEL is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/diabetes_mlp.pth")
    return {"status": "ok", "model": "MLP", "params": MODEL.count_params()}


@app.post("/predict")
def predict(f: HealthFeatures):
    """21 chỉ số thô → scale bằng scaler train → MLP → sigmoid → probability."""
    if MODEL is None:
        raise HTTPException(500, "Model chưa load")

    x = pd.DataFrame([f.model_dump()])[META_ART["feature_cols"]].astype(np.float32).to_numpy()
    x = (x - META_ART["scaler_mean"]) / META_ART["scaler_scale"]
    with torch.no_grad():
        prob = torch.sigmoid(MODEL(torch.tensor(x, dtype=torch.float32))).item()
    pred = int(prob >= 0.5)
    return {
        "prediction": "diabetic" if pred else "not_diabetic",
        "prediction_label_vi": "CÓ TIỂU ĐƯỜNG" if pred else "KHÔNG TIỂU ĐƯỜNG",
        "confidence": round(prob if pred else 1 - prob, 4),
        "probability_diabetic": round(prob, 4),
        "model": "PyTorch MLP d→64→32→1 (E2 Deeper)",
        "metrics_test": META_ART["metrics_test"],
    }
