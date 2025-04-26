import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))  # Render PORT
HOST = "0.0.0.0"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ক্যাপশন মুছে মিডিয়া পাঠাবে
@dp.message()
async def remove_caption_and_send_media(message: types.Message):
    if message.photo:
        try:
            # ক্যাপশন থাকলে মুছে দিবে, শুধু ছবি পাঠাবে
            await bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message.message_id,
                caption=""  # ক্যাপশন ফাঁকা করে দিবে
            )
        except Exception as e:
            logging.error(f"Failed to remove caption: {e}")
    
    elif message.video:
        try:
            # ক্যাপশন থাকলে মুছে দিবে, শুধু ভিডিও পাঠাবে
            await bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message.message_id,
                caption=""  # ক্যাপশন ফাঁকা করে দিবে
            )
        except Exception as e:
            logging.error(f"Failed to remove caption: {e}")
    
    elif message.document:
        try:
            # ক্যাপশন থাকলে মুছে দিবে, শুধু ডকুমেন্ট পাঠাবে
            await bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message.message_id,
                caption=""  # ক্যাপশন ফাঁকা করে দিবে
            )
        except Exception as e:
            logging.error(f"Failed to remove caption: {e}")

# HTTP server for UptimeRobot
async def handle(request):
    return web.Response(text="Bot is alive!")

async def main():
    # Run aiohttp web server
    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=HOST, port=PORT)
    await site.start()

    # Run the bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
