from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# --- This is what makes it show up in your stats! ---
__MODULE__ = "Welcome"
__HELP__ = """
<b>Welcome Module:</b>
Automatically sends a welcome card when a new user joins the group.
"""
# ----------------------------------------------------

@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    for member in message.new_chat_members:
        # Ignore if the bot itself was added
        if member.is_self:
            continue
            
        # Extract user details
        user_id = member.id
        first_name = member.first_name
        mention = member.mention
        
        # Download the user's profile picture safely
        photo_path = None
        try:
            if member.photo:
                photo_path = await client.download_media(member.photo.big_file_id)
        except Exception:
            pass 

        # The image you want to send (we will replace this with Pillow code later)
        welcome_image = "https://telegra.ph/file/YOUR_DEFAULT_WELCOME_IMAGE.jpg" 
        
        welcome_text = (
            f"Hey {mention}, welcome to the group!\n\n"
            f"Enjoy the music and make sure to read the rules."
        )

        # Send the welcome card
        await message.reply_photo(
            photo=welcome_image,
            caption=welcome_text,
            parse_mode=ParseMode.HTML
        )
