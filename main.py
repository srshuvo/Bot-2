import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web

# Bot Token
API_TOKEN = os.getenv("API_TOKEN")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Keep Alive server
async def handle(request):
    return web.Response(text="✅ Bot is alive!")

async def keep_alive():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logging.info("✅ Keep Alive server started!")

# /start কমান্ড হ্যান্ডলার
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("✅ বট চালু আছে! ফরোয়ার্ডের উৎসের তথ্য সরাবে এবং মিডিয়া ঠিক রাখবে।")

# Main Message Handler
@dp.message()
async def remove_forward_info(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    try:
        # যদি ফরোয়ার্ড করা মেসেজ হয় → ফরোয়ার্ডের উৎস মুছে ফেলো
        if message.forward_from or message.forward_from_chat:
            # শুধুমাত্র ফরোয়ার্ডের উৎসের তথ্য মুছে ফেলা হবে
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=message.text or "ফরওয়ার্ড মেসেজ"
            )
            logging.info("✂️ Forward source removed, media intact.")
            return

        # যদি মিডিয়া + ক্যাপশন থাকে → মেসেজ ডিলিট করে নতুন মিডিয়া পাঠাও
        if (message.photo or message.video or message.document or message.animation) and message.caption:
            file_id = None

            if message.photo:
                file_id = message.photo[-1].file_id
                content_type = "photo"
            elif message.video:
                file_id = message.video.file_id
                content_type = "video"
            elif message.document:
                file_id = message.document.file_id
                content_type = "document"
            elif message.animation:
                file_id = message.animation.file_id
                content_type = "animation"
            else:
                return  # যদি কোনো মিডিয়া না থাকে

            # পুরানো মেসেজ ডিলিট করো
            await message.delete()

            # নতুন করে মিডিয়া পাঠাও (ক্যাপশন ছাড়া)
            if content_type == "photo":
                await message.answer_photo(photo=file_id)
            elif content_type == "video":
                await message.answer_video(video=file_id)
            elif content_type == "document":
                await message.answer_document(document=file_id)
            elif content_type == "animation":
                await message.answer_animation(animation=file_id)

            logging.info(f"✂️ Caption removed and {content_type} resent.")

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
