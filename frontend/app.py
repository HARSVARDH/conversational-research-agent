import streamlit as st
import requests
import os 
import uuid
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Paper Agent", page_icon="📄", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("📄 Chat with the Authors")
st.markdown("Upload a research paper and interrogate the 'authors' directly.")

with st.sidebar:
    st.header("1. Upload Paper")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    if st.button("Process Document"):
        if uploaded_file is not None:
            with st.spinner("Processing document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{BACKEND_URL}/upload/", files=files)
                if response.status_code == 200:
                    st.success("Paper ingested successfully!")
                else:
                    st.error("Error processing document.")
        else:
            st.warning("Please upload a file first.")
            
    st.divider()
    
    st.header("Session Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.success("Chat cleared! You have a fresh session.")

st.header("2. Ask Questions")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about the methodology, architecture, or code..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        payload = {
            "session_id": st.session_state.session_id,
            "question": prompt
        }
        res = requests.post(f"{BACKEND_URL}/chat/", json=payload, stream=True)
        
        if res.status_code == 200:
            def stream_parser():
                for chunk in res.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        yield chunk
            answer = st.write_stream(stream_parser())
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Failed to connect to the backend.")