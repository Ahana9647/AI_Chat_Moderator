import streamlit as st
import pymongo
from datetime import datetime

st.set_page_config(page_title="AI Chat Pro", page_icon="💬", layout="centered")

# সুন্দর এবং আধুনিক কালার স্কিম
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #eef2f3 0%, #8e9eab 100%); }
    .welcome-text { text-align: center; color: #2d3436; font-size: 2.2em; font-weight: 800; padding: 20px; }
    .msg-bubble { background: #ffffff; padding: 15px; border-radius: 15px; border-left: 5px solid #6c5ce7; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .analysis-panel { background: #f1f2f6; padding: 10px; border-radius: 10px; margin-top: 5px; font-size: 0.9em; color: #2d3436; }
    </style>
""", unsafe_allow_html=True)

# MongoDB Connection
MONGO_URI = "mongodb+srv://ahana741222_db_user:xovyPVFSibWK6moy@whatsappcluster.vo6e4k0.mongodb.net/?appName=WhatsappCluster"
db = pymongo.MongoClient(MONGO_URI)["ai_chat_database"]
collection = db["messages_history"]

# Session
if "username" not in st.session_state: st.session_state.username = ""
if not st.session_state.username:
    name_input = st.text_input("Enter your name:")
    if st.button("Join Room 🚀"):
        st.session_state.username = name_input
        st.rerun()
    st.stop()

# Header
st.markdown(f"<div class='welcome-text'>Welcome, {st.session_state.username}! 👋</div>", unsafe_allow_html=True)

# Sidebar
if st.sidebar.button("🗑️ Clear All"): collection.delete_many({}); st.rerun()

# AI Analysis
def analyze_message(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["fuck", "stupid", "hate"]):
        return {"emotion": "Angry 😡", "toxicity": "Toxic 🔴", "category": "Sensitive", "urgency": "High"}
    elif any(w in text_lower for w in ["love", "happy", "great"]):
        return {"emotion": "Positive 😊", "toxicity": "Safe 🟢", "category": "Social", "urgency": "Low"}
    return {"emotion": "Neutral 😐", "toxicity": "Safe 🟢", "category": "General", "urgency": "Low"}

# Display Messages
for msg in collection.find().sort("timestamp", 1):
    with st.chat_message(msg.get("username")):
        st.markdown(f"**{msg.get('username')}**")
        st.markdown(f"<div class='msg-bubble'>{msg.get('text')}</div>", unsafe_allow_html=True)
        
        ana = msg.get("analysis", {})
        st.markdown(f"""
            <div class='analysis-panel'>
            🤖 <b>{ana.get('emotion')}</b> | {ana.get('toxicity')} | 
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
