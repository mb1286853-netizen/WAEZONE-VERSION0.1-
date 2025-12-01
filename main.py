# main.py - WarZone Bot با Polling ساده (اصلاح شده)
import os
import asyncio
import logging
import sys
import random
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode

print("🚀 شروع WarZone Bot با Polling ساده...")

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# بررسی توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ توکن یافت نشد!")
    print("⚠️ در Railway: Settings → Variables → TELEGRAM_TOKEN را تنظیم کن")
    sys.exit(1)

print(f"✅ توکن دریافت شد: {TOKEN[:10]}...")

# ایجاد بات با تنظیمات ساده
bot = Bot(
    token=TOKEN,
    parse_mode=ParseMode.HTML
)
dp = Dispatcher()

# ==================== هندلرهای اصلی ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎯 <b>به WarZone خوش آمدید!</b> ⚔️\n\n"
        "✅ بات با Polling فعال است!\n\n"
        "<b>دستورات:</b>\n"
        "/help - راهنما\n"
        "/test - تست بات\n"
        "/ping - بررسی سرعت\n"
        "/status - وضعیت بات"
    )
    print(f"✅ کاربر {message.from_user.id} استارت زد")

@dp.message(Command("test"))
async def test_cmd(message: types.Message):
    await message.answer("<b>✅ بات فعال است!</b> Polling کار می‌کند.")
    print(f"✅ تست از کاربر {message.from_user.id}")

@dp.message(Command("ping"))
async def ping_cmd(message: types.Message):
    start_time = time.time()
    ping_msg = await message.answer("🏓 <b>در حال پینگ...</b>")
    latency = (time.time() - start_time) * 1000
    
    await ping_msg.edit_text(
        f"🏓 <b>پونگ!</b>\n"
        f"⏱ زمان پاسخ: <code>{latency:.0f}ms</code>\n"
        f"✅ بات آنلاین"
    )

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    try:
        me = await bot.get_me()
        await message.answer(
            f"📊 <b>وضعیت بات</b>\n\n"
            f"🤖 بات: @{me.username}\n"
            f"🆔 ID: <code>{me.id}</code>\n"
            f"👤 نام: {me.full_name}\n"
            f"🕒 زمان: {time.strftime('%H:%M:%S')}\n"
            f"🔧 حالت: <b>Polling</b>\n"
            f"✅ وضعیت: <b>آنلاین</b>"
        )
    except Exception as e:
        await message.answer(f"❌ خطا در دریافت وضعیت: {str(e)}")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "🆘 <b>راهنمای WarZone</b>\n\n"
        "🎮 <b>سیستم‌های بازی:</b>\n"
        "• ⚔️ حمله\n"
        "• 🛒 فروشگاه\n"
        "• 📦 باکس\n"
        "• ⛏ ماینر\n"
        "• 🦠 خرابکاری\n"
        "• 🏢 برج امنیت\n"
        "• 🏆 لیگ\n\n"
        "✅ <b>بات با Polling فعال است</b>"
    )

@dp.message(Command("id"))
async def get_id_cmd(message: types.Message):
    await message.answer(
        f"🆔 <b>اطلاعات کاربر</b>\n\n"
        f"👤 ID: <code>{message.from_user.id}</code>\n"
        f"👥 نام: {message.from_user.full_name}\n"
        f"📱 نام کاربری: @{message.from_user.username or 'ندارد'}"
    )

# ==================== سیستم Keep Alive ساده ====================
async def keep_alive():
    """سیستم ساده Keep Alive"""
    print("🔗 Keep Alive فعال شد")
    counter = 0
    while True:
        await asyncio.sleep(60)  # هر 1 دقیقه
        counter += 1
        current_time = time.strftime("%H:%M:%S")
        print(f"✅ Keep Alive #{counter} - {current_time}")

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
        print(f"👤 نام بات: {me.full_name}")
        
        # شروع Keep Alive در پس‌زمینه
        keep_alive_task = asyncio.create_task(keep_alive())
        print("🔗 Keep Alive در پس‌زمینه فعال شد")
        
        # شروع Polling ساده
        print("🔄 شروع Polling...")
        print("⏳ منتظر پیام‌ها...")
        print("=" * 50)
        
        await dp.start_polling(
            bot,
            skip_updates=True,  # نادیده گرفتن پیام‌های قدیمی
            timeout=30,
            relax=0.1
        )
        
    except KeyboardInterrupt:
        print("\n⏹️ بات توسط کاربر متوقف شد")
    except Exception as e:
        print(f"❌ خطای بحرانی: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # راه‌اندازی بات
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 بات متوقف شد")
        sys.exit(0)
