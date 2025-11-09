import os
import threading
from flask import Flask
# bot.py থেকে নতুন 'run_bot' ফাংশনটি ইম্পোর্ট করা হচ্ছে
from bot import run_bot 

# --- Flask Web Server Setup ---
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Flask server is running. Telethon bot is active in background.'

# --- Telethon Bot Thread ---
def run_bot_in_background():
    """
    একটি নতুন থ্রেডে টেলিগ্রাম বটটি চালু করে।
    এই ফাংশনটি কোনো asyncio ম্যানেজ করবে না, শুধু bot.py-কে কল করবে।
    """
    print("Starting bot.py in a new thread...")
    try:
        run_bot() # bot.py-এর run_bot() ফাংশনটি সরাসরি কল করা হচ্ছে
    except Exception as e:
        print(f"Error starting bot thread: {e}")

# --- Gunicorn Start ---
print("Starting background bot thread...")
bot_thread = threading.Thread(target=run_bot_in_background)
bot_thread.daemon = True
bot_thread.start()
