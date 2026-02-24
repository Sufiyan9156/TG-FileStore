from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, WORKERS

app = Client(
    "FileStoreSession",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=WORKERS
)

# 🔥 Start Command Only (No Spam Loop)
@app.on_message(filters.command("start") & filters.private & ~filters.me)
async def start_handler(client, message):
    await message.reply_text(
        "⚡ ORA ORA ORA! ⚡\n\n"
        "📦 Welcome to JOJO SYNC SENPAI\n\n"
        "Your files are sealed inside the vault 🔐\n"
        "Open a valid link to access them."
    )

print("🚀 JOJO SYNC SENPAI BOT STARTING...")
app.run()
