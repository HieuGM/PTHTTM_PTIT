# -*- coding: utf-8 -*-
"""
ỨNG DỤNG PHÂN TÍCH CẢM XÚC COMMENT (DEEP LEARNING) — Web UI (Assignment 03, App 3)
Streamlit UI → REST API FastAPI /predict (TF-IDF 5000 + PyTorch MLP 3 lớp) → hiển thị.
API_URL qua biến môi trường COMMENTS_API_URL (mặc định localhost:8013).
"""
import json
import os
import urllib.request
import streamlit as st

API_URL = os.environ.get("COMMENTS_API_URL", "http://localhost:8013")

st.set_page_config(page_title="Phân tích cảm xúc comment (DL) — ISD Assignment 03",
                   page_icon="💬", layout="wide")


def call_api(payload: dict) -> dict:
    req = urllib.request.Request(
        f"{API_URL}/predict",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


st.title("💬 Phân tích Cảm xúc Comment — Deep Learning")
st.caption(
    "Assignment 03 — Amazon Fine Food Reviews (100k từ 568,454) | "
    "TF-IDF 5000D → PyTorch MLP 5000→64→32→3 (learned sentiment representation)"
)

with st.expander("ℹ️ Kiến trúc hệ thống"):
    st.markdown(
        """
```
Comment ──▶ clean/lowercase ──▶ Tokens ──▶ Token IDs (vocab 5000) ──▶ TF-IDF ──▶ MLP ──▶ softmax
                                                                                          │
Streamlit UI ──JSON──▶ FastAPI /predict ◀──────────── {neg, neutral, pos} + probs ◀──────┘
```
Pipeline text giữ nguyên 4 bước A02 (Comment → Tokens → IDs → Embeddings);
điểm mới A03: MLP **học transformation** của TF-IDF (h₁∈R⁶⁴ → h₂∈R³²) thay vì đưa thẳng vào SVM.
    """
    )

st.subheader("Nhập comment sản phẩm (tiếng Anh)")
default_text = ("Best granola I have ever bought. Crunchy, fresh and not too sweet. "
                "Will order again!")
comment = st.text_area("Comment", value=default_text, height=140,
                       help="Mô hình huấn luyện trên review Amazon tiếng Anh")

examples = {
    "Tích cực": "Amazing product! Great taste and fast delivery. Five stars!",
    "Trung lập": "The taste is okay, nothing special. Probably won't buy again but it's fine for the price.",
    "Tiêu cực": "Terrible. Arrived melted and stale. Customer service ignored my emails. Waste of money.",
}
c1, c2, c3 = st.columns(3)
if c1.button("Ví dụ tích cực"):
    comment = examples["Tích cực"]
if c2.button("Ví dụ trung lập"):
    comment = examples["Trung lập"]
if c3.button("Ví dụ tiêu cực"):
    comment = examples["Tiêu cực"]

st.divider()
if st.button("🔍 Phân tích cảm xúc bằng Deep Learning", type="primary",
             use_container_width=True):
    if len(comment.strip()) < 2:
        st.warning("Comment quá ngắn.")
    else:
        try:
            with st.spinner("Đang gọi API..."):
                r = call_api({"comment": comment})
            icon = {"negative": "😞", "neutral": "😐", "positive": "😊"}
            if r["prediction"] == "positive":
                st.success(f"{icon['positive']} {r['prediction_label_vi']} — "
                           f"độ tin cậy {r['confidence']:.1%}")
            elif r["prediction"] == "negative":
                st.error(f"{icon['negative']} {r['prediction_label_vi']} — "
                         f"độ tin cậy {r['confidence']:.1%}")
            else:
                st.info(f"{icon['neutral']} {r['prediction_label_vi']} — "
                        f"độ tin cậy {r['confidence']:.1%}")

            st.markdown("**Xác suất từng lớp**")
            cols = st.columns(3)
            probs = r["probabilities"]
            cols[0].metric("😞 Tiêu cực", f"{probs['negative']:.1%}")
            cols[1].metric("😐 Trung lập", f"{probs['neutral']:.1%}")
            cols[2].metric("😊 Tích cực", f"{probs['positive']:.1%}")
            st.caption(f"Model: {r['model']} | Test metrics: {r.get('metrics_test', {})}")
        except Exception as e:
            st.error(f"Không gọi được API ({e}). Kiểm tra API đang chạy ở {API_URL}")
