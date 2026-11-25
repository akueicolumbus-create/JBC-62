import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="South Sudan Connectivity", layout="wide")
st.title("📡 South Sudan Connectivity Reality")

prices = pd.DataFrame(
    {
        "Service": ["MTN 2GB/day", "Zain 2GB/day", "Starlink Mini/mo", "Starlink Std/mo"],
        "USD": [13.15, 12.50, 30.00, 55.00],
        "Type": ["Mobile", "Mobile", "Satellite", "Satellite"],
    }
)

devices = pd.DataFrame(
    {
        "Device": ["Smartphone", "Feature phone", "No phone"],
        "Household %": [13, 40, 47],
    }
)

st.header("1. What people pay")
st.plotly_chart(px.bar(prices, x="Service", y="USD", color="Type", text="USD"), use_container_width=True)

st.header("2. Who can connect")
st.plotly_chart(px.funnel(devices, x="Household %", y="Device").update_traces(texttemplate="%{x}%"), use_container_width=True)

st.header("3. Tax burden")
pkg = st.slider("Monthly package (USD)", 1, 100, 15)
tax = pkg * 0.328 + (pkg + pkg * 0.328) * 0.18
st.metric("Estimated tax portion", f"${tax:.2f}", f"{tax / pkg * 100:.0f}% of price")
st.caption("Excise 32.8% + 18% sales tax (GSMA). Illustrative.")

st.divider()
st.markdown("> For most South Sudanese, $30/month is not a choice. Starlink serves those who can pay — and need it to work.")
