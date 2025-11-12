import asyncio
import logging
import os
import time
import random
from collections import deque
from telethon import TelegramClient, events, sessions
from telethon.tl.types import User
from telethon.errors import (
    FloodWaitError, 
    UserBannedInChannelError, 
    ChatWriteForbiddenError, 
    ChannelPrivateError,
    ChatAdminRequiredError,
    AuthKeyDuplicatedError,
    UserNotParticipantError
)

# --- ১. অ্যাডভান্সড লগিং সেটআপ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("HSC_Genius_Bot")

# --- ২. কনফিগারেশন ---
API_ID = 20193909
API_HASH = '82cd035fc1eb439bda68b2bfc75a57cb'

# সেশন স্ট্রিং (অবশ্যই নতুন জেনারেট করা সেশন ব্যবহার করবেন)
SESSION_STRINGS = [
    os.environ.get('SESSION_1'),
    os.environ.get('SESSION_2'),
    os.environ.get('SESSION_3')
]

# টার্গেট গ্রুপ
TARGET_GROUPS = [
    'chemistryteli', 'hsc_sharing', 'linkedstudies', 'hsc234', 'buetkuetruetcuet',
    'thejournyofhsc24', 'haters_hsc', 'Dacs2025', 'superb1k', 'studywar2021',
    'hscacademicandadmissionchatgroup', 'Acs_Udvash_Link', 'DiscussionGroupEngineering', 'HHEHRETW'
]

IMAGE_PATH = 'Replit1.jpg'

MESSAGE_CONTENT = """
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

# কনস্ট্যান্টস
DEBOUNCE_SECONDS = 15  # ১৫ সেকেন্ড অপেক্ষা
RETRY_DELAY = 5        # ফেইল হলে ৫ সেকেন্ড পর আবার চেষ্টা

# --- ৩. গ্রুপ ম্যানেজার ক্লাস (প্রতিটি গ্রুপের জন্য আলাদা ব্রেইন) ---
class GroupManager:
    def __init__(self, chat_id, chat_name, bot_manager):
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.bot_manager = bot_manager
        self.last_message_time = 0
        self.is_timer_running = False
        self.lock = asyncio.Lock() # রেস কন্ডিশন আটকাতে লক

    async def incoming_message(self):
        """নতুন মেসেজ আসলে এই ফাংশন কল হবে"""
        self.last_message_time = time.time()
        
        # যদি অলরেডি টাইমার না চলে, তবে নতুন টাইমার চালু করো
        if not self.is_timer_running:
            asyncio.create_task(self.start_timer())
        else:
            # টাইমার অলরেডি চলছে, শুধু সময় আপডেট হয়েছে (অটোমেটিক)
            # logger.info(f"⏳ '{self.chat_name}' - টাইমার রিসেট হয়েছে (নতুন মেসেজ)")
            pass

    async def start_timer(self):
        """স্মার্ট টাইমার লজিক"""
        async with self.lock: # এক সাথে দুইটা টাইমার যেন না চলে
            self.is_timer_running = True
            logger.info(f"🕒 '{self.chat_name}' - টাইমার শুরু (১৫ সেকেন্ড)...")
            
            try:
                while True:
                    # বর্তমান সময় এবং শেষ মেসেজের পার্থক্য
                    current_time = time.time()
                    elapsed = current_time - self.last_message_time
                    
                    if elapsed >= DEBOUNCE_SECONDS:
                        # সময় শেষ! এখন মেসেজ পাঠাতে হবে
                        logger.info(f"✨ '{self.chat_name}' - নীরবতা শনাক্ত হয়েছে। মেসেজ পাঠানো হচ্ছে...")
                        await self.bot_manager.broadcast_message(self.chat_id, self.chat_name)
                        break # কাজ শেষ, লুপ ভাঙো
                    
                    # এখনো সময় হয়নি, বাকি সময়টুকু অপেক্ষা করো (কিন্তু সর্বোচ্চ ১ সেকেন্ড স্লিপ)
                    # ১ সেকেন্ড স্লিপ দেয়ার কারণ হলো যাতে লুপটি দ্রুত রেসপন্স করতে পারে
                    await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Error in timer for {self.chat_name}: {e}")
            finally:
                self.is_timer_running = False


# --- ৪. বট ম্যানেজার ক্লাস (সমস্ত অ্যাকাউন্টের বস) ---
class BotSwarm:
    def __init__(self):
        self.clients = []
        self.my_ids = []
        self.managers = {} # {chat_id: GroupManager_Object}
        self.client_queue = deque() # রাউন্ড রবিন কিউ

    async def initialize(self):
        """সব ক্লায়েন্ট কানেক্ট করা এবং আইডি সংগ্রহ করা"""
        print("\n🛠️  সিস্টেম ইনিশিয়ালাইজ হচ্ছে...")
        
        active_count = 0
        for i, s_str in enumerate(SESSION_STRINGS):
            if not s_str: continue
            
            try:
                client = TelegramClient(
                    sessions.StringSession(s_str),
                    API_ID, API_HASH,
                    device_model=f"GeniusBot V4 Pro-{i}",
                    app_version="4.0.1"
                )
                await client.start()
                me = await client.get_me()
                
                self.clients.append(client)
                self.my_ids.append(me.id)
                self.client_queue.append(client) # কিউতে যোগ করা
                
                print(f"🟢 অ্যাকাউন্ট {i+1} রেডি: {me.first_name} | ID: {me.id}")
                active_count += 1
                
            except AuthKeyDuplicatedError:
                print(f"🔴 অ্যাকাউন্ট {i+1} বাদ: সেশন নষ্ট (AuthKeyDuplicated)।")
            except Exception as e:
                print(f"🔴 অ্যাকাউন্ট {i+1} এরর: {e}")

        if not active_count:
            print("❌ কোনো অ্যাকাউন্ট কানেক্ট করা যায়নি। প্রোগ্রাম বন্ধ হচ্ছে।")
            exit(1)
            
        print(f"🛡️  মোট {active_count} টি অ্যাকাউন্ট এবং {len(TARGET_GROUPS)} টি গ্রুপ মনিটর করা হবে।")
        print("====================================================\n")

    def get_next_client(self):
        """পরের এভেইলেবল ক্লায়েন্ট দেয় (Round Robin)"""
        if not self.client_queue:
            return None
        # প্রথম জনকে নাও, এবং তাকে আবার লাইনের শেষে পাঠিয়ে দাও
        client = self.client_queue.popleft()
        self.client_queue.append(client)
        return client

    async def broadcast_message(self, chat_id, chat_name):
        """নির্ভরযোগ্যভাবে মেসেজ পাঠানোর ফাংশন (Failover সহ)"""
        
        file_path = IMAGE_PATH if os.path.exists(IMAGE_PATH) else None
        attempts = len(self.clients) # যতগুলো অ্যাকাউন্ট ততবার চেষ্টা
        
        # হিউম্যান ফিল: পাঠানোর আগে ২ সেকেন্ড অপেক্ষা
        await asyncio.sleep(2) 

        for _ in range(attempts):
            client = self.get_next_client()
            if not client: break
            
            try:
                # পাঠানোর চেষ্টা
                await client.send_message(
                    chat_id,
                    MESSAGE_CONTENT,
                    file=file_path,
                    link_preview=False
                )
                
                # সফল হলে
                me = await client.get_me()
                logger.info(f"✅ সফল! '{me.first_name}' মেসেজ পাঠিয়েছে -> '{chat_name}'")
                return # কাজ শেষ, রিটার্ন করো

            except (ChatWriteForbiddenError, UserBannedInChannelError):
                # logger.warning(f"⚠️ ব্যানড: এই অ্যাকাউন্ট '{chat_name}' এ মেসেজ দিতে পারবে না। পরের জন...")
                continue
            except (UserNotParticipantError, ChannelPrivateError):
                # logger.warning(f"⚠️ মেম্বার না: এই অ্যাকাউন্ট গ্রুপে নেই। পরের জন...")
                continue
            except FloodWaitError as e:
                logger.warning(f"⏳ ফ্লাড ওয়েট: {e.seconds} সেকেন্ড। পরের জন...")
                continue
            except AuthKeyDuplicatedError:
                logger.critical(f"💀 সেশন নষ্ট! এই অ্যাকাউন্ট লিস্ট থেকে বাদ দেয়া হচ্ছে।")
                if client in self.clients: self.clients.remove(client)
                if client in self.client_queue: self.client_queue.remove(client)
                continue
            except Exception as e:
                logger.error(f"❌ অজানা সমস্যা: {e}")
                continue

        logger.error(f"⛔ সব চেষ্টা ব্যর্থ! '{chat_name}' গ্রুপে মেসেজ যায়নি।")

# --- ৫. মেইন ফাংশন ---

async def main():
    # ১. বট সিস্টেম তৈরি
    bot_swarm = BotSwarm()
    await bot_swarm.initialize()

    # ২. মনিটর তৈরি (শুধুমাত্র ১ম ক্লায়েন্ট দিয়ে মনিটর, লোড কমানোর জন্য)
    monitor_client = bot_swarm.clients[0]
    
    # ৩. ইভেন্ট হ্যান্ডলার
    @monitor_client.on(events.NewMessage(chats=TARGET_GROUPS, incoming=True))
    async def message_handler(event):
        chat_id = event.chat_id
        sender = await event.get_sender()
        sender_id = event.sender_id

        # --- কড়া ফিল্টারিং ---
        
        # ক. নিজের অ্যাকাউন্ট হলে ইগনোর
        if sender_id in bot_swarm.my_ids:
            return
            
        # খ. অন্য বট হলে ইগনোর
        if isinstance(sender, User) and sender.bot:
            return

        # গ. সার্ভিস মেসেজ (যেমন: কেউ জয়েন করেছে) হলে ইগনোর
        if event.is_group and (event.action or not event.text):
             return

        # --- প্রসেসিং ---
        
        chat_name = getattr(event.chat, 'title', str(chat_id))
        
        # এই গ্রুপের জন্য কি ম্যানেজার আছে? না থাকলে বানাও
        if chat_id not in bot_swarm.managers:
            bot_swarm.managers[chat_id] = GroupManager(chat_id, chat_name, bot_swarm)
        
        # ম্যানেজারকে জানাও যে নতুন মেসেজ এসেছে
        await bot_swarm.managers[chat_id].incoming_message()

    print("🚀 সিস্টেম সম্পূর্ণ চালু। মনিটরিং চলছে...")
    await monitor_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 প্রোগ্রাম বন্ধ করা হয়েছে।")
    except Exception as e:
        print(f"❌ ক্রিটিক্যাল এরর: {e}")
