import asyncio
import logging
import os
import time
from itertools import cycle
from telethon import TelegramClient, events, sessions
from telethon.errors import (
    FloodWaitError, 
    UserBannedInChannelError, 
    ChatWriteForbiddenError, 
    ChannelPrivateError,
    ChatAdminRequiredError
)

# --- ১. বেসিক সেটআপ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'

session_strings = [
    os.environ.get('SESSION_1'), 
    os.environ.get('SESSION_2'),
    os.environ.get('SESSION_3')
]

target_groups = [
    'chemistryteli', 'hsc_sharing', 'linkedstudies', 'hsc234', 'buetkuetruetcuet',
    'thejournyofhsc24', 'haters_hsc', 'Dacs2025', 'superb1k', 'studywar2021',
    'hscacademicandadmissionchatgroup', 'Acs_Udvash_Link', 'DiscussionGroupEngineering', 'HHEHRETW'
]

image_path = 'Replit1.jpg' 

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

# --- ২. কন্ট্রোল ভেরিয়েবল ---
clients = []
sender_cycle = None
my_bot_ids = []

# কোড যাতে গুলিয়ে না ফেলে, তাই সব হিসাব এখানে রাখা হবে
last_msg_time = {}    # কোন গ্রুপে শেষ কখন মানুষ মেসেজ দিয়েছে
active_monitors = []  # কোন কোন গ্রুপে বর্তমানে টাইমার চলছে
DELAY_SECONDS = 15    # ১৫ সেকেন্ড চুপ থাকার নিয়ম

# --- ৩. হেল্পার ফাংশন ---
async def init_clients():
    global sender_cycle, my_bot_ids
    active_clients = []
    my_bot_ids = []
    
    print("⚙️ সিস্টেম সেটআপ হচ্ছে...")
    
    for i, s_str in enumerate(session_strings):
        if not s_str: continue
        try:
            client = TelegramClient(
                sessions.StringSession(s_str), 
                api_id, api_hash,
                device_model=f"HSC Bot {i+1}",
                app_version="Final Fixed"
            )
            await client.start()
            me = await client.get_me()
            my_bot_ids.append(me.id)
            active_clients.append(client)
            print(f"✅ আইডি যুক্ত হয়েছে: {me.first_name} (ID: {me.id})")
        except Exception as e:
            print(f"❌ একাউন্ট এরর: {e}")

    if not active_clients:
        exit()
        
    sender_cycle = cycle(active_clients)
    return active_clients

# --- ৪. মেসেজ পাঠানোর ফাংশন ---
async def send_safe_message(chat_id, chat_name):
    global sender_cycle
    
    file_to_send = image_path if os.path.exists(image_path) else None
    
    # চেষ্টা করার সর্বোচ্চ সংখ্যা (যতগুলো একাউন্ট আছে)
    attempts = len(clients)
    
    logging.info(f"📤 '{chat_name}' - ১৫ সেকেন্ড নীরবতা শেষ। এখন মেসেজ পাঠানো হচ্ছে...")

    for _ in range(attempts):
        current_client = next(sender_cycle)
        
        # পাঠানোর আগে আবার চেক করা যে এই একাউন্টটা ব্যান আছে কিনা (সিম্পল ট্রাই)
        try:
            await current_client.send_message(
                chat_id,
                message_text,
                file=file_to_send,
                link_preview=False
            )
            me = await current_client.get_me()
            logging.info(f"✅ সফল! '{me.first_name}' মেসেজ দিয়েছে।")
            return # সফল হলে ফাংশন থেকে বের হয়ে যাও
            
        except Exception as e:
            # কোনো এরর হলে লগ দেখাবে কিন্তু কোড থামবে না, পরের একাউন্ট ট্রাই করবে
            # logging.error(f"⚠️ ব্যর্থ: {e}") 
            pass

    logging.error(f"⛔ সব একাউন্ট ব্যর্থ '{chat_name}' গ্রুপে।")

# --- ৫. আসল লজিক (The Watcher) ---
async def waiter_task(chat_id, chat_name):
    """
    এই ফাংশনটি প্রতি ১ সেকেন্ড পর পর চেক করবে যে ১৫ সেকেন্ড পার হয়েছে কিনা।
    """
    try:
        while True:
            # বর্তমান সময় এবং শেষ মেসেজের সময়ের পার্থক্য বের করা
            current_time = time.time()
            last_time = last_msg_time.get(chat_id, current_time)
            elapsed = current_time - last_time
            
            # যদি ১৫ সেকেন্ড পার হয়ে যায়
            if elapsed >= DELAY_SECONDS:
                # মেসেজ পাঠাও
                await send_safe_message(chat_id, chat_name)
                
                # মেসেজ পাঠানোর পর লুপ ভেঙে বের হয়ে যাও (যাতে আর মেসেজ না দেয়)
                break
            
            # যদি ১৫ সেকেন্ড পার না হয়, বাকি সময়টুকু অপেক্ষা করো
            remaining = DELAY_SECONDS - elapsed
            # আমরা পুরো সময় স্লিপ করব না, ১ সেকেন্ড করে চেক করব (সেফটি)
            sleep_time = min(remaining, 1) 
            await asyncio.sleep(sleep_time)
            
    except Exception as e:
        logging.error(f"Task Error: {e}")
    finally:
        # কাজ শেষ, লিস্ট থেকে রিমুভ করে দাও
        if chat_id in active_monitors:
            active_monitors.remove(chat_id)

# --- ৬. ইভেন্ট হ্যান্ডলার ---
async def main():
    global clients
    clients = await init_clients()
    monitor_client = clients[0] # শুধুমাত্র ১ম জন মনিটর করবে

    print(f"\n🛡️ মনিটরিং চালু। নিজের আইডি ইগনোর করা হচ্ছে।")
    print(f"⏱️ লজিক: মেসেজ আসার পর {DELAY_SECONDS} সেকেন্ড অপেক্ষা, তারপর ১টি রিপ্লাই।")
    print("==================================================")

    @monitor_client.on(events.NewMessage(chats=target_groups, incoming=True))
    async def handler(event):
        chat_id = event.chat_id
        sender_id = event.sender_id
        
        # ১. যদি মেসেজটা আমাদের নিজেদের ৩টা আইডির কোনোটার হয় - একদম ইগনোর
        if sender_id in my_bot_ids:
            # logging.info("নিজেদের মেসেজ - ইগনোর করা হলো")
            return

        chat_name = getattr(event.chat, 'title', str(chat_id))
        
        # ২. শেষ মেসেজের সময় আপডেট করা
        last_msg_time[chat_id] = time.time()
        
        # ৩. যদি এই গ্রুপের জন্য অলরেডি কোনো 'ওয়েটার' (waiter) চালু না থাকে, তবে চালু করো
        if chat_id not in active_monitors:
            active_monitors.append(chat_id)
            asyncio.create_task(waiter_task(chat_id, chat_name))
            logging.info(f"⏳ '{chat_name}' - টাইমার শুরু (১৫ সেকেন্ড)...")
        else:
            # অলরেডি ওয়েটার আছে, সে শুধু টাইম আপডেট দেখবে, নতুন করে কিছু করার দরকার নেই
            # logging.info(f"🔄 '{chat_name}' - টাইমার রিসেট হলো (নতুন মেসেজ)")
            pass

    await monitor_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
