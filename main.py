import asyncio
import os
from telethon import TelegramClient, events, sessions
from telethon.errors.rpcerrorlist import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError
from telethon.tl.types import ChannelParticipantsAdmins

# --- Configuration ---
api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'
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
group_last_message_time = {}
WAIT_TIME = 15

client = TelegramClient(
    sessions.StringSession(session_string), 
    api_id, 
    api_hash,
    system_version="4.16.30-vxCUSTOM"
)

# --- নতুন মেসেজ হ্যান্ডলার ---
@client.on(events.NewMessage(chats=group_usernames))
async def handler(event):
    if event.message.sender_id == (await client.get_me()).id:
        return

    sender = await event.get_sender()
    
    # রিকোয়ারমেন্ট ১: অ্যাডমিন বা বট হলে ইগনোর করা
    if sender.bot or sender.admin_rights:
        return

    # রিকোয়ারমেন্ট ২: টাইমার রিসেট করা
    group_id = event.chat_id
    group_last_message_time[group_id] = asyncio.get_event_loop().time()

# --- ব্যাকগ্রাউন্ড পোস্টিং টাস্ক ---
async def poster_task(group_id, group_title):
    print(f"✅ Poster task started for: {group_title}")
    
    # টাস্ক শুরু হওয়ার সময়কে প্রথম মেসেজ টাইম ধরে নিচ্ছি
    group_last_message_time[group_id] = asyncio.get_event_loop().time()

    while True:
        try:
            await asyncio.sleep(1) # প্রতি ১ সেকেন্ড পর পর চেক করবে
            
            loop_time = asyncio.get_event_loop().time()
            last_msg_time = group_last_message_time.get(group_id, 0)
            
            time_since_last_message = loop_time - last_msg_time
            
            # যদি ১৫ সেকেন্ডের বেশি সময় কোনো মেসেজ না আসে
            if time_since_last_message > WAIT_TIME:
                
                # --- FIX: Immediately reset timer ---
                # এই লাইনটি একাধিক মেসেজ পাঠানো বন্ধ করবে।
                # মেসেজ পাঠানোর আগেই সময় রিসেট করা হয়।
                group_last_message_time[group_id] = loop_time
                # --- End Fix ---

                print(f"Posting in {group_title} after {time_since_last_message:.0f}s of inactivity...")
                try:
                    await client.send_message(
                        group_id,
                        message_to_send,
                        file=image_path,
                        parse_mode='md'
                    )
                    print(f"✅ Advertisement posted successfully in {group_title}")
                    
                except (UserBannedInChannelError, ChatWriteForbiddenError):
                    print(f"❌ Cannot post in {group_title}. Bot is banned or restricted. Stopping task for this group.")
                    break # এই গ্রুপের জন্য টাস্ক বন্ধ করে দাও
                except FloodWaitError as e:
                    print(f"Flood wait in {group_title}. Sleeping for {e.seconds}s.")
                    await asyncio.sleep(e.seconds)
                    # Flood wait এর পর আবার টাইমার রিসেট করা
                    group_last_message_time[group_id] = asyncio.get_event_loop().time()
                except Exception as e:
                    print(f"An error occurred while posting in {group_title}: {e}")
                    # কোনো এরর হলেও, টাইমার আগেই রিসেট হয়ে গেছে, তাই আবার ১৫ সেকেন্ড অপেক্ষা করবে।

        except Exception as e:
            print(f"Error in poster_task for {group_title}: {e}")
            await asyncio.sleep(10) # বড় কোনো সমস্যা হলে ১০ সেকেন্ড পর আবার চেষ্টা করবে


# --- Main Bot Function ---
async def main_bot_logic():
    print("Bot starting with Telethon String Session...")
    try:
        await client.start()
        print("SUCCESS: Client is connected.")
        
        print("Resolving group entities and starting poster tasks...")
        tasks = []
        for username in group_usernames:
            try:
                entity = await client.get_entity(username)
                group_id = entity.id
                group_title = entity.title
                
                task = asyncio.create_task(poster_task(group_id, group_title))
                tasks.append(task)
                
            except ValueError:
                print(f"CRITICAL ERROR: Username '{username}' not found or invalid. Skipping.")
            except Exception as e:
                print(f"Could not resolve {username}: {e}. Skipping.")

        print(f"Successfully started {len(tasks)} poster tasks.")
        
        await client.run_until_disconnected() 
        
    except Exception as e:
        print(f"Telethon client failed to start or crashed: {e}")
        if "string given is not valid" in str(e):
            print("CRITICAL ERROR: The STRING_SESSION is invalid or expired.")

# --- Start the bot ---
if __name__ == "__main__":
    if session_string:
        print("Starting Telethon client...")
        asyncio.run(main_bot_logic())
