# -*- coding: utf-8 -*-
"""
DIABETES PREDICTION API — Assignment 02, App 1
Môn học: Intelligent System Development

POST /predict — nhận 8 chỉ số lâm sàng → dự đoán tiểu đường type 2.
Load pipeline đã huấn luyện trong notebook (impute median + StandardScaler + RandomForest).

Chạy local:  uvicorn main:app --reload --port 8001
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).parent / "model" / "diabetes_pipeline.joblib"
if not MODEL_PATH.exists():
    MODEL_PATH = Path(__file__).parent.parent / "model" / "diabetes_pipeline.joblib"

app = FastAPI(
    title="Diabetes Prediction API",
    description="Assignment 02 — Intelligent System Development | App 1: Pima Indians Diabetes",
    version="1.0.0",
)

from fastapi.middleware.cors import CORSMiddleware

# Cho phép web client (HF Spaces) và mobile client gọi API từ domain khác
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # demo học tập — production nên giới hạn origin
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount trang mobile client (nếu có thư mục static/ — dùng khi deploy HF Spaces)
_static = Path(__file__).parent / "static"
if _static.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/mobile", StaticFiles(directory=str(_static), html=True), name="mobile")

try:
    ART = joblib.load(MODEL_PATH)
except FileNotFoundError:
    ART = None


class PatientFeatures(BaseModel):
    """Input 8 chỉ số lâm sàng (đơn vị y khoa chuẩn)."""
    Pregnancies: int = Field(ge=0, le=20, description="Số lần mang thai")
    Glucose: float = Field(ge=0, le=300, description="Nồng độ glucose huyết tương 2h (mg/dL)")
    BloodPressure: float = Field(ge=0, le=200, description="Huyết áp tâm trương (mm Hg)")
    SkinThickness: float = Field(ge=0, le=100, description="Độ dày gấp da cơ tam đầu (mm)")
    Insulin: float = Field(ge=0, le=900, description="Insulin serum 2h (μU/mL); 0 = không đo")
    BMI: float = Field(ge=0, le=70, description="Chỉ số khối cơ thể (kg/m²)")
    DiabetesPedigreeFunction: float = Field(ge=0, le=3, description="Hệ số di truyền tiểu đường")
    Age: int = Field(ge=1, le=120, description="Tuổi (năm)")


@app.get("/")
def root():
    return {
        "service": "diabetes-prediction",
        "usage": "POST /predict với JSON 8 trường — xem /docs để thử",
    }


@app.get("/health")
def health():
    if ART is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/diabetes_pipeline.joblib")
    return {"status": "ok", "model": ART["model"].named_steps["model"].__class__.__name__}


@app.post("/predict")
def predict(patient: PatientFeatures):
    """Raw input → ép 0 vô lý → NaN → pipeline (impute+scale+RF) → prediction + confidence."""
    if ART is None:
        raise HTTPException(500, "Model chưa load")

    x = pd.DataFrame([patient.model_dump()])[ART["feature_cols"]].astype(float)
    # Cùng preprocessing như training: 0 vô lý sinh lý → NaN → imputer trong pipeline xử lý
    x[ART["zero_invalid"]] = x[ART["zero_invalid"]].replace(0, np.nan)

    pred = int(ART["model"].predict(x)[0])
    proba = float(ART["model"].predict_proba(x)[0][1])

    return {
        "prediction": "diabetic" if pred == 1 else "not_diabetic",
        "prediction_label_vi": "CÓ TIỂU ĐƯỜNG" if pred == 1 else "KHÔNG TIỂU ĐƯỜNG",
        "confidence": round(proba if pred == 1 else 1 - proba, 4),
        "probability_diabetic": round(proba, 4),
        "model": "RandomForestClassifier(n_estimators=200)",
        "metrics_test": ART["metrics_test"],
    }
