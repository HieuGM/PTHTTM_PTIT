# -*- coding: utf-8 -*-
"""
ỨNG DỤNG ĐỊNH GIÁ BĐS NEW YORK (DEEP LEARNING) — Web UI (Assignment 03, App 2)
Streamlit UI → REST API FastAPI /predict (PyTorch MLP trên one-hot 133D) → hiển thị.
API_URL qua biến môi trường HOUSE_API_URL (mặc định localhost:8012).
"""
import json
import os
import urllib.request
import streamlit as st

API_URL = os.environ.get("HOUSE_API_URL", "http://localhost:8012")

st.set_page_config(page_title="Định giá BĐS NYC (DL) — ISD Assignment 03",
                   page_icon="🏠", layout="wide")


def call_api(payload: dict) -> dict:
    req = urllib.request.Request(
        f"{API_URL}/predict",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


st.title("🏠 Định giá Bất động sản New York — Deep Learning")
st.caption(
    "Assignment 03 — NYC Rolling Sales 84,548 giao dịch (lớn ×4 KC House A02) | "
    "PyTorch MLP 133→64→32→1, target log10(price)"
)

with st.expander("ℹ️ Kiến trúc hệ thống"):
    st.markdown(
        """
```
Streamlit UI ──JSON──▶ FastAPI /predict ──▶ one-hot(133D) + scale → PyTorch MLP → 10^log10(price)
 (WEB CLIENT)             (REST API)           (representation contract)                    │
    ▲                                                                                          │
    └────────────────── JSON {predicted_price_usd, price_range} ◀──────────────────────────────┘
```
    """
    )

st.subheader("Đặc tính bất động sản")

left, right = st.columns(2)
with left:
    boroughs = {1: "Manhattan", 2: "Bronx", 3: "Brooklyn", 4: "Queens", 5: "Staten Island"}
    b_opt = st.selectbox("Borough (quận)", list(boroughs.keys()),
                         format_func=lambda v: boroughs[v], index=2)
    bldg_classes = [
        "01 ONE FAMILY DWELLINGS", "02 TWO FAMILY DWELLINGS", "03 THREE FAMILY DWELLINGS",
        "04 TAX CLASS 1 CONDOS", "06 TAX CLASS 1 OTHERS",
        "07 RENTALS - WALKUP APARTMENTS", "08 RENTALS - ELEVATOR APARTMENTS",
        "09 COOPS - WALKUP APARTMENTS", "10 COOPS - ELEVATOR APARTMENTS",
        "12 CONDOS - WALKUP APARTMENTS", "13 CONDOS - ELEVATOR APARTMENTS",
        "15 CONDOS - 2-10 UNIT RESIDENTIAL",
    ]
    bldg = st.selectbox("Loại bất động sản", bldg_classes, index=0)
    zip_ = st.number_input("ZIP code", 10001, 11697, 11211)
with right:
    res = st.number_input("Số căn hộ (residential units)", 0.0, 500.0, 3.0, 1.0)
    com = st.number_input("Số đơn vị thương mại", 0.0, 500.0, 0.0, 1.0)
    land = st.number_input("Diện tích đất (sq ft) — 0 nếu không biết", 0.0, 5000000.0, 2000.0, 100.0)
    gross = st.number_input("Tổng diện tích sàn (sq ft)", 100.0, 2000000.0, 1800.0, 100.0)
    year = st.number_input("Năm xây (0 nếu không biết)", 0.0, 2025.0, 1940.0, 5.0)
    tax = st.selectbox("Lớp thuế", [1, 2, 4], index=0)

payload = {
    "borough": int(b_opt), "bldg_class": bldg, "zip": int(zip_),
    "res_units": float(res), "com_units": float(com),
    "land_sf": float(land) if land > 0 else None,
    "gross_sf": float(gross),
    "year_built": float(year) if year > 0 else None,
    "tax_class": int(tax),
}

st.divider()
if st.button("💰 Định giá bằng Deep Learning MLP", type="primary", use_container_width=True):
    try:
        with st.spinner("Đang gọi API..."):
            r = call_api(payload)
        st.success(f"Giá dự đoán: **{r['predicted_price_display']}**")
        lo, hi = r["price_range"]
        st.caption(f"Khoảng tham khảo (±30-40%): ${lo:,.0f} – ${hi:,.0f}")
        st.caption(f"Model: {r['model']} | Test metrics: {r.get('metrics_test', {})}")
    except Exception as e:
        st.error(f"Không gọi được API ({e}). Kiểm tra API đang chạy ở {API_URL}")
