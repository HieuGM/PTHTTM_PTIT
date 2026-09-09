# -*- coding: utf-8 -*-
"""
ỨNG DỤNG DỰ ĐOÁN TIỂU ĐƯỜNG (DEEP LEARNING) — Web UI (Assignment 03, App 1)
Môn học: Intelligent System Development

Kiến trúc: Streamlit UI → REST API FastAPI /predict (PyTorch MLP) → hiển thị.
API_URL qua biến môi trường DIABETES_API_URL (mặc định localhost:8011).
"""
import json
import os
import urllib.request
import streamlit as st

API_URL = os.environ.get("DIABETES_API_URL", "http://localhost:8011")

st.set_page_config(page_title="Dự đoán tiểu đường (DL) — ISD Assignment 03",
                   page_icon="🩸", layout="wide")


def call_api(payload: dict) -> dict:
    """POST /predict tới FastAPI — web UI KHÔNG chứa model."""
    req = urllib.request.Request(
        f"{API_URL}/predict",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


st.title("🩸 Hệ Dự đoán Tiểu đường — Deep Learning (CDC 253,680)")
st.caption(
    "Assignment 03 — Neural Networks & Representation Learning | "
    "PyTorch MLP 21→64→32→1 (learned representation) | "
    "Dataset: CDC BRFSS 2015 (lớn ×330 lần PIMA của A02)"
)

with st.expander("ℹ️ Kiến trúc hệ thống"):
    st.markdown(
        """
```
Streamlit UI (file này) ──JSON──▶ FastAPI /predict ──▶ StandardScaler → PyTorch MLP ──▶ sigmoid
   (WEB CLIENT)                      (REST API)        (SAVED .pth từ notebook)          │
      ▲                                                                                     │
      └──────────────── JSON {prediction, confidence, probability} ◀───────────────────────┘
```
Khác biệt Assignment 02: model không còn là RandomForest trên human features mà là
**MLP tự học representation** h₁∈R⁶⁴ → h₂∈R³² từ 21 feature thô (Slide 03 trang 11).
    """
    )

st.subheader("Nhập 21 chỉ số sức khỏe (BRFSS)")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Tình trạng y tế**")
    highbp = st.selectbox("Cao huyết áp", [0, 1], format_func=lambda v: "Có" if v else "Không")
    highchol = st.selectbox("Cao cholesterol", [0, 1], format_func=lambda v: "Có" if v else "Không")
    cholcheck = st.selectbox("Xét nghiệm cholesterol 5 năm", [1, 0],
                             format_func=lambda v: "Có" if v else "Không")
    bmi = st.number_input("BMI (kg/m²)", 10.0, 100.0, 27.0, 0.5)
    smoker = st.selectbox("Hút thuốc (≥100 điếu)", [0, 1], format_func=lambda v: "Có" if v else "Không")
    stroke = st.selectbox("Từng đột quỵ", [0, 1], format_func=lambda v: "Có" if v else "Không")
    heart = st.selectbox("Bệnh tim / đau tim", [0, 1], format_func=lambda v: "Có" if v else "Không")
with c2:
    st.markdown("**Lối sống**")
    phys = st.selectbox("Vận động (30 ngày qua)", [1, 0], format_func=lambda v: "Có" if v else "Không")
    fruits = st.selectbox("Ăn trái cây mỗi ngày", [1, 0], format_func=lambda v: "Có" if v else "Không")
    veggies = st.selectbox("Ăn rau mỗi ngày", [1, 0], format_func=lambda v: "Có" if v else "Không")
    alcohol = st.selectbox("Uống nhiều rượu", [0, 1], format_func=lambda v: "Có" if v else "Không")
    genhlth = st.slider("Sức khỏe tổng quát (1 xấu → 5 tốt)", 1, 5, 3)
    menthlth = st.slider("Số ngày tinh thần kém / 30 ngày", 0, 30, 0)
    physHlth = st.slider("Số ngày thể chất kém / 30 ngày", 0, 30, 0)
with c3:
    st.markdown("**Thông tin cá nhân**")
    diffwalk = st.selectbox("Khó đi bộ / leo cầu thang", [0, 1],
                            format_func=lambda v: "Có" if v else "Không")
    sex = st.selectbox("Giới tính", [0, 1], format_func=lambda v: "Nam" if v else "Nữ")
    age = st.select_slider("Nhóm tuổi", range(1, 14),
                           value=6,
                           format_func=lambda v: f"{18 + (v-1)*5}+")
    education = st.slider("Học vấn (1→6)", 1, 6, 4)
    income = st.slider("Thu nhập (1→8)", 1, 8, 5)
    anyhc = st.selectbox("Có bảo hiểm y tế", [1, 0], format_func=lambda v: "Có" if v else "Không")
    nodoc = st.selectbox("Không khám được vì giá", [0, 1],
                         format_func=lambda v: "Có" if v else "Không")

payload = {
    "HighBP": highbp, "HighChol": highchol, "CholCheck": cholcheck, "BMI": float(bmi),
    "Smoker": smoker, "Stroke": stroke, "HeartDiseaseorAttack": heart,
    "PhysActivity": phys, "Fruits": fruits, "Veggies": veggies,
    "HvyAlcoholConsump": alcohol, "AnyHealthcare": anyhc, "NoDocbcCost": nodoc,
    "GenHlth": genhlth, "MentHlth": menthlth, "PhysHlth": physHlth,
    "DiffWalk": diffwalk, "Sex": sex, "Age": age, "Education": education, "Income": income,
}

st.divider()
if st.button("🔍 Dự đoán bằng Deep Learning MLP", type="primary", use_container_width=True):
    try:
        with st.spinner("Đang gọi API..."):
            res = call_api(payload)
        col1, col2 = st.columns([2, 3])
        with col1:
            if res["prediction"] == "diabetic":
                st.error(f"⚠️ {res['prediction_label_vi']}")
            else:
                st.success(f"✅ {res['prediction_label_vi']}")
            st.metric("Độ tin cậy", f"{res['confidence']:.1%}")
        with col2:
            st.markdown("**Phân phối xác suất**")
            p = res["probability_diabetic"]
            st.progress(p, text=f"P(tiểu đường) = {p:.1%}  |  P(khỏe) = {1-p:.1%}")
            if 0.35 <= p <= 0.65:
                st.warning("Vùng mơ hồ (0.35–0.65) — khuyến nghị xét nghiệm HbA1c xác nhận.")
        st.caption(f"Model: {res['model']} | Test metrics: {res['metrics_test']}")
    except Exception as e:
        st.error(f"Không gọi được API ({e}). Kiểm tra API đang chạy ở {API_URL}")
