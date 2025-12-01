# main.py - WarZone Bot با Polling بهبود یافته
import os
import asyncio
import logging
import sys
import random
import time
from datetime import datetime
from aiohttp import web  # برای health check

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import keyboards as kb
from config import SHOP_ITEMS, ATTACK_TYPES, ADMINS, SABOTAGE_TEAMS, CYBER_TOWER
from database_stable import db

print("🚀 شروع WarZone Bot با Polling بهبود یافته...")

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# بررسی توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("❌ توکن یافت نشد!")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==================== HEALTH CHECK ====================
# ایجاد سرور ساده برای Railway Health Check
app = web.Application()

async def health_check(request):
    return web.Response(text="✅ بات WarZone فعال است")

app.router.add_get('/health', health_check)
app.router.add_get('/', health_check)

# ==================== KEEP ALIVE ====================
async def keep_alive():
    """سیستم Keep Alive"""
    print("🔗 Keep Alive فعال شد")
    while True:
        try:
            await asyncio.sleep(60)  # هر 60 ثانیه
            me = await bot.get_me()
            print(f"✅ Keep Alive - بات فعال: @{me.username}")
        except Exception as e:
            print(f"⚠️ Keep Alive خطا: {e}")

# ==================== تست بات ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    await message.answer(
        f"🎯 **به WarZone خوش آمدید!** ⚔️\n\n"
        f"💰 موجودی: {user['zp']:,} ZP\n"
        f"⭐ سطح: {user['level']}\n"
        f"💪 قدرت: {user['power']}\n\n"
        f"👇 از منوی زیر انتخاب کنید:",
        reply_markup=kb.main_menu()
    )
    print(f"✅ کاربر {message.from_user.id} استارت زد")

@dp.message(Command("ping"))
async def ping_cmd(message: types.Message):
    """بررسی latency"""
    start = time.time()
    msg = await message.answer("🏓 پینگ...")
    latency = (time.time() - start) * 1000
    await msg.edit_text(f"🏓 پونگ!\n⏱ زمان: {latency:.0f}ms\n✅ بات فعال است")

@dp.message(Command("debug"))
async def debug_cmd(message: types.Message):
    """اطلاعات دیباگ"""
    try:
        me = await bot.get_me()
        user = db.get_user(message.from_user.id)
        
        await message.answer(
            f"🔧 **اطلاعات دیباگ**\n\n"
            f"🤖 بات: @{me.username}\n"
            f"👤 کاربر: {message.from_user.id}\n"
            f"💰 ZP: {user['zp']:,}\n"
            f"🕒 زمان: {datetime.now().strftime('%H:%M:%S')}\n"
            f"✅ وضعیت: آنلاین"
        )
    except Exception as e:
        await message.answer(f"❌ خطا: {str(e)}")

# ==================== تابع اصلی ====================
async def main():
    print("=" * 50)
    print("🤖 راه‌اندازی WarZone Bot")
    print("=" * 50)
    
    try:
        # 1. شروع Health Check Server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        print("🌐 Health Check: http://0.0.0.0:8080/health")
        
        # 2. شروع Keep Alive
        asyncio.create_task(keep_alive())
        
        # 3. حذف webhook قبلی
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook حذف شد")
        
        # 4. شروع Polling با تنظیمات بهینه
        print("🔄 شروع Polling...")
        print("⏳ منتظر پیام‌ها...")
        print("=" * 50)
        
        await dp.start_polling(
            bot,
            skip_updates=True,
            timeout=60,  # افزایش timeout
            relax=0.5,
            allowed_updates=dp.resolve_used_update_types()
        )
        
    except KeyboardInterrupt:
        print("\n⏹️ بات متوقف شد")
    except Exception as e:
        print(f"❌ خطای بحرانی: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # شروع برنامه
    asyncio.run(main())
