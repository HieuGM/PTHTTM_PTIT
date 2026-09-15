# -*- coding: utf-8 -*-
"""
MNIST DIGIT RECOGNITION API — Assignment 04, App 1
Môn học: Intelligent System Development

POST /predict — nhận ảnh 28×28 (list 28 hàng × 28 giá trị [0,1]) → PyTorch CNN dự đoán chữ số.
GET  /samples — trả vài ảnh test mẫu (kèm nhãn) cho web/mobile demo.

Chạy local:  uvicorn main:app --reload --port 8014
"""
import gzip
from pathlib import Path

import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from cnn_model import TorchCNN

HERE = Path(__file__).parent
WEIGHTS = HERE / "model" / "mnist_cnn.pth"
if not WEIGHTS.exists():
    WEIGHTS = HERE.parent / "model" / "mnist_cnn.pth"

app = FastAPI(
    title="MNIST Digit Recognition API (CNN)",
    description="Assignment 04 — CNN | App 1: MNIST 70,000 ảnh 28×28 — "
                "PyTorch CNN Conv8→Conv16→Pool→Dense (24,298 tham số)",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_static = HERE / "static"
if _static.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/mobile", StaticFiles(directory=str(_static), html=True), name="mobile")

MODEL = None
if WEIGHTS.exists():
    MODEL = TorchCNN()
    MODEL.load_state_dict(torch.load(WEIGHTS, weights_only=True, map_location="cpu"))
    MODEL.eval()

META = None
_meta_path = WEIGHTS.parent / "mnist_api_meta.npy"
if _meta_path.exists():
    META = np.load(_meta_path, allow_pickle=True).item()
METRICS_TEST = {"accuracy": round(float(META["acc_torch"]), 4)} if META else {"accuracy": 0.988}

CLASS_NAMES = [str(i) for i in range(10)]


def _load_idx_images(gz_path):
    """Đọc ảnh IDX nén gzip → (n,28,28) float32 [0,1] — giống notebook 01."""
    with gzip.open(gz_path, "rb") as f:
        _, n, rows, cols = np.frombuffer(f.read(16), dtype=">u4")
        data = np.frombuffer(f.read(), dtype=np.uint8)
    return data.reshape(n, rows, cols).astype(np.float32) / 255.0


def _load_idx_labels(gz_path):
    """Đọc nhãn IDX → (n,) uint8."""
    with gzip.open(gz_path, "rb") as f:
        _, n = np.frombuffer(f.read(8), dtype=">u4")
        return np.frombuffer(f.read(), dtype=np.uint8)


# Ảnh mẫu: ưu tiên samples.npz gọn trong gói deploy (Render), fallback dataset đầy đủ local
X_SAMPLE, Y_SAMPLE = None, None
_npz = HERE / "model" / "samples.npz"
if _npz.exists():
    _d = np.load(_npz)
    X_SAMPLE, Y_SAMPLE = _d["X"], _d["Y"]
elif (HERE.parent / "data" / "t10k-images-idx3-ubyte.gz").exists():
    X_SAMPLE = _load_idx_images(HERE.parent / "data" / "t10k-images-idx3-ubyte.gz")[:100]
    Y_SAMPLE = _load_idx_labels(HERE.parent / "data" / "t10k-labels-idx1-ubyte.gz")[:100]


class DigitImage(BaseModel):
    """Ảnh 28×28 grayscale — 28 hàng, mỗi hàng 28 giá trị [0,1]."""
    image: list = Field(..., description="list 28 hàng × 28 số thực [0..1]")


@app.get("/")
def root():
    return {"service": "mnist-digit-cnn",
            "model": "PyTorch CNN Conv8→Conv16→Pool→Dense (24,298 params)",
            "usage": "POST /predict {image: 28×28 list} — xem /docs"}


@app.get("/health")
def health():
    if MODEL is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/mnist_cnn.pth")
    return {"status": "ok", "model": "TorchCNN", "params": MODEL.count_params()}


@app.get("/samples")
def samples(n: int = 8):
    """Vài ảnh test mẫu kèm nhãn — cho client không có dataset."""
    if X_SAMPLE is None:
        raise HTTPException(500, "Không tìm thấy dữ liệu mẫu trong ../data")
    n = max(1, min(n, len(X_SAMPLE)))
    step = max(1, len(X_SAMPLE) // n)
    return {"samples": [{"index": int(i), "label": int(Y_SAMPLE[i]),
                         "image": [[round(float(v), 3) for v in row] for row in X_SAMPLE[i]]}
                        for i in range(0, len(X_SAMPLE), step)][:n]}


@app.post("/predict")
def predict(f: DigitImage):
    """Ảnh 28×28 → CNN → softmax 10 lớp → chữ số + xác suất."""
    if MODEL is None:
        raise HTTPException(500, "Model chưa load")
    img = np.asarray(f.image, dtype=np.float32)
    if img.shape != (28, 28):
        raise HTTPException(400, f"image phải 28×28, nhận {img.shape}")
    x = torch.tensor(img.reshape(1, 1, 28, 28))
    with torch.no_grad():
        probs = torch.softmax(MODEL(x), dim=1)[0].numpy()
    top = int(probs.argmax())
    return {"prediction": top,
            "prediction_label_vi": "Chữ số %d" % top,
            "confidence": round(float(probs[top]), 4),
            "probabilities": {CLASS_NAMES[i]: round(float(p), 4) for i, p in enumerate(probs)},
            "model": "PyTorch CNN Conv8→Conv16→Pool→Dense",
            "metrics_test": METRICS_TEST}
