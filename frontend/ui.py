import streamlit as st
import requests
import os

# Configure API base URL
API_BASE_URL = os.getenv("API_BASE_URL")

def call_backend_api(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to call API: {e}")
        return None

# Example usage
st.title("Hello World")
if st.button("Test Backend Connection"):
    result = call_backend_api("/healthcheck")  # or whatever endpoint you have
    if result:
        st.success("Backend connected!")
        st.json(result)