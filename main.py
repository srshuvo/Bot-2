import asyncio
import logging
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from fastapi import FastAPI
import uvicorn

from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")

url_pattern = re.compile(r'https?://\S+|www\.\S+')

bot = Bot(token=TOKEN)
dp = Dispatcher()

# FastAPI Server Setup
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bot is running!"}

@dp.message(F.content_type.in_({"text", "photo", "video", "document", "animation"}))
async def remove_links_and_captions(message: Message):
    try:
        text = message.text or message.caption
        if text and (url_pattern.search(text) or message.entities or message.caption_entities):
            if message.text:
                await message.edit_text("⛔️ লিংক মুছে ফেলা হয়েছে", reply_markup=message.reply_markup)
            elif message.caption:
                await message.edit_caption(caption="⛔️ ক্যাপশন মুছে ফেলা হয়েছে", reply_markup=message.reply_markup)
    except Exception as e:
        logging.error(f"Error: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(dp.start_polling(bot))
    # FastAPI server রান করানো
    config = uvicorn.Config(app=app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
