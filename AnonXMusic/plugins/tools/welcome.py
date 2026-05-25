import os
import asyncio
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import ChatMemberUpdated

from AnonXMusic import app 

__MODULE__ = "Welcome"
__HELP__ = "Automatically sends a clean, beautiful welcome card when a new user joins."

print("✅ WELCOME.PY: Loaded successfully! URL Mode Active.")

# 🚨 PASTE YOUR GITHUB RAW LINK HERE 🚨
# 🚨 PASTE YOUR POSTIMAGES DIRECT LINK HERE 🚨
BACKGROUND_URL = "https://ibb.co/Sw9JzsnR"

def circle_crop(image):
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    result = Image.new('RGBA', image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    return result

async def process_welcome(client, chat, user):
    if user.is_self:
        return
        
    print(f"🚨 WELCOME DEBUG: Processing welcome for {user.first_name} in {chat.title}")

    user_id = user.id
    name = (user.first_name or "Unknown")[:15]
    username = f"@{user.username}" if user.username else "No Username"
    
    pfp_path = None
    try:
        if user.photo:
            print("🚨 WELCOME DEBUG: Downloading profile picture...")
            pfp_path = await client.download_media(user.photo.big_file_id)
    except Exception as e:
        print(f"🚨 WELCOME DEBUG: Error downloading PFP: {e}")

    def generate_card():
        try:
            print("🚨 WELCOME DEBUG: Fetching background straight from the internet...")
            # We download the image into memory, completely bypassing Heroku folders!
            response = requests.get(BACKGROUND_URL)
            bg = Image.open(BytesIO(response.content)).convert("RGBA")
        except Exception as e:
            print(f"❌ FATAL ERROR: Could not fetch background from URL! Error: {e}")
            return None

        if pfp_path:
            pfp = Image.open(pfp_path).convert("RGBA")
        else:
            pfp = Image.new("RGBA", (400, 400), color=(150, 150, 150, 255))
        
        pfp_size = (350, 350)
        pfp = pfp.resize(pfp_size)
        pfp = circle_crop(pfp)
        
        # Paste PFP
        bg.paste(pfp, (750, 150), pfp)
        
        draw = ImageDraw.Draw(bg)
        
        # Try to load a font, otherwise fallback safely so the bot doesn't crash
        try:
            font = ImageFont.truetype("font.ttf", 45)
        except IOError:
            print("🚨 WELCOME DEBUG: font.ttf not found on Heroku, using default font.")
            font = ImageFont.load_default()
        
        text_color = "white"
        # Draw Text
        draw.text((100, 350), f"NAME : {name}", fill=text_color, font=font)
        draw.text((100, 450), f"ID : {user_id}", fill=text_color, font=font)
        draw.text((100, 550), f"USERNAME : {username}", fill=text_color, font=font)
        
        output = BytesIO()
        bg.convert("RGB").save(output, format="JPEG", quality=95)
        output.name = "welcome.jpg"
        return output

    card_io = await asyncio.to_thread(generate_card)
    
    if card_io:
        caption = f"Hey {user.mention}, welcome to **{chat.title}**!\nEnjoy the music 🎵"
        try:
            print("🚨 WELCOME DEBUG: Sending photo...")
            await client.send_photo(chat_id=chat.id, photo=card_io, caption=caption)
            print("✅ WELCOME DEBUG: SUCCESS! Card sent.")
        except Exception as e:
            print(f"❌ WELCOME DEBUG: Telegram refused the message. Error: {e}")
        
    if pfp_path and os.path.exists(pfp_path):
        os.remove(pfp_path)

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
        print("🚨 TRAP 1 TRIGGERED (Background Update)")
        await process_welcome(client, update.chat, update.new_chat_member.user)
