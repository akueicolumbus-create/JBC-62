import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="JBC-62 | Connectivity Decisions", layout="wide")

# ============ SIDEBAR: YOUR LIVE INPUTS ============
st.sidebar.header("⚙️ Live Inputs")
ssp_per_usd = st.sidebar.number_input(
    "SSP per 1 USD (your market rate)",
    min_value=1000.0, max_value=50000.0, value=7082.5, step=100.0,
)
st.sidebar.caption("Default: 100 USD = 708,250 SSP")

st.sidebar.divider()
st.sidebar.subheader("Mobile data (SSP)")
mtn_daily_ssp = st.sidebar.number_input("MTN 2GB daily (SSP)", value=17100.0, step=500.0)
zain_daily_ssp = st.sidebar.number_input("Zain 2GB daily (SSP)", value=16250.0, step=500.0)
digitel_daily_ssp = st.sidebar.number_input("Digitel 2GB daily (SSP)", value=14300.0, step=500.0)

st.sidebar.divider()
st.sidebar.subheader("Starlink (USD, your shop)")
starlink_lite = st.sidebar.number_input("Residential Lite / month", value=30.0, step=1.0)
starlink_std = st.sidebar.number_input("Residential Standard / month", value=50.0, step=1.0)

# ============ HEADER ============
st.title("📡 JBC-62 | South Sudan Connectivity Decisions")
st.caption(
    f"Live rate: **1 USD ≈ {ssp_per_usd:,.0f} SSP**  |  "
    "Mobile vs. Starlink, device reality, tax policy. Adjust inputs in sidebar."
)

# ============ MODULE 1: BREAK-EVEN ============
st.header("1. Who is actually cheaper?")
st.markdown("Compare **monthly cost (USD)** by how much data a customer uses.")

gb_per_month = st.slider("Customer monthly data use (GB)", 1, 120, 30)

# Mobile: 2GB/day package, scaled to monthly GB
# Cost per GB per day = daily_price_ssp / 2 GB; monthly = *30 days
mobile = []
for name, daily_ssp in [("MTN", mtn_daily_ssp), ("Zain", zain_daily_ssp), ("Digitel", digitel_daily_ssp)]:
    cost_per_gb_day_usd = (daily_ssp / ssp_per_usd) / 2
    monthly_usd = cost_per_gb_day_usd * gb_per_month
    mobile.append({"Provider": name, "Monthly USD": monthly_usd, "Type": "Mobile"})

starlink = [
    {"Provider": "Starlink Lite", "Monthly USD": starlink_lite, "Type": "Satellite"},
    {"Provider": "Starlink Std", "Monthly USD": starlink_std, "Type": "Satellite"},
]

df = pd.DataFrame(mobile + starlink)
fig = px.bar(
    df, x="Provider", y="Monthly USD", color="Type", text="Monthly USD",
    title=f"Monthly cost at {gb_per_month} GB/month (USD)",
)
fig.update_traces(texttemplate="$%{text:.0f}", textposition="outside")
fig.update_layout(height=420, yaxis_title="USD / month")
st.plotly_chart(fig, use_container_width=True)

# Break-even line
st.subheader("Break-even vs. Starlink Lite")
mobile_avg_per_gb = (
    (mtn_daily_ssp + zain_daily_ssp + digitel_daily_ssp) / 3 / ssp_per_usd / 2
)
be_gb = starlink_lite / mobile_avg_per_gb if mobile_avg_per_gb > 0 else 0
st.metric(
    "Data volume where Starlink Lite becomes cheaper",
    f"{be_gb:.0f} GB/month",
    f"≈ {be_gb/30:.1f} GB/day",
)
st.caption(
    "Above this usage, Starlink Lite's flat USD price beats mobile per-GB cost. "
    "Below it, mobile daily bundles are cheaper."
)

# ============ MODULE 2: WHO CAN AFFORD IT ============
st.header("2. Who can afford it?")

col1, col2 = st.columns([1, 1])

with col1:
    devices = pd.DataFrame({
        "Device": ["Smartphone", "Feature phone", "No phone"],
        "Household %": [13, 40, 47],
    })
    fig2 = px.funnel(devices, x="Household %", y="Device",
                     title="Household device ownership (national)")
    fig2.update_traces(texttemplate="%{x}%")
    fig2.update_layout(height=320)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    customer = st.selectbox(
        "Customer profile",
        ["Has smartphone, needs video/reliable", "Has smartphone, basic use",
         "Feature phone only", "No phone"],
    )
    if customer.startswith("Has smartphone, needs video"):
        st.success("**Recommend Starlink.** Reliable video needs satellite. Mobile congestion is the bottleneck.")
    elif customer.startswith("Has smartphone, basic"):
        st.info("**Mobile bundle may suffice.** Compare daily cost vs. their income. Starlink only if business-critical.")
    elif customer == "Feature phone only":
        st.warning("**SMS/USSD services only.** Not a Starlink or data-bundle customer today.")
    else:
        st.error("**Outside the market.** Connectivity requires device + power + income first.")

# ============ MODULE 3: TAX POLICY SIMULATOR ============
st.header("3. What if the excise tax drops?")
st.markdown("GSMA model: cutting mobile excise from **26% → 10%** by 2030.")

excise = st.slider("Excise tax rate (%)", 10, 26, 26)

# Linear-ish interpolation to GSMA 2030 endpoints (illustrative)
scale = (26 - excise) / 16
pen_gain = 4 * scale
data_gain = 28 * scale
gdp_gain = 89 * scale

c1, c2, c3 = st.columns(3)
c1.metric("Mobile internet penetration", f"+{pen_gain:.1f}%", "vs. baseline")
c2.metric("Data usage", f"+{data_gain:.0f}%", "vs. baseline")
c3.metric("GDP impact", f"+${gdp_gain:.0f}M", "cumulative to 2030")
st.caption("Interpolated from GSMA 'Taxing Mobile Connectivity' scenario. Illustrative, not a forecast.")

# ============ CLOSING ============
st.divider()
st.markdown(
    f"""
    > **The decision rule:** At **{ssp_per_usd:,.0f} SSP/USD**, a customer using more than
    > **{be_gb:.0f} GB/month** is better off on Starlink Lite — *and* gets reliability
    > mobile networks can't guarantee.
    """
)
st.caption("Sources: NCA tariffs, GSMA taxation model, ITU/World Bank device data, JBC-62 shop pricing.")
