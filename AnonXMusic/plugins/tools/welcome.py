import asyncio
import requests
import json
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import ChatMemberUpdated

from AnonXMusic import app 
from AnonXMusic.core.mongo import mongodb
import config 

welcome_db = mongodb.welcome_status

print("✅ WELCOME.PY: Loaded successfully! 10-Min Auto-Delete & Heavy Debugger Active.")

BACKGROUND_URL = "https://i.ibb.co/gZ6c84TL/Gemini-Generated-Image-8y28q28y28q28y28.png"
FONT_URL = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"

__MODULE__ = "Welcome"
__HELP__ = "Automatically sends a clean, beautiful welcome card when a new user joins."

def circle_crop(image):
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    result = Image.new('RGBA', image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    return result

# 🚀 BACKGROUND TASK: 10 Minute Timer with Debug Fallbacks
async def auto_delete_welcome(client, chat_id, message_id):
    print(f"⏱️ WELCOME DEBUG: Countdown started! Will delete message {message_id} in 10 minutes.")
    
    # 600 seconds = 5 minutes
    await asyncio.sleep(300)
    
    print(f"🗑️ WELCOME DEBUG: 10 minutes passed! Attempting to delete message {message_id} in chat {chat_id}...")
    try:
        await client.delete_messages(chat_id=chat_id, message_ids=message_id)
        print(f"✅ WELCOME DEBUG: SUCCESS! Welcome card auto-deleted flawlessly.")
    except Exception as e:
        print(f"❌ WELCOME FATAL ERROR: Failed to auto-delete message! Reason: {e}")

@app.on_message(filters.command("welcome") & filters.group)
async def welcome_toggle(client, message):
    user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply_text("❌ You need to be an admin to use this command.")
        
    if len(message.command) > 1 and message.command[1].lower() == "off":
        await welcome_db.update_one({"chat_id": message.chat.id}, {"$set": {"disabled": True}}, upsert=True)
        await message.reply_text("✅ Welcome card has been **disabled** for this group.")
    else:
        await message.reply_text("Use `/welcome off` to disable the welcome card.")

async def process_welcome(client, chat, user):
    if user.is_self:
        return
        
    is_disabled = await welcome_db.find_one({"chat_id": chat.id})
    if is_disabled and is_disabled.get("disabled"):
        return

    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"
    
    pfp_bytes = None
    try:
        if user.photo:
            pfp_bytes = await client.download_media(user.photo.big_file_id, in_memory=True)
    except Exception as e:
        pass

    def generate_card():
        try:
            bg_response = requests.get(BACKGROUND_URL)
            bg = Image.open(BytesIO(bg_response.content)).convert("RGBA")
            bg = bg.resize((1280, 720))
            
            font_data = requests.get(FONT_URL).content
            font_normal = ImageFont.truetype(BytesIO(font_data), 55)
            font_huge = ImageFont.truetype(BytesIO(font_data), 100) 
        except Exception as e:
            return None

        if pfp_bytes:
            pfp = Image.open(pfp_bytes).convert("RGBA")
        else:
            pfp = Image.new("RGBA", (400, 400), color=(150, 150, 150, 255))
        
        pfp_size = (370, 370)
        pfp = pfp.resize(pfp_size)
        pfp = circle_crop(pfp)
        
        bg.paste(pfp, (750, 150), pfp)
        
        draw = ImageDraw.Draw(bg)
        text_color = "white"
        
        draw.text((80, 250), "WELCOME!", fill=text_color, font=font_huge)
        draw.text((80, 420), f"ID : {user_id}", fill=text_color, font=font_normal)
        draw.text((80, 520), f"USERNAME : {username}", fill=text_color, font=font_normal)
        
        output = BytesIO()
        bg.convert("RGB").save(output, format="JPEG", quality=95)
        output.name = "welcome.jpg"
        return output

    card_io = await asyncio.to_thread(generate_card)
    
    if card_io:
        bot_username = client.me.username if client.me else "BeatNovaBot"
        
        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat.id))
        form.add_field("photo", card_io.getvalue(), filename="welcome.jpg", content_type="image/jpeg")
        form.add_field("caption", "")
        
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "Add Me To Your Group",
                        "url": f"https://t.me/{bot_username}?startgroup=true",
                        "style": "danger",
                        "icon_custom_emoji_id": "5235472087652510235"
                    }
                ]
            ]
        }
        form.add_field("reply_markup", json.dumps(reply_markup))
        
        try:
            url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendPhoto"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form) as resp:
                    if resp.status != 200:
                        print(f"🔥 HTTP API BYPASS FAILED: {await resp.text()}")
                    else:
                        print("✅ WELCOME DEBUG: Card successfully sent!")
                        
                        # 🚀 DEBUGGING THE JSON RESPONSE TO ENSURE WE GET THE MESSAGE ID
                        try:
                            response_data = await resp.json()
                            if response_data.get("ok"):
                                message_id = response_data["result"]["message_id"]
                                print(f"✅ WELCOME DEBUG: Grabbed Message ID [{message_id}]. Sending to auto-deleter...")
                                asyncio.create_task(auto_delete_welcome(client, chat.id, message_id))
                            else:
                                print(f"⚠️ WELCOME DEBUG: Telegram blocked the message ID retrieval. Data: {response_data}")
                        except Exception as parse_err:
                            print(f"⚠️ WELCOME DEBUG: Could not parse JSON for auto-delete: {parse_err}")
                            
        except Exception as e:
            print(f"🔥 HTTP REQUEST CRASHED: {e}")

@app.on_chat_member_updated(group=10)
async def member_updated_welcome(client, update: ChatMemberUpdated):
    if update.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return
        
    if not update.new_chat_member:
        return
        
    is_new_join = False
    if update.old_chat_member is None:
        is_new_join = True
    elif update.old_chat_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT]:
        if update.new_chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
            is_new_join = True
            
    if is_new_join:
        await process_welcome(client, update.chat, update.new_chat_member.user)
