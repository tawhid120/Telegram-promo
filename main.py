import asyncio
import logging
import os
import random
from itertools import cycle
from telethon import TelegramClient, events, sessions
from telethon.tl.types import User
from telethon.errors.rpcerrorlist import (
    FloodWaitError, 
    UserBannedInChannelError, 
    ChatWriteForbiddenError, 
    ChannelPrivateError,
    ChatAdminRequiredError
)

# --- ১. লগিং সেটআপ (Logging Setup) ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
# Telethon এর নিজস্ব লগ কমিয়ে রাখা হয়েছে যাতে কনসোল ক্লিন থাকে
logging.getLogger('telethon').setLevel(logging.WARNING)

# --- ২. কনফিগারেশন এবং ক্রেডেনশিয়াল ---
api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'

# Sevalla Environment Variables থেকে সেশন লোড করা
session_strings = [
    os.environ.get('SESSION_1'),
    os.environ.get('SESSION_2'),
    os.environ.get('SESSION_3')
]

# যে গ্রুপগুলো মনিটর করা হবে
group_usernames = [
    'chemistryteli', 'hsc_sharing', 'linkedstudies', 'hsc234', 'buetkuetruetcuet',
    'thejournyofhsc24', 'haters_hsc', 'Dacs2025', 'superb1k', 'studywar2021',
    'hscacademicandadmissionchatgroup', 'Acs_Udvash_Link', 'DiscussionGroupEngineering', 'HHEHRETW'
]

image_path = 'Replit1.jpg'  # নিশ্চিত করুন এই ছবিটি Sevalla তে আপলোড করা আছে

message_to_send = """
**[𝐇𝐒𝐂 𝐆𝐞𝐧𝐢𝐮𝐬 𝐇𝐮𝐛](https://t.me/HSCGeniusHubMZ)**
                                           
**♛ HSC শিক্ষার্থীদের জন্য সাজানো-গোছানো স্টাডি কোর্স**

**ⓘ** সম্পূর্ণ ফ্রী এবং রিজনেবল প্রাইসে প্রিমিয়াম কোর্স!

**❖** মানসম্মত সাজানো গোছানো লেকচার 
**❖** পরীক্ষার জন্য বিশেষ গাইড ও প্রস্তুতি সহায়ক

**֎ আপনার পড়াশোনাকে করুন আরও সহজ, স্মার্ট ও কার্যকরী!**

**✮  Index  ✮**

**❶** **[HSC26 PCMB All Course](https://t.me/HSCGeniusHubMZ/92)**
**❷** **[HSC27 PCMB All Course](https://t.me/HSCGeniusHubMZ/93)** **❸** **[All EBI Course](https://t.me/HSCGeniusHubMZ/94)**

**➟ তাহলে আর দেরি কেন? এখনই** **[HSC Genius Hub](https://t.me/HSCGeniusHubMZ)** **এর সাথে যুক্ত হও!!**

**⎙ কোর্স কিনতে নক করুন: ➤ @HSCGeniusHubBot**

**⁀➴ প্রধান চ্যানেল:** **[HSC Genius Hub](https://t.me/HSCGeniusHubMZ)**

**────୨ৎ────**
"""

# --- ৩. গ্লোবাল ভেরিয়েবল (Global Variables) ---
active_clients = []        # কানেক্টেড অ্যাকাউন্ট লিস্ট
sender_cycle = None        # অ্যাকাউন্ট রোটেশনের জন্য
send_lock = asyncio.Lock() # এক সাথে একাধিক মেসেজ আটকাতে লক
debounce_tasks = {}        # টাইমার ট্র্যাক করার জন্য
DEBOUNCE_DELAY = 15        # মেসেজ আসার পর কত সেকেন্ড অপেক্ষা করবে

# --- ৪. হেল্পার ফাংশন (Helper Functions) ---

async def start_all_clients():
    """Sevalla এনভায়রনমেন্ট থেকে সেশন নিয়ে সব ক্লায়েন্ট কানেক্ট করবে"""
    global sender_cycle, active_clients
    active_clients = []
    
    logging.info("🔄 Initializing accounts from Environment Variables...")
    
    # ইমেজ ফাইল আছে কিনা চেক করা
    if not os.path.exists(image_path):
        logging.critical(f"❌ CRITICAL: '{image_path}' file not found! Upload it to Sevalla.")
        # ফাইল না থাকলেও কোড চলবে, কিন্তু ছবি যাবে না
    
    for i, s_str in enumerate(session_strings):
        if not s_str:
            logging.warning(f"⚠️ SESSION_{i+1} not found in environment variables. Skipping.")
            continue
            
        try:
            # প্রতিটি অ্যাকাউন্টের জন্য আলাদা সেশন ফাইল তৈরি হবে মেমোরিতে
            client = TelegramClient(sessions.StringSession(s_str), api_id, api_hash)
            await client.start()
            
            me = await client.get_me()
            logging.info(f"✅ Account {i+1} Connected: {me.first_name} (ID: {me.id})")
            active_clients.append(client)
        except Exception as e:
            logging.error(f"❌ Failed to connect Account {i+1}: {e}")

    if not active_clients:
        logging.critical("⛔️ No accounts could be connected. Check your Session Strings. Exiting.")
        exit()

    # সাইকেল তৈরি করা (যেমন: ১ -> ২ -> ৩ -> ১...)
    sender_cycle = cycle(active_clients)
    logging.info(f"🚀 Total {len(active_clients)} accounts ready for rotation.")
    return active_clients

async def send_promotional_message(chat_id, chat_title):
    """
    স্মার্ট ফেইলওভার সিস্টেম:
    এটি একটির পর একটি অ্যাকাউন্ট দিয়ে চেষ্টা করবে যতক্ষণ না মেসেজ পাঠানো সফল হয়।
    """
    global sender_cycle
    
    # লক ব্যবহার করা হচ্ছে যাতে আগের কাজ শেষ না হওয়া পর্যন্ত নতুন কাজ না ধরে
    async with send_lock:
        logging.info(f"⚙️ Processing message task for '{chat_title}'...")
        
        # আমাদের হাতে যতগুলো অ্যাকাউন্ট আছে, সর্বোচ্চ ততবার চেষ্টা করব
        max_attempts = len(active_clients)
        success = False
        
        # ইমেজ পাথ চেক (যদি ফাইল ডিলিট হয়ে গিয়ে থাকে)
        file_to_send = image_path if os.path.exists(image_path) else None
        if not file_to_send:
            logging.warning("⚠️ Image file missing, sending text only.")

        for attempt in range(max_attempts):
            # সাইকেল থেকে পরের ক্লায়েন্ট নেওয়া
            current_client = next(sender_cycle)
            me = await current_client.get_me()

            try:
                # চেষ্টা করা হচ্ছে...
                await current_client.send_message(
                    chat_id, 
                    message_to_send, 
                    file=file_to_send, 
                    parse_mode='md', 
                    link_preview=False
                )
                
                # যদি কোড এখানে আসে, তার মানে মেসেজ সফলভাবে গেছে
                logging.info(f"  ✅ SUCCESS: Message sent by '{me.first_name}' to '{chat_title}'")
                success = True
                
                # সফল হলে লুপ ব্রেক করুন (আর অন্য অ্যাকাউন্ট দিয়ে পাঠানোর দরকার নেই)
                # সেফটির জন্য ২ থেকে ৫ সেকেন্ড বিরতি
                await asyncio.sleep(random.randint(2, 5))
                break 

            except (ValueError, ChannelPrivateError):
                # অ্যাকাউন্ট গ্রুপে নেই
                logging.warning(f"  ⚠️ '{me.first_name}' is NOT in the group. Switching account...")
            
            except (ChatWriteForbiddenError, UserBannedInChannelError, ChatAdminRequiredError):
                # অ্যাকাউন্ট ব্যানড বা পারমিশন নেই
                logging.warning(f"  🚫 '{me.first_name}' cannot write in this chat. Switching account...")

            except FloodWaitError as e:
                # ফ্লাড ওয়েট খেলে অপেক্ষা না করে পরের অ্যাকাউন্টে সুইচ করবে
                logging.warning(f"  ⏳ '{me.first_name}' hit FloodWait ({e.seconds}s). Switching account...")

            except Exception as e:
                # অন্য কোনো অজানা সমস্যা
                logging.error(f"  ❌ Error with '{me.first_name}': {e}")

        if not success:
            logging.error(f"⛔️ FAILED: Tried all {max_attempts} accounts but none could send message to '{chat_title}'.")
        
        # টাস্ক ক্লিনআপ
        if chat_id in debounce_tasks:
            del debounce_tasks[chat_id]

# --- ৫. ইভেন্ট হ্যান্ডলার (Message Listener) ---
async def message_handler(event):
    """নতুন মেসেজ আসলে ডিলে টাইমার সেট বা রিসেট করে"""
    sender = await event.get_sender()
    
    # নিজের বট বা নিজের অ্যাকাউন্টের মেসেজ হলে ইগনোর করবে
    if not sender or (isinstance(sender, User) and sender.bot):
        return

    # লগিং: নতুন মেসেজ ডিটেক্ট হয়েছে
    chat_title = event.chat.title if hasattr(event.chat, 'title') else "Unknown Chat"
    # logging.info(f"📩 New message in '{chat_title}' - Resetting timer.")

    chat_id = event.chat.id
    
    # যদি আগে থেকেই টাইমার চলতে থাকে, সেটা বাতিল করে নতুন করে শুরু করবে
    if chat_id in debounce_tasks:
        debounce_tasks[chat_id].cancel()
        
    async def schedule_send():
        try:
            logging.info(f"⏳ Timer started for '{chat_title}': Waiting {DEBOUNCE_DELAY}s...")
            await asyncio.sleep(DEBOUNCE_DELAY)
            # টাইমার শেষ হলে মেসেজ ফাংশন কল করবে
            await send_promotional_message(chat_id, chat_title)
        except asyncio.CancelledError:
            # যদি টাইমার রিসেট হয়
            pass
            
    # নতুন টাস্ক তৈরি করে ডিকশনারিতে রাখা
    debounce_tasks[chat_id] = asyncio.create_task(schedule_send())

# --- ৬. মেইন ফাংশন (Main Execution) ---
async def main():
    print("\n––––––––––––––––––––––––––––––––––––––")
    print("    HSC Genius Hub - Multi-Account Bot")
    print("––––––––––––––––––––––––––––––––––––––\n")

    # ১. সব ক্লায়েন্ট স্টার্ট করা
    clients = await start_all_clients()
    
    # ২. মনিটরিংয়ের জন্য শুধুমাত্র ১ম ক্লায়েন্ট ব্যবহার করা হবে
    # (কারণ সব ক্লায়েন্ট দিয়ে মনিটর করলে একই মেসেজ ৩ বার প্রসেস হবে)
    monitor_client = clients[0]
    monitor_me = await monitor_client.get_me()
    
    logging.info(f"👁️ Monitoring Active via: {monitor_me.first_name}")
    
    # ৩. ইভেন্ট হ্যান্ডলার সেট করা
    # আমরা এখানে নির্দিষ্ট গ্রুপ ইউজারনেম ফিল্টার হিসেবে ব্যবহার করছি
    monitor_client.add_event_handler(
        message_handler,
        events.NewMessage(chats=group_usernames)
    )
    
    logging.info("✅ Bot is running securely on Sevalla. Press Ctrl+C to stop.")
    
    # ৪. সংযোগ বিচ্ছিন্ন না হওয়া পর্যন্ত চালানো
    await monitor_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\n🛑 Bot stopped by user.")
    except Exception as e:
        logging.critical(f"❌ Critical Error in Main Loop: {e}", exc_info=True)

