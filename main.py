import asyncio
import os
from telethon import TelegramClient, events, sessions
from telethon.errors.rpcerrorlist import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError

# --- Configuration ---
api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'
session_string = os.environ.get('TELETHON_SESSION_STRING') 

if not session_string:
    print("CRITICAL ERROR: TELETHON_SESSION_STRING environment variable not set.")
    exit()

# --- group_usernames লিস্ট থেকে 'thejournyofsc24' সরানো হয়েছে ---
group_usernames = [
    #'Acs_Udvash_Link', 'buetkuetruetcuet', 'linkedstudies',
    # 'thejournyofsc24',  <-- এই ভুল নামটি ডিলিট করা হয়েছে
    #'hsc_sharing', 'ACSDISCUSSION',
    'HHEHRETW', 'chemistryteli', 'hsc234',
    #'studywar2021', 'DiscussionGroupEngineering', 'buetkuetruetcuet',
    #'superb1k', 'Dacs2025',
]
image_path = 'Replit.jpg'
message_to_send = """
Course Index (HSC27)

1. [Shikho Animated Lessons](https://t.me/HSCGeniusHubMZ/70) (200 Tk)

HSC-27 

Physics
 
ACS

1. [27 Physics Cycle 1](https://t.me/HSCGeniusHubMZ/21) (70 Tk)
2. 27 Physics Cycle 2 (70 Tk)
3. 27 Physics Cycle 3 (70 Tk)
4. 27 Physics Cycle 4 (70 Tk)
5. 27 Physics Cycle 5 (70 Tk)
6. 27 Physics Cycle 6 (70 Tk)
7. 27 RM Physics 1st Paper (150 Tk)

বন্দী পাঠশালা 

1. [27 BP Physics 1st Paper](https://t.me/HSCGeniusHubMZ/270) (130 Tk)

Chemistry

Himel Vai

1. [27 Chemistry Cycle 1](https://t.me/HSCGeniusHubMZ/27) (70 Tk)
2. 27 Chemistry Cycle 2 (70 Tk)
3. 27 Chemistry Cycle 3 (70 Tk)
4. 27 Chemistry Cycle 4 (70 Tk)
5. 27 Chemistry Cycle 5 (70 Tk)

Ridwan method 

6. [27 Hasan Enam Chemistry 1st Paper](https://t.me/HSCGeniusHubMZ/229) (100 Tk)

Aloron 

7. [27 Aloron Chemistry Cycle 1](https://t.me/HSCGeniusHubMZ/252) (90 Tk)
8. 27 Aloron Chemistry Cycle 2 (90 Tk)
9. 27 Aloron Chemistry Cycle 3 (90 Tk)
10. 27 Aloron Chemistry Cycle 4 (90 Tk)
11. 27 Aloron Chemistry Cycle 5 (90 Tk)
12. 27 Aloron Chemistry Combo (350 Tk)

Biology
 
Biomission 

1. 27 Biomission Cycle 1 (70 Tk)
2. 27 Biomission Cycle 2 (70 Tk)
3. 27 Biomission Cycle 3 (70 Tk)
4. 27 Biomission Cycle 4 (70 Tk)
5. 27 Biomission Cycle 5 (70 Tk)
6. 27 Biomission Cycle 6 (70 Tk)

BH Troops 

7. 27 BH Troops Cycle 1 (Free)
8. 27 BH Troops Cycle 2 (90 TK)
9. 27 BH Troops Cycle 3 (90 TK)
10. 27 BH Troops Cycle 4 (90 TK)
11. 27 BH Troops Cycle 5 (90 TK)
12. 27 BH Troops Cycle 6 (90 TK)
13. 27 BH Troops All Cycle (400 Tk)

DMC Dreamers 

14. 27 DMC Dreamers Cycle 1 (70 Tk)
15. 27 DMC Dreamers Cycle 2 (70 Tk)
16. 27 DMC Dreamers Cycle 3 (70 Tk)

Math

1. 27 Math Cycle 1 (Free)
2. 27 Math Cycle 2 (70 Tk)
3. 27 Math Cycle 3 (70 Tk)
4. 27 Math Cycle 4 (70 Tk)
5. 27 Math Cycle 5 (70 Tk)
6. 27 Math Cycle 6 (70 Tk)

ICT

1. ACS ICT DECODER 27 (70 TK)

English

1. 27 Galacticos English 1.0 (70 Tk)
2. 27 Galacticos English 2.0 (70 Tk)

Bangla
 
1. 27 অনুসর্গের ব্যঞ্জন (90 Tk)

HSC27 ব্যাচ ACS কম্ব অফার

👉যে কোন একটি বিষয় সম্পূর্ণ একত্রে - 280 টাকা
👉 PCMC+EBI সম্পূর্ণটা একত্রে - 900 টাকা


HSC-27 (Others)

1. 27 Biology Adda Cycle 1 (70 Tk) 
2. 27 BP Chemistry Cycle 1 (70 Tk)
3. 27 BP Chemistry Cycle 2 (70 Tk)

Others

1. EBI All Course 
2. HSC26 PCMB All Course 

📩 কোর্স কিনতে নক করুন: 👉 @HSCGeniusHubBot

📌 প্রধান চ্যানেল: HSC Genius Hub
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
