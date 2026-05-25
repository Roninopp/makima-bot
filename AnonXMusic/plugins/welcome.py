import os
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import ChatMemberUpdated

__MODULE__ = "Welcome"
__HELP__ = "Automatically sends a clean, beautiful welcome card when a new user joins."

# This prints instantly when the bot starts, proving the file is read.
print("✅ WELCOME.PY: Module successfully loaded into memory!")

def circle_crop(image):
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    result = Image.new('RGBA', image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    return result

# Removed filters.group from here to guarantee we catch the event
@Client.on_chat_member_updated(group=10)
async def simple_welcome_card(client: Client, update: ChatMemberUpdated):
    
    # 1. Manually enforce the group filter here
    if update.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return

    print(f"🚨 WELCOME DEBUG: chat_member_updated fired in {update.chat.title}!")

    if not update.new_chat_member:
        print("🚨 WELCOME DEBUG: No new_chat_member found in update. Ignoring.")
        return
        
    is_new_join = False
    if update.old_chat_member is None:
        is_new_join = True
    elif update.old_chat_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT]:
        if update.new_chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
            is_new_join = True
            
    if not is_new_join:
        print("🚨 WELCOME DEBUG: Event is just a status update, not a new join.")
        return

    user = update.new_chat_member.user
    
    if user.is_self:
        print("🚨 WELCOME DEBUG: Bot itself was added. Ignoring.")
        return

    print(f"🚨 WELCOME DEBUG: Valid join detected for {user.first_name}! Starting image generation...")

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
            print("🚨 WELCOME DEBUG: Opening background.jpg...")
            bg = Image.open("background.jpg").convert("RGBA")
        except FileNotFoundError:
            print("❌ FATAL ERROR: background.jpg is missing from the root folder!")
            return None

        if pfp_path:
            pfp = Image.open(pfp_path).convert("RGBA")
        else:
            pfp = Image.new("RGBA", (400, 400), color=(150, 150, 150, 255))
        
        pfp_size = (350, 350)
        pfp = pfp.resize(pfp_size)
        pfp = circle_crop(pfp)
        
        # Coordinates for PFP
        bg.paste(pfp, (750, 150), pfp)
        
        draw = ImageDraw.Draw(bg)
        try:
            font = ImageFont.truetype("font.ttf", 45)
        except IOError:
            print("🚨 WELCOME DEBUG: font.ttf missing, using default font.")
            font = ImageFont.load_default()
        
        text_color = "white"
        # Coordinates for Text
        draw.text((100, 350), f"NAME : {name}", fill=text_color, font=font)
        draw.text((100, 450), f"ID : {user_id}", fill=text_color, font=font)
        draw.text((100, 550), f"USERNAME : {username}", fill=text_color, font=font)
        
        print("🚨 WELCOME DEBUG: Image compiled successfully. Saving to memory...")
        output = BytesIO()
        bg.convert("RGB").save(output, format="JPEG", quality=95)
        output.name = "welcome.jpg"
        return output

    card_io = await asyncio.to_thread(generate_card)
    
    if card_io:
        caption = f"Hey {user.mention}, welcome to **{update.chat.title}**!\nEnjoy the music 🎵"
        try:
            print("🚨 WELCOME DEBUG: Attempting to send photo to Telegram...")
            await client.send_photo(
                chat_id=update.chat.id,
                photo=card_io,
                caption=caption
            )
            print("✅ WELCOME DEBUG: SUCCESS! Card sent.")
        except Exception as e:
            print(f"❌ WELCOME DEBUG: Telegram refused the message. Error: {e}")
        
    if pfp_path and os.path.exists(pfp_path):
        os.remove(pfp_path)
