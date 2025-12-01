# main.py - سازگار با aiogram 3.x
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
print("🚀 WARZONE BOT V3 STARTING...")
print("=" * 50)

# دریافت توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("⚠️ توکن یافت نشد! حالت تست فعال شد.")
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
    app.router.add_get('/healthcheck', health_check)  # برای railway
    
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
        return None, None
    
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
        from aiogram.enums import ParseMode
        
        print("🤖 Connecting to Telegram...")
        
        # ساخت بات
        bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
        
        # تست اتصال
        me = await bot.get_me()
        print(f"✅ Connected to: @{me.username} (ID: {me.id})")
        
        # ساخت دیسپچر
        dp = Dispatcher()
        
        # ========== HANDLERS ==========
        @dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            await message.answer(
                "🎯 <b>به WarZone خوش آمدید!</b>\n\n"
                "🤖 بات فعال است و آماده خدمت!\n"
                "✅ همه سیستم‌ها آنلاین هستند\n\n"
                "<b>دستورات سریع:</b>\n"
                "/help - راهنما\n"
                "/profile - پروفایل\n"
                "/shop - فروشگاه\n"
                "/attack - حمله\n\n"
                "<i>بات توسط Railway میزبانی می‌شود</i>"
            )
            print(f"👤 کاربر {message.from_user.id} استارت زد")
        
        @dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            await message.answer(
                "🆘 <b>راهنمای WarZone</b>\n\n"
                "<b>دستورات اصلی:</b>\n"
                "/start - شروع بات\n"
                "/help - این راهنما\n"
                "/profile - پروفایل\n"
                "/shop - فروشگاه\n"
                "/attack - حمله\n\n"
                "<b>سیستم‌ها:</b>\n"
                "• ⚔️ سیستم حمله\n"
                "• 🛒 فروشگاه تجهیزات\n"
                "• ⛏ ماینر منابع\n"
                "• 🏆 سیستم لیگ\n\n"
                "<i>ورژن: 3.0 | میزبان: Railway</i>"
            )
        
        @dp.message(Command("profile"))
        async def cmd_profile(message: types.Message):
            from datetime import datetime
            user_id = message.from_user.id
            username = message.from_user.username or message.from_user.first_name
            
            profile = f"""
👤 <b>پروفایل جنگجو</b>

🆔 <b>آیدی:</b> {user_id}
👤 <b>نام:</b> {username}
⭐ <b>سطح:</b> 1
💰 <b>ZP:</b> 1,000
💎 <b>جم:</b> 10
💪 <b>قدرت:</b> 100

⚔️ <b>حملات:</b> 0
💥 <b>دمیج کل:</b> 0
🛡 <b>دفاع:</b> 50%

⏰ <b>عضویت:</b> {datetime.now().strftime('%Y-%m-%d')}
✅ <b>وضعیت:</b> فعال
"""
            await message.answer(profile)
        
        @dp.message(Command("shop"))
        async def cmd_shop(message: types.Message):
            shop = """
🛒 <b>فروشگاه WarZone</b>

<b>🚀 موشک‌ها:</b>
• تیرباران - 400 ZP
• رعدآسا - 700 ZP
• تندباد - 1,000 ZP

<b>🛩 جنگنده‌ها:</b>
• شب‌پرواز - 5,000 ZP
• توفان‌ساز - 8,000 ZP

<b>🛸 پهپادها:</b>
• زنبورک - 3,000 ZP
• سایفر - 5,000 ZP

💰 <b>موجودی شما:</b> 1,000 ZP
✅ <b>فروشگاه:</b> باز
"""
            await message.answer(shop)
        
        @dp.message(Command("attack"))
        async def cmd_attack(message: types.Message):
            import random
            damage = random.randint(50, 150)
            reward = random.randint(100, 300)
            
            attack = f"""
⚔️ <b>حمله موفق!</b>

🎯 <b>نوع:</b> حمله تکی
💥 <b>دمیج:</b> {damage}
💰 <b>جایزه:</b> {reward} ZP
⭐ <b>XP:</b> +25

🏆 <b>نتیجه:</b> پیروزی
✅ <b>موجودی جدید:</b> 1,{reward} ZP

<i>از حمله ترکیبی برای جایزه بیشتر استفاده کنید!</i>
"""
            await message.answer(attack)
        
        # هندلر برای تمام پیام‌ها
        @dp.message()
        async def echo(message: types.Message):
            if message.text:
                # اگر دستور نبود
                if not message.text.startswith('/'):
                    await message.answer(
                        f"📨 <b>پیام دریافت شد:</b> {message.text}\n\n"
                        "🤖 <i>بات در حال کار است!</i>\n"
                        "💡 برای راهنما /help را بفرستید"
                    )
        
        print("✅ All handlers registered successfully")
        return dp, bot
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("📦 لطفا aiogram را آپدیت کنید:")
        print("pip install aiogram==3.11.2")
        return None, None
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
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
            # شروع پولینگ
            await dp.start_polling(bot, skip_updates=True)
            
        except Exception as e:
            print(f"❌ Polling error: {e}")
            print("⚠️ اما HTTP server همچنان فعال است")
            await asyncio.Future()  # Run forever
    else:
        print("⚠️ Telegram bot failed to start")
        print("✅ اما HTTP server is running for Railway healthcheck")
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
        # باز هم اجرا بمان برای Railway
        import time
        time.sleep(3600)
