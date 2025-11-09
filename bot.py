import asyncio
import os
from telethon import TelegramClient, events, sessions
from telethon.errors.rpcerrorlist import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError

# --- Configuration (All unchanged) ---
api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'
session_string = os.environ.get('TELETHON_SESSION_STRING')

group_usernames = [
    'Acs_Udvash_Link', 'buetkuetruetcuet', 'linkedstudies',
    'thejournyofsc24', 'hsc_sharing', 'ACSDISCUSSION',
    'HHEHRETW', 'chemistryteli', 'haters_hsc', 'hsc234',
    'studywar2021', 'DiscussionGroupEngineering', 'buetkuetruetcuet',
    'superb1k', 'Dacs2025',
]
image_path = 'Replit.jpg'
message_to_send = """
🤫 **ছাত্রজীবনের কয়েকটি গোপন চ্যানেল!**

👉 **All platforms class, note, guide PDF:** @PDFNexus
👉 **Free time এর মধ্যে earning tips**: @EarnovaX
👉 **HSC Guideline & problem helping groups**: @guildline01

🔴 Earn **14 Taka** selling per **Gmail**: [https://t.me/GmailFarmerBot?start=7647683104](https://t.me/GmailFarmerBot?start=7647683104)

🗣️ Spoken English Zone 🇬🇧
Spoken English, Vocabulary, Grammar ও IELTS শেখো সহজভাবে বাংলাসহ।
👉 ইংরেজি শেখার পারফেক্ট চ্যানেল!
Join Now: ⬇️
 [https://t.me/Spoken_English_Zone](https://t.me/Spoken_English_Zone)
"""

client = TelegramClient(
    sessions.StringSession(session_string), 
    api_id, 
    api_hash
)

# --- Bot Handlers (Unchanged) ---
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
            file=image_path,
            parse_mode='md'
        )
        print("Advertisement posted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Async Main Function ---
async def main_bot_logic():
    """ এটি হলো মূল async ফাংশন যা বটটি চালায় """
    if not session_string:
        print("CRITICAL ERROR in bot.py: TELETHON_SESSION_STRING not set.")
        return
        
    print("Bot starting with Telethon String Session...")
    try:
        await client.start()
        print("SUCCESS: Client is connected and listening.")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Telethon client failed to start or crashed: {e}")
        # আপনি এখানে লগইন ব্যর্থতার জন্য নির্দিষ্ট এরর যোগ করতে পারেন
        # যেমন, সেশন স্ট্রিং ভুল হলে:
        if "string given is not valid" in str(e):
            print("CRITICAL ERROR: The TELETHON_SESSION_STRING is invalid or expired.")

# --- Sync Starter Function (NEW) ---
def run_bot():
    """
    এই sync ফাংশনটি app.py দ্বারা কল হবে।
    এটি নিজেই একটি নতুন asyncio ইভেন্ট লুপ তৈরি এবং চালাবে।
    """
    print("asyncio.run() is called from bot.py")
    asyncio.run(main_bot_logic())
