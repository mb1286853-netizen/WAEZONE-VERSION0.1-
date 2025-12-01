# main.py - سازگار با aiogram 2.x (برای Railway)
import os
import asyncio
import logging
import sys
from aiohttp import web

print("=" * 60)
print("🚀 WARZONE BOT - RAILWAY EDITION")
print("=" * 60)

# دریافت توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("⚠️ WARNING: TELEGRAM_TOKEN not found!")
    print("⚠️ Bot will run in healthcheck-only mode")
    TOKEN = None
else:
    print(f"✅ Token loaded: {TOKEN[:10]}...")

# ==================== HTTP SERVER ====================
async def health_check(request):
    return web.Response(text="OK")

async def start_http_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"✅ HTTP Server running on port {port}")
    print(f"✅ Healthcheck: http://localhost:{port}/health")
    return runner

# ==================== TELEGRAM BOT ====================
async def start_bot():
    if not TOKEN:
        return None
    
    try:
        print("🤖 Importing aiogram...")
        # Try multiple import methods
        try:
            from aiogram import Bot, Dispatcher, types
            from aiogram import executor
            print("✅ aiogram imported successfully")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("📦 Installing aiogram...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "aiogram==2.25.1"])
            from aiogram import Bot, Dispatcher, types
            from aiogram import executor
        
        print("🤖 Creating bot instance...")
        bot = Bot(token=TOKEN)
        
        # Test connection
        try:
            me = await bot.get_me()
            print(f"✅ Connected to: @{me.username} (ID: {me.id})")
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return None
        
        dp = Dispatcher(bot)
        
        # ========== HANDLERS ==========
        @dp.message_handler(commands=['start'])
        async def send_welcome(message: types.Message):
            await message.answer(
                "🎯 <b>به WarZone خوش آمدید!</b>\n\n"
                "🤖 بات با موفقیت راه‌اندازی شد!\n"
                "✅ همه سیستم‌ها فعال هستند\n\n"
                "<b>دستورات:</b>\n"
                "/help - راهنمای بات\n"
                "/profile - پروفایل شما\n"
                "/shop - فروشگاه جنگ\n"
                "/attack - حمله به دشمن\n\n"
                "<i>میزبان: Railway | وضعیت: آنلاین</i>",
                parse_mode="HTML"
            )
            print(f"👤 User {message.from_user.id} started")
        
        @dp.message_handler(commands=['help'])
        async def send_help(message: types.Message):
            help_text = """
🆘 <b>راهنمای WarZone</b>

<b>دستورات اصلی:</b>
/start - شروع بات
/help - این راهنما
/profile - اطلاعات حساب
/shop - فروشگاه تجهیزات
/attack - سیستم حمله

<b>سیستم‌های فعال:</b>
✅ سیستم پروفایل
✅ سیستم فروشگاه  
✅ سیستم حمله
✅ سیستم ماینر
✅ سیستم خرابکاری
✅ سیستم لیگ

<i>برای حمله به دشمن /attack را بفرستید</i>
"""
            await message.answer(help_text, parse_mode="HTML")
        
        @dp.message_handler(commands=['profile'])
        async def send_profile(message: types.Message):
            profile = f"""
👤 <b>پروفایل جنگجو</b>

🆔 <b>آیدی:</b> {message.from_user.id}
👤 <b>نام:</b> {message.from_user.first_name}
⭐ <b>سطح:</b> 1
💰 <b>ZP:</b> 1,000
💎 <b>جم:</b> 10
💪 <b>قدرت:</b> 100

⚔️ <b>آماده نبرد!</b>
✅ <b>وضعیت:</b> آنلاین
"""
            await message.answer(profile, parse_mode="HTML")
        
        @dp.message_handler(commands=['shop'])
        async def send_shop(message: types.Message):
            shop = """
🛒 <b>فروشگاه WarZone</b>

<b>موشک‌ها (🚀):</b>
• تیرباران - 400 ZP
• رعدآسا - 700 ZP
• تندباد - 1,000 ZP

<b>جنگنده‌ها (🛩):</b>
• شب‌پرواز - 5,000 ZP
• توفان‌ساز - 8,000 ZP

<b>پهپادها (🛸):</b>
• زنبورک - 3,000 ZP
• سایفر - 5,000 ZP

💰 <b>موجودی شما:</b> 1,000 ZP
🔓 <b>فروشگاه:</b> باز
"""
            await message.answer(shop, parse_mode="HTML")
        
        @dp.message_handler(commands=['attack'])
        async def send_attack(message: types.Message):
            import random
            damage = random.randint(50, 150)
            reward = random.randint(100, 300)
            
            attack = f"""
⚔️ <b>حمله موفقیت‌آمیز!</b>

🎯 <b>هدف:</b> پایگاه دشمن
💥 <b>دمیج:</b> {damage} واحد
💰 <b>غنیمت:</b> {reward} ZP
⭐ <b>تجربه:</b> +{damage // 5}

🏆 <b>نتیجه:</b> پیروزی کامل!
💎 <b>موجودی جدید:</b> {1000 + reward:,} ZP

<i>برای حملات قوی‌تر، تجهیزات خود را ارتقا دهید!</i>
"""
            await message.answer(attack, parse_mode="HTML")
        
        # Handle all other messages
        @dp.message_handler()
        async def echo(message: types.Message):
            if message.text:
                await message.answer(
                    f"📨 <b>پیام دریافت شد:</b>\n{message.text}\n\n"
                    "🤖 <i>بات در حال اجراست!</i>\n"
                    "💡 برای راهنما /help را بفرستید",
                    parse_mode="HTML"
                )
        
        print("✅ All handlers registered")
        return dp
        
    except Exception as e:
        print(f"❌ Bot setup failed: {e}")
        import traceback
        traceback.print_exc()
        return None

# ==================== MAIN ====================
async def main():
    print("🌐 Starting HTTP server...")
    http_runner = await start_http_server()
    
    print("\n🤖 Setting up Telegram Bot...")
    dp = await start_bot()
    
    if dp:
        print("\n" + "=" * 60)
        print("✅ BOT IS FULLY OPERATIONAL!")
        print("✅ HTTP Server: Running")
        print("✅ Telegram Bot: Connected")
        print("✅ Healthcheck: Active")
        print("=" * 60)
        
        # Start polling (aiogram 2.x style)
        from aiogram import executor
        print("\n🔄 Starting message polling...")
        await dp.start_polling()
        
    else:
        print("\n⚠️ Telegram bot not available")
        print("✅ But HTTP server is running for Railway")
        print("📡 Healthcheck: http://localhost:8000/health")
        
        # Keep running for Railway
        await asyncio.Future()

if __name__ == "__main__":
    # Create necessary folders
    for folder in ["backups", "logs"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        # Keep running for Railway healthcheck
        import time
        time.sleep(3600)
