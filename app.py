import asyncio
import os
import threading
from flask import Flask
from bot import start_telethon_bot  # bot.py ফাইল থেকে ফাংশনটি ইম্পোর্ট করা হলো

# --- Flask Web Server Setup (for Gunicorn & Uptime Robot) ---
# Gunicorn এই 'app' ভেরিয়েবলটিকে খুঁজবে
app = Flask(__name__)

@app.route('/')
def hello_world():
    # Uptime Robot এই মেসেজটি দেখবে
    return 'Flask server is running. Telethon bot is active in background.'

# --- Telethon Bot Thread ---
def run_bot_in_background():
    """
    একটি নতুন থ্রেডে টেলিগ্রাম বটটি চালু করে।
    """
    print("Starting Telethon client in a new thread...")
    # Telethon-এর জন্য একটি নতুন ইভেন্ট লুপ তৈরি করা হচ্ছে
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_telethon_bot())

# --- মূল কোড 실행 ---
# Gunicorn যখন এই app.py ফাইলটি লোড করবে, তখন এই কোডটি চলবে
print("Starting background bot thread...")
# একটি আলাদা থ্রেড তৈরি করা হচ্ছে যাতে Flask সার্ভার ব্লক না হয়
bot_thread = threading.Thread(target=run_bot_in_background)
bot_thread.daemon = True  # True সেট করলে মূল অ্যাপ বন্ধ হলে থ্রেডও বন্ধ হয়ে যাবে
bot_thread.start()

# **বিশেষ নোট:** Gunicorn নিজেই সার্ভারটি চালাবে,
# তাই এখানে `app.run()` বা `if __name__ == "__main__":` ব্লকের কোনো প্রয়োজন নেই।
