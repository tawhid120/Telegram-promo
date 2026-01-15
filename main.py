import asyncio
import logging
import os
import random
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait, ChatWriteForbidden

# --- ১. কনফিগারেশন ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

API_ID = 20193909
API_HASH = '82cd035fc1eb439bda68b2bfc75a57cb'

# Pyrogram সেশন স্ট্রিং
SESSION_STRINGS = [
    os.environ.get('SESSION_1'), 
    os.environ.get('SESSION_2'),
]

# টার্গেট গ্রুপগুলোর ইউজারনেম
TARGET_GROUPS = [
    'chemistryteli', 'hsc_sharing', 'linkedstudies', 'hsc234', 'buetkuetruetcuet',
    'thejournyofhsc24', 'haters_hsc', 'Dacs2025', 'superb1k', 'studywar2021',
    'Acs_Udvash_Link', 'DiscussionGroupEngineering', 'HHEHRETW', 'hscacademicandadmissionchatgroup', -1001549949017, -1002250041542
]

# ডিফল্ট ছবি (যদি কোনো টেমপ্লেটে ছবির নাম না থাকে)
DEFAULT_IMAGE = 'IMG-20251205-WA0022.jpg'
TEMPLATE_FILE = 'guideline.txt'

# গ্লোবাল ভেরিয়েবলস
clients = []
my_user_ids = []
processed_chats = {} 
templates = [] # এখানে এখন ডিকশনারি আকারে ডেটা থাকবে

# --- ২. টেমপ্লেট লোডার ফাংশন (আপডেট করা হয়েছে) ---
def load_templates():
    global templates
    try:
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        raw_msgs = [msg.strip() for msg in content.split("###---###") if msg.strip()]
        
        parsed_templates = []
        for msg in raw_msgs:
            lines = msg.split('\n')
            first_line = lines[0].strip()
            
            # চেক করা হচ্ছে প্রথম লাইনে "Image:" আছে কিনা
            if first_line.lower().startswith("image:"):
                # ছবির নাম আলাদা করা হচ্ছে
                image_path = first_line.split(":", 1)[1].strip()
                # প্রথম লাইন বাদে বাকিটুকু ক্যাপশন
                caption = "\n".join(lines[1:]).strip()
            else:
                # যদি Image: ট্যাগ না থাকে, তবে ডিফল্ট ছবি ব্যবহার হবে
                image_path = DEFAULT_IMAGE
                caption = msg
            
            parsed_templates.append({
                'image': image_path,
                'caption': caption
            })
            
        templates = parsed_templates
        print(f"✅ মোট {len(templates)} টি টেমপ্লেট লোড করা হয়েছে।")
        
    except FileNotFoundError:
        print(f"❌ '{TEMPLATE_FILE}' ফাইলটি পাওয়া যায়নি!")
        exit()

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

# --- ৪. মেসেজ সেন্ডিং লজিক (আপডেট করা হয়েছে) ---
async def send_ad_message(chat_id):
    sender_app = random.choice(clients)
    
    if not templates:
        logging.error("❌ কোনো টেমপ্লেট লোড করা নেই!")
        return

    # র‍্যান্ডম টেমপ্লেট সিলেক্ট করা (যাতে ছবি ও ক্যাপশন দুটোই আছে)
    selection = random.choice(templates)
    photo_path = selection['image']
    caption_text = selection['caption']
    
    # ছবি ফাইল আছে কিনা চেক করা (অপশনাল কিন্তু ভালো প্র্যাকটিস)
    if not os.path.exists(photo_path):
        logging.warning(f"⚠️ ছবি পাওয়া যায়নি: {photo_path}, ডিফল্ট ছবি ব্যবহার করা হচ্ছে।")
        photo_path = DEFAULT_IMAGE

    try:
        await sender_app.send_photo(
            chat_id=chat_id,
            photo=photo_path,
            caption=caption_text
        )
        logging.info(f"🚀 মেসেজ পাঠানো হয়েছে চ্যাট ID: {chat_id} - {sender_app.me.first_name} দিয়ে | ছবি: {photo_path}")
    except FloodWait as e:
        logging.warning(f"⏳ FloodWait: {e.value} সেকেন্ড অপেক্ষা করতে হবে।")
        await asyncio.sleep(e.value)
    except ChatWriteForbidden:
        logging.error(f"🚫 এই গ্রুপে মেসেজ লেখার অনুমতি নেই: {chat_id}")
    except Exception as e:
        logging.error(f"❌ সমস্যা হয়েছে: {e}")

# --- ৫. মেইন হ্যান্ডলার ---
async def main():
    load_templates()
    await start_clients()
    
    monitor_app = clients[0]

    print("\n👁️ মনিটরিং শুরু হয়েছে...")
    print("--------------------------------------------------")

    @monitor_app.on_message(filters.chat(TARGET_GROUPS) & ~filters.me)
    async def incoming_handler(client, message):
        chat_id = message.chat.id
        
        if message.from_user and message.from_user.id in my_user_ids:
            return

        if chat_id in processed_chats:
            processed_chats[chat_id].cancel()
        
        processed_chats[chat_id] = asyncio.create_task(wait_and_send(chat_id))

    async def wait_and_send(chat_id):
        try:
            await asyncio.sleep(15)
            await send_ad_message(chat_id)
        except asyncio.CancelledError:
            pass 
        finally:
            processed_chats.pop(chat_id, None)

    await idle()
    
    for app in clients:
        await app.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
