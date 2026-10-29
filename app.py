import os
import streamlit as st
from agent import run_workflow

# Page configuration
st.set_page_config(
    page_title="Task-Automation Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Task-Automation Agent")
st.caption("Search the web + summarize into a 3-bullet brief (Gemini + DuckDuckGo)")

# API Key fallback for local execution if not in environment
if not os.environ.get("GOOGLE_API_KEY"):
    with st.sidebar:
        st.subheader("Configuration")
        api_key_input = st.text_input("Enter Google API Key", type="password")
        if api_key_input:
            os.environ["GOOGLE_API_KEY"] = api_key_input

# User Inputs
topic = st.text_input("Topic", placeholder="e.g. tell me about agentic AI")
temperature = st.slider("Temperature (creativity)", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

run_button = st.button("Generate Brief", type="primary")

if run_button:
    if not topic.strip():
        st.warning("Please enter a topic to begin.")
    elif not os.environ.get("GOOGLE_API_KEY"):
        st.error("Google API key is missing. Set GOOGLE_API_KEY environment variable or enter it in the sidebar.")
    else:
        status_placeholder = st.empty()
        
        def update_progress(msg: str):
            status_placeholder.info(msg)

        try:
            with st.spinner("Processing..."):
                brief = run_workflow(topic=topic, temperature=temperature, progress=update_progress)
            
            status_placeholder.success("Done!")
            st.subheader("Research brief")
            st.markdown(brief)
        except Exception as e:
            status_placeholder.empty()
            st.error(f"Execution failed: {e}")