import streamlit as st
import pymongo
from datetime import datetime
import time

st.set_page_config(page_title="AI Chat Pro", page_icon="💬", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    </style>
""", unsafe_allow_html=True)

# MongoDB Connection
MONGO_URI = "mongodb+srv://ahana741222_db_user:xovyPVFSibWK6moy@whatsappcluster.vo6e4k0.mongodb.net/?appName=WhatsappCluster"

@st.cache_resource
def get_db():
    client = pymongo.MongoClient(MONGO_URI)
    return client["ai_chat_database"]

db = get_db()
collection = db["messages_history"]

# Session State
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    name_input = st.text_input("Enter your name to join:")
    if st.button("Join Room 🚀"):
        if name_input.strip():
            st.session_state.username = name_input
            st.rerun()
    st.stop()

# Sidebar
if st.sidebar.button("🗑️ Clear All Chat"):
    collection.delete_many({})
    st.rerun()
if st.sidebar.button("Log Out"):
    st.session_state.username = ""
    st.rerun()

# AI Analysis
def analyze_message(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["fuck", "stupid", "hate"]):
        return {"emotion": "Angry 😡", "toxicity": "Toxic 🔴"}
    elif any(word in text_lower for word in ["love", "happy", "great"]):
        return {"emotion": "Positive 😊", "toxicity": "Safe 🟢"}
    return {"emotion": "Neutral 😐", "toxicity": "Safe 🟢"}

# Helper
def get_user_color(username):
    colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33A1"]
    return colors[hash(username) % len(colors)]

# Display Chat
st.title(f"Welcome, {st.session_state.username}! 👋")
messages = list(collection.find().sort("timestamp", 1))

for msg in messages:
    user = msg.get("username", "Anonymous")
    text = msg.get("text", "")
    analysis = msg.get("analysis", {"emotion": "Neutral", "toxicity": "Safe"})
    msg_id = msg.get("_id")
    
    user_color = get_user_color(user)
    
    with st.chat_message(user):
        st.markdown(f"<span style='color:{user_color}; font-weight:bold;'>{user}</span>", unsafe_allow_html=True)
        st.write(text)
        st.caption(f"🤖 {analysis.get('emotion')} | {analysis.get('toxicity')}")
        if st.button("Delete", key=str(msg_id)):
            collection.delete_one({"_id": msg_id})
            st.rerun()

# Input
user_message = st.chat_input("Type your message here...")
if user_message:
    analysis = analyze_message(user_message)
    payload = {
        "text": user_message, 
        "username": st.session_state.username,
        "analysis": analysis,
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(payload)
    st.rerun()
