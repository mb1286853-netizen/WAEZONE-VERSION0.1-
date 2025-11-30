# main.py - Emergency Fix
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

print("🚀 STARTING BOT...")

# تنظیمات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
print(f"TOKEN: {TOKEN}")

if not TOKEN:
    print("❌ NO TOKEN!")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# هندلر ساده start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    print(f"✅ START RECEIVED FROM: {message.from_user.id}")
    await message.answer("🎯 **بات WarZone فعال است!**\n\nبه بات خوش آمدید!")

# هندلر ساده test
@dp.message(Command("test"))
async def test_cmd(message: types.Message):
    await message.answer("✅ **بات کار می‌کند!**")

# هندلر برای همه پیام‌ها
@dp.message()
async def echo_cmd(message: types.Message):
    print(f"📩 Message: {message.text} from {message.from_user.id}")
    await message.answer("🔧 بات در حال راه‌اندازی...")

async def main():
    print("🔧 Starting bot...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted")
        await dp.start_polling(bot)
        print("✅ Polling started successfully")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
