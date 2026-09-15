# -*- coding: utf-8 -*-
"""
AMAZON COMMENT SENTIMENT API — Assignment 04, App 3
Môn học: Intelligent System Development

POST /predict — nhận {"comment": "..."} → tokenize → IDs → PyTorch TextCNN (Conv1D)
→ dự đoán 1/3 lớp cảm xúc (tiêu cực / trung tính / tích cực).

Chạy local:  uvicorn main:app --reload --port 8016
"""
import json
import re
from pathlib import Path

import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from cnn_model import TorchTextCNN

HERE = Path(__file__).parent
WEIGHTS = HERE / "model" / "comments_cnn.pth"
TOKENIZER = HERE / "model" / "tokenizer.json"
if not WEIGHTS.exists():
    WEIGHTS = HERE.parent / "model" / "comments_cnn.pth"
    TOKENIZER = HERE.parent / "model" / "tokenizer.json"

app = FastAPI(
    title="Amazon Comment Sentiment API (Text CNN)",
    description="Assignment 04 — CNN | App 3: Amazon Fine Food 100,000 comment — "
                "PyTorch TextCNN Embedding(32)→Conv1d(64,k3)→max-over-time→Dense",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_static = HERE / "static"
if _static.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/mobile", StaticFiles(directory=str(_static), html=True), name="mobile")

MODEL, VOCAB, MAX_LEN, METRICS_TEST = None, None, 100, {}
if WEIGHTS.exists() and TOKENIZER.exists():
    tok = json.loads(TOKENIZER.read_text(encoding="utf-8"))
    VOCAB, MAX_LEN = tok["vocab"], tok["max_len"]
    MODEL = TorchTextCNN(len(VOCAB))
    MODEL.load_state_dict(torch.load(WEIGHTS, weights_only=True, map_location="cpu"))
    MODEL.eval()
    _meta = WEIGHTS.parent / "comments_api_meta.npy"
    if _meta.exists():
        m = np.load(_meta, allow_pickle=True).item()
        METRICS_TEST = {"accuracy": round(m["acc_torch"], 4), "macro_f1": round(m["f1_torch"], 4)}

LABELS = ["negative", "neutral", "positive"]
LABEL_VI = ["Tiêu cực 😠", "Trung tính 😐", "Tích cực 😊"]


def clean_text(s):
    """Thường hoá + bỏ HTML/số — giống notebook 03."""
    s = s.lower()
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^a-z' ]", " ", s)
    return s.strip()


def text_to_ids(text):
    """Comment → ma trận ID (1, MAX_LEN) — cắt/bù như lúc train."""
    tokens = clean_text(text).split()[:MAX_LEN]
    ids = np.zeros((1, MAX_LEN), dtype=np.int64)
    row = [VOCAB.get(t, 1) for t in tokens]
    ids[0, :len(row)] = row
    return ids, len(tokens)


class CommentIn(BaseModel):
    """Một comment cần phân loại cảm xúc."""
    comment: str = Field(..., min_length=1, max_length=4000, description="Nội dung comment")


@app.get("/")
def root():
    return {"service": "comments-sentiment-textcnn",
            "model": "PyTorch TextCNN Embedding→Conv1d→max-over-time→Dense",
            "usage": "POST /predict {comment: '...'} — xem /docs"}


@app.get("/health")
def health():
    if MODEL is None:
        raise HTTPException(500, "Model chưa load — kiểm tra model/comments_cnn.pth")
    return {"status": "ok", "model": "TorchTextCNN", "params": MODEL.count_params(),
            "vocab": len(VOCAB)}


@app.post("/predict")
def predict(f: CommentIn):
    """Comment → tokens → IDs → Conv1D CNN → softmax 3 lớp cảm xúc."""
    if MODEL is None:
        raise HTTPException(500, "Model chưa load")
    ids, n_tok = text_to_ids(f.comment)
    with torch.no_grad():
        probs = torch.softmax(MODEL(torch.tensor(ids)), dim=1)[0].numpy()
    top = int(probs.argmax())
    return {"prediction": LABELS[top],
            "prediction_label_vi": LABEL_VI[top],
            "confidence": round(float(probs[top]), 4),
            "probabilities": {LABELS[i]: round(float(p), 4) for i, p in enumerate(probs)},
            "n_tokens": n_tok,
            "model": "PyTorch TextCNN Conv1D (Embedding 32, 64 filters 3-gram)",
            "metrics_test": METRICS_TEST}
