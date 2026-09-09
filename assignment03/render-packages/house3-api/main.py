# -*- coding: utf-8 -*-
"""
HOUSE PRICE PREDICTION API — Assignment 03, App 2
Môn học: Intelligent System Development

POST /predict — đặc tính bất động sản NYC → dự đoán giá bán bằng PyTorch MLP
(E2 Deeper d→64→32→1 trên one-hot 133D + log10 target).

Chạy local:  uvicorn main:app --reload --port 8012
"""
import joblib
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from mlp_model import MLP

HERE = Path(__file__).parent
WEIGHTS = HERE / "model" / "house_mlp.pth"
META = HERE / "model" / "house_mlp_meta.joblib"
if not WEIGHTS.exists():
    WEIGHTS = HERE.parent / "model" / "house_mlp.pth"
    META = HERE.parent / "model" / "house_mlp_meta.joblib"

app = FastAPI(
    title="NYC House Price API (Deep Learning)",
    description="Assignment 03 — App 2: NYC Rolling Sales (84,548) — PyTorch MLP",
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
    MODEL = MLP(len(META_ART["cat_dummies"]) + len(META_ART["num_cols"]),
                tuple(META_ART["hidden"]))
    MODEL.load_state_dict(torch.load(WEIGHTS, weights_only=True, map_location="cpu"))
    MODEL.eval()


class HouseFeatures(BaseModel):
    """Đặc tính bất động sản NYC (đơn vị gốc dataset)."""
    borough: int = Field(3, ge=1, le=5, description="1 Manhattan, 2 Bronx, 3 Brooklyn, 4 Queens, 5 Staten Island")
    bldg_class: str = Field("01 ONE FAMILY DWELLINGS", description="BUILDING CLASS CATEGORY")
    zip: int = Field(11211, ge=10001, le=11697)
    res_units: float = Field(3, ge=0, le=1000)
    com_units: float = Field(0, ge=0, le=1000)
    land_sf: Optional[float] = Field(None, ge=0, le=5_000_000, description="Để trống nếu không biết")
    gross_sf: float = Field(1800, ge=100, le=2_000_000)
    year_built: Optional[float] = Field(None, ge=1800, le=2025, description="Để trống nếu không biết")
    tax_class: int = Field(1, ge=1, le=10)


@app.get("/")
def root():
    return {"service": "nyc-house-price-dl",
            "model": "PyTorch MLP 133→64→32→1 (log10 price target)",
            "usage": "POST /predict — xem /docs"}


@app.get("/health")
def health():
    if MODEL is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/house_mlp.pth")
    return {"status": "ok", "model": "MLP", "params": MODEL.count_params()}


def build_input(f: HouseFeatures) -> np.ndarray:
    """Đặc tính thô → one-hot + scale đúng representation contract lúc training
    (thứ tự cột: num_cols + cat_dummies — như notebook)."""
    m = META_ART
    num_vals = {
        "res_units": f.res_units, "com_units": f.com_units,
        "total_units": f.res_units + f.com_units,
        "land_sf": np.nan if f.land_sf is None else f.land_sf,
        "gross_sf": f.gross_sf,
        "year_built": np.nan if f.year_built is None else f.year_built,
    }
    num_vals = {k: (v if not pd.isna(v) else m["median_train"][k]) for k, v in num_vals.items()}
    row = {c: 0.0 for c in m["cat_dummies"]}
    row[f"borough_{f.borough}"] = 1.0
    row[f"tax_class_{f.tax_class}"] = 1.0
    if f"bldg_class_{f.bldg_class}" in row:
        row[f"bldg_class_{f.bldg_class}"] = 1.0
    zip_red = f.zip if f.zip in m["top_zips"] else 0
    row[f"zip_reduced_{zip_red}"] = 1.0
    x = pd.DataFrame([{**num_vals, **row}])[m["num_cols"] + m["cat_dummies"]].astype(float)
    arr = x.to_numpy()
    return (arr - np.array(m["scaler_mean"])) / np.array(m["scaler_scale"])


@app.post("/predict")
def predict(f: HouseFeatures):
    if MODEL is None:
        raise HTTPException(500, "Model chưa load")
    x = build_input(f).astype(np.float32)
    with torch.no_grad():
        log_price = MODEL(torch.tensor(x)).item()
    price = float(10 ** log_price)
    return {
        "predicted_price_usd": round(price, 0),
        "predicted_price_display": f"${price:,.0f}",
        "price_range": [round(price * 0.7, -3), round(price * 1.4, -3)],
        "model": "PyTorch MLP d→64→32→1 (E2 Deeper, log10 target)",
        "metrics_test": META_ART.get("metrics_test", {}),
    }
