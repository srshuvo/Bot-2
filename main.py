import logging
import os
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
import aiohttp

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Keep Alive Server
async def handle(request):
    return web.Response(text="Bot is alive!")

async def keep_alive():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logging.info("Keep Alive Server started on port 8080")

async def self_ping():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(os.getenv("SELF_URL"))
                logging.info("Self-ping sent!")
        except Exception as e:
            logging.error(f"Ping error: {e}")
        await asyncio.sleep(300)

# Helper function: মেসেজ থেকে লিংক সরানো
def remove_links(text):
    if text:
        pattern = r"(https?://\S+|www\.\S+)"
        return re.sub(pattern, '', text).strip()
    return text

# Start Command
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("✅ বট প্রস্তুত! ক্যাপশন ও লিংক সরাতে প্রস্তুত।")

# Main Handler
@dp.message()
async def process_message(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        try:
            # যদি মিডিয়া থাকে এবং ক্যাপশন থাকে
            if (message.photo or message.video or message.document or message.animation) and message.caption:
                clean_caption = remove_links(message.caption)
                if clean_caption != message.caption:
                    await bot.edit_message_caption(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        caption=clean_caption
                    )

            # যদি টেক্সট মেসেজে লিংক থাকে
            elif message.text:
                clean_text = remove_links(message.text)
                if clean_text != message.text:
                    await bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        text=clean_text
                    )
            
            # যদি বট মেসেজ থাকে
            if message.from_user.is_bot:
                if (message.photo or message.video or message.document or message.animation) and message.caption:
                    clean_caption = remove_links(message.caption)
                    if clean_caption != message.caption:
                        await bot.edit_message_caption(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            caption=clean_caption
                        )

        except Exception as e:
            logging.error(f"Error editing message: {e}")

async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        keep_alive(),
        self_ping()
    )

if __name__ == "__main__":
    asyncio.run(main())
