import os
import asyncio
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated

# Setup basic logging to see if it triggers
logger = logging.getLogger(__name__)

__MODULE__ = "Welcome"
__HELP__ = "Automatically sends a clean, beautiful welcome card when a new user joins."

# --- Helper: Crops the profile picture into a perfect circle ---
def circle_crop(image):
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    result = Image.new('RGBA', image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    return result

# --- Main Event Listener ---
# group=10 ensures this runs smoothly even if other bots are active
@Client.on_chat_member_updated(filters.group, group=10)
async def simple_welcome_card(client: Client, update: ChatMemberUpdated):
    
    # 1. Verify this is actually a NEW user joining
    if not update.new_chat_member:
        return
        
    is_new_join = False
    # If they had no previous status, or went from 'left' to 'member'
    if update.old_chat_member is None:
        is_new_join = True
    elif update.old_chat_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT]:
        if update.new_chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
            is_new_join = True
            
    if not is_new_join:
        return

    # Extract user data
    user = update.new_chat_member.user
    
    # 2. Ignore if the bot itself joined the group
    if user.is_self:
        return

    logger.info(f"🚨 NEW JOIN TRIGGERED: {user.first_name} joined {update.chat.title}")

    # 3. Get User Info
    user_id = user.id
    name = (user.first_name or "Unknown")[:15] # Limit length to fit the card
    username = f"@{user.username}" if user.username else "No Username"
    
    # 4. Safely Download Profile Picture
    pfp_path = None
    try:
        if user.photo:
            pfp_path = await client.download_media(user.photo.big_file_id)
    except Exception as e:
        logger.warning(f"Could not download PFP: {e}")

    # 5. Image Generation Function (Runs in background so it doesn't freeze the bot)
    def generate_card():
        try:
            # Looks for background.jpg in your main server folder
            bg = Image.open("background.jpg").convert("RGBA")
        except FileNotFoundError:
            logger.error("❌ ERROR: background.jpg not found in the root folder!")
            return None

        # Load profile picture or default gray circle
        if pfp_path:
            pfp = Image.open(pfp_path).convert("RGBA")
        else:
            pfp = Image.new("RGBA", (400, 400), color=(150, 150, 150, 255))
        
        # Resize and crop PFP
        pfp_size = (350, 350)
        pfp = pfp.resize(pfp_size)
        pfp = circle_crop(pfp)
        
        # Paste PFP onto background (Adjust the 750, 150 coordinates to fit your specific template!)
        bg.paste(pfp, (750, 150), pfp)
        
        # Setup Text
        draw = ImageDraw.Draw(bg)
        try:
            # Looks for font.ttf in your main server folder
            font = ImageFont.truetype("font.ttf", 45)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw the text on the image (Adjust X, Y coordinates here too!)
        text_color = "white"
        draw.text((100, 350), f"NAME : {name}", fill=text_color, font=font)
        draw.text((100, 450), f"ID : {user_id}", fill=text_color, font=font)
        draw.text((100, 550), f"USERNAME : {username}", fill=text_color, font=font)
        
        # Save to memory and return
        output = BytesIO()
        bg.convert("RGB").save(output, format="JPEG", quality=95)
        output.name = "welcome.jpg"
        return output

    # 6. Generate and Send
    card_io = await asyncio.to_thread(generate_card)
    
    if card_io:
        caption = f"Hey {user.mention}, welcome to **{update.chat.title}**!\nEnjoy the music 🎵"
        try:
            await client.send_photo(
                chat_id=update.chat.id,
                photo=card_io,
                caption=caption
            )
            logger.info("✅ Welcome card sent successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to send photo: {e}")
        
    # 7. Cleanup downloaded PFP to save server space
    if pfp_path and os.path.exists(pfp_path):
        os.remove(pfp_path)
