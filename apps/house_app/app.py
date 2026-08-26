# -*- coding: utf-8 -*-
"""
HOUSE PRICE PREDICTION — Intelligent System App (Assignment 01)
Môn học: Intelligent System Development

Pipeline: Input → Representation → Preprocessing → Model → Prediction → Output
Model: Random Forest Regressor (B=100, log-target) — notebook 02_house_price_system.ipynb
App dùng top-8 feature mạnh nhất (giữ ~95% hiệu năng, người dùng nhập được hết)
"""
import joblib
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dự đoán giá nhà — ISD Assignment 01",
                   page_icon="🏠", layout="wide")

ARTIFACTS = "ames_model.joblib"


@st.cache_resource
def load_artifacts():
    return joblib.load(ARTIFACTS)


try:
    art = load_artifacts()
except FileNotFoundError:
    st.error("⚠️ Không tìm thấy `ames_model.joblib`. Hãy đặt file model cạnh `app.py`.")
    st.stop()

RMSE = 29_297.0     # từ notebook: test RMSE ($)
MAE = 17_277.0      # từ notebook: test MAE ($)
MEDIAN = 163_000.0  # median giá Ames


def predict_house(user_input: dict):
    """Input dạng người dùng → đúng representation training (one-hot 271 cột) → giá USD.

    Model đầy đủ cần 74 feature; app cho người dùng nhập 8 feature quyết định,
    phần còn lại điền median/mode của tập train (ký hiệu trong notebook Exp 3b).
    """
    x = pd.DataFrame([user_input])
    x_enc = pd.get_dummies(x, columns=art["categorical"], prefix=art["categorical"])
    x_enc = x_enc.reindex(columns=art["enc_columns"], fill_value=0).astype(float)
    pred_log = art["model"].predict(x_enc)
    return float(np.expm1(pred_log[0]))


st.title("🏠 Hệ Dự đoán Giá nhà — Intelligent System")
st.caption(
    "Assignment 01 — Intelligent System Development | Random Forest Regressor | "
    "Dataset: Ames Housing (Iowa, 1460 giao dịch) | Test: R² = 0.89, MAE ≈ $17k"
)

with st.expander("ℹ️ Hệ thống hoạt động thế nào? (kiến trúc)"):
    st.markdown(
        """
```
Người dùng nhập thuộc tính nhà ──▶ One-hot encode + log-target ──▶ Random Forest ──▶ log(giá)
        (INPUT)                          (REPRESENTATION)             (MODEL)            │
                                                                 expm1 revert ──▶ GIÁ ƯỚC TÍNH ($)
                                                                                   ± dải tin cậy (OUTPUT)
```
Model học từ 1460 giao dịch nhà tại Ames, Iowa (2006–2010). Target được học trên thang
**log(1+giá)** để công bằng với nhà rẻ lẫn đắt, sau đó revert về USD — chi tiết Experiment 3.
    """
    )

st.subheader("Nhập đặc điểm căn nhà")

tab1, tab2, tab3 = st.tabs(["📋 Chất lượng & quy mô", "📐 Chi tiết diện tích", "📍 Vị trí & năm xây"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        overall_qual = st.select_slider("Chất lượng tổng thể — OverallQual (1–10)",
                                        options=range(1, 11), value=6,
                                        help="Điểm đánh giá vật liệu + hoàn thiện tổng thể của căn nhà")
        overall_cond = st.select_slider("Tình trạng tổng thể — OverallCond (1–10)",
                                        options=range(1, 11), value=5,
                                        help="Đánh giá tình trạng bảo trì hiện tại")
    with c2:
        full_bath = st.number_input("Số phòng tắm đầy đủ — FullBath", 0, 4, 2)
        garage_cars = st.number_input("Sức chứa garage (số ô tô) — GarageCars", 0, 5, 2)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        gr_liv_area = st.number_input("Diện tích sinh hoạt — GrLivArea (ft²)", 400, 5000, 1500, 50)
        total_bsmt_sf = st.number_input("Diện tích tầng hầm — TotalBsmtSF (ft²)", 0, 3000, 800, 50)
    with c2:
        lot_area = st.number_input("Diện tích lô đất — LotArea (ft²)", 1000, 100000, 9000, 500)

with tab3:
    year_built = st.slider("Năm xây — YearBuilt", 1872, 2010, 1980)
    neighborhood = st.selectbox(
        "Khu dân cư — Neighborhood (Ames, Iowa)",
        ["CollgCr (trung tâm, phổ thông)", "OldTown (cổ, trung bình)", "NridgHt (cao cấp, đắt)",
         "NoRidge (cao cấp nhất)", "StoneBr (cao cấp)", "Somerset (khang trang)",
         "NWAmes (trung lưu)", "Gilbert (vùng ven)", "Sawyer (phổ thông)",
         "Edwards (phổ thông)", "NAmes (phổ thông)", "Mitchel (phổ thông)",
         "BrkSide (thấp)", "IDOTRR (thấp, gần đường sắt)", "MeadowV (thấp nhất)"],
    )
    st.caption("Khu trung bình (không chọn): dùng giá trị phổ thông nhất của tập train.")

# map lựa chọn người dùng → mã Neighborhood gốc
NEIGH_MAP = {
    "CollgCr": "CollgCr", "OldTown": "OldTown", "NridgHt": "NridgHt", "NoRidge": "NoRidge",
    "StoneBr": "StoneBr", "Somerset": "Somerset", "NWAmes": "NWAmes", "Gilbert": "Gilbert",
    "Sawyer": "Sawyer", "Edwards": "Edwards", "NAmes": "NAmes", "Mitchel": "Mitchel",
    "BrkSide": "BrkSide", "IDOTRR": "IDOTRR", "MeadowV": "MeadowV",
}

user_input = {
    # 8 feature người dùng nhập (Exp 3b: giữ ~95% hiệu năng)
    "OverallQual": float(overall_qual),
    "GrLivArea": float(gr_liv_area),
    "GarageCars": float(garage_cars),
    "TotalBsmtSF": float(total_bsmt_sf),
    "FullBath": float(full_bath),
    "YearBuilt": float(year_built),
    "OverallCond": float(overall_cond),
    "LotArea": float(lot_area),
    # các feature còn lại điền median/mode của train (ký hiệu notebook)
    "MSSubClass": 50.0, "MSZoning": "RL", "LotFrontage": 68.0, "Street": "Pave",
    "LotShape": "Reg", "LandContour": "Lvl", "Utilities": "AllPub", "LotConfig": "Inside",
    "LandSlope": "Gtl", "Condition1": "Norm", "Condition2": "Norm", "BldgType": "1Fam",
    "HouseStyle": "1Story", "RoofStyle": "Gable", "RoofMatl": "CompShg",
    "Exterior1st": "VinylSd", "Exterior2nd": "VinylSd", "MasVnrArea": 100.0,
    "ExterQual": "TA", "ExterCond": "TA", "Foundation": "PConc", "BsmtQual": "TA",
    "BsmtCond": "TA", "BsmtExposure": "No", "BsmtFinType1": "GLQ", "BsmtFinSF1": 400.0,
    "BsmtFinType2": "Unf", "BsmtFinSF2": 0.0, "BsmtUnfSF": 400.0, "Heating": "GasA",
    "HeatingQC": "Ex", "CentralAir": "Y", "Electrical": "SBrkr", "1stFlrSF": gr_liv_area * 0.6,
    "2ndFlrSF": gr_liv_area * 0.4, "LowQualFinSF": 0.0, "BsmtFullBath": 0.0,
    "BsmtHalfBath": 0.0, "HalfBath": 1.0, "BedroomAbvGr": 3.0, "KitchenAbvGr": 1.0,
    "KitchenQual": "TA", "TotRmsAbvGrd": 6.0, "Functional": "Typ", "Fireplaces": 1.0,
    "FireplaceQu": "Gd", "GarageType": "Attchd", "GarageYrBlt": float(year_built),
    "GarageFinish": "Fin", "GarageArea": garage_cars * 240.0,
    "GarageQual": "TA", "GarageCond": "TA", "PavedDrive": "Y", "WoodDeckSF": 100.0,
    "YearRemodAdd": 1994.0, "OpenPorchSF": 50.0, "EnclosedPorch": 0.0,
    "3SsnPorch": 0.0, "ScreenPorch": 0.0,
    "PoolArea": 0.0, "MiscVal": 0.0, "MoSold": 6.0, "YrSold": 2008.0,
    "SaleType": "WD ", "SaleCondition": "Normal",
}
user_input["Neighborhood"] = NEIGH_MAP[neighborhood.split(" ")[0]]

st.divider()

if st.button("💰 Dự đoán giá nhà", type="primary", use_container_width=True):
    price = predict_house(user_input)
    lo, hi = price - RMSE, price + RMSE

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Giá ước tính", f"${price:,.0f}")
    with m2:
        st.metric("Dải tham chiếu (±RMSE)", f"${max(lo,0):,.0f} – ${hi:,.0f}")
    with m3:
        st.metric("So với median Ames", f"{(price-MEDIAN)/MEDIAN:+.0%}")

    band = (price - MAE, price + MAE)
    st.success(
        f"🏷️ Căn nhà với các thuộc tính đã nhập được định giá khoảng **${price:,.0f}** "
        f"(dải tham chiếu thực tế thường nằm trong **${band[0]:,.0f} – ${band[1]:,.0f}** "
        f"với sai số trung bình MAE ≈ ${MAE:,.0f})."
    )

    if price > 400_000:
        st.info("💎 Phân khúc cao cấp — model kém tin cậy hơn ở vùng này (ít dữ liệu nhà đắt).")
    elif price < 90_000:
        st.info("🔧 Phân khúc giá thấp — tham khảo thêm thẩm định thực tế.")

    st.caption(
        "⚠️ Công cụ ước tính tham khảo học thuật trên dữ liệu Ames 2006–2010 — không phải "
        "thẩm định giá chính thức. 8 feature chính do người dùng nhập; các feature phụ dùng "
        "giá trị phổ thông của tập huấn luyện (thiết kế mô tả trong notebook, Experiment 3b)."
    )

# ==== preset demo ====
st.divider()
st.subheader("🎬 Demo nhanh — 3 phân khúc")
presets = {
    "Nhà phổ thông": {"OverallQual": 5, "GrLivArea": 1200, "GarageCars": 1,
                      "TotalBsmtSF": 600, "FullBath": 1, "YearBuilt": 1975,
                      "OverallCond": 5, "LotArea": 7000, "Neighborhood": "CollgCr"},
    "Nhà cao cấp": {"OverallQual": 9, "GrLivArea": 2600, "GarageCars": 3,
                    "TotalBsmtSF": 1400, "FullBath": 3, "YearBuilt": 2005,
                    "OverallCond": 8, "LotArea": 12000, "Neighborhood": "NridgHt"},
    "Nhà cấp thấp": {"OverallQual": 3, "GrLivArea": 900, "GarageCars": 0,
                     "TotalBsmtSF": 300, "FullBath": 1, "YearBuilt": 1930,
                     "OverallCond": 4, "LotArea": 5000, "Neighborhood": "MeadowV"},
}
pcols = st.columns(3)
for col, (name, preset) in zip(pcols, presets.items()):
    with col:
        if st.button(name, key=name):
            base = user_input.copy()
            base.update(preset)
            price = predict_house(base)
            st.metric("Giá ước tính", f"${price:,.0f}")
            st.progress(min(price / 500_000, 1.0))

st.divider()
st.markdown(
    "<sub>Assignment 01 — Intelligent System Development | Hệ Dự đoán giá nhà | "
    "Random Forest Regressor (log-target) | Deploy: Hugging Face Spaces (Streamlit)</sub>",
    unsafe_allow_html=True,
)
