import streamlit as st
import pymongo
from datetime import datetime

st.set_page_config(page_title="AI Chat Pro", page_icon="💬", layout="centered")

# CSS: হেডিং এবং ইনপুট লেবেলের কালার ফিক্স
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .main-title { color: #003399; text-align: center; font-weight: 800; font-size: 2.5em; }
    .input-label { color: #000000 !important; font-weight: bold; font-size: 1.1em; }
    .msg-bubble { background-color: #d1e7ff; padding: 15px; border-radius: 15px; color: #003366; font-weight: 600; margin-bottom: 5px; }
    .analysis-panel { background: #ffffff; padding: 10px; border-radius: 10px; margin-top: 5px; color: #000000; font-weight: bold; border-left: 5px solid #FF1493; }
    </style>
""", unsafe_allow_html=True)

# MongoDB Connection
MONGO_URI = "mongodb+srv://ahana741222_db_user:xovyPVFSibWK6moy@whatsappcluster.vo6e4k0.mongodb.net/?appName=WhatsappCluster"
db = pymongo.MongoClient(MONGO_URI)["ai_chat_database"]
collection = db["messages_history"]

# Header
st.markdown("<h1 class='main-title'>💬 AI Chat Moderator & Group</h1>", unsafe_allow_html=True)

# Session
if "username" not in st.session_state: st.session_state.username = ""
if not st.session_state.username:
    # লেবেলটিকে কালো করার জন্য কাস্টম এইচটিএমএল ব্যবহার করেছি
    st.markdown("<p class='input-label'>Enter your name:</p>", unsafe_allow_html=True)
    name_input = st.text_input("", key="name_input")
    if st.button("Join Room 🚀"):
        if name_input.strip():
            st.session_state.username = name_input
            st.rerun()
    st.stop()

# AI Analysis
def analyze_message(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["fuck", "stupid", "hate"]):
        return {"emotion": "Angry 😡", "toxicity": "Toxic 🔴", "category": "Sensitive", "urgency": "High 🚨"}
    elif any(w in text_lower for w in ["love", "happy", "great"]):
        return {"emotion": "Positive 😊", "toxicity": "Safe 🟢", "category": "Social", "urgency": "Low 🟢"}
    return {"emotion": "Neutral 😐", "toxicity": "Safe 🟢", "category": "General", "urgency": "Low 🟢"}

# Display Chat
for msg in collection.find().sort("timestamp", 1):
    with st.chat_message(msg.get("username")):
        st.markdown(f"<span style='color:#FF1493; font-weight:bold;'>{msg.get('username')}</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='msg-bubble'>{msg.get('text')}</div>", unsafe_allow_html=True)
        
        ana = msg.get("analysis", {})
        st.markdown(f"""
            <div class='analysis-panel'>
            Emotion: {ana.get('emotion')} | Toxicity: {ana.get('toxicity')} | 
            Cat: {ana.get('category')} | Urg: {ana.get('urgency')}
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Delete", key=str(msg.get("_id"))):
            collection.delete_one({"_id": msg.get("_id")})
            st.rerun()

# Input
if user_msg := st.chat_input("Type your message..."):
    collection.insert_one({
        "text": user_msg, 
        "username": st.session_state.username, 
        "analysis": analyze_message(user_msg),
        "timestamp": datetime.utcnow()
    })
    st.rerun()
