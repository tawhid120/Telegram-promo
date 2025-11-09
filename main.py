import asyncio
import os
from telethon import TelegramClient, events, sessions
from telethon.errors.rpcerrorlist import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError
from telethon.tl.types import ChannelParticipantsAdmins

# --- Configuration ---
api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb
session_string = os.environ.get('STRING_SESSION') 

if not session_string:
    print("CRITICAL ERROR: STRING_SESSION environment variable not set.")
    exit()

# --- group_usernames লিস্ট ---
group_usernames = [
    'hscacademicandadmissionchatgroup', 'HHEHRETW', 'chemistryteli', 'hsc234', 'buetkuetruetcuet', 'linkedstudies',
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

# --- Bot Logic ---
# প্রতিটি গ্রুপের জন্য pending task ট্র্যাক করার জন্য dictionary
pending_tasks = {}

# কত সেকেন্ড অপেক্ষা করতে হবে
WAIT_TIME = 15

client = TelegramClient(
    sessions.StringSession(session_string), 
    api_id, 
    api_hash,
    system_version="4.16.30-vxCUSTOM"
)

async def send_advertisement(chat_id, chat_title):
    """15 সেকেন্ড পর advertisement পাঠানোর function"""
    try:
        print(f"✅ 15s quiet. Sending advertisement to '{chat_title}'...")
        await client.send_message(
            chat_id,
            message_to_send,
            file=image_path,
            parse_mode='md'
        )
        print(f"✅ Advertisement posted successfully in '{chat_title}'.")
    except (UserBannedInChannelError, ChatWriteForbiddenError):
        print(f"❌ Cannot post in {chat_title}. Bot is banned or restricted.")
    except FloodWaitError as e:
        print(f"Flood wait in {chat_title}. Sleeping for {e.seconds}s.")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"Error posting advertisement in '{chat_title}': {e}")
    finally:
        # Task complete হওয়ার পর pending_tasks থেকে remove করা
        if chat_id in pending_tasks:
            del pending_tasks[chat_id]

# --- Bot Handler ---
@client.on(events.NewMessage(chats=group_usernames))
async def handler(event):
    # ১. নিজের মেসেজ ইগনোর করা
    if event.message.sender_id == (await client.get_me()).id:
        return

    # ২. অ্যাডমিন বা বট-এর মেসেজ ইগনোর করা (সবচেয়ে নির্ভরযোগ্য উপায়)
    try:
        sender = await event.get_sender()
        if sender.bot or sender.admin_rights:
            # print(f"Ignored admin/bot message in {event.chat.title}")
            return
    except Exception as e:
        # কোনো কারণে sender check করতে না পারলে (যেমন, banned user) ইগনোর করা
        # print(f"Could not check sender in {event.chat.title}: {e}")
        return
    
    # ৩. সাধারণ ইউজার মেসেজ দিলে টাইমার রিসেট/স্টার্ট করা
    chat_id = event.chat_id
    chat_title = event.chat.title
    
    # ৪. যদি এই গ্রুপের জন্য আগে থেকেই কোনো পোস্ট পেন্ডিং থাকে, সেটা বাতিল করা
    if chat_id in pending_tasks:
        pending_tasks[chat_id].cancel()
        # print(f"Timer reset for {chat_title}.")
    
    # ৫. ১৫ সেকেন্ড পর পোস্ট করার জন্য নতুন একটি টাস্ক তৈরি করা
    async def wait_and_send():
        try:
            await asyncio.sleep(WAIT_TIME)
            # ১৫ সেকেন্ড সফলভাবে অপেক্ষা শেষ হলে, মেসেজ পাঠানো
            await send_advertisement(chat_id, chat_title)
        except asyncio.CancelledError:
            # যদি এই টাস্কটি বাতিল করা হয় (অর্থাৎ নতুন মেসেজ আসে)
            # print(f"Posting to {chat_title} cancelled by new message.")
            pass # এখানে কিছু করার দরকার নেই

    # নতুন টাস্কটি pending_tasks-এ সেভ করা
    pending_tasks[chat_id] = asyncio.create_task(wait_and_send())
    # print(f"New 15s timer started for {chat_title}.")


# --- Main Bot Function ---
async def main_bot_logic():
    print("Bot starting with Telethon String Session...")
    try:
        await client.start()
        print("SUCCESS: Client is connected and listening.")
        print(f"Monitoring {len(group_usernames)} groups.")
        print(f"Will post after {WAIT_TIME} seconds of inactivity from non-admin users.")
        
        # এই লাইনটি বটকে ২৪/৭ চালু রাখে
        await client.run_until_disconnected() 
        
    except ValueError as e:
        print(f"CRITICAL ERROR: A username in your list is invalid: {e}")
    except Exception as e:
        print(f"Telethon client failed to start or crashed: {e}")
        if "string given is not valid" in str(e):
            print("CRITICAL ERROR: The STRING_SESSION is invalid or expired.")

# --- Start the bot ---
if __name__ == "__main__":
    if session_string:
        print("Starting Telethon client...")
        asyncio.run(main_bot_logic())
