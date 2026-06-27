import streamlit as st
import pymongo
from datetime import datetime

st.set_page_config(page_title="AI Chat Pro", page_icon="💬", layout="centered")

# CSS দিয়ে সব কালার কাস্টমাইজ করা হয়েছে
st.markdown("""
    <style>
    /* ব্যাকগ্রাউন্ড গ্রেডিয়েন্ট */
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    .welcome-text { text-align: center; font-size: 2em; font-weight: bold; color: #4a4a4a; margin-bottom: 20px; }
    
    /* মেসেজ বক্স ডিজাইন */
    .msg-bubble { 
        background-color: #d1e7ff; /* হালকা নীল ব্যাকগ্রাউন্ড */
        padding: 15px; 
        border-radius: 15px; 
        color: #003366; /* গাঢ় নীল টেক্সট */
        font-weight: 600;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    
    /* অ্যানালাইসিস প্যানেল */
    .analysis-panel { 
        background: #ffffff; 
        padding: 8px; 
        border-radius: 10px; 
        margin-top: 5px; 
        font-size: 0.85em; 
        border-left: 4px solid #ff1493; /* পিঙ্ক বর্ডার */
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

# Header
st.markdown(f"<div class='welcome-text'>Welcome, {st.session_state.username}! 👋</div>", unsafe_allow_html=True)

# Sidebar
if st.sidebar.button("🗑️ Clear All Chat"): collection.delete_many({}); st.rerun()

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
        # নাম গাঢ় পিঙ্ক রঙে
        st.markdown(f"<span style='color:#FF1493; font-weight:bold;'>{msg.get('username')}</span>", unsafe_allow_html=True)
        # মেসেজ গাঢ় ব্লু এবং বক্স হালকা নীল
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
