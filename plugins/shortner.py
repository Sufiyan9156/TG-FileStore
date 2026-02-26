import requests
import random
import string
from config import SHORT_URL, SHORT_API, MESSAGES
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaPhoto
)
from pyrogram.errors.pyromod import ListenerTimeout

# =============================================================== #
# CACHE
# =============================================================== #

shortened_urls_cache = {}

def generate_random_alphanumeric():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

# =============================================================== #
# SHORT LINK FUNCTION
# =============================================================== #

def get_short(url, client):

    if not getattr(client, "shortner_enabled", True):
        return url

    if url in shortened_urls_cache:
        return shortened_urls_cache[url]

    try:
        alias = generate_random_alphanumeric()

        short_url = getattr(client, "short_url", SHORT_URL)
        short_api = getattr(client, "short_api", SHORT_API)

        api_url = f"https://{short_url}/api?api={short_api}&url={url}&alias={alias}"

        response = requests.get(api_url, timeout=10)
        rjson = response.json()

        if rjson.get("status") == "success" and response.status_code == 200:
            final_url = rjson.get("shortenedUrl", url)
            shortened_urls_cache[url] = final_url
            return final_url

    except Exception as e:
        print(f"[Shortener Error] {e}")

    return url

# =============================================================== #
# COMMAND
# =============================================================== #

@Client.on_message(filters.private & filters.command("shortner"))
async def shortner_command(client: Client, message: Message):

    if message.from_user.id not in client.admins:
        return await message.reply("❌ Only admins can use this.")

    await shortner_panel(client, message)

# =============================================================== #
# PANEL
# =============================================================== #

async def shortner_panel(client, query_or_message):

    short_url = getattr(client, "short_url", SHORT_URL)
    short_api = getattr(client, "short_api", SHORT_API)
    tutorial_link = getattr(client, "tutorial_link", "https://t.me/How_to_Download_7x/26")
    shortner_enabled = getattr(client, "shortner_enabled", True)

    status_text = "✓ ENABLED" if shortner_enabled else "✗ DISABLED"
    toggle_text = "TURN OFF" if shortner_enabled else "TURN ON"

    msg = f"""
<b>SHORTNER SETTINGS</b>

Status: <code>{status_text}</code>
URL: <code>{short_url}</code>
API: <code>{short_api}</code>

Tutorial: <code>{tutorial_link}</code>
"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_text, callback_data="toggle_shortner")],
        [InlineKeyboardButton("SET SHORTNER", callback_data="add_shortner")],
        [InlineKeyboardButton("SET TUTORIAL LINK", callback_data="set_tutorial_link")],
        [InlineKeyboardButton("TEST SHORTNER", callback_data="test_shortner")]
    ])

    image_url = MESSAGES.get("SHORT")

    if hasattr(query_or_message, "message"):
        await query_or_message.message.edit_media(
            media=InputMediaPhoto(media=image_url, caption=msg),
            reply_markup=reply_markup
        )
    else:
        await query_or_message.reply_photo(
            photo=image_url,
            caption=msg,
            reply_markup=reply_markup
        )

# =============================================================== #
# TOGGLE
# =============================================================== #

@Client.on_callback_query(filters.regex("^toggle_shortner$"))
async def toggle_shortner(client: Client, query: CallbackQuery):

    if query.from_user.id not in client.admins:
        return await query.answer("❌ Admin only", show_alert=True)

    new_status = not getattr(client, "shortner_enabled", True)
    client.shortner_enabled = new_status

    await client.mongodb.set_shortner_status(new_status)

    await query.answer("Updated!")
    await shortner_panel(client, query)

# =============================================================== #
# TEST
# =============================================================== #

@Client.on_callback_query(filters.regex("^test_shortner$"))
async def test_shortner(client: Client, query: CallbackQuery):

    if query.from_user.id not in client.admins:
        return await query.answer("❌ Admin only", show_alert=True)

    await query.answer()

    short_url = getattr(client, "short_url", SHORT_URL)
    short_api = getattr(client, "short_api", SHORT_API)

    try:
        test_url = "https://google.com"
        alias = generate_random_alphanumeric()

        api_url = f"https://{short_url}/api?api={short_api}&url={test_url}&alias={alias}"
        response = requests.get(api_url, timeout=10)
        rjson = response.json()

        if rjson.get("status") == "success":
            msg = f"✅ Working\n\nShort URL:\n<code>{rjson.get('shortenedUrl')}</code>"
        else:
            msg = f"❌ Failed\n\nResponse:\n<code>{rjson}</code>"

    except Exception as e:
        msg = f"❌ Error\n\n<code>{str(e)}</code>"

    await query.message.edit_text(
        msg,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="shortner")]]
        )
    )
