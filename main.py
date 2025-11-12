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

# --- ১. লগিং এবং কনফিগারেশন ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'

# সেশন স্ট্রিং (আপনার এনভায়রনমেন্ট বা সরাসরি স্ট্রিং)
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
"""

# --- ২. গ্লোবাল ভেরিয়েবল ---
clients = []           
sender_cycle = None    
debounce_tasks = {}    
my_bot_ids = []        # আমাদের নিজেদের অ্যাকাউন্টের আইডি লিস্ট
WAIT_TIME = 15         

# --- ৩. হেল্পার ফাংশন: সব অ্যাকাউন্ট চালু করা ---
async def init_clients():
    global sender_cycle, my_bot_ids
    active_clients = []
    my_bot_ids = [] # আইডি লিস্ট রিসেট
    
    print("🔄 অ্যাকাউন্টগুলো কানেক্ট করা হচ্ছে এবং আইডি চেক করা হচ্ছে...")
    
    for i, s_str in enumerate(session_strings):
        if not s_str: continue
        try:
            client = TelegramClient(
                sessions.StringSession(s_str), 
                api_id, api_hash,
                device_model=f"HSC Bot {i+1}",
                app_version="3.5 Fix"
            )
            await client.start()
            me = await client.get_me()
            
            # আইপি লিস্টে নিজের আইডি যোগ করা
            my_bot_ids.append(me.id)
            active_clients.append(client)
            
            print(f"✅ অ্যাকাউন্ট {i+1} রেডি: {me.first_name} (ID: {me.id})")
            
        except Exception as e:
            print(f"❌ অ্যাকাউন্ট {i+1} এরর: {e}")

    if not active_clients:
        print("⛔ কোনো অ্যাকাউন্ট কানেক্ট করা যায়নি।")
        exit()
        
    sender_cycle = cycle(active_clients)
    print(f"🛡️ ইগনোর লিস্ট তৈরি সম্পন্ন: {my_bot_ids}")
    return active_clients

# --- ৪. স্মার্ট সেন্ডিং ফাংশন ---
async def send_smart_message(chat_id, chat_name):
    global sender_cycle
    
    file_to_send = image_path if os.path.exists(image_path) else None
    attempts = len(clients)
    sent_success = False
    
    logging.info(f"🚀 '{chat_name}' - মেসেজ পাঠানোর প্রসেস শুরু...")

    for _ in range(attempts):
        current_client = next(sender_cycle)
        me = await current_client.get_me()
        
        try:
            await current_client.send_message(
                chat_id,
                message_text,
                file=file_to_send,
                link_preview=False
            )
            logging.info(f"✅ সফল! '{me.first_name}' মেসেজ পাঠিয়েছে।")
            sent_success = True
            break 
            
        except (UserNotParticipantError, ChannelPrivateError):
            logging.warning(f"⚠️ '{me.first_name}' গ্রুপে নেই। স্কিপ...")
        except (ChatWriteForbiddenError, UserBannedInChannelError):
            logging.warning(f"🚫 '{me.first_name}' ব্যানড। স্কিপ...")
        except FloodWaitError as e:
            logging.warning(f"⏳ '{me.first_name}' ফ্লাড ওয়েট ({e.seconds}s)। স্কিপ...")
        except Exception as e:
            logging.error(f"❌ সমস্যা ({me.first_name}): {e}")

    if not sent_success:
        logging.error(f"⛔ সব অ্যাকাউন্ট ব্যর্থ হয়েছে '{chat_name}' এ।")

# --- ৫. টাইমার এবং ফিল্টার হ্যান্ডলার ---
async def debounce_handler(event):
    # ১. নিজের আইডি চেক (সবচেয়ে গুরুত্বপূর্ণ অংশ)
    sender_id = event.sender_id
    
    # যদি মেসেজ পাঠানো ব্যক্তি আমাদের নিজেদের ৩টা অ্যাকাউন্টের একটা হয়, তবে থামো
    if sender_id in my_bot_ids:
        return # চুপচাপ বের হয়ে যাও, কোনো লগ বা রিপ্লাই দরকার নেই

    chat_id = event.chat_id
    chat_name = getattr(event.chat, 'title', str(chat_id))
    
    # ২. আগের টাইমার বাতিল করা (রিস্টার্ট লজিক)
    if chat_id in debounce_tasks:
        task = debounce_tasks[chat_id]
        if not task.done():
            task.cancel() 

    # ৩. নতুন টাইমার শুরু
    debounce_tasks[chat_id] = asyncio.create_task(process_delayed_message(chat_id, chat_name))

async def process_delayed_message(chat_id, chat_name):
    try:
        # ১৫ সেকেন্ড অপেক্ষা
        await asyncio.sleep(WAIT_TIME)
        
        # সময় শেষ, এখন মেসেজ পাঠাও
        await send_smart_message(chat_id, chat_name)
        
        if chat_id in debounce_tasks:
            del debounce_tasks[chat_id]
            
    except asyncio.CancelledError:
        # নতুন মেসেজ এসেছে, তাই এই টাস্ক বাতিল
        pass

# --- ৬. মেইন ফাংশন ---
async def main():
    global clients
    
    clients = await init_clients()
    
    # মনিটরিংয়ের জন্য শুধুমাত্র ১ম ক্লায়েন্ট ব্যবহার
    monitor_client = clients[0] 
    me = await monitor_client.get_me()
    
    print(f"\n👁️ মনিটরিং করছে: {me.first_name}")
    print(f"🚫 নিজেদের আইডি ফিল্টার চালু আছে।")
    print("--------------------------------------------------")

    @monitor_client.on(events.NewMessage(chats=target_groups, incoming=True))
    async def handler(event):
        await debounce_handler(event)

    await monitor_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
