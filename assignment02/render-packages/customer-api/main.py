# -*- coding: utf-8 -*-
"""
E-COMMERCE CUSTOMER INTEREST API — Assignment 02, App 3
Môn học: Intelligent System Development

POST /predict — nhận RFM + văn bản giỏ hàng khách → dự đoán interest (category sở thích).
Load pipeline đã huấn luyện trong notebook (StandardScaler + TF-IDF + Linear SVM).

Chạy local:  uvicorn main:app --reload --port 8003
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.sparse import hstack, csr_matrix
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).parent / "model" / "customer_pipeline.joblib"
if not MODEL_PATH.exists():
    MODEL_PATH = Path(__file__).parent.parent / "model" / "customer_pipeline.joblib"

app = FastAPI(
    title="E-commerce Customer Interest API",
    description="Assignment 02 — Intelligent System Development | App 3: Online Retail",
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


class CustomerFeatures(BaseModel):
    """Input hành vi khách: 5 chỉ số RFM + văn bản giỏ hàng."""
    recency_days: int = Field(ge=0, le=400, description="Số ngày từ đơn mua gần nhất")
    frequency: int = Field(ge=1, le=100, description="Số đơn hàng")
    monetary: float = Field(gt=0, le=100_000, description="Tổng chi tiêu (USD)")
    total_items: int = Field(gt=0, le=50_000, description="Tổng sản phẩm đã mua")
    avg_order_value: float = Field(gt=0, le=500, description="Giá trị TB 1 dòng đơn (USD)")
    basket_text: str = Field(min_length=3, max_length=2000,
                             description="Văn bản giỏ hàng: tên/mô tả sản phẩm khách mua")


@app.get("/")
def root():
    return {
        "service": "customer-interest-prediction",
        "usage": "POST /predict với RFM + basket_text — xem /docs để thử",
    }


@app.get("/health")
def health():
    if ART is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/customer_pipeline.joblib")
    return {"status": "ok", "model": ART["model"].__class__.__name__}


@app.post("/predict")
def predict(customer: CustomerFeatures):
    """RFM → log + scale (transform) ⊕ basket_text → TF-IDF (transform) → SVM → interest + confidence."""
    if ART is None:
        raise HTTPException(500, "Model chưa load")

    d = customer.model_dump()
    basket = d.pop("basket_text")

    # Feature engineering giống training: log1p monetary/total_items
    row = pd.DataFrame([{
        "recency_days": d["recency_days"],
        "frequency": d["frequency"],
        "log_monetary": float(np.log1p(d["monetary"])),
        "log_items": float(np.log1p(d["total_items"])),
        "avg_order_value": d["avg_order_value"],
    }])[ART["tab_features"]]

    tab_m = ART["scaler"].transform(row)      # transform-only — không fit lại (tránh leakage)
    txt_m = ART["tfidf"].transform([basket])
    x = hstack([csr_matrix(tab_m), txt_m]).tocsr()

    pred = ART["model"].predict(x)[0]
    proba = ART["model"].predict_proba(x)[0]
    top3_idx = proba.argsort()[::-1][:3]

    return {
        "interest": pred,
        "confidence": round(float(proba.max()), 4),
        "top3_interests": [
            {"interest": ART["classes"][i], "probability": round(float(proba[i]), 4)}
            for i in top3_idx
        ],
        "model": "Linear SVM (TF-IDF + RFM)",
    }
