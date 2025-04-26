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

# লিংক ডিটেক্ট করার প্যাটার্ন
url_pattern = re.compile(r'(https?://\S+|www\.\S+)')

bot = Bot(token=TOKEN)
dp = Dispatcher()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bot is running!"}

# /start হ্যান্ডলার
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("✅ বট চালু আছে! আমি টেক্সট থেকে শুধু লিংক মুছে দিবো এবং ক্যাপশন থাকলে ফাঁকা করে দিবো।")

# মেইন কাজের হ্যান্ডলার
@dp.message(F.content_type.in_({"text", "photo", "video", "document", "animation"}))
async def clean_links(message: Message):
    try:
        if message.text:
            # টেক্সটের মধ্যে লিংক থাকলে কাটা হবে
            cleaned_text = url_pattern.sub('', message.text).strip()
            if cleaned_text != message.text:
                try:
                    await message.edit_text(cleaned_text or "⛔️ শুধুমাত্র লিংক ছিল, তাই লিংক মুছে ফেলা হয়েছে।", reply_markup=message.reply_markup)
                except TelegramBadRequest as e:
                    logging.warning(f"Cannot edit text message id={message.message_id}: {e}")

        elif message.caption:
            # ক্যাপশন থাকলে সরিয়ে দিবে
            try:
                await message.edit_caption(caption="", reply_markup=message.reply_markup)
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
