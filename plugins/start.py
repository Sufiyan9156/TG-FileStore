from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from config import MSG_EFFECT, OWNER_ID
from plugins.shortner import get_short
from helper.helper_func import (
    get_messages,
    force_sub,
    decode,
    batch_auto_del_notification
)
import asyncio

# =============================================================== #

@Client.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):

    # ✅ FORCE SUB CHECK
    if not await force_sub(client, message):
        return

    user_id = message.from_user.id

    # Add user if not present
    if not await client.mongodb.present_user(user_id):
        try:
            await client.mongodb.add_user(user_id)
        except:
            pass

    # Check banned
    if await client.mongodb.is_banned(user_id):
        return await message.reply("❌ You are banned from using this bot.")

    text = message.text

    # ===============================================================
    # FILE REQUEST MODE
    # ===============================================================

    if len(text.split()) > 1:

        try:
            original_payload = text.split(" ", 1)[1]
            base64_string = original_payload
        except:
            return await message.reply("⚠️ Invalid link.")

        # Premium check
        is_user_pro = await client.mongodb.is_pro(user_id)
        shortner_enabled = getattr(client, "shortner_enabled", True)

        # 🔹 Shortner condition
        if (
            not is_user_pro
            and user_id != OWNER_ID
            and shortner_enabled
            and not base64_string.startswith("yu3elk")
        ):
            try:
                short_link = get_short(
                    f"https://t.me/{client.username}?start=yu3elk{base64_string}7",
                    client
                )
            except:
                return await message.reply("❌ Shortener failed.")

            tutorial_link = getattr(
                client,
                "tutorial_link",
                "https://t.me/How_to_Download_7x/26"
            )

            await message.reply(
                "🔗 Click below to access your file:",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("• Open Link •", url=short_link),
                        InlineKeyboardButton("Tutorial", url=tutorial_link)
                    ]
                ])
            )
            return

        # Decode payload
        try:
            decoded = await decode(base64_string)
            data = decoded.split("-")
        except:
            return await message.reply("⚠️ Invalid or expired link.")

        ids = []

        try:
            if len(data) == 3:
                start = int(int(data[1]) / abs(client.db))
                end = int(int(data[2]) / abs(client.db))
                ids = list(range(start, end + 1))
            elif len(data) == 2:
                msg_id = int(int(data[1]) / abs(client.db))
                ids = [msg_id]
        except:
            return await message.reply("⚠️ Corrupted link.")

        wait_msg = await message.reply("⏳ Please wait...")

        try:
            messages = await get_messages(client, ids)
        except:
            await wait_msg.edit("❌ Failed fetching files.")
            return

        if not messages:
            return await wait_msg.edit("❌ Files not found.")

        await wait_msg.delete()

        sent_msgs = []

        for msg in messages:
            try:
                copied = await msg.copy(
                    chat_id=user_id,
                    protect_content=client.protect
                )
                sent_msgs.append(copied)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied = await msg.copy(
                    chat_id=user_id,
                    protect_content=client.protect
                )
                sent_msgs.append(copied)
            except:
                pass

        # Auto delete
        if sent_msgs and getattr(client, "auto_del", 0) > 0:
            asyncio.create_task(
                batch_auto_del_notification(
                    bot_username=client.username,
                    messages=sent_msgs,
                    delay_time=client.auto_del,
                    transfer_link=original_payload,
                    chat_id=user_id,
                    client=client
                )
            )

        return

    # ===============================================================
    # NORMAL START MESSAGE
    # ===============================================================

    buttons = [
        [
            InlineKeyboardButton("Help", callback_data="about"),
            InlineKeyboardButton("Close", callback_data="close")
        ]
    ]

    if user_id in client.admins:
        buttons.insert(
            0,
            [InlineKeyboardButton("⚙ Settings", callback_data="settings")]
        )

    start_caption = f"👋 Welcome {message.from_user.mention}"

    await message.reply(
        start_caption,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
