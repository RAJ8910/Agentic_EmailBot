import streamlit as st
import requests
import datetime
import time
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# from exception.exceptions import TradingBotException
import sys

BASE_URL = "http://localhost:8000"  # Backend endpoint

        
st.set_page_config(
    page_title="Email Agentic Application",
    page_icon="",
    layout="wide",
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
    

# --- New section to display tracking table ---
st.header("🧾 Tracking Table")

# Refresh every 5 minutes (300 seconds)
REFRESH_INTERVAL_SEC = 300  

# Spinner while loading
with st.spinner("Fetching tracking data..."):
    try:
        tracking_response = requests.get(f"{BASE_URL}/tracking")
        if tracking_response.status_code == 200:
            tracking_data = tracking_response.json().get("data", [])
            if tracking_data:
                # Fancy Table using AgGrid
                from st_aggrid import AgGrid, GridOptionsBuilder

                gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(tracking_data))
                gb.configure_pagination(paginationAutoPageSize=True)
                gb.configure_side_bar() 
                gb.configure_grid_options(domLayout='normal')  
                # gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True)
                gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=False)
                grid_options = gb.build()

                AgGrid(
                    pd.DataFrame(tracking_data),
                    gridOptions=grid_options,
                    height=500,
                    width='100%',
                    fit_columns_on_grid_load=True
                )
            else:
                st.info("No tracking data found.")
        else:
            st.error("❌ Failed to fetch tracking data: " + tracking_response.text)
    except Exception as e:
        st.error(f"⚠️ Error fetching tracking data: {e}")

# Auto-refresh every 5 minutes
st.experimental_rerun() if int(time.time()) % REFRESH_INTERVAL_SEC == 0 else None