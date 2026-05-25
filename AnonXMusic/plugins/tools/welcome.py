import traceback
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# Set up logging for this specific file
logger = logging.getLogger(__name__)

__MODULE__ = "Welcome"
__HELP__ = """
<b>Welcome Module:</b>
Automatically sends a welcome card when a new user joins the group.
"""

# The `group=30` is the magic fix! It prevents other plugins from blocking this one.
@Client.on_message(filters.new_chat_members & filters.group, group=30)
async def welcome_new_member(client: Client, message: Message):
    logger.info("🚨 WELCOME DEBUG: A new chat member event was triggered!")
    
    try:
        for member in message.new_chat_members:
            logger.info(f"🚨 WELCOME DEBUG: Processing user {member.first_name} (ID: {member.id})")
            
            # 1. Ignore if the bot itself was added
            if member.is_self:
                logger.info("🚨 WELCOME DEBUG: The bot itself was added. Ignoring.")
                continue
                
            mention = member.mention
            
            # 2. Safely try to download the profile picture
            photo_path = None
            try:
                if member.photo:
                    logger.info("🚨 WELCOME DEBUG: User has a profile picture. Downloading...")
                    photo_path = await client.download_media(member.photo.big_file_id)
                    logger.info("🚨 WELCOME DEBUG: Profile picture downloaded successfully!")
                else:
                    logger.info("🚨 WELCOME DEBUG: User does not have a profile picture.")
            except Exception as e:
                logger.warning(f"🚨 WELCOME DEBUG: Failed to download profile picture: {e}")

            # 3. Use a REAL placeholder image so Telegram doesn't reject the request
            # We will replace this with your dynamic Pillow image later
            welcome_image = "https://telegra.ph/file/b8a0c1a00db3e57522b53.jpg" 
            
            welcome_text = (
                f"Hey {mention}, welcome to the group!\n\n"
                f"Enjoy the music and make sure to read the rules."
            )

            # 4. Attempt to send the message
            logger.info("🚨 WELCOME DEBUG: Attempting to send the welcome photo to the group...")
            await message.reply_photo(
                photo=welcome_image,
                caption=welcome_text,
                parse_mode=ParseMode.HTML
            )
            logger.info("🚨 WELCOME DEBUG: ✅ Welcome message sent successfully!")
            
    except Exception as e:
        logger.error(f"🚨 WELCOME DEBUG: ❌ CRITICAL ERROR in welcome module: {e}")
        logger.error(traceback.format_exc())
