# -*- coding: utf-8 -*-
"""
ỨNG DỤNG ĐỊNH GIÁ NHÀ — Web UI (Assignment 02, App 2)
Môn học: Intelligent System Development

Kiến trúc: Streamlit UI → (gọi REST API FastAPI /predict) → hiển thị giá dự đoán.
API_URL cấu hình qua biến môi trường HOUSE_API_URL (mặc định localhost:8002).
"""
import json
import os
import urllib.request
import streamlit as st

API_URL = os.environ.get("HOUSE_API_URL", "https://house-api-odk5.onrender.com")

st.set_page_config(page_title="Định giá nhà — ISD Assignment 02",
                   page_icon="🏠", layout="wide")


def call_api(payload: dict) -> dict:
    req = urllib.request.Request(
        f"{API_URL}/predict",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


st.title("🏠 Hệ Định giá Nhà — Quận King (Seattle)")
st.caption(
    "Assignment 02 — Intelligent System Development | GradientBoosting | "
    "Dataset: KC House Sales (Kaggle, 21,613 giao dịch) | Test: R² 0.90, MAE $68k"
)

with st.expander("ℹ️ Kiến trúc hệ thống"):
    st.markdown(
        """
```
Streamlit UI ──JSON──▶ FastAPI /predict ──▶ ColumnTransformer(scale + one-hot 70 zipcode)
   (WEB)                                     → GradientBoosting (log-target) → expm1 → Giá USD
```
Cùng một pipeline đã lưu từ notebook — preprocessing fit trên TRAIN, chỉ transform lúc inference.
    """
    )

st.subheader("Nhập đặc điểm căn nhà")

left, right = st.columns(2)
with left:
    st.markdown("**Diện tích & cấu trúc**")
    sqft_living = st.number_input("Diện tích sống (sqft)", 300, 10000, 1340)
    sqft_lot = st.number_input("Diện tích lô đất (sqft)", 500, 200000, 5650)
    sqft_above = st.number_input("Diện tích trên mặt đất (sqft)", 0, 10000, 1340)
    sqft_basement = st.number_input("Diện tích tầng hầm (sqft)", 0, 5000, 0)
    bedrooms = st.number_input("Số phòng ngủ", 0, 15, 3)
    bathrooms = st.number_input("Số vệ sinh", 0.0, 10.0, 1.5, 0.5)
    floors = st.number_input("Số tầng", 1.0, 4.0, 1.0, 0.5)

with right:
    st.markdown("**Chất lượng & vị trí**")
    waterfront = st.radio("View mặt nước", ["Không (0)", "Có (1)"], horizontal=True)
    view = st.select_slider("Cấp view (0–4)", options=[0, 1, 2, 3, 4], value=0)
    condition = st.select_slider("Tình trạng (1–5)", options=[1, 2, 3, 4, 5], value=4)
    grade = st.select_slider("Grade chất lượng (1–13)", options=list(range(1, 14)), value=7)
    yr_built = st.number_input("Năm xây", 1900, 2015, 1976)
    yr_renovated = st.number_input("Năm cải tạo (0 = chưa)", 0, 2015, 0)
    zipcode = st.selectbox(
        "Zipcode (chọn vùng King County)",
        [98001, 98002, 98003, 98004, 98005, 98006, 98007, 98008, 98010, 98011,
         98014, 98019, 98022, 98023, 98024, 98027, 98028, 98029, 98030, 98031,
         98032, 98033, 98034, 98038, 98039, 98040, 98042, 98045, 98050, 98052,
         98053, 98055, 98056, 98057, 98058, 98059, 98065, 98070, 98072, 98074,
         98075, 98077, 98092, 98102, 98103, 98105, 98106, 98107, 98108, 98109,
         98112, 98115, 98116, 98117, 98118, 98119, 98122, 98125, 98126, 98133,
         98136, 98144, 98146, 98148, 98155, 98166, 98168, 98177, 98178, 98188,
         98198, 98199], index=25)
    lat = st.number_input("Vĩ độ", 47.0, 47.8, 47.61, 0.001)
    long_ = st.number_input("Kinh độ", -122.6, -121.0, -122.29, 0.001)

payload = {
    "sqft_living": float(sqft_living), "sqft_lot": float(sqft_lot),
    "sqft_above": float(sqft_above), "sqft_basement": float(sqft_basement),
    "bedrooms": int(bedrooms), "bathrooms": float(bathrooms),
    "floors": float(floors), "waterfront": 0 if waterfront.startswith("Không") else 1,
    "view": int(view), "condition": int(condition), "grade": int(grade),
    "yr_built": int(yr_built), "yr_renovated": int(yr_renovated),
    "lat": float(lat), "long": float(long_), "zipcode": int(zipcode),
}

st.divider()

if st.button("💰 Định giá qua API", type="primary", use_container_width=True):
    try:
        r = call_api(payload)
        price = r["predicted_price"]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Giá dự đoán", f"${price:,.0f}")
        with col2:
            st.metric("Dải tham chiếu (±12%)", r["confidence_range"])

        st.markdown(
            f"""
            **Diễn giải:** với {int(sqft_living):,} sqft, {int(bedrooms)} phòng ngủ,
            grade {int(grade)}, zipcode **{int(zipcode)}** — model ước giá trung bình
            **${price:,.0f}**. Sai số điển hình trên test: MAE ≈ $68k (nhà phổ thông chính xác
            hơn nhà siêu sang).
            """
        )
        if price > 2_000_000:
            st.warning("⚠️ Phân khúc cao cấp (> $2M): model kém tin cậy hơn — dữ liệu hiếm trong train.")
    except Exception as e:
        st.error(f"Không gọi được API tại `{API_URL}` — chạy `uvicorn main:app --port 8002`. Lỗi: {e}")

st.divider()
st.subheader("🎬 Demo nhanh — 3 phân khúc")
cols = st.columns(3)
presets = {
    "Nhà phổ thông (98103)": {
        "sqft_living": 1340, "sqft_lot": 5650, "sqft_above": 1340, "sqft_basement": 0,
        "bedrooms": 3, "bathrooms": 1.5, "floors": 1.0, "waterfront": 0, "view": 0,
        "condition": 4, "grade": 7, "yr_built": 1976, "yr_renovated": 0,
        "lat": 47.61, "long": -122.29, "zipcode": 98103},
    "Nhà cao cấp (98039)": {
        "sqft_living": 4600, "sqft_lot": 12000, "sqft_above": 3800, "sqft_basement": 800,
        "bedrooms": 5, "bathrooms": 3.5, "floors": 2.0, "waterfront": 1, "view": 4,
        "condition": 4, "grade": 11, "yr_built": 1998, "yr_renovated": 2010,
        "lat": 47.63, "long": -122.23, "zipcode": 98039},
    "Nhà cấp thấp (98002)": {
        "sqft_living": 780, "sqft_lot": 4000, "sqft_above": 780, "sqft_basement": 0,
        "bedrooms": 2, "bathrooms": 1.0, "floors": 1.0, "waterfront": 0, "view": 0,
        "condition": 3, "grade": 5, "yr_built": 1955, "yr_renovated": 0,
        "lat": 47.29, "long": -122.25, "zipcode": 98002},
}
for col, (name, p) in zip(cols, presets.items()):
    with col:
        if st.button(name, key=name):
            try:
                r = call_api(p)
                st.success(f"**${r['predicted_price']:,.0f}**")
                st.caption(r["confidence_range"])
            except Exception as e:
                st.error(f"Lỗi API: {e}")

st.divider()
st.markdown("<sub>Assignment 02 — App 2 | Web client gọi REST API FastAPI</sub>",
            unsafe_allow_html=True)
