import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

API_TOKEN = os.getenv("API_TOKEN")  # Render এ সেট করা Environment Variable

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())