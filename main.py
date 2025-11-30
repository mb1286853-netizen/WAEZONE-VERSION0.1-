# main.py - WarZone Bot
import os
import asyncio
import logging
import signal
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import aiohttp
import random

# Import database and config
from database import WarZoneDatabase
from config import TOKEN
from keyboards import main_menu, attack_menu, shop_menu, boxes_menu, miner_menu, back_only

print("🚀 راه‌اندازی WarZone Bot...")

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# بررسی توکن
if not TOKEN:
    logger.error("❌ توکن یافت نشد! لطفا TOKEN را تنظیم کنید.")
    sys.exit(1)

# ساخت بات
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

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
        f"🛡️ **یک بازی استراتژیک جنگی پیشرفته**\n\n"
        "از کیبورد زیر برای دسترسی سریع استفاده کنید:\n\n"
        f"💰 **موجودی اولیه**: {user[4]:,} ZP\n"
        "👇 گزینه مورد نظر را انتخاب کنید:"
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
            f"🏠 **میزبان**: رندر (Render.com)\n"
            f"🕒 **آپ‌تایم**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📊 **وضعیت**: 🟢 آنلاین"
        )
        
        await message.answer(status_text, reply_markup=main_menu())
    except Exception as e:
        await message.answer("❌ خطا در دریافت وضعیت", reply_markup=main_menu())

# هندلر منوی اصلی
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
            f"💥 **دمیج کل**: {stats['total_damage']:,}\n\n"
            f"📅 **عضویت**: {user[15].split()[0] if user[15] else 'نامشخص'}"
        )
        
        db.log_activity(message.from_user.id, "profile_view")
        await message.answer(profile_text, reply_markup=main_menu())
    except Exception as e:
        await message.answer("❌ خطا در نمایش پروفایل", reply_markup=main_menu())

@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "نوع حمله را انتخاب کنید:",
        reply_markup=attack_menu()
    )

@dp.message(lambda message: message.text == "🛒 فروشگاه")
async def shop_handler(message: types.Message):
    await message.answer(
        "🛒 **فروشگاه WarZone**\n\n"
        "دسته مورد نظر را انتخاب کنید:",
        reply_markup=shop_menu()
    )

@dp.message(lambda message: message.text == "📦 باکس")
async def boxes_handler(message: types.Message):
    await message.answer(
        "📦 **جعبه‌های شانس**\n\n"
        "نوع جعبه را انتخاب کنید:",
        reply_markup=boxes_menu()
    )

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

# هندلرهای حمله
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
        
        # ثبت آمار
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET total_attacks = total_attacks + 1, total_damage = total_damage + ? WHERE user_id = ?',
            (reward, message.from_user.id)
        )
        conn.commit()
        
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

@dp.message(lambda message: message.text == "💥 حمله ترکیبی")
async def combo_attack_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        # حمله ترکیبی
        base_damage = random.randint(80, 150)
        is_critical = random.random() < 0.15
        total_damage = base_damage * 2 if is_critical else base_damage
        reward = total_damage
        xp_gain = random.randint(15, 25)
        
        db.update_user_zp(message.from_user.id, reward)
        level_up = db.update_user_xp(message.from_user.id, xp_gain)
        
        critical_text = " 🔥**بحرانی**" if is_critical else ""
        
        response = f"💥 **حمله ترکیبی موفق{critical_text}!**\n\n"
        response += f"💥 **دمیج**: {total_damage}\n"
        response += f"💰 **جایزه**: {reward} ZP\n"
        response += f"⭐ **XP**: +{xp_gain}\n"
        
        if level_up:
            new_level = db.get_user(message.from_user.id)[2]
            response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
        
        response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
        
        db.log_activity(message.from_user.id, "combo_attack", f"حمله ترکیبی - {reward} ZP")
        await message.answer(response, reply_markup=attack_menu())
    except Exception as e:
        await message.answer("❌ خطا در حمله ترکیبی", reply_markup=attack_menu())

@dp.message(lambda message: message.text == "🔄 انتقام")
async def revenge_attack_handler(message: types.Message):
    await message.answer(
        "🔄 **سیستم انتقام**\n\n"
        "در حال حاضر حمله‌ای برای انتقام وجود ندارد.\n"
        "پس از مورد حمله قرار گرفتن، این گزینه فعال می‌شود.",
        reply_markup=attack_menu()
    )

@dp.message(lambda message: message.text == "📋 تاریخچه حملات")
async def attack_history_handler(message: types.Message):
    await message.answer(
        "📋 **تاریخچه حملات**\n\n"
        "در حال توسعه...\n"
        "به زودی قابلیت مشاهده تاریخچه حملات اضافه می‌شود.",
        reply_markup=attack_menu()
    )

# هندلرهای فروشگاه
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
            "برای خرید ریپلای کنید: <code>خرید موشک نامموشک</code>"
        )
        
        await message.answer(missiles_text, reply_markup=shop_menu())
    except Exception as e:
        await message.answer("❌ خطا در نمایش موشک‌ها", reply_markup=shop_menu())

@dp.message(lambda message: message.text == "🛩 جنگنده‌ها")
async def fighters_shop_handler(message: types.Message):
    await message.answer(
        "🛩 **جنگنده‌های موجود:**\n\n"
        "• **شب‌پرواز** - 5,000 ZP\n  💥 دمیج: 200\n\n"
        "• **توفان‌ساز** - 8,000 ZP\n  💥 دمیج: 320\n\n"
        "• **آذرخش** - 12,000 ZP\n  💥 دمیج: 450\n\n"
        "• **شبح‌ساحل** - 18,000 ZP\n  💥 دمیج: 700\n\n"
        "برای خرید ریپلای کنید: <code>خرید جنگنده نامجنگنده</code>",
        reply_markup=shop_menu()
    )

@dp.message(lambda message: message.text == "🛸 پهپادها")
async def drones_shop_handler(message: types.Message):
    await message.answer(
        "🛸 **پهپادهای موجود:**\n\n"
        "• **زنبورک** - 3,000 ZP\n  💥 دمیج: 90\n\n"
        "• **سایفر** - 5,000 ZP\n  💥 دمیج: 150\n\n"
        "• **ریزپرنده V** - 8,000 ZP\n  💥 دمیج: 250\n\n"
        "برای خرید ریپلای کنید: <code>خرید پهپاد نامپهپاد</code>",
        reply_markup=shop_menu()
    )

@dp.message(lambda message: message.text == "💎 ویژه‌ها")
async def special_shop_handler(message: types.Message):
    await message.answer(
        "💎 **آیتم‌های ویژه:**\n\n"
        "• **آتشفشان** - 8,000 ZP\n  💥 دمیج: 2,000\n\n"
        "• **توفان‌نو** - 15,000 ZP\n  💥 دمیج: 3,000\n\n"
        "• **خاموش‌کن** - 20,000 ZP\n  🔧 قطع سیستم\n\n"
        "برای خرید ریپلای کنید: <code>خرید ویژه نامآیتم</code>",
        reply_markup=shop_menu()
    )

# هندلرهای ماینر
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

@dp.message(lambda message: message.text == "🔼 ارتقا")
async def upgrade_miner_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        upgrade_cost = user[9] * 500
        
        if user[4] >= upgrade_cost:
            db.update_user_zp(message.from_user.id, -upgrade_cost)
            
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET miner_level = miner_level + 1 WHERE user_id = ?',
                (message.from_user.id,)
            )
            conn.commit()
            
            new_level = db.get_user(message.from_user.id)[9]
            new_balance = db.get_user(message.from_user.id)[4]
            
            response = (
                f"🔼 **ارتقای موفق!**\n\n"
                f"📊 **سطح جدید**: {new_level}\n"
                f"💰 **هزینه**: {upgrade_cost:,} ZP\n"
                f"💎 **تولید جدید**: {new_level * 100} ZP/ساعت\n"
                f"💎 **موجودی جدید**: {new_balance:,} ZP"
            )
        else:
            response = (
                f"❌ **موجودی ناکافی**\n\n"
                f"💰 **هزینه ارتقا**: {upgrade_cost:,} ZP\n"
                f"💎 **موجودی شما**: {user[4]:,} ZP\n"
                f"📉 **کمبود**: {upgrade_cost - user[4]:,} ZP"
            )
        
        await message.answer(response, reply_markup=miner_menu())
    except Exception as e:
        await message.answer("❌ خطا در ارتقای ماینر", reply_markup=miner_menu())

@dp.message(lambda message: message.text == "📊 وضعیت")
async def miner_status_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        status_text = (
            f"⛏️ **وضعیت ماینر**\n\n"
            f"📊 **سطح**: {user[9]}\n"
            f"💰 **تولید ساعتی**: {user[9] * 100} ZP\n"
            f"💎 **موجودی فعلی**: {user[10]:,} ZP\n"
            f"🔼 **هزینه ارتقا بعدی**: {user[9] * 500} ZP\n\n"
            f"⏰ **سیستم**: فعال"
        )
        
        await message.answer(status_text, reply_markup=miner_menu())
    except Exception as e:
        await message.answer("❌ خطا در نمایش وضعیت", reply_markup=miner_menu())

# هندلرهای باکس
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

@dp.message(lambda message: message.text == "🥈 نقره‌ای")
async def silver_box_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        price = 5000
        
        if user[4] >= price:
            db.update_user_zp(message.from_user.id, -price)
            reward = random.randint(200, 500)
            db.update_user_zp(message.from_user.id, reward)
            
            response = (
                f"🥈 **جعبه نقره‌ای** 🎉\n\n"
                f"💰 **هزینه**: {price:,} ZP\n"
                f"💰 **جایزه**: {reward} ZP\n"
                f"💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
            )
            
            db.log_activity(message.from_user.id, "lootbox", "جعبه نقره‌ای")
        else:
            response = (
                f"❌ **موجودی ناکافی**\n\n"
                f"💰 **قیمت جعبه**: {price:,} ZP\n"
                f"💎 **موجودی شما**: {user[4]:,} ZP"
            )
        
        await message.answer(response, reply_markup=boxes_menu())
    except Exception as e:
        await message.answer("❌ خطا در باز کردن جعبه", reply_markup=boxes_menu())

@dp.message(lambda message: message.text == "🥇 طلایی")
async def gold_box_handler(message: types.Message):
    await message.answer(
        "🥇 **جعبه طلایی**\n\n"
        "💰 **قیمت**: ۲ جم\n\n"
        "🔜 به زودی فعال می‌شود\n"
        "در حال حاضر از جعبه‌های برنزی و نقره‌ای استفاده کنید.",
        reply_markup=boxes_menu()
    )

@dp.message(lambda message: message.text == "💎 الماس")
async def diamond_box_handler(message: types.Message):
    await message.answer(
        "💎 **جعبه الماس**\n\n"
        "💰 **قیمت**: ۵ جم\n\n"
        "🔜 به زودی فعال می‌شود\n"
        "در حال حاضر از جعبه‌های برنزی و نقره‌ای استفاده کنید.",
        reply_markup=boxes_menu()
    )

# هندلرهای قابلیت‌های آینده
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

# هندلر پیام‌های متنی برای خرید
@dp.message()
async def all_messages(message: types.Message):
    try:
        text = message.text.lower()
        
        if "خرید" in text and "موشک" in text:
            user = db.get_user(message.from_user.id)
            missile_name = text.replace("خرید", "").replace("موشک", "").strip()
            
            missile_prices = {"تیرباران": 400, "رعدآسا": 700, "تندباد": 1000}
            
            if missile_name in missile_prices:
                price = missile_prices[missile_name]
                
                if user[4] >= price:
                    db.update_user_zp(message.from_user.id, -price)
                    db.add_missile(message.from_user.id, missile_name, 1)
                    
                    await message.answer(
                        f"✅ **خرید موفق**\n\n"
                        f"🚀 **موشک**: {missile_name}\n"
                        f"💰 **قیمت**: {price:,} ZP\n"
                        f"💎 **موجودی جدید**: {user[4] - price:,} ZP",
                        reply_markup=main_menu()
                    )
                else:
                    await message.answer(
                        f"❌ **موجودی ناکافی**\n\n"
                        f"💰 **قیمت**: {price:,} ZP\n"
                        f"💎 **موجودی شما**: {user[4]:,} ZP",
                        reply_markup=main_menu()
                    )
            else:
                await message.answer("❌ موشک پیدا نشد!", reply_markup=main_menu())
        
        elif message.text and not message.text.startswith('/'):
      
