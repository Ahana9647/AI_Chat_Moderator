from fastapi import FastAPI
from pymongo import MongoClient
from textblob import TextBlob
import datetime

app = FastAPI(title="AI Chat Moderator Backend")

# মঙ্গোডিবি ক্লাউড কানেকশন (পাসওয়ার্ড সহ রেডি করা আছে)
try:
    client = MongoClient("mongodb+srv://ahana741222_db_user:xovyPVFSibWK6moy@whatsappcluster.vo6e4k0.mongodb.net/?retryWrites=true&w=majority&appName=WhatsappCluster", serverSelectionTimeoutMS=2000)
    db = client["ai_chat_database"]
    chat_collection = db["messages_history"]
    client.server_info()
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    chat_collection = None

@app.get("/")
def home():
    return {"status": "success", "message": "Backend Server is running!"}

# ডেটাবেজ থেকে সব পুরানো মেসেজ তুলে আনার জন্য রুট
@app.get("/messages")
def get_messages():
    if chat_collection is not None:
        messages = list(chat_collection.find({}, {"_id": 0}).sort("timestamp", 1))
        return messages
    return []

@app.post("/analyze")
def analyze_message(user_data: dict):
    text = user_data.get("text", "")
    username = user_data.get("username", "Anonymous")
    
    # আসল এআই অ্যানালাইসিস (TextBlob)
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    
    if sentiment > 0.2:
        emotion = "Positive 😊"
        toxicity = "Safe ✅"
    elif sentiment < -0.2:
        emotion = "Negative 😡"
        toxicity = "Toxic ⚠️"
    else:
        emotion = "Neutral 😐"
        toxicity = "Safe ✅"
        
    analysis_result = {
        "emotion": emotion,
        "toxicity": toxicity,
        "intent": "General Chat 💬"
    }
    
    document = {
        "username": username,
        "text": text,
        "analysis": analysis_result,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    if chat_collection is not None:
        try:
            chat_collection.insert_one(document)
            print(f"💾 Message from {username} saved to MongoDB!")
        except Exception as e:
            print(f"❌ Failed to save: {e}")
            
    return analysis_result