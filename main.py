# main.py - WarZone Bot با کیبورد جدید
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
db = WarZoneDatabase()

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

# هندلر منوی اصلی
@dp.message(lambda message: message.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    stats = db.get_user_stats(message.from_user.id)
    
    xp_needed = user[2] * 100
    xp_percent = (user[3] / xp_needed) * 100 if xp_needed > 0 else 0
    
    profile_text = (
        f"👤 **پروفایل جنگجو**\n\n"
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
    user = db.get_user(message.from_user.id)
    
    miner_text = (
        f"⛏️ **سیستم ماینر**\n\n"
        f"💰 **تولید**: {user[9] * 100} ZP/ساعت\n"
        f"📊 **سطح**: {user[9]}\n"
        f"💎 **موجودی**: {user[10]:,} ZP\n\n"
        f"🔼 **هزینه ارتقا**: {user[9] * 500} ZP"
    )
    
    await message.answer(miner_text, reply_markup=miner_menu())

# هندلرهای حمله
@dp.message(lambda message: message.text == "🎯 حمله تکی")
async def single_attack_handler(message: types.Message):
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

@dp.message(lambda message: message.text == "💥 حمله ترکیبی")
async def combo_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # حمله ترکیبی
    base_damage = random.randint(80, 150)
    is_critical = random.random() < 0.15
    total_damage = base_damage * 2 if is_critical else base_damage
    xp_gain = random.randint(15, 25)
    
    db.update_user_zp(message.from_user.id, total_damage)
    level_up = db.update_user_xp(message.from_user.id, xp_gain)
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    
    response = f"💥 **حمله ترکیبی موفق{critical_text}!**\n\n"
    response += f"💥 **دمیج**: {total_damage}\n"
    response += f"💰 **جایزه**: {total_damage} ZP\n"
    response += f"⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)[2]
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
    
    db.log_activity(message.from_user.id, "combo_attack", f"حمله ترکیبی - {total_damage} ZP")
    await message.answer(response, reply_markup=attack_menu())

# هندلرهای فروشگاه
@dp.message(lambda message: message.text == "🚀 موشک‌ها")
async def missiles_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    missiles_text = (
        "🚀 **موشک‌های موجود:**\n\n"
        "• **تیرباران** - 400 ZP\n  💥 دمیج: 60\n\n"
        "• **رعدآسا** - 700 ZP\n  💥 دمیج: 90\n\n"
        "• **تندباد** - 1,000 ZP\n  💥 دمیج: 120\n\n"
        f"💰 **موجودی شما**: {user[4]:,} ZP\n\n"
        "برای خرید ریپلای کنید: <code>خرید موشک نامموشک</code>"
    )
    
    await message.answer(missiles_text, reply_markup=shop_menu())

# هندلرهای ماینر
@dp.message(lambda message: message.text == "💰 برداشت")
async def claim_miner_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # شبیه
