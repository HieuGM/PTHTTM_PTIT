# -*- coding: utf-8 -*-
"""
NHẬN DẠNG VẬT THỂ CIFAR-10 (CNN + SE attention) — Web UI (Assignment 04, App 2)
Môn học: Intelligent System Development

Kiến trúc: Streamlit UI → REST API FastAPI /predict (PyTorch M4 SE-CNN) → hiển thị.
API_URL qua biến môi trường CIFAR_API_URL (mặc định localhost:8015).
"""
import io
import json
import os
import urllib.request

import numpy as np
import streamlit as st

API_URL = os.environ.get("CIFAR_API_URL", "http://localhost:8015")

st.set_page_config(page_title="Nhận dạng vật thể CIFAR-10 — ISD Assignment 04",
                   page_icon="🖼️", layout="wide")


def call_api(path, payload=None):
    """GET/POST tới FastAPI — web UI KHÔNG chứa model."""
    if payload is None:
        with urllib.request.urlopen(f"{API_URL}{path}", timeout=60) as r:
            return json.loads(r.read())
    req = urllib.request.Request(f"{API_URL}{path}", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


st.title("🖼️ Hệ Nhận dạng Vật thể CIFAR-10 — CNN cải tiến (M4: SE attention)")
st.caption("Assignment 04 — Models improved from CNN | PyTorch M4: Conv+BN+**Residual**+"
           "**SE attention** (experiment M1→M4, tutorial §45) | 60,000 ảnh 32×32×3")

with st.expander("ℹ️ Kiến trúc hệ thống"):
    st.markdown("""
```
Streamlit UI (file này) ──JSON 32×32×3──▶ FastAPI /predict ──▶ PyTorch SE-CNN ──▶ softmax 10 lớp
   (WEB CLIENT)                            (REST API :8015)      (cifar_m4_se.pth)
```
M4 = M3(+Residual $y=F(x)+x$) + SE attention $Y=X\\odot s$ — so sánh M1→M4 ở notebook 02.
""")

tab_sample, tab_upload = st.tabs(["🖼️ Chọn ảnh mẫu từ tập test", "⬆️ Tải ảnh lên"])

image = None
with tab_sample:
    try:
        smp = call_api("/samples?n=12")["samples"]
        pick = st.selectbox("Ảnh mẫu", range(len(smp)),
                            format_func=lambda i: f"#{smp[i]['index']} — {smp[i]['label_name']}")
        img_np = np.array(smp[pick]["image"], dtype=np.float32)
        st.image(img_np, caption=f"Ảnh test #{smp[pick]['index']} (nhãn thật: {smp[pick]['label_name']})",
                 width=200)
        image = [[[round(float(v), 4) for v in px] for px in row] for row in img_np]
    except Exception as e:
        st.error(f"Không lấy được mẫu từ API ({e}). Kiểm tra API đang chạy ở {API_URL}")

with tab_upload:
    up = st.file_uploader("Tải ảnh vật thể (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if up is not None:
        from PIL import Image
        pil = Image.open(io.BytesIO(up.getvalue())).convert("RGB")
        st.image(pil, caption="Ảnh gốc", width=200)
        arr = np.array(pil.resize((32, 32)), dtype=np.float32) / 255.0
        st.image(arr, caption="Sau khi resize 32×32×3", width=200)
        image = [[[round(float(v), 4) for v in px] for px in row] for row in arr]

st.divider()
if image is not None and st.button("🔍 Dự đoán bằng SE-CNN", type="primary", use_container_width=True):
    try:
        with st.spinner("Đang gọi API..."):
            res = call_api("/predict", {"image": image})
        c1, c2 = st.columns([1, 2])
        with c1:
            st.success(f"🎯 {res['prediction_label_vi'].upper()}")
            st.metric("Độ tin cậy", f"{res['confidence']:.1%}")
        with c2:
            probs = res["probabilities"]
            st.bar_chart({"x": list(probs.keys()), "y": list(probs.values())},
                         x="x", y="y", use_container_width=True)
        st.caption(f"Model: {res['model']} | Test accuracy: {res['metrics_test']}")
    except Exception as e:
        st.error(f"Lỗi gọi API ({e}). Kiểm tra API đang chạy ở {API_URL}")
else:
    st.info("Chọn ảnh mẫu hoặc tải ảnh lên rồi bấm **Dự đoán bằng SE-CNN**.")
