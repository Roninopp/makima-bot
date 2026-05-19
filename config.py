import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Fixed getenv formats to properly use default values
API_ID = int(getenv("API_ID", "7217645"))
API_HASH = getenv("API_HASH", "78ba6352dd5cdc166fdef5aa84ba7c67")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "8842377028:AAFGLIO_Jp_PGnhAkD4wrQ1iopB73ft6tOM")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://delipshief_db_user:Ronin112190@cluster0.aq4lbij.mongodb.net/?appName=Cluster0")

# Vars For API End Pont.
YTPROXY_URL = getenv("YTPROXY_URL", 'https://tgapi.xbitcode.com') ## xBit Music Endpoint.
YT_API_KEY = getenv("YT_API_KEY" , "xbit_qxkNri00qFMQcYL3L1cOGML0qTTI5fJE" ) ## Your API key like: xbit_10000000xx0233 Get from  https://t.me/tgmusic_apibot

## Other vars
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))

# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", "-1003794240890"))
# Get this value from @FallenxBot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", "6837532865"))

## Fill these variables if you're deploying on heroku.
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/Roninopp/anonxron")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/amigr8")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/randomlychats")

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))
ASSISTANT_LEAVE_TIME = int(getenv("ASSISTANT_LEAVE_TIME",  5400))

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 204857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 2073741824))

PRIVATE_BOT_MODE_MEM = int(getenv("PRIVATE_BOT_MODE_MEM", 1))

CACHE_DURATION = int(getenv("CACHE_DURATION" , "86400"))  #60*60*24
CACHE_SLEEP = int(getenv("CACHE_SLEEP" , "3600"))   #60*60

# FIXED: Removed the broken newline that was causing the SyntaxError
STRING1 = getenv("STRING_SESSION", "BQBuIe0AGfdcAzBIm18faj-SV6mPW6dsolcpRJ8S2BsnEEeadvVcbJb6Tp-W4yh_mM5_Y-2vQa7rAefGxthuUHh6XzTS12BnhiwW5uq6Zoh5-VflHO-ZZHLDzDPHAATxI3g8mXoYd9zhoUVmJNp6zU1JjOlFT4rZM539xiibptEaSK46cKa4kCDKi6IYNnSfslosJfi8HAXhnMj9oLZ63GTe6IVkStfNVlJMC8JvC1DueCEeKtdqdp2TEtxmQiqIOz4m52IgwLcJngNH9dE1SgiCFxE8pqQqulzhdj9zS8d8-9Ql8wVBaCWV3ccxa6gv2pXk8R2rSVdZ8OqPtRY3joc4x_gXgAAAAGpRDpwAA")
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
file_cache: dict[str, float] = {}

START_IMG_URL = ["https://te.legra.ph/file/5fd13f2cc0d03bce9f7f2.jpg",
                 "https://te.legra.ph/file/c15d01b3e6b40ea141dc9.jpg",
                 "https://te.legra.ph/file/5fd13f2cc0d03bce9f7f2.jpg"]
    
PING_IMG_URL = getenv("PING_IMG_URL", "https://telegra.ph/file/87f680aead03443f291b0.jpg")
PLAYLIST_IMG_URL = "https://graph.org/file/c95a687e777b55be1c792.jpg"
STATS_IMG_URL = "https://telegra.ph/file/edd388a42dd2c499fd868.jpg"
TELEGRAM_AUDIO_URL = "https://telegra.ph/file/492a3bb2e880d19750b79.jpg"
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/492a3bb2e880d19750b79.jpg"
STREAM_IMG_URL = "https://graph.org/file/ff2af8d4d10afa1baf49e.jpg"
SOUNCLOUD_IMG_URL = "https://graph.org/file/c95a687e777b55be1c792.jpg"
YOUTUBE_IMG_URL = "https://graph.org/file/e8730fdece86a1166f608.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://graph.org/file/0bb6f36796d496b4254ff.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://graph.org/file/0bb6f36796d496b4254ff.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://graph.org/file/0bb6f36796d496b4254ff.jpg"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:360"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://")

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://")
