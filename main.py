import asyncio
import logging
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from fastapi import FastAPI
import uvicorn

from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest

TOKEN = os.getenv("API_TOKEN")

# লিংক ডিটেক্ট করার জন্য regex
url_pattern = re.compile(r'(https?://\S+|www\.\S+)')

bot = Bot(token=TOKEN)
dp = Dispatcher()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bot is running!"}

# /start কমান্ড হ্যান্ডলার
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("✅ বট চালু আছে! গ্রুপে যেকেউ মেসেজ পাঠালেই নিয়ম অনুযায়ী অ্যাকশন হবে।")

# সবার মেসেজ প্রসেসর
@dp.message()
async def handle_all_messages(message: Message):
    try:
        if message.text:
            # টেক্সটে যদি লিংক থাকে ➔ মেসেজ ডিলিট করবে
            if url_pattern.search(message.text):
                try:
                    await message.delete()
                    logging.info(f"Deleted text message with link from user {message.from_user.id}")
                except TelegramBadRequest as e:
                    logging.warning(f"Cannot delete text message id={message.message_id}: {e}")

        elif message.caption:
            # মিডিয়াতে ক্যাপশন থাকলে ➔ ক্যাপশন ফাঁকা করবে
            try:
                await message.edit_caption(caption="", reply_markup=message.reply_markup)
                logging.info(f"Cleared caption in media message id={message.message_id}")
            except TelegramBadRequest as e:
                logging.warning(f"Cannot edit caption of message id={message.message_id}: {e}")

    except Exception as e:
        logging.error(f"Error: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(dp.start_polling(bot))
    config = uvicorn.Config(app=app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
