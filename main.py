# main.py - نسخه فوق ساده
import os
import asyncio
import logging
import sys

print("🚀 WarZone Bot Starting...")

# دریافت توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
print(f"🔍 توکن دریافت شد: {'*' * 10 if TOKEN else '❌ NOT FOUND'}")

if not TOKEN:
    print("❌ خطا: توکن یافت نشد!")
    print("✅ اما بات برای Healthcheck Railway اجرا می‌شود")
    # Railway نیاز به process داره که بسته نشه
    import time
    time.sleep(3600)
    sys.exit(0)

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("🎯 به WarZone خوش آمدید! بات فعال است.")

async def main():
    print("🤖 در حال اتصال به تلگرام...")
    try:
        me = await bot.get_me()
        print(f"✅ ربات متصل شد: @{me.username}")
        
        print("🔄 شروع پولینگ...")
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        print("\n🔧 راه حل:")
        print("1. توکن رو از @BotFather بگیر")
        print("2. در Railway Variables تنظیم کن")
        print("3. پروژه رو Redeploy کن")
        
        # برای Railway Healthcheck
        import time
        time.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
