"""
Streamlit dashboard for attendance data visualization.
"""
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")
PROFESSOR_TOKEN = os.getenv("PROFESSOR_TOKEN", "default_professor_token")

# Set page config
st.set_page_config(
    page_title="Attendance Dashboard",
    page_icon="✅",
    layout="wide"
)

# Header
st.title("Attendance System Dashboard")
st.markdown("View and export attendance records")

# Helper function to make API calls
def make_api_call(endpoint, method="GET", data=None):
    headers = {"Authorization": f"Bearer {PROFESSOR_TOKEN}"}
    url = f"{BACKEND_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return None
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {e}")
        return None

# Sidebar filters
st.sidebar.header("Filters")
sessions_data = make_api_call("sessions")
if sessions_data:
    session_options = {s["id"]: s["name"] for s in sessions_data}
    selected_session = st.sidebar.selectbox(
        "Select Session",
        options=list(session_options.keys()),
        format_func=lambda x: session_options[x]
    )
else:
    selected_session = None

date_range = st.sidebar.date_input(
    "Date Range",
    value=(datetime.now() - timedelta(days=7), datetime.now()),
    max_value=datetime.now()
)

# Fetch attendance data
attendance_data = make_api_call(f"attendance?session_id={selected_session}" if selected_session else "attendance")

if attendance_data:
    # Convert to DataFrame
    df = pd.DataFrame(attendance_data)
    
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Apply date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)]
    
    # Display data
    st.subheader("Attendance Records")
    st.dataframe(df)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Unique Students", df["student_id"].nunique())
    with col3:
        st.metric("Latest Record", df["timestamp"].max().strftime("%Y-%m-%d %H:%M"))
    
    # Visualization
    st.subheader("Visualization")
    
    # Daily attendance count
    daily_count = df.groupby(df["timestamp"].dt.date).size().reset_index(name="count")
    fig_daily = px.bar(daily_count, x="timestamp", y="count", title="Daily Attendance")
    st.plotly_chart(fig_daily)
    
    # Student attendance count
    student_count = df.groupby("student_id").size().reset_index(name="count")
    fig_student = px.bar(student_count, x="student_id", y="count", title="Attendance by Student")
    st.plotly_chart(fig_student)
    
    # Export functionality
    st.subheader("Export Data")
    if st.button("Export to CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="attendance_records.csv",
            mime="text/csv"
        )
else:
    st.warning("No attendance data available or unable to connect to server.")

# Session management
st.sidebar.header("Session Management")
new_session_name = st.sidebar.text_input("New Session Name")
new_session_desc = st.sidebar.text_input("New Session Description")

if st.sidebar.button("Start New Session"):
    if new_session_name:
        session_data = {
            "name": new_session_name,
            "description": new_session_desc
        }
        result = make_api_call("start_attendance", method="POST", data=session_data)
        if result:
            st.sidebar.success(f"Session '{result['name']}' started!")
            st.experimental_rerun()
    else:
        st.sidebar.error("Session name is required")

# Stop active session
active_session = make_api_call("current_session")
if active_session:
    if st.sidebar.button("Stop Current Session"):
        result = make_api_call("stop_attendance", method="POST", data={"session_id": active_session["id"]})
        if result:
            st.sidebar.success("Session stopped!")
            st.experimental_rerun()
else:
    st.sidebar.info("No active session")