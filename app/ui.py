import streamlit as st
import requests

API_URL = "http://localhost:8000/run"

st.set_page_config(page_title="E-Commerce Product Quality ML", layout="wide")

st.title("🛒 E-Commerce Product Quality Classification")
st.markdown("Run the ML pipeline using FastAPI + Docker")

if st.button("▶ Run ML Pipeline"):
    with st.spinner("Running model... this may take a few minutes"):
        response = requests.post(API_URL, json={"run_training": True})

        if response.status_code == 200:
            data = response.json()

            st.success("Pipeline executed successfully")

            st.subheader("📤 Model Output")
            st.text_area(
                "STDOUT",
                data.get("stdout", ""),
                height=400
            )

            if data.get("stderr"):
                st.subheader("⚠ Warnings / STDERR")
                st.text_area(
                    "STDERR",
                    data.get("stderr", ""),
                    height=150
                )
        else:
            st.error("API call failed")
