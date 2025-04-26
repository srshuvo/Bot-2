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

# Helper function: টেক্সট বা ক্যাপশনে লিংক আছে কিনা চেক
def contains_link(text):
    if text:
        pattern = r"(https?://\S+|www\.\S+)"
        return re.search(pattern, text)
    return False

# Start Command
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("✅ বট প্রস্তুত! যেখানে ক্যাপশন বা মেসেজে লিংক পাবে, সাথে সাথে ডিলিট করবে।")

# Main Handler
@dp.message()
async def remove_links(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        try:
            # যদি টেক্সট মেসেজ বা ক্যাপশন এ লিংক থাকে
            if contains_link(message.text) or contains_link(message.caption):
                await message.delete()
        except Exception as e:
            logging.error(f"Error deleting message: {e}")

async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        keep_alive(),
        self_ping()
    )

if __name__ == "__main__":
    asyncio.run(main())
