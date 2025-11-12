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
from datetime import datetime

# --- ১. লগিং সেটআপ ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logging.getLogger('telethon').setLevel(logging.WARNING)

# --- ২. কনফিগারেশন ---
api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'

# সেশন ভেরিয়েবল লোড করা
session_strings = [
    os.environ.get('SESSION_1'),
    os.environ.get('SESSION_2'),
    os.environ.get('SESSION_3')
]

group_usernames = [
    'chemistryteli', 'hsc_sharing', 'linkedstudies', 'hsc234', 'buetkuetruetcuet',
    'thejournyofhsc24', 'haters_hsc', 'Dacs2025', 'superb1k', 'studywar2021',
    'hscacademicandadmissionchatgroup', 'Acs_Udvash_Link', 'DiscussionGroupEngineering', 'HHEHRETW'
]

image_path = 'Replit1.jpg'

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

# --- ৩. গ্লোবাল ভেরিয়েবল ---
active_clients = []
sender_cycle = None
DEBOUNCE_DELAY = 15  # ১৫ সেকেন্ড ডিলে

# প্রতিটি গ্রুপের জন্য আলাদা ডেবাউন্স ডাটা রাখার ডিকশনারি
# Structure: {chat_id: {'task': asyncio.Task, 'count': int, 'last_time': datetime}}
chat_debounce = {}

# --- ৪. হেল্পার ফাংশন ---

async def start_all_clients():
    """সব অ্যাকাউন্ট কানেক্ট করা এবং রেডি করা"""
    global sender_cycle, active_clients
    active_clients = []
    
    logging.info("🔄 অ্যাকাউন্ট ইনিশিয়ালাইজ করা হচ্ছে...")
    
    if not os.path.exists(image_path):
        logging.warning(f"⚠️ ছবি '{image_path}' পাওয়া যায়নি। শুধু টেক্সট পাঠানো হবে।")

    for i, s_str in enumerate(session_strings, 1):
        if not s_str:
            logging.warning(f"⚠️ SESSION_{i} এনভায়রনমেন্ট ভেরিয়েবলে নেই। বাদ দেওয়া হলো।")
            continue
            
        try:
            # ডিভাইস মডেল আলাদা দিলে টেলিগ্রাম সাসপিশাস অ্যাক্টিভিটি কম ধরে
            client = TelegramClient(
                sessions.StringSession(s_str), 
                api_id, 
                api_hash,
                device_model=f"HSC Bot {i}",
                app_version="2.0"
            )
            await client.start()
            
            me = await client.get_me()
            logging.info(f"✅ অ্যাকাউন্ট {i} কানেক্টেড: {me.first_name} (@{me.username or 'N/A'})")
            active_clients.append(client)
        except Exception as e:
            logging.error(f"❌ অ্যাকাউন্ট {i} সংযোগ ব্যর্থ: {e}")

    if not active_clients:
        logging.critical("⛔️ কোনো অ্যাকাউন্ট কানেক্ট করা যায়নি। কোড বন্ধ করা হচ্ছে।")
        exit(1)

    # সাইক্লিং ইটারেটর তৈরি (1 -> 2 -> 3 -> 1...)
    sender_cycle = cycle(active_clients)
    logging.info(f"🚀 মোট {len(active_clients)} টি অ্যাকাউন্ট প্রস্তুত। রোটেশন শুরু হবে।\n")
    return active_clients

async def send_promotional_message(chat_id, chat_title, msg_count):
    """
    প্রমোশনাল মেসেজ পাঠানো - ফেইলওভার সাপোর্ট সহ
    যদি একটি অ্যাকাউন্ট ব্যর্থ হয়, পরেরটি চেষ্টা করবে।
    """
    global sender_cycle
    
    logging.info(f"📤 '{chat_title}'-এ মেসেজ পাঠানোর চেষ্টা চলছে (গত ১৫ সেকেন্ডে {msg_count}টি মেসেজ এসেছিল)")
    
    max_attempts = len(active_clients)
    file_to_send = image_path if os.path.exists(image_path) else None
    
    for attempt in range(1, max_attempts + 1):
        # সাইকেল থেকে পরের অ্যাকাউন্ট নেওয়া
        current_client = next(sender_cycle)
        me = await current_client.get_me()

        try:
            await current_client.send_message(
                chat_id, 
                message_to_send, 
                file=file_to_send, 
                parse_mode='md', 
                link_preview=False
            )
            
            logging.info(f"  ✅ সফল: '{me.first_name}' মেসেজ পাঠিয়েছে '{chat_title}' গ্রুপে।")
            
            # সফল হলে সেফটির জন্য একটু বিরতি দিয়ে রিটার্ন করুন
            await asyncio.sleep(random.uniform(3, 6))
            return True

        except (ValueError, ChannelPrivateError):
            logging.warning(f"  ⚠️ '{me.first_name}' গ্রুপে নেই বা অ্যাক্সেস নেই। পরের অ্যাকাউন্ট চেষ্টা করা হচ্ছে...")
        except (ChatWriteForbiddenError, UserBannedInChannelError, ChatAdminRequiredError):
            logging.warning(f"  🚫 '{me.first_name}' এই গ্রুপে নিষিদ্ধ বা পারমিশন নেই।")
        except FloodWaitError as e:
            logging.warning(f"  ⏳ '{me.first_name}' FloodWait খেয়েছে ({e.seconds}s)। পরের অ্যাকাউন্ট...")
        except Exception as e:
            logging.error(f"  ❌ অজানা সমস্যা '{me.first_name}' এর সাথে: {str(e)[:100]}")

    logging.error(f"⛔️ ব্যর্থ: সব {max_attempts}টি অ্যাকাউন্ট চেষ্টা করেও '{chat_title}' এ মেসেজ পাঠাতে পারেনি।")
    return False

# --- ৫. ডেবাউন্স টাইমার সিস্টেম ---

async def debounce_timer(chat_id, chat_title):
    """
    ১৫ সেকেন্ড অপেক্ষা করবে। এই সময়ের মধ্যে টাস্কটি ক্যানসেল না হলে মেসেজ পাঠাবে।
    """
    try:
        await asyncio.sleep(DEBOUNCE_DELAY)
        
        # টাইমার শেষ হওয়ার পর কোড এখানে আসবে
        data = chat_debounce.get(chat_id)
        if data:
            msg_count = data['count']
            await send_promotional_message(chat_id, chat_title, msg_count)
            
            # কাজ শেষ, মেমোরি ক্লিন করা
            if chat_id in chat_debounce:
                del chat_debounce[chat_id]
                logging.info(f"🧹 '{chat_title}' এর টাইমার ডাটা ক্লিয়ার করা হয়েছে।\n")
                
    except asyncio.CancelledError:
        # যদি ১৫ সেকেন্ডের আগে নতুন মেসেজ আসে, এই টাস্ক ক্যানসেল হবে
        # তখন এখানে আসবে এবং কিছু না করেই শেষ হবে (রিসেট ইফেক্ট)
        pass

# --- ৬. মেসেজ ইভেন্ট হ্যান্ডলার ---

async def message_handler(event):
    """
    নতুন মেসেজ আসলে এই ফাংশন কল হবে।
    এটি পুরনো টাইমার বাতিল করে নতুন টাইমার সেট করে।
    """
    sender = await event.get_sender()
    
    # ১. বট বা নিজের পাঠানো মেসেজ ইগনোর করা
    if not sender or (isinstance(sender, User) and sender.bot):
        return

    chat_id = event.chat.id
    chat_title = getattr(event.chat, 'title', 'Unknown Group')
    current_time = datetime.now()

    # যদি এই চ্যাটের জন্য আগে থেকেই টাইমার (টাস্ক) থাকে
    if chat_id in chat_debounce:
        # পুরনো টাস্ক বাতিল করো (রিসেট)
        old_task = chat_debounce[chat_id]['task']
        if old_task and not old_task.done():
            old_task.cancel()
            
        # মেসেজ কাউন্ট বাড়াও
        chat_debounce[chat_id]['count'] += 1
        chat_debounce[chat_id]['last_time'] = current_time
        
        count = chat_debounce[chat_id]['count']
        logging.info(f"🔄 '{chat_title}': নতুন মেসেজ (#{count}) - টাইমার রিসেট করা হলো (১৫সে অপেক্ষা শুরু)")
    
    else:
        # এই সেশনে এই গ্রুপ থেকে প্রথম মেসেজ
        chat_debounce[chat_id] = {
            'count': 1,
            'last_time': current_time,
            'task': None
        }
        logging.info(f"🆕 '{chat_title}': প্রথম মেসেজ ডিটেক্টেড - টাইমার স্টার্ট (১৫সে)")

    # নতুন টাইমার টাস্ক শুরু করো এবং ডিকশনারিতে সেভ রাখো
    new_task = asyncio.create_task(debounce_timer(chat_id, chat_title))
    chat_debounce[chat_id]['task'] = new_task

# --- ৭. মেইন ফাংশন ---

async def main():
    print("\n" + "="*60)
    print(" 🎓 HSC Genius Hub - স্মার্ট অ্যান্টি-স্প্যাম বট")
    print("="*60 + "\n")

    # ১. সব ক্লায়েন্ট কানেক্ট করা
    clients = await start_all_clients()
    
    # ২. মনিটরিং সেটআপ
    # সতর্কতা: শুধু ১ম অ্যাকাউন্ট মনিটর করবে যাতে ডুপ্লিকেট ইভেন্ট না হয়।
    # নিশ্চিত করুন 'SESSION_1' এর অ্যাকাউন্টটি সব টার্গেট গ্রুপে অ্যাড আছে।
    monitor_client = clients[0]
    monitor_me = await monitor_client.get_me()
    
    logging.info(f"👁️ মনিটরিং করছে: {monitor_me.first_name}")
    logging.info(f"⏱️ ডেবাউন্স ডিলে: {DEBOUNCE_DELAY} সেকেন্ড")
    
    # ৩. ইভেন্ট হ্যান্ডলার যুক্ত করা
    monitor_client.add_event_handler(
        message_handler,
        events.NewMessage(chats=group_usernames, incoming=True)
    )
    
    logging.info("✅ বট সফলভাবে চালু হয়েছে। বন্ধ করতে Ctrl+C চাপুন।\n")
    
    # ৪. আজীবন চালানোর লুপ
    await monitor_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\n🛑 ব্যবহারকারী দ্বারা বট বন্ধ করা হয়েছে।")
    except Exception as e:
        logging.critical(f"\n❌ ক্রিটিকাল এরর: {e}", exc_info=True)


