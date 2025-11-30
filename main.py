# main.py - WarZone Bot Fixed
import os
import asyncio
import logging
import sys
import random
import time
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import keyboards as kb
from config import SHOP_ITEMS, ATTACK_TYPES, ADMINS
from database import db

print("🚀 شروع WarZone Bot...")

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

# وضعیت کاربران
user_purchase_state = {}
user_admin_state = {}

# ==================== دستورات اصلی ====================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    welcome_text = f"""
🎯 **به WarZone خوش آمدید {username}!** ⚔️

💰 **موجودی**: {user['zp']:,} ZP
⭐ **سطح**: {user['level']}
💪 **قدرت**: {user['power']}

👇 از منوی زیر انتخاب کنید:
"""
    await message.answer(welcome_text, reply_markup=kb.main_menu())
    print(f"✅ کاربر {message.from_user.id} استارت زد")

@dp.message(Command("test"))
async def test_handler(message: types.Message):
    await message.answer("✅ **بات فعال است!**")
    print("✅ تست بات موفق")

@dp.message(F.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    profile_text = f"""
👤 **پروفایل جنگجو**

⭐ **سطح**: {user['level']}
💰 **ZP**: {user['zp']:,}
💎 **جم**: {user['gem']}
💪 **قدرت**: {user['power']}

🎯 **حملات**: {user['total_attacks']:,}
💥 **دمیج کل**: {user['total_damage']:,}
"""
    await message.answer(profile_text, reply_markup=kb.main_menu())

@dp.message(F.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    await message.answer(
        "⚔️ **سیستم حمله**\n\n"
        "🎯 حمله تکی\n"
        "💥 حمله ترکیبی\n"
        "🛸 حمله پهپادی\n\n"
        "👇 نوع حمله را انتخاب کنید:",
        reply_markup=kb.attack_menu()
    )

@dp.message(F.text == "🎯 حمله تکی")
async def single_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # محاسبات حمله
    reward = random.randint(50, 100)
    xp_gain = random.randint(10, 20)
    
    # آپدیت کاربر
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += reward
    
    response = f"⚔️ **حمله تکی موفق!**\n\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n💎 **موجودی جدید**: {new_balance:,} ZP"
    
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "🛒 فروشگاه")
async def shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    shop_text = f"""
🛒 **فروشگاه WarZone**

💰 **موجودی شما**: {user['zp']:,} ZP

👇 دسته مورد نظر را انتخاب کنید:

🚀 موشک‌ها
🛩 جنگنده‌ها  
🛸 پهپادها
"""
    await message.answer(shop_text, reply_markup=kb.shop_main_menu())

# ==================== هندلر پیش‌فرض ====================
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("از منوی زیر انتخاب کنید:", reply_markup=kb.main_menu())

# ==================== تابع اصلی ====================
async def main():
    logger.info("🤖 بات WarZone در حال راه‌اندازی...")
    print("✅ شروع راه‌اندازی...")
    
    try:
        print("✅ حذف webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        
        print("✅ شروع polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ خطا: {e}")
        print(f"❌ خطای جدی: {e}")

if __name__ == "__main__":
    print("🔧 اجرای بات...")
    asyncio.run(main())
