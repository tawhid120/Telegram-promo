import asyncio
import os
import threading  # ওয়েব সার্ভার আলাদাভাবে চালানোর জন্য
from flask import Flask  # Render-কে "Live" রাখার জন্য ওয়েব সার্ভার

from telethon import TelegramClient, events, sessions
from telethon.errors.rpcerrorlist import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError

# --- Flask Web Server Setup ---
# এটি Uptime Robot-এর জন্য একটি নকল ওয়েব সার্ভার তৈরি করবে
app = Flask(__name__)
# Render ডায়নামিকভাবে এই PORT ভেরিয়েবলটি সেট করে
port = int(os.environ.get("PORT", 10000)) 

@app.route('/')
def hello_world():
    # Uptime Robot এই লেখাটি দেখতে পাবে
    return 'Bot is alive and running!' 

def run_flask():
    # 0.0.0.0 হোস্টে চললে Render এটি বাইরে থেকে অ্যাক্সেস করতে পারে
    app.run(host='0.0.0.0', port=port)
# --- End of Web Server Setup ---


# --- Your Telegram API Credentials ---
api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'

# --- Session Configuration (String Session) ---
# Render-এর Environment Variable থেকে সেশন স্ট্রিং লোড হবে
session_string = os.environ.get('TELETHON_SESSION_STRING')

if not session_string:
    print("CRITICAL ERROR: TELETHON_SESSION_STRING environment variable not set.")
    # সেশন স্ট্রিং ছাড়া বট চালানো সম্ভব নয়
else:
    print("Session string found. Initializing Telethon Client...")

# --- Target Configuration ---
group_usernames = [
    'Acs_Udvash_Link', 'buetkuetruetcuet', 'linkedstudies',
    'thejournyofsc24', 'hsc_sharing', 'ACSDISCUSSION',
    'HHEHRETW', 'chemistryteli', 'haters_hsc', 'hsc234',
    'studywar2021', 'DiscussionGroupEngineering', 'buetkuetruetcuet',
    'superb1k', 'Dacs2025',
]
image_path = 'Replit.jpg' # এই নামের ছবিটিও আপলোড করতে হবে
message_to_send = """
🤫 **ছাত্রজীবনের কয়েকটি গোপন চ্যানেল!**

👉 **All platforms class, note, guide PDF:** @PDFNexus
👉 **Free time এর মধ্যে earning tips**: @EarnovaX
👉 **HSC Guideline & problem helping groups**: @guildline01

🔴 Earn **14 Taka** selling per **Gmail**: [https://t.me/GmailFarmerBot?start=7647683104](https://t.me/GmailFarmerBot?start=7647683104)

🗣️ Spoken English Zone 🇬🇧
Spoken English, Vocabulary, Grammar ও IELTS শেখো সহজভাবে বাংলাসহ।
👉 ইংরেজি শেখার পারফেক্ট চ্যানেল!
Join Now: ⬇️
 [https://t.me/Spoken_English_Zone](https://t.me/Spoken_English_Zone)
"""

# Initialize the Telegram client using StringSession
# এখানে sessions.StringSession(session_string) ব্যবহার করা হয়েছে
client = TelegramClient(
    sessions.StringSession(session_string), 
    api_id, 
    api_hash
)

# --- আপনার মূল বট লজিক (অপরিবর্তিত) ---
@client.on(events.NewMessage(chats=group_usernames))
async def handler(event):
    if event.is_private or event.message.sender_id == (await client.get_me()).id:
        return

    print(f"New message detected in group '{event.chat.title}'. Posting...")
    try:
        await asyncio.sleep(2)
        await client.send_message(
            event.chat_id,
            message_to_send,
            file=image_path,
            parse_mode='md'
        )
        print("Advertisement posted successfully.")
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")
    except FloodWaitError as e:
        print(f"FloodWait: Waiting for {e.seconds} seconds.")
        await asyncio.sleep(e.seconds)
    except (ChatWriteForbiddenError, UserBannedInChannelError):
        print(f"Permission denied in group '{event.chat.title}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def main_bot():
    print("Bot starting with Telethon String Session...")
    await client.start()
    print("Client is connected and listening for messages.")
    await client.run_until_disconnected()

# --- Main execution ---
if __name__ == "__main__":
    if not session_string:
        print("Bot cannot start without TELETHON_SESSION_STRING.")
        print("Starting Flask server only so you can see this error in Render logs.")
        run_flask() # শুধু ফ্লাস্ক চলবে যাতে আপনি লগ দেখতে পারেন
    else:
        # একটি আলাদা থ্রেডে ওয়েব সার্ভার চালু করা হচ্ছে (Uptime Robot-এর জন্য)
        print("Starting Flask web server in a new thread...")
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()
        
        # মূল থ্রেডে টেলিগ্রাম বট চালু করা হচ্ছে
        print("Starting Telethon client in the main thread...")
        asyncio.run(main_bot())
