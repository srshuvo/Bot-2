import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
import aiohttp

API_TOKEN = os.getenv("API_TOKEN")
SELF_URL = os.getenv("SELF_URL")  # Self-ping এর জন্য URL

# Logging setup
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

# Self-Ping প্রতি ৫ মিনিটে
async def self_ping():
    if not SELF_URL:
        logging.warning("SELF_URL নাই, Self-ping স্কিপ করা হচ্ছে।")
        return

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(SELF_URL)
                logging.info("Self-ping পাঠানো হয়েছে!")
        except Exception as e:
            logging.error(f"Ping error: {e}")
        await asyncio.sleep(300)  # প্রতি ৫ মিনিট

# /start কমান্ড হ্যান্ডলার
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("✅ বট চালু আছে! মিডিয়ার ক্যাপশন সরাবে এবং ফরোয়ার্ড মেসেজ মুছে ফেলবে।")

# মূল হ্যান্ডলার
@dp.update()
async def remove_caption_or_forward(update: types.Update):
    message = update.message or update.channel_post
    if not message:
        return

    if message.chat.type in ["group", "supergroup"]:
        try:
            # ফরোয়ার্ড করা মেসেজ হলে ডিলিট
            if message.forward_from or message.forward_from_chat:
                await message.delete()
                logging.info("Forwarded message deleted.")
                return

            # মিডিয়া + ক্যাপশন থাকলে ক্যাপশন ছাড়া রিসেন্ড
            if (message.photo or message.video or message.document or message.animation) and message.caption:
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
            logging.error(f"Error while processing message: {e}")

# মেইন রান
async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        keep_alive(),
        self_ping()
    )

if __name__ == "__main__":
    asyncio.run(main())
