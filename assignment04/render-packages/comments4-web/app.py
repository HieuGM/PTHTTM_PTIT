# -*- coding: utf-8 -*-
"""
PHÂN TÍCH CẢM XÚC COMMENT AMAZON (Text CNN) — Web UI (Assignment 04, App 3)
Môn học: Intelligent System Development

Kiến trúc: Streamlit UI → REST API FastAPI /predict (PyTorch TextCNN Conv1D) → hiển thị.
API_URL qua biến môi trường COMMENTS_API_URL (mặc định localhost:8016).
"""
import json
import os
import urllib.request

import streamlit as st

API_URL = os.environ.get("COMMENTS_API_URL", "http://localhost:8016")

st.set_page_config(page_title="Phân tích cảm xúc comment — ISD Assignment 04",
                   page_icon="💬", layout="wide")


def call_api(payload):
    """POST /predict tới FastAPI — web UI KHÔNG chứa model."""
    req = urllib.request.Request(f"{API_URL}/predict", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


st.title("💬 Hệ Phân tích Cảm xúc Comment Amazon — Text CNN (Conv1D)")
st.caption("Assignment 04 — CNN cho text | Amazon Fine Food 100,000 comment | "
           "PyTorch TextCNN: tokens → Embedding(32) → Conv1d(64, k=3) → max-over-time → Dense")

with st.expander("ℹ️ Kiến trúc hệ thống"):
    st.markdown("""
```
Streamlit UI (file này) ──JSON text──▶ FastAPI /predict ──▶ tokenize → IDs → PyTorch TextCNN
   (WEB CLIENT)                        (REST API :8016)       → softmax 3 lớp cảm xúc
```
Conv1D bắt pattern cục bộ 3 từ liền kề: `[very, good]` vs `[not, good]` (Slide 04 trang 11).
""")

comment = st.text_area(
    "✍️ Nhập comment về sản phẩm thức ăn:",
    height=140,
    placeholder="Ví dụ: Best granola I have ever bought. Crunchy and fresh!",
)

st.divider()
if st.button("🔍 Phân tích cảm xúc bằng Text CNN", type="primary", use_container_width=True):
    if not comment.strip():
        st.warning("Hãy nhập nội dung comment trước.")
    else:
        try:
            with st.spinner("Đang gọi API..."):
                res = call_api({"comment": comment})
            color = {"positive": "✅", "neutral": "😐", "negative": "⚠️"}
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Kết quả", f"{color[res['prediction']]} {res['prediction_label_vi']}")
                st.metric("Độ tin cậy", f"{res['confidence']:.1%}")
                st.caption(f"{res['n_tokens']} tokens (sau clean + tokenize)")
            with c2:
                probs = res["probabilities"]
                st.bar_chart({"x": list(probs.keys()), "y": list(probs.values())},
                             x="x", y="y", use_container_width=True)
            st.caption(f"Model: {res['model']} | Test: {res['metrics_test']}")
        except Exception as e:
            st.error(f"Lỗi gọi API ({e}). Kiểm tra API đang chạy ở {API_URL}")
else:
    st.info("Nhập comment rồi bấm **Phân tích cảm xúc bằng Text CNN**.")
