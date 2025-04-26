import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web

# Environment থেকে টোকেন নাও
API_TOKEN = os.getenv("API_TOKEN")

# Logging সেটআপ
logging.basicConfig(level=logging.INFO)

# Bot এবং Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Keep Alive server (Render / Railway তে app awake রাখতে)
async def handle(request):
    return web.Response(text="✅ Bot is alive!")

async def keep_alive():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logging.info("✅ Keep Alive Server started on port 8080")

# /start কমান্ড হ্যান্ডলার
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("✅ বট চালু আছে! ক্যাপশন সরাবে এবং ফরোয়ার্ড মেসেজ মুছে ফেলবে।")

# মেসেজ হ্যান্ডলার: ক্যাপশন রিমুভ + ফরোয়ার্ড ডিলিট
@dp.message()
async def remove_caption_or_forward(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    try:
        # যদি ফরোয়ার্ড করা মেসেজ হয় → সাথে সাথে ডিলিট করো
        if message.forward_from or message.forward_from_chat:
            await message.delete()
            logging.info("❌ Forwarded message deleted.")
            return

        # যদি মিডিয়া + ক্যাপশন থাকে → ক্যাপশন ছাড়া আবার পাঠাও
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

            logging.info("✂️ Caption removed and media resent.")

    except Exception as e:
        logging.error(f"Error while processing message: {e}")

# Main Function
async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        keep_alive()
    )

if __name__ == "__main__":
    asyncio.run(main())
