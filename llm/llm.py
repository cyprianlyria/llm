import json
import os
import pandas as pd
import streamlit as st
from openai import OpenAI
from datetime import datetime

# Configurations
EXCEL_FILE = "geo_with_info_std_100.xlsx"
JSON_FILE = "geo_with_info_std_100.json"
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"

# Page configuration
st.set_page_config(
    page_title="AI Educational Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Clean CSS for focused UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: #f8f9fa;
        padding: 0;
    }
    
    /* Header styling */
    .header {
        padding: 1rem 0;
        text-align: left;
        margin-bottom: 1rem;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        height: 60vh;
        overflow-y: auto;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* User message bubble */
    .user-message {
        background: #007bff;
        color: white;
        padding: 10px 15px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        margin-left: 20%;
        max-width: 75%;
    }
    
    /* Bot message bubble */
    .bot-message {
        background: #f1f3f5;
        color: #212529;
        padding: 10px 15px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        margin-right: 20%;
        max-width: 75%;
    }
    
    /* Input container */
    .input-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Chat input styling */
    .stChatInput > div > div > input {
        border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Convert Excel to JSON if JSON does not exist
if not os.path.exists(JSON_FILE):
    df = pd.read_excel(EXCEL_FILE)
    df.to_json(JSON_FILE, orient='records', indent=4)

# Load JSON knowledge base
with open(JSON_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

knowledge_base = {}
if isinstance(data, list) and len(data) > 0:
    question_key = "stem"
    answer_key = "std"
    if question_key in data[0] and answer_key in data[0]:
        knowledge_base = {item[question_key]: item[answer_key] for item in data}
    else:
        st.error("ERROR: Missing expected keys in JSON!")
        st.stop()
else:
    st.error("ERROR: Unsupported JSON format!")
    st.stop()

# Initialize OpenAI (DeepSeek) client
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

# Chatbot function
def chatbot(prompt):
    # Check local knowledge base first
    if prompt in knowledge_base:
        return knowledge_base[prompt]

    # Fallback to DeepSeek AI
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://educational-chatbot.streamlit.app/",
                "X-Title": "Educational Chatbot",
            },
            model="deepseek/deepseek-r1:free",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Header
st.markdown('<div class="header">', unsafe_allow_html=True)
st.title("web Aplication AI embedded")
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input container
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Input area
user_input = st.chat_input("Type your message here...")

# Handle user input
if user_input:
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get bot response
    with st.spinner(""):
        bot_response = chatbot(user_input)
    
    # Add bot response to session state
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    st.rerun()