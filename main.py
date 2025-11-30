# main.py - WarZone Bot (Optimized for Render)
import os
import asyncio
import logging
import signal
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enum import ParseMode
import aiohttp

# Import database and config
from database import WarZoneDatabase
from config import TOKEN

print("🚀 راه‌اندازی WarZone Bot برای رندر...")

# تنظیمات لاگ برای رندر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # برای دیدن لاگ در رندر
    ]
)
logger = logging.getLogger(__name__)

# بررسی توکن
if not TOKEN:
    logger.error("❌ توکن یافت نشد! لطفا TOKEN را در تنظیمات رندر تنظیم کنید.")
    sys.exit(1)

# ساخت بات
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# دیتابیس
db = WarZoneDatabase()

# منوی اصلی
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👤 پروفایل"), types.KeyboardButton(text="⚔️ حمله")],
            [types.KeyboardButton(text="🛒 فروشگاه"), types.KeyboardButton(text="⛏ ماینر")],
            [types.KeyboardButton(text="📦 جعبه"), types.KeyboardButton(text="📊 آمار")]
        ],
        resize_keyboard=True,
        input_field_placeholder="انتخاب کنید..."
    )

# هندلر استارت
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else "ناشناس"
    
    welcome_text = (
        f"🎯 **به WarZone خوش آمدید {username}!** ⚔️\n\n"
        f"🛡️ **ربات روی رندر میزبانی می‌شود** 🚀\n\n"
        "✅ **قابلیت‌های فعال:**\n"
        "• ⚔️ سیستم حمله پیشرفته\n" 
        "• 🛒 فروشگاه جنگ‌افزار\n"
        "• ⛏️ ماینر تولید ZP\n"
        "• 📦 جعبه‌های شانس\n"
        "• 👤 پروفایل و سطح‌بندی\n"
        "• 📊 آمار کامل\n\n"
        f"💰 **موجودی اولیه**: {user[4]:,} ZP\n"
        "👇 از منوی زیر انتخاب کنید:"
    )
    
    db.log_activity(message.from_user.id, "start", "ورود به ربات")
    await message.answer(welcome_text, reply_markup=main_menu())

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    bot_info = await bot.get_me()
    total_users = db.get_total_users()
    total_attacks = db.get_total_attacks()
    
    status_text = (
        "🤖 **وضعیت WarZone Bot**\n\n"
        f"🆔 **بات**: @{bot_info.username}\n"
        f"👥 **کاربران**: {total_users:,}\n"
        f"⚔️ **حملات**: {total_attacks:,}\n"
        f"🏠 **میزبان**: رندر (Render.com)\n"
        f"🕒 **آپ‌تایم**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"📊 **وضعیت**: 🟢 آنلاین\n\n"
        "✅ تمام سیستم‌ها فعال هستند"
    )
    
    await message.answer(status_text)

# هندلر پروفایل
@dp.message(lambda message: message.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    stats = db.get_user_stats(message.from_user.id)
    
    xp_needed = user[2] * 100
    xp_percent = (user[3] / xp_needed) * 100 if xp_needed > 0 else 0
    
    profile_text = (
        f"👤 **پروفایل جنگجو**\n\n"
        f"🆔 **شناسه**: {user[0]}\n"
        f"⭐ **سطح**: {user[2]}\n"
        f"📊 **XP**: {user[3]}/{xp_needed} ({xp_percent:.1f}%)\n"
        f"💰 **ZP**: {user[4]:,}\n"
        f"💎 **جم**: {user[5]}\n"
        f"💪 **قدرت**: {user[6]}\n"
        f"🎯 **حملات**: {stats['total_attacks']:,}\n"
        f"💥 **دمیج کل**: {stats['total_damage']:,}\n\n"
        f"🏠 **میزبان**: رندر"
    )
    
    db.log_activity(message.from_user.id, "profile_view")
    await message.answer(profile_text, reply_markup=main_menu())

# هندلرهای دیگر (مشابه قبل)
@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    import random
    user = db.get_user(message.from_user.id)
    
    # حمله ساده
    is_critical = random.random() < 0.15
    base_reward = random.randint(40, 80)
    reward = base_reward * 2 if is_critical else base_reward
    xp_gain = random.randint(8, 15)
    
    db.update_user_zp(message.from_user.id, reward)
    level_up = db.update_user_xp(message.from_user.id, xp_gain)
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    
    response = f"⚔️ **حمله موفق{critical_text}!**\n\n"
    response += f"💰 **جایزه**: {reward} ZP\n"
    response += f"⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)[2]
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
    
    db.log_activity(message.from_user.id, "attack", f"حمله - {reward} ZP")
    await message.answer(response, reply_markup=main_menu())

@dp.message(lambda message: message.text == "📊 آمار")
async def stats_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    stats = db.get_user_stats(message.from_user.id)
    total_users = db.get_total_users()
    total_attacks = db.get_total_attacks()
    
    stats_text = (
        "📊 **آمار جهانی WarZone**\n\n"
        f"👥 **کل کاربران**: {total_users:,}\n"
        f"🎯 **حملات شما**: {stats['total_attacks']:,}\n"
        f"💥 **دمیج کل شما**: {stats['total_damage']:,}\n"
        f"⭐ **سطح شما**: {user[2]}\n"
        f"💰 **ZP شما**: {user[4]:,}\n\n"
        f"🏠 **میزبان**: رندر\n"
        f"🕒 **تاریخ**: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    db.log_activity(message.from_user.id, "stats_view")
    await message.answer(stats_text, reply_markup=main_menu())

@dp.message(lambda message: message.text in ["🛒 فروشگاه", "⛏ ماینر", "📦 جعبه"])
async def coming_soon_handler(message: types.Message):
    feature_name = {
        "🛒 فروشگاه": "فروشگاه جنگ‌افزار",
        "⛏ ماینر": "سیستم ماینر", 
        "📦 جعبه": "جعبه‌های شانس"
    }[message.text]
    
    await message.answer(
        f"🛠 **{feature_name}**\n\n"
        f"🔜 به زودی فعال می‌شود\n\n"
        f"✅ در حال حاضر از این قابلیت‌ها استفاده کنید:\n"
        f"• ⚔️ سیستم حمله پیشرفته\n"
        f"• 👤 پروفایل و آمار\n"
        f"• 📊 آمار جهانی\n\n"
        f"🏠 **میزبان**: رندر",
        reply_markup=main_menu()
    )

@dp.message()
async def all_messages(message: types.Message):
    if message.text and not message.text.startswith('/'):
        await message.answer("🎯 از منوی زیر انتخاب کنید:", reply_markup=main_menu())

# مدیریت خطا
async def error_handler(update: types.Update, exception: Exception):
    logger.error(f"خطا در پردازش آپدیت: {exception}")
    return True

# مدیریت خاموشی
async def shutdown():
    logger.info("🔄 دریافت سیگنال خاموشی...")
    await bot.session.close()
    db.close()
    logger.info("✅ بات WarZone خاموش شد")

# شروع بات برای رندر
async def main():
    logger.info("🚀 شروع WarZone Bot روی رندر...")
    
    try:
        # حذف وب‌هوک برای پولینگ
        async with aiohttp.ClientSession() as session:
            await session.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
            logger.info("✅ وب‌هوک حذف شد")
        
        # اطلاعات بات
        bot_info = await bot.get_me()
        logger.info(f"✅ بات: @{bot_info.username}")
        logger.info(f"✅ شناسه بات: {bot_info.id}")
        
        # تنظیم هندلر خطا
        dp.errors.register(error_handler)
        
        logger.info("🟢 بات WarZone روی رندر آنلاین شد!")
        logger.info("⏰ پولینگ فعال - بات همیشه آنلاین خواهد بود")
        
        # شروع پولینگ
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"❌ خطای بحرانی: {e}")
        await shutdown()
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹ توقف دستی بات")
    except Exception as e:
        logger.error(f"❌ خطای اصلی: {e}")
