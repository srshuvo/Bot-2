import logging
import re
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import MessageEntityType

# টোকেন নিন এনভায়রনমেন্ট থেকে
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# লিংক খোঁজার জন্য প্যাটার্ন
url_pattern = re.compile(r'https?://\S+|www\.\S+')

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def remove_links_and_captions(message: types.Message):
    try:
        is_bot = message.from_user.is_bot

        # টেক্সট বা ক্যাপশনে লিংক থাকলে
        text = message.text or message.caption

        if text and (url_pattern.search(text) or message.entities or message.caption_entities):
            # ক্যাপশন বা টেক্সটের মধ্যে লিংক থাকলে এডিট করে দিবে
            if message.text:
                await message.edit_text("⛔ লিংক সরানো হয়েছে", reply_markup=message.reply_markup)
            elif message.caption:
                await message.edit_caption(caption="⛔ ক্যাপশন সরানো হয়েছে", reply_markup=message.reply_markup)

    except Exception as e:
        logging.error(f"Error processing message: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
