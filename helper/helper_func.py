import base64
import re
import asyncio
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, Forbidden, FloodWait
from datetime import datetime, timedelta
from pyrogram import errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# =============================================================== #
# ENCODE / DECODE
# =============================================================== #

async def encode(string: str):
    return base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")

async def decode(base64_string: str):
    base64_string += "=" * (-len(base64_string) % 4)
    return base64.urlsafe_b64decode(base64_string.encode()).decode()

# =============================================================== #
# FETCH MESSAGES (ALWAYS FROM DB)
# =============================================================== #

async def get_messages(client, message_ids):
    """
    Always fetch from primary DB channel.
    Link generator MUST copy file to DB first.
    """
    messages = []

    for i in range(0, len(message_ids), 200):
        chunk = message_ids[i:i + 200]

        try:
            msgs = await client.get_messages(client.db, chunk)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(client.db, chunk)

        messages.extend([m for m in msgs if m])

    return messages

# =============================================================== #
# MESSAGE ID EXTRACTION (NO DB RESTRICTION)
# =============================================================== #

async def get_message_id(client, message):
    """
    Accept ANY forwarded message or t.me link.
    Only extracts source id.
    Storing logic handled in link_generator.py
    """

    # Forwarded message
    if message.forward_from_chat:
        return message.forward_from_message_id, message.forward_from_chat.id

    # Anonymous forward reject
    if message.forward_sender_name:
        return 0, 0

    # t.me link
    if message.text:
        pattern = r"https://t.me/(?:c/)?(.+?)/(\d+)"
        match = re.match(pattern, message.text.strip())

        if not match:
            return 0, 0

        channel_part = match.group(1)
        msg_id = int(match.group(2))

        try:
            # Private channel format
            if channel_part.isdigit():
                return msg_id, int(f"-100{channel_part}")

            # Public username
            chat = await client.get_chat(channel_part)
            return msg_id, chat.id

        except:
            return 0, 0

    return 0, 0

async def get_message_id_legacy(client, message):
    msg_id, _ = await get_message_id(client, message)
    return msg_id

# =============================================================== #
# TIME HELPERS
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
# FORCE SUB SYSTEM (UNCHANGED CORE)
# =============================================================== #

async def check_subscription(client, user_id):
    statuses = {}

    if not await client.mongodb.present_user(user_id):
        await client.mongodb.add_user(user_id)

    for channel_id, (channel_name, channel_link, request, timer) in client.fsub_dict.items():
        try:
            user = await client.get_chat_member(channel_id, user_id)
            status = user.status

            if status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                statuses[channel_id] = status
            else:
                statuses[channel_id] = ChatMemberStatus.BANNED

        except UserNotParticipant:
            statuses[channel_id] = ChatMemberStatus.BANNED

        except Forbidden:
            statuses[channel_id] = None

        except Exception:
            statuses[channel_id] = None

    return statuses

def is_user_subscribed(statuses):
    return all(
        status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
        for status in statuses.values() if status is not None
    ) and bool(statuses)

# =============================================================== #
# AUTO DELETE
# =============================================================== #

DEL_MSG = """<b>This File is deleting automatically in <a href="https://t.me/{username}">{time}</a>.. Forward in your Saved Messages..!</b>"""

async def batch_auto_del_notification(bot_username, messages, delay_time, transfer_link, chat_id, client):

    if not messages:
        return

    notification_msg = await client.send_message(
        chat_id=chat_id,
        text=DEL_MSG.format(username=bot_username, time=convert_time(delay_time)),
        disable_web_page_preview=True
    )

    await asyncio.sleep(delay_time)

    for msg in messages:
        try:
            await msg.delete()
        except:
            pass

    try:
        if transfer_link:
            name = "• ɢᴇᴛ ғɪʟᴇs •"
            link = f"https://t.me/{bot_username}?start={transfer_link}"
            button = [[InlineKeyboardButton(text=name, url=link)]]

            await notification_msg.edit_text(
                text="<b>›› Files Deleted</b>",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            await notification_msg.edit_text("<b>›› Files Deleted</b>")
    except:
        pass

# =============================================================== #
# FORCE SUB WRAPPER (Required for shortner.py)
# =============================================================== #

async def force_sub(client, message):
    statuses = await check_subscription(client, message.from_user.id)

    if not is_user_subscribed(statuses):
        buttons = []

        for channel_id, (channel_name, channel_link, request, timer) in client.fsub_dict.items():
            if channel_link:
                buttons.append(
                    [InlineKeyboardButton(f"Join {channel_name}", url=channel_link)]
                )

        await message.reply(
            "⚠️ You must join all required channels before using this bot.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return False

    return True
