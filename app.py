import streamlit as st
import pymongo
from datetime import datetime

st.set_page_config(page_title="AI Chat Moderator", page_icon="💬", layout="centered")

st.title("💬 AI Chat Moderator & WhatsApp Group")

# MongoDB Connection
MONGO_URI = "mongodb+srv://ahana741222_db_user:xovyPVFSibWK6moy@whatsappcluster.vo6e4k0.mongodb.net/?appName=WhatsappCluster"

@st.cache_resource
def get_db():
    client = pymongo.MongoClient(MONGO_URI)
    return client["ai_chat_database"]

db = get_db()
collection = db["messages_history"]

# Session State for User
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    name_input = st.text_input("Enter your name to join:")
    if st.button("Join Room 🚀"):
        if name_input.strip():
            st.session_state.username = name_input
            st.rerun()
    st.stop()

# Logout
if st.sidebar.button("Log Out"):
    st.session_state.username = ""
    st.rerun()

# AI Analysis
def analyze_message(text):
    text_lower = text.lower()
    bad_words = ["stupid", "bad", "hate", "খারাপ", "পাগল"]
    good_words = ["good", "happy", "love", "ভালো", "ধন্যবাদ", "nice"]
    
    toxicity, emotion = "Low", "Neutral"
    if any(word in text_lower for word in bad_words):
        toxicity, emotion = "High", "Angry"
    elif any(word in text_lower for word in good_words):
        emotion = "Happy"
    return {"emotion": emotion, "toxicity": toxicity}

# Display Chat
messages = list(collection.find().sort("timestamp", 1))
for msg in messages:
    user = msg.get("username", "Anonymous")
    text = msg.get("text", "")
    analysis = msg.get("analysis", {})
    st.markdown(f"**{'🔴 You' if user == st.session_state.username else '🔵 ' + user}:** {text}")
    st.caption(f"🤖 Analysis: {analysis.get('emotion')} | Toxicity: {analysis.get('toxicity')}")

# Input Message
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
