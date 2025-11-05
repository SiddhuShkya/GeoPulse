import streamlit as st

st.set_page_config(
    page_title="GeoPulse App",
    layout="wide",  # wide mode instead of centered
    initial_sidebar_state="expanded",
)

st.title("🌍 Welcome to GeoPulse")
st.sidebar.success(
    "Welcome to GeoPulse! Select a page from the sidebar to get started."
)
