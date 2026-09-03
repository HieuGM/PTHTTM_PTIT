# -*- coding: utf-8 -*-
"""
ỨNG DỤNG DỰ ĐOÁN TIỂU ĐƯỜNG — Web UI (Assignment 02, App 1)
Môn học: Intelligent System Development

Kiến trúc: Streamlit UI → (gọi REST API FastAPI /predict) → hiển thị kết quả.
API_URL cấu hình qua biến môi trường DIABETES_API_URL (mặc định localhost:8001).
"""
import json
import os
import urllib.request
import streamlit as st

API_URL = os.environ.get("DIABETES_API_URL", "https://diabetes-api-a02.onrender.com")

st.set_page_config(page_title="Dự đoán tiểu đường — ISD Assignment 02",
                   page_icon="🩸", layout="wide")


def call_api(payload: dict) -> dict:
    """POST /predict tới FastAPI — web UI KHÔNG chứa model, chỉ gọi service."""
    req = urllib.request.Request(
        f"{API_URL}/predict",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


st.title("🩸 Hệ Dự đoán Bệnh Tiểu đường — Intelligent System")
st.caption(
    "Assignment 02 — Intelligent System Development | RandomForest 200 cây | "
    "Dataset: Pima Indians Diabetes (Kaggle, 768 bệnh nhân) | "
    "Test: Accuracy 0.74, ROC-AUC 0.81"
)

with st.expander("ℹ️ Kiến trúc hệ thống"):
    st.markdown(
        """
```
Streamlit UI (file này) ──JSON──▶ FastAPI /predict ──▶ Pipeline: impute→scale→RF ──▶ Prediction
   (WEB CLIENT)                      (REST API)             (SAVED MODEL từ notebook)      │
      ▲                                                                        │
      └────────────────── JSON response {prediction, confidence} ◀────────────┘
```
Web và Mobile dùng **cùng một API + cùng preprocessing** như lúc training — nguyên tắc
tránh lệch representation giữa training và serving.
    """
    )

st.subheader("Nhập chỉ số lâm sàng của bệnh nhân")

left, right = st.columns(2)
with left:
    st.markdown("**Thông tin chung**")
    pregnancies = st.number_input("Số lần mang thai", 0, 20, 1)
    glucose = st.number_input("Glucose 2h (mg/dL)", 0, 300, 120)
    blood_pressure = st.number_input("Huyết áp tâm trương (mm Hg)", 0, 200, 70)
    skin_thickness = st.number_input("Độ dày da (mm)", 0, 100, 20)

with right:
    st.markdown("**Chỉ số chuyển hóa**")
    insulin = st.number_input("Insulin 2h (μU/mL) — 0 nếu không đo", 0, 900, 79)
    bmi = st.number_input("BMI (kg/m²)", 0.0, 70.0, 32.0, 0.1)
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.45, 0.01)
    age = st.number_input("Tuổi", 1, 120, 33)

payload = {
    "Pregnancies": int(pregnancies),
    "Glucose": float(glucose),
    "BloodPressure": float(blood_pressure),
    "SkinThickness": float(skin_thickness),
    "Insulin": float(insulin),
    "BMI": float(bmi),
    "DiabetesPedigreeFunction": float(dpf),
    "Age": int(age),
}

st.divider()

if st.button("🩺 Dự đoán qua API", type="primary", use_container_width=True):
    try:
        result = call_api(payload)
        pred = result["prediction"]
        proba = result["probability_diabetic"]
        conf = result["confidence"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Xác suất tiểu đường", f"{proba:.1%}")
        with col2:
            st.metric("Ngưỡng quyết định", "0.50")
        with col3:
            st.metric("Kết luận", "CÓ BỆNH" if pred == "diabetic" else "KHỎE")

        st.progress(min(proba, 1.0))

        if pred == "diabetic":
            st.error(
                f"⚠️ **Rủi ro CAO** — model dự đoán bệnh nhân **có khả năng tiểu đường type 2** "
                f"(xác suất {proba:.1%}). Khuyến nghị: xét nghiệm HbA1c xác nhận."
            )
        else:
            st.success(
                f"✅ **Rủi ro THẤP** — model dự đoán **không có dấu hiệu tiểu đường** "
                f"(xác suất bệnh chỉ {proba:.1%})."
            )

        if 0.35 <= proba <= 0.65:
            st.warning(
                "⚖️ Xác suất trong **vùng mơ hồ** (0.35–0.65) — khuyến nghị xét nghiệm thêm, "
                "không kết luận chỉ dựa vào model."
            )

        st.caption(
            "⚠️ Công cụ hỗ trợ sàng lọc nghiên cứu — KHÔNG thay thế chẩn đoán bác sĩ. "
            "Model học từ 768 bệnh nhân phụ nữ Pima Indian (Kaggle)."
        )
    except Exception as e:
        st.error(f"Không gọi được API tại `{API_URL}` — hãy chạy `uvicorn main:app --port 8001`. "
                 f"Chi tiết: {e}")

st.divider()
st.subheader("🎬 Demo nhanh — 3 case mẫu")
preset_cols = st.columns(3)
presets = {
    "Case 1 — Nguy cơ thấp (27t)": {
        "Pregnancies": 1, "Glucose": 89, "BloodPressure": 66, "SkinThickness": 23,
        "Insulin": 94, "BMI": 26.1, "DiabetesPedigreeFunction": 0.167, "Age": 27},
    "Case 2 — Nguy cơ cao (45t)": {
        "Pregnancies": 6, "Glucose": 183, "BloodPressure": 88, "SkinThickness": 35,
        "Insulin": 230, "BMI": 36.5, "DiabetesPedigreeFunction": 0.72, "Age": 45},
    "Case 3 — Case biên (36t)": {
        "Pregnancies": 3, "Glucose": 130, "BloodPressure": 78, "SkinThickness": 30,
        "Insulin": 0, "BMI": 32.0, "DiabetesPedigreeFunction": 0.4, "Age": 36},
}
for col, (name, p) in zip(preset_cols, presets.items()):
    with col:
        if st.button(name, key=name):
            try:
                r = call_api(p)
                prob = r["probability_diabetic"]
                if r["prediction"] == "diabetic":
                    st.error(f"**CÓ TIỂU ĐƯỜNG** — xác suất {prob:.1%}")
                else:
                    st.success(f"**KHỎE** — xác suất bệnh {prob:.1%}")
                st.progress(min(prob, 1.0))
            except Exception as e:
                st.error(f"Lỗi API: {e}")

st.divider()
st.markdown(
    "<sub>Assignment 02 — App 1 | Web client gọi REST API FastAPI | Deploy: HF Spaces (web) + "
    "Render (API)</sub>",
    unsafe_allow_html=True,
)
