import asyncio
import logging
import os
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait, ChatWriteForbidden

# --- ১. কনফিগারেশন ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

API_ID = 20193909
API_HASH = '82cd035fc1eb439bda68b2bfc75a57cb'

# Pyrogram সেশন স্ট্রিং (Telethon এর স্ট্রিং এখানে কাজ করবে না, নতুন করে জেনারেট করতে হবে)
SESSION_STRINGS = [
    os.environ.get('SESSION_1'), 
    os.environ.get('SESSION_2'),
    # আরও থাকলে এখানে যোগ করো
]

# টার্গেট গ্রুপগুলোর ইউজারনেম (লিংক ছাড়া, শুধু ইউজারনেম)
TARGET_GROUPS = [
    'chemistryteli', 'hsc_sharing', 'linkedstudies', 'hsc234', 'buetkuetruetcuet',
    'thejournyofhsc24', 'haters_hsc', 'Dacs2025', 'superb1k', 'studywar2021',
    'Acs_Udvash_Link', 'DiscussionGroupEngineering', 'HHEHRETW'
]

# ছবির পাথ (তোমার ফোল্ডারে যেন এই নামের ছবি থাকে)
IMAGE_PATH = 'IMG-20251205-WA0022.jpg'

# --- ২. হুবহু টেমপ্লেট (Markdown ফরম্যাটে) ---
# স্ক্রিনশটের মতো দেখতে > (Quote) এবং ** (Bold) ব্যবহার করা হয়েছে
# এই ভেরিয়েবলটি তোমার কোডে ব্যবহার করো
CAPTION_TEXT = """
>🎓 HSC & Admission Guideline Channel

যারা সত্যি সিরিয়াসলি HSC + ভর্তি প্রস্তুতি নিতে চাও — এখানে পাচ্ছো দৈনিক টিপস, স্টাডি স্ট্র্যাটেজি, MCQ গাইডলাইন আর মোটিভেশন।

👉 জয়েন করো: https://t.me/guildeline01
>সঠিক গাইডলাইনেই সঠিক প্রস্তুতি। 🚀
"""

# মেসেজ পাঠানোর সময় এভাবে লিখবে:
# await app.send_photo(chat_id, photo=IMAGE_PATH, caption=CAPTION_TEXT)


# গ্লোবাল ভেরিয়েবলস
clients = []
my_user_ids = []
processed_chats = {} # টাইমার হ্যান্ডেল করার জন্য

# --- ৩. ক্লায়েন্ট সেটআপ ---
async def start_clients():
    print("🔄 অ্যাকাউন্টগুলো কানেক্ট করা হচ্ছে...")
    for i, session in enumerate(SESSION_STRINGS):
        if not session: continue
        try:
            app = Client(f"account_{i}", api_id=API_ID, api_hash=API_HASH, session_string=session)
            await app.start()
            me = await app.get_me()
            clients.append(app)
            my_user_ids.append(me.id)
            print(f"✅ অ্যাকাউন্ট {i+1} রেডি: {me.first_name}")
        except Exception as e:
            print(f"❌ অ্যাকাউন্ট {i+1} এরর: {e}")
    
    if not clients:
        print("⛔ কোনো অ্যাকাউন্ট কানেক্ট করা যায়নি।")
        exit()

# --- ৪. মেসেজ সেন্ডিং লজিক ---
async def send_ad_message(chat_id):
    # সাইক্লিং লজিক (র‍্যান্ডমলি বা সিরিয়াল অনুযায়ী একটা আইডি পিক করবে)
    import random
    sender_app = random.choice(clients)
    
    try:
        # ছবি এবং ক্যাপশন পাঠানো
        await sender_app.send_photo(
            chat_id=chat_id,
            photo=IMAGE_PATH,
            caption=CAPTION_TEXT
        )
        logging.info(f"🚀 মেসেজ পাঠানো হয়েছে চ্যাট ID: {chat_id} - {sender_app.me.first_name} দিয়ে")
    except FloodWait as e:
        logging.warning(f"⏳ FloodWait: {e.value} সেকেন্ড অপেক্ষা করতে হবে।")
        await asyncio.sleep(e.value)
    except ChatWriteForbidden:
        logging.error(f"🚫 এই গ্রুপে মেসেজ লেখার অনুমতি নেই: {chat_id}")
    except Exception as e:
        logging.error(f"❌ সমস্যা হয়েছে: {e}")

# --- ৫. মেইন হ্যান্ডলার ---
async def main():
    await start_clients()
    
    # মনিটরিং করার জন্য প্রথম ক্লায়েন্ট ব্যবহার করছি (যেকোনো একটা হলেই হয়)
    monitor_app = clients[0]

    print("\n👁️ মনিটরিং শুরু হয়েছে...")
    print("--------------------------------------------------")

    @monitor_app.on_message(filters.chat(TARGET_GROUPS) & ~filters.me)
    async def incoming_handler(client, message):
        chat_id = message.chat.id
        
        # যদি মেসেজটি আমাদের নিজেদের কোনো বটের হয়, ইগনোর করো
        if message.from_user and message.from_user.id in my_user_ids:
            return

        # ডিবাউন্স লজিক (একই গ্রুপে বারবার মেসেজ না যাওয়ার জন্য)
        # যদি এই গ্রুপে অলরেডি টাইমার চলতে থাকে, সেটা বাতিল করো এবং নতুন করে শুরু করো
        if chat_id in processed_chats:
            processed_chats[chat_id].cancel()
        
        # নতুন টাস্ক তৈরি
        processed_chats[chat_id] = asyncio.create_task(wait_and_send(chat_id))

    async def wait_and_send(chat_id):
        try:
            # ১৫ সেকেন্ড অপেক্ষা (যাতে মনে হয় মানুষ রিপ্লাই দিচ্ছে)
            await asyncio.sleep(15)
            await send_ad_message(chat_id)
        except asyncio.CancelledError:
            pass # নতুন মেসেজ আসলে আগেরটা বাতিল হবে
        finally:
            processed_chats.pop(chat_id, None)

    # প্রোগ্রাম রানিং রাখা
    await idle()
    
    # সব ক্লায়েন্ট বন্ধ করা
    for app in clients:
        await app.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
