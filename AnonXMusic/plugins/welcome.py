from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# If you need database or config variables, import them here
# import config

@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    for member in message.new_chat_members:
        # 1. Ignore if the bot itself was added to avoid spamming
        if member.is_self:
            continue
            
        # 2. Extract user details
        user_id = member.id
        first_name = member.first_name
        mention = member.mention
        
        # 3. Download the user's profile picture (Optional, but great for cards)
        # We wrap this in a try-except because some users hide their profile pictures
        photo_path = None
        try:
            if member.photo:
                photo_path = await client.download_media(member.photo.big_file_id)
        except Exception as e:
            pass # Handle users with no profile picture here

        # 4. TODO: Generate your image using Pillow here!
        # For now, we will use a static placeholder image URL or local path
        welcome_image = "https://telegra.ph/file/YOUR_DEFAULT_WELCOME_IMAGE.jpg" 
        
        welcome_text = (
            f"Hey {mention}, welcome to the group!\n\n"
            f"Enjoy the music and make sure to read the rules."
        )

        # 5. Send the welcome card
        await message.reply_photo(
            photo=welcome_image,
            caption=welcome_text,
            parse_mode=ParseMode.HTML
        )
