import streamlit as st
import pymongo
import time
from datetime import datetime

st.set_page_config(page_title="AI Chat Moderator", page_icon="💬", layout="centered")

st.title("💬 AI Chat Moderator & WhatsApp Group")
st.write("Real-time Cloud Chat Room with Real AI Analysis!")

# ⚠️ এখানে তোমার MongoDB Atlas থেকে পাওয়া ক্লাউড কানেকশন স্ট্রিংটি বসাবে।
# উদাহরণ: "mongodb+srv://username:password@cluster0.xxxx.mongodb.net/..."
# যদি ক্লাউড লিংক না থাকে, তবে আপাতত নিচের লোকাল লিংকটিই থাক।
MONGO_URI = "mongodb+srv://ahana741222_db_user:xovyPVFSibWK6moy@whatsappcluster.vo6e4k0.mongodb.net/?appName=WhatsappCluster"
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(MONGO_URI)

try:
    client = init_connection()
    db = client["chat_db"]
    collection = db["messages"]
except Exception as e:
    st.error(f"Database Connection Error: {e}")

# Name Input Session
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    st.subheader("Enter your name to join the chat room:")
    name_input = st.text_input("Your Name...", key="name_box")
    if st.button("Join Room 🚀"):
        if name_input.strip():
            st.session_state.username = name_input
            st.rerun()
        else:
            st.error("Name field cannot be empty!")
    st.stop()

st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")
if st.sidebar.button("Log Out"):
    st.session_state.username = ""
    st.rerun()

# হালকা ও সহজ AI Analysis ফাংশন (ভারী লাইব্রেরি ছাড়া)
def analyze_message(text):
    text_lower = text.lower()
    toxicity = "Low"
    emotion = "Neutral"
    
    # কিছু সাধারণ শব্দ দিয়ে ফিল্টারিং করার উদাহরণ
    bad_words = ["stupid", "bad", "hate", "খারাপ", "পাগল"]
    good_words = ["good", "happy", "love", "ভালো", "ধন্যবাদ", "nice"]
    
    if any(word in text_lower for word in bad_words):
        toxicity = "High"
        emotion = "Angry"
    elif any(word in text_lower for word in good_words):
        emotion = "Happy"
        
    return {"emotion": emotion, "toxicity": toxicity}

# সরাসরি MongoDB থেকে মেসেজ হিস্ট্রি নিয়ে আসা
chat_history = []
try:
    chat_history = list(collection.find().sort("_id", 1))
except Exception as e:
    chat_history = []

# স্ক্রিনে মেসেজ দেখানো
st.write("---")
if chat_history:
    for msg in chat_history:
        user = msg.get("username", "Anonymous")
        text = msg.get("text", "")
        analysis = msg.get("analysis", {})
        
        if user == st.session_state.username:
            st.markdown(f"**🔴 You:** {text}")
        else:
            st.markdown(f"**🔵 {user}:** {text}")
            
        st.caption(f"🤖 AI Analysis | Emotion: {analysis.get('emotion', 'Neutral')} | Toxicity: {analysis.get('toxicity', 'Low')}")
else:
    st.info("No messages yet or synchronizing with database...")
st.write("---")

# নতুন মেসেজ ইনপুট বক্স
user_message = st.chat_input("Type your message here...")

if user_message:
    # সরাসরি এখানেই লাইটওয়েট অ্যানালাইসিস করা হচ্ছে
    analysis_result = analyze_message(user_message)
    
    payload = {
        "text": user_message, 
        "username": st.session_state.username,
        "analysis": analysis_result,
        "timestamp": datetime.utcnow()
    }
    try:
        # সরাসরি ডেটাবেসে মেসেজটি ইনসার্ট করা হচ্ছে
        collection.insert_one(payload)
        st.rerun()
    except Exception as e:
        st.error("Failed to send message.")

# প্রতি ৩ সেকেন্ড পর পর অটো-রিফ্রেশ হবে যেন সবার মেসেজ রিয়েল-টাইমে আসে
time.sleep(3)
st.rerun()
