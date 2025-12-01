# main.py - WarZone Bot با Polling ساده
import os
import asyncio
import logging
import sys
import random
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

print("🚀 شروع WarZone Bot با Polling ساده...")

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# بررسی توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ توکن یافت نشد!")
    sys.exit(1)

# ایجاد بات
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==================== هندلرهای اصلی ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎯 **به WarZone خوش آمدید!** ⚔️\n\n"
        "✅ بات با Polling فعال است!\n\n"
        "دستورات:\n"
        "/help - راهنما\n"
        "/test - تست بات\n"
        "/ping - بررسی سرعت"
    )
    print(f"✅ کاربر {message.from_user.id} استارت زد")

@dp.message(Command("test"))
async def test_cmd(message: types.Message):
    await message.answer("✅ بات فعال است! Polling کار می‌کند.")
    print(f"✅ تست از کاربر {message.from_user.id}")

@dp.message(Command("ping"))
async def ping_cmd(message: types.Message):
    start = time.time()
    msg = await message.answer("🏓 پینگ...")
    latency = (time.time() - start) * 1000
    await msg.edit_text(f"🏓 پونگ!\n⏱ زمان: {latency:.0f}ms")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "🆘 **راهنمای WarZone**\n\n"
        "🎮 سیستم‌های بازی:\n"
        "- حمله\n"
        "- فروشگاه\n"
        "- باکس\n"
        "- ماینر\n"
        "- خرابکاری\n"
        "- برج امنیت\n"
        "- لیگ\n\n"
        "✅ بات با Polling فعال است"
    )

# ==================== سیستم Keep Alive ساده ====================
async def keep_alive():
    """سیستم ساده Keep Alive"""
    print("🔗 Keep Alive فعال شد")
    while True:
        await asyncio.sleep(300)  # هر 5 دقیقه
        current_time = time.strftime("%H:%M:%S")
        print(f"✅ Keep Alive - {current_time}")

# ==================== تابع اصلی ====================
async def main():
    print("=" * 50)
    print("🤖 WarZone Bot - Polling Mode")
    print("=" * 50)
    
    try:
        # تست اتصال اولیه
        print("🔍 تست اتصال به تلگرام...")
        me = await bot.get_me()
        print(f"✅ بات شناسایی شد: @{me.username}")
        
        # شروع Keep Alive در پس‌زمینه
        asyncio.create_task(keep_alive())
        
        # شروع Polling ساده
        print("🔄 شروع Polling...")
        print("⏳ منتظر پیام‌ها...")
        print("=" * 50)
        
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        print("\n⏹️ بات متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
