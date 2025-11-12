import asyncio
import logging
import os
import random
from itertools import cycle
from telethon import TelegramClient, events, sessions
from telethon.errors import (
    FloodWaitError, 
    UserBannedInChannelError, 
    ChatWriteForbiddenError, 
    ChannelPrivateError,
    ChatAdminRequiredError,
    UserNotParticipantError
)
from datetime import datetime

# --- ১. লগিং এবং কনফিগারেশন ---
#logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

#api_id = 20193909
#api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'

# আপনার সেশন ভেরিয়েবলগুলো এনভায়রনমেন্ট বা সরাসরি এখানে দিন
session_strings = [
    os.environ.get('SESSION_1'), # অথবা সরাসরি স্ট্রিং দিন
    os.environ.get('SESSION_2'),
    os.environ.get('SESSION_3')
]

# টার্গেট গ্রুপগুলোর ইউজারনেম
target_groups = [
    'chemistryteli', 'hsc_sharing', 'linkedstudies', 'hsc234', 'buetkuetruetcuet',
    'thejournyofhsc24', 'haters_hsc', 'Dacs2025', 'superb1k', 'studywar2021',
    'hscacademicandadmissionchatgroup', 'Acs_Udvash_Link', 'DiscussionGroupEngineering', 'HHEHRETW'
]

image_path = 'Replit1.jpg' # ছবি না থাকলে টেক্সট যাবে

message_text = """
**[𝐇𝐒𝐂 𝐆𝐞𝐧𝐢𝐮𝐬 𝐇𝐮𝐛](https://t.me/HSCGeniusHubMZ)**
                                           
**♛ HSC শিক্ষার্থীদের জন্য সাজানো-গোছানো স্টাডি কোর্স**

**ⓘ** সম্পূর্ণ ফ্রী এবং রিজনেবল প্রাইসে প্রিমিয়াম কোর্স!

**❖** মানসম্মত সাজানো গোছানো লেকচার 
**❖** পরীক্ষার জন্য বিশেষ গাইড ও প্রস্তুতি সহায়ক

**֎ আপনার পড়াশোনাকে করুন আরও সহজ, স্মার্ট ও কার্যকরী!**

**✮  Index  ✮**

**❶** **[HSC26 PCMB All Course](https://t.me/HSCGeniusHubMZ/92)**
**❷** **[HSC27 PCMB All Course](https://t.me/HSCGeniusHubMZ/93)** **❸** **[All EBI Course](https://t.me/HSCGeniusHubMZ/94)**

**➟ তাহলে আর দেরি কেন? এখনই** **[HSC Genius Hub](https://t.me/HSCGeniusHubMZ)** **এর সাথে যুক্ত হও!!**

**⎙ কোর্স কিনতে নক করুন: ➤ @HSCGeniusHubBot**

**⁀➴ প্রধান চ্যানেল:** **[HSC Genius Hub](https://t.me/HSCGeniusHubMZ)**

**────୨ৎ────**
"""

# --- ২. গ্লোবাল ভেরিয়েবল ---
clients = []           # সব ক্লায়েন্টের লিস্ট
sender_cycle = None    # ঘুরিয়ে ফিরিয়ে অ্যাকাউন্ট ব্যবহারের জন্য
debounce_tasks = {}    # টাইমার ট্র্যাক করার জন্য ডিকশনারি
WAIT_TIME = 15         # ১৫ সেকেন্ড অপেক্ষা

# --- ৩. হেল্পার ফাংশন: সব অ্যাকাউন্ট চালু করা ---
async def init_clients():
    global sender_cycle
    active_clients = []
    
    print("🔄 অ্যাকাউন্টগুলো কানেক্ট করা হচ্ছে...")
    
    for i, s_str in enumerate(session_strings):
        if not s_str: continue
        try:
            client = TelegramClient(
                sessions.StringSession(s_str), 
                api_id, api_hash,
                device_model=f"HSC Bot {i+1}",
                app_version="3.0"
            )
            await client.start()
            me = await client.get_me()
            print(f"✅ অ্যাকাউন্ট {i+1} কানেক্টেড: {me.first_name}")
            active_clients.append(client)
        except Exception as e:
            print(f"❌ অ্যাকাউন্ট {i+1} এরর: {e}")

    if not active_clients:
        print("⛔ কোনো অ্যাকাউন্ট কানেক্ট করা যায়নি।")
        exit()
        
    # সাইক্লিং ইটারেটর তৈরি (একটার পর একটা অ্যাকাউন্ট ব্যবহার করার জন্য)
    sender_cycle = cycle(active_clients)
    return active_clients

# --- ৪. স্মার্ট সেন্ডিং ফাংশন (একটার পর একটা ট্রাই করবে) ---
async def send_smart_message(chat_id, chat_name):
    global sender_cycle
    
    # ছবি আছে কিনা চেক করা
    file_to_send = image_path if os.path.exists(image_path) else None
    
    # মোট কতগুলো ক্লায়েন্ট আছে ততবার চেষ্টা করবে
    attempts = len(clients)
    sent_success = False
    
    logging.info(f"🚀 '{chat_name}' গ্রুপে মেসেজ পাঠানোর চেষ্টা করা হচ্ছে...")

    for _ in range(attempts):
        # সাইকেল থেকে পরের ক্লায়েন্ট নাও
        current_client = next(sender_cycle)
        me = await current_client.get_me()
        
        try:
            # মেসেজ পাঠানোর চেষ্টা
            await current_client.send_message(
                chat_id,
                message_text,
                file=file_to_send,
                link_preview=False
            )
            logging.info(f"✅ সফল! '{me.first_name}' এর মাধ্যমে '{chat_name}' এ পাঠানো হয়েছে।")
            sent_success = True
            break # সফল হলে লুপ ব্রেক করো (অন্যরা আর পাঠাবে না)
            
        except (UserNotParticipantError, ChannelPrivateError):
            logging.warning(f"⚠️ '{me.first_name}' এই গ্রুপে নেই। পরের অ্যাকাউন্ট ট্রাই হচ্ছে...")
        except (ChatWriteForbiddenError, UserBannedInChannelError):
            logging.warning(f"🚫 '{me.first_name}' এখানে নিষিদ্ধ/ব্যানড। পরের অ্যাকাউন্ট ট্রাই হচ্ছে...")
        except FloodWaitError as e:
            logging.warning(f"⏳ '{me.first_name}' ফ্লাড ওয়েট ({e.seconds}s)। পরের অ্যাকাউন্ট ট্রাই হচ্ছে...")
        except Exception as e:
            logging.error(f"❌ অজানা সমস্যা ({me.first_name}): {e}")

    if not sent_success:
        logging.error(f"⛔ ব্যর্থ: কোনো অ্যাকাউন্টই '{chat_name}' এ মেসেজ পাঠাতে পারেনি।")

# --- ৫. টাইমার লজিক (আসল জাদুকরী অংশ) ---
async def debounce_handler(event):
    chat_id = event.chat_id
    chat_name = getattr(event.chat, 'title', str(chat_id))
    
    # ১. যদি আগে থেকেই এই গ্রুপের জন্য কোনো টাইমার (Task) চালু থাকে, সেটা বাতিল করো
    if chat_id in debounce_tasks:
        task = debounce_tasks[chat_id]
        if not task.done():
            task.cancel() # আগের গণনা বাতিল!
            # logging.info(f"⏳ রিসেট: '{chat_name}' এ নতুন মেসেজ এসেছে, টাইমার আবার শুরু...")

    # ২. নতুন টাইমার টাস্ক তৈরি করো
    # আমরা asyncio.create_task ব্যবহার করছি যাতে এটি ব্যাকগ্রাউন্ডে চলে
    debounce_tasks[chat_id] = asyncio.create_task(process_delayed_message(chat_id, chat_name))

async def process_delayed_message(chat_id, chat_name):
    try:
        # ১৫ সেকেন্ড অপেক্ষা করো
        await asyncio.sleep(WAIT_TIME)
        
        # যদি ১৫ সেকেন্ড কোনো বাধা ছাড়া পার হয়, মেসেজ পাঠাও
        await send_smart_message(chat_id, chat_name)
        
        # মেমোরি ক্লিয়ার করো
        if chat_id in debounce_tasks:
            del debounce_tasks[chat_id]
            
    except asyncio.CancelledError:
        # যদি স্লিপের মধ্যে টাস্ক ক্যান্সেল হয়, তার মানে নতুন মেসেজ এসেছে
        # তাই আমরা এখানে কিছুই করব না (ফাংশন চুপচাপ বন্ধ হবে)
        pass

# --- ৬. মেইন ফাংশন ---
async def main():
    global clients
    
    # সব ক্লায়েন্ট কানেক্ট করা
    clients = await init_clients()
    
    # *** ট্রিক: শুধুমাত্র ১ম অ্যাকাউন্ট দিয়ে মনিটর করা ***
    # সব অ্যাকাউন্ট দিয়ে মনিটর করলে ৩ গুণ ইভেন্ট ফায়ার হয়, যা স্প্যামের কারণ।
    monitor_client = clients[0] 
    me = await monitor_client.get_me()
    
    print(f"\n👁️ মনিটরিং চালু আছে: {me.first_name} এর মাধ্যমে।")
    print(f"⏱️ স্প্যাম প্রটেকশন: {WAIT_TIME} সেকেন্ড।")
    print("--------------------------------------------------")

    # ইভেন্ট হ্যান্ডলার শুধু মনিটর ক্লায়েন্টে অ্যাড করা
    @monitor_client.on(events.NewMessage(chats=target_groups, incoming=True))
    async def handler(event):
        # নিজের বা অন্য বটের মেসেজ ইগনোর করো
        if event.sender_id == (await monitor_client.get_me()).id:
            return
        await debounce_handler(event)

    # বট চালু রাখা
    await monitor_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
