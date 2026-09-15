# -*- coding: utf-8 -*-
"""
NHẬN DẠNG CHỮ SỐ VIẾT TAY (CNN) — Web UI (Assignment 04, App 1)
Môn học: Intelligent System Development

Kiến trúc: Streamlit UI → REST API FastAPI /predict (PyTorch CNN) → hiển thị.
API_URL qua biến môi trường MNIST_API_URL (mặc định localhost:8014).
"""
import io
import json
import os
import urllib.request

import numpy as np
import streamlit as st

API_URL = os.environ.get("MNIST_API_URL", "http://localhost:8014")

st.set_page_config(page_title="Nhận dạng chữ số MNIST — ISD Assignment 04",
                   page_icon="🔢", layout="wide")


def call_api(path, payload=None):
    """GET/POST tới FastAPI — web UI KHÔNG chứa model."""
    if payload is None:
        with urllib.request.urlopen(f"{API_URL}{path}", timeout=30) as r:
            return json.loads(r.read())
    req = urllib.request.Request(f"{API_URL}{path}", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


st.title("🔢 Hệ Nhận dạng Chữ số viết tay — CNN (MNIST 70,000 ảnh)")
st.caption("Assignment 04 — Convolutional Neural Networks | "
           "PyTorch CNN Conv8→Conv16→Pool→Dense (24,298 tham số — NumPy from scratch ở notebook)")

with st.expander("ℹ️ Kiến trúc hệ thống"):
    st.markdown("""
```
Streamlit UI (file này) ──JSON 28×28──▶ FastAPI /predict ──▶ PyTorch CNN ──▶ softmax 10 lớp
   (WEB CLIENT)                          (REST API :8014)      (.pth từ notebook)
```
CNN từ đầu (NumPy) + PyTorch + TensorFlow/Keras cùng MỘT kiến trúc — xem notebook 01.
""")

tab_sample, tab_upload = st.tabs(["🖼️ Chọn ảnh mẫu từ tập test", "⬆️ Tải ảnh PNG lên"])

image = None
with tab_sample:
    try:
        smp = call_api("/samples?n=12")["samples"]
        cols = st.columns(6)
        pick = st.selectbox("Ảnh mẫu (index trong 10k ảnh test)",
                            range(len(smp)), format_func=lambda i: f"#{smp[i]['index']} — nhãn {smp[i]['label']}")
        img_np = np.array(smp[pick]["image"], dtype=np.float32)
        with cols[0]:
            st.image(img_np, caption=f"Ảnh test #{smp[pick]['index']} (nhãn thật {smp[pick]['label']})",
                     width=160, clamp=True)
        st.progress(1.0, text="Ảnh 28×28 đã chuẩn hoá [0,1] — sẵn sàng dự đoán")
        image = [[round(float(v), 4) for v in row] for row in img_np]
    except Exception as e:
        st.error(f"Không lấy được mẫu từ API ({e}). Kiểm tra API đang chạy ở {API_URL}")

with tab_upload:
    up = st.file_uploader("Tải ảnh chữ số (PNG/JPG — nên nền đen chữ trắng)", type=["png", "jpg", "jpeg"])
    if up is not None:
        from PIL import Image
        pil = Image.open(io.BytesIO(up.getvalue())).convert("L")
        arr = np.array(pil.resize((28, 28)), dtype=np.float32) / 255.0
        c1, c2 = st.columns(2)
        with c1:
            st.image(arr, caption="Sau khi resize 28×28 grayscale", width=160, clamp=True)
        with c2:
            st.image(arr, caption="Ảnh gốc (đã chuyển xám)", clamp=True)
        image = [[round(float(v), 4) for v in row] for row in arr]

st.divider()
if image is not None and st.button("🔍 Dự đoán bằng CNN", type="primary", use_container_width=True):
    try:
        with st.spinner("Đang gọi API..."):
            res = call_api("/predict", {"image": image})
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Chữ số dự đoán", res["prediction_label_vi"])
            st.metric("Độ tin cậy", f"{res['confidence']:.1%}")
        with c2:
            probs = res["probabilities"]
            st.bar_chart({"x": list(probs.keys()), "y": list(probs.values())},
                         x="x", y="y", use_container_width=True)
        st.caption(f"Model: {res['model']} | Test accuracy: {res['metrics_test']}")
    except Exception as e:
        st.error(f"Lỗi gọi API ({e}). Kiểm tra API đang chạy ở {API_URL}")
else:
    st.info("Chọn ảnh mẫu hoặc tải ảnh lên rồi bấm **Dự đoán bằng CNN**.")
