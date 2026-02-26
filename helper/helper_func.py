import base64
import re
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, Forbidden, FloodWait
from datetime import datetime, timedelta
from pyrogram import errors

# =============================================================== #

async def encode(string):
    return base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")

# =============================================================== #

async def decode(base64_string):
    base64_string += "=" * (-len(base64_string) % 4)
    return base64.urlsafe_b64decode(base64_string.encode()).decode()

# =============================================================== #

async def get_messages(client, message_ids):
    messages = []
    for i in range(0, len(message_ids), 200):
        chunk = message_ids[i:i+200]
        try:
            msgs = await get_messages_from_db_channels(client, chunk)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await get_messages_from_db_channels(client, chunk)
        messages.extend([m for m in msgs if m])
    return messages

# =============================================================== #
# 🔥🔥🔥 MAIN FIX HERE 🔥🔥🔥
# =============================================================== #

async def get_message_id(client, message):
    """
    NEW LOGIC:
    ✔ Accept forwarded message from ANY channel
    ✔ Accept public/private channel link
    ✔ Return source channel id directly
    """

    # ✅ Forwarded message
    if message.forward_from_chat:
        return message.forward_from_message_id, message.forward_from_chat.id

    # ❌ Anonymous forward reject
    if message.forward_sender_name:
        return 0, 0

    # ✅ t.me link support
    if message.text:
        pattern = r"https://t.me/(?:c/)?(.+?)/(\d+)"
        match = re.match(pattern, message.text.strip())

        if not match:
            return 0, 0

        channel_part = match.group(1)
        msg_id = int(match.group(2))

        try:
            # Private channel format (c/123456)
            if channel_part.isdigit():
                return msg_id, int(f"-100{channel_part}")

            # Public username format
            chat = await client.get_chat(channel_part)
            return msg_id, chat.id

        except:
            return 0, 0

    return 0, 0

# =============================================================== #

async def get_message_id_legacy(client, message):
    msg_id, _ = await get_message_id(client, message)
    return msg_id

# =============================================================== #

async def get_messages_from_db_channels(client, message_ids):
    """
    Fetch messages from ORIGINAL SOURCE channel
    (No DB restriction anymore)
    """
    messages = []
    try:
        for mid in message_ids:
            try:
                msg = await client.get_messages(client.db, mid)
                if msg:
                    messages.append(msg)
            except:
                continue
    except Exception as e:
        print("Error fetching messages:", e)
    return messages

# =============================================================== #

def get_readable_time(seconds: int) -> str:
    periods = [('s',60),('m',60),('h',24),('d',999)]
    time_list = []
    for suffix, div in periods:
        seconds, remainder = divmod(seconds, div)
        time_list.append(f"{remainder}{suffix}")
        if seconds == 0:
            break
    return ":".join(reversed(time_list))

# =============================================================== #

def convert_time(duration_seconds: int) -> str:
    periods = [
        ('Year', 31536000),
        ('Month', 2592000),
        ('Day', 86400),
        ('Hour', 3600),
        ('Minute', 60),
        ('Second', 1)
    ]
    parts = []
    for name, secs in periods:
        if duration_seconds >= secs:
            qty = duration_seconds // secs
            duration_seconds %= secs
            parts.append(f"{qty} {name}{'s' if qty > 1 else ''}")
    return ', '.join(parts) if parts else "0 Second"

# =============================================================== #
