# -*- coding: utf-8 -*-
"""
COMMENT SENTIMENT API — Assignment 03, App 3
Môn học: Intelligent System Development

POST /predict — nhận văn bản comment → phân loại 3 lớp cảm xúc (neg/neutral/pos)
bằng TF-IDF (5000 từ) + PyTorch MLP 5000→64→32→3.

Chạy local:  uvicorn main:app --reload --port 8013
"""
import joblib
import re
import numpy as np
import torch
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mlp_model import MLP

HERE = Path(__file__).parent
WEIGHTS = HERE / "model" / "comments_mlp.pth"
META = HERE / "model" / "comments_mlp_meta.joblib"
if not WEIGHTS.exists():
    WEIGHTS = HERE.parent / "model" / "comments_mlp.pth"
    META = HERE.parent / "model" / "comments_mlp_meta.joblib"

app = FastAPI(
    title="Comment Sentiment API (Deep Learning)",
    description="Assignment 03 — App 3: Amazon Fine Food Reviews (100k) — "
                "TF-IDF + PyTorch MLP 5000→64→32→3",
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
    MODEL = MLP(len(META_ART["tfidf_vocabulary"]), tuple(META_ART["hidden"]), 3)
    MODEL.load_state_dict(torch.load(WEIGHTS, weights_only=True, map_location="cpu"))
    MODEL.eval()


def clean_text(s: str) -> str:
    """Cùng cleaning như training: bỏ <br>, URL, chữ thường."""
    s = re.sub(r"<br\s*/?>", " ", str(s))
    s = re.sub(r"http\S+", " ", s)
    return s.lower().strip()


def tfidf_transform(text: str) -> np.ndarray:
    """Rebuild vector TF-IDF từ vocabulary + idf đã lưu (không cần pickle vectorizer)."""
    from collections import Counter
    from sklearn.feature_extraction.text import TfidfTransformer
    vocab = META_ART["tfidf_vocabulary"]
    tokens = clean_text(text).split()
    # bigram (khớp ngram_range=(1,2) khi train)
    terms = tokens + [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]
    tf_raw = np.zeros((1, len(vocab)), dtype=np.float64)
    for t, c in Counter(terms).items():
        if t in vocab:
            tf_raw[0, vocab[t]] = c
    # sublinear_tf: 1 + log(tf) khi tf>0
    mask = tf_raw > 0
    tf_raw[mask] = 1.0 + np.log(tf_raw[mask])
    idf = np.array(META_ART["tfidf_idf"])
    x = tf_raw * idf
    norm = np.linalg.norm(x, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    return (x / norm).astype(np.float32)


class CommentIn(BaseModel):
    comment: str = Field(..., min_length=2, max_length=5000,
                         description="Nội dung comment sản phẩm (tiếng Anh)")


@app.get("/")
def root():
    return {"service": "comment-sentiment-dl",
            "model": "TF-IDF 5000 + PyTorch MLP 5000→64→32→3",
            "usage": "POST /predict {\"comment\": \"...\"} — xem /docs"}


@app.get("/health")
def health():
    if MODEL is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/comments_mlp.pth")
    return {"status": "ok", "model": "MLP", "params": MODEL.count_params()}


@app.post("/predict")
def predict(c: CommentIn):
    if MODEL is None:
        raise HTTPException(500, "Model chưa load")
    x = tfidf_transform(c.comment)
    with torch.no_grad():
        logits = MODEL(torch.tensor(x))
        proba = torch.softmax(logits, 1).numpy().ravel()
    labels = ["negative", "neutral", "positive"]
    pred = int(proba.argmax())
    return {
        "prediction": labels[pred],
        "prediction_label_vi": ["TIÊU CỰC", "TRUNG LẬP", "TÍCH CỰC"][pred],
        "confidence": round(float(proba[pred]), 4),
        "probabilities": {labels[i]: round(float(p), 4) for i, p in enumerate(proba)},
        "model": "TF-IDF 5000 → PyTorch MLP d→64→32→3 (E2 Deeper)",
        "metrics_test": META_ART.get("metrics_test", {}),
    }
