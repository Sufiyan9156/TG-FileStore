import logging
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = '5010'
OWNER_ID = 2079844068

MSG_EFFECT = 5046509860389126442

SHORT_URL = "linkshortify.com"
SHORT_API = ""
SHORT_TUT = "https://t.me/How_to_Download_7x/26"

# Bot Configuration
SESSION = "filestoredb"
TOKEN = "8586327207:AAFW0ZP0x3nwds9ldddAe2ZSDT0UzmaSryY"
API_ID = 26044496   # ❗ int rakho string nahi
API_HASH = "e2b4c24b7a9642e47a5ae5a45e013c31"
WORKERS = 5

DB_URI = "mongodb+srv://sofiyanb42_db_user:Test12345@abufilebotdb.up4utqb.mongodb.net/filestoredb?retryWrites=true&w=majority"
DB_NAME = "filestoredb"

FSUBS = [[-1002517849305, True, 10]]

DB_CHANNEL = -1003436758650   # ❗ int rakho, string nahi

AUTO_DEL = 300

ADMINS = [2079844068]

DISABLE_BTN = True
PROTECT = True

MESSAGES = {
    "START": "<b>›› ʜᴇʏ!!, {first} ~ <blockquote> ʙʀᴏ? ɪ ᴀᴍ ᴍᴀᴅᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ғɪɴᴅ ᴡʜᴀᴛ ʏᴏᴜ aʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ.</blockquote></b>",
    "FSUB": "<b><blockquote>›› ʜᴇʏ ×</blockquote>\n  ʏᴏᴜʀ ғɪʟᴇ ɪs ʀᴇᴀᴅʏ ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғɪʟᴇs</b>",
    "ABOUT": "<b>›› ғᴏʀ ᴍᴏʀᴇ: @SenpaiAnimess \n <blockquote expandable>›› ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/SenpaiAnimess'>Cʟɪᴄᴋ ʜᴇʀᴇ</a></blockquote></b>",
    "REPLY": "<b>For More Join - @SenpaiAnimess</b>",
    "SHORT_MSG": "<b>📊 ʜᴇʏ {first},\n\n‼️ ɢᴇᴛ ᴀʟʟ ꜰɪʟᴇꜱ ɪɴ ᴀ ꜱɪɴɢʟᴇ ʟɪɴᴋ ‼️</b>",
    "START_PHOTO": "https://graph.org/file/510affa3d4b6c911c12e3.jpg",
}

# ✅ SAFE LOGGER (No Duplicate Handlers)
def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # 🚀 Prevent duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )

    file_handler = RotatingFileHandler(
        LOG_FILE_NAME,
        maxBytes=50_000_000,
        backupCount=10
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
