import logging
import os
import asyncio
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
        await asyncio.sleep(300)  # প্রতি 5 মিনিটে ping

# Telegram Bot Handler
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("আমি প্রস্তুত! ছবি, ভিডিও, ডকুমেন্ট পাঠান - আমি ক্যাপশন সরিয়ে দিবো।")

@dp.message()
async def remove_caption(message: types.Message):
    if message.photo or message.video or message.document or message.animation:
        if message.caption:
            try:
                if message.chat.type in ["group", "supergroup"]:
                    await message.delete()
                
                if message.photo:
                    file_id = message.photo[-1].file_id
                    await message.answer_photo(photo=file_id)
                elif message.video:
                    file_id = message.video.file_id
                    await message.answer_video(video=file_id)
                elif message.document:
                    file_id = message.document.file_id
                    await message.answer_document(document=file_id)
                elif message.animation:
                    file_id = message.animation.file_id
                    await message.answer_animation(animation=file_id)
            except Exception as e:
                logging.error(f"Error processing media: {e}")

async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        keep_alive(),
        self_ping()
    )

if __name__ == "__main__":
    asyncio.run(main())
