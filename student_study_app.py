
import os
import streamlit as st
import openai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Initialize OpenAI client (only if API_KEY is present)
client = None
if API_KEY:
    client = openai.OpenAI(api_key=API_KEY, base_url="https://api.poe.com/v1")
# Page configuration
st.set_page_config(page_title="AI Plan Helper", page_icon="💬", layout="wide")

st.title("AI Planner")
st.caption("Helping you whenever you need!")

# Sidebar for preprompt and character settings
with st.sidebar:
    st.header("⚙️ AI Settings")
        
with st.form("AI planner"):
    st.subheader("AI Planner Form")

    if not API_KEY:
        st.warning("API_KEY not found. OpenAI-related features are disabled. Set API_KEY in .env to enable them.")

    # Events input (times)
    times = ["8:00 AM", "9:15 AM", "10:30 AM", "11:30 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:15 PM"]
    st.markdown("#### Events")
    events = {}
    for t in times:
        key = "event_" + t.replace(":", "").replace(" ", "")
        events[t] = st.text_input(f"Event at {t}", key=key)

    # Weekly timetable inputs
    st.markdown("#### Weekly Timetable")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    schedule = {t: {} for t in times}
    for t in times:
        cols = st.columns(len(days) + 1)
        cols[0].markdown(f"**{t}**")
        for i, d in enumerate(days):
            cell_key = f"{t.replace(":", "").replace(" ", "")}_{d}"
            schedule[t][d] = cols[i+1].text_input(f"{d}", key=cell_key)

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.success("Timetable submitted")
        st.write("Events:", events)
        rows = [{"Time": t, **{d: schedule[t][d] for d in days}} for t in times]
        st.table(rows)