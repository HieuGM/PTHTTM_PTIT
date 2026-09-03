# -*- coding: utf-8 -*-
"""
ỨNG DỤNG PHÁT HIỆN SỞ THÍCH KHÁCH HÀNG — Web UI (Assignment 02, App 3)
Môn học: Intelligent System Development

Kiến trúc: Streamlit UI → (gọi REST API FastAPI /predict) → interest + confidence.
API_URL cấu hình qua biến môi trường CUSTOMER_API_URL (mặc định localhost:8003).
"""
import json
import os
import urllib.request
import streamlit as st

API_URL = os.environ.get("CUSTOMER_API_URL", "https://customer-api-8is4.onrender.com")

st.set_page_config(page_title="Sở thích khách hàng — ISD Assignment 02",
                   page_icon="🛒", layout="wide")


def call_api(payload: dict) -> dict:
    req = urllib.request.Request(
        f"{API_URL}/predict",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


st.title("🛒 Hệ Phát hiện Sở thích Khách hàng E-commerce")
st.caption(
    "Assignment 02 — Intelligent System Development | Linear SVM (TF-IDF + RFM) | "
    "Dataset: Online Retail (Kaggle, 55k giao dịch, 1,033 khách) | Test macro-F1 0.37"
)

with st.expander("ℹ️ Kiến trúc hệ thống — text representation pipeline"):
    st.markdown(
        """
```
Streamlit UI ──JSON──▶ FastAPI /predict
                          ├─ RFM 5 chỉ số → log + StandardScaler (đã lưu từ train)
                          ├─ basket_text  → Tokens → Token IDs → TF-IDF weights (đã lưu từ train)
                          └─ Hợp nhất [tabular ⊕ text 4000 chiều] → Linear SVM → interest
```
**Pipeline text (Lecture 02):** Comment → Tokens → Token IDs → Vector/Embedding.
Từ vựng + idf weights học **chỉ trên train set**, transform cho khách mới — không leakage.
    """
    )

st.subheader("Nhập hồ sơ hành vi khách hàng")

left, right = st.columns(2)
with left:
    st.markdown("**Chỉ số RFM (hành vi)**")
    recency = st.number_input("Recency — số ngày từ đơn gần nhất", 0, 400, 5)
    frequency = st.number_input("Frequency — số đơn hàng", 1, 100, 4)
    monetary = st.number_input("Monetary — tổng chi tiêu (USD)", 1.0, 100000.0, 665.0, 10.0)
    total_items = st.number_input("Tổng sản phẩm đã mua", 1, 50000, 403)
    avg_order = st.number_input("Giá trị TB 1 dòng đơn (USD)", 0.5, 500.0, 12.0, 0.5)

with right:
    st.markdown("**Văn bản giỏ hàng (dấu hiệu sở thích)**")
    basket = st.text_area(
        "Tên/mô tả các sản phẩm khách đã mua",
        value="white hanging heart t-light holder metal lantern candle holder vintage",
        height=150,
        help="Chính là 'comment' của khách — hệ thống sẽ Tokens → Token IDs → TF-IDF → dự đoán interest.",
    )

payload = {
    "recency_days": int(recency), "frequency": int(frequency),
    "monetary": float(monetary), "total_items": int(total_items),
    "avg_order_value": float(avg_order), "basket_text": basket,
}

st.divider()

if st.button("🎯 Dự đoán sở thích qua API", type="primary", use_container_width=True):
    try:
        r = call_api(payload)
        interest = r["interest"]
        conf = r["confidence"]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Interest dự đoán", interest)
        with col2:
            st.metric("Confidence", f"{conf:.1%}")

        st.markdown("**Top-3 phân khúc sở thích (xác suất):**")
        for item in r["top3_interests"]:
            st.progress(min(item["probability"], 1.0),
                        text=f"{item['interest']}: {item['probability']:.1%}")

        st.info(
            f"**Diễn giải business:** khách này có xu hướng quan tâm nhóm **{interest}** "
            f"(độ tin cậy {conf:.1%}). Ứng dụng: gợi ý sản phẩm nhóm này, gửi ưu đãi targeted, "
            "xếp vào chiến dịch marketing đúng phân khúc."
        )
    except Exception as e:
        st.error(f"Không gọi được API tại `{API_URL}` — chạy `uvicorn main:app --port 8003`. Lỗi: {e}")

st.divider()
st.subheader("🎬 Demo nhanh — 3 khách mẫu")
cols = st.columns(3)
presets = {
    "Khách decor": {
        "recency_days": 5, "frequency": 4, "monetary": 665.0, "total_items": 403,
        "avg_order_value": 12.0,
        "basket_text": "white hanging heart t-light holder metal lantern candle holder vintage"},
    "Khách kitchen": {
        "recency_days": 30, "frequency": 2, "monetary": 245.0, "total_items": 180,
        "avg_order_value": 8.0,
        "basket_text": "set of 3 cake tins serving bowl teacup and saucer picnic plate"},
    "Khách toys": {
        "recency_days": 60, "frequency": 1, "monetary": 55.0, "total_items": 55,
        "avg_order_value": 5.0,
        "basket_text": "plush bunny easter toy party cones candy assorted game puzzle"},
}
for col, (name, p) in zip(cols, presets.items()):
    with col:
        if st.button(name, key=name):
            try:
                r = call_api(p)
                st.success(f"**{r['interest']}** ({r['confidence']:.1%})")
            except Exception as e:
                st.error(f"Lỗi API: {e}")

st.divider()
st.markdown("<sub>Assignment 02 — App 3 | Web client gọi REST API FastAPI | "
            "Text pipeline: Comment → Tokens → IDs → TF-IDF Embedding</sub>",
            unsafe_allow_html=True)
