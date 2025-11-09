# m5_final_simplified_v1.py

import asyncio
import logging
import os  # <-- os ইমপোর্ট করা হয়েছে
from telethon import TelegramClient, events, sessions  # <-- sessions ইমপোর্ট করা হয়েছে
from telethon.tl.types import User
from telethon.errors.rpcerrorlist import (
    FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError
)

# --- Standard Logging Setup (কালারফুল লগ সরানো হয়েছে) ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logging.getLogger('telethon').setLevel(logging.WARNING)

# --- অ্যাকাউন্ট ক্রেডেনশিয়াল (String Session) ---
STRING_SESSION = os.environ.get('STRING_SESSION')
if not STRING_SESSION:
    logging.critical("CRITICAL: 'STRING_SESSION' Replit Secrets এ সেট করা নেই।")
    exit()

api_id = 20193909
api_hash = '82cd035fc1eb439bda68b2bfc75a57cb'

# --- Groups to Monitor ---
group_usernames = [
    'chemistryteli', 'hsc_sharing', 'linkedstudies', 'hsc234', 'buetkuetruetcuet',
    'thejournyofhsc24', 'haters_hsc', 'Dacs2025', 'superb1k', 'studywar2021',
    'hscacademicandadmissionchatgroup', 'Acs_Udvash_Link', 'DiscussionGroupEngineering', 'HHEHRETW'
]

# --- Image and Message Details (Updated) ---
image_path = 'Replit1.jpg' # <-- আপনার অন্য কোড অনুযায়ী নামটি Replit1.jpg করা হয়েছে
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

# --- Client and other variables (একটি ক্লায়েন্টে সিম্পল করা) ---
client = TelegramClient(sessions.StringSession(STRING_SESSION), api_id, api_hash)
own_ids = set()
debounce_tasks = {}
DEBOUNCE_DELAY = 15 # আপনার ১৫ সেকেন্ড ডিলে

async def find_and_verify_groups(client_to_check, target_usernames):
    """Iterates through the client's dialogs to find groups."""
    logging.info("\n--- Finding and Verifying Target Groups ---")
    accessible_entities = {}
    target_set = set(u.lower() for u in target_usernames)

    logging.info("Searching for groups in the account's chat list...")
    try:
        async for dialog in client_to_check.iter_dialogs():
            if hasattr(dialog.entity, 'username') and dialog.entity.username:
                username_lower = dialog.entity.username.lower()
                if username_lower in target_set and username_lower not in accessible_entities:
                    accessible_entities[username_lower] = dialog.entity
    except Exception as e:
        logging.error(f"Could not fetch dialogs: {e}")

    logging.info("\n--- Verification Report ---")
    found_usernames = set(accessible_entities.keys())
    
    for username in target_set:
        if username in found_usernames:
            logging.info(f"✅ SUCCESS: Found group '@{username}'")
        else:
            logging.error(f"❌ FAILED: Could not find '@{username}'. Ensure the account has joined this group.")
            
    return list(accessible_entities.values())

async def send_promotional_message(chat_id, chat_title):
    """Sends the message using the single client."""
    logging.info(f"Silence period ended for '{chat_title}'. Preparing to send promotional message...")
    message_sent = False

    try:
        logging.info(f"  -> Attempting to send message...")
        await client.send_message(
            chat_id, 
            message_to_send, 
            file=image_path, 
            parse_mode='md', 
            link_preview=False
        )
        logging.info(f"  ✅ SUCCESS: Message sent to '{chat_title}'.")
        message_sent = True
    except (ChatWriteForbiddenError, UserBannedInChannelError):
        logging.warning(f"  ⚠️ WARNING: Account is banned or can't post in '{chat_title}'.")
    except FloodWaitError as e:
        logging.warning(f"  ⏳ FLOOD WAIT: Must wait for {e.seconds}s.")
        await asyncio.sleep(e.seconds)
        # Flood wait এর পর আবার চেষ্টা করা হবে না, পরবর্তী মেসেজের জন্য অপেক্ষা করবে
    except FileNotFoundError:
        logging.error(f"  ❌ FATAL: Image file not found at '{image_path}'.")
    except Exception as e:
        logging.error(f"  ❌ UNEXPECTED ERROR in '{chat_title}': {e}")

    if not message_sent:
        logging.critical(f"⛔️ FINAL FAILURE: Failed to send message to '{chat_title}'.")
    
    if chat_id in debounce_tasks:
        del debounce_tasks[chat_id]

async def message_handler(event):
    """Handles new messages and resets the debounce timer."""
    sender = await event.get_sender()
    if not isinstance(sender, User) or sender.bot or sender.id in own_ids:
        if sender and hasattr(sender, 'bot') and sender.bot:
            logging.debug(f"Ignoring a message from bot in '{event.chat.title}'.")
        return
    
    logging.info(f"\n–––––––––––––––––––––––\n📲 NEW MESSAGE in '{event.chat.title}' from '{sender.first_name}'")
    
    chat_id = event.chat.id
    if chat_id in debounce_tasks:
        debounce_tasks[chat_id].cancel()
        
    async def schedule_send():
        try:
            logging.info(f"⏳ Scheduling response for '{event.chat.title}' in {DEBOUNCE_DELAY} seconds.")
            await asyncio.sleep(DEBOUNCE_DELAY)
            await send_promotional_message(chat_id, event.chat.title)
        except asyncio.CancelledError:
            logging.info(f"⏰ Timer for '{event.chat.title}' was reset by a newer message.")
            
    debounce_tasks[chat_id] = asyncio.create_task(schedule_send())

async def main():
    logging.info("Connecting Client...")
    await client.start()
    logging.info("✅ Client Connected.")
    
    me = await client.get_me()
    own_ids.add(me.id)
    logging.info(f"Own account ID identified: {me.id}")

    accessible_groups = await find_and_verify_groups(client, group_usernames)
    
    if not accessible_groups:
        logging.critical("⛔️ No target groups found. The bot will not monitor any chats. Exiting.")
        return

    logging.info(f"\n✅ Bot is now monitoring {len(accessible_groups)} groups. Waiting for messages...")
    
    client.add_event_handler(message_handler, events.NewMessage(chats=accessible_groups))
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\nBot stopped by user.")
    except Exception as e:
        logging.critical(f"A critical error occurred in the main execution: {e}", exc_info=True)
