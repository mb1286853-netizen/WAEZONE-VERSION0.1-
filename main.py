# main.py - با Healthcheck برای Railway
import os
import asyncio
import logging
import sys
from aiohttp import web

print("🚀 WarZone Bot Starting...")

# دریافت توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
print(f"🔍 توکن دریافت شد: {'*' * 10 if TOKEN else '❌ NOT FOUND'}")

# Healthcheck سرور برای Railway
async def handle_healthcheck(request):
    return web.Response(text="OK")

async def start_http_server():
    """سرور HTTP برای Healthcheck"""
    app = web.Application()
    app.router.add_get('/health', handle_healthcheck)
    app.router.add_get('/', handle_healthcheck)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"✅ Healthcheck سرور روی پورت {port} راه‌اندازی شد")
    return runner

async def main():
    print("🌐 راه‌اندازی Healthcheck سرور...")
    http_runner = await start_http_server()
    
    if not TOKEN:
        print("❌ توکن یافت نشد! فقط Healthcheck فعال است.")
        # برای همیشه اجرا بمان
        await asyncio.Future()
        return
    
    print("🤖 در حال اتصال به تلگرام...")
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
        
        bot = Bot(token=TOKEN)
        dp = Dispatcher()
        
        @dp.message(Command("start"))
        async def start_cmd(message: types.Message):
            await message.answer("🎯 به WarZone خوش آمدید! بات فعال است.")
        
        @dp.message(Command("help"))
        async def help_cmd(message: types.Message):
            await message.answer("🆘 کمک: /start - شروع بات")
        
        # تست اتصال
        me = await bot.get_me()
        print(f"✅ ربات متصل شد: @{me.username}")
        
        print("🔄 شروع پولینگ...")
        
        # اجرای همزمان پولینگ و سرور HTTP
        polling_task = asyncio.create_task(
            dp.start_polling(bot, skip_updates=True)
        )
        
        print("✅ بات با موفقیت راه‌اندازی شد!")
        
        # منتظر بمان تا هر دو task اجرا بشن
        try:
            await asyncio.wait_for(polling_task, timeout=1.0)
        except asyncio.TimeoutError:
            # پولینگ در پس‌زمینه ادامه داره
            pass
        
        # برای همیشه اجرا بمان
        await asyncio.Future()
        
    except Exception as e:
        print(f"❌ خطا در تلگرام: {e}")
        print("⚠️ اما Healthcheck سرور فعال باقی می‌ماند...")
        await asyncio.Future()  # برای همیشه اجرا بمان

if __name__ == "__main__":
    asyncio.run(main())
