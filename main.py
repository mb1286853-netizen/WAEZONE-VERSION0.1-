# main.py - Simple Test
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

print("=== STARTING BOT ===")

# تنظیمات ساده
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
print(f"TOKEN: {TOKEN}")

if not TOKEN:
    print("❌ NO TOKEN!")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    print(f"📱 User {message.from_user.id} started")
    await message.answer("🎯 **بات فعال است!**")

@dp.message(Command("ping"))
async def ping_cmd(message: types.Message):
    await message.answer("🏓 **Pong!**")

async def main():
    print("🔄 Starting polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted")
        await dp.start_polling(bot)
        print("✅ Polling started")
    except Exception as e:
        print(f"❌ Polling error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
