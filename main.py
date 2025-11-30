# main.py - WarZone Bot
import os
import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import aiohttp
import random

print("🚀 راه‌اندازی WarZone Bot...")

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import database and config
try:
    from database import WarZoneDatabase
    from config import TOKEN
    from keyboards import main_menu, attack_menu, shop_menu, boxes_menu, miner_menu, back_only
except ImportError as e:
    logger.error(f"❌ خطا در ایمپورت ماژول‌ها: {e}")
    sys.exit(1)

# بررسی توکن
if not TOKEN:
    logger.error("❌ توکن یافت نشد! لطفا TOKEN را تنظیم کنید.")
    sys.exit(1)

# ساخت بات و دیسپچر
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()  # این خط باید قبل از هندلرها باشد

# دیتابیس
try:
    db = WarZoneDatabase()
    logger.info("✅ دیتابیس متصل شد")
except Exception as e:
    logger.error(f"❌ خطا در اتصال به دیتابیس: {e}")
    sys.exit(1)

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

# هندلر وضعیت
@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    try:
        bot_info = await bot.get_me()
        total_users = db.get_total_users()
        total_attacks = db.get_total_attacks()
        
        status_text = (
            "🤖 **وضعیت WarZone Bot**\n\n"
            f"🆔 **بات**: @{bot_info.username}\n"
            f"👥 **کاربران**: {total_users:,}\n"
            f"⚔️ **حملات**: {total_attacks:,}\n"
            f"🏠 **میزبان**: رندر (Worker Service)\n"
            f"🕒 **آپ‌تایم**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📊 **وضعیت**: 🟢 آنلاین"
        )
        
        await message.answer(status_text, reply_markup=main_menu())
    except Exception as e:
        await message.answer("❌ خطا در دریافت وضعیت", reply_markup=main_menu())

# هندلر پروفایل
@dp.message(lambda message: message.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    try:
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
            f"🛡️ **پدافند**: سطح {user[7]}\n"
            f"🔒 **امنیت**: سطح {user[8]}\n"
            f"⛏️ **ماینر**: سطح {user[9]}\n"
            f"🎯 **حملات**: {stats['total_attacks']:,}\n"
            f"💥 **دمیج کل**: {stats['total_damage']:,}"
        )
        
        db.log_activity(message.from_user.id, "profile_view")
        await message.answer(profile_text, reply_markup=main_menu())
    except Exception as e:
        await message.answer("❌ خطا در نمایش پروفایل", reply_markup=main_menu())

# هندلر حمله
@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "نوع حمله را انتخاب کنید:",
        reply_markup=attack_menu()
    )

@dp.message(lambda message: message.text == "🎯 حمله تکی")
async def single_attack_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        # شانس حمله بحرانی
        is_critical = random.random() < 0.15
        base_reward = random.randint(40, 80)
        reward = base_reward * 2 if is_critical else base_reward
        xp_gain = random.randint(8, 15)
        
        # اعطای جایزه
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
        
        db.log_activity(message.from_user.id, "attack", f"حمله تکی - {reward} ZP")
        await message.answer(response, reply_markup=attack_menu())
    except Exception as e:
        await message.answer("❌ خطا در حمله", reply_markup=attack_menu())

# هندلر فروشگاه
@dp.message(lambda message: message.text == "🛒 فروشگاه")
async def shop_handler(message: types.Message):
    await message.answer(
        "🛒 **فروشگاه WarZone**\n\n"
        "دسته مورد نظر را انتخاب کنید:",
        reply_markup=shop_menu()
    )

@dp.message(lambda message: message.text == "🚀 موشک‌ها")
async def missiles_shop_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        missiles_text = (
            "🚀 **موشک‌های موجود:**\n\n"
            "• **تیرباران** - 400 ZP\n  💥 دمیج: 60\n  🎯 سطح ۱\n\n"
            "• **رعدآسا** - 700 ZP\n  💥 دمیج: 90\n  🎯 سطح ۳\n\n"
            "• **تندباد** - 1,000 ZP\n  💥 دمیج: 120\n  🎯 سطح ۵\n\n"
            f"💰 **موجودی شما**: {user[4]:,} ZP\n\n"
            "برای خرید ریپلای کنید: خرید موشک نامموشک"
        )
        
        await message.answer(missiles_text, reply_markup=shop_menu())
    except Exception as e:
        await message.answer("❌ خطا در نمایش موشک‌ها", reply_markup=shop_menu())

# هندلر باکس
@dp.message(lambda message: message.text == "📦 باکس")
async def boxes_handler(message: types.Message):
    await message.answer(
        "📦 **جعبه‌های شانس**\n\n"
        "نوع جعبه را انتخاب کنید:",
        reply_markup=boxes_menu()
    )

@dp.message(lambda message: message.text == "📦 برنزی")
async def bronze_box_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        # شانس‌ها
        reward_type = random.choices(['zp', 'missile'], weights=[70, 30])[0]
        
        if reward_type == 'zp':
            reward = random.randint(50, 200)
            db.update_user_zp(message.from_user.id, reward)
            response = f"📦 **جعبه برنزی** 🎉\n\n💰 **جایزه**: {reward} ZP"
        else:
            missiles = ["تیرباران", "رعدآسا"]
            missile = random.choice(missiles)
            db.add_missile(message.from_user.id, missile, 1)
            response = f"📦 **جعبه برنزی** 🎉\n\n🚀 **جایزه**: ۱ عدد {missile}"
        
        response += f"\n\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
        
        db.log_activity(message.from_user.id, "lootbox", "جعبه برنزی")
        await message.answer(response, reply_markup=boxes_menu())
    except Exception as e:
        await message.answer("❌ خطا در باز کردن جعبه", reply_markup=boxes_menu())

# هندلر ماینر
@dp.message(lambda message: message.text == "⛏ ماینر")
async def miner_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        miner_text = (
            f"⛏️ **سیستم ماینر**\n\n"
            f"💰 **تولید**: {user[9] * 100} ZP/ساعت\n"
            f"📊 **سطح**: {user[9]}\n"
            f"💎 **موجودی**: {user[10]:,} ZP\n\n"
            f"🔼 **هزینه ارتقا**: {user[9] * 500} ZP\n\n"
            "برای برداشت از دکمه زیر استفاده کنید:"
        )
        
        await message.answer(miner_text, reply_markup=miner_menu())
    except Exception as e:
        await message.answer("❌ خطا در نمایش ماینر", reply_markup=main_menu())

@dp.message(lambda message: message.text == "💰 برداشت")
async def claim_miner_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        # شبیه‌سازی برداشت
        income = user[10] + (user[9] * 100)
        db.update_user_zp(message.from_user.id, income)
        
        # ریست کردن ماینر
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET miner_balance = 0 WHERE user_id = ?',
            (message.from_user.id,)
        )
        conn.commit()
        
        new_balance = db.get_user(message.from_user.id)[4]
        
        response = (
            f"⛏️ **برداشت موفق!**\n\n"
            f"💰 **مبلغ برداشت**: {income:,} ZP\n"
            f"💎 **موجودی جدید**: {new_balance:,} ZP\n\n"
            f"✅ برداشت بعدی: ۱ ساعت دیگر"
        )
        
        db.log_activity(message.from_user.id, "miner_claim", f"{income} ZP")
        await message.answer(response, reply_markup=miner_menu())
    except Exception as e:
        await message.answer("❌ خطا در برداشت ماینر", reply_markup=miner_menu())

# هندلر قابلیت‌های آینده
@dp.message(lambda message: message.text in ["🕵️ خرابکاری", "🏆 لیگ ها", "🛡 دفاع", "⚙️ تنظیمات"])
async def coming_soon_handler(message: types.Message):
    feature_name = {
        "🕵️ خرابکاری": "سیستم خرابکاری",
        "🏆 لیگ ها": "سیستم لیگ‌ها", 
        "🛡 دفاع": "سیستم دفاع",
        "⚙️ تنظیمات": "تنظیمات پیشرفته"
    }[message.text]
    
    await message.answer(
        f"🛠 **{feature_name}**\n\n"
        f"🔜 به زودی فعال می‌شود\n\n"
        f"✅ در حال حاضر از این قابلیت‌ها استفاده کنید:\n"
        f"• ⚔️ سیستم حمله\n"
        f"• 🛒 فروشگاه\n"
        f"• ⛏️ ماینر\n"
        f"• 📦 جعبه‌ها",
        reply_markup=main_menu()
    )

# هندلر بازگشت
@dp.message(lambda message: message.text == "🔙 بازگشت")
async def back_handler(message: types.Message):
    await message.answer("🔙 بازگشت به منوی اصلی", reply_markup=main_menu())

# هندلر پیام‌های متنی
@dp.message()
async def all_messages(message: types.Message):
    if message.text and not message.text.startswith('/'):
        await message.answer("🎯 از منوی زیر انتخاب کنید:", reply_markup=main_menu())

# مدیریت خطا
async def error_handler(update: types.Update, exception: Exception):
    logger.error(f"خطا در پردازش آپدیت: {exception}")
    return True

# شروع بات
async def main():
    logger.info("🚀 شروع WarZone Bot...")
    
    try:
        # حذف وب‌هوک
        async with aiohttp.ClientSession() as session:
            await session.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
            logger.info("✅ وب‌هوک حذف شد")
        
        # اطلاعات بات
        bot_info = await bot.get_me()
        logger.info(f"✅ بات: @{bot_info.username}")
        logger.info(f"✅ شناسه بات: {bot_info.id}")
        
        # تنظیم هندلر خطا
        dp.errors.register(error_handler)
        
        logger.info("🟢 بات WarZone آنلاین شد و آماده دریافت پیام‌ها است...")
        
        # شروع پولینگ
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"❌ خطای بحرانی: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹ توقف دستی بات")
    except Exception as e:
        logger.error(f"❌ خطای اصلی: {e}")
