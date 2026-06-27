import streamlit as st
import pymongo
from datetime import datetime

st.set_page_config(page_title="AI Chat Pro", page_icon="💬", layout="centered")

# CSS: লেখাগুলো গাঢ় করার জন্য কালার পরিবর্তন করা হয়েছে
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .msg-bubble { 
        background-color: #d1e7ff; padding: 15px; border-radius: 15px; 
        color: #003366; font-weight: 600; margin-bottom: 5px; 
    }
    /* অ্যানালাইসিস প্যানেল যাতে পরিষ্কার দেখা যায় */
    .analysis-panel { 
        background: #ffffff; padding: 10px; border-radius: 10px; margin-top: 5px; 
        color: #000000; font-weight: bold; border-left: 5px solid #FF1493; 
    }
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

st.markdown(f"<h2 style='text-align: center; color: #4a4a4a;'>Welcome, {st.session_state.username}! 👋</h2>", unsafe_allow_html=True)

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
        # প্রতিটি ফিল্ড স্পষ্টভাবে লেখা হয়েছে
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
