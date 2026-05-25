import asyncio
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

# Hook into AnonXMusic's Core & Database
from AnonXMusic import app 
from AnonXMusic.core.mongo import mongodb

# Create a database collection specifically for welcome settings
welcome_db = mongodb.welcome_status

print("✅ WELCOME.PY: Loaded successfully! Pro Mode Active.")

BACKGROUND_URL = "https://i.ibb.co/WvYsLxyg/background.png"
# 🚨 Fetching a beautiful, bold font directly from Google to prevent microscopic text!
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

# --- NEW FEATURE: The /welcome off Command ---
@app.on_message(filters.command("welcome") & filters.group)
async def welcome_toggle(client, message):
    # 1. Security Check: Only admins can use this
    user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply_text("❌ You need to be an admin to use this command.")
        
    if len(message.command) > 1 and message.command[1].lower() == "off":
        # Save to MongoDB so it remembers even if the bot restarts!
        await welcome_db.update_one({"chat_id": message.chat.id}, {"$set": {"disabled": True}}, upsert=True)
        await message.reply_text("✅ Welcome card has been **disabled** for this group.")
    else:
        await message.reply_text("Use `/welcome off` to disable the welcome card.")

# --- CORE WELCOME LOGIC ---
async def process_welcome(client, chat, user):
    if user.is_self:
        return
        
    # 2. Check Database: Skip if the group used /welcome off
    is_disabled = await welcome_db.find_one({"chat_id": chat.id})
    if is_disabled and is_disabled.get("disabled"):
        return

    user_id = user.id
    name = (user.first_name or "Unknown")[:15]
    username = f"@{user.username}" if user.username else "No Username"
    
    # 3. Download PFP directly into RAM (Bypassing Heroku folders entirely!)
    pfp_bytes = None
    try:
        if user.photo:
            pfp_bytes = await client.download_media(user.photo.big_file_id, in_memory=True)
    except Exception as e:
        print(f"🚨 PFP Error: {e}")

    def generate_card():
        try:
            # Download Background and force it to a massive 1280x720 resolution
            bg_response = requests.get(BACKGROUND_URL)
            bg = Image.open(BytesIO(bg_response.content)).convert("RGBA")
            bg = bg.resize((1280, 720))
            
            # Download Font and set size to 55px so it pops!
            font_response = requests.get(FONT_URL)
            font = ImageFont.truetype(BytesIO(font_response.content), 55)
        except Exception as e:
            print(f"❌ Asset Error: {e}")
            return None

        if pfp_bytes:
            pfp = Image.open(pfp_bytes).convert("RGBA")
        else:
            pfp = Image.new("RGBA", (400, 400), color=(150, 150, 150, 255))
        
        pfp_size = (370, 370)
        pfp = pfp.resize(pfp_size)
        pfp = circle_crop(pfp)
        
        # Coordinates aligned specifically for your neon ring image!
        bg.paste(pfp, (780, 175), pfp)
        
        draw = ImageDraw.Draw(bg)
        text_color = "white"
        
        # Draw huge, clear text!
        draw.text((80, 320), f"NAME : {name}", fill=text_color, font=font)
        draw.text((80, 420), f"ID : {user_id}", fill=text_color, font=font)
        draw.text((80, 520), f"USERNAME : {username}", fill=text_color, font=font)
        
        output = BytesIO()
        bg.convert("RGB").save(output, format="JPEG", quality=95)
        output.name = "welcome.jpg"
        return output

    card_io = await asyncio.to_thread(generate_card)
    
    if card_io:
        # 4. Generate the "Add Me" Button using your bot's actual username
        bot_username = client.me.username if client.me else "BeatNovaBot"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{bot_username}?startgroup=true")]
        ])
        
        try:
            # Send the image with NO caption, just the button!
            await client.send_photo(
                chat_id=chat.id, 
                photo=card_io, 
                caption="", 
                reply_markup=markup
            )
        except Exception as e:
            print(f"❌ Send Error: {e}")

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
