import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bond Valuation Tool", layout="centered")
st.title("📈 Bond Valuation & Sensitivity Analysis")

# --- Inputs ---
face_value = st.number_input("Face Value (₹)", value=100)
coupon_rate = st.slider("Coupon Rate (%)", 0.0, 15.0, 6.0) / 100
ytm = st.slider("Yield to Maturity (%)", 0.0, 15.0, 5.0) / 100
years_to_maturity = st.slider("Years to Maturity", 1, 30, 5)
payments_per_year = st.radio("Coupon Payments Per Year", [1, 2, 4], index=1)

# --- Calculations ---
coupon_payment = face_value * coupon_rate / payments_per_year
periods = years_to_maturity * payments_per_year
periodic_ytm = ytm / payments_per_year

# Present Value of coupons
coupon_pvs = np.array([
    coupon_payment / (1 + periodic_ytm)**t for t in range(1, int(periods) + 1)
])
face_value_pv = face_value / (1 + periodic_ytm)**int(periods)
bond_price = coupon_pvs.sum() + face_value_pv

# Duration and Convexity
cash_flows = np.array([coupon_payment] * (int(periods) - 1) + [coupon_payment + face_value])
discount_factors = np.array([(1 + periodic_ytm)**t for t in range(1, int(periods) + 1)])
pv_factors = cash_flows / discount_factors
time_factors = np.arange(1, int(periods) + 1)

macaulay_duration = np.sum(time_factors * pv_factors) / bond_price
modified_duration = macaulay_duration / (1 + periodic_ytm)
convexity = np.sum([
    cf * t * (t + 1) / (1 + periodic_ytm)**(t + 2)
    for t, cf in zip(time_factors, cash_flows)
]) / bond_price

# --- Display Results ---
st.subheader("💵 Bond Price & Metrics")
st.write(f"**Bond Price:** ₹{bond_price:.2f}")
st.write(f"**Macaulay Duration:** {macaulay_duration:.2f} periods")
st.write(f"**Modified Duration:** {modified_duration:.2f} periods")
st.write(f"**Convexity:** {convexity:.4f}")

# --- Sensitivity Analysis ---
ytm_range = np.arange(ytm - 0.02, ytm + 0.021, 0.005)
sensitivity_prices = []

for y in ytm_range:
    py = y / payments_per_year
    c_pvs = np.array([
        coupon_payment / (1 + py)**t for t in range(1, int(periods) + 1)
    ])
    fv_pv = face_value / (1 + py)**int(periods)
    sensitivity_prices.append(c_pvs.sum() + fv_pv)

df = pd.DataFrame({
    "YTM (%)": (ytm_range * 100).round(2),
    "Price (₹)": np.round(sensitivity_prices, 2)
})

st.subheader("📊 Sensitivity Table")
st.dataframe(df.set_index("YTM (%)"))

# --- Graph ---
st.subheader("📉 Price vs. YTM Graph")
fig, ax = plt.subplots()
ax.plot(df["YTM (%)"], df["Price (₹)"], marker='o', color='blue')
ax.set_xlabel("Yield to Maturity (%)")
ax.set_ylabel("Bond Price (₹)")
ax.grid(True)
st.pyplot(fig)
