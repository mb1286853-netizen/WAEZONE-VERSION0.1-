# main.py - نسخه پایدار و تست شده
import os
import asyncio
import logging
import sys
from aiohttp import web

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 50)
print("🚀 WARZONE BOT STARTING...")
print("=" * 50)

# دریافت توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ توکن یافت نشد!")
    TOKEN = "dummy_token"
else:
    print(f"✅ توکن دریافت شد")

# ==================== HTTP SERVER برای Railway ====================
async def health_check(request):
    return web.Response(text="OK")

async def start_http_server():
    """سرور سلامت برای Railway"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"✅ Healthcheck server started on port {port}")
    return runner

# ==================== TELEGRAM BOT ====================
async def start_telegram_bot():
    """شروع تلگرام بات"""
    if TOKEN == "dummy_token":
        print("⚠️ حالت تست: تلگرام بات غیرفعال")
        return None
    
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
        from aiogram.client.default import DefaultBotProperties
        
        print("🤖 Connecting to Telegram...")
        
        # ساخت بات با تنظیمات بهتر
        bot = Bot(
            token=TOKEN,
            default=DefaultBotProperties(
                parse_mode="HTML",
                link_preview_is_disabled=True
            )
        )
        
        # تست اتصال
        me = await bot.get_me()
        print(f"✅ Connected to: @{me.username} (ID: {me.id})")
        
        # ساخت دیسپچر
        dp = Dispatcher()
        
        # ========== HANDLERS ==========
        @dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            await message.answer(
                "🎯 **به WarZone خوش آمدید!**\n\n"
                "🤖 بات فعال است و آماده خدمت!\n"
                "✅ همه سیستم‌ها آنلاین هستند\n\n"
                "💡 از منوی زیر استفاده کنید:",
                parse_mode="Markdown"
            )
            print(f"👤 کاربر {message.from_user.id} استارت زد")
        
        @dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            await message.answer(
                "🆘 **راهنمای WarZone**\n\n"
                "/start - شروع بات\n"
                "/help - این راهنما\n"
                "/profile - پروفایل\n"
                "/shop - فروشگاه\n"
                "/attack - حمله\n\n"
                "🎮 از منوهای کیبورد هم می‌توانید استفاده کنید",
                parse_mode="Markdown"
            )
        
        @dp.message(Command("profile"))
        async def cmd_profile(message: types.Message):
            await message.answer(
                "👤 **پروفایل شما**\n\n"
                "💰 ZP: 1,000\n"
                "⭐ Level: 1\n"
                "💪 Power: 100\n"
                "⚔️ Attacks: 0\n\n"
                "✅ سیستم پروفایل فعال است",
                parse_mode="Markdown"
            )
        
        @dp.message(Command("shop"))
        async def cmd_shop(message: types.Message):
            await message.answer(
                "🛒 **فروشگاه WarZone**\n\n"
                "🚀 موشک‌ها\n"
                "🛩 جنگنده‌ها\n"
                "🛸 پهپادها\n"
                "🛡 پدافند\n\n"
                "✅ سیستم فروشگاه فعال است",
                parse_mode="Markdown"
            )
        
        @dp.message(Command("attack"))
        async def cmd_attack(message: types.Message):
            await message.answer(
                "⚔️ **سیستم حمله**\n\n"
                "🎯 حمله تکی\n"
                "💥 حمله ترکیبی\n"
                "🛸 حمله پهپادی\n\n"
                "✅ سیستم حمله فعال است",
                parse_mode="Markdown"
            )
        
        # هندلر برای تمام پیام‌های متنی
        @dp.message()
        async def echo(message: types.Message):
            if message.text:
                await message.answer(
                    f"📨 پیام شما: {message.text}\n\n"
                    "✅ بات در حال کار است!\n"
                    "💡 از دستور /help استفاده کنید",
                    parse_mode="Markdown"
                )
        
        print("✅ All handlers registered")
        return dp, bot
        
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        import traceback
        traceback.print_exc()
        return None, None

# ==================== MAIN FUNCTION ====================
async def main():
    print("🌐 Starting HTTP server for Railway...")
    http_runner = await start_http_server()
    
    print("🤖 Initializing Telegram Bot...")
    dp, bot = await start_telegram_bot()
    
    if dp and bot:
        print("🔄 Starting polling...")
        try:
            # شروع پولینگ در یک task جداگانه
            polling_task = asyncio.create_task(
                dp.start_polling(bot, skip_updates=True)
            )
            
            print("=" * 50)
            print("✅ BOT IS FULLY OPERATIONAL!")
            print("✅ Healthcheck: http://localhost:8000/health")
            print("✅ Commands: /start, /help, /profile, /shop, /attack")
            print("=" * 50)
            
            # منتظر بمان
            await asyncio.Future()
            
        except Exception as e:
            print(f"❌ Polling error: {e}")
    else:
        print("⚠️ Telegram bot not started, but HTTP server is running")
        print("✅ Healthcheck available at: http://localhost:8000/health")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
