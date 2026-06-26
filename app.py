import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Chat Moderator", page_icon="💬", layout="centered")

st.title("💬 AI Chat Moderator & WhatsApp Group")
st.write("Real-time Cloud Chat Room with Real AI Analysis!")

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

# Fetch message history from backend (Time out বাড়িয়ে ৩ সেকেন্ড করা হলো)
chat_history = []
try:
    response = requests.get("http://127.0.0.1:8000/messages", timeout=3)
    if response.status_code == 200:
        chat_history = response.json()
except:
    chat_history = []

# Show messages on screen
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
            
        st.caption(f"🤖 AI Analysis | Emotion: {analysis.get('emotion')} | Toxicity: {analysis.get('toxicity')}")
else:
    st.info("No messages yet or synchronizing with server...")
st.write("---")

# New message input box
user_message = st.chat_input("Type your message here...")

if user_message:
    payload = {"text": user_message, "username": st.session_state.username}
    try:
        # এখানে timeout বাড়িয়ে ৫ সেকেন্ড করা হলো যেন ফ্রন্টএন্ড তাড়াহুড়ো না করে
        res = requests.post("http://127.0.0.1:8000/analyze", json=payload, timeout=5)
        if res.status_code == 200:
            st.rerun()
    except:
        st.error("Server is busy. Retrying...")

# Auto-refresh loop every 3 seconds
time.sleep(3)
st.rerun()