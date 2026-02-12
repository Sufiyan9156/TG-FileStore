
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random

MAX_CHANNELS = 5

async def check_force_sub(client, user_id):

    all_channels = list(client.fsub_dict.keys())

    if not all_channels:
        return True

    not_joined = []

    for ch in all_channels:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)

    if not not_joined:
        return True

    selected = random.sample(not_joined, min(MAX_CHANNELS, len(not_joined)))

    buttons = []

    for ch in selected:
        invite = await client.create_chat_invite_link(ch)
        buttons.append([
            InlineKeyboardButton("Join Channel", url=invite.invite_link)
        ])

    buttons.append([
        InlineKeyboardButton("🔄 Try Again", callback_data="recheck_fsub")
    ])

    return InlineKeyboardMarkup(buttons)
