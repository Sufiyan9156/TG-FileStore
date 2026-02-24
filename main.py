from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, WORKERS

app = Client(
    "FileStoreSession",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=WORKERS
)

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):

    # Agar deep link hai
    if len(message.command) > 1:
        file_key = message.command[1]

        await message.reply_text(
            f"🔐 Vault Key Detected...\n\n"
            f"Key: `{file_key}`\n\n"
            f"Checking access..."
        )

        # Yaha future me:
        # ForceSub check
        # MongoDB lookup
        # File send logic
        return

    # Agar normal /start hai
    await message.reply_text(
        "⚡ ORA ORA ORA! ⚡\n\n"
        "📦 Welcome to JOJO SYNC SENPAI\n\n"
        "Your files are sealed inside the vault 🔐\n"
        "Open a valid link to access them."
    )

print("🚀 JOJO SYNC SENPAI BOT STARTING...")
app.run()
