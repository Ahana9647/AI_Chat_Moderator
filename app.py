import streamlit as st
import pymongo
from datetime import datetime, timedelta
from streamlit_emoji_picker import emoji_picker # ইমোজি লাইব্রেরি

st.set_page_config(page_title="AI Chat Pro", page_icon="💬", layout="centered")

# CSS ডিজাইন
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .main-title { color: #8A2BE2 !important; text-align: center; font-weight: 800; font-size: 2.5em; }
    .input-label { color: #000000 !important; font-weight: bold; font-size: 1.1em; }
    .msg-bubble { background-color: #d1e7ff; padding: 15px; border-radius: 15px; color: #003366; font-weight: 600; margin-bottom: 5px; }
    .analysis-panel { background: #ffffff; padding: 10px; border-radius: 10px; margin-top: 5px; color: #000000; font-weight: bold; border-left: 5px solid #FF1493; font-size: 0.85em; }
    .time-text { font-size: 0.75em; color: #333333; font-weight: bold; text-align: right; margin-top: -3px; margin-bottom: 10px; padding-right: 5px; }
    .typing { font-size: 0.8em; color: #8A2BE2; font-style: italic; }
    </style>
""", unsafe_allow_html=True)

# MongoDB Connection
MONGO_URI = "mongodb+srv://ahana741222_db_user:xovyPVFSibWK6moy@whatsappcluster.vo6e4k0.mongodb.net/?appName=WhatsappCluster"
db = pymongo.MongoClient(MONGO_URI)["ai_chat_database"]
collection = db["messages_history"]

st.markdown("<h1 class='main-title'>💬 AI Chat Moderator & Group</h1>", unsafe_allow_html=True)

# Session
if "username" not in st.session_state: st.session_state.username = ""
if not st.session_state.username:
    name_input = st.text_input("Enter your name:")
    if st.button("Join Room 🚀"):
        if name_input.strip():
            st.session_state.username = name_input
            st.rerun()
    st.stop()

# --- ইমোজি পিকার ও টাইপিং ইন্ডিকেটর ---
col1, col2 = st.columns([0.7, 0.3])
with col1:
    st.markdown(f"### Welcome, {st.session_state.username}! 👋")
    # সিম্পল টাইপিং ইন্ডিকেটর লজিক
    if st.checkbox("Show Typing Indicator"):
        st.markdown("<p class='typing'>Someone is typing...</p>", unsafe_allow_html=True)
with col2:
    if st.button("🗑️ Clear All"):
        collection.delete_many({})
        st.rerun()

# ইমোজি পিকার
chosen_emoji = emoji_picker("Pick an emoji", key="emoji")

# AI Math Logic
def analyze_message(text):
    if "sum" in text.lower():
        parts = text.lower().split()
        nums = [float(n) for n in parts if n.replace('.','',1).isdigit()]
        if len(nums) >= 2:
            return {"emotion": "Helpful 🤖", "toxicity": "Safe 🟢", "category": "Math", "urgency": "Low 🟢", "result": sum(nums)}
    return {"emotion": "Neutral 😐", "toxicity": "Safe 🟢", "category": "General", "urgency": "Low 🟢"}

# Display Chat
for msg in collection.find().sort("timestamp", 1):
    with st.chat_message(msg.get("username")):
        st.markdown(f"<span style='color:#FF1493; font-weight:bold;'>{msg.get('username')}</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='msg-bubble'>{msg.get('text')}</div>", unsafe_allow_html=True)
        # Math result
        if "result" in msg.get("analysis", {}):
            st.success(f"💡 AI Math Result: {msg['analysis']['result']}")
        
        ts = msg.get("timestamp")
        time_str = (ts + timedelta(hours=5, minutes=30)).strftime("%I:%M %p") if isinstance(ts, datetime) else "N/A"
        st.markdown(f"<div class='time-text'>{time_str}</div>", unsafe_allow_html=True)
        
        ana = msg.get("analysis", {})
        st.markdown(f"<div class='analysis-panel'>Emotion: {ana.get('emotion')} | Toxicity: {ana.get('toxicity')} | Cat: {ana.get('category')}</div>", unsafe_allow_html=True)
        
        if st.button("Delete", key=str(msg.get("_id"))):
            collection.delete_one({"_id": msg.get("_id")})
            st.rerun()

# Input with Emoji support
user_msg = st.chat_input("Type message...")
if user_msg:
    final_msg = f"{user_msg} {chosen_emoji if chosen_emoji else ''}"
    collection.insert_one({
        "text": final_msg, 
        "username": st.session_state.username, 
        "analysis": analyze_message(final_msg),
        "timestamp": datetime.utcnow()
    })
    st.rerun()
