import streamlit as st
import requests
import datetime

# from exception.exceptions import TradingBotException
import sys

BASE_URL = "http://localhost:8000"  # Backend endpoint

st.set_page_config(
    page_title="Email Agentic Application",
    page_icon="",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("Email Agentic Application")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


st.header("How can I help you?.")

with st.form(key="query_form", clear_on_submit=True):
    user_input = st.text_input("User Input", placeholder="")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input.strip():
    try:
        # # Show user message
        # Show thinking spinner while backend processes
        with st.spinner("Bot is thinking..."):
            payload = {"query": user_input}
            response = requests.post(f"{BASE_URL}/query", json=payload)

        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            markdown_content = f"""
            {answer}
            """
            st.markdown(markdown_content)
        else:
            st.error(" Bot failed to respond: " + response.text)

    except Exception as e:
        raise f"The response failed due to {e}"