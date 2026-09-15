# -*- coding: utf-8 -*-
"""
CIFAR-10 OBJECT RECOGNITION API — Assignment 04, App 2
Môn học: Intelligent System Development

POST /predict — nhận ảnh 32×32 RGB (list 32 hàng × 32 pixel [r,g,b] [0,1])
→ PyTorch SE-CNN (M4: Conv+BN+Residual+SE attention) dự đoán 1/10 lớp.
GET  /samples — vài ảnh test mẫu kèm nhãn.

Chạy local:  uvicorn main:app --reload --port 8015
"""
import pickle
import tarfile
from pathlib import Path

import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from cnn_model import SEClassifier

HERE = Path(__file__).parent
WEIGHTS = HERE / "model" / "cifar_m4_se.pth"
if not WEIGHTS.exists():
    WEIGHTS = HERE.parent / "model" / "cifar_m4_se.pth"

app = FastAPI(
    title="CIFAR-10 Recognition API (CNN + SE attention)",
    description="Assignment 04 — CNN | App 2: CIFAR-10 60,000 ảnh 32×32×3 — "
                "PyTorch M4: Conv+BN+Residual+SE (experiment M1→M4, tutorial §45)",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_static = HERE / "static"
if _static.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/mobile", StaticFiles(directory=str(_static), html=True), name="mobile")

MODEL = None
if WEIGHTS.exists():
    MODEL = SEClassifier()
    MODEL.load_state_dict(torch.load(WEIGHTS, weights_only=True, map_location="cpu"))
    MODEL.eval()

META = None
_meta_path = WEIGHTS.parent / "cifar_api_meta.npy"
if _meta_path.exists():
    META = np.load(_meta_path, allow_pickle=True).item()
METRICS_TEST = {"accuracy": round(float(META["acc_m4"]), 4)} if META else {"accuracy": 0.74}

CLASS_NAMES = ["airplane", "automobile", "bird", "cat", "deer",
               "dog", "frog", "horse", "ship", "truck"]
CLASS_VI = ["máy bay", "ô tô", "chim", "mèo", "hươu", "chó", "ếch", "ngựa", "tàu thủy", "xe tải"]

# Ảnh mẫu: ưu tiên samples.npz gọn trong gói deploy (Render), fallback tar.gz đầy đủ local
X_SAMPLE, Y_SAMPLE = None, None
_npz = HERE / "model" / "samples.npz"
if _npz.exists():
    _d = np.load(_npz)
    X_SAMPLE, Y_SAMPLE = _d["X"], _d["Y"]
else:
    _tar = HERE.parent / "data" / "cifar-10-python.tar.gz"
    if _tar.exists():
        with tarfile.open(_tar, "r:gz") as tar:
            for m in tar.getmembers():
                if m.name.split("/")[-1] == "test_batch":
                    d = pickle.loads(tar.extractfile(m).read(), encoding="bytes")
                    X_SAMPLE = (d[b"data"].reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1) / 255.0)[:200]
                    Y_SAMPLE = np.array(d[b"labels"])[:200]
                    break


class CifarImage(BaseModel):
    """Ảnh 32×32 RGB — 32 hàng, mỗi hàng 32 pixel [r,g,b] trong [0,1]."""
    image: list


@app.get("/")
def root():
    return {"service": "cifar10-se-cnn",
            "model": "PyTorch M4 SE-CNN (Conv+BN+Residual+SE)",
            "usage": "POST /predict {image: 32×32×3 list} — xem /docs"}


@app.get("/health")
def health():
    if MODEL is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/cifar_m4_se.pth")
    return {"status": "ok", "model": "SEClassifier (M4)", "params": MODEL.count_params()}


@app.get("/samples")
def samples(n: int = 8):
    """Vài ảnh test mẫu kèm nhãn."""
    if X_SAMPLE is None:
        raise HTTPException(500, "Không tìm thấy dữ liệu mẫu trong ../data")
    n = max(1, min(n, len(X_SAMPLE)))
    step = max(1, len(X_SAMPLE) // n)
    return {"samples": [{"index": int(i), "label": int(Y_SAMPLE[i]),
                         "label_name": CLASS_NAMES[Y_SAMPLE[i]],
                         "image": [[[round(float(v), 3) for v in px] for px in row]
                                   for row in X_SAMPLE[i]]}
                        for i in range(0, len(X_SAMPLE), step)][:n]}


@app.post("/predict")
def predict(f: CifarImage):
    """Ảnh 32×32×3 → SE-CNN → softmax 10 lớp."""
    if MODEL is None:
        raise HTTPException(500, "Model chưa load")
    img = np.asarray(f.image, dtype=np.float32)
    if img.shape != (32, 32, 3):
        raise HTTPException(400, f"image phải 32×32×3, nhận {img.shape}")
    x = torch.tensor(img.transpose(2, 0, 1).reshape(1, 3, 32, 32))
    with torch.no_grad():
        probs = torch.softmax(MODEL(x), dim=1)[0].numpy()
    top = int(probs.argmax())
    return {"prediction": CLASS_NAMES[top],
            "prediction_label_vi": CLASS_VI[top],
            "confidence": round(float(probs[top]), 4),
            "probabilities": {CLASS_NAMES[i]: round(float(p), 4) for i, p in enumerate(probs)},
            "model": "PyTorch M4 SE-CNN (Conv+BN+Residual+SE attention)",
            "metrics_test": METRICS_TEST}
