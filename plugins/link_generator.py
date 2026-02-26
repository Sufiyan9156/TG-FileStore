from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ListenerTimeout
from helper.helper_func import encode
import asyncio


# =============================================================== #
# SINGLE LINK GENERATOR
# =============================================================== #

@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):

    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    ask_msg = await message.reply("📥 Send or Forward the file you want to store in DB...")

    try:
        file_msg = await client.ask(
            chat_id=message.from_user.id,
            filters=filters.media,
            timeout=300  # ⏱ 5 Minutes
        )
    except ListenerTimeout:
        return await ask_msg.edit("❌ Time Out! Send file again.")

    await ask_msg.edit("⏳ Storing in database...")

    try:
        stored = await file_msg.copy(chat_id=client.db)
    except Exception as e:
        return await ask_msg.edit(f"❌ Failed to store file\n\n{e}")

    encoded = await encode(f"get-{stored.id * abs(client.db)}")
    link = f"https://t.me/{client.username}?start={encoded}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]
    ])

    await ask_msg.edit(
        f"✅ <b>Here is your link</b>\n\n<code>{link}</code>",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


# =============================================================== #
# BATCH LINK GENERATOR
# =============================================================== #

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):

    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    ask_msg = await message.reply(
        "📥 Send multiple files one by one.\nType /done when finished.\n\n⏱ You have 5 minutes per file."
    )

    stored_ids = []

    while True:
        try:
            file_msg = await client.ask(
                chat_id=message.from_user.id,
                timeout=300  # ⏱ 5 Minutes per message
            )
        except ListenerTimeout:
            break

        if file_msg.text and file_msg.text.lower() == "/done":
            break

        if not file_msg.media:
            continue

        try:
            stored = await file_msg.copy(chat_id=client.db)
            stored_ids.append(stored.id)
        except:
            continue

    if not stored_ids:
        return await ask_msg.edit("❌ No files stored.")

    start_id = min(stored_ids)
    end_id = max(stored_ids)

    encoded = await encode(
        f"get-{start_id * abs(client.db)}-{end_id * abs(client.db)}"
    )

    link = f"https://t.me/{client.username}?start={encoded}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share Batch URL", url=f"https://telegram.me/share/url?url={link}")]
    ])

    await ask_msg.edit(
        f"✅ <b>Your Batch Link</b>\n\n<code>{link}</code>",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
