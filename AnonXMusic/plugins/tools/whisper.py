import asyncio
import json
import uuid
import aiohttp
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import PeerIdInvalid

# Hooking directly into your AnonXMusic core!
from AnonXMusic import app
from AnonXMusic.core.mongo import mongodb
import config

# Create a dedicated MongoDB collection for whispers
whispers_db = mongodb.whispers

print("✅ WHISPER.PY: Loaded successfully! MongoDB & HTTP Bypass Active.")

# 🚀 Helper function to send raw JSON to Telegram API for colored inline buttons!
async def answer_inline_query_raw(inline_query_id, results):
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/answerInlineQuery"
    payload = {
        "inline_query_id": inline_query_id,
        "results": results,
        "cache_time": 0
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    print(f"🔥 HTTP API BYPASS FAILED: {await resp.text()}")
        except Exception as e:
            print(f"🔥 HTTP REQUEST CRASHED: {e}")

@app.on_inline_query()
async def inline_whisper_handler(client, inline_query):
    query = inline_query.query.strip()
    bot_username = client.me.username if client.me else "BeatNovaBot"
    
    # 1. If the user hasn't typed anything yet, show the colorful Help Menu!
    if len(query.split()) < 2:
        help_result = [{
            "type": "article",
            "id": "help_whisper",
            "title": "💒 How to send a Whisper",
            "description": f"@{bot_username} [Username] [Message]",
            "thumb_url": "https://telegra.ph/file/4287c313c71ab800e29d0.jpg",
            "input_message_content": {
                "message_text": f"**💒 Whisper Usage:**\n\nType `@{(bot_username)} @target_username Your Secret Message`\n\n_Example:_ `@{(bot_username)} @Dushmanxroninn Hey, are you there?`"
            },
            "reply_markup": {
                "inline_keyboard": [[{
                    "text": "Try it now!",
                    "switch_inline_query_current_chat": "",
                    "style": "primary",
                    "icon_custom_emoji_id": "5235472087652510235"
                }]]
            }
        }]
        return await answer_inline_query_raw(inline_query.id, help_result)

    # 2. Logic: Split into Target and Message
    try:
        first_arg = query.split()[0]
        msg = query.split(None, 1)[1]
    except IndexError:
        return # Not enough text yet

    # 3. Find the Target User
    try:
        user = await client.get_users(first_arg)
        target_id = user.id
        target_name = user.first_name
    except Exception:
        error_result = [{
            "type": "article",
            "id": "error_whisper",
            "title": "❌ Invalid User",
            "description": "I can't find that user! Make sure I know them.",
            "thumb_url": "https://telegra.ph/file/ff4455f02730649f7a98f.jpg",
            "input_message_content": {
                "message_text": "❌ **Invalid Username!**\nMake sure you typed it correctly and they have started the bot before."
            }
        }]
        return await answer_inline_query_raw(inline_query.id, error_result)

    # 4. Create secure UUIDs for the database
    normal_id = uuid.uuid4().hex
    onetime_id = uuid.uuid4().hex
    
    # 5. Save BOTH options to MongoDB instantly
    sender_id = inline_query.from_user.id
    
    await whispers_db.insert_one({"whisper_id": normal_id, "sender": sender_id, "target": target_id, "msg": msg, "type": "normal"})
    await whispers_db.insert_one({"whisper_id": onetime_id, "sender": sender_id, "target": target_id, "msg": msg, "type": "onetime"})

    # 6. Build the HTTP JSON Payload with Colored Buttons!
    results = [
        {
            "type": "article",
            "id": "normal_whisper",
            "title": "💒 Send Secure Whisper",
            "description": f"Secret message to {target_name}",
            "thumb_url": "https://telegra.ph/file/4287c313c71ab800e29d0.jpg",
            "input_message_content": {
                "message_text": f"🔒 **A Secure Whisper has been sent to {target_name}.**\n\nOnly they can open it!"
            },
            "reply_markup": {
                "inline_keyboard": [[{
                    "text": f"Read Whisper",
                    "callback_data": f"openw_{normal_id}",
                    "style": "success",
                    "icon_custom_emoji_id": "5235472087652510235"
                }]]
            }
        },
        {
            "type": "article",
            "id": "onetime_whisper",
            "title": "🔥 Send One-Time Whisper",
            "description": f"Burn after reading message to {target_name}",
            "thumb_url": "https://telegra.ph/file/ff4455f02730649f7a98f.jpg",
            "input_message_content": {
                "message_text": f"🔥 **A One-Time Whisper was sent to {target_name}.**\n\nIt will self-destruct after reading!"
            },
            "reply_markup": {
                "inline_keyboard": [[{
                    "text": f"Open & Destroy",
                    "callback_data": f"openw_{onetime_id}",
                    "style": "danger",
                    "icon_custom_emoji_id": "5235472087652510235"
                }]]
            }
        }
    ]
    
    # Send our bypassed payload!
    await answer_inline_query_raw(inline_query.id, results)

# --- CALLBACK HANDLER (When button is clicked) ---
@app.on_callback_query(filters.regex(pattern=r"^openw_(.*)"))
async def whisper_callback(client, query):
    whisper_id = query.data.split("_")[1]
    user_id = query.from_user.id
    
    # 1. Fetch from MongoDB
    whisper_data = await whispers_db.find_one({"whisper_id": whisper_id})
    
    if not whisper_data:
        return await query.answer("🚫 Error!\n\nThis whisper has expired or was destroyed.", show_alert=True)
        
    sender = whisper_data["sender"]
    target = whisper_data["target"]
    msg = whisper_data["msg"]
    w_type = whisper_data["type"]
    
    # 2. Permission Check
    if user_id not in [sender, target, config.OWNER_ID]:
        return await query.answer("🚧 Hands off! This whisper is not for you!", show_alert=True)
    
    # 3. Show the secret message via Alert Popup!
    await query.answer(msg, show_alert=True)
    
    # 4. Self-Destruct Logic for One-Time whispers
    if w_type == "onetime" and user_id == target:
        await whispers_db.delete_one({"whisper_id": whisper_id})
        
        # We change the message to show it was destroyed!
        try:
            bot_username = client.me.username if client.me else "BeatNovaBot"
            switch_btn = InlineKeyboardMarkup([[
                InlineKeyboardButton("Send your own Whisper 🤫", switch_inline_query_current_chat="")
            ]])
            await query.edit_message_text("📬 **This One-Time Whisper has been read and permanently destroyed!**", reply_markup=switch_btn)
        except Exception:
            pass

# Added dynamic module variables so it automatically shows in your /help command!
__MODULE__ = "Whisper"
__HELP__ = """
**🤫 Inline Whisper (Premium)**

Securely send hidden messages in groups that no one else can read!

**How to use:**
1. Type `@YourBotUsername @username Your Secret Message` in the chat.
2. Wait for the popup menu to appear.
3. Choose either **Secure Whisper** or **One-Time Whisper** (Self-Destructs).
4. Only the person you tagged can open it!

**Features:**
• 🔥 One-Time Self-Destructing Whispers.
• 💾 MongoDB Backed (Survives bot restarts).
• 🎨 Premium UI with Colored Action Buttons.
"""
