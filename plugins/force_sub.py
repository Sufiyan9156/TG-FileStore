from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, Forbidden

# =============================================================== #
# CHECK BOT ADMIN
# =============================================================== #

async def is_bot_admin(client, channel_id):
    try:
        member = await client.get_chat_member(channel_id, "me")
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True, None
        else:
            return False, "Bot is not admin in this channel."
    except UserNotParticipant:
        return False, "Bot is not a participant in this channel."
    except Forbidden:
        return False, "Bot does not have permission to access this channel."
    except Exception as e:
        return False, str(e)

# =============================================================== #
# MAIN FSUB PANEL
# =============================================================== #

async def fsub(client, query):
    if client.fsub_dict:
        channel_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            channel_name = channel_data[0]
            request_status = "Request: ✅" if channel_data[2] else "Request: ❌"
            timer_status = f"Timer: {channel_data[3]}m" if channel_data[3] > 0 else "Timer: ∞"
            channel_list.append(
                f"• `{channel_name}` (`{channel_id}`) - {request_status}, {timer_status}"
            )
        channels_display = "\n".join(channel_list)
    else:
        channels_display = "_No force subscription channels configured_"

    msg = f"""<blockquote><b>Force Subscription Settings:</b></blockquote>

<b>Configured Channels:</b>
{channels_display}

__Use buttons below to manage force subscription.__
"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", callback_data="add_fsub"),
         InlineKeyboardButton("ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ", callback_data="rm_fsub")],
        [InlineKeyboardButton("◂ ʙᴀᴄᴋ", callback_data="settings")]
    ])

    await query.message.edit_text(msg, reply_markup=reply_markup)

# =============================================================== #
# ADD FORCE SUB
# =============================================================== #

@Client.on_callback_query(filters.regex("^add_fsub$"))
async def add_fsub(client: Client, query: CallbackQuery):
    await query.answer()

    ask = await client.ask(
        query.from_user.id,
        "Send:\n`channel_id request(true/false) timer_minutes`\n\nExample:\n`-1001234567890 yes 5`",
        timeout=60
    )

    try:
        channel_id, request, timer = ask.text.split()
        channel_id = int(channel_id)

        if channel_id in client.fsub_dict:
            return await ask.reply("Channel already exists in force sub list.")

        is_admin, error = await is_bot_admin(client, channel_id)
        if not is_admin:
            return await ask.reply(f"Error: {error}")

        request = request.lower() in ("true", "yes", "on")
        timer = int(timer)

        chat = await client.get_chat(channel_id)
        name = chat.title

        if timer > 0:
            client.fsub_dict[channel_id] = [name, None, request, timer]
        else:
            invite = await client.create_chat_invite_link(
                channel_id,
                creates_join_request=request
            )
            client.fsub_dict[channel_id] = [name, invite.invite_link, request, timer]

        await client.mongodb.add_fsub_channel(channel_id, client.fsub_dict[channel_id])

        await fsub(client, query)
        await ask.reply(f"Channel `{name}` added successfully.")

    except Exception as e:
        await ask.reply(f"Error: {e}")

# =============================================================== #
# REMOVE FORCE SUB
# =============================================================== #

@Client.on_callback_query(filters.regex("^rm_fsub$"))
async def rm_fsub(client: Client, query: CallbackQuery):
    await query.answer()

    ask = await client.ask(
        query.from_user.id,
        "Send channel_id to remove:",
        timeout=60
    )

    try:
        channel_id = int(ask.text)

        if channel_id not in client.fsub_dict:
            return await ask.reply("Channel not found in force sub list.")

        client.fsub_dict.pop(channel_id)
        await client.mongodb.remove_fsub_channel(channel_id)

        await fsub(client, query)
        await ask.reply(f"Channel `{channel_id}` removed successfully.")

    except Exception as e:
        await ask.reply(f"Error: {e}")
