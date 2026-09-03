# -*- coding: utf-8 -*-
"""
HOUSE PRICE PREDICTION API — Assignment 02, App 2
Môn học: Intelligent System Development

POST /predict — nhận đặc điểm nhà (King County) → dự đoán giá bán USD.
Load pipeline đã huấn luyện trong notebook (scale + one-hot zipcode + GradientBoosting, log-target).

Chạy local:  uvicorn main:app --reload --port 8002
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).parent / "model" / "house_pipeline.joblib"
if not MODEL_PATH.exists():
    MODEL_PATH = Path(__file__).parent.parent / "model" / "house_pipeline.joblib"

app = FastAPI(
    title="House Price Prediction API",
    description="Assignment 02 — Intelligent System Development | App 2: KC House Sales",
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


class HouseFeatures(BaseModel):
    """Input đặc điểm nhà — cùng đơn vị dataset KC House."""
    sqft_living: float = Field(gt=0, le=15000, description="Diện tích sống (sqft)")
    sqft_lot: float = Field(gt=0, le=2_000_000, description="Diện tích lô đất (sqft)")
    sqft_above: float = Field(ge=0, le=10000, description="Diện tích trên mặt đất (sqft)")
    sqft_basement: float = Field(ge=0, le=5000, description="Diện tích tầng hầm (sqft)")
    bedrooms: int = Field(ge=0, le=15, description="Số phòng ngủ")
    bathrooms: float = Field(ge=0, le=10, description="Số vệ sinh (0.5 = toilet riêng)")
    floors: float = Field(gt=0, le=4, description="Số tầng")
    waterfront: int = Field(ge=0, le=1, description="1 = view mặt nước")
    view: int = Field(ge=0, le=4, description="Cấp độ view (0-4)")
    condition: int = Field(ge=1, le=5, description="Tình trạng nhà (1-5)")
    grade: int = Field(ge=1, le=13, description="Chất lượng xây dựng (1-13)")
    yr_built: int = Field(ge=1900, le=2015, description="Năm xây")
    yr_renovated: int = Field(ge=0, le=2015, description="Năm cải tạo cuối (0 = chưa)")
    lat: float = Field(ge=47.0, le=47.8, description="Vĩ độ")
    long: float = Field(ge=-122.6, le=-121.0, description="Kinh độ")
    zipcode: int = Field(ge=98000, le=98200, description="Mã vùng King County")


@app.get("/")
def root():
    return {
        "service": "house-price-prediction",
        "usage": "POST /predict với JSON 16 trường — xem /docs để thử",
    }


@app.get("/health")
def health():
    if ART is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/house_pipeline.joblib")
    return {"status": "ok", "model": ART["model"].named_steps["model"].__class__.__name__}


@app.post("/predict")
def predict(house: HouseFeatures):
    """Raw input → feature engineering (house_age, renovated) → pipeline (scale + one-hot) → GB → giá USD."""
    if ART is None:
        raise HTTPException(500, "Model chưa load")

    d = house.model_dump()
    d["house_age"] = 2015 - d["yr_built"]
    d["renovated"] = 1 if d["yr_renovated"] > 0 else 0
    x = pd.DataFrame([d])
    x["zipcode"] = x["zipcode"].astype(int).astype(str)

    log_pred = ART["model"].predict(x)[0]
    price = float(np.expm1(log_pred))  # đảo log1p — trả về USD

    return {
        "predicted_price": round(price),
        "predicted_price_display": f"${price:,.0f}",
        "confidence_range": f"${price * 0.88:,.0f} – ${price * 1.12:,.0f}",
        "model": "GradientBoostingRegressor(n_estimators=200)",
        "metrics_test": ART["metrics_test"],
    }
