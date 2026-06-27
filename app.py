import streamlit as st
import pymongo
from datetime import datetime

st.set_page_config(page_title="AI Chat Pro", page_icon="💬", layout="centered")

# Custom CSS for Dynamic Colors
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); }
    .welcome-text { text-align: center; font-size: 2.5em; font-weight: bold; color: #6a11cb; text-shadow: 2px 2px 4px #aaa; }
    .msg-box { padding: 10px; border-radius: 15px; margin-bottom: 10px; color: white; font-weight: 500; }
    .analysis-box { background: rgba(255, 255, 255, 0.9); padding: 8px; border-radius: 10px; margin-top: 5px; color: #333; font-size: 0.8em; }
    </style>
""", unsafe_allow_html=True)

# MongoDB
MONGO_URI = "mongodb+srv://ahana741222_db_user:xovyPVFSibWK6moy@whatsappcluster.vo6e4k0.mongodb.net/?appName=WhatsappCluster"
db = pymongo.MongoClient(MONGO_URI)["ai_chat_database"]
collection = db["messages_history"]

# Session
if "username" not in st.session_state: st.session_state.username = ""
if not st.session_state.username:
    name_input = st.text_input("Enter your name:")
    if st.button("Join"):
        st.session_state.username = name_input
        st.rerun()
    st.stop()

# Helper for Dynamic Colors
def get_color(text):
    colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#FFD700", "#8A2BE2"]
    return colors[hash(text) % len(colors)]

# UI
st.markdown(f"<div class='welcome-text'>Welcome, {st.session_state.username}! 👋</div>", unsafe_allow_html=True)

if st.sidebar.button("Clear Chat"): collection.delete_many({}); st.rerun()

# Display
for msg in collection.find().sort("timestamp", 1):
    user = msg.get("username")
    text = msg.get("text")
    analysis = msg.get("analysis", {})
    user_color = get_color(user)
    msg_color = get_color(text)
    
    with st.chat_message(user):
        st.markdown(f"<b style='color:{user_color}'>{user}</b>", unsafe_allow_html=True)
        st.markdown(f"<div class='msg-box' style='background-color:{msg_color}'>{text}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='analysis-box'>🤖 {analysis.get('emotion')} | {analysis.get('toxicity')}</div>", unsafe_allow_html=True)
        if st.button("Delete", key=str(msg.get("_id"))): collection.delete_one({"_id": msg.get("_id")}); st.rerun()

# Input
if user_msg := st.chat_input("Type..."):
    collection.insert_one({"text": user_msg, "username": st.session_state.username, "timestamp": datetime.utcnow()})
    st.rerun()
