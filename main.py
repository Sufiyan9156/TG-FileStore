from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, WORKERS

app = Client(
    "FileStoreSession",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=WORKERS
)

@app.on_message()
async def alive(_, message):
    await message.reply_text("⚡ ORA ORA ORA! Bot is Alive!")

print("🚀 JOJO SYNC SENPAI BOT STARTING...")
app.run()
