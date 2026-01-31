import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

BACKEND = "http://localhost:8000"

st.set_page_config("Pick & Place Dashboard", layout="wide")
st_autorefresh(interval=2000, key="refresh")

# =====================
# SIDEBAR
# =====================
st.sidebar.header("Start Orders")

user = st.sidebar.text_input("User")
count = st.sidebar.number_input("Total Orders", min_value=0, step=1)

if st.sidebar.button("Start"):
    requests.post(
        f"{BACKEND}/start_orders",
        json={"user": user, "total_orders": count}
    )
    st.sidebar.success("Order started")

# =====================
# MAIN DASHBOARD
# =====================
st.header("Live Status")

s = requests.get(f"{BACKEND}/status").json()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Orders", s["total_orders"])
c2.metric("Dispatched", s["dispatched_orders"])
c3.metric("Stored", s["stored_objects"])
c4.metric("System", "Picking" if s["picking"] else "Idle")

# =====================
# PROGRESS BAR
# =====================
if s["total_orders"] > 0:
    progress = int(
        (s["dispatched_orders"] + s["stored_objects"])
        / s["total_orders"] * 100
    )
else:
    progress = 0

st.progress(progress)
