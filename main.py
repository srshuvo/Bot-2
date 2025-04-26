import logging
import os
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

API_TOKEN = os.getenv("API_TOKEN")  # Render এ সেট করা Environment Variable

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# লিংক ডিটেক্ট করার জন্য regex
url_pattern = re.compile(r'(https?://\S+|www\.\S+)')

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("আমি প্রস্তুত! ছবি, ভিডিও, ডকুমেন্ট পাঠান - আমি ক্যাপশন সরিয়ে দিবো।")

@dp.message()
async def remove_caption_or_link(message: types.Message):
    try:
        # যদি টেক্সট মেসেজ হয় এবং তাতে লিংক থাকে ➔ মেসেজ ডিলিট করবে
        if message.text and url_pattern.search(message.text):
            if message.chat.type in ["group", "supergroup"]:
                await message.delete()
                logging.info(f"Deleted text message with link from {message.from_user.id}")

        # যদি মিডিয়া মেসেজ হয় ➔ ক্যাপশন থাকুক বা না থাকুক ➔ ক্যাপশন ছাড়া নতুন করে পাঠাবে
        elif message.photo or message.video or message.document or message.animation:
            try:
                if message.chat.type in ["group", "supergroup"]:
                    await message.delete()
                
                # ক্যাপশন ছাড়া মিডিয়া আবার পাঠানো
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

    except Exception as e:
        logging.error(f"Error in processing message: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
