import asyncio
import os
from telethon import TelegramClient, events, sessions
from telethon.errors.rpcerrorlist import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError

# --- Configuration ---
api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'
session_string = os.environ.get('STRING_SESSION') 

if not session_string:
    print("CRITICAL ERROR: TELETHON_SESSION_STRING environment variable not set.")
    exit()

# --- group_usernames লিস্ট থেকে 'thejournyofsc24' সরানো হয়েছে ---
group_usernames = [
    #'Acs_Udvash_Link', 
    # 'thejournyofsc24',  <-- এই ভুল নামটি ডিলিট করা হয়েছে
    #'hsc_sharing', 'ACSDISCUSSION',
    'hscacademicandadmissionchatgroup', 'HHEHRETW', 'chemistryteli', 'hsc234', 'buetkuetruetcuet', 'linkedstudies',
    #'studywar2021', 'DiscussionGroupEngineering', 'buetkuetruetcuet',
    #'superb1k', 'Dacs2025',
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
**❷** **[HSC27 PCMB All Course](https://t.me/HSCGeniusHubMZ/93)** 
**❸** **[All EBI Course](https://t.me/HSCGeniusHubMZ/94)**

**➟ তাহলে আর দেরি কেন? এখনই** **[HSC Genius Hub](https://t.me/HSCGeniusHubMZ)** **এর সাথে যুক্ত হও!!**

**⎙ কোর্স কিনতে নক করুন: ➤ @HSCGeniusHubBot**

**⁀➴ প্রধান চ্যানেল:** **[HSC Genius Hub](https://t.me/HSCGeniusHubMZ)**

**────୨ৎ────**
"""

client = TelegramClient(
    sessions.StringSession(session_string), 
    api_id, 
    api_hash
)

# --- Bot Handler ---
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
            #file=image_path,
            parse_mode='md'
        )
        print("Advertisement posted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Main Bot Function ---
async def main_bot_logic():
    print("Bot starting with Telethon String Session...")
    try:
        await client.start()
        print("SUCCESS: Client is connected and listening.")
        
        # এই লাইনটি বটকে ২৪/৭ চালু রাখে
        await client.run_until_disconnected() 
        
    except ValueError as e:
        # ভুল ইউজারনেমের জন্য নির্দিষ্ট এরর লগ
        print(f"CRITICAL ERROR: A username in your list is invalid: {e}")
    except Exception as e:
        print(f"Telethon client failed to start or crashed: {e}")
        if "string given is not valid" in str(e):
            print("CRITICAL ERROR: The TELETHON_SESSION_STRING is invalid or expired.")

# --- Start the bot ---
if __name__ == "__main__":
    if session_string:
        print("Starting Telethon client...")
        asyncio.run(main_bot_logic())
