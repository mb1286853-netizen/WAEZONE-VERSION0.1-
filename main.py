import os
import asyncio
import logging
import sys
import random
import time
from datetime import datetime
from aiohttp import web
import socket

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties

print("🚀 شروع WarZone Bot...")

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== تنظیمات بات ====================
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ توکن یافت نشد!")
    print("⚠️ در Railway: Settings → Variables → TELEGRAM_TOKEN")
    sys.exit(1)

print(f"✅ توکن دریافت شد: {TOKEN[:10]}...")

# ایجاد session با timeout بیشتر
session = AiohttpSession(
    timeout=30.0,
    connector=None,
)

default = DefaultBotProperties(
    parse_mode="HTML",
    disable_web_page_preview=True,
)

bot = Bot(
    token=TOKEN,
    session=session,
    default=default,
)

dp = Dispatcher()

# ==================== تست اتصال ====================
async def test_connection():
    """تست اتصال به تلگرام"""
    max_retries = 3
    for i in range(max_retries):
        try:
            print(f"🔗 تلاش {i+1} برای اتصال...")
            me = await bot.get_me()
            print(f"✅ اتصال موفق! بات: @{me.username}")
            return True
        except Exception as e:
            print(f"❌ خطای اتصال: {e}")
            if i < max_retries - 1:
                await asyncio.sleep(2)
    return False

# ==================== HEALTH CHECK ====================
app = web.Application()

async def health_check(request):
    return web.Response(text="✅ بات WarZone فعال است")

app.router.add_get('/', health_check)
app.router.add_get('/health', health_check)

# ==================== KEEP ALIVE ====================
async def keep_alive():
    """سیستم Keep Alive"""
    print("🔗 Keep Alive فعال شد")
    while True:
        try:
            await asyncio.sleep(300)  # هر 5 دقیقه
            # تست اتصال ساده
            print(f"🕒 Keep Alive: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"⚠️ Keep Alive خطا: {e}")

# ==================== هندلرهای ساده ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎯 **به WarZone خوش آمدید!** ⚔️\n\n"
        "👇 از منوی زیر انتخاب کنید:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="✅ تست بات")],
                [types.KeyboardButton(text="📊 وضعیت")]
            ],
            resize_keyboard=True
        )
    )

@dp.message(F.text == "✅ تست بات")
async def test_bot(message: types.Message):
    await message.answer("✅ بات فعال است! می‌توانید شروع کنید.")

@dp.message(F.text == "📊 وضعیت")
async def status_cmd(message: types.Message):
    await message.answer(
        f"📊 **وضعیت بات**\n\n"
        f"✅ وضعیت: آنلاین\n"
        f"🕒 زمان: {datetime.now().strftime('%H:%M:%S')}\n"
        f"🔗 Keep Alive: فعال\n"
        f"🌐 Health Check: OK"
    )

# ==================== تابع اصلی ====================
async def main():
    print("=" * 50)
    print("🤖 راه‌اندازی WarZone Bot")
    print("=" * 50)
    
    try:
        # 1. تست اتصال اولیه
        print("🔍 تست اتصال به تلگرام...")
        if not await test_connection():
            print("❌ اتصال به تلگرام ناموفق بود!")
            print("⚠️ دلایل احتمالی:")
            print("   - توکن اشتباه")
            print("   - مشکل شبکه")
            print("   - IP شما بلاک شده")
            sys.exit(1)
        
        # 2. شروع Health Check Server
        port = int(os.getenv("PORT", 8080))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        print(f"🌐 Health Check فعال: پورت {port}")
        
        # 3. شروع Keep Alive
        asyncio.create_task(keep_alive())
        
        # 4. شروع Polling (بدون delete_webhook اول)
        print("🔄 شروع Polling...")
        print("⏳ منتظر پیام‌ها...")
        print("=" * 50)
        
        await dp.start_polling(
            bot,
            skip_updates=True,
            timeout=90,  # timeout طولانی
            relax=1.0,
            close_bot_session=True
        )
        
    except KeyboardInterrupt:
        print("\n⏹️ بات متوقف شد")
    except Exception as e:
        print(f"❌ خطای بحرانی: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # تنظیم event loop
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 بات متوقف شد")
        sys.exit(0)
